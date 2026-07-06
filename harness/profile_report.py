#!/usr/bin/env python3
"""Build a MobileMoE profiling report from metrics and optional trace summary."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def load_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
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


def pick(data: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    return {key: data.get(key) for key in keys if key in data}


def missing(metrics: dict[str, Any], keys: list[str]) -> list[str]:
    return [key for key in keys if num(metrics, key) is None]


def build_report(
    metrics: dict[str, Any],
    trace_summary: dict[str, Any],
    manifest: dict[str, Any],
    detail_profile: dict[str, Any],
    label: str,
) -> dict[str, Any]:
    layer_breakdown = (
        detail_profile.get("adapter_specific_appendix", {})
        .get("mobile_moe_layer_breakdown", {})
    )
    layer_totals = (
        layer_breakdown.get("totals", {})
        if isinstance(layer_breakdown, dict)
        else {}
    )
    detail_rollup = {
        "available": bool(layer_totals),
        "source": "detail_profile.adapter_specific_appendix.mobile_moe_layer_breakdown.totals",
        "operator_timing_ms": pick(
            layer_totals,
            [
                "total_ms",
                "gpu_total_ms",
                "kernel_ms",
                "meta_ms",
                "download_ms",
            ],
        ),
        "transfer_mib": pick(
            layer_totals,
            [
                "core_upload_mib",
                "factor_upload_mib",
                "input_upload_mib",
                "download_mib",
                "req_page_touch_mib",
            ],
        ),
        "upload_attribution_ms": pick(
            layer_totals,
            [
                "core_upload_ms",
                "factor_upload_ms",
                "input_upload_ms",
                "download_ms",
                "req_mat_enqueue_ms",
                "req_mat_finish_ms",
            ],
        ),
        "materialization_service": pick(
            layer_totals,
            [
                "req_service_ms",
                "req_page_touch_ms",
                "req_mat_enqueue_ms",
                "req_mat_finish_ms",
                "req_mat_writes",
                "req_miss",
                "req_hit",
                "evict",
            ],
        ),
        "residency": pick(
            layer_totals,
            [
                "res_upload",
                "res_dup_upload",
            ],
        ),
    }
    required_metrics = [
        "decode_tok_s",
        "mib_per_token",
        "decode_req_miss",
        "decode_evict",
        "decode_req_service_ms",
        "decode_core_upload_mib",
    ]
    compute_metrics = [
        "decode_kernel_ms",
        "decode_kernel_events",
        "decode_kernel_total_ms",
    ]
    upload_attribution_metrics = [
        "decode_core_upload_ms",
        "decode_req_mat_enqueue_ms",
        "decode_req_mat_finish_ms",
        "decode_core_upload_mib",
        "decode_req_mat_writes",
    ]
    page_residency_metrics = [
        "decode_req_page_touch_ms",
        "decode_req_page_touch_mib",
        "upload_attr_pages_before",
        "upload_attr_resident_before",
        "upload_attr_pages_after",
        "upload_attr_resident_after",
    ]
    trace_present = bool(trace_summary)
    detail_present = bool(detail_profile)

    return {
        "label": label,
        "profile_kind": "mobile_moe_profile_report",
        "harness_role": "facts_only_no_bottleneck_decision",
        "sections": {
            "validity": pick(
                metrics,
                [
                    "compile_success",
                    "correct",
                    "generated_tokens",
                    "runs",
                    "ret",
                    "error",
                ],
            ),
            "throughput": pick(
                metrics,
                [
                    "decode_tok_s",
                    "prefill_tok_s",
                    "total_s",
                    "decode_s",
                    "tokens_per_s",
                ],
            ),
            "operator_timing": pick(
                metrics,
                [
                    "decode_total_ms",
                    "decode_gpu_total_ms",
                    "decode_upload_ms",
                    "decode_transfer_ms",
                    "decode_read_ms",
                    "decode_meta_ms",
                    "decode_download_ms",
                    "decode_hybrid_lines",
                ],
            ),
            "compute": pick(
                metrics,
                [
                    "decode_kernel_ms",
                    "decode_kernel_events",
                    "decode_kernel_total_ms",
                    "decode_kernel_gate_ms",
                    "decode_kernel_up_ms",
                    "decode_kernel_down_ms",
                    "decode_kernel_factor_ms",
                    "decode_kernel_silu_ms",
                    "decode_kernel_qdq_ms",
                    "decode_kernel_reduce_ms",
                    "decode_kernel_other_ms",
                ],
            ),
            "transfer": pick(
                metrics,
                [
                    "mib_per_token",
                    "upload_bytes",
                    "decode_core_upload_mib",
                    "decode_req_mat_mib",
                    "decode_req_payload_mib",
                    "decode_payload_weight_mib",
                    "decode_payload_scale_mib",
                    "decode_factor_upload_mib",
                    "decode_input_upload_mib",
                    "decode_download_mib",
                    "decode_req_mat_writes",
                    "decode_req_page_touch_mib",
                ],
            ),
            "upload_attribution": pick(
                metrics,
                [
                    "decode_core_upload_ms",
                    "decode_factor_upload_ms",
                    "decode_input_upload_ms",
                    "decode_meta_ms",
                    "decode_download_ms",
                    "decode_req_mat_enqueue_ms",
                    "decode_req_mat_finish_ms",
                    "decode_req_mat_writes",
                    "decode_core_upload_mib",
                    "decode_factor_upload_mib",
                    "decode_input_upload_mib",
                    "decode_download_mib",
                    "upload_attr_mincore_before_ms",
                    "upload_attr_mincore_after_ms",
                    "upload_attr_spans",
                    "upload_attr_mib",
                ],
            ),
            "page_residency": pick(
                metrics,
                [
                    "decode_req_page_touch_ms",
                    "decode_req_page_touch_mib",
                    "decode_arena_resident_mib",
                    "decode_slot_resident_mib",
                    "upload_attr_pages_before",
                    "upload_attr_resident_before",
                    "upload_attr_pages_after",
                    "upload_attr_resident_after",
                ],
            ),
            "cache": pick(
                metrics,
                [
                    "decode_req_miss",
                    "decode_req_hit",
                    "decode_evict",
                    "required_miss_count",
                    "eviction_churn",
                    "cache_hit_rate",
                ],
            ),
            "materialization_service": pick(
                metrics,
                [
                    "decode_req_service_ms",
                    "required_miss_wait_ms_per_token",
                    "decode_req_page_touch_ms",
                    "decode_req_mat_enqueue_ms",
                    "decode_req_mat_finish_ms",
                ],
            ),
            "residency_aggregate": pick(
                metrics,
                [
                    "res_probe",
                    "res_hit",
                    "res_miss",
                    "res_mat_req",
                    "res_upload",
                    "res_dup_upload",
                    "res_record",
                    "res_evict",
                    "res_base_record",
                    "res_sibling_missing",
                    "res_later_sibling_miss",
                    "res_later_sibling_hit",
                ],
            ),
            "state_trace": {
                "available": trace_present,
                **pick(
                    trace_summary,
                    [
                        "events",
                        "event_counts",
                        "action_counts",
                        "phase_counts",
                        "invalidation_counts",
                        "later_access_counts",
                        "derived_relation_counts",
                        "logical_keys_seen",
                        "physical_keys_seen",
                        "stable_physical_keys_seen",
                        "examples",
                        "derived_examples",
                    ],
                ),
            },
            "physical_logical_consistency": {
                "available": bool(trace_summary.get("physical_logical_consistency")),
                **(
                    trace_summary.get("physical_logical_consistency")
                    if isinstance(
                        trace_summary.get("physical_logical_consistency"), dict
                    )
                    else {}
                ),
            },
            "runtime_event_profile": {
                "available": detail_present,
                **pick(
                    detail_profile,
                    [
                        "runtime_event_profile",
                    ],
                ),
            },
            "detail_profile_rollup": detail_rollup,
            "qnn_context_timeline": {
                "available": bool(detail_profile.get("qnn_context_timeline")),
                **(
                    detail_profile.get("qnn_context_timeline")
                    if isinstance(detail_profile.get("qnn_context_timeline"), dict)
                    else {}
                ),
            },
            "lm_head_timeline": {
                "available": bool(detail_profile.get("lm_head_timeline")),
                **(
                    detail_profile.get("lm_head_timeline")
                    if isinstance(detail_profile.get("lm_head_timeline"), dict)
                    else {}
                ),
            },
            "async_overlap_profile": {
                "available": bool(detail_profile.get("async_overlap_profile")),
                **(
                    detail_profile.get("async_overlap_profile")
                    if isinstance(detail_profile.get("async_overlap_profile"), dict)
                    else {}
                ),
            },
            "adapter_specific_appendix": detail_profile.get(
                "adapter_specific_appendix", {}
            ),
            "thermal": pick(
                metrics,
                [
                    "peak_temp_skin_c_decode",
                    "peak_temp_battery_c_decode",
                    "start_temp_skin_c",
                    "start_temp_battery_c",
                    "end_temp_skin_c",
                    "end_temp_battery_c",
                ],
            ),
            "provenance": {
                **pick(
                    metrics,
                    [
                        "iteration_id",
                        "stage",
                        "profile",
                        "out_dir",
                    ],
                ),
                "adapter_manifest": manifest,
            },
        },
        "missing_observations": {
            "required_metrics": missing(metrics, required_metrics),
            "compute": missing(metrics, compute_metrics),
            "upload_attribution": missing(metrics, upload_attribution_metrics),
            "page_residency": missing(metrics, page_residency_metrics),
            "state_trace": [] if trace_present else ["state_trace_summary"],
            "runtime_event_profile": [] if detail_present else ["detail_profile"],
            "qnn_context_timeline": (
                []
                if detail_profile.get("qnn_context_timeline", {}).get("available")
                else ["qnn_context_log"]
            ),
            "lm_head_timeline": (
                []
                if detail_profile.get("lm_head_timeline", {}).get("available")
                else ["lm_head_summary"]
            ),
            "async_overlap_profile": (
                []
                if detail_profile.get("async_overlap_profile", {}).get("available")
                else ["qnn_context_log"]
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--trace-summary", type=Path)
    parser.add_argument("--detail-profile", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--label")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    metrics = load_json(args.metrics)
    trace_summary = load_json(args.trace_summary)
    detail_profile = load_json(args.detail_profile)
    manifest = load_json(args.manifest)
    label = args.label or str(metrics.get("iteration_id") or args.metrics.parent.name)
    report = build_report(metrics, trace_summary, manifest, detail_profile, label)
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
