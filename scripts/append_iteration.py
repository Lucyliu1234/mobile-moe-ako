#!/usr/bin/env python3
"""Append a structured MobileMoE-AKO iteration entry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


METRIC_KEYS = [
    "decode_tok_s",
    "mib_per_token",
    "required_miss_count",
    "upload_bytes",
    "prewarm_hit_rate",
    "eviction_churn",
    "required_miss_wait_ms_per_token",
    "decode_req_page_touch_ms",
    "decode_req_mat_enqueue_ms",
    "decode_req_mat_finish_ms",
    "decode_req_service_ms",
    "decode_req_mat_writes",
    "decode_req_page_touch_mib",
    "decode_core_upload_mib",
    "decode_req_miss",
    "decode_req_hit",
    "decode_evict",
    "cache_hit_rate",
    "peak_temp_skin_c_decode",
]


def load_metrics(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return {}
    return json.loads(text.splitlines()[-1])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=Path, default=Path("ITERATIONS.md"))
    parser.add_argument("--iteration-id", required=True)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--prompt-setting", default="")
    parser.add_argument("--baseline-bottleneck", default="")
    parser.add_argument("--targeted-bottleneck", default="")
    parser.add_argument("--expected-diagnostic-movement", default="")
    parser.add_argument("--hypothesis", default="")
    parser.add_argument("--direction", default="")
    parser.add_argument("--files-inspected", default="")
    parser.add_argument("--files-modified", default="")
    parser.add_argument("--change-summary", default="")
    parser.add_argument("--benchmark-command", default="bash scripts/agent_bench.sh")
    parser.add_argument("--compile-result", default="")
    parser.add_argument("--correctness-result", default="")
    parser.add_argument("--metrics-json", type=Path, default=None)
    parser.add_argument("--result", default="")
    parser.add_argument("--agent-diagnosis", default="")
    parser.add_argument("--my-diagnosis", default="")
    parser.add_argument("--needed-expert-knowledge", default="")
    parser.add_argument("--patch-or-commit", default="")
    args = parser.parse_args()

    metrics = load_metrics(args.metrics_json)
    compile_result = args.compile_result or str(metrics.get("compile_success", ""))
    correctness_result = args.correctness_result or str(metrics.get("correct", ""))

    lines = [
        "",
        f"## {args.iteration_id}",
        "",
        f"Iteration ID: {args.iteration_id}",
        f"Stage: {args.stage}",
        f"Agent prompt setting: {args.prompt_setting}",
        f"Baseline bottleneck decomposition: {args.baseline_bottleneck}",
        f"Targeted bottleneck: {args.targeted_bottleneck}",
        f"Expected diagnostic movement: {args.expected_diagnostic_movement}",
        f"Agent hypothesis: {args.hypothesis}",
        f"Chosen optimization direction: {args.direction}",
        f"Files inspected: {args.files_inspected}",
        f"Files modified: {args.files_modified}",
        f"Change summary: {args.change_summary}",
        f"Benchmark command: {args.benchmark_command}",
        f"Compile result: {compile_result}",
        f"Correctness result: {correctness_result}",
        "Metrics:",
    ]
    for key in METRIC_KEYS:
        lines.append(f"  {key}: {metrics.get(key, '')}")
    lines.extend(
        [
            f"Result: {args.result}",
            f"Agent diagnosis: {args.agent_diagnosis}",
            f"My diagnosis: {args.my_diagnosis}",
            f"Needed expert knowledge: {args.needed_expert_knowledge}",
            f"Patch / commit: {args.patch_or_commit}",
            "",
        ]
    )

    args.iterations.parent.mkdir(parents=True, exist_ok=True)
    with args.iterations.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
