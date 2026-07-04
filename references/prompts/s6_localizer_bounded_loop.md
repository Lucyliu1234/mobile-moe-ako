Use $mobile-moe-ako.

You are running:
S6-Localizer-Diagnostic-Plan MobileMoE-AKO.

Purpose:
Evaluate whether an explicit profiling-to-boundary localizer makes the agentic
systems optimization loop more controllable. This is not a test of whether a
specific prior S6 answer can be reproduced. It is a test of whether profiling
can choose a bounded task before the agent patches code.

Runtime repo:
/home/liuxu/projects/mllm-s6-localizer-diagnostic-plan

This clean worktree has already been prepared. Continue from this worktree and
do not touch:

/home/liuxu/projects/mllm

Harness package:
/home/liuxu/projects/mobile-moe-ako

Branch:
exp/s6-localizer-diagnostic-plan

Base:
Use the clean pre-success base commit:
da9fa3534a16c0f34adb6709e2ba871741cbf8cc

The prepared worktree is already on this branch and base. Do not switch
branches unless verification shows the prepared worktree is not in this state.

Iteration log isolation:
The old iteration log has already been preserved at:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS_BEFORE_s6_localizer_diagnostic_plan_20260703_233039.md

Before running the baseline or editing source code, verify this backup exists.
If it exists, do not create another backup solely for this run. If it is missing,
copy:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS.md

to a uniquely named backup such as:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS_BEFORE_s6_localizer_diagnostic_plan_<timestamp>.md

Then append this experiment's entries to:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS.md

Do not delete or overwrite old iteration logs.

Prepared-worktree note:
Because this is a git worktree, submodule directories may be empty. If configure
or build fails because initialized third-party submodule contents are missing,
copy only the needed initialized submodule directory contents from the existing
main runtime tree at /home/liuxu/projects/mllm into the prepared worktree. Do
not reset, checkout, clean, or otherwise modify /home/liuxu/projects/mllm.

Required context:
Read and follow:

- /home/liuxu/projects/mobile-moe-ako/SKILL.md
- /home/liuxu/projects/mobile-moe-ako/references/constraints.md
- /home/liuxu/projects/mobile-moe-ako/references/benchmark_instructions.md
- /home/liuxu/projects/mobile-moe-ako/references/metrics_schema.md
- /home/liuxu/projects/mobile-moe-ako/references/control_surface_localization.md
- this prompt file

Do not read prior S6 answer reports, prior successful commit diffs, or prior
failed patch archives as direct patch guidance. Broad git status or directory
listings may reveal their names; ignore those names and do not open their
contents.

Goal:
Improve `decode_tok_s` on the fixed benchmark while preserving correctness and
not worsening normalized transfer volume.

Primary research question:
Can the loop convert profiling into a clear bounded task before patching?

Secondary research question:
Does the selected boundary prevent false positives such as logical-counter-only
improvements, latency shifts, or wrong-path scheduling changes?

Additional research question:
Can the localizer generate a useful diagnostic plan when the boundary is clear
but the cause inside that boundary is still ambiguous?

Benchmark contract:
Use the fixed p16/d16 daytime smoke contract:

```bash
cd /home/liuxu/projects/mobile-moe-ako
/home/liuxu/projects/tucker/tucker_env/bin/python \
  /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py \
  --serial 10.29.230.131:5555 \
  --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl \
  --decode-tokens 16 \
  --repeats 1 \
  --idle-seconds 30 \
  --sleep-between-runs-s 0 \
  --cooldown-poll-s 30 \
  --cooldown-max-wait-s 600 \
  --max-start-skin-c 37 \
  --max-start-battery-c 34 \
  --context-len 384 \
  --gpu-cache-capacity 8 \
  --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/<iteration_id>
```

Use this exact contract for:

- `s6_localizer_diagplan_baseline_fasttemp_p16_d16`
- `s6_localizer_diagplan_diag_01_fasttemp_p16_d16`, if the diagnostic planning gate says competing causes are not distinguishable
- `s6_localizer_diagplan_iter_01_fasttemp_p16_d16`
- `s6_localizer_diagplan_iter_02_fasttemp_p16_d16`
- `s6_localizer_diagplan_iter_03_fasttemp_p16_d16`

Only replace `<iteration_id>`.

Baseline provenance rule:
Before the baseline, build and deploy the Android runner from the selected base
and verify host/phone md5 match. Do not reuse an unknown phone-side runner.
Every optimization iteration must repeat build, deploy, host md5, phone md5,
and phone stat verification before benchmarking.

Expected build command:

```bash
cmake --build /home/liuxu/projects/mllm-s6-localizer-diagnostic-plan/build-android-arm64-v8a-qnn --target mllm-qwen2-moe-td-qnn-aot-runner
```

Expected deploy path:

```text
/data/local/tmp/qwen2_moe_td_w8a16_clean_20260527/mllm-qwen2-moe-td-qnn-aot-runner
```

Workflow:

1. Confirm branch, base, clean state, and log backup.
2. Build/deploy/md5-verify the baseline runner.
3. Run `s6_localizer_diagplan_baseline_fasttemp_p16_d16`.
4. Parse metrics and append a baseline entry to `ITERATIONS.md`.
5. Use `references/control_surface_localization.md` to produce a localization
   report before any optimization edit.
6. The localization report must name:
   - bottleneck class
   - expensive physical event
   - triggering logical decision
   - selected bounded task
   - allowed edit surface
   - forbidden-first surface
   - must-inspect read/write/eviction sites
   - expected metric movement
   - falsification rule
7. Run the diagnostic planning gate from `references/control_surface_localization.md`.
   If the selected boundary is clear but competing causes inside that boundary
   are not distinguishable, run one diagnostic-only iteration before any
   optimization patch.
8. The diagnostic plan must name:
   - competing causes
   - missing observation
   - minimal instrumentation
   - expected interpretation
   - non-goals
9. If the report cannot name a physical event, trigger, and code search target,
   run one diagnostic-only iteration instead of an optimization patch.
10. Before every optimization edit, answer the patch gate from `SKILL.md`,
   including the selected boundary and expected physical-cost movement.
11. Make one small runtime-policy patch inside the selected boundary.
12. Build/deploy/md5-verify, run one p16/d16 benchmark, parse metrics, append
    `ITERATIONS.md`, classify the result, and commit or archive immediately.

Allowed edit surface:
The selected bounded task determines the allowed runtime/policy edit surface.
By default, likely files include runtime policy code such as:

```text
/home/liuxu/projects/mllm-s6-localizer-diagnostic-plan/examples/qwen2_moe_td_qnn_aot/aot_run.cpp
/home/liuxu/projects/mllm-s6-localizer-diagnostic-plan/mllm/backends/opencl/moe/
```

Do not edit benchmark scripts, prompts, datasets, correctness checks,
generated-token accounting, parser semantics, model artifacts, or phone runner
contract unless the task is explicitly diagnostic-only and semantics are
unchanged.

Acceptance:
Accept a patch only if:

- correctness passes
- generated tokens match the contract
- benchmark contract and md5 deploy verification hold
- primary metric improves beyond smoke noise or the selected diagnostic goal is
  met
- guardrails hold
- physical-cost metrics and supporting diagnostics move consistently with the
  selected boundary

Reject/archive a patch if:

- it only improves logical counters while physical cost is unchanged
- it moves latency from one subcounter to another without total-service or
  primary improvement
- it changes scheduling while claiming a transfer win without transfer evidence
- it changes benchmark/correctness/parser semantics
- thermal or deployment conditions invalidate the comparison

Iteration budget:

- 1 baseline
- at most 1 localizer-guided diagnostic-only iteration before the first optimization patch
- up to 3 optimization iterations
- stop early after 3 consecutive correctness-passing no-signal, wrong-boundary,
  logical-only, latency-shift, or regression results
- do not run p32/d32 unless a p16/d16 patch is accepted

Final report:
Summarize:

- baseline metrics
- localization report and selected bounded task
- diagnostic plan, if one was needed, and what ambiguity it resolved
- each patch gate and result classification
- whether the localizer prevented false positives
- whether it improved control-surface localization compared with free-form S6
  prompting
- remaining missing diagnostics or expert knowledge
