# Control-Surface Localization

This document defines the reusable localization step between profiling and
patching. Its purpose is to turn noisy whole-system metrics into a bounded
optimization task, so the coding agent does not search the entire runtime after
every baseline.

The rules here are intentionally system-level and not specific to a prior S6
answer. Project-specific counters may provide evidence, but the output should be
a generic boundary: what cost is expensive, what runtime decision triggers it,
what physical action consumes time or bytes, and which code surfaces may change
that action.

## Required Output

After every baseline and before any optimization edit, produce a localization
report with these fields:

- **Bottleneck class**: transfer, materialization/service, scheduling,
  compute/kernel, thermal/noise, correctness/harness, or missing diagnostics.
- **Expensive physical event**: the real action consuming time, bytes, energy, or
  device resources.
- **Triggering logical decision**: the cache lookup, admission decision,
  scheduler decision, operator dispatch, or policy branch that causes the
  physical event.
- **Selected bounded task**: one sentence describing what this run is allowed to
  optimize.
- **Allowed edit surface**: code paths that may plausibly control the expensive
  physical event.
- **Forbidden-first surface**: plausible but lower-priority surfaces that should
  not be edited before the selected boundary is falsified.
- **Must-inspect read/write sites**: where the controlling state is read before
  the physical event, where it is written after the event, and where it is
  invalidated or evicted.
- **Expected metric movement**: primary metric, physical-cost metrics, and
  supporting diagnostics that should move if the boundary is correct.
- **Falsification rule**: what result proves the patch is logical-only,
  scheduling-only, latency-shift, noisy, or on the wrong path.

If the report cannot name a physical event, a trigger, and at least one
read/write site to inspect, do not make an optimization edit. Run a diagnostic
iteration or narrow the benchmark contract first.

## Diagnostic Plan Gate

Localization chooses a boundary; it does not always prove which cause inside
that boundary is responsible. Before the first optimization patch, decide
whether the current diagnostics can distinguish the main competing causes for
the selected boundary.

If they cannot, produce a diagnostic plan and run a diagnostic-only iteration
before patching. The diagnostic must preserve benchmark semantics and expose why
the expensive physical event repeats, waits, or runs slowly.

The diagnostic plan must include:

- **Competing causes**: two or more plausible reasons for the selected physical
  event.
- **Missing observation**: what state transition, resource lifetime, key,
  phase boundary, or queue relation is currently invisible.
- **Minimal instrumentation**: the smallest counters or logs that distinguish
  those causes.
- **Expected interpretation**: how each possible counter pattern maps to the
  next bounded task.
- **Non-goals**: what the diagnostic will not change, such as correctness,
  prompt/decode contract, parser semantics, model work, or benchmark workload.

Generic diagnostic questions by boundary:

| Boundary | Must distinguish before patching when ambiguous |
| --- | --- |
| Transfer / residency | Is the repeated physical event caused by missing state, eviction/lifetime, resource-key mismatch, phase-boundary reset, or async/prewarm-vs-required state divergence? |
| Materialization/service | Is the time spent in demand work, queue wait, synchronization, page faulting, DMA/write service, or repeated materialization? |
| Scheduling | Is the stall caused by useful overlap missing, speculative work contention, queue saturation, priority inversion, or work submitted to an inactive path? |
| Compute/kernel | Is the kernel limited by memory bandwidth, occupancy, instruction mix, launch overhead, layout conversion, or an upstream/downstream operator? |
| Thermal/noise | Is the run incomparable because of start temperature, end temperature, throttling, background process activity, or measurement variance? |

For transfer/residency boundaries, useful generic counters often answer:

- whether a physical resource key was seen before;
- whether a duplicate happened before or after invalidation/eviction;
- whether the duplicate crossed a phase boundary;
- whether two paths used different keys or state tables for the same resource;
- whether a logical hit actually skipped the physical action.

Do not hard-code a prior solution. The diagnostic should identify which control
surface is real, not directly implement the suspected fix.

## State-Relation Sub-Localizer

When a selected boundary involves repeated physical work, do not stop at a
coarse explanation such as "cache pressure", "eviction", "queue contention", or
"misses are high". Refine the boundary by mapping logical requests to physical
actions and checking whether the physical effect could have been reused.

This sub-localizer is intentionally generic. Use project-specific names only as
instances of the following abstract fields:

- **Logical request identity**: the logical operation, lookup, tensor, page,
  block, RPC, compile request, operator call, or resource request that asks for
  work.
- **Physical action identity**: the real upload, disk read, network call,
  kernel launch, materialization, memory allocation, compilation, or other
  action that consumes time, bytes, energy, or device resources.
- **Effect lifetime**: how long the physical action's result remains valid or
  reusable.
- **Coverage relation**: which later logical requests are satisfied by one
  physical action.
- **Invalidation reason**: why the logical state, physical resource, or reusable
  effect stopped being valid.
- **Execution phase**: the stage, phase, thread, queue, or async path where the
  request/action/state transition occurred.
- **Reuse/skip decision**: whether a later logical request reused the previous
  physical effect or repeated the physical action, and why.

Before patching a repeated-work boundary, distinguish at least these cases:

1. The physical resource or effect was truly unavailable, so repeating the
   physical action was necessary.
2. The logical state record was missing or stale while the physical effect was
   still reusable.
3. One physical action covered multiple logical requests, but later requests did
   not use that coverage relation.
4. A later logical request repeated work even though the previous physical effect
   was still valid.
5. A counter measured logical churn rather than real physical churn.
6. Two execution phases or async paths used divergent state or identity keys for
   the same reusable effect.

If the current diagnostics cannot distinguish these cases, the next step should
be a state-relation diagnostic, not an optimization patch.

The diagnostic plan should expose only the smallest necessary state relation:

```text
logical_request_id:
physical_action_id:
effect_lifetime:
coverage_relation:
invalidation_reason:
execution_phase:
reuse_or_skip_decision:
```

Examples of this abstraction:

- GPU upload: logical tensor/resource request vs physical buffer upload.
- KV cache: logical token/block request vs physical memory residency.
- Disk cache: logical file/page request vs physical disk read.
- RPC: logical operation request vs physical network call.
- Kernel scheduling: logical operator invocation vs physical kernel launch.
- Compilation cache: logical compile request vs physical compilation action.

Do not encode a project-specific answer in the localizer. The goal is to make
the agent prove whether a logical request actually controls a physical action,
and whether a later request could reuse the previous physical effect.

## Generic Localization Rules

Use the following rules as a decision table. More than one may match; choose the
smallest boundary whose expected metric movement can be validated.

| Metric pattern | Bottleneck class | Bounded task | Allowed edit surface | Forbidden-first surface | Acceptance signal |
| --- | --- | --- | --- | --- | --- |
| High normalized transfer volume; high physical upload/read/write bytes; repeated physical events | Transfer / residency | Reduce repeated physical movement for the fixed workload | cache/residency lookup, resource identity keys, admission/skip logic, eviction/lifetime, materialization write path | kernel math, parser, benchmark, cosmetic counters, generic scheduling | physical bytes or write count decrease; primary metric improves or service drops |
| Logical cache hit/miss counters improve but physical bytes and service do not move | Logical-only accounting | Find the state that controls the physical skip, not just counters | read site before physical action, write site after physical action, eviction/invalidation site | accepting hit-rate alone, counter-only changes | physical skip/write/bytes move with logical counters |
| One service subcounter drops but another service subcounter rises; total service and primary metric do not improve | Latency shift | Identify the true blocking action rather than moving wait time between counters | total service path, queue wait, synchronization boundaries | local page-touch/enqueue/finish micro-edits without total-service proof | total service and primary metric improve together |
| Transfer stable; async submit/complete, queue backlog, or wait counters dominate; primary metric improves when scheduling pressure drops | Scheduling | Reduce contention or overlap stalls without changing required work | scheduling policy, prewarm admission, queue priority, throttling, overlap window | cache accounting, physical transfer elimination claims | scheduling counters and primary metric improve while transfer guardrail holds |
| Kernel/operator time dominates; transfer and cache counters are stable and low | Compute/kernel | Optimize the specific operator/kernel for the fixed workload | operator dispatch, kernel implementation, tensor layout, arithmetic path | cache/prefetch/materialization policy | kernel time and primary metric improve without extra transfer |
| Thermal or power state differs materially across runs | Noise / invalid | Restore comparable measurement conditions | benchmark timing, cooldown, device state, repeated measurement | optimization edits based on hot/noisy runs | comparable thermal envelope before judging patch |
| Counters cannot distinguish competing causes | Missing diagnostics | Add minimal diagnostic instrumentation | counters/logs that preserve benchmark semantics | speculative optimization edits | new counters identify a smaller bounded task |

## Patch Gate Extension

Before editing, the agent must bind the patch to the selected boundary:

```text
Selected boundary:
Expensive physical event:
Triggering logical decision:
Read site before physical action:
Write/update site after physical action:
Invalidation/eviction site:
Expected physical metric movement:
Expected supporting diagnostic movement:
False-positive risk:
Reject if:
```

Do not patch outside the selected boundary unless code inspection falsifies the
boundary first. If the boundary is falsified, update the localization report and
log the reason before choosing a new one.

If a diagnostic plan was required, the first optimization patch must cite the
new diagnostic evidence. Do not ignore a diagnostic-only iteration and continue
with the original guess if the evidence points to a different cause.

## Result Classification

Use the normal MobileMoE-AKO result classes, but classify against the selected
boundary:

- A transfer boundary cannot be accepted on logical hit-rate improvement alone.
- A scheduling boundary cannot be reported as a transfer win if bytes are
  unchanged.
- A kernel boundary cannot be accepted if the measured gain comes from skipped
  work, changed benchmark semantics, or changed generated-token accounting.
- A diagnostic boundary is not a speedup patch, even if it exposes the right
  next target.

The goal is not to prevent exploration. The goal is to make every exploration
step auditable: profiling chooses a boundary, the boundary chooses code surfaces,
and the benchmark verdict decides whether the patch actually moved the physical
cost it claimed to control.
