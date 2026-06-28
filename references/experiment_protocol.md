# Experiment Protocol: Progressive Context Setting

This protocol is project-specific. It is not part of vanilla AKO4ALL and is not required for every MobileMoE-AKO run.

Use it when the goal is to evaluate how much system context an agent needs for whole-system mobile MoE optimization. The reusable skill remains the AKO-style loop; this file defines one research design that wraps that loop.

## Principle

Run the same target under separate context conditions:

```text
Target: CoreMoE required-core serving policy
```

The stages are separate experiments under one progressive-context study. They should have separate branches, metric files, iteration entries, and summaries. Do not treat them as unrelated optimization directions; they differ in how much context the agent receives.

## Shared AKO Rules

Every stage must start from a baseline for the exact same benchmark contract used by that stage. Prefer reusing S0 when the dataset, decode length, runner, device, and thermal controls are unchanged; otherwise run a stage-local baseline before any source edit.

Every code-changing round must contain one coherent runtime-policy change tied to one hypothesis. Do not mix unrelated policy changes, benchmark changes, parser changes, logging changes, and broad refactors in one round.

Failed attempts are part of the trajectory. Record and archive compile failures, correctness failures, generated-token mismatches, speed regressions, no-signal changes, wrong file choices, forbidden-surface edits, and hypothesis/metric mismatches.

Baseline decomposition is required before the first source edit in every stage, but its interpretation is stage-bounded. In S1, decomposition is black-box observation of benchmark metrics, logs, and device state; do not supply MoE-specific optimization categories. In S2-S4, decomposition may use the expert concepts or file hints intentionally provided by that stage.

Stage-aware search policy:

- S1: external search is disabled except for benchmark/harness/environment failures. Do not search for MoE-specific optimization mechanisms or read expert hints. Missing domain knowledge is an S1 result.
- S2-S4: after a stall, search only for mobile MoE/runtime-system material: expert caching, prefetching, transfer scheduling, heterogeneous CPU/GPU/NPU execution, Android thermal benchmarking, Qualcomm QNN/OpenCL behavior, and MoE serving systems. Prefer local project notes, official vendor documentation, and systems papers. Do not perform generic kernel-optimization search unless the chosen file is actually a kernel.
- Every external source or project note used after a stall must be named in `ITERATIONS.md`, along with whether that knowledge would have violated the current stage's context budget.

## Stages

### S0: Baseline Stability

Purpose: measure harness noise and baseline stability.

Rules:

- Do not edit code.
- Run 3 baseline measurements with fixed model, prompt set, decode length, runner, and thermal controls.
- Log all runs in `ITERATIONS.md` or a baseline summary.
- Use the observed spread as the minimum meaningful effect size for later stages.

Recommended IDs:

```text
s0_baseline_01
s0_baseline_02
s0_baseline_03
```

Suggested outputs:

```text
exp/s0-baseline
results/metrics_s0.jsonl
```

### S1: Whole-System Black-Box Exploration

Purpose: test whether an agent can discover the relevant system surface with little context.

Context:

- repo
- objective
- benchmark command
- guardrails

Do not provide optimization direction or key files. Read `references/prompts/s1_blackbox.md`.

Before edits, cite the shared S0 baseline if the contract is unchanged, or run `s1_baseline_01`.

Recommended rounds: 3.

One-day S1 plan:

1. Create or switch to the runtime branch `exp/s1-blackbox-mobile-moe-ako`. Do not edit the runtime main branch directly.
2. Run a daytime smoke baseline before edits:

```bash
cd /home/liuxu/projects/mobile-moe-ako
AKO_CODE_REPO=/home/liuxu/projects/mllm \
AKO_BENCH_PROFILE=day_smoke_p16_d16 \
AKO_ITERATION_ID=s1_baseline_day_smoke_p16_d16 \
bash scripts/agent_bench.sh
```

3. Analyze the baseline diagnostic decomposition before the first edit using only raw benchmark metrics, logs, and device state. Do not supply MoE-specific interpretations. Missing fields should be recorded as instrumentation gaps.
4. Run 3 S1 smoke iterations. Each iteration uses `day_smoke_p16_d16`, one hypothesis, one coherent runtime-policy change, immediate `ITERATIONS.md` logging, and commit/archive before the next hypothesis.
5. Recheck any promising correctness-passing patch with the more credible daytime signal contract:

```bash
cd /home/liuxu/projects/mobile-moe-ako
AKO_CODE_REPO=/home/liuxu/projects/mllm \
AKO_BENCH_PROFILE=day_signal_p32_d32 \
AKO_ITERATION_ID=s1_iter_XX_day_signal_p32_d32 \
bash scripts/agent_bench.sh
```

6. In the evening, compare the original S1 baseline and the best S1 patch with the fixed 4-category verdict contract, for example 4mix prompt32 decode64. Do not use the evening verdict as every-iteration feedback.
7. S1 external search is disabled unless the benchmark or harness cannot run. Do not read expert hints, S2-S4 prompts, prior human optimization notes, or search for MoE-specific mechanisms. Missing domain knowledge is an S1 finding.

Suggested outputs:

```text
exp/s1-blackbox
results/metrics_s1.jsonl
```

### S2: Concept-Guided Exploration

Purpose: test whether high-level systems concepts help the agent map ideas to code.

Add concepts:

- dynamic expert/core serving
- residency
- prewarm/prefetch
- required miss
- eviction churn
- GPU expert path

Still do not give exact files. Read `references/prompts/s2_concept_guided.md`.

Before edits, cite the shared S0 baseline if the contract is unchanged, or run `s2_baseline_01`.

Recommended rounds: 3.

Suggested outputs:

```text
exp/s2-concept-guided
results/metrics_s2.jsonl
```

### S3: Key-File-Set Guided Exploration

Purpose: test whether a smaller search space improves optimization quality.

Provide candidate key files. The agent still chooses which file to modify and must justify the choice. Read `references/prompts/s3_key_file_set.md`.

Before edits, cite the shared S0 baseline if the contract is unchanged, or run `s3_baseline_01`.

Recommended rounds: 5.

Suggested outputs:

```text
exp/s3-key-file-set
results/metrics_s3.jsonl
```

### S4: Single-File / Core-Algorithm Optimization

Purpose: fallback when S1-S3 do not produce signal, or when a human expert identifies the core policy file.

Run local variant search inside the specified file or algorithm. Read `references/prompts/s4_single_file.md`.

Before variants, cite the shared S0 baseline if the contract is unchanged, or run `s4_baseline_01`.

Recommended rounds: optional, 3-5.

Suggested outputs:

```text
exp/s4-single-file
results/metrics_s4.jsonl
```

## Reporting

For each stage, summarize:

- context provided
- chosen optimization directions
- useful iteration ratio
- best valid metrics
- failed patches and why they failed
- invalid/no-signal attempts and why they were archived
- agent diagnosis versus human diagnosis
- needed expert knowledge

The main comparison is not just speedup. It is whether context level changes file localization, hypothesis quality, correctness, and useful iteration ratio.
