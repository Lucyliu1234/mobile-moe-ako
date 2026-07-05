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
QNN_PRELOAD_RE = re.compile(
    r"QNNBackend::preloadContextAsync '([^']+)'\s+slot=(\d+)\s+retrieveContext\s+(enter|done)(?:\s+ok=(\w+))?"
)
QNN_ACTIVATE_RE = re.compile(r"QNNBackend::activatePreloadedContext '([^']+)':\s*(.*)")
QNN_LOAD_BEGIN_RE = re.compile(r"QNNBackend::loadContext begin path=([^\s]+)")
QNN_LOAD_SATISFIED_RE = re.compile(
    r"QNNBackend::loadContext '([^']+)'\s+satisfied by async preloaded context"
)
LM_HEAD_RE = re.compile(r"External lm_head\s*:\s*(.*)")


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


def parse_qnn_context_log(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for lineno, raw_line in enumerate(
        path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1
    ):
        line = ANSI_RE.sub("", raw_line)

        preload = QNN_PRELOAD_RE.search(line)
        if preload:
            context_path, slot, state, ok = preload.groups()
            events.append(
                {
                    "line": lineno,
                    "event": "preload_retrieve",
                    "context": context_path,
                    "slot": int(slot),
                    "stage": state,
                    "state": state,
                    "ok": ok,
                }
            )
            continue

        activate = QNN_ACTIVATE_RE.search(line)
        if activate:
            context_path, detail = activate.groups()
            event: dict[str, Any] = {
                "line": lineno,
                "event": "activate",
                "context": context_path,
                "detail": detail,
            }
            if "find slot done" in detail:
                event["stage"] = "find_slot"
                if m := re.search(
                    r"us=(\d+)\s+slot=(-?\d+)\s+wait_joinable=(\d+)", detail
                ):
                    event["us"] = int(m.group(1))
                    event["slot"] = int(m.group(2))
                    event["wait_joinable"] = int(m.group(3))
            elif "wait preload thread enter" in detail:
                event["stage"] = "wait_preload_enter"
            elif "wait preload thread done" in detail:
                event["stage"] = "wait_preload"
                if m := re.search(r"us=(\d+)", detail):
                    event["us"] = int(m.group(1))
            elif "extract preloaded context done" in detail:
                event["stage"] = "extract_preloaded"
                if m := re.search(r"us=(\d+)\s+models=(\d+)", detail):
                    event["us"] = int(m.group(1))
                    event["models"] = int(m.group(2))
            elif "clearRegisteredMemHandles enter" in detail:
                event["stage"] = "clear_registered_enter"
            elif "clearRegisteredMemHandles done" in detail:
                event["stage"] = "clear_registered"
                if m := re.search(r"us=(\d+)", detail):
                    event["us"] = int(m.group(1))
            elif "contextFree enter" in detail:
                event["stage"] = "context_free_enter"
            elif "contextFree done" in detail:
                event["stage"] = "context_free"
                if m := re.search(r"us=(\d+)", detail):
                    event["us"] = int(m.group(1))
            elif "rebuild graph map done" in detail:
                event["stage"] = "rebuild_graph_map"
                if m := re.search(r"us=(\d+)\s+entries=(\d+)", detail):
                    event["us"] = int(m.group(1))
                    event["entries"] = int(m.group(2))
            elif "setQNNPointer done" in detail:
                event["stage"] = "set_qnn_pointer"
                if m := re.search(r"us=(\d+)", detail):
                    event["us"] = int(m.group(1))
            elif "activated with" in detail:
                event["stage"] = "activated"
            elif "total done" in detail:
                event["stage"] = "total"
                if m := re.search(r"us=(\d+)", detail):
                    event["us"] = int(m.group(1))
            else:
                event["stage"] = "other"
            events.append(event)
            continue

        load_begin = QNN_LOAD_BEGIN_RE.search(line)
        if load_begin:
            events.append(
                {
                    "line": lineno,
                    "event": "load_context",
                    "stage": "begin",
                    "context": load_begin.group(1).strip("'\""),
                }
            )
            continue

        load_satisfied = QNN_LOAD_SATISFIED_RE.search(line)
        if load_satisfied:
            events.append(
                {
                    "line": lineno,
                    "event": "load_context",
                    "stage": "satisfied_by_async_preload",
                    "context": load_satisfied.group(1),
                }
            )
    return events


def parse_lm_head_log(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = ANSI_RE.sub("", raw_line)
        match = LM_HEAD_RE.search(line)
        if not match:
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


def summary_stats(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "sum": None, "mean": None, "max": None}
    return {
        "count": len(values),
        "sum": sum(values),
        "mean": sum(values) / len(values),
        "max": max(values),
    }


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


def summarize_qnn_context_timeline(
    events: list[dict[str, Any]], limit: int
) -> dict[str, Any]:
    if not events:
        return {"available": False, "events": 0}

    by_stage_us: dict[str, list[float]] = defaultdict(list)
    by_context: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"events": 0, "us_total": 0.0}
    )
    counts = Counter()
    slots = Counter()

    for event in events:
        name = event_key(event, "event")
        stage = event_key(event, "stage")
        context = event_key(event, "context")
        counts[f"{name}:{stage}"] += 1
        if event.get("slot") is not None:
            slots[str(event.get("slot"))] += 1
        us = num(event.get("us"))
        if event.get("us") is not None:
            by_stage_us[stage].append(us)
        if context != "unknown":
            group = by_context[context]
            group["key"] = context
            group["context"] = context
            group["events"] = int(group.get("events", 0)) + 1
            group["us_total"] = num(group.get("us_total")) + us
            if stage != "unknown":
                group[f"stage_{stage}"] = int(group.get(f"stage_{stage}", 0)) + 1
                if event.get("us") is not None:
                    group[f"us_{stage}"] = num(group.get(f"us_{stage}")) + us

    stage_summary = {
        stage: summary_stats(values)
        for stage, values in sorted(by_stage_us.items())
    }
    top_contexts = sorted(
        by_context.values(),
        key=lambda item: (num(item.get("us_total")), int(item.get("events", 0))),
        reverse=True,
    )[:limit]

    return {
        "available": True,
        "events": len(events),
        "event_stage_counts": dict(sorted(counts.items())),
        "slot_event_counts": dict(sorted(slots.items())),
        "stage_us": stage_summary,
        "top_contexts_by_us": top_contexts,
    }


def summarize_async_overlap(events: list[dict[str, Any]]) -> dict[str, Any]:
    if not events:
        return {"available": False, "events": 0}

    preload_enter = Counter()
    preload_done = Counter()
    load_begin = Counter()
    load_satisfied = Counter()
    wait_joinable = Counter()
    wait_us: list[float] = []
    total_us: list[float] = []
    blocked_contexts: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"wait_events": 0, "wait_us": 0.0}
    )

    for event in events:
        context = event_key(event, "context")
        name = event_key(event, "event")
        stage = event_key(event, "stage")
        if name == "preload_retrieve" and event.get("state") == "enter":
            preload_enter[context] += 1
        elif name == "preload_retrieve" and event.get("state") == "done":
            preload_done[context] += 1
        elif name == "load_context" and stage == "begin":
            load_begin[context] += 1
        elif name == "load_context" and stage == "satisfied_by_async_preload":
            load_satisfied[context] += 1
        elif stage == "find_slot":
            wait_joinable[str(event.get("wait_joinable", "unknown"))] += 1
        elif stage == "wait_preload":
            us = num(event.get("us"))
            wait_us.append(us)
            if context != "unknown":
                blocked = blocked_contexts[context]
                blocked["key"] = context
                blocked["context"] = context
                blocked["wait_events"] = int(blocked.get("wait_events", 0)) + 1
                blocked["wait_us"] = num(blocked.get("wait_us")) + us
        elif stage == "total":
            total_us.append(num(event.get("us")))

    contexts = sorted(
        set(preload_enter) | set(preload_done) | set(load_begin) | set(load_satisfied)
    )
    by_context = []
    for context in contexts:
        by_context.append(
            {
                "context": context,
                "preload_enter": preload_enter.get(context, 0),
                "preload_done": preload_done.get(context, 0),
                "load_begin": load_begin.get(context, 0),
                "load_satisfied_by_async": load_satisfied.get(context, 0),
                "preload_done_without_satisfied_load": max(
                    0, preload_done.get(context, 0) - load_satisfied.get(context, 0)
                ),
            }
        )

    top_blocked = sorted(
        blocked_contexts.values(),
        key=lambda item: (num(item.get("wait_us")), int(item.get("wait_events", 0))),
        reverse=True,
    )[:12]

    return {
        "available": True,
        "events": len(events),
        "contexts": len(contexts),
        "wait_joinable_counts": dict(sorted(wait_joinable.items())),
        "wait_preload_us": summary_stats(wait_us),
        "activate_total_us": summary_stats(total_us),
        "by_context": by_context[:24],
        "top_blocking_contexts_by_wait_us": top_blocked,
    }


def summarize_lm_head_timeline(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"available": False, "records": 0}

    numeric_keys = sorted({key for row in rows for key in row})
    totals: dict[str, float] = {}
    means: dict[str, float] = {}
    maxima: dict[str, float] = {}
    for key in numeric_keys:
        values = [num(row.get(key)) for row in rows if key in row]
        if not values:
            continue
        totals[key] = sum(values)
        means[key] = sum(values) / len(values)
        maxima[key] = max(values)

    time_keys = ["upload", "kernel", "read", "total"]
    mib_keys = ["weight_up", "input_up", "read"]
    return {
        "available": True,
        "records": len(rows),
        "totals": totals,
        "means": means,
        "maxima": maxima,
        "time_ms_totals": {key: totals[key] for key in time_keys if key in totals},
        "data_mib_totals": {key: totals[key] for key in mib_keys if key in totals},
        "latest": rows[-1],
    }


def build_detail_profile(
    events: list[dict[str, Any]],
    hybrid_rows: list[dict[str, Any]],
    qnn_events: list[dict[str, Any]],
    lm_head_rows: list[dict[str, Any]],
    label: str,
    limit: int,
) -> dict[str, Any]:
    return {
        "label": label,
        "profile_kind": "generic_runtime_event_detail_profile",
        "harness_role": "facts_only_ranked_hotspots_no_bottleneck_decision",
        "runtime_event_profile": summarize_events(events, limit),
        "qnn_context_timeline": summarize_qnn_context_timeline(qnn_events, limit),
        "lm_head_timeline": summarize_lm_head_timeline(lm_head_rows),
        "async_overlap_profile": summarize_async_overlap(qnn_events),
        "adapter_specific_appendix": {
            "mobile_moe_event_breakdown": summarize_adapter_event_appendix(events, limit),
            "mobile_moe_layer_breakdown": summarize_hybrid_layers(hybrid_rows, limit),
        },
        "missing_observations": {
            "state_trace_jsonl": [] if events else ["state_trace_jsonl"],
            "decode_hybrid_layer_log": [] if hybrid_rows else ["decode_hybrid_layer_log"],
            "qnn_context_log": [] if qnn_events else ["qnn_context_log"],
            "lm_head_summary": [] if lm_head_rows else ["lm_head_summary"],
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
    qnn_events = parse_qnn_context_log(args.log)
    lm_head_rows = parse_lm_head_log(args.log)
    report = build_detail_profile(
        events, hybrid_rows, qnn_events, lm_head_rows, args.label, args.limit
    )
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
