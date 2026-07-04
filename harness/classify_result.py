#!/usr/bin/env python3
"""Emit a simple accept/reject verdict for a MobileMoE candidate run."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


EPS = 1e-9


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def num(data: dict[str, Any], key: str) -> float | None:
    value = data.get(key)
    if value is None:
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def pct_delta(base: float | None, cand: float | None) -> float | None:
    if base is None or cand is None or abs(base) < EPS:
        return None
    return (cand - base) / base * 100.0


def metric_deltas(base: dict[str, Any], cand: dict[str, Any]) -> dict[str, float | None]:
    keys = [
        "decode_tok_s",
        "mib_per_token",
        "decode_core_upload_mib",
        "decode_req_mat_writes",
        "upload_bytes",
        "decode_req_service_ms",
        "required_miss_wait_ms_per_token",
        "decode_req_miss",
        "required_miss_count",
        "decode_evict",
        "eviction_churn",
    ]
    return {key: pct_delta(num(base, key), num(cand, key)) for key in keys}


def classify(args: argparse.Namespace) -> dict[str, Any]:
    base = load(args.baseline)
    cand = load(args.candidate)
    deltas = metric_deltas(base, cand)
    speed_delta = deltas["decode_tok_s"]

    guardrail_failures: list[str] = []
    guardrail_warnings: list[str] = []
    notes: list[str] = []
    verdict = "inconclusive"
    accept = False

    if cand.get("compile_success") is False or cand.get("correct") is not True:
        verdict = "invalid"
        guardrail_failures.append("candidate failed compile/correctness guardrail")
    elif speed_delta is None:
        verdict = "invalid"
        guardrail_failures.append("decode_tok_s missing or not comparable")
    elif speed_delta <= -args.regression_pct:
        verdict = "reject"
        guardrail_failures.append(f"decode_tok_s regressed {speed_delta:.2f}%")
    elif speed_delta >= args.speedup_pct:
        verdict = "accept"
        accept = True
        notes.append(f"decode_tok_s improved {speed_delta:.2f}%")
    else:
        verdict = "inconclusive"
        notes.append(f"decode_tok_s movement {speed_delta:.2f}% is below accept threshold")

    transfer_delta = deltas.get("mib_per_token")
    if transfer_delta is not None and transfer_delta >= args.transfer_warning_pct:
        guardrail_warnings.append(f"mib_per_token increased {transfer_delta:.2f}%")

    return {
        "verdict": verdict,
        "accept": accept,
        "hypothesis": args.hypothesis,
        "baseline": str(args.baseline),
        "candidate": str(args.candidate),
        "metric_deltas_pct": deltas,
        "guardrail_failures": guardrail_failures,
        "guardrail_warnings": guardrail_warnings,
        "notes": notes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--hypothesis", default="unknown")
    parser.add_argument("--speedup-pct", type=float, default=1.0)
    parser.add_argument("--regression-pct", type=float, default=1.0)
    parser.add_argument("--transfer-warning-pct", type=float, default=5.0)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    result = classify(args)
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
