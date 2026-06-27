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
