Use $mobile-moe-ako.

You are running:
S6-Localizer-State-Relation MobileMoE-AKO.

Purpose:
Evaluate whether a state-relation sub-localizer can make a whole-system
optimization loop more controllable. The goal is not to reproduce a prior S6
answer. The goal is to test whether the agent can refine a coarse bottleneck
boundary into a logical-request vs physical-action relation before patching.

Runtime repo:
/home/liuxu/projects/mllm-s6-localizer-state-relation

This clean worktree has already been prepared. Continue from this worktree and
do not touch:

/home/liuxu/projects/mllm

Harness package:
/home/liuxu/projects/mobile-moe-ako

Branch:
exp/s6-localizer-state-relation

Base:
Use the clean pre-success base commit:
da9fa3534a16c0f34adb6709e2ba871741cbf8cc

The prepared worktree should already be on this branch and base. Do not switch
branches unless verification shows the prepared worktree is not in this state.

Iteration log isolation:
The old iteration log has already been preserved at:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS_BEFORE_s6_localizer_state_relation_20260704_011052.md

Before running the baseline or editing source code, verify that a matching
backup exists. If it is missing, copy:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS.md

to a uniquely named backup such as:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS_BEFORE_s6_localizer_state_relation_<timestamp>.md

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

Research question:
Can the harness convert a coarse bottleneck boundary into a state relation:

```text
logical request -> physical action -> reusable physical effect
```

before allowing optimization patches?

Goal:
Improve `decode_tok_s` only if the state-relation evidence supports a bounded
optimization patch. Avoid accepting logical-counter-only, latency-shift, or
wrong-relation changes.

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

- `s6_state_relation_localizer_baseline_fasttemp_p16_d16`
- `s6_state_relation_localizer_diag_01_fasttemp_p16_d16`
- `s6_state_relation_localizer_iter_01_fasttemp_p16_d16`
- `s6_state_relation_localizer_iter_02_fasttemp_p16_d16`
- `s6_state_relation_localizer_iter_03_fasttemp_p16_d16`

Only replace `<iteration_id>`.

Baseline provenance rule:
Before the baseline, build and deploy the Android runner from the selected base
and verify host/phone md5 match. Do not reuse an unknown phone-side runner.
Every diagnostic or optimization iteration must repeat build, deploy, host md5,
phone md5, and phone stat verification before benchmarking.

Expected build command:

```bash
cmake --build /home/liuxu/projects/mllm-s6-localizer-state-relation/build-android-arm64-v8a-qnn --target mllm-qwen2-moe-td-qnn-aot-runner
```

Expected deploy path:

```text
/data/local/tmp/qwen2_moe_td_w8a16_clean_20260527/mllm-qwen2-moe-td-qnn-aot-runner
```

Workflow:

1. Confirm branch, base, clean state, and log backup.
2. Build/deploy/md5-verify the baseline runner.
3. Run `s6_state_relation_localizer_baseline_fasttemp_p16_d16`.
4. Parse metrics and append a baseline entry to `ITERATIONS.md`.
5. Produce the standard localization report from
   `references/control_surface_localization.md`.
6. If the selected boundary involves repeated physical work, apply the
   State-Relation Sub-Localizer before any optimization edit.
7. The state-relation report must name:
   - logical request identity
   - physical action identity
   - effect lifetime
   - coverage relation
   - invalidation reason
   - execution phase
   - reuse/skip decision
8. If these fields are not observable from baseline metrics and code inspection,
   run one diagnostic-only iteration to expose the minimal state relation.
9. The diagnostic plan must not encode a project-specific answer. It should only
   expose the relation between logical requests and physical actions.
10. After the diagnostic, update the state-relation report and only then decide
    whether an optimization patch is justified.
11. Before every optimization edit, answer the patch gate from `SKILL.md` and
    cite the state-relation evidence.
12. Make one small runtime-policy patch inside the selected relation boundary.
13. Build/deploy/md5-verify, run one p16/d16 benchmark, parse metrics, append
    `ITERATIONS.md`, classify the result, and commit or archive immediately.

Allowed edit surface:
The selected bounded task determines the allowed runtime/policy edit surface.
By default, likely files include runtime policy code such as:

```text
/home/liuxu/projects/mllm-s6-localizer-state-relation/examples/qwen2_moe_td_qnn_aot/aot_run.cpp
/home/liuxu/projects/mllm-s6-localizer-state-relation/mllm/backends/opencl/moe/
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
- guardrails hold
- the patch changes the physical action, reuse/skip decision, or service cost
  predicted by the state-relation report
- physical-cost metrics and supporting diagnostics move consistently with the
  selected relation
- primary metric improves beyond smoke noise, or the active prompt explicitly
  treats the result as diagnostic-only rather than a speedup

Reject/archive a patch if:

- it only improves logical counters while physical action metrics are unchanged
- it improves a local subcounter while total service or primary metric does not
  support the hypothesis
- it changes scheduling while claiming a transfer/state-relation win without
  physical-action evidence
- it changes benchmark/correctness/parser semantics
- thermal or deployment conditions invalidate the comparison

Iteration budget:

- 1 baseline
- at most 1 state-relation diagnostic-only iteration before the first
  optimization patch
- up to 3 optimization iterations
- stop early after 3 consecutive correctness-passing no-signal, wrong-relation,
  logical-only, latency-shift, or regression results
- do not run p32/d32 unless a p16/d16 patch is accepted

Final report:
Summarize:

- baseline metrics
- localization report and selected bounded task
- state-relation report
- diagnostic plan, if one was needed, and what relation it exposed
- each patch gate and result classification
- whether the sub-localizer prevented false positives or coarse-boundary drift
- whether it improved harness controllability compared with the previous
  localizer-only and diagnostic-plan runs
- remaining missing diagnostics or expert knowledge
