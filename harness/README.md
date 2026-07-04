# MobileMoE-AKO Harness V0

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

### `localize_boundary.py`

Turns one normalized metrics JSON into a bounded task before patching.

```bash
python3 harness/localize_boundary.py \
  --metrics results/runs/<baseline>/metrics.json \
  --out results/runs/<baseline>/bounded_task.json
```

The output names the bottleneck class, physical event, logical trigger, allowed
surfaces, forbidden-first surfaces, expected metric movement, and falsification
rule.

### `classify_result.py`

Compares a candidate against a baseline and emits a verdict class.

```bash
python3 harness/classify_result.py \
  --baseline results/runs/<baseline>/metrics.json \
  --candidate results/runs/<candidate>/metrics.json \
  --hypothesis transfer_residency \
  --out results/runs/<candidate>/classification.json
```

Initial verdict classes:

- `true_system_win`
- `transfer_win`
- `scheduling_win`
- `logical_counter_only`
- `latency_shift`
- `no_signal`
- `wrong_path`
- `regression`
- `invalid`

## Intended Flow

```text
profiled baseline metrics
    -> localize_boundary.py
    -> bounded_task.json
    -> state-relation statement when required
    -> patch within the bounded task
    -> benchmark_adapter.py run
    -> classify_result.py
    -> accept/archive/log
```

The goal is not to make the agent less capable. The goal is to make every
exploration step auditable: the profile chooses a boundary, the boundary chooses
code surfaces, and the benchmark verdict decides whether the patch moved the
physical cost it claimed to control.

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

Use this after `localize_boundary.py` selects a repeated-physical-work boundary
and aggregate counters cannot identify which logical request caused which
physical action.
