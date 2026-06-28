# S1 Black-Box Prompt

You are optimizing a mobile MoE inference system. You have the repository, a fixed benchmark command, and guardrails.

Use only the base MobileMoE-AKO skill, benchmark instructions, constraints, metrics schema, and the fixed benchmark feedback. Do not read `references/expert_hints/`, S2-S4 prompt files, or prior human optimization notes during S1.

External search is disabled for S1 unless the benchmark or harness cannot run. If search is needed for a harness/environment failure, restrict it to neutral tooling topics such as Android thermal measurement, adb connectivity, QNN runtime error interpretation, or shell/build issues. Do not search for MoE-specific optimization mechanisms, expert caching, expert prefetching, residency, required-core serving, or prior CoreMoE hints. Missing domain knowledge should be recorded as an S1 capability-boundary finding.

Objective:

- Improve `decode_tok_s` without breaking correctness or worsening `mib_per_token`.
- Do not edit benchmark inputs, prompts, correctness checks, metric parsers, or model artifacts.
- Discover relevant code paths yourself.

Required loop:

1. Run or cite a baseline for this exact benchmark contract before editing.
2. Decompose the baseline using only benchmark-exposed metrics, logs, and device state. Record the primary metric, correctness, generated-token status, normalized transfer guardrail if exposed, thermal/device state if exposed, any other raw metrics the harness reports, missing diagnostics, and the bottleneck you infer yourself. Do not use supplied MoE-specific categories to interpret the metrics.
3. Inspect the repo and identify a plausible bottleneck without being given key files.
4. State one concrete hypothesis, the targeted bottleneck, and the expected diagnostic movement.
5. Make one coherent runtime-policy change only.
6. Run `bash scripts/agent_bench.sh` through the fixed profile selected for this S1 contract.
7. Immediately record metrics and diagnosis in `ITERATIONS.md`.
8. Commit the correctness-passing change or archive the failed patch before starting another hypothesis.

One-day S1 execution:

- Use branch `exp/s1-blackbox-mobile-moe-ako`.
- Use `AKO_BENCH_PROFILE=day_smoke_p16_d16` for the baseline and 3 smoke iterations.
- Use `AKO_BENCH_PROFILE=day_signal_p32_d32` only to recheck promising correctness-passing patches.
- Use the evening 4-category verdict benchmark only for baseline-vs-best comparison.

Archive failures as research evidence, including compile failure, correctness failure, speed regression, no metric movement, wrong file localization, forbidden-surface edits, or hypothesis/metric mismatch.
