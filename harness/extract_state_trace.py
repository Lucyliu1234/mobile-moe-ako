#!/usr/bin/env python3
"""Extract sampled state-relation events from MobileMoE runtime logs."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PREFIX = "[TD-RES-TRACE]"


def read_events(log_path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if PREFIX not in line:
            continue
        payload = line.split(PREFIX, 1)[1].strip()
        if not payload:
            continue
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            events.append(event)
    return events


def event_key(event: dict[str, Any], key: str) -> str:
    value = event.get(key)
    if value in (None, ""):
        return "unknown"
    return str(value)


def bool_value(event: dict[str, Any], key: str) -> bool:
    value = event.get(key)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return bool(value)


def summarize(events: list[dict[str, Any]], max_examples: int) -> dict[str, Any]:
    event_counts = Counter(event_key(event, "event") for event in events)
    action_counts = Counter(event_key(event, "action") for event in events)
    phase_counts = Counter(event_key(event, "phase") for event in events)
    logical_counts = Counter(event_key(event, "logical_key") for event in events)
    physical_counts = Counter(event_key(event, "physical_key") for event in events)
    stable_physical_counts = Counter(
        event_key(event, "stable_physical_key") for event in events
    )
    invalidation_counts = Counter(
        event_key(event, "invalidated_by") for event in events
        if event_key(event, "event") == "evict"
    )
    later_access_counts = Counter(
        event_key(event, "later_access") for event in events
        if event_key(event, "event") == "later_access"
    )

    by_physical: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_stable_physical: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_logical: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        by_physical[event_key(event, "physical_key")].append(event)
        by_stable_physical[event_key(event, "stable_physical_key")].append(event)
        by_logical[event_key(event, "logical_key")].append(event)

    derived_counts: Counter[str] = Counter()
    derived_examples: list[dict[str, Any]] = []
    evicted_stable: set[str] = set()
    evicted_physical: set[str] = set()
    for event in events:
        name = event_key(event, "event")
        physical_key = event_key(event, "physical_key")
        stable_key = event_key(event, "stable_physical_key")
        if name == "evict":
            if stable_key != "unknown":
                evicted_stable.add(stable_key)
            if physical_key != "unknown":
                evicted_physical.add(physical_key)
            if physical_key != "unknown" or stable_key != "unknown":
                derived_counts["keyed_evict"] += 1
            continue
        if name in {"upload", "repeat_upload"}:
            if name == "repeat_upload" or bool_value(event, "duplicate"):
                derived_counts["repeat_upload_by_physical_key"] += 1
            if bool_value(event, "duplicate_by_stable_key"):
                derived_counts["repeat_upload_by_stable_key"] += 1
            continue
        if name == "later_access" and event.get("later_access") == "miss":
            was_covered = bool_value(event, "was_covered_by_previous_upload")
            if was_covered:
                if stable_key != "unknown" and stable_key in evicted_stable:
                    relation = "later_miss_after_keyed_evict"
                elif physical_key != "unknown" and physical_key in evicted_physical:
                    relation = "later_miss_after_keyed_evict"
                else:
                    relation = "later_miss_before_keyed_evict"
                derived_counts[relation] += 1
                if len(derived_examples) < max_examples:
                    derived_examples.append(
                        {
                            "relation": relation,
                            "logical_key": event_key(event, "logical_key"),
                            "physical_key": physical_key,
                            "stable_physical_key": stable_key,
                            "slot_id": event.get("slot_id"),
                            "later_access": event.get("later_access"),
                            "covered_logical_keys": event.get(
                                "covered_logical_keys", []
                            ),
                        }
                    )
            else:
                derived_counts["later_miss_without_known_coverage"] += 1

    examples: list[dict[str, Any]] = []
    for physical_key, group in by_physical.items():
        if physical_key == "unknown":
            continue
        names = [event_key(event, "event") for event in group]
        later = [
            {
                "logical_key": event_key(event, "logical_key"),
                "later_access": event.get("later_access"),
                "event": event_key(event, "event"),
            }
            for event in group
            if event.get("later_access") is not None
            or event_key(event, "event") in {"later_access", "repeat_upload"}
        ]
        covered: list[str] = []
        for event in group:
            value = event.get("covered_logical_keys")
            if isinstance(value, list):
                covered.extend(str(item) for item in value)
        examples.append(
            {
                "physical_key": physical_key,
                "events": names,
                "event_count": len(group),
                "covered_logical_keys": sorted(set(covered)),
                "logical_keys": sorted(
                    {event_key(event, "logical_key") for event in group}
                    - {"unknown"}
                ),
                "has_upload": "upload" in names,
                "has_repeat_upload": "repeat_upload" in names
                or any(bool(event.get("duplicate")) for event in group),
                "has_evict": "evict" in names,
                "later_accesses": later[:max_examples],
            }
        )

    examples.sort(
        key=lambda item: (
            not item["has_repeat_upload"],
            not item["has_upload"],
            -item["event_count"],
            item["physical_key"],
        )
    )

    return {
        "events": len(events),
        "event_counts": dict(sorted(event_counts.items())),
        "action_counts": dict(sorted(action_counts.items())),
        "phase_counts": dict(sorted(phase_counts.items())),
        "invalidation_counts": dict(sorted(invalidation_counts.items())),
        "later_access_counts": dict(sorted(later_access_counts.items())),
        "derived_relation_counts": dict(sorted(derived_counts.items())),
        "logical_keys_seen": len([key for key in logical_counts if key != "unknown"]),
        "physical_keys_seen": len([key for key in physical_counts if key != "unknown"]),
        "stable_physical_keys_seen": len(
            [key for key in stable_physical_counts if key != "unknown"]
        ),
        "top_logical_keys": logical_counts.most_common(max_examples),
        "top_physical_keys": physical_counts.most_common(max_examples),
        "top_stable_physical_keys": stable_physical_counts.most_common(max_examples),
        "examples": examples[:max_examples],
        "derived_examples": derived_examples,
    }


def write_jsonl(path: Path, events: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--out-jsonl", type=Path, required=True)
    parser.add_argument("--out-summary", type=Path, required=True)
    parser.add_argument("--max-examples", type=int, default=12)
    args = parser.parse_args()

    events = read_events(args.log)
    summary = summarize(events, args.max_examples)
    write_jsonl(args.out_jsonl, events)
    args.out_summary.parent.mkdir(parents=True, exist_ok=True)
    args.out_summary.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
