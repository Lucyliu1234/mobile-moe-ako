#!/usr/bin/env python3
"""Generate the pre-patch boundary form an agent must fill."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def profile_summary(profile_report: dict[str, Any]) -> list[str]:
    sections = profile_report.get("sections")
    if not isinstance(sections, dict):
        return []
    out: list[str] = []
    for name in [
        "validity",
        "throughput",
        "operator_timing",
        "compute",
        "transfer",
        "upload_attribution",
        "page_residency",
        "cache",
        "materialization_service",
        "residency_aggregate",
        "state_trace",
        "runtime_event_profile",
        "adapter_specific_appendix",
        "thermal",
    ]:
        data = sections.get(name)
        if isinstance(data, dict) and data:
            present = [key for key, value in data.items() if value is not None]
            if present:
                out.append(f"- `{name}`: {', '.join(f'`{key}`' for key in present[:16])}")
    return out


def missing_summary(profile_report: dict[str, Any]) -> list[str]:
    missing = profile_report.get("missing_observations")
    if not isinstance(missing, dict):
        return []
    out: list[str] = []
    for name, values in missing.items():
        if isinstance(values, list) and values:
            out.append(f"- `{name}`: {', '.join(f'`{value}`' for value in values)}")
    return out


def build_markdown(label: str, profile_report: dict[str, Any]) -> str:
    profile_label = profile_report.get("label") or "unknown"
    sections = profile_summary(profile_report)
    missing = missing_summary(profile_report)
    section_text = "\n".join(sections) if sections else "- No profile sections found."
    missing_text = "\n".join(missing) if missing else "- No missing observations reported."

    return f"""# Boundary Form: {label}

Profile report: `{profile_label}`

This is a required pre-patch form. The harness provides facts only. The agent
must fill every `TBD` from profile evidence and code inspection before editing
runtime policy.

## Available Profile Sections

{section_text}

## Missing Observations

{missing_text}

## Boundary Definition

### 1. Suspected Boundary

TBD

Name the smallest system boundary that appears responsible for the current
performance cost. This can be a boundary the agent defines from the profile and
code; it is not restricted to a predefined list.

### 2. Evidence From Profile

TBD

Quote concrete metric names and values from `mobile_profile.json`. Do not use a
metric family without naming the exact fields and direction.

Required evidence:

- Primary metric:
- Cost/time metrics:
- Transfer or memory metrics:
- Cache/state metrics:
- Thermal/provenance comparability:

### 3. Physical-vs-Logical Distinction

TBD

Explain whether the hypothesis changes real physical work or only logical
counters. If it claims to affect physical work, name the physical action and the
metric that measures it. If the current profile cannot distinguish physical
work from logical accounting, say what observation is missing before patching.

### 4. Target Control Surface

TBD

List the files/functions/states to inspect first and why they plausibly control
the suspected boundary. This is an inspection target, not permission to edit
unrelated code.

Required:

- Files/functions to inspect:
- Runtime state or resource being controlled:
- Why this code is on the fixed benchmark critical path:

### 5. State Transition Hypothesis

TBD

Describe the causal chain in code terms.

Required:

- State written:
- State read:
- Physical action triggered or skipped:
- Effect lifetime or invalidation path:
- How this affects later materialization/upload/compute/synchronization:

### 6. Expected Metric Movement

TBD

If the patch is correct, which metrics should move and in what direction?

Required:

- `decode_tok_s` expected direction:
- Physical cost metrics expected direction:
- Supporting diagnostic metrics expected direction:
- Guardrails that must not regress:

### 7. Falsification Condition

TBD

State exactly what benchmark result would reject the hypothesis. Include at
least one condition based on unchanged physical-cost metrics when the hypothesis
claims to reduce physical work.

Required:

- Reject if primary metric:
- Reject if physical-cost metrics:
- Reject if supporting diagnostics:
- Treat as inconclusive if:

## Pre-Patch Rule

Do not edit runtime policy until all `TBD` fields above are filled with concrete
profile facts and code references.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile-report", type=Path, required=True)
    parser.add_argument("--label")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    profile_report = load_json(args.profile_report)
    label = args.label or str(profile_report.get("label") or "boundary_form")
    text = build_markdown(label, profile_report)
    print(text)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
