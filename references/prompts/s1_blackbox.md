# S1 Black-Box Prompt

You are optimizing a mobile MoE inference system. You have the repository, a fixed benchmark command, and guardrails.

Use only the base MobileMoE-AKO skill, benchmark instructions, constraints, and the fixed benchmark feedback. Do not read `references/expert_hints/` or S2-S4 prompt files during S1.

Objective:

- Improve `decode_tok_s` without breaking correctness or worsening `mib_per_token`.
- Do not edit benchmark inputs, prompts, correctness checks, metric parsers, or model artifacts.
- Discover relevant code paths yourself.

Required loop:

1. Run or cite a baseline for this exact benchmark contract before editing.
2. Inspect the repo and identify a plausible bottleneck.
3. State one concrete hypothesis and the expected metric movement.
4. Make one coherent runtime-policy change only.
5. Run `bash scripts/agent_bench.sh`.
6. Immediately record metrics and diagnosis in `ITERATIONS.md`.
7. Commit the correctness-passing change or archive the failed patch before starting another hypothesis.

Archive failures as research evidence, including compile failure, correctness failure, speed regression, no metric movement, wrong file localization, forbidden-surface edits, or hypothesis/metric mismatch.
