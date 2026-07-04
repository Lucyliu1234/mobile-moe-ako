#!/usr/bin/env python3
"""Classify a MobileMoE candidate run against a baseline."""

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


def moved_down(base: dict[str, Any], cand: dict[str, Any], keys: list[str], min_pct: float) -> bool:
    for key in keys:
        b = num(base, key)
        c = num(cand, key)
        if b is not None and c is not None and b > 0 and (b - c) / b * 100.0 >= min_pct:
            return True
    return False


def moved_up(base: dict[str, Any], cand: dict[str, Any], keys: list[str], min_pct: float) -> bool:
    for key in keys:
        b = num(base, key)
        c = num(cand, key)
        if b is not None and c is not None and b > 0 and (c - b) / b * 100.0 >= min_pct:
            return True
    return False


def classify(args: argparse.Namespace) -> dict[str, Any]:
    base = load(args.baseline)
    cand = load(args.candidate)
    speed_delta = pct_delta(num(base, "decode_tok_s"), num(cand, "decode_tok_s"))
    service_delta = pct_delta(num(base, "decode_req_service_ms"), num(cand, "decode_req_service_ms"))
    transfer_keys = ["mib_per_token", "decode_core_upload_mib", "decode_req_mat_writes", "upload_bytes"]
    logical_keys = ["decode_req_miss", "required_miss_count", "decode_evict", "eviction_churn"]
    service_keys = ["decode_req_service_ms", "required_miss_wait_ms_per_token"]

    reasons: list[str] = []
    result = "no_signal"
    accept = False

    if cand.get("compile_success") is False or cand.get("correct") is not True:
        result = "invalid"
        reasons.append("candidate failed compile/correctness guardrail")
    elif speed_delta is not None and speed_delta <= -args.regression_pct:
        result = "regression"
        reasons.append(f"decode_tok_s changed {speed_delta:.2f}%")
    elif moved_up(base, cand, ["mib_per_token"], args.transfer_regression_pct):
        result = "regression"
        reasons.append("normalized transfer volume regressed")
    else:
        physical_down = moved_down(base, cand, transfer_keys, args.physical_move_pct)
        service_down = moved_down(base, cand, service_keys, args.service_move_pct)
        logical_down = moved_down(base, cand, logical_keys, args.logical_move_pct)
        page_touch_down = moved_down(base, cand, ["decode_req_page_touch_ms"], args.service_move_pct)
        enqueue_up = moved_up(base, cand, ["decode_req_mat_enqueue_ms", "decode_req_mat_finish_ms"], args.service_move_pct)
        speed_good = speed_delta is not None and speed_delta >= args.speedup_pct

        if logical_down and not physical_down and not service_down:
            result = "logical_counter_only"
            reasons.append("logical cache/miss counters moved but physical/service metrics did not")
        elif page_touch_down and enqueue_up and not service_down:
            result = "latency_shift"
            reasons.append("page-touch cost moved into enqueue/finish without total service proof")
        elif physical_down and speed_good:
            result = "transfer_win"
            accept = True
            reasons.append("physical transfer metrics and primary throughput improved")
        elif service_down and speed_good:
            result = "scheduling_win" if args.hypothesis == "scheduling" else "true_system_win"
            accept = True
            reasons.append("service metrics and primary throughput improved")
        elif speed_good and (physical_down or service_down):
            result = "true_system_win"
            accept = True
            reasons.append("primary improvement has supporting physical/service movement")
        elif speed_delta is None or abs(speed_delta) < args.speedup_pct:
            result = "no_signal"
            reasons.append("primary metric movement is below threshold or unavailable")
        else:
            result = "wrong_path"
            reasons.append("primary movement is not supported by expected diagnostics")

    return {
        "class": result,
        "accept": accept,
        "hypothesis": args.hypothesis,
        "baseline": str(args.baseline),
        "candidate": str(args.candidate),
        "decode_tok_s_delta_pct": speed_delta,
        "decode_req_service_ms_delta_pct": service_delta,
        "reasons": reasons,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--hypothesis", default="unknown")
    parser.add_argument("--speedup-pct", type=float, default=1.0)
    parser.add_argument("--regression-pct", type=float, default=1.0)
    parser.add_argument("--physical-move-pct", type=float, default=1.0)
    parser.add_argument("--service-move-pct", type=float, default=1.0)
    parser.add_argument("--logical-move-pct", type=float, default=5.0)
    parser.add_argument("--transfer-regression-pct", type=float, default=1.0)
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
