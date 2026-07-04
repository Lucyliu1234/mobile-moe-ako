# MobileMoE-AKO Harness

This directory contains the first AKO4X-style harness layer for MobileMoE
whole-system runtime optimization. The tools do not replace the existing
benchmark scripts; they wrap them so agent runs produce explicit boundaries,
manifests, and verdicts.

## Tools

### `benchmark_adapter.py`

Wraps `scripts/agent_bench.sh` with a stable interface and writes
`adapter_manifest.json` beside each run.

Dry run:

```bash
python3 harness/benchmark_adapter.py run \
  --label harness_v0_dry_run \
  --runtime /home/liuxu/projects/mllm \
  --stage harness_v0 \
  --profile day_smoke_p16_d16 \
  --trace-residency \
  --dry-run
```

Real run:

```bash
python3 harness/benchmark_adapter.py run \
  --label <iteration_id> \
  --runtime /home/liuxu/projects/mllm \
  --stage <stage> \
  --profile day_smoke_p16_d16
```

Use `--trace-residency` only when the runtime binary contains the matching
diagnostic counters and the run intentionally needs state-level tracing.

### `boundary_template.py`

Writes the strong pre-patch boundary form the agent must fill before patching.

```bash
python3 harness/boundary_template.py \
  --profile-report results/runs/<baseline>/mobile_profile.json \
  --out results/runs/<baseline>/boundary_form.md
```

The output does not suggest bottleneck axes or candidate answers. It is an empty
causal explanation form with required sections for suspected boundary, profile
evidence, physical-vs-logical distinction, target control surface, state
transition hypothesis, expected metric movement, and falsification condition.

`localize_boundary.py` remains only as a compatibility wrapper for older prompt
references. New prompts should use `boundary_template.py`.

### `profile_report.py`

Builds a facts-only MobileMoE profiling report from `metrics.json` and optional
state trace, detail profile, and provenance artifacts.

```bash
python3 harness/profile_report.py \
  --metrics results/runs/<baseline>/metrics.json \
  --trace-summary results/runs/<baseline>/state_trace_summary.json \
  --detail-profile results/runs/<baseline>/detail_profile.json \
  --manifest results/runs/<baseline>/adapter_manifest.json \
  --out results/runs/<baseline>/mobile_profile.json
```

The report is organized into sections such as validity, throughput, operator
timing, compute, transfer, upload attribution, page residency, cache,
materialization service, residency aggregate, state trace, thermal, and
provenance. It is a profiler output, not a bottleneck decision.

`profile_report.py` intentionally reports missing observations as missing
rather than zero. For example, absent kernel breakdown, page-residency, or
upload-attribution fields should tell the agent that a diagnostic gap remains,
not that compute/page faults/upload waits are free.

### `detail_profile.py`

Builds generic runtime-event hotspot tables from sampled state events and
optional runtime logs. Its main output is not layer-centric. It reports facts
such as physical action hotspots, logical request hotspots, resource lifetime
hotspots, reuse/skip effectiveness, phase/path breakdown, coverage sizes, and
physical resource byte hotspots.

```bash
python3 harness/detail_profile.py \
  --state-trace results/runs/<baseline>/state_trace.jsonl \
  --log results/runs/<baseline>/logs/qwen2_td_qnn.log \
  --out results/runs/<baseline>/detail_profile.json
```

Adapter-specific tables, such as MobileMoE layer or projection breakdowns, are
kept under `adapter_specific_appendix`. They are supplemental facts, not the
main harness coordinate system.

This is still profiling, not diagnosis. It gives the agent finer-grained
runtime-event tables to cite in `boundary_form.md`.

### `classify_result.py`

Compares a candidate against a baseline and emits a simple patch-acceptance
verdict.

```bash
python3 harness/classify_result.py \
  --baseline results/runs/<baseline>/metrics.json \
  --candidate results/runs/<candidate>/metrics.json \
  --hypothesis transfer_residency \
  --out results/runs/<candidate>/classification.json
```

Verdicts:

- `accept`: correctness passed and `decode_tok_s` improved beyond the configured
  threshold.
- `reject`: primary metric clearly regressed.
- `inconclusive`: primary movement is below threshold.
- `invalid`: compile, correctness, or metric comparability failed.

The script also emits metric deltas and guardrail warnings. It does not explain
the system bottleneck or choose the next direction.

## Intended Flow

```text
profiled baseline metrics
    -> optional detail_profile.py for ranked hotspots
    -> profile_report.py
    -> mobile_profile.json
    -> boundary_template.py
    -> boundary_form.md
    -> agent fills boundary form with profile facts and code references
    -> state trace when required
    -> patch within the bounded task
    -> benchmark_adapter.py run
    -> classify_result.py
    -> accept/archive/log
```

The goal is not to make the agent less capable. The goal is to make every
exploration step auditable: profiling exposes facts, the agent defines a
boundary, and the benchmark verdict decides whether the patch can be accepted.

### `extract_state_trace.py`

Extracts sampled event-level state-relation logs from runtime output. The
runtime must emit lines with the `[TD-RES-TRACE]` prefix and JSON payloads that
follow `references/state_relation_trace_schema.md`.

```bash
python3 harness/extract_state_trace.py \
  --log results/runs/<label>/logs/qwen2_td_qnn.log \
  --out-jsonl results/runs/<label>/state_trace.jsonl \
  --out-summary results/runs/<label>/state_trace_summary.json
```

Use this after the agent identifies a repeated-physical-work question and
aggregate counters cannot identify which logical request caused which physical
action.
