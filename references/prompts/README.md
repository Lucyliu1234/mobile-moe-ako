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

`s6_harness_v0_bounded_flow.md` is the B-group pilot for the AKO4X-style harness
flow. It does not rerun old S6 as A-control; instead it uses historical S6 runs
as qualitative controls and tests whether `harness/benchmark_adapter.py`,
`harness/localize_boundary.py`, state-relation files, and
`harness/classify_result.py` make the loop more controllable.

`s6_harness_v1_event_trace.md` is a diagnostic-harness evolution prompt. It
tests whether sampled `[TD-RES-TRACE]` event logs and
`harness/extract_state_trace.py` can upgrade aggregate state relations into
per-key logical-request / physical-action evidence before optimization.

`s6_harness_v1_1_trace_plumbing.md` is a diagnostic-only follow-up for empty
event traces. It expects a runtime `trace_config` sentinel and classifies the
failure as binary/env/log plumbing vs active-path event instrumentation.
