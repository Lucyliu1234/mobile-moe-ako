Use $mobile-moe-ako.

You are running:
S6-Long-Horizon-State-Relation MobileMoE-AKO.

Purpose:
Test whether longer autonomous iteration helps a whole-system agentic
optimization loop, once the harness provides localization, state-relation
gating, active-path verification, and strict verdict rules.

This is not a prompt for random extra attempts. It is a controlled long-horizon
run to answer whether previous failures were mainly caused by short iteration
budget or by insufficient localization/feedback.

Runtime repo:
/home/liuxu/projects/mllm-s6-long-horizon-state-relation

This clean worktree has already been prepared. Continue from this worktree and
do not touch:

/home/liuxu/projects/mllm

Harness package:
/home/liuxu/projects/mobile-moe-ako

Branch:
exp/s6-long-horizon-state-relation

Base:
Use the clean pre-success base commit:
da9fa3534a16c0f34adb6709e2ba871741cbf8cc

The prepared worktree should already be on this branch and base. Do not switch
branches unless verification shows the prepared worktree is not in this state.

Iteration log isolation:
The old iteration log has already been preserved at:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS_BEFORE_s6_long_horizon_state_relation_20260704_015111.md

Before running the baseline or editing source code, verify this backup exists.
If it is missing, copy:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS.md

to a uniquely named backup such as:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS_BEFORE_s6_long_horizon_state_relation_<timestamp>.md

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

Research questions:

1. Does a longer horizon improve the chance of finding a useful system patch?
2. Does a longer horizon mostly produce more no-signal/wrong-path attempts?
3. Can repeated diagnostic and reflection steps make the control surface
   progressively more precise?
4. Does the agent avoid repeating failed patch classes when forced to summarize
   failure modes?

Goal:
Improve `decode_tok_s` only if state-relation evidence supports the patch.
Reject logical-counter-only, latency-shift, wrong-relation, wrong-active-path,
or thermal/noise results even if a local metric looks better.

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

- `s6_long_state_relation_baseline_fasttemp_p16_d16`
- `s6_long_state_relation_diag_01_fasttemp_p16_d16`
- `s6_long_state_relation_diag_02_fasttemp_p16_d16`
- `s6_long_state_relation_diag_03_fasttemp_p16_d16`
- `s6_long_state_relation_iter_01_fasttemp_p16_d16`
- `s6_long_state_relation_iter_02_fasttemp_p16_d16`
- ...
- `s6_long_state_relation_iter_12_fasttemp_p16_d16`

Only replace `<iteration_id>`.

Baseline provenance rule:
Before the baseline, build and deploy the Android runner from the selected base
and verify host/phone md5 match. Do not reuse an unknown phone-side runner.
Every diagnostic or optimization iteration must repeat build, deploy, host md5,
phone md5, and phone stat verification before benchmarking.

Expected build command:

```bash
cmake --build /home/liuxu/projects/mllm-s6-long-horizon-state-relation/build-android-arm64-v8a-qnn --target mllm-qwen2-moe-td-qnn-aot-runner
```

Expected deploy path:

```text
/data/local/tmp/qwen2_moe_td_w8a16_clean_20260527/mllm-qwen2-moe-td-qnn-aot-runner
```

Core workflow:

1. Confirm branch, base, clean state, and log backup.
2. Build/deploy/md5-verify the baseline runner.
3. Run `s6_long_state_relation_baseline_fasttemp_p16_d16`.
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
   run a diagnostic-only iteration to expose the minimal state relation.
9. After each diagnostic-only iteration, update the state-relation report and
   decide whether the next step is another diagnostic or an optimization patch.
10. Before every optimization edit, answer the patch gate from `SKILL.md` and
    cite the current state-relation evidence.
11. Make one small runtime-policy patch inside the selected relation boundary.
12. Build/deploy/md5-verify, run one p16/d16 benchmark, parse metrics, append
    `ITERATIONS.md`, classify the result, and commit or archive immediately.

Long-horizon controls:

- Run up to 12 optimization iterations or up to about 3 hours, whichever comes
  first.
- Run up to 3 diagnostic-only iterations total.
- Every diagnostic-only iteration must resolve one named ambiguity. It is not a
  speedup patch.
- Every 3 optimization iterations, pause for a reflection entry in
  `ITERATIONS.md` before continuing.
- The reflection entry must summarize:
  - failed patch classes tried so far
  - boundaries or relations falsified so far
  - diagnostics that changed the search space
  - repeated mistakes to avoid
  - whether continuing is likely to add information
- Do not repeat the same patch class unless new diagnostic evidence changes the
  hypothesis.
- Do not switch boundaries or relations without citing new diagnostic evidence
  or a code-path falsification.
- If active-path verification fails, do not patch that relation. Run a
  diagnostic or choose a new relation with evidence.
- Stop early if 3 consecutive optimization iterations are correctness-passing
  but classified as no-signal, wrong-relation, logical-only, latency-shift, or
  regression, unless a new diagnostic has changed the boundary.

Allowed edit surface:
The selected bounded task determines the allowed runtime/policy edit surface.
By default, likely files include runtime policy code such as:

```text
/home/liuxu/projects/mllm-s6-long-horizon-state-relation/examples/qwen2_moe_td_qnn_aot/aot_run.cpp
/home/liuxu/projects/mllm-s6-long-horizon-state-relation/mllm/backends/opencl/moe/
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
- it repeats a prior failed patch class without new evidence
- it changes benchmark/correctness/parser semantics
- thermal or deployment conditions invalidate the comparison

Best-patch recheck:
Run p32/d32 only if a p16/d16 patch is accepted as a plausible best patch. Do
not run the evening verdict benchmark unless the user explicitly asks.

Final report:
Summarize:

- baseline metrics
- localization report and selected bounded task
- state-relation reports over time
- diagnostic plans and what ambiguity each resolved
- each patch gate and result classification
- every 3-iteration reflection
- whether longer horizon found a useful patch or mainly produced more rejected
  attempts
- whether longer horizon improved localization precision
- whether the dominant blocker appears to be iteration budget, diagnostics,
  expert knowledge, active-path localization, or a real system tradeoff
