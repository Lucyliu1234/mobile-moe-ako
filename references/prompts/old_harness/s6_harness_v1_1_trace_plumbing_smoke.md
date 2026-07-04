Use $mobile-moe-ako.

You are running **S6 Harness V1.1 Trace Plumbing Smoke**.

This is a diagnostic-only smoke validation of the binary provenance gate added
in harness commit `9caab04`. Do not optimize runtime policy. Do not reuse or
overwrite prior V1.1 artifacts.

## Purpose

Validate that the updated event-trace discipline works:

```text
host/phone runner md5 must match before interpreting missing traces
trace_config must appear before data events are interpreted
missing/mismatched binary provenance must be classified as binary_provenance_invalid
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

The runtime must include the `trace_config` sentinel event:

```json
{"event":"trace_config","phase":"init","enabled":true,"events_enabled":true,"event_limit":200}
```

## Required Binary Provenance Gate

Before interpreting missing events, verify and record:

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
classify result: binary_provenance_invalid
do not interpret trace absence
do not change instrumentation
do not optimize
```

If md5 matches, continue to the smoke run below.

## Smoke Run

Use this new label only:

```text
s6_harness_v1_1_trace_plumbing_smoke_fasttemp_p16_d16
```

Run:

```bash
python3 harness/benchmark_adapter.py run \
  --label s6_harness_v1_1_trace_plumbing_smoke_fasttemp_p16_d16 \
  --runtime /home/liuxu/projects/mllm \
  --stage s6_harness_v1_1_trace_plumbing_smoke \
  --profile day_smoke_p16_d16 \
  --trace-residency \
  --extra-env AKO_QWEN2_RESIDENCY_TRACE_EVENTS=1 \
  --extra-env AKO_QWEN2_RESIDENCY_TRACE_EVENT_LIMIT=200
```

Extract:

```bash
python3 harness/extract_state_trace.py \
  --log results/runs/s6_harness_v1_1_trace_plumbing_smoke_fasttemp_p16_d16/logs/qwen2_td_qnn.log \
  --out-jsonl results/runs/s6_harness_v1_1_trace_plumbing_smoke_fasttemp_p16_d16/state_trace.jsonl \
  --out-summary results/runs/s6_harness_v1_1_trace_plumbing_smoke_fasttemp_p16_d16/state_trace_summary.json
```

## Decision

```text
events=0:
  if host/phone md5 mismatch, classify binary_provenance_invalid;
  otherwise binary/env/log capture is not proven.

trace_config present but no data events:
  binary/env/log plumbing works, but active-path event instrumentation or guards
  are missing.

trace_config plus data events:
  event-level trace plumbing is working.
```

Data events include:

```text
miss
upload
record
evict
later_access
repeat_upload
```

## Output

Append a concise smoke result to `ITERATIONS.md`.

Report:

- whether binary provenance gate was executed;
- whether host/phone md5 matched;
- whether `trace_config` appeared;
- whether data events appeared;
- `state_trace_summary.json` path;
- final classification.

Do not run optimization patches. Do not run p32/d32.
