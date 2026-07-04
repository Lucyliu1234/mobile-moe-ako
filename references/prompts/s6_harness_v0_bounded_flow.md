Use $mobile-moe-ako.

You are running **S6 Harness V0 Bounded Flow**, the B-group pilot for evaluating
whether an AKO4X-style harness makes MobileMoE whole-system runtime optimization
more controllable.

This run is about harness controllability, not about maximizing speed at any
cost. The key question is:

```text
Can the harness force the agent to form a bounded task, state-relation evidence,
and an explicit verdict before accepting or rejecting a runtime patch?
```

## Historical A-Control

Do not rerun the old free-form S6 prompt for A. Historical A-control already
exists in previous runs. Use these as qualitative controls when writing the
final comparison:

- `s6_verify2`: old diagnostic-driven flow; logical counters improved in some
  attempts while physical transfer did not.
- `s6_detailed_expert`: found a scheduling/prewarm-service patch, but not a
  physical transfer reduction.
- `s6_long_state_relation`: longer horizon improved localization, but still
  produced rejected page-touch/service tradeoffs.

This run is B only.

## Repositories

Harness package:

```text
/home/liuxu/projects/mobile-moe-ako
```

Runtime repo:

```text
/home/liuxu/projects/mllm
```

Runtime base commit:

```text
da9fa3534a16c0f34adb6709e2ba871741cbf8cc
```

Runtime branch for this run:

```text
exp/s6-harness-v0-bounded-flow
```

Harness branch expected:

```text
exp/s6-harness-v0-bounded-flow-prompt
```

If `/home/liuxu/projects/mllm` is dirty or on a branch that should not be
rewritten, create a separate clean worktree instead of resetting the main repo.
Do not touch unrelated runtime work.

## Fixed Benchmark Contract

Use the harness adapter. Do not directly run ad hoc Tucker commands unless the
adapter itself is broken and you are diagnosing the harness.

Smoke contract:

```text
profile: day_smoke_p16_d16
dataset: references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl
decode tokens: 16
context length: fixed by backend at 384
gpu cache capacity: fixed by backend at 8
correctness: correct=true, generated=16/16
primary metric: decode_tok_s
guardrails: correct, generated_tokens, mib_per_token, benchmark semantics
```

Do not edit benchmark prompts, datasets, correctness checks, generated-token
accounting, metric parser semantics, or model artifacts.

## Required Log Isolation

Before running the baseline, preserve the existing iteration log:

```bash
cp /home/liuxu/projects/mobile-moe-ako/ITERATIONS.md \
  /home/liuxu/projects/mobile-moe-ako/ITERATIONS_BEFORE_s6_harness_v0_bounded_flow_$(date +%Y%m%d_%H%M%S).md
```

Append every baseline, diagnostic, optimization iteration, and final comparison
entry to:

```text
/home/liuxu/projects/mobile-moe-ako/ITERATIONS.md
```

Archive every rejected patch under:

```text
/home/liuxu/projects/mobile-moe-ako/patches/failed_attempts/
```

## Required Baseline

From `/home/liuxu/projects/mobile-moe-ako`, run:

```bash
python3 harness/benchmark_adapter.py run \
  --label s6_harness_v0_baseline_fasttemp_p16_d16 \
  --runtime /home/liuxu/projects/mllm \
  --stage s6_harness_v0 \
  --profile day_smoke_p16_d16 \
  --trace-residency
```

After baseline, verify:

```text
results/runs/s6_harness_v0_baseline_fasttemp_p16_d16/metrics.json
results/runs/s6_harness_v0_baseline_fasttemp_p16_d16/adapter_manifest.json
```

Correctness must pass before optimization.

## Required Boundary Localization

Immediately after baseline and before reading or editing runtime code for an
optimization hypothesis, run:

```bash
python3 harness/localize_boundary.py \
  --metrics results/runs/s6_harness_v0_baseline_fasttemp_p16_d16/metrics.json \
  --out results/runs/s6_harness_v0_baseline_fasttemp_p16_d16/bounded_task.json
```

Read `bounded_task.json` and summarize it in `ITERATIONS.md`.

You must not patch until `bounded_task.json` exists.

## Required State-Relation File

If `bounded_task.json` has:

```json
"state_relation_required": true
```

then write:

```text
results/runs/s6_harness_v0_baseline_fasttemp_p16_d16/state_relation.json
```

The JSON must include:

```text
logical_request_identity
physical_action_identity
coverage_relation
effect_lifetime
invalidation_reason
execution_phase
reuse_skip_decision
unknowns
```

This file is required before any optimization edit. If the current diagnostics
cannot fill the fields, run one diagnostic-only iteration rather than guessing.

## Patch Rules

For every optimization attempt:

1. Read `bounded_task.json`.
2. Read `state_relation.json` when required.
3. State which bounded task field justifies the patch.
4. Stay inside `allowed_edit_surface`.
5. Do not patch `forbidden_first_surface` unless the bounded task is explicitly
   falsified and updated in the log.
6. Make one coherent runtime-policy change only.
7. Build/deploy/verify the changed runtime before benchmarking.

Patch acceptance is not subjective. The classifier verdict controls accept or
reject.

## Candidate Run Template

For iteration `XX`, run:

```bash
python3 harness/benchmark_adapter.py run \
  --label s6_harness_v0_iter_XX_fasttemp_p16_d16 \
  --runtime /home/liuxu/projects/mllm \
  --stage s6_harness_v0 \
  --profile day_smoke_p16_d16 \
  --baseline-metrics results/runs/s6_harness_v0_baseline_fasttemp_p16_d16/metrics.json \
  --trace-residency
```

Then classify:

```bash
python3 harness/classify_result.py \
  --baseline results/runs/s6_harness_v0_baseline_fasttemp_p16_d16/metrics.json \
  --candidate results/runs/s6_harness_v0_iter_XX_fasttemp_p16_d16/metrics.json \
  --hypothesis <bounded_task.bottleneck_class> \
  --out results/runs/s6_harness_v0_iter_XX_fasttemp_p16_d16/classification.json
```

Replace `XX` with `01`, `02`, or `03`. Replace
`<bounded_task.bottleneck_class>` with the value from `bounded_task.json`, for
example `transfer_residency`.

## Acceptance Rule

Accept and commit an optimization patch only if:

```json
"accept": true
```

in `classification.json`.

If `accept=false`, archive the patch and revert only your own failed edit before
continuing.

A patch classified as any of the following must be rejected:

```text
logical_counter_only
latency_shift
no_signal
wrong_path
regression
invalid
thermal_invalid
```

Diagnostic-only patches are not optimization wins.

## Iteration Budget

Run at most:

```text
1 baseline
up to 1 diagnostic-only iteration if state_relation.json cannot be filled
up to 3 optimization iterations
```

Do not run p32/d32 unless an optimization patch is accepted by the classifier.
If a patch is accepted, run one p32/d32 recheck using the same adapter pattern
with `--profile day_signal_p32_d32`.

## Final Comparison Against Historical A-Control

At the end, append a comparison entry to `ITERATIONS.md` that answers:

```text
Did B generate bounded_task.json before patching?
Did B generate state_relation.json before patching?
Did every patch cite the bounded task?
Did classifier output exist for every candidate?
Did any accept=false patch get rejected rather than subjectively accepted?
Did the flow prevent logical_counter_only or latency_shift false positives?
Did the agent stay inside the selected boundary?
Was failure easier to explain than historical A?
```

Use this qualitative comparison table:

```text
Dimension                         Historical A        B harness v0
bounded_task before patch          mostly no           yes/no
state_relation before patch         inconsistent        yes/no
classifier verdict                  manual             automatic yes/no
logical-counter-only rejected       sometimes late      yes/no
latency-shift rejected              sometimes late      yes/no
false-positive accepted             risk exists         yes/no
patch stayed in boundary            inconsistent        yes/no
failure explanation quality         medium              1-5
```

## Final Report

Report:

- runtime branch and final commit, if any;
- baseline metrics path;
- bounded_task path;
- state_relation path, if created;
- each iteration metrics path and classification path;
- accepted commit or archived rejected patches;
- whether B improved controllability relative to historical A;
- whether the harness was too weak, too restrictive, or useful.

Do not claim a new optimization unless the classifier accepted it and the
benchmark guardrails passed.
