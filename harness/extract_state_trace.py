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


def summarize(events: list[dict[str, Any]], max_examples: int) -> dict[str, Any]:
    event_counts = Counter(event_key(event, "event") for event in events)
    action_counts = Counter(event_key(event, "action") for event in events)
    phase_counts = Counter(event_key(event, "phase") for event in events)
    logical_counts = Counter(event_key(event, "logical_key") for event in events)
    physical_counts = Counter(event_key(event, "physical_key") for event in events)

    by_physical: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_logical: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        by_physical[event_key(event, "physical_key")].append(event)
        by_logical[event_key(event, "logical_key")].append(event)

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
        "logical_keys_seen": len([key for key in logical_counts if key != "unknown"]),
        "physical_keys_seen": len([key for key in physical_counts if key != "unknown"]),
        "top_logical_keys": logical_counts.most_common(max_examples),
        "top_physical_keys": physical_counts.most_common(max_examples),
        "examples": examples[:max_examples],
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
