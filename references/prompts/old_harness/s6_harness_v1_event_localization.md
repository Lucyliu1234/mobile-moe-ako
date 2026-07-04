Use $mobile-moe-ako.

You are running **S6 Harness V1 Event-Level Localization**.

This is a formal diagnostic-only harness test. Its purpose is not to optimize
MobileMoE runtime policy. Its purpose is to test whether event-level
state-relation tracing improves control-surface localization beyond aggregate
metrics.

Do not edit runtime policy. Do not run optimization patches. Do not run p32/d32.

## Purpose

Answer this research question:

```text
Given a transfer/residency bounded task, can the harness use sampled event-level
state relations to expose the concrete logical request / physical action
timelines that aggregate metrics hide?
```

## Expected Runtime

Runtime repo:

```text
/home/liuxu/projects/mllm
```

Expected runtime branch:

```text
exp/s6-residency-event-trace-v1
```

Expected runtime commit:

```text
f4a73850
```

Expected host runner candidate:

```text
/home/liuxu/projects/mllm/build-android-arm64-v8a-qnn/bin/mllm-qwen2-moe-td-qnn-aot-runner
```

Phone runner path:

```text
/data/local/tmp/qwen2_moe_td_w8a16_clean_20260527/mllm-qwen2-moe-td-qnn-aot-runner
```

## Required Binary Provenance Gate

Before interpreting any trace absence or trace content, verify and record:

```text
runtime branch/commit
host runner path
host runner md5
phone runner path
phone runner md5
host md5 == phone md5
phone runner size/mode/stat
```

If host and phone runner md5 do not match:

```text
record binary_provenance_invalid
append ITERATIONS.md
do not interpret trace absence
do not change instrumentation
do not optimize
```

## Formal Run

Use this new label only:

```text
s6_harness_v1_event_localization_fasttemp_p16_d16
```

Run:

```bash
python3 harness/benchmark_adapter.py run \
  --label s6_harness_v1_event_localization_fasttemp_p16_d16 \
  --runtime /home/liuxu/projects/mllm \
  --stage s6_harness_v1_event_localization \
  --profile day_smoke_p16_d16 \
  --trace-residency \
  --extra-env AKO_QWEN2_RESIDENCY_TRACE_EVENTS=1 \
  --extra-env AKO_QWEN2_RESIDENCY_TRACE_EVENT_LIMIT=2000
```

Extract:

```bash
python3 harness/extract_state_trace.py \
  --log results/runs/s6_harness_v1_event_localization_fasttemp_p16_d16/logs/qwen2_td_qnn.log \
  --out-jsonl results/runs/s6_harness_v1_event_localization_fasttemp_p16_d16/state_trace.jsonl \
  --out-summary results/runs/s6_harness_v1_event_localization_fasttemp_p16_d16/state_trace_summary.json \
  --max-examples 24
```

Localize:

```bash
python3 harness/localize_boundary.py \
  --metrics results/runs/s6_harness_v1_event_localization_fasttemp_p16_d16/metrics.json \
  --label s6_harness_v1_event_localization_fasttemp_p16_d16 \
  --out results/runs/s6_harness_v1_event_localization_fasttemp_p16_d16/bounded_task.json
```

## Event-Level Profiling Report

Write:

```text
results/runs/s6_harness_v1_event_localization_fasttemp_p16_d16/state_profile.event_level.json
```

It must include:

```text
evidence:
  trace_config_present
  data_events_present
  event_counts
  logical_keys_seen
  physical_keys_seen
  examples

state_relation_fields:
  logical_request_identity
  physical_action_identity
  effect_lifetime
  coverage_relation
  invalidation_reason
  execution_phase
  reuse_or_skip_decision

harness_value:
  what additional raw profiling facts this trace exposes over aggregate metrics

agent_interpretation_space:
  open questions that a coding agent should resolve by reading code
  plausible next inspection questions, without assigning fixed cause labels
```

## Profiling Rules

```text
md5 mismatch:
  record binary_provenance_invalid and stop.

trace_config missing:
  binary/env/log capture is not proven.

trace_config present, data events absent:
  active-path event instrumentation or emission guard missing.

data events present but no evict/repeat/later_access evidence:
  record the observation gap.

Do not turn the trace into fixed semantic categories. Preserve the event
sequences, relation counts, coverage sets, physical keys, and examples so the
agent can form and revise its own causal hypothesis after code inspection.
```

## Output

Append a concise result to `ITERATIONS.md`.

Report:

- binary provenance gate result;
- benchmark correctness and primary metrics;
- event counts and whether data events appeared;
- event-level profiling facts;
- whether event-level trace improved observability over aggregate relation;
- paths to `metrics.json`, `bounded_task.json`,
  `state_trace_summary.json`, and `state_profile.event_level.json`.

Do not run optimization patches.
