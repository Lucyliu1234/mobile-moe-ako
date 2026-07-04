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
  simple patch-acceptance verdict.
- `harness/boundary_template.py` writes the pre-patch boundary form the agent
  must fill before patching.
- `references/cases/s6-residency/` stores a compact S6 reference case so future
  runs do not need to rediscover the same traps from the full iteration log.

Status:
Accepted as harness v0. This does not claim a new MobileMoE optimization; it
makes future optimization attempts more auditable and less dependent on prompt
memory.

## 2026-07-04 - Add Event-Level State-Relation Trace Schema

Finding:
The B-only harness v0 run forced `bounded_task.json`, `state_relation.json`, and
candidate-verdict rejection, but the state relation remained aggregate. It could
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

## 2026-07-04 - Validate V1 Event-Level Localization

Finding:
The formal V1 event-localization run produced a valid p16/d16 benchmark and
sampled 2002 trace events. Aggregate metrics selected the same broad
transfer/residency boundary, but event samples exposed a more precise relation:
one packed physical upload records a coverage set for `gate/up/down`, while
many later sibling logical accesses still miss before any keyed eviction can be
observed in the sample.

Evidence:
`s6_harness_v1_event_localization_fasttemp_p16_d16` has
`res_probe=32256`, `res_upload=7344`, `res_dup_upload=4912`, and event counts
`upload=265`, `record=795`, `later_access=544`, `evict=123`. The event-level
profile exposed covered sibling logical misses whose physical lifetime was not
yet keyed well enough to interpret confidently.

Harness change:
Fix `scripts/parse_metrics.py` to normalize both `decode_hybrid_*` fields and
the backend's actual `hybrid_*` fields, so `res_*`, required-miss, upload, and
service counters are visible to the boundary form workflow.

Status:
Accepted as harness v1 profiling evidence. Event-level tracing improves
observability over aggregate counters, but the next observation-layer gap is
keyed lifetime: evict and later-access events need `physical_key` or `slot_id`,
and repeat uploads need stable identity beyond pointer-only keys.

## 2026-07-04 - Add V1.2 Keyed Lifetime Trace

Finding:
V1 event-level tracing showed covered sibling logical misses, but could not say
whether those misses happened before or after physical invalidation. V1.2 added
stable physical identity, slot id, coverage state, keyed eviction, and
stable-key repeat-upload evidence.

Evidence:
`s6_harness_v1_2_keyed_lifetime_fasttemp_p16_d16` passed correctness and
sampled 4002 trace events. Derived relation counts were
`later_miss_before_keyed_evict=886`, `later_miss_after_keyed_evict=10`,
`keyed_evict=230`, and `repeat_upload_by_stable_key=7`.

Harness change:
Upgrade the runtime diagnostic trace and `harness/extract_state_trace.py` so the
state-relation summary includes keyed lifetime facts and derived relation counts
rather than only raw events.

Status:
Accepted as harness v1.2 profiling evidence. The broad transfer/residency
boundary now has fine-grained event timelines: many sampled covered sibling
misses occur before keyed eviction, while keyed eviction and stable-key repeat
upload events are also visible. This is profiler output for the agent to
interpret, not a fixed cause label baked into the harness.

## 2026-07-04 - Change Localizer Into Boundary Workspace

Finding:
The first bounded-task localizer was still too close to a fixed expert decision
table. Even when it stopped short of a semantic state-trace diagnosis, it could
still steer the agent by naming a small set of candidate boundaries. For a
whole-system runtime, that list will never be complete.

Harness change:
`harness/localize_boundary.py` emitted a boundary-definition workspace:

- observed signal groups from the current metrics;
- non-exhaustive suggested observation axes;
- `agent_may_ignore_or_extend_suggested_axes=true`;
- a `required_boundary_definition` template the agent must fill before patching.

Status:
Superseded by the profile-report split below. This was a useful intermediate
step, but suggested axes still risked steering the agent.

## 2026-07-04 - Split Profile Report From Boundary Template

Finding:
Even non-exhaustive suggested axes can steer the agent toward harness-authored
possibilities. The current research goal is to measure more useful facts and let
the agent choose the boundary.

Harness change:
Add `harness/profile_report.py` to produce a facts-only profile report. Simplify
`harness/localize_boundary.py` so it emits only the empty
`required_boundary_definition` template.

Status:
Accepted. Profiling now provides data; the boundary template provides process
discipline; the agent supplies the bottleneck interpretation.

## 2026-07-04 - Rename Localizer To Boundary Template

Finding:
The name `localize_boundary.py` still implied that the harness was choosing the
control surface. The intended B-flow is different: the harness provides facts
and a strong form, while the agent supplies the causal boundary explanation.

Harness change:
Add `harness/boundary_template.py` as the formal entry point. It writes
`boundary_form.md`, a Markdown form requiring the agent to fill:

- suspected boundary;
- evidence from profile;
- physical-vs-logical distinction;
- target control surface;
- state transition hypothesis;
- expected metric movement;
- falsification condition.

`harness/localize_boundary.py` is kept only as a compatibility wrapper for old
prompts.

Status:
Accepted. B now means facts-only profiling plus a strong causal explanation
template, not a harness-authored localizer.

## 2026-07-04 - Simplify Candidate Verdict Gate

Finding:
The first candidate classifier used explanatory result classes. That made the
acceptance gate look like another bottleneck interpreter, which conflicts with
the profiler-first harness design.

Harness change:
`harness/classify_result.py` now emits only `accept`, `reject`, `inconclusive`,
or `invalid`, plus metric deltas, guardrail failures, warnings, and notes.

Status:
Accepted. The script is now a patch acceptance gate, not a diagnosis engine.

## 2026-07-04 - Expand Facts-Only Profiling Quality

Finding:
After the profiler/localizer split, the remaining bottleneck was not another
rule. The harness still hid useful observations that were already present in
runtime logs, especially decode-phase operator timing, upload attribution,
kernel timing, and page-residency/page-touch related fields.

Harness change:
Expose richer profiling facts without adding bottleneck categories:

- `scripts/parse_metrics.py` now normalizes decode-phase timing, upload MiB,
  upload/enqueue/finish attribution, kernel breakdown, and page-residency
  fields when present.
- `scripts/backends/qwen2_td_qnn.sh` now summarizes decode-phase
  `[TD-RUN][hybrid-cold]` layer logs into `decode_hybrid_*` totals for future
  adapter runs.
- `harness/profile_report.py` adds facts-only sections for operator timing,
  compute, upload attribution, and page residency, plus explicit missing
  observation lists.

Status:
Accepted as profiling-quality v1.3. This does not choose a boundary for the
agent; it gives the agent more measured facts and makes missing measurements
visible.

## 2026-07-04 - Add Generic Runtime-Event Detail Profile Tables

Finding:
Aggregate metrics and event traces were useful, but the agent still had to
manually scan raw event streams to find which logical requests, physical
actions, resources, phases, or reuse/skip outcomes dominated the sampled
behavior.

Harness change:
Add `harness/detail_profile.py`. It converts existing `state_trace.jsonl` and
runtime logs into facts-only ranked tables:

- physical action hotspots;
- logical request hotspots;
- resource lifetime hotspots;
- phase/path breakdown;
- reuse/skip effectiveness;
- physical resource byte hotspots;
- coverage-size counts.

MobileMoE layer and projection breakdowns are kept under
`adapter_specific_appendix` instead of the main profile.

`harness/profile_report.py` can embed this report through `--detail-profile`.

Status:
Accepted as profiling-quality v1.4. This increases granularity without adding
new bottleneck categories or harness-selected directions.

## 2026-07-04 - Demote Layer Breakdowns To Adapter Appendix

Finding:
Layer-level rankings are useful for MobileMoE debugging, but they are not a
universal whole-system runtime coordinate. Making layer rankings a primary
profile view risks steering the agent toward adapter-specific explanations.

Harness change:
Change `harness/detail_profile.py` so the main output is
`runtime_event_profile`, organized around logical requests, physical actions,
resources, phases, reuse/skip outcomes, and coverage. Move MobileMoE layer and
projection breakdowns under `adapter_specific_appendix`.

Status:
Accepted. The harness now treats layer as adapter metadata, while the primary
profile remains generic enough for other runtime systems.
