Use $mobile-moe-ako.

You are running **S6 Harness V1 Event Trace**, a diagnostic-harness evolution
run. The goal is not to optimize immediately. The goal is to upgrade the
state-relation evidence from aggregate counters to sampled event-level logical
request vs physical action traces.

## Repositories

Harness package:

```text
/home/liuxu/projects/mobile-moe-ako
```

Runtime repo:

```text
/home/liuxu/projects/mllm
```

Runtime branch expected:

```text
exp/s6-residency-event-trace-v1
```

Runtime must include:

```text
MLLM_QNN_TD_RESIDENCY_TRACE=1 aggregate counters
MLLM_QNN_TD_RESIDENCY_TRACE_EVENTS=1 sampled JSON event logs
MLLM_QNN_TD_RESIDENCY_TRACE_EVENT_LIMIT=<small cap>
```

## Required Baseline

Run the adapter with event tracing enabled:

```bash
python3 harness/benchmark_adapter.py run \
  --label s6_harness_v1_event_trace_baseline_fasttemp_p16_d16 \
  --runtime /home/liuxu/projects/mllm \
  --stage s6_harness_v1_event_trace \
  --profile day_smoke_p16_d16 \
  --trace-residency \
  --extra-env AKO_QWEN2_RESIDENCY_TRACE_EVENTS=1 \
  --extra-env AKO_QWEN2_RESIDENCY_TRACE_EVENT_LIMIT=200
```

After the run, extract trace events:

```bash
python3 harness/extract_state_trace.py \
  --log results/runs/s6_harness_v1_event_trace_baseline_fasttemp_p16_d16/logs/qwen2_td_qnn.log \
  --out-jsonl results/runs/s6_harness_v1_event_trace_baseline_fasttemp_p16_d16/state_trace.jsonl \
  --out-summary results/runs/s6_harness_v1_event_trace_baseline_fasttemp_p16_d16/state_trace_summary.json
```

Then run boundary localization:

```bash
python3 harness/localize_boundary.py \
  --metrics results/runs/s6_harness_v1_event_trace_baseline_fasttemp_p16_d16/metrics.json \
  --out results/runs/s6_harness_v1_event_trace_baseline_fasttemp_p16_d16/bounded_task.json
```

## Required Interpretation

Write:

```text
results/runs/s6_harness_v1_event_trace_baseline_fasttemp_p16_d16/state_relation.event_level.json
```

It must answer from `state_trace_summary.json`:

- Which logical keys triggered uploads?
- Which physical keys were uploaded more than once?
- Which physical keys covered multiple logical keys?
- Did later misses happen before or after eviction/invalidation?
- Are repeated uploads explained by logical missing state, true physical
  eviction, key mismatch, phase divergence, or unknown?

If the event trace has zero events, classify this as a diagnostic harness
failure and stop without optimization.

## Stop Rule

Do not run optimization patches in this prompt unless explicitly asked later.
This run should produce diagnostic artifacts and a short harness assessment:

```text
metrics.json
bounded_task.json
state_trace.jsonl
state_trace_summary.json
state_relation.event_level.json
ITERATIONS.md entry
```

The final answer should say whether event-level tracing improved control-surface
localization compared with aggregate `state_relation.json`.
