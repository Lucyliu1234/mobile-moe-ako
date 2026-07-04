---
name: mobile-moe-ako
description: Evaluate agentic coding for whole-system mobile MoE inference optimization. Use when Codex needs to run an AKO-style optimization loop for mobile MoE runtime policy, caching behavior, transfer scheduling, heterogeneous CPU/GPU/NPU execution, Android deployment, benchmark harnessing, structured metrics, iteration logs, git branches, best-version selection, failed-patch archives, or an external staged experiment protocol. Do not use for single-kernel CUDA/Triton optimization; use ako4all for that.
---

# MobileMoE-AKO

Drive an AKO-style analyze -> edit -> benchmark -> log -> commit loop for whole-system mobile MoE inference optimization. The target is not a single GPU kernel; it is the mobile runtime policy that controls caching, data movement, scheduling, and heterogeneous execution.

The goal is twofold:

- Try to improve `decode_tok_s` while preserving correctness and normalized transfer volume.
- Produce research evidence about what agentic coding can and cannot do in a real mobile MoE system.

## When this skill applies

Use this skill for AKO-style optimization of a mobile MoE inference system:

- mobile MoE runtime policy work
- caching, transfer scheduling, execution placement, or runtime coordination
- Android deployment and benchmark loops
- structured metrics and iteration logging for whole-system optimization
- optional external staged protocols such as `references/experiment_protocol.md`, only when explicitly requested

Does NOT apply when:

- The task is a single CUDA/Triton/TileLang kernel optimization; use `ako4all` instead.
- The user only wants a one-off code review with no benchmark loop.
- The user wants to design a paper experiment but not run or prepare the AKO loop.

### MobileMoE target

The base skill defines the AKO-style loop and benchmark discipline for whole-system mobile MoE runtime-policy optimization.

Keep the base context general:

- runtime policy
- caching behavior
- transfer scheduling
- heterogeneous CPU/GPU/NPU execution
- Android benchmark feedback

Do not put stage-specific expert mechanisms in the base skill. When a staged protocol intentionally provides more domain context, load the relevant prompt or expert hint from `references/`.

## First action

Before editing code or running a benchmark, establish the experiment workspace and stage.

### Inventory the workspace + prompt

Browse the target workspace and the MobileMoE-AKO package to identify:

- **Experiment label**: the run label, branch, or external protocol stage if the user provides one.
- **Runtime repo**: the repo containing the mobile MoE runtime/policy code, often `/home/liuxu/projects/MNN`, `/home/liuxu/projects/mllm`, or another user-specified tree.
- **Harness package**: the MobileMoE-AKO directory containing `scripts/agent_bench.sh`, normally `/home/liuxu/projects/mobile-moe-ako`.
- **Benchmark backend**: default `scripts/backends/qwen2_td_qnn.sh`, which adapts the known-good Qwen2 MoE TD QNN AOT Android command.
- **Android target**: `AKO_SERIAL` or runner default.
- **Model/prompt contract**: dataset, model artifact, decode length, repeat count, and correctness rule.
- **Allowed edit surface**: runtime/policy files only, unless the user explicitly widens the contract.
- **Existing logs**: `ITERATIONS.md`, `results/metrics_*.jsonl`, `patches/failed_attempts/`, prior stage branches.
- **Hints/context**: `references/system_overview.md`, `references/constraints.md`, `references/benchmark_instructions.md`, and `references/metrics_schema.md`. Do not read or expand `references/experiment_protocol.md` unless the user affirmatively asks to use, run, inspect, or evaluate the progressive context protocol, staged protocol, or how context affects agent behavior. A negated instruction such as "do not use the staged protocol" is not a trigger to read the protocol.
- **Localization rules**: `references/control_surface_localization.md`, used after profiling to translate raw metrics into a bounded optimization task.

Whether the runtime repo follows a clean research layout is not the signal. The signal is whether you can confidently identify the benchmark contract, policy surface, and guardrails.

### Ask only when genuinely uncertain

If the prompt and filesystem identify the stage, benchmark contract, and target repo, do not stop to ask. Proceed with a resolved plan.

Ask the user only when a wrong assumption would invalidate the experiment, for example:

- two different Android devices or benchmark runners could be the intended target
- the dataset/model/decode length is ambiguous
- the selected protocol refers to key files that were not provided and cannot be inferred
- a requested edit would touch benchmark/correctness code

### Always present the resolved plan before running anything

Before running a stage or making edits, state the resolved plan in this shape:

**Resolved Plan**

- **Experiment label**: `<label or protocol stage>`
- **Runtime repo**: `<path>`
- **Harness package**: `<path>`
- **Benchmark command**: `<command>`
- **Branch**: `<branch>` or `none`
- **Allowed edit surface**: `<paths or policy>`
- **Fixed contract**: `<model/prompt/decode/repeats/correctness>`
- **Primary metric**: `decode_tok_s`
- **Guardrails**: `correct`, `mib_per_token`, unchanged benchmark contract
- **Diagnostics**: transfer volume, cache behavior, scheduling delay, thermal state, and any stage-specific counters

If a field is still uncertain, resolve it before editing.

### Bringing in scaffold

The MobileMoE-AKO package owns the reusable harness scaffold:

- `harness/benchmark_adapter.py`
- `harness/localize_boundary.py`
- `harness/classify_result.py`
- `harness/extract_state_trace.py`
- `harness/harness_ledger.md`
- `scripts/agent_bench.sh`
- `scripts/backends/`
- `scripts/parse_metrics.py`
- `scripts/append_iteration.py`
- `ITERATIONS.md`
- `results/`
- `patches/failed_attempts/`

Prefer running the scaffold in place from `/home/liuxu/projects/mobile-moe-ako`. Copy scripts into a runtime repo only when the user explicitly wants a self-contained experiment branch there. If copying, do not overwrite an existing user-edited harness or iteration log.

### Persisting user-supplied hints

If the user gives experiment constraints, file hints, forbidden edits, benchmark settings, or stage/protocol instructions, persist them in the right durable location:

- Stable loop constraints belong in `references/constraints.md`.
- Benchmark invocation details belong in `references/benchmark_instructions.md`.
- Project-specific staged protocol details belong in `references/experiment_protocol.md`, not in `SKILL.md`.
- Per-iteration observations belong in `ITERATIONS.md`.

Do not leave important constraints only in the current chat turn.

### Surfacing hint changes

Whenever you persist user-supplied hints, tell the user what changed and where. Name the source, for example: "I added your fixed decode-length constraint from this prompt to `references/constraints.md`."

## Optional Research Protocol

The core skill is the reusable AKO-style MobileMoE loop. It does not require a specific staged experiment design.

Read `references/experiment_protocol.md` only if the user affirmatively asks to use, run, inspect, or evaluate the progressive context protocol, staged protocol, or how context affects agent behavior. Do not read it merely because the prompt says not to use the staged protocol. Do not include staged phases in a generic resolved plan.

Keep stage definitions in `references/experiment_protocol.md` and stage-specific prompts under `references/prompts/`. `SKILL.md` should remain the general execution discipline: workspace resolution, benchmark contract, edit loop, metrics, logging, commit/archive, and stopping rules.

## Workflow

1. **Load context.** Read `references/system_overview.md`, `references/constraints.md`, `references/benchmark_instructions.md`, `references/metrics_schema.md`, and `references/control_surface_localization.md`. Read `references/experiment_protocol.md` only when the user affirmatively requests the staged research protocol.
2. **Create or switch branch.** Use a branch that matches the experiment label and preserves useful commits. If the protocol specifies branch names, follow it.
3. **Verify baseline contract.** Confirm benchmark inputs, model, decode length, and correctness guardrail are fixed. Do not silently change them to make iteration easier.
4. **Verify stage baseline.** Before source edits in a stage, run or cite a baseline for the exact same benchmark contract. If the current protocol says no edits, run the harness and log the baseline without inspecting for changes.
5. **Analyze baseline diagnostic decomposition.** Before the first source edit in a stage, inspect the baseline benchmark output, metrics, logs, and device state allowed by the current prompt or staged protocol. Interpret metrics only within the context budget explicitly allowed for that stage. Record the suspected bottleneck and any missing diagnostics in `ITERATIONS.md`.
6. **Localize the control surface.** Use `references/control_surface_localization.md` to translate the baseline diagnostics into a bounded optimization task: bottleneck class, expensive physical event, triggering logical decision, allowed edit surface, forbidden-first surface, must-inspect read/write sites, expected metric movement, and falsification rule.
7. **Form the first hypothesis from the bounded task.** The first code-changing iteration must name the selected boundary it targets and which physical metric or diagnostic should move. Use only the concepts, diagnostics, file hints, and external knowledge allowed by the current prompt or staged protocol.
8. **Inspect files.** Discover the relevant runtime paths, or start from user-provided candidate files when available. Always verify the call path before editing.
9. **Make one coherent change.** Keep changes small enough to attribute metric movement to a policy hypothesis. Do not mix unrelated policy, benchmark, logging, parser, and instrumentation changes in one iteration.
10. **Run the harness.** Use `bash scripts/agent_bench.sh` from the MobileMoE-AKO package, or the equivalent copied into the runtime repo.
11. **Close the iteration immediately.** Append `ITERATIONS.md` and commit/archive before starting a new hypothesis.
12. **Compare against baseline and stage best.** Use primary and guardrail metrics, then diagnostics to explain why the attempt worked or failed.

## Diagnosis-Aware Control Loop

Use this loop to make the agentic optimization process more controllable. The goal is not to reveal a stage-specific answer; it is to force every edit to be tied to a diagnosable systems control surface.

### After baseline, before source edits

Produce a bottleneck localization report before making the first code change. Use `references/control_surface_localization.md` as the decision table for translating metrics into a bounded optimization task. This report can be written in the assistant message and summarized in `ITERATIONS.md`; it does not require a separate script unless the active prompt asks for one.

The report must include:

- **Observed bottleneck pattern**: the metric pattern seen in the baseline, such as high transfer volume, cache churn, service-time bottleneck, scheduling contention, thermal/noise, or missing diagnostics.
- **Evidence**: concrete metric names and values supporting the pattern.
- **Selected bounded task**: the smallest optimization boundary justified by the profile.
- **Expensive physical event**: the actual upload, read, write, synchronization, kernel execution, or resource action consuming time/bytes.
- **Triggering logical decision**: the cache lookup, admission decision, scheduler decision, operator dispatch, or policy branch that causes the physical event.
- **Allowed edit surface**: runtime states, policy decisions, resource paths, or kernel/operator classes that plausibly control the selected physical event.
- **Forbidden-first directions**: plausible-looking edits that should not be tried first because they do not address the selected boundary or cannot be validated by current diagnostics.
- **Code search targets**: functions, classes, state variables, or call paths to inspect first.
- **Must-inspect read/write sites**: where the controlling state is read before the expensive physical event, where it is written after the event, and where it can be invalidated or evicted.
- **Expected metric movement**: primary, guardrail, physical-cost, and supporting diagnostic fields that should move if the boundary is correct.
- **Falsification rule**: what result proves the boundary is logical-only, scheduling-only, latency-shift, noisy, or wrong-path.
- **Observation gaps**: missing counters or logs that would make a diagnostic-only iteration more valuable than an optimization attempt.

Do not jump from a raw metric to a patch. First translate the metric pattern into a bounded task and code search target. If the report cannot name an expensive physical event, a triggering logical decision, and at least one read/write site to inspect, prefer a diagnostic iteration over an optimization edit.

### Diagnostic planning gate

After localization and before the first optimization edit, decide whether the available diagnostics can distinguish the main competing causes inside the selected boundary. Use the Diagnostic Plan Gate in `references/control_surface_localization.md`.

If the selected boundary is plausible but competing causes remain indistinguishable, run one diagnostic-only iteration before optimization. The diagnostic plan must name:

- **Competing causes**: plausible reasons for the expensive physical event.
- **Missing observation**: the invisible state transition, resource lifetime, identity key, phase boundary, queue relation, or physical-skip relation.
- **Minimal instrumentation**: the smallest counters or logs needed to distinguish those causes.
- **Expected interpretation**: how each possible counter pattern maps to the next bounded task.
- **Non-goals**: benchmark semantics, correctness, prompt/decode contract, model work, and parser semantics that must remain unchanged.

Diagnostic-only iterations are not optimization wins. They should be archived or kept as diagnostic commits only when the active prompt asks for that. A later optimization patch must cite the diagnostic evidence that justifies its chosen control surface.

### State-relation sub-localization

For boundaries involving repeated physical work, apply the State-Relation Sub-Localizer from `references/control_surface_localization.md` before patching. Do not stop at a coarse label such as cache pressure, eviction, or queue contention if the diagnostics do not yet show how logical requests map to physical actions.

The report must identify:

- **Logical request identity**
- **Physical action identity**
- **Effect lifetime**
- **Coverage relation**
- **Invalidation reason**
- **Execution phase**
- **Reuse/skip decision**

If these fields cannot be inferred from current metrics and code inspection, prefer a state-relation diagnostic-only iteration. The diagnostic should expose whether a later logical request repeated a physical action even though the previous physical effect was still reusable, or whether the physical effect was truly unavailable.

### Patch hypothesis gate

Before every source edit, answer this gate explicitly:

1. What system bottleneck does this patch target?
2. What runtime state, policy decision, resource path, or compute path will this patch change?
3. Where is that state, decision, or path read, written, or executed in code?
4. Which selected boundary from the localization report does this patch stay inside?
5. What expensive physical event should be reduced or better scheduled?
6. What logical decision controls that physical event?
7. Where is the read site before the physical action, the write/update site after it, and any invalidation/eviction site?
8. Why is this on the critical path for the fixed benchmark?
9. What primary metric should improve?
10. What physical-cost diagnostics should move consistently with the hypothesis?
11. What supporting diagnostics should move consistently with the hypothesis?
12. What guardrail metrics must not regress?
13. What result would falsify the hypothesis?
14. What false positive could this patch create?
15. If the expected physical-cost movement does not appear, will this patch be rejected or archived?

Do not edit until the gate is answered. If the gate cannot be answered from existing diagnostics and code inspection, prefer one small diagnostic iteration over a speculative optimization patch.

### After each benchmark

Classify the result before deciding whether to commit or archive. Use the stage's metrics and guardrails, not only the primary metric.

Default result classes:

- **true_system_win**: primary metric improves beyond noise, guardrails hold, and diagnostics move consistently with the hypothesis.
- **transfer_win**: normalized transfer volume or physical upload volume falls without correctness or service regressions.
- **scheduling_win**: transfer volume is stable, but scheduling/service diagnostics and primary metric improve consistently.
- **logical_counter_only**: hit/miss or eviction counters improve, but physical transfer volume, service time, and primary metric do not support a real win.
- **latency_shift**: one service subcounter improves while another absorbs the cost, with no meaningful total service or primary-metric improvement.
- **noise_or_no_signal**: primary metric movement is within noise or diagnostics do not support the hypothesis.
- **regression**: correctness, primary metric, transfer guardrail, thermal comparability, or service diagnostics regress.
- **invalid**: build, deploy, correctness, generated-token, parser, or benchmark-contract failure.

Do not accept a patch based only on a local diagnostic if the end-to-end metric and guardrails do not support it. Do not accept a patch based only on a small primary-metric movement if diagnostics contradict the hypothesis.

Record the classification and the reason in `ITERATIONS.md`.

## Harness

Default command:

```bash
bash scripts/agent_bench.sh
```

Daytime fast smoke command:

```bash
AKO_BENCH_PROFILE=day_smoke_p16_d16 AKO_ITERATION_ID=runtime_iter_01 bash scripts/agent_bench.sh
```

Daytime signal recheck command:

```bash
AKO_BENCH_PROFILE=day_signal_p32_d32 AKO_ITERATION_ID=runtime_iter_01_recheck bash scripts/agent_bench.sh
```

Useful environment variables:

- `AKO_STAGE`: experiment group label used for `results/metrics_<stage>.jsonl`
- `AKO_BENCH_PROFILE`: optional fixed benchmark profile; supported values include `day_smoke_p16_d16` and `day_signal_p32_d32`
- `AKO_ITERATION_ID`: stable label such as `runtime_iter_01`
- `AKO_BUILD_CMD`: optional build command run in `AKO_CODE_REPO`
- `AKO_CODE_REPO`: repo where `AKO_BUILD_CMD` runs, default `/home/liuxu/projects/MNN`
- `AKO_BACKEND`: backend name, default `qwen2_td_qnn`
- `AKO_BACKEND_SCRIPT`: explicit backend script override
- `AKO_QWEN2_PHONE_BASE`: used by the default backend, default `/data/local/tmp/qwen2_moe_td_w8a16_clean_20260527`
- `AKO_PROMPT`: prompt text for default backend, default `hello`
- `AKO_TUCKER_ROOT`: used by the optional `ds2_edgemoe` backend, default `/home/liuxu/projects/tucker`
- `AKO_RUNNER_SCRIPT`: used by the optional `ds2_edgemoe` backend, default `${AKO_TUCKER_ROOT}/scripts/run_ds2_edgemoe_end2end.py`
- `AKO_SERIAL`: Android device serial
- `AKO_DATASET`: fixed prompt JSONL
- `AKO_DECODE_TOKENS`: fixed decode length
- `AKO_REPEATS`, `AKO_LIMIT`, `AKO_START_INDEX`: run scope controls
- `AKO_IDLE_SECONDS`, `AKO_SLEEP_BETWEEN_RUNS_S`, `AKO_COOLDOWN_MAX_WAIT_S`: thermal controls
- `AKO_OUT_ROOT`: output root, default `results/runs`

The public entry point is always `scripts/agent_bench.sh`. It calls a backend adapter under `scripts/backends/`. The default backend is `scripts/backends/qwen2_td_qnn.sh`, which wraps the known-good Qwen2 MoE TD QNN AOT Android command and writes `summary.jsonl` from the pulled device log. `scripts/parse_metrics.py` normalizes `summary.jsonl` into a single metrics JSON and appends it to `results/metrics_<stage>.jsonl`.

For harness-mediated studies, prefer the wrappers under `harness/`:

- `harness/benchmark_adapter.py` records a run manifest and calls the same fixed benchmark entry point.
- `harness/localize_boundary.py` turns baseline metrics into a bounded task before patching.
- `harness/classify_result.py` compares candidate metrics against baseline metrics and emits a verdict class.
- `harness/extract_state_trace.py` extracts sampled event-level state-relation traces from runtime logs when a repeated-work boundary needs per-key evidence.
- `harness/harness_ledger.md` records why harness rules changed.

For one-day studies, use `day_smoke_p16_d16` for most agent iterations and `day_signal_p32_d32` to recheck promising patches. Treat the evening 4-category run as the verdict benchmark, not as the per-iteration loop.

## Metrics

Primary:

- `decode_tok_s`: generated decode tokens per second. Higher is better.

Guardrails:

- `compile_success`: build and benchmark launch succeeded.
- `correct`: correctness passed. When the runner exposes `ret`, all rows should have `ret == 0`.
- `mib_per_token`: normalized dynamic transfer volume per generated token. It should not regress without a strong reason.

Diagnostics:

- transfer-volume counters
- cache-behavior counters
- scheduling/service-time counters
- optional energy counters
- optional thermal and memory counters

Read `references/metrics_schema.md` before interpreting missing or renamed fields.

## Iteration protocol

Every benchmarked code attempt is one iteration. Number sequentially inside the experiment label:

```text
runtime_iter_01
runtime_iter_02
cache_iter_01
schedule_iter_03
```

An iteration can be one of two types:

- **Optimization iteration**: changes runtime policy and is eligible to become the best patch if correctness and guardrails pass.
- **Diagnostic iteration**: adds lightweight counters or exposes existing diagnostics to improve bottleneck visibility. It is part of the same AKO loop, but is not eligible as a best speedup patch.

Each iteration has exactly this closure sequence:

1. Run the benchmark with a stable `AKO_ITERATION_ID`.
2. Append a structured entry to `ITERATIONS.md`.
3. Commit a useful/correct change, or save a failed patch under `patches/failed_attempts/`.

The log/archive step must happen before new probing or a new edit. This is AKO discipline: do not read the benchmark result, jump into the next idea, and reconstruct the log later from memory.

Before the first code-changing iteration in a stage, run or cite a baseline for the exact same fixed benchmark contract. If a shared protocol baseline already exists and the stage reuses the same contract, cite that result path in the first stage entry.

Each optimization iteration must be one coherent runtime-policy change tied to one hypothesis. Split unrelated edits into separate iterations, especially changes to caching behavior, scheduling behavior, diagnostics, build/deploy plumbing, and benchmark configuration.

Each diagnostic iteration must answer one observation gap, such as separating page-touch, enqueue, finish, and total required-miss service time. It must preserve benchmark semantics, generated-token accounting, model work, prompt set, correctness checks, and parser semantics. Mark it as `diagnostic-only` in `ITERATIONS.md`.

### Logging

Use:

```bash
python3 scripts/append_iteration.py \
  --iteration-id runtime_iter_01 \
  --stage runtime \
  --prompt-setting "MobileMoE-AKO core loop" \
  --hypothesis "..." \
  --direction "..." \
  --files-inspected "..." \
  --files-modified "..." \
  --change-summary "..." \
  --benchmark-command "AKO_STAGE=runtime AKO_ITERATION_ID=runtime_iter_01 bash scripts/agent_bench.sh" \
  --metrics-json results/runs/runtime_iter_01/metrics.json \
  --result "..." \
  --agent-diagnosis "..." \
  --my-diagnosis "..." \
  --needed-expert-knowledge "..." \
  --patch-or-commit "..."
```

Required research fields:

- `Chosen optimization direction`
- `My diagnosis`
- `Needed expert knowledge`

These matter even when speed does not improve.

### Commit or Archive

Commit only useful changes that compile and preserve correctness, unless the user explicitly wants all attempts committed.

Good commit messages:

```text
[runtime iter 02] Reduce repeated transfer under cache pressure
[runtime iter 03] Adjust scheduling to reduce transfer stalls
[runtime iter 04] Improve runtime cache reuse under fixed benchmark
```

Archive failed or invalid attempts, including:

- compile failure
- correctness failure
- generated-token mismatch
- `decode_tok_s` regression
- no metric movement
- hypothesis/metric mismatch
- wrong file localization
- edits to forbidden benchmark, prompt, parser, or accounting surfaces

For these attempts:

```bash
git diff > patches/failed_attempts/runtime_iter_03.patch
```

Then append `ITERATIONS.md` with the diagnosis and revert only the agent's own failed edits. Preserve unrelated user changes.

## Keeping the iteration loop fast

The benchmark is expensive because it includes Android deployment, device temperature, model execution, and log parsing. Make iteration faster only through explicit harness controls that preserve the experiment contract.

Allowed fast-loop controls when the user accepts them:

- reduce `AKO_LIMIT` for smoke/debug runs
- use `AKO_IDLE_SECONDS=0` for harness plumbing tests, not final measurements
- use fewer repeats for exploratory iterations, then re-run the best candidate with the full stage contract

Not allowed:

- changing the prompt dataset to make the policy look better
- changing decode length mid-stage without marking a new contract
- editing correctness checks or metric parser semantics
- hiding failed generated-token counts
- disabling expensive required work, hiding data movement, or calling skipped execution speedup

Separate signal from verdict:

- **Signal runs**: small prompt count or reduced thermal wait can help debug plumbing and compare rough policy direction.
- **Verdict runs**: use the fixed stage contract before declaring improvement or best version.

## Stall handling

When 3 consecutive iterations in a stage show no meaningful improvement, pause before editing again.

Meaningful improvement should exceed measured baseline noise or roughly 3%, whichever is more conservative.

Re-assess:

- Did the agent localize the right code path?
- Did the hypothesis name the right diagnostic?
- Did the benchmark run under comparable thermal conditions?
- Did `mib_per_token`, transfer volume, cache behavior, or scheduling delay move in the expected direction?
- Is the failure due to missing systems context, missing file hints, or a real performance floor?
- Would more context, better file localization, or extra instrumentation be more valuable than another blind edit?
- Are the existing counters sufficient to distinguish the competing hypotheses?
- If local diagnostics are insufficient, consult only knowledge sources allowed by the current prompt or staged protocol. Do not perform generic kernel-optimization search unless the current experiment is explicitly a kernel-level study. Record what external knowledge was used and whether that knowledge would have violated the current stage's context budget.

Default outcome:

- Record the failure mode before changing context, file hints, or optimization direction.
- Choose a new local policy axis only if diagnostics justify it.
- If diagnostics cannot distinguish plausible causes, run one diagnostic iteration before another optimization iteration.

Do not keep making random edits after a stall. The failure mode is part of the research output.

## When to stop

Stop the current run, stage, or experiment when:

1. The planned round count is reached.
2. Correctness or harness instability prevents comparable metrics and cannot be fixed without changing the contract.
3. Three or more directions have been tried and diagnostics show no plausible next policy move.
4. The user asks to move to the next stage.

Do not stop just because a single edit failed. Archive it and continue within the stage budget.

### Best-version handling on stop

At the end of a stage, identify the best version by reading:

- `ITERATIONS.md`
- `results/metrics_<stage>.jsonl`
- per-run `results/runs/<iteration>/metrics.json`
- git commits or failed patches

Best is not automatically the fastest single noisy run. Prefer:

- correctness passing
- stable or repeated `decode_tok_s` improvement
- no unacceptable `mib_per_token` regression
- diagnostics consistent with the hypothesis
- smaller and more interpretable code change

If the latest commit is not the best, restore the best version using git from the actual committed state rather than reconstructing from memory. Then run a final sanity benchmark and commit a stage-final marker if the user wants branches to preserve best versions.

## Profiling and diagnosis - best effort, not a gate

This skill does not assume `ncu`. Use system-level diagnostics instead:

- EdgeMoE/MobileMoE diagnostic counters
- Android logs
- `summary.jsonl`
- transfer volume
- cache behavior
- scheduling delay
- thermal and memory data

After a baseline, and after a stall, produce a MobileMoE profiling report from available counters before choosing the next optimization direction. For required-miss work, include all available decomposition fields:

- `decode_req_page_touch_ms`
- `decode_req_mat_enqueue_ms`
- `decode_req_mat_finish_ms`
- `decode_req_service_ms`
- `decode_req_mat_writes`
- `decode_req_page_touch_mib`
- `decode_core_upload_mib`
- `decode_req_miss`, `decode_req_hit`, and `decode_evict`

If these counters are missing or cannot distinguish the competing hypotheses, adding diagnostics can be a valid diagnostic iteration only when it does not change benchmark semantics. Log instrumentation-only iterations as such and do not treat them as speedup wins.

Do not optimize blindly. A hypothesis should connect code behavior to at least one metric.

Examples:

- If `mib_per_token` is high, inspect repeated data movement or cache policy.
- If cache behavior improves but `decode_tok_s` does not, inspect transfer contention or scheduling delay.
- If transfer volume falls but correctness fails, treat the result as invalid and archive the patch.
- If speed improves but correctness fails, treat the result as invalid and archive the patch.

## Guardrails

- Keep model, prompt set, decode length, correctness rule, and metric parser fixed inside a stage.
- Do not optimize by weakening the benchmark, skipping model work, changing generated-token accounting, or hiding data movement.
- Do not commit failed/correctness-breaking patches as useful results.
- Do not edit benchmark scripts, prompts, datasets, correctness checks, or parser semantics unless the user explicitly changes the experiment contract.
- Prefer small runtime-policy edits over broad refactors.
- Preserve user changes. Revert only edits made by the current failed attempt.

## Gotchas

- **Whole-system optimization is noisy.** Baseline spread matters. A 1% speed delta may be meaningless.
- **Android thermal state can dominate.** Compare runs only when cooldown/temperature conditions are comparable.
- **Local cache signals can hurt globally.** Better local reuse can still increase transfer contention or scheduling delay.
- **Cache hit rate is not the whole story.** A high hit rate can coexist with high transfer volume or bad service timing.
- **Correctness failures are data, not wins.** Archive and diagnose them.
- **File localization can be part of the experiment.** When the protocol tests discovery ability, a wrong file choice should be recorded as an agent failure mode.
- **Instrumentation can perturb behavior.** Keep diagnostics lightweight and note any added logging.
- **A no-speedup result can still be publishable.** The key output is the capability boundary and the context needed for useful agent behavior.

## Reference files

- `references/system_overview.md`: project framing and research questions.
- `references/benchmark_instructions.md`: harness usage, branches, and logging commands.
- `references/metrics_schema.md`: metric names and normalization.
- `references/constraints.md`: allowed and forbidden changes.
- `references/control_surface_localization.md`: reusable profiling-to-boundary localization rules.
- `references/state_relation_trace_schema.md`: event-level logical-request vs physical-action trace schema.
- `references/experiment_protocol.md`: optional staged research protocol for progressive context experiments.
- `references/expert_hints/coremoe_required_core.md`: expert mechanisms for stages that intentionally expose domain hints; read only when the active prompt or protocol permits it.
- `references/prompts/`: optional staged-protocol prompts; read only the prompt selected by the active protocol or user request.
- `scripts/backends/qwen2_td_qnn.sh`: default backend adapter for the known-good Qwen2 MoE TD QNN AOT Android command.
- `scripts/backends/ds2_edgemoe.sh`: optional backend adapter for the older DeepSeek-V2 EdgeMoE Android runner.
- `ITERATIONS.md`: durable iteration log.
- `results/metrics_*.jsonl`: structured metrics by stage.
- `patches/failed_attempts/`: archive of invalid or no-signal patches.
