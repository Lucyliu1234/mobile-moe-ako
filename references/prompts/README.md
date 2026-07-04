# Staged Prompt References

This directory stores the concrete Codex prompts used for the MobileMoE-AKO staged runs.

These files are not just abstract stage templates. They intentionally include the practical constraints used in the actual runs, such as:

- runtime branch names
- old-log isolation rules
- fixed Tucker benchmark commands
- p16/d16 smoke and p32/d32 recheck contracts
- temperature-gated benchmark settings
- build/deploy verification requirements
- run-count limits and early-stop rules
- reporting fields

Use `references/experiment_protocol.md` for the high-level staged research design, and use the matching prompt file here as the source of truth when reproducing a specific stage run.

Do not silently replace these prompts with shorter summaries. If a future run uses a different prompt, add it as a separate prompt reference or clearly mark the version.

`harness_full_v1_optimization_test.md` is the current formal prompt for testing
the new profiler-first harness as an optimization environment. It uses
`mobile_profile.json`, `boundary_form.md`, agent-filled causal hypotheses, and
the acceptance gate. Prefer it for new harness validation runs.

`s1_plus_s6style_diagnostic_blackbox.md` is a derived controlled experiment rather than one of the original staged phases. It keeps the low-expert black-box context budget but uses a diagnostic-driven workflow, while explicitly forbidding prior-answer leakage.

`s6_localizer_bounded_loop.md` is a derived controllability experiment. It tests
whether a reusable profiling-to-boundary localization step can turn whole-system
diagnostics into a bounded optimization task before the agent patches code.

`s6_localizer_state_relation.md` is a derived controllability experiment. It
tests whether a state-relation sub-localizer can refine a coarse boundary into a
logical-request vs physical-action relation before optimization patches.

`s6_long_horizon_state_relation.md` is a derived controllability experiment. It
uses the state-relation workflow with a longer autonomous iteration budget,
multiple diagnostic-only iterations, and reflection checkpoints to test whether
previous failures were caused by short budgets or by insufficient
localization/feedback.

## Old Harness Prompt Archive

Older harness-evolution prompts are archived under
`references/prompts/old_harness/`.

Those files preserve the exact historical prompts used while developing the
earlier `bounded_task.json` / `localize_boundary.py` style harness. They are
kept for audit and reproduction, not as the default flow for new runs.

For new harness-mediated optimization tests, use the current `$mobile-moe-ako`
skill flow:

```text
benchmark_adapter.py
  -> extract_state_trace.py
  -> detail_profile.py
  -> profile_report.py
  -> boundary_template.py
  -> agent-filled boundary form
  -> candidate benchmark
  -> acceptance gate
```

The current harness should provide profiling facts and an empty boundary form;
the agent should infer the boundary from profile evidence and code inspection.
