# State-Relation Event Trace Schema

This schema upgrades state-relation diagnostics from aggregate counters to
sampled event-level evidence. Use it when a bounded task involves repeated
physical work and aggregate counters cannot explain which logical request caused
which physical action.

## Log Format

Runtime logs should emit one JSON object per line with this prefix:

```text
[TD-RES-TRACE] {"event":"miss",...}
```

Each event is intentionally small. The runtime should cap event count with an
environment-controlled limit so diagnostic logs remain bounded.

Recommended runtime switches:

```text
MLLM_QNN_TD_RESIDENCY_TRACE=1
MLLM_QNN_TD_RESIDENCY_TRACE_EVENTS=1
MLLM_QNN_TD_RESIDENCY_TRACE_EVENT_LIMIT=200
```

## Event Fields

Required fields:

```json
{
  "event": "trace_config|probe|hit|miss|upload|record|evict|later_access|repeat_upload",
  "phase": "prefill|required_decode|prewarm_decode|unknown",
  "layer": 0,
  "expert": 0,
  "projection": "gate|up|down|packed|unknown",
  "logical_key": "L0:E0:gate",
  "physical_key": "L0:E0:ptr0x0:bytes0",
  "action": "probe|skip|upload|record|evict|reuse|unknown",
  "skip_physical": false
}
```

Optional fields:

```json
{
  "enabled": true,
  "events_enabled": true,
  "event_limit": 200,
  "covered_logical_keys": ["L0:E0:gate", "L0:E0:up", "L0:E0:down"],
  "stable_physical_key": "L0:E0:path:off123:bytes456",
  "invalidated_by": "eviction|overwrite|phase_reset|unknown",
  "later_access": "hit|miss|repeated_upload|unknown",
  "slot_id": 0,
  "bytes": 0,
  "duplicate": false,
  "duplicate_by_stable_key": false,
  "was_covered_by_previous_upload": true,
  "reason": "free-form short reason"
}
```

## Interpretation

The trace should make these questions answerable from examples:

- Did the runtime binary/env/log path actually enable event tracing?
- Which logical request triggered the physical action?
- Which physical key was uploaded, recorded, reused, repeated, or evicted?
- Which later logical keys should have been covered by one physical action?
- Did a later logical miss happen before or after invalidation?
- What event sequences are visible around repeated physical work, including
  uploads, records, later accesses, evictions, repeat uploads, keys, and
  coverage sets?

## V1.2 Keyed Lifetime Requirements

For repeated-work boundaries, pointer identity is not enough. Diagnostic events
should carry a stable physical identity when available:

```text
stable_physical_key = layer/expert/storage-path/storage-offset/storage-bytes
```

`later_access` events should include:

```text
physical_key
stable_physical_key
slot_id
was_covered_by_previous_upload
covered_logical_keys
```

`evict` events should include:

```text
logical_key
physical_key
stable_physical_key
slot_id
covered_logical_keys
invalidated_by=eviction
```

The extractor derives profiling relation counts such as:

```text
later_miss_before_keyed_evict
later_miss_after_keyed_evict
repeat_upload_by_physical_key
repeat_upload_by_stable_key
later_miss_without_known_coverage
```

## Harness Output

`harness/extract_state_trace.py` reads the runtime log and writes:

```text
state_trace.jsonl
state_trace_summary.json
```

The summary groups events by physical key and logical key so a future agent can
inspect examples instead of scanning raw logs.

The summary is a profiling artifact. It should preserve raw facts and derived
relation counts without assigning fixed cause labels. Explanations should be
made by the agent after code inspection and may be revised or rejected.

## Acceptance Discipline

Before interpreting missing event traces, verify binary provenance:

```text
host runner md5 == phone runner md5
phone runner path/stat recorded
runtime branch/commit recorded
```

If md5 does not match, record `binary_provenance_invalid` and do not interpret
the trace as an event-schema or active-path instrumentation failure.

If `trace_config` is missing, debug build/deploy/env/log capture before drawing
state-relation conclusions. If `trace_config` is present but no data events
appear, debug active-path instrumentation or event-emission guards.

Event traces are profiling evidence, not speedups. A runtime patch still needs
the normal candidate-verdict and benchmark guardrails before acceptance.
