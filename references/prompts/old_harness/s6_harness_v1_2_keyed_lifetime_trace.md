Use $mobile-moe-ako.

You are running **S6 Harness V1.2 Keyed Lifetime Trace**.

This is a diagnostic-only harness test. Do not optimize runtime policy. Do not
run p32/d32. The purpose is to provide fine-grained event-level profiling for
the lifetime of a reusable physical payload, not to assign a fixed cause label.

## Purpose

Expose:

```text
When a later logical access misses after a packed upload covered that logical
key, what upload, record, later-access, eviction, and repeat-upload events are
visible around that logical/physical relation?
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

Runtime must include V1.2 keyed lifetime event fields:

```text
stable_physical_key
slot_id
was_covered_by_previous_upload
duplicate_by_stable_key
keyed evict physical/logical identity
```

## Required Binary Provenance Gate

Before interpreting traces, verify and record:

```text
runtime branch/commit
host runner path
host runner md5
phone runner path
phone runner md5
host md5 == phone md5
phone runner size/mode/stat
```

If host and phone runner md5 do not match, record
`binary_provenance_invalid` and stop.

## Formal Run

Use this label only:

```text
s6_harness_v1_2_keyed_lifetime_fasttemp_p16_d16
```

Run:

```bash
python3 harness/benchmark_adapter.py run \
  --label s6_harness_v1_2_keyed_lifetime_fasttemp_p16_d16 \
  --runtime /home/liuxu/projects/mllm \
  --stage s6_harness_v1_2_keyed_lifetime \
  --profile day_smoke_p16_d16 \
  --trace-residency \
  --extra-env AKO_QWEN2_RESIDENCY_TRACE_EVENTS=1 \
  --extra-env AKO_QWEN2_RESIDENCY_TRACE_EVENT_LIMIT=4000
```

Extract:

```bash
python3 harness/extract_state_trace.py \
  --log results/runs/s6_harness_v1_2_keyed_lifetime_fasttemp_p16_d16/logs/qwen2_td_qnn.log \
  --out-jsonl results/runs/s6_harness_v1_2_keyed_lifetime_fasttemp_p16_d16/state_trace.jsonl \
  --out-summary results/runs/s6_harness_v1_2_keyed_lifetime_fasttemp_p16_d16/state_trace_summary.json \
  --max-examples 32
```

Localize:

```bash
python3 harness/localize_boundary.py \
  --metrics results/runs/s6_harness_v1_2_keyed_lifetime_fasttemp_p16_d16/metrics.json \
  --label s6_harness_v1_2_keyed_lifetime_fasttemp_p16_d16 \
  --out results/runs/s6_harness_v1_2_keyed_lifetime_fasttemp_p16_d16/bounded_task.json
```

## Required Profiling Report

Write:

```text
results/runs/s6_harness_v1_2_keyed_lifetime_fasttemp_p16_d16/state_profile.keyed_lifetime.json
```

Keep the report profiler-like. Preserve profiling evidence:

```text
binary_provenance
benchmark metrics
event_counts
derived_relation_counts
top timelines
derived examples
open questions for code inspection
```

Use extractor-derived counts:

```text
later_miss_before_keyed_evict
later_miss_after_keyed_evict
repeat_upload_by_physical_key
repeat_upload_by_stable_key
later_miss_without_known_coverage
```

## Output

Append a concise result to `ITERATIONS.md` and update
`harness/harness_ledger.md`.

Report whether V1.2 converts the V1 observation from:

```text
covered sibling later misses without keyed lifetime evidence
```

to a richer keyed-lifetime profiling report. The agent may use that report to
form its own causal hypothesis, and may reject any suggested interpretation if
code inspection contradicts it.
