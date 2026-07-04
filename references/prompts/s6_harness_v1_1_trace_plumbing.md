Use $mobile-moe-ako.

You are running **S6 Harness V1.1 Trace Plumbing Debug**.

This is a diagnostic harness run only. Do not optimize runtime policy. The goal
is to determine why the previous V1 event-trace run produced zero
`[TD-RES-TRACE]` events.

Expected runtime branch:

```text
exp/s6-residency-event-trace-v1
```

The runtime must include the `trace_config` sentinel event:

```json
{"event":"trace_config","phase":"init","enabled":true,"events_enabled":true,"event_limit":200}
```

Before interpreting missing events, verify binary provenance:

```text
host runner md5
phone runner md5
host md5 == phone md5
phone runner path/size/mode
runtime branch/commit
```

If host and phone runner md5 do not match, classify the run as
`binary_provenance_invalid`, rebuild/deploy the expected runner, and rerun this
diagnostic before changing instrumentation.

Run:

```bash
python3 harness/benchmark_adapter.py run \
  --label s6_harness_v1_1_trace_plumbing_fasttemp_p16_d16 \
  --runtime /home/liuxu/projects/mllm \
  --stage s6_harness_v1_1_trace_plumbing \
  --profile day_smoke_p16_d16 \
  --trace-residency \
  --extra-env AKO_QWEN2_RESIDENCY_TRACE_EVENTS=1 \
  --extra-env AKO_QWEN2_RESIDENCY_TRACE_EVENT_LIMIT=200
```

Extract:

```bash
python3 harness/extract_state_trace.py \
  --log results/runs/s6_harness_v1_1_trace_plumbing_fasttemp_p16_d16/logs/qwen2_td_qnn.log \
  --out-jsonl results/runs/s6_harness_v1_1_trace_plumbing_fasttemp_p16_d16/state_trace.jsonl \
  --out-summary results/runs/s6_harness_v1_1_trace_plumbing_fasttemp_p16_d16/state_trace_summary.json
```

Decision:

```text
events=0:
  if host/phone md5 mismatch, classify binary_provenance_invalid;
  otherwise binary/env/log capture is not proven. Check deployed binary md5,
  remote env, and pulled full log path.

trace_config present but no data events:
  binary/env/log plumbing works. Active-path instrumentation or event-emission
  guards are missing.

trace_config plus miss/upload/record/evict/later_access/repeat_upload:
  event-level tracing is working. Write state_relation.event_level.json and stop.
```

Append the result to `ITERATIONS.md`. Do not run optimization patches.
