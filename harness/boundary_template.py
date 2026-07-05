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
        "qnn_context_timeline",
        "lm_head_timeline",
        "async_overlap_profile",
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


def compact_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)


def adapter_state_facts(profile_report: dict[str, Any]) -> str:
    sections = profile_report.get("sections")
    if not isinstance(sections, dict):
        return "- No state/resource consistency facts were found in the profile."

    facts: list[str] = []
    consistency = sections.get("physical_logical_consistency")
    if isinstance(consistency, dict) and consistency.get("available"):
        slim = {
            "counts": consistency.get("counts", {}),
            "ratios": consistency.get("ratios", {}),
            "examples": consistency.get("examples", [])[:3],
        }
        facts.append(
            "- `physical_logical_consistency`:\n\n"
            f"```json\n{compact_json(slim)}\n```"
        )

    state_trace = sections.get("state_trace")
    if isinstance(state_trace, dict) and state_trace.get("available"):
        slim = {
            "event_counts": state_trace.get("event_counts", {}),
            "later_access_counts": state_trace.get("later_access_counts", {}),
            "derived_relation_counts": state_trace.get(
                "derived_relation_counts", {}
            ),
            "logical_keys_seen": state_trace.get("logical_keys_seen"),
            "physical_keys_seen": state_trace.get("physical_keys_seen"),
            "stable_physical_keys_seen": state_trace.get(
                "stable_physical_keys_seen"
            ),
        }
        facts.append(
            "- `state_trace` resource/lifetime summary:\n\n"
            f"```json\n{compact_json(slim)}\n```"
        )

    runtime_profile = sections.get("runtime_event_profile")
    if isinstance(runtime_profile, dict) and runtime_profile.get("available"):
        data = runtime_profile.get("runtime_event_profile")
        if isinstance(data, dict):
            slim = {
                "coverage_size_counts": data.get("coverage_size_counts", {}),
                "reuse_skip_effectiveness": data.get(
                    "reuse_skip_effectiveness", {}
                ),
            }
            facts.append(
                "- `runtime_event_profile` state/reuse summary:\n\n"
                f"```json\n{compact_json(slim)}\n```"
            )

    return "\n\n".join(facts) if facts else (
        "- No state/resource consistency facts were found in the profile."
    )


def build_markdown(label: str, profile_report: dict[str, Any]) -> str:
    profile_label = profile_report.get("label") or "unknown"
    sections = profile_summary(profile_report)
    missing = missing_summary(profile_report)
    section_text = "\n".join(sections) if sections else "- No profile sections found."
    missing_text = "\n".join(missing) if missing else "- No missing observations reported."
    state_facts_text = adapter_state_facts(profile_report)

    return f"""# Boundary Form: {label}

Profile report: `{profile_label}`

This is a required pre-patch form. The harness provides facts only. The agent
must fill every `TBD` from profile evidence and code inspection before editing
runtime policy.

## Available Profile Sections

{section_text}

## Missing Observations

{missing_text}

## Compute-Vs-Bandwidth Triage

TBD

Classify the coarse bottleneck from measured profile facts before choosing a
patch. This only decides whether to use original AKO4ALL for compute-bound
operator work or MobileMoE-AKO for bandwidth/system runtime exploration. It
does not choose the concrete runtime boundary or patch.

Required:

- Selected route:
  `compute_operator_kernel | bandwidth_system`
- Evidence for selected route:
- Why the other route is weaker:
- If `compute_operator_kernel`, why the operator/kernel accounts for enough
  end-to-end time to justify switching to `/home/liuxu/projects/AKO4ALL`:
- If not `compute_operator_kernel`, why a local kernel/operator loop is not the
  first tool and why MobileMoE should continue exploring bandwidth/system
  runtime boundaries:
- Falsification condition for this route:

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

### 6. State/Resource Consistency Audit

TBD

If the profile contains facts about physical actions, logical requests,
resource coverage, reuse, invalidation, eviction, phase reset, or later
accesses, explain them before choosing a patch. This section is generic: use
the profile's own resource IDs and logical request IDs, not adapter-specific
assumptions.

Required:

- Observed physical resources or actions:
- Logical requests covered by those resources/actions:
- Later covered requests: hit, miss, repeated work, or unknown:
- Observed invalidation/eviction/overwrite/phase reset before later misses:
- Code sites that write physical/resource state:
- Code sites that write logical/request state:
- Code sites that decide reuse versus rematerialization/reupload/recompute:
- If choosing another boundary, why this state/resource relation is lower
  priority:
- Metrics or events that should move if this relation is the real boundary:

### 7. Minimal Intervention Audit

TBD

List the plausible control surfaces for this boundary before choosing a patch.
The goal is not to prefer small patches forever; the goal is to test the
causal hypothesis with the smallest sufficient intervention before changing a
heavier execution path.

Required:

- Physical action surface:
- Dispatch/execution owner surface:
- Metadata/state accounting surface:
- Lifetime/invalidation surface:
- Smallest surface that can test the hypothesis:
- Why this surface preserves semantics and the existing execution path when
  possible:
- If choosing a heavier surface, why lighter surfaces cannot test the
  hypothesis:

### 8. Expected Metric Movement

TBD

If the patch is correct, which metrics should move and in what direction?

Required:

- `decode_tok_s` expected direction:
- Physical cost metrics expected direction:
- Supporting diagnostic metrics expected direction:
- Guardrails that must not regress:

### 9. Falsification Condition

TBD

State exactly what benchmark result would reject the hypothesis. Include at
least one condition based on unchanged physical-cost metrics when the hypothesis
claims to reduce physical work.

Required:

- Reject if primary metric:
- Reject if physical-cost metrics:
- Reject if supporting diagnostics:
- Treat as inconclusive if:

## Adapter-Specific State/Resource Facts

These facts are copied from `mobile_profile.json` to make state/resource
relations visible. They are profiling facts, not a diagnosis.

{state_facts_text}

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
