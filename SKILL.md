---
name: mobile-moe-ako
description: Evaluate agentic coding for whole-system mobile MoE inference optimization. Use when Codex needs to run a MobileMoE/EdgeMoE-style whole-system AKO harness with Android deployment, profiling reports, event traces, boundary forms, candidate benchmarking, acceptance verdicts, iteration logs, commits, and failed-patch archives. Do not use for single-kernel CUDA/Triton/TileLang optimization; use ako4all for that.
---

# MobileMoE-AKO

Use this skill to run an AKO-style loop for a whole-system mobile MoE runtime.
The target is not one isolated kernel. The target is the runtime behavior around
model execution, data movement, caching, materialization, scheduling, and
heterogeneous execution.

The current default workflow is profiler-first:

```text
baseline benchmark
  -> trace extraction
  -> detail profile
  -> facts-only profile report
  -> empty boundary form
  -> agent fills causal boundary from profile facts and code inspection
  -> one coherent runtime patch
  -> candidate benchmark
  -> acceptance gate
  -> commit or archive
```

The harness provides facts and validation. The agent chooses the boundary and
the hypothesis. Do not use fixed bottleneck categories or pre-baked cause
labels as the default reasoning path.

## Scope

Use this skill for:

- MobileMoE/EdgeMoE runtime policy optimization.
- Android deploy/build/benchmark loops.
- Whole-system profiling, event traces, and metric parsing.
- Harness-mediated optimization experiments.
- Iteration logs, failed-patch archives, and best-version selection.

Do not use it for:

- Single CUDA/Triton/TileLang kernel optimization.
- A one-off code review with no benchmark loop.
- Changing benchmark, parser, prompt, dataset, or correctness semantics unless
  the user explicitly changes the experiment contract.

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
  sampled events and logs.
- `harness/profile_report.py`: builds facts-only `mobile_profile.json` from
  metrics, trace summaries, detail profile, and manifest.
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
--extra-env MLLM_QNN_TD_RESIDENCY_TRACE_EVENTS=1
--extra-env MLLM_QNN_TD_RESIDENCY_TRACE_EVENT_LIMIT=<N>
```

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

### 4. Fill The Boundary Form Before Patching

Before editing runtime code, fill `boundary_form.md` or copy its completed
content into `ITERATIONS.md`.

The agent must answer from profile facts and code inspection:

1. Suspected boundary.
2. Evidence from concrete profile fields and values.
3. Physical-vs-logical distinction.
4. Target files/functions/states to inspect.
5. State transition or execution hypothesis.
6. Expected metric movement.
7. Falsification condition.

The form is intentionally open. It must not provide candidate bottleneck
answers. If the evidence is insufficient, run a diagnostic-only iteration rather
than a speculative optimization patch.

### 5. Make One Coherent Runtime Patch

Each optimization iteration should change one runtime-policy idea only. Keep
benchmark semantics, parser semantics, prompt set, decode length, correctness
checks, and generated-token accounting unchanged.

Allowed surfaces are normally runtime policy, cache/resource state,
materialization, scheduling, execution placement, or operator implementation
code inside the runtime repo. If the needed edit is outside that surface, ask or
record the contract change.

### 6. Run Candidate Through The Same Adapter

If the candidate changed runtime code, build the runner, push it to the phone,
chmod it, and verify host md5 equals phone md5 before benchmarking. The
benchmark adapter pushes only the remote shell script and collects logs; it does
not guarantee that a newly built runner binary was deployed.

Use the same benchmark profile and trace settings as baseline. Pass
`--baseline-metrics` when using the adapter. Generate the same trace/profile
artifacts for the candidate when they are relevant to interpreting the result.

If a candidate launch fails with `Text file busy`, missing generated tokens, or
another pre-execution device/deploy error, classify the run as invalid. Do not
accept or reject the patch as a performance result until the runner has been
md5-verified on the phone and the exact same adapter command has produced
comparable metrics.

### 7. Run The Acceptance Gate

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

### 8. Commit Or Archive

If accepted, commit the runtime patch with a concise message tied to the
experiment. If rejected, inconclusive, or invalid, save the patch under:

```text
patches/failed_attempts/<experiment>_<iteration>.patch
```

Then revert only the edits made by that failed attempt. Preserve unrelated user
changes.

### 9. Log Immediately

Append `ITERATIONS.md` before starting another idea. Include:

- Baseline or candidate label.
- Benchmark command or adapter command.
- Metrics path.
- Profile artifacts path.
- Filled boundary summary.
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
