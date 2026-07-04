# Benchmark Instructions

Run from the MobileMoE-AKO skill directory unless the user copies the scripts into a target repo:

```bash
AKO_STAGE=runtime AKO_ITERATION_ID=runtime_iter_01 bash scripts/agent_bench.sh
```

For daytime agent iterations, use the fixed fast profile:

```bash
AKO_BENCH_PROFILE=day_smoke_p16_d16 AKO_ITERATION_ID=s1_iter_01 bash scripts/agent_bench.sh
```

Use the larger signal profile only after a p16/d16 patch has already been
accepted:

```bash
AKO_BENCH_PROFILE=day_signal_p32_d32 AKO_ITERATION_ID=s1_iter_01_recheck bash scripts/agent_bench.sh
```

`day_smoke_p16_d16` uses one fixed prompt with 16 prompt tokens and 16 decode tokens. Use it for baseline and every normal p16 candidate iteration. `day_signal_p32_d32` uses one fixed prompt with 32 prompt tokens and 32 decode tokens. Use it only to recheck an already accepted p16/d16 patch before spending time on the evening verdict.

The profile datasets are versioned under `references/datasets/` so the smoke contract is stable with the harness.

## Harness Adapter Phone Benchmark

For current harness-mediated runs, prefer `harness/benchmark_adapter.py` over
calling `scripts/agent_bench.sh` directly. The adapter writes
`adapter_manifest.json` beside the run artifacts and keeps the phone benchmark
contract explicit.

Baseline template:

```bash
python3 harness/benchmark_adapter.py run \
  --label <experiment>_baseline_fasttemp_p16_d16 \
  --runtime /home/liuxu/projects/mllm \
  --stage <experiment> \
  --profile day_smoke_p16_d16 \
  --trace-residency \
  --extra-env AKO_QWEN2_RESIDENCY_TRACE_EVENTS=1 \
  --extra-env AKO_QWEN2_RESIDENCY_TRACE_EVENT_LIMIT=300
```

Candidate template:

```bash
python3 harness/benchmark_adapter.py run \
  --label <experiment>_iter_XX_fasttemp_p16_d16 \
  --runtime /home/liuxu/projects/mllm \
  --stage <experiment> \
  --profile day_smoke_p16_d16 \
  --baseline-metrics results/runs/<experiment>_baseline_fasttemp_p16_d16/metrics.json \
  --trace-residency \
  --extra-env AKO_QWEN2_RESIDENCY_TRACE_EVENTS=1 \
  --extra-env AKO_QWEN2_RESIDENCY_TRACE_EVENT_LIMIT=300
```

Accepted-patch recheck template:

```bash
python3 harness/benchmark_adapter.py run \
  --label <experiment>_accepted_recheck_p32_d32 \
  --runtime /home/liuxu/projects/mllm \
  --stage <experiment> \
  --profile day_signal_p32_d32 \
  --baseline-metrics results/runs/<experiment>_baseline_fasttemp_p16_d16/metrics.json \
  --trace-residency \
  --extra-env AKO_QWEN2_RESIDENCY_TRACE_EVENTS=1 \
  --extra-env AKO_QWEN2_RESIDENCY_TRACE_EVENT_LIMIT=300
```

Profile rule for formal harness optimization tests:

- baseline: `day_smoke_p16_d16`
- each normal candidate iteration: `day_smoke_p16_d16`
- accepted-patch recheck only: `day_signal_p32_d32`
- rejected or inconclusive patches: no `day_signal_p32_d32` run

The default phone/device contract is owned by `scripts/backends/qwen2_td_qnn.sh`:

- serial: `AKO_SERIAL`, default `10.29.230.131:5555`
- phone base: `/data/local/tmp/qwen2_moe_td_w8a16_clean_20260527`
- runner: `mllm-qwen2-moe-td-qnn-aot-runner`
- context length: `384`
- GPU cache capacity: `8`
- profile `day_smoke_p16_d16`: fixed p16/d16 smoke benchmark
- profile `day_signal_p32_d32`: fixed p32/d32 recheck benchmark

If ADB fails with a smartsocket/listener permission error, rerun the exact same
adapter command with escalated device access. Do not change benchmark settings
to work around device permissions.

## Default Backend

The public entry point is:

```text
scripts/agent_bench.sh
```

It calls the default backend adapter:

```text
scripts/backends/qwen2_td_qnn.sh
```

That backend wraps the known-good Qwen2 MoE TD QNN AOT Android command under:

```text
/data/local/tmp/qwen2_moe_td_w8a16_clean_20260527
```

It writes `summary.jsonl` from the pulled device log so `scripts/parse_metrics.py` can emit normalized metrics. The older `scripts/backends/ds2_edgemoe.sh` backend remains available by setting `AKO_BACKEND=ds2_edgemoe`.

The default `qwen2_td_qnn` backend reads the prompt from `AKO_PROMPT` when provided. Otherwise, it reads the JSONL row selected by `AKO_DATASET` and `AKO_START_INDEX`.

## Branches

Use branch names that match the current experiment label, for example:

- `exp/runtime-policy`
- `exp/cache-policy`
- `exp/transfer-scheduling`

If running the optional progressive context protocol, use the branch names defined in `references/experiment_protocol.md`.

## Useful Commands

Append an iteration entry:

```bash
python3 scripts/append_iteration.py \
  --iteration-id runtime_iter_01 \
  --stage runtime \
  --prompt-setting "MobileMoE-AKO core loop" \
  --hypothesis "..." \
  --direction "..." \
  --files-inspected "..." \
  --files-modified "..." \
  --change-summary "..." \
  --benchmark-command "bash scripts/agent_bench.sh" \
  --metrics-json results/runs/runtime_iter_01/metrics.json \
  --result "..." \
  --agent-diagnosis "..." \
  --my-diagnosis "..." \
  --needed-expert-knowledge "..." \
  --patch-or-commit "..."
```

Save a failed patch:

```bash
git diff > patches/failed_attempts/runtime_iter_01.patch
```
