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
  "invalidated_by": "eviction|overwrite|phase_reset|unknown",
  "later_access": "hit|miss|repeated_upload|unknown",
  "slot_id": 0,
  "bytes": 0,
  "duplicate": false,
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
- Was repeated physical work caused by missing logical state, true physical
  eviction, key mismatch, phase divergence, or another reason?

## Harness Output

`harness/extract_state_trace.py` reads the runtime log and writes:

```text
state_trace.jsonl
state_trace_summary.json
```

The summary groups events by physical key and logical key so a future agent can
inspect examples instead of scanning raw logs.

## Acceptance Discipline

If `trace_config` is missing, debug build/deploy/env/log capture before drawing
state-relation conclusions. If `trace_config` is present but no data events
appear, debug active-path instrumentation or event-emission guards.

Event traces are diagnostic evidence, not speedups. A runtime patch still needs
the normal classifier verdict and benchmark guardrails before acceptance.
