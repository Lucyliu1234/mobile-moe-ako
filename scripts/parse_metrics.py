#!/usr/bin/env python3
"""Normalize MobileMoE benchmark summary.jsonl into one metrics JSON."""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


def number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def avg(rows: list[dict[str, Any]], key: str) -> float | None:
    vals = [v for row in rows if (v := number(row.get(key))) is not None]
    return mean(vals) if vals else None


def total(rows: list[dict[str, Any]], key: str) -> float | None:
    vals = [v for row in rows if (v := number(row.get(key))) is not None]
    return sum(vals) if vals else None


def first_number(rows: list[dict[str, Any]], *keys: str) -> float | None:
    for row in rows:
        for key in keys:
            value = number(row.get(key))
            if value is not None:
                return value
    return None


def total_any(rows: list[dict[str, Any]], *keys: str) -> float | None:
    vals: list[float] = []
    for row in rows:
        for key in keys:
            value = number(row.get(key))
            if value is not None:
                vals.append(value)
                break
    return sum(vals) if vals else None


def avg_any(rows: list[dict[str, Any]], *keys: str) -> float | None:
    vals: list[float] = []
    for row in rows:
        for key in keys:
            value = number(row.get(key))
            if value is not None:
                vals.append(value)
                break
    return mean(vals) if vals else None


def all_correct(rows: list[dict[str, Any]]) -> bool | None:
    if not rows:
        return None

    saw_guard = False
    for row in rows:
        ret = row.get("ret")
        if ret is not None:
            saw_guard = True
            if int(ret) != 0:
                return False

        generated = number(row.get("generated"))
        requested = number(row.get("decode_tokens_requested"))
        if requested is not None:
            saw_guard = True
            if generated is None or int(generated) != int(requested):
                return False

    return True if saw_guard else None


def load_baseline_decode_tok_s(path: Path | None) -> float | None:
    if path is None:
        return None
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return number(data.get("decode_tok_s"))


def build_metrics(args: argparse.Namespace, rows: list[dict[str, Any]]) -> dict[str, Any]:
    load_mb_total = total_any(
        rows,
        "edgemoe_demand_load_mb",
        "hybrid_core_up",
        "decode_hybrid_core_upload_mib",
        "decode_hybrid_req_mat_mib",
    )
    upload_bytes = load_mb_total * 1024 * 1024 if load_mb_total is not None else None
    generated = total(rows, "generated")
    decode_tok_s = avg(rows, "decode_tok_s")
    baseline_decode_tok_s = load_baseline_decode_tok_s(args.baseline_metrics)
    speedup_vs_baseline = (
        decode_tok_s / baseline_decode_tok_s
        if decode_tok_s is not None and baseline_decode_tok_s not in (None, 0)
        else None
    )

    mib_per_token = avg_any(
        rows,
        "uploaded_expert_mib_per_token_metric",
        "uploaded_expert_mib_per_token_est",
        "overall_uploaded_expert_mib_per_token_metric",
    )
    if mib_per_token is None and load_mb_total is not None and generated:
        mib_per_token = load_mb_total / generated

    return {
        "stage": args.stage,
        "iteration_id": args.iteration_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "compile_success": bool(args.compile_success),
        "correct": all_correct(rows),
        "runs": len(rows),
        "generated_tokens": generated,
        "decode_tok_s": decode_tok_s,
        "baseline_decode_tok_s": baseline_decode_tok_s,
        "speedup_vs_baseline": speedup_vs_baseline,
        "mib_per_token": mib_per_token,
        "required_miss_count": total_any(
            rows,
            "edgemoe_demand_misses",
            "hybrid_req_miss",
            "decode_hybrid_req_miss",
        ),
        "upload_bytes": upload_bytes,
        "prewarm_hit_rate": avg_any(
            rows,
            "prefetch_already_loaded_rate",
            "hybrid_pre_hit_rate",
        ),
        "eviction_churn": total_any(
            rows,
            "edgemoe_demand_evicts",
            "hybrid_evictions",
            "decode_hybrid_evict",
        ),
        "cache_hit_rate": avg_any(
            rows,
            "cache_hit_rate",
            "metric_required_hit_rate",
            "overall_metric_required_hit_rate",
        ),
        "required_miss_wait_ms_per_token": avg_any(
            rows,
            "required_miss_service_ms_per_token_est",
            "required_miss_service_ms_per_token_metric",
            "overall_required_miss_service_ms_per_token_metric",
        ),
        "decode_req_page_touch_ms": avg(rows, "decode_hybrid_req_page_touch_ms"),
        "decode_req_mat_enqueue_ms": avg(rows, "decode_hybrid_req_mat_enqueue_ms"),
        "decode_req_mat_finish_ms": avg(rows, "decode_hybrid_req_mat_finish_ms"),
        "decode_req_service_ms": avg(rows, "decode_hybrid_req_service_ms"),
        "decode_req_mat_writes": avg(rows, "decode_hybrid_req_mat_writes"),
        "decode_req_page_touch_mib": avg(rows, "decode_hybrid_req_page_touch_mib"),
        "decode_core_upload_mib": avg(rows, "decode_hybrid_core_upload_mib"),
        "decode_req_miss": total(rows, "decode_hybrid_req_miss"),
        "decode_req_hit": total(rows, "decode_hybrid_req_hit"),
        "decode_evict": total(rows, "decode_hybrid_evict"),
        "res_probe": total(rows, "decode_hybrid_res_probe"),
        "res_hit": total(rows, "decode_hybrid_res_hit"),
        "res_miss": total(rows, "decode_hybrid_res_miss"),
        "res_mat_req": total(rows, "decode_hybrid_res_mat_req"),
        "res_upload": total(rows, "decode_hybrid_res_upload"),
        "res_dup_upload": total(rows, "decode_hybrid_res_dup_upload"),
        "res_record": total(rows, "decode_hybrid_res_record"),
        "res_evict": total(rows, "decode_hybrid_res_evict"),
        "res_base_record": total(rows, "decode_hybrid_res_base_record"),
        "res_sibling_missing": total(rows, "decode_hybrid_res_sibling_missing"),
        "res_later_sibling_miss": total(
            rows, "decode_hybrid_res_later_sibling_miss"
        ),
        "res_later_sibling_hit": total(
            rows, "decode_hybrid_res_later_sibling_hit"
        ),
        "energy_j_per_token_decode": avg(rows, "energy_j_per_token_decode"),
        "peak_temp_skin_c_decode": avg(rows, "peak_temp_skin_c_decode"),
        "source_summary": str(args.summary),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, required=True, help="Path to summary.jsonl")
    parser.add_argument("--stage", required=True)
    parser.add_argument("--iteration-id", required=True)
    parser.add_argument("--compile-success", type=int, choices=(0, 1), default=1)
    parser.add_argument("--baseline-metrics", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    rows = read_jsonl(args.summary)
    metrics = build_metrics(args, rows)
    text = json.dumps(metrics, ensure_ascii=False, sort_keys=True)
    print(text)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
