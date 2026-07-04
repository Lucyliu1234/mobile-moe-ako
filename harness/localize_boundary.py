#!/usr/bin/env python3
"""Generate a bounded optimization task from normalized MobileMoE metrics."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


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


def positive(data: dict[str, Any], key: str) -> bool:
    value = num(data, key)
    return value is not None and value > 0


def localize(metrics: dict[str, Any], label: str) -> dict[str, Any]:
    high_transfer = positive(metrics, "mib_per_token") or positive(metrics, "decode_core_upload_mib")
    high_miss = positive(metrics, "decode_req_miss") or positive(metrics, "required_miss_count")
    high_service = positive(metrics, "decode_req_service_ms") or positive(metrics, "required_miss_wait_ms_per_token")
    has_res_trace = positive(metrics, "res_probe")

    if high_transfer and high_miss:
        bottleneck = "transfer_residency"
        selected_task = "reduce repeated required physical payload movement or service in the fixed decode workload"
        physical_event = "required-path payload materialization, page-touch, and device upload/write"
        logical_decision = "runtime cache/residency lookup or admission decision before materialization"
        allowed = [
            "residency lookup state",
            "physical resource identity keys",
            "materialization skip/admission",
            "eviction and effect lifetime",
            "required-path upload batching when it changes total service",
        ]
        forbidden = [
            "benchmark/parser/correctness semantics",
            "logical counter-only edits",
            "generic kernel math",
            "page-touch micro-edits without total-service proof",
            "generic scheduling/prewarm unless required physical work is unchanged and scheduling is the selected hypothesis",
        ]
        must_inspect = [
            "read site before materialization/upload",
            "write/update site after physical action",
            "eviction or invalidation site",
            "mapping between logical request and physical payload key",
        ]
        acceptance = [
            "decode_tok_s",
            "mib_per_token",
            "decode_core_upload_mib",
            "decode_req_mat_writes",
            "decode_req_service_ms",
        ]
        reject_if = "logical hit/miss counters improve but physical bytes/write/service metrics do not move"
    elif high_service:
        bottleneck = "materialization_service"
        selected_task = "reduce required-miss service time without shifting latency between subcounters"
        physical_event = "blocking service work on the fixed decode critical path"
        logical_decision = "materialization or synchronization path selected for a required request"
        allowed = ["service decomposition", "queue wait", "synchronization", "upload/page-fault attribution"]
        forbidden = ["counter-only edits", "parser changes", "physical-transfer claims without byte/write movement"]
        must_inspect = ["service start/end sites", "enqueue and finish waits", "blocking synchronization site"]
        acceptance = ["decode_tok_s", "decode_req_service_ms", "decode_req_mat_enqueue_ms", "decode_req_mat_finish_ms"]
        reject_if = "one service subcounter drops while another absorbs the cost"
    else:
        bottleneck = "missing_diagnostics"
        selected_task = "add minimal diagnostics before optimization"
        physical_event = "unknown"
        logical_decision = "unknown"
        allowed = ["diagnostic counters that preserve benchmark semantics"]
        forbidden = ["optimization patches before a bounded task exists"]
        must_inspect = ["missing metric source", "benchmark log parser", "runtime timing/counter site"]
        acceptance = ["new counters identify a smaller bounded task"]
        reject_if = "diagnostic changes alter correctness, prompt, model work, or parser semantics"

    state_relation_required = bottleneck in {"transfer_residency", "materialization_service"}
    observation_gaps = []
    if state_relation_required and not has_res_trace:
        observation_gaps.append("state-level logical request vs physical action relation is not traced")
    if state_relation_required and not positive(metrics, "decode_req_mat_writes"):
        observation_gaps.append("physical write/action count is missing")

    return {
        "label": label,
        "bottleneck_class": bottleneck,
        "selected_bounded_task": selected_task,
        "expensive_physical_event": physical_event,
        "triggering_logical_decision": logical_decision,
        "allowed_edit_surface": allowed,
        "forbidden_first_surface": forbidden,
        "must_inspect_read_write_sites": must_inspect,
        "expected_metric_movement": acceptance,
        "falsification_rule": reject_if,
        "state_relation_required": state_relation_required,
        "observation_gaps": observation_gaps,
        "evidence": {
            key: metrics.get(key)
            for key in [
                "decode_tok_s",
                "mib_per_token",
                "decode_core_upload_mib",
                "decode_req_miss",
                "decode_req_hit",
                "decode_evict",
                "decode_req_service_ms",
                "decode_req_mat_writes",
                "res_probe",
                "res_upload",
                "res_dup_upload",
            ]
            if key in metrics
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--label", default=None)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    metrics = load(args.metrics)
    label = args.label or str(metrics.get("iteration_id") or args.metrics.parent.name)
    result = localize(metrics, label)
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
