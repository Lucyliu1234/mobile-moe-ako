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

## 2026-07-04 - Add Event-Level State-Relation Trace Schema

Finding:
The B-only harness v0 run forced `bounded_task.json`, `state_relation.json`, and
classifier-based rejection, but the state relation remained aggregate. It could
say that repeated physical work existed, but not which logical request caused
which physical action or whether a later miss happened before or after physical
invalidation.

Evidence:
The S6 harness v0 bounded-flow run archived in `ITERATIONS.md` rejected an
`accept=false` regression and reported that the remaining weakness was missing
per-key logical/physical identity.

Harness change:
Add `references/state_relation_trace_schema.md` and
`harness/extract_state_trace.py` so future runs can collect sampled
`[TD-RES-TRACE]` JSON events and summarize logical-key / physical-key chains.

Status:
Accepted as harness v1 diagnostic design. This is not an optimization; it is a
more precise observation layer for deciding which control surface is real.

## 2026-07-04 - Add Trace Plumbing Sentinel

Finding:
The first V1 event-trace run requested trace env vars and passed correctness,
but `state_trace_summary.json` contained zero events. That left two very
different possibilities indistinguishable: build/deploy/env/log capture was not
proven, or the active runtime path never hit event-emission sites.

Harness change:
Require a `trace_config` sentinel event before data events are interpreted. Add
the V1.1 trace-plumbing prompt so zero-event diagnostics split into:

- no sentinel: binary/env/log path not proven;
- sentinel only: active-path instrumentation gap;
- sentinel plus data events: event-level state relation can be analyzed.

Status:
Accepted as observability plumbing. This is a diagnostic reliability change, not
a runtime optimization.

## 2026-07-04 - Require Binary Provenance Before Trace Interpretation

Finding:
The V1.1 trace-plumbing run initially produced zero events because the deployed
phone runner did not match the rebuilt local runtime binary. After rebuilding
`/home/liuxu/projects/mllm` at `f4a73850`, deploying that exact runner, and
verifying host/phone md5 equality, the same trace path produced `trace_config`
and data events.

Harness change:
Event-trace prompts and schema now require host/phone runner md5 verification
before interpreting missing traces. An md5 mismatch is classified as
`binary_provenance_invalid`, not as an event-schema or active-path failure.

Status:
Accepted. This turns an ambiguous zero-event observation into a concrete
build/deploy provenance gate.
