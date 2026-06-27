# Benchmark Instructions

Run from the MobileMoE-AKO skill directory unless the user copies the scripts into a target repo:

```bash
AKO_STAGE=runtime AKO_ITERATION_ID=runtime_iter_01 bash scripts/agent_bench.sh
```

For fast smoke runs, reduce the prompt count and thermal waits:

```bash
AKO_STAGE=smoke AKO_ITERATION_ID=smoke AKO_LIMIT=1 AKO_REPEATS=1 AKO_IDLE_SECONDS=0 AKO_SLEEP_BETWEEN_RUNS_S=0 bash scripts/agent_bench.sh
```

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
