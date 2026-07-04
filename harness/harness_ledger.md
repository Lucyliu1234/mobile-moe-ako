# MobileMoE-AKO Harness Ledger

This ledger records why the harness changes, not whether a particular runtime
patch was fast. It is the audit trail for turning MobileMoE from a prompt-driven
experiment into a bounded, feedback-explicit agent environment.

## 2026-07-04 - Add V0 Bounded-Feedback Harness

Finding:
Repeated S6-family runs showed that free-form prompting can find real runtime
issues, but it also lets the agent chase false positives: logical hit/miss
counter improvements, page-touch latency shifts, scheduling-only changes, and
inactive control surfaces.

Evidence:
S6 verify, ablation, causal-gate, skill-control-loop, control-surface-map,
state-relation, and long-horizon runs archived in `ITERATIONS.md` and
`patches/failed_attempts/`.

Harness change:
Add a small AKO4X-style harness layer:

- `harness/benchmark_adapter.py` wraps the existing benchmark entry point and
  records a manifest per run.
- `harness/classify_result.py` compares baseline/candidate metrics and emits a
  verdict class such as `logical_counter_only`, `latency_shift`, `regression`,
  `no_signal`, `transfer_win`, or `true_system_win`.
- `harness/localize_boundary.py` turns normalized metrics into a bounded task
  before patching.
- `references/cases/s6-residency/` stores a compact S6 reference case so future
  runs do not need to rediscover the same traps from the full iteration log.

Status:
Accepted as harness v0. This does not claim a new MobileMoE optimization; it
makes future optimization attempts more auditable and less dependent on prompt
memory.
