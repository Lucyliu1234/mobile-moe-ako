#!/usr/bin/env python3
"""Build generic runtime-event profiling tables from logs and state events."""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ANSI_RE = re.compile(r"\x1b\[[0-9;:]*m")
HYBRID_COLD_RE = re.compile(r"\[TD-RUN\]\[hybrid-cold\]\s*(.*)")
KV_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=([^\s]+)")


def parse_value(raw: str) -> int | float | str:
    value = raw.rstrip(",")
    for suffix in ("MiB", "KiB", "ms"):
        if value.endswith(suffix):
            value = value[: -len(suffix)]
            break
    try:
        if re.fullmatch(r"[-+]?\d+", value):
            return int(value)
        if re.fullmatch(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)", value):
            return float(value)
    except ValueError:
        pass
    return raw


def num(value: Any) -> float:
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    return 0.0


def event_key(event: dict[str, Any], key: str) -> str:
    value = event.get(key)
    if value in (None, ""):
        return "unknown"
    return str(value)


def read_jsonl(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict):
                rows.append(row)
    return rows


def parse_hybrid_cold_log(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    in_decode_phase = False
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = ANSI_RE.sub("", raw_line)
        if "[TD-RUN][debug] generate: prefill done" in line:
            in_decode_phase = True
        match = HYBRID_COLD_RE.search(line)
        if not (in_decode_phase and match):
            continue
        row: dict[str, Any] = {}
        for key, raw_value in KV_RE.findall(match.group(1)):
            value = parse_value(raw_value)
            if isinstance(value, (int, float)) and math.isfinite(float(value)):
                row[key] = value
        if row:
            rows.append(row)
    return rows


def top_items(groups: dict[str, dict[str, Any]], sort_key: str, limit: int) -> list[dict[str, Any]]:
    return sorted(
        groups.values(),
        key=lambda item: (num(item.get(sort_key)), num(item.get("bytes")), str(item.get("key"))),
        reverse=True,
    )[:limit]


def add_event(group: dict[str, Any], event: dict[str, Any]) -> None:
    name = event_key(event, "event")
    action = event_key(event, "action")
    later_access = event_key(event, "later_access")
    group["events"] = int(group.get("events", 0)) + 1
    group[f"event_{name}"] = int(group.get(f"event_{name}", 0)) + 1
    group[f"action_{action}"] = int(group.get(f"action_{action}", 0)) + 1
    if name == "later_access":
        group[f"later_{later_access}"] = int(group.get(f"later_{later_access}", 0)) + 1
    if event.get("duplicate") is True:
        group["duplicate_events"] = int(group.get("duplicate_events", 0)) + 1
    if event.get("duplicate_by_stable_key") is True:
        group["duplicate_by_stable_key"] = int(group.get("duplicate_by_stable_key", 0)) + 1
    if event.get("was_covered_by_previous_upload") is True:
        group["covered_later_or_record_events"] = int(
            group.get("covered_later_or_record_events", 0)
        ) + 1
    group["bytes"] = num(group.get("bytes")) + num(event.get("bytes"))


def summarize_events(events: list[dict[str, Any]], limit: int) -> dict[str, Any]:
    by_action: dict[str, dict[str, Any]] = {}
    by_phase: dict[str, dict[str, Any]] = {}
    by_logical: dict[str, dict[str, Any]] = {}
    by_physical: dict[str, dict[str, Any]] = {}
    by_stable_physical: dict[str, dict[str, Any]] = {}
    coverage_sizes = Counter()
    reuse_skip = Counter()

    for event in events:
        action = event_key(event, "action")
        phase = event_key(event, "phase")
        logical = event_key(event, "logical_key")
        physical = event_key(event, "physical_key")
        stable = event_key(event, "stable_physical_key")
        covered = event.get("covered_logical_keys")
        if isinstance(covered, list):
            coverage_sizes[len(covered)] += 1
        if event.get("skip_physical") is True:
            reuse_skip["skip_physical_true"] += 1
        elif event.get("skip_physical") is False:
            reuse_skip["skip_physical_false"] += 1
        if event.get("was_covered_by_previous_upload") is True:
            reuse_skip["covered_by_previous_action"] += 1
        if event_key(event, "event") == "later_access":
            reuse_skip[f"later_access_{event_key(event, 'later_access')}"] += 1

        for groups, key, extra in [
            (by_action, action, {"physical_action": action}),
            (by_phase, phase, {"phase": phase}),
            (by_logical, logical, {"logical_request_id": logical}),
            (
                by_physical,
                physical,
                {
                    "resource_id": physical,
                    "resource_id_kind": "physical_key",
                    "adapter_layer": event.get("layer"),
                    "adapter_expert": event.get("expert"),
                    "adapter_slot_id": event.get("slot_id"),
                },
            ),
            (
                by_stable_physical,
                stable,
                {
                    "resource_id": stable,
                    "resource_id_kind": "stable_physical_key",
                    "adapter_layer": event.get("layer"),
                    "adapter_expert": event.get("expert"),
                    "adapter_slot_id": event.get("slot_id"),
                },
            ),
        ]:
            if key == "unknown":
                continue
            group = groups.setdefault(key, {"key": key, **extra})
            add_event(group, event)

    return {
        "events": len(events),
        "coverage_size_counts": dict(sorted(coverage_sizes.items())),
        "reuse_skip_effectiveness": dict(sorted(reuse_skip.items())),
        "phase_path_breakdown": top_items(by_phase, "events", limit),
        "physical_action_hotspots": top_items(by_action, "events", limit),
        "logical_request_hotspots": top_items(by_logical, "events", limit),
        "resource_lifetime_hotspots": top_items(by_stable_physical, "events", limit),
        "physical_resource_hotspots": top_items(by_physical, "events", limit),
        "physical_action_bytes_hotspots": top_items(by_physical, "bytes", limit),
        "stable_resource_hotspots": top_items(
            by_stable_physical, "events", limit
        ),
    }


def summarize_adapter_event_appendix(
    events: list[dict[str, Any]], limit: int
) -> dict[str, Any]:
    by_layer: dict[str, dict[str, Any]] = {}
    by_projection: dict[str, dict[str, Any]] = {}

    for event in events:
        layer = event_key(event, "layer")
        projection = event_key(event, "projection")
        for groups, key, extra in [
            (by_layer, layer, {"layer": event.get("layer")}),
            (by_projection, projection, {"projection": projection}),
        ]:
            if key == "unknown":
                continue
            group = groups.setdefault(key, {"key": key, **extra})
            add_event(group, event)

    return {
        "top_layers_by_event_count": top_items(by_layer, "events", limit),
        "top_layers_by_event_bytes": top_items(by_layer, "bytes", limit),
        "top_projections_by_event_count": top_items(by_projection, "events", limit),
    }


def summarize_hybrid_layers(rows: list[dict[str, Any]], limit: int) -> dict[str, Any]:
    if not rows:
        return {"available": False, "layers": 0}

    by_layer: dict[str, dict[str, Any]] = defaultdict(dict)
    numeric_keys = [
        "total_ms",
        "gpu_total_ms",
        "core_upload_ms",
        "factor_upload_ms",
        "input_upload_ms",
        "meta_ms",
        "download_ms",
        "kernel_ms",
        "req_service_ms",
        "req_page_touch_ms",
        "req_mat_enqueue_ms",
        "req_mat_finish_ms",
        "core_upload_mib",
        "factor_upload_mib",
        "input_upload_mib",
        "download_mib",
        "req_page_touch_mib",
        "req_mat_writes",
        "req_miss",
        "req_hit",
        "evict",
        "res_upload",
        "res_dup_upload",
    ]
    for row in rows:
        layer = str(row.get("layer", "unknown"))
        if layer == "unknown":
            continue
        group = by_layer.setdefault(layer, {"key": layer, "layer": row.get("layer"), "records": 0})
        group["records"] = int(group.get("records", 0)) + 1
        for key in numeric_keys:
            group[key] = num(group.get(key)) + num(row.get(key))

    def top(sort_key: str) -> list[dict[str, Any]]:
        return sorted(
            by_layer.values(),
            key=lambda item: (num(item.get(sort_key)), num(item.get("core_upload_mib")), str(item.get("key"))),
            reverse=True,
        )[:limit]

    return {
        "available": True,
        "layers": len(by_layer),
        "records": len(rows),
        "top_layers_by_total_ms": top("total_ms"),
        "top_layers_by_core_upload_ms": top("core_upload_ms"),
        "top_layers_by_page_touch_ms": top("req_page_touch_ms"),
        "top_layers_by_core_upload_mib": top("core_upload_mib"),
        "top_layers_by_req_miss": top("req_miss"),
    }


def build_detail_profile(
    events: list[dict[str, Any]],
    hybrid_rows: list[dict[str, Any]],
    label: str,
    limit: int,
) -> dict[str, Any]:
    return {
        "label": label,
        "profile_kind": "generic_runtime_event_detail_profile",
        "harness_role": "facts_only_ranked_hotspots_no_bottleneck_decision",
        "runtime_event_profile": summarize_events(events, limit),
        "adapter_specific_appendix": {
            "mobile_moe_event_breakdown": summarize_adapter_event_appendix(events, limit),
            "mobile_moe_layer_breakdown": summarize_hybrid_layers(hybrid_rows, limit),
        },
        "missing_observations": {
            "state_trace_jsonl": [] if events else ["state_trace_jsonl"],
            "decode_hybrid_layer_log": [] if hybrid_rows else ["decode_hybrid_layer_log"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-trace", type=Path)
    parser.add_argument("--log", type=Path)
    parser.add_argument("--label", default="detail_profile")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    events = read_jsonl(args.state_trace)
    hybrid_rows = parse_hybrid_cold_log(args.log)
    report = build_detail_profile(events, hybrid_rows, args.label, args.limit)
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
