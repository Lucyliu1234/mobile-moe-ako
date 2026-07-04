#!/usr/bin/env python3
"""MobileMoE benchmark adapter for harness-mediated agent runs.

This is a thin wrapper over the existing MobileMoE-AKO shell harness. It makes
the run contract explicit and writes a small manifest next to each metrics file
so later tools can audit what was actually executed.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AGENT_BENCH = ROOT / "scripts" / "agent_bench.sh"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_command(args: argparse.Namespace) -> int:
    out_dir = ROOT / "results" / "runs" / args.label
    metrics_path = out_dir / "metrics.json"
    env = os.environ.copy()
    env.update(
        {
            "AKO_STAGE": args.stage,
            "AKO_ITERATION_ID": args.label,
            "AKO_OUT_DIR": str(out_dir),
            "AKO_CODE_REPO": str(args.runtime),
        }
    )
    if args.profile:
        env["AKO_BENCH_PROFILE"] = args.profile
    if args.baseline_metrics:
        env["AKO_BASELINE_METRICS"] = str(args.baseline_metrics)
    if args.trace_residency:
        env["AKO_QWEN2_RESIDENCY_TRACE"] = "1"
    if args.extra_env:
        for item in args.extra_env:
            if "=" not in item:
                raise SystemExit(f"--extra-env expects KEY=VALUE, got {item!r}")
            key, value = item.split("=", 1)
            env[key] = value

    manifest = {
        "adapter": "mobile-moe-ako-v0",
        "command": " ".join([str(AGENT_BENCH), *args.forward_args]),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "label": args.label,
        "profile": args.profile,
        "runtime": str(args.runtime),
        "stage": args.stage,
        "trace_residency": bool(args.trace_residency),
        "baseline_metrics": str(args.baseline_metrics) if args.baseline_metrics else None,
        "out_dir": str(out_dir),
    }
    write_json(out_dir / "adapter_manifest.json", manifest)

    if args.dry_run:
        print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))
        return 0

    proc = subprocess.run([str(AGENT_BENCH), *args.forward_args], cwd=ROOT, env=env, check=False)
    if metrics_path.exists():
        metrics = load_json(metrics_path)
        check = check_correctness(metrics)
        write_json(out_dir / "adapter_check.json", check)
        print(json.dumps({"metrics": str(metrics_path), **check}, ensure_ascii=False, sort_keys=True))
    return proc.returncode


def parse_command(args: argparse.Namespace) -> int:
    metrics = load_json(args.metrics)
    if args.check:
        print(json.dumps(check_correctness(metrics), ensure_ascii=False, sort_keys=True))
    else:
        print(json.dumps(metrics, ensure_ascii=False, sort_keys=True))
    return 0


def check_correctness(metrics: dict[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if metrics.get("compile_success") is False:
        reasons.append("compile_success=false")
    if metrics.get("correct") is not True:
        reasons.append("correct is not true")
    generated = metrics.get("generated_tokens")
    if generated in (None, 0):
        reasons.append("generated_tokens missing or zero")
    return {
        "valid": not reasons,
        "correct": metrics.get("correct"),
        "generated_tokens": generated,
        "reasons": reasons,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="Run the fixed MobileMoE benchmark harness")
    run.add_argument("--label", required=True, help="Stable run label under results/runs/")
    run.add_argument("--runtime", type=Path, default=Path("/home/liuxu/projects/mllm"))
    run.add_argument("--stage", default="harness_v0")
    run.add_argument("--profile", default="day_smoke_p16_d16")
    run.add_argument("--baseline-metrics", type=Path)
    run.add_argument("--trace-residency", action="store_true")
    run.add_argument("--extra-env", action="append", default=[])
    run.add_argument("--dry-run", action="store_true")
    run.add_argument("forward_args", nargs=argparse.REMAINDER, help="Arguments forwarded to agent_bench.sh")
    run.set_defaults(func=run_command)

    parse = sub.add_parser("parse", help="Print or check an existing metrics JSON")
    parse.add_argument("--metrics", type=Path, required=True)
    parse.add_argument("--check", action="store_true")
    parse.set_defaults(func=parse_command)

    args = parser.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
