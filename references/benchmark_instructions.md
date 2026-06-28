# Benchmark Instructions

Run from the MobileMoE-AKO skill directory unless the user copies the scripts into a target repo:

```bash
AKO_STAGE=runtime AKO_ITERATION_ID=runtime_iter_01 bash scripts/agent_bench.sh
```

For daytime agent iterations, use one of the fixed fast profiles:

```bash
AKO_BENCH_PROFILE=day_smoke_p16_d16 AKO_ITERATION_ID=s1_iter_01 bash scripts/agent_bench.sh
```

```bash
AKO_BENCH_PROFILE=day_signal_p32_d32 AKO_ITERATION_ID=s1_iter_01_recheck bash scripts/agent_bench.sh
```

`day_smoke_p16_d16` uses one fixed prompt with 16 prompt tokens and 16 decode tokens. Use it for fast compile/run/correctness feedback and obvious regressions. `day_signal_p32_d32` uses one fixed prompt with 32 prompt tokens and 32 decode tokens. Use it to recheck promising patches before spending time on the evening verdict.

The profile datasets are versioned under `references/datasets/` so the smoke contract is stable with the harness.

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
