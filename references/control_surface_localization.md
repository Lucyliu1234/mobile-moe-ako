# Control-Surface Localization

This document defines the reusable boundary-definition step between profiling
and patching. Its purpose is to make the coding agent define a bounded
optimization task before editing. The harness should provide profiling facts,
not enumerate possible control surfaces in a whole-system runtime.

Project-specific counters may provide evidence, but the harness output should be
a profile report plus an empty boundary template, not a final bottleneck verdict
or candidate-axis list. The agent must define a concrete boundary before
patching.

## Required Output

After every baseline and before any optimization edit, produce:

- **Profile report**: facts organized by section, such as validity, throughput,
  transfer, cache, materialization service, residency aggregate, state trace,
  thermal, and provenance.
- **Boundary form**: an empty, strong template the agent must fill before
  patching. The form should require suspected boundary, profile evidence,
  physical-vs-logical distinction, target control surface, state transition
  hypothesis, expected metric movement, and falsification condition.
- **Expensive physical event**: the real action consuming time, bytes, energy, or
  device resources, filled by the agent after inspection.
- **Triggering logical decision**: the cache lookup, admission decision,
  scheduler decision, operator dispatch, or policy branch that causes the
  physical event, filled by the agent after inspection.
- **Selected bounded task**: one sentence describing what this run is allowed to
  optimize, filled by the agent after inspection.
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

If the agent cannot fill the boundary form with concrete profile facts and code
references, do not make an optimization edit. Run a diagnostic iteration or
narrow the benchmark contract first.

## Diagnostic Plan Gate

The harness does not choose the final boundary. The agent chooses or defines one
after reading profiling facts and code. Before the first optimization patch,
decide whether the current diagnostics can distinguish the main competing
causes for the selected boundary.

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

Do not hard-code a prior solution. A diagnostic should expose missing facts, not
directly implement the suspected fix.

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

## Patch Gate Extension

Before editing, the agent must fill the boundary definition and bind the patch
to it:

```text
Selected or newly defined boundary:
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

Do not patch before this definition is filled. Do not patch outside the selected
boundary unless code inspection falsifies it first. If the boundary is
falsified, update the workspace and log the reason before choosing a new one.

If a diagnostic plan was required, the first optimization patch must cite the
new diagnostic evidence. Do not ignore a diagnostic-only iteration and continue
with the original guess if the evidence points to a different cause.

## Patch Acceptance Verdict

Use the normal MobileMoE-AKO acceptance gate against the selected boundary:

- `invalid`: compile, correctness, generated-token, benchmark-contract, or
  metric-comparability failure.
- `accept`: correctness passed and the primary metric improved beyond the
  configured threshold.
- `reject`: the primary metric clearly regressed.
- `inconclusive`: primary movement is below threshold.

Other metrics should be reported as deltas or warnings. They are evidence for
the agent to interpret, not result classes.

The goal is not to prevent exploration. The goal is to make every exploration
step auditable: profiling exposes facts, the agent defines a boundary, the
boundary chooses code surfaces, and the benchmark verdict decides whether the
patch actually moved the physical cost it claimed to control.
