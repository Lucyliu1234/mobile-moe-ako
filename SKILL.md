---
name: mobile-moe-ako
description: Evaluate agentic coding for whole-system mobile MoE inference optimization. Use when Codex needs to run a MobileMoE/EdgeMoE-style whole-system AKO harness with Android deployment, profiling reports, event traces, boundary forms, candidate benchmarking, acceptance verdicts, iteration logs, commits, and failed-patch archives. Do not use for single-kernel CUDA/Triton/TileLang optimization; use ako4all for that.
---

# MobileMoE-AKO

Use this skill to run an AKO-style loop for a whole-system mobile MoE runtime.
The target is not one isolated kernel. The target is the runtime behavior around
model execution, data movement, caching, materialization, scheduling, and
heterogeneous execution.

The current default workflow is a simple compute-vs-bandwidth triage followed
by profiler-first exploration:

```text
baseline benchmark
  -> trace extraction
  -> detail profile
  -> facts-only profile report
  -> compute-vs-bandwidth triage
  -> empty boundary form
  -> agent fills causal boundary from profile facts and code inspection
  -> one coherent runtime patch
  -> candidate benchmark
  -> acceptance gate
  -> commit or archive
```

The harness provides facts, a coarse route decision, and validation. If the
profile is compute/operator-bound, switch to the original AKO4ALL workflow in
`/home/liuxu/projects/AKO4ALL`. If the profile is bandwidth/system-bound, stay
in the MobileMoE profiler-first harness and let the agent choose the concrete
runtime boundary from profile facts. Do not use pre-baked cause labels or
known-case answers as the default reasoning path.

## Scope

Use this skill for:

- MobileMoE/EdgeMoE runtime policy optimization.
- Android deploy/build/benchmark loops.
- Whole-system profiling, event traces, and metric parsing.
- Harness-mediated optimization experiments.
- Iteration logs, failed-patch archives, and best-version selection.

Do not use this skill itself to perform:

- Single CUDA/Triton/TileLang kernel optimization.
- A one-off code review with no benchmark loop.
- Changing benchmark, parser, prompt, dataset, or correctness semantics unless
  the user explicitly changes the experiment contract.

If profiling shows the active bottleneck is an isolated compute/operator kernel,
use this skill only to record the triage decision. Then switch to the original
AKO4ALL workflow in `/home/liuxu/projects/AKO4ALL` for the kernel/operator
itself instead of forcing a whole-system runtime patch loop.

## First Action

Before edits or benchmarks, identify the experiment contract:

- Experiment label or stage.
- Runtime repo, often `/home/liuxu/projects/mllm`.
- Harness repo, normally `/home/liuxu/projects/mobile-moe-ako`.
- Benchmark backend, normally `scripts/backends/qwen2_td_qnn.sh`.
- Android target serial, if specified.
- Fixed dataset, decode length, repeats, cache capacity, correctness rule.
- Allowed edit surface, normally runtime/policy code only.
- Existing `ITERATIONS.md`, prior metrics, and failed-patch archives.
- Whether this is a smoke test, a profiling-only run, or an optimization run.

Then present a resolved plan:

```text
Experiment label:
Runtime repo:
Harness repo:
Benchmark entry:
Branch/worktree:
Allowed edit surface:
Fixed contract:
Primary metric:
Guardrails:
Profiling artifacts:
Stop rule:
```

Ask the user only when a wrong assumption would invalidate the run, such as an
ambiguous device, benchmark contract, runtime repo, or permission to touch
benchmark/correctness code.

## Context To Load

Always read these before a real harness run:

- `references/system_overview.md`
- `references/constraints.md`
- `references/benchmark_instructions.md`
- `references/metrics_schema.md`

Read these only when relevant:

- `references/state_relation_trace_schema.md`: when using event-level state or
  residency traces.
- `references/experiment_protocol.md`: only if the user explicitly asks for the
  staged/progressive-context protocol.
- `references/control_surface_localization.md`: historical guidance or optional
  comparison material. It is not the default localizer for new harness runs.
- `references/expert_hints/`: only when the active prompt or protocol permits
  expert hints.
- `references/prompts/`: only the prompt selected by the active user request or
  protocol.

## Harness Tools

Prefer the reusable scaffold in `/home/liuxu/projects/mobile-moe-ako`:

- `harness/benchmark_adapter.py`: runs the fixed benchmark entry point and
  writes `adapter_manifest.json`.
- `harness/extract_state_trace.py`: extracts `[TD-RES-TRACE]` JSON events from
  runtime logs into `state_trace.jsonl` and `state_trace_summary.json`.
- `harness/detail_profile.py`: builds generic runtime-event hotspot tables from
  sampled events and logs, including residency events, QNN context timeline,
  lm_head timing, and async preload/activation overlap facts when those logs are
  present.
- `harness/profile_report.py`: builds facts-only `mobile_profile.json` from
  metrics, trace summaries, detail profile, and manifest.
- A manually filled triage section in `boundary_form.md`: records whether the
  profile is compute/operator-bound or bandwidth/system-bound from measured
  profile facts. This is a coarse router, not a patch diagnosis.
- `harness/boundary_template.py`: writes `boundary_form.md`, an empty causal
  form the agent must fill before patching.
- `harness/classify_result.py`: acceptance gate for a candidate patch. It emits
  `accept`, `reject`, `inconclusive`, or `invalid`; it does not diagnose the
  bottleneck.
- `scripts/agent_bench.sh`: stable benchmark entry point.
- `scripts/append_iteration.py`: durable iteration-log appender.

Do not copy harness scripts into the runtime repo unless the user explicitly
wants a self-contained branch.

## Complete Harness Optimization Flow

Use this for a real optimization test.

### 1. Preserve The Log

Before the first run in a new experiment, copy `ITERATIONS.md` to a timestamped
backup under `iterations/backups/`:

```text
iterations/backups/ITERATIONS_BEFORE_<experiment_label>_<timestamp>.md
```

### 2. Run Baseline Through The Adapter

Run `harness/benchmark_adapter.py run` with a stable label, stage, runtime repo,
and fixed profile. For current Qwen2 TD QNN residency/event tracing, use:

```text
--trace-residency
--extra-env AKO_QWEN2_RESIDENCY_TRACE_EVENTS=1
--extra-env AKO_QWEN2_RESIDENCY_TRACE_EVENT_LIMIT=<N>
```

The adapter/backend layer maps these `AKO_QWEN2_*` controls to the on-device
`MLLM_QNN_TD_*` environment variables. When using `benchmark_adapter.py`, pass
the `AKO_QWEN2_*` controls rather than direct phone-only `MLLM_*` names.

If ADB fails with a smartsocket/listener permission error, rerun the exact same
adapter command with escalated device access. Do not change benchmark settings
to work around device permissions.

### 3. Build Baseline Profile Artifacts

From the baseline run directory, generate:

- `state_trace.jsonl`
- `state_trace_summary.json`
- `detail_profile.json`
- `mobile_profile.json`
- `boundary_form.md`

The profile report is facts-only. It should expose observations and missing
observations, not choose an optimization direction.

### 4. Triage Compute Versus Bandwidth/System

Before choosing a patch surface, perform a coarse bottleneck triage from
`mobile_profile.json`, `detail_profile.json`, and the benchmark manifest.

The triage must answer:

1. Is the profile primarily `compute_operator_kernel` or `bandwidth_system`?
2. Which concrete profile fields and values support that choice?
3. Why is the other route weaker for the current run?
4. What evidence would falsify this route choice?

Use only these route names:

- `compute_operator_kernel`: a single operator/kernel dominates enough of the
  end-to-end runtime that local kernel speedup can plausibly move the primary
  metric. Do not patch MobileMoE runtime policy first. Switch to the original
  AKO4ALL workflow in `/home/liuxu/projects/AKO4ALL` for operator/kernel
  optimization, then use the MobileMoE adapter only for end-to-end validation.
- `bandwidth_system`: the bottleneck is not an isolated compute kernel, or the
  profile points to bytes moved, upload/download, page-touch, materialization,
  synchronization/wait, cache/residency, logical/physical resource state, QNN
  context, async overlap, or other whole-system runtime costs. Stay in the
  MobileMoE profiler-first harness. Do not subdivide this route into fixed
  subcategories; let the agent choose the concrete runtime boundary from the
  profile and code inspection.

This triage is deliberately coarse. It only decides whether to use original
AKO4ALL for compute-bound operator work or MobileMoE-AKO for bandwidth/system
runtime exploration.

### 5. Fill The Boundary Form Before Patching

Before editing runtime code, fill `boundary_form.md` or copy its completed
content into `ITERATIONS.md`.

The agent must answer from profile facts and code inspection:

1. Suspected boundary.
2. Evidence from concrete profile fields and values.
3. Physical-vs-logical distinction.
4. Target files/functions/states to inspect.
5. State transition or execution hypothesis.
6. State/resource consistency audit when the profile exposes physical actions,
   logical requests, resource coverage, reuse, invalidation, eviction, phase
   reset, or later accesses.
7. Mechanism-first intervention audit: list plausible control surfaces for the
   selected boundary, including but not limited to physical action,
   execution/dispatch owner, scheduling/overlap, resource lifetime,
   metadata/state accounting, memory layout/allocation, kernel/operator
   integration, and telemetry/provenance. Choose the intervention that most
   directly tests the causal hypothesis while keeping the result interpretable
   and benchmark semantics unchanged. Do not prefer a smaller text diff when it
   only changes a knob or weakly probes the mechanism. If choosing a narrower
   probe, explain what mechanism it isolates. If choosing a broader
   mechanism-level change, explain why the broader change is necessary and what
   metrics would distinguish success from collateral effects.
8. Expected metric movement.
9. Falsification condition.

The form is intentionally open. It must not provide candidate bottleneck
answers. If the evidence is insufficient, run a diagnostic-only iteration rather
than a speculative optimization patch.

When listing control surfaces, use the following generic whole-system runtime
map as prompts for inspection, not as fixed answers:

- Physical action: upload, download, materialization, page touch, memcpy,
  mmap/madvise, buffer write/read.
- Execution/dispatch owner: CPU/GPU/QNN placement, subgraph owner, packed versus
  unpacked path, synchronous versus async path.
- Scheduling/overlap: preload timing, queue depth, async admission, activation
  wait, finish/wait placement, context switch timing.
- Resource lifetime: cache residency, eviction, invalidation, pin/protect
  lifetime, phase reset, arena reuse.
- Metadata/state accounting: logical versus physical state, coverage records,
  hit/miss bookkeeping, stable keys, duplicate detection.
- Memory layout/allocation: buffer pooling, allocation reuse, arena capacity,
  span coalescing, alignment, fragmentation.
- Kernel/operator integration: launch shape, local size, quant block handling,
  auxiliary upload/readback, host-device boundary.
- Telemetry/logging/provenance: use as diagnostic instrumentation unless the
  profile shows measurable overhead.

### 6. Make One Coherent Patch In The Selected Route

Each optimization iteration should change one idea only. Keep benchmark
semantics, parser semantics, prompt set, decode length, correctness checks, and
generated-token accounting unchanged.

Prefer a mechanism-level runtime intervention that directly tests the current
hypothesis while keeping the result interpretable. Do not optimize for the
smallest text diff when a slightly broader mechanism-level change would test
the causal boundary more clearly. The patch should avoid unrelated behavior
changes that make the result hard to interpret. After the hypothesis is
validated, later iterations may broaden or tune the implementation for larger
effect.

Avoid treating constant-only changes as mechanism patches. A patch that only
changes a numeric default, capacity, threshold, slot count, lookahead, memory
budget, batch cap, or enable flag is allowed as a diagnostic probe only when
the boundary form says what mechanism it is probing and what observation would
confirm or falsify it. If such a probe produces a signal, the next iteration
must either convert that signal into a mechanism-level runtime policy or run a
diagnostic-only iteration to measure the missing mechanism. Do not continue
sweeping nearby numeric values unless the user explicitly asks for parameter
tuning.

Allowed MobileMoE bandwidth/system surfaces are normally runtime policy,
cache/resource state, materialization, scheduling, execution placement, transfer
paths, synchronization, or operator integration code inside the runtime repo.
If the selected route is `compute_operator_kernel`, the allowed surface shifts
to the isolated operator/kernel implementation and the original AKO4ALL
benchmark harness. If the needed edit is outside the selected route's surface,
ask or record the contract change.

### 7. Run Candidate Through The Same Adapter

If the candidate changed runtime code, build the runner, push it to the phone,
chmod it, and verify host md5 equals phone md5 before benchmarking. The
benchmark adapter pushes only the remote shell script and collects logs; it does
not guarantee that a newly built runner binary was deployed.

Use the same benchmark profile and trace settings as baseline. Pass
`--baseline-metrics` when using the adapter. Generate the same trace/profile
artifacts for the candidate when they are relevant to interpreting the result.
For `compute_operator_kernel` route, first use the operator-local AKO4ALL
benchmark to judge the local kernel patch; then use the MobileMoE adapter as
the end-to-end validation gate.

If a candidate launch fails with `Text file busy`, missing generated tokens, or
another pre-execution device/deploy error, classify the run as invalid. Do not
accept or reject the patch as a performance result until the runner has been
md5-verified on the phone and the exact same adapter command has produced
comparable metrics.

### 8. Run The Acceptance Gate

Run `harness/classify_result.py` with baseline and candidate metrics.

The verdict gate is only a patch acceptance check:

- `accept`: correctness passed and `decode_tok_s` improves beyond threshold.
- `reject`: primary metric clearly regresses.
- `inconclusive`: movement is below threshold or too noisy.
- `invalid`: build, deploy, correctness, generated-token, contract, or metric
  comparability failure.

Other metrics should be emitted as deltas or warnings. Let the agent explain
why they moved in the iteration log; do not encode system-cause categories in
the verdict.

### 9. Commit Or Archive

If accepted, commit the runtime patch with a concise message tied to the
experiment. If rejected, inconclusive, or invalid, save the patch under:

```text
patches/failed_attempts/<experiment>_<iteration>.patch
```

Then revert only the edits made by that failed attempt. Preserve unrelated user
changes.

### 10. Log Immediately

Append `ITERATIONS.md` before starting another idea. Include:

- Baseline or candidate label.
- Benchmark command or adapter command.
- Metrics path.
- Profile artifacts path.
- Filled boundary summary.
- Compute-vs-bandwidth triage decision.
- Files inspected and modified.
- Patch hypothesis.
- Acceptance verdict and metric deltas.
- Agent diagnosis and remaining missing observations.
- Commit hash or archived patch path.

## Diagnostic-Only Iterations

Use a diagnostic-only iteration when profile facts cannot distinguish the next
safe edit. A diagnostic iteration may add lightweight counters or event logs,
but it must preserve model work and benchmark semantics.

Good diagnostic targets are generic runtime observations:

- Operator/kernel timing.
- Upload attribution.
- Page residency or prefault behavior.
- Queue/enqueue/finish/wait timing.
- Event-level state/resource lifetime.
- Logical request vs physical action mapping.
- QNN context preload/activation timing, including wait, cleanup, context-free,
  graph-map rebuild, and async-satisfied load facts.
- lm_head upload/kernel/readback timing.
- Runtime async overlap facts, including preload enter/done, load satisfied by
  async preload, and activation wait time.
- Thermal and provenance comparability.

Diagnostic iterations are not speedup wins. Mark them as diagnostic-only, log
the observation they answer, and do not treat them as accepted optimization
patches.

## Event-Level Profiling

Use event traces when aggregate counters are insufficient. The main profile
coordinate system should be generic runtime events, not MobileMoE layers.

Useful event fields include:

- `event`
- `phase`
- `logical_key`
- `physical_key`
- `stable_physical_key`
- `slot_id`
- `action`
- `bytes`
- `covered_logical_keys`
- `invalidated_by`
- `later_access`

MobileMoE-specific layer/expert/projection tables belong in
`adapter_specific_appendix`; they are supplemental facts, not the main harness
logic.

## Acceptance And Best Version

Primary metric:

- `decode_tok_s`, higher is better.

Guardrails:

- `compile_success`
- `correct`
- generated token count
- fixed benchmark contract
- `mib_per_token` and other transfer metrics as warnings/guardrails, not as
  bottleneck diagnoses

Do not accept a patch because a local diagnostic improved if end-to-end
throughput and correctness do not support it. Do not accept tiny speed movement
inside the noise band as a system win.

If an optimization patch is accepted at p16/d16, run the configured larger
recheck such as p32/d32 only then. Do not run p32/d32 for rejected or
inconclusive patches.

At the end of a stage, best version is not automatically the fastest noisy run.
Prefer correctness-passing, comparable, interpretable improvements with stable
guardrails and a clear patch hypothesis.

## Stop Rules

Stop the current optimization run when:

- The user-requested round count is reached.
- One accepted patch is found, if the prompt asks to stop there.
- Three consecutive optimization attempts are non-accepted.
- Correctness or harness instability prevents comparable metrics.
- The profile shows that another optimization edit would be blind without a
  diagnostic-only iteration.

Do not stop merely because one patch failed. Archive it and continue within the
stage budget unless the stop rule triggers.

## Branches And Worktrees

Use a branch matching the experiment label. Prefer a normal branch when the
main runtime repo can be touched. Use a separate worktree only when the user
asks to isolate from the main repo, or when existing dirty state makes a clean
experiment impossible.

Do not reset, delete, or revert user changes without explicit permission.

## Fast Loop Versus Verdict

Fast-loop controls can be used only when the experiment contract allows them:

- Smaller prompt limits for plumbing/debug.
- Lower idle time for harness smoke tests.
- Fewer repeats for exploratory signal.

Verdict runs must use the fixed stage contract. Do not change dataset, decode
length, generated-token accounting, parser logic, or correctness checks to make
a patch look better.

## Reference Map

- `references/system_overview.md`: project framing.
- `references/constraints.md`: stable allowed/forbidden changes.
- `references/benchmark_instructions.md`: benchmark setup and profiles.
- `references/metrics_schema.md`: metric names and normalization.
- `references/state_relation_trace_schema.md`: optional event trace schema.
- `references/control_surface_localization.md`: historical/optional
  localization guidance; not the default new harness flow.
- `references/experiment_protocol.md`: optional staged research protocol.
- `references/prompts/`: optional run prompts selected by user/protocol.
- `harness/harness_ledger.md`: why harness rules changed.
- `ITERATIONS.md`: durable experiment log.
- `iterations/backups/`: archived snapshots of `ITERATIONS.md` before runs.
- `results/runs/`: per-run artifacts.
- `results/metrics_*.jsonl`: stage metrics streams.
- `patches/failed_attempts/`: archived failed patches.

## Gotchas

- Whole-system mobile runs are noisy; temperature and device state matter.
- Instrumentation can perturb behavior; keep it lightweight and record it.
- Better local counters do not prove a system win.
- Correctness failure is never a speedup.
- Missing observations are useful research evidence.
- A no-speedup run can still improve the harness if it makes failures more
  auditable and prevents false acceptance.
