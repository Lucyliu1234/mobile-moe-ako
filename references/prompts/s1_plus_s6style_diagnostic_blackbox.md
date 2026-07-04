Use $mobile-moe-ako.

You are running a controlled follow-up experiment:
Black-Box Diagnostic-Driven MobileMoE-AKO.

This experiment starts from basic task context and uses diagnostic feedback to guide runtime localization and optimization.

Research question:
Can a coding agent use fine-grained runtime diagnostics to independently localize a whole-system Mobile MoE runtime bottleneck, without being given the prior successful patch or solution explanation?

Target runtime repo:
/home/liuxu/projects/mllm

Harness package:
/home/liuxu/projects/mobile-moe-ako

Fixed host-side benchmark harness:
/home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py

Branch:
exp/blackbox-diagnostic-codex-mobile-moe-ako-rerun

Iteration log isolation:
Before running the baseline or editing source code, preserve the existing MobileMoE-AKO iteration log by copying:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS.md

to a uniquely named backup file, for example:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS_BEFORE_blackbox_diagnostic_rerun_<timestamp>.md

Then continue appending this experiment's entries to /home/liuxu/projects/mobile-moe-ako/ITERATIONS.md.
Do not delete or overwrite the old iteration log.

Base:
Start from the same clean pre-success baseline used for the staged MobileMoE-AKO experiments.
Do not start from prior best, prior followup, or any commit that already contains a known prior fix.
If the exact pre-success base commit is ambiguous, stop and ask the user before editing.

Goal:
Improve decode_tok_s on the fixed benchmark while preserving correctness and not worsening normalized transfer volume.

Important distinction:
- This is not a normal diagnostic-driven staged run.
- This is not a continuation of any previous staged run.
- Existing logs may exist in ITERATIONS.md, results/runs, and patches/failed_attempts.
- Do not use previous staged results as baseline, optimization guidance, or evidence for this run.
- Only use existing run names to avoid filename collisions.

Context policy:
Start from basic task context.

You may inspect:
- runtime source code
- build/deploy scripts
- benchmark outputs
- logs and generated metrics
- MobileMoE-AKO constraints, benchmark instructions, and metrics schema

You may add minimal diagnostic-only counters if existing diagnostics cannot distinguish hypotheses.

Do not use as optimization guidance:
- prior successful patch descriptions
- prior solution explanations
- prior best or prior followup commits
- committed diffs or failed patches from the prior successful stage
- prior staged run logs as patch-level guidance

Do not use these terms or equivalent known-answer explanations as an initial hypothesis:
- sibling residency
- packed payload sibling marking
- projection sibling bookkeeping
- sibling projection residency accounting

Anti-leak file policy:
Do not read or use prior solution explanations, prior successful patch descriptions, or prior successful diffs as guidance. Existing historical files may be used only to avoid filename collisions or to verify that this run is not overwriting prior results.
The previous blackbox_diag_* run directories and archived patches from the provenance-contaminated attempt are invalid for metric comparison. Do not use them as baseline, evidence, or optimization guidance.

You may read:
- /home/liuxu/projects/mobile-moe-ako/SKILL.md
- references/constraints.md
- references/benchmark_instructions.md
- references/metrics_schema.md
- this prompt file

Do not ask for key files.
Discover relevant code paths yourself from the baseline diagnostics and runtime repo inspection.

Search policy:
Prefer local code, benchmark outputs, logs, and diagnostics.
If external search is needed, keep it relevant to the active blocker or runtime question, and record what external knowledge was used. Do not use search to look up prior solutions to this project.

Benchmark contract:
Use the Tucker Qwen2 TD end-to-end runner as the fixed benchmark harness.
Baseline and optimized versions must use the same host-side runner and the same thermal gate.
Do not use a non-temperature-controlled benchmark for performance comparison.
Do not modify the Tucker runner, dataset, prompts, correctness checks, generated-token accounting, metric parser semantics, model artifacts, or benchmark contract.

Baseline provenance rule:
Before running the baseline benchmark, do not reuse any existing phone-side runner.
The baseline is valid only if it is built and deployed from the specified base source in this experiment.

Before the baseline run, you must:
1. Check out the specified base commit or branch in /home/liuxu/projects/mllm.
2. Build the Android runner from that exact source.
3. Record the host-side runner md5sum.
4. Push the runner to the phone-side benchmark directory used by the Tucker runner.
5. Record the phone-side runner md5sum and stat.
6. Confirm the host and phone md5 values match.
7. Only then run blackbox_diag_rerun_baseline_fasttemp_p16_d16.

The baseline is invalid if it only cites a git commit or branch without rebuilding, redeploying, and verifying the phone-side runner.
Every optimization iteration must repeat build, deploy, host md5, phone md5, and phone stat verification before benchmarking.

Black-box diagnostic-driven p16/d16 temperature-gated smoke contract:

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

Use this exact p16/d16 contract for:
- blackbox_diag_rerun_baseline_fasttemp_p16_d16
- blackbox_diag_rerun_diag_01_fasttemp_p16_d16
- blackbox_diag_rerun_iter_01_fasttemp_p16_d16
- blackbox_diag_rerun_iter_02_fasttemp_p16_d16
- blackbox_diag_rerun_iter_03_fasttemp_p16_d16
- blackbox_diag_rerun_iter_04_fasttemp_p16_d16
- blackbox_diag_rerun_iter_05_fasttemp_p16_d16

Only replace <iteration_id> with the current ID.
Do not change the runner, serial, temperature gate, context length, gpu cache capacity, dataset, decode tokens, repeats, or correctness behavior within this p16/d16 contract.

Hard limits:
- Run this black-box diagnostic-driven experiment only.
- Verify /home/liuxu/projects/mllm is on branch exp/blackbox-diagnostic-codex-mobile-moe-ako-rerun and clean before editing. If dirty, stop and ask the user.
- Run at most 1 temperature-gated p16/d16 baseline.
- Run at most 1 diagnostic-only iteration before the first optimization attempt, only if existing metrics are insufficient.
- Run up to 5 temperature-gated p16/d16 optimization iterations.
- Stop early after 3 consecutive compile failures, correctness failures, no-signal regressions, hypothesis-mismatch iterations, or repeated blockers.
- Run at most 1 temperature-gated p32/d32 recheck for the best correctness-passing patch.
- Total benchmark runs must not exceed 8.
- Do not run the 4mix p32/d64 evening verdict benchmark unless explicitly asked.
- If the same blocker repeats for 30 minutes or 3 failed attempts, stop and write the blocker to ITERATIONS.md.

Before editing source code:
1. Confirm the runtime repo is on the requested branch and clean.
2. Confirm the base does not already contain the known prior fix. Do not inspect the prior successful mechanism to do this; use branch/commit ancestry or ask the user if ambiguous.
3. Build, deploy, and md5-verify the baseline runner from the specified base source, then run baseline blackbox_diag_rerun_baseline_fasttemp_p16_d16 using the exact p16/d16 contract above.
4. Analyze the baseline as black-box system feedback, but use the stronger diagnostic workflow below.

Diagnostic-driven workflow:
Before each code-changing iteration, write a short causal chain:

Observed anomaly:
Verified runtime code path:
Suspected wasteful behavior:
Expected metric movement:
Guardrails that must remain stable:

Use available diagnostics such as:
- decode_tok_s
- normalized transfer volume / mib_per_token
- cache hit, miss, eviction, and churn counters
- parameter-miss or required-miss handling cost
- upload/page-touch/enqueue/finish timing
- correctness status
- generated token count
- thermal state

The hypothesis must come from observed diagnostics and verified code paths, not from prior solution text.

Allowed diagnostic-only iteration:
If existing metrics cannot distinguish competing hypotheses, you may add one minimal diagnostic-only counter set.
Diagnostic-only changes must:
- preserve benchmark semantics
- preserve generated-token accounting
- preserve model work
- preserve correctness checks
- preserve parser semantics
- be labeled diagnostic-only in ITERATIONS.md
- not be treated as a speedup patch

Iteration rules:
For each optimization iteration:
1. Inspect the repo yourself.
2. Form one concrete hypothesis from this experiment's baseline or previous iteration feedback only.
3. Name the targeted bottleneck and expected diagnostic movement.
4. Make one coherent runtime-policy change only.
5. Do not combine unrelated mechanisms in one iteration.
6. Build and deploy the changed runtime to the phone-side setup used by the benchmark.
7. Verify deployment before benchmarking by reporting a changed phone-side checksum, timestamp, or equivalent artifact identity.
8. Do not edit benchmark inputs, prompts, generated-token accounting, correctness checks, metric parser semantics, Tucker runner files, model artifacts, or the benchmark contract.
9. Run the same p16/d16 temperature-gated benchmark contract.
10. Immediately append /home/liuxu/projects/mobile-moe-ako/ITERATIONS.md with metrics and diagnosis.
11. Commit a useful correctness-passing change, or archive the failed/no-signal patch under /home/liuxu/projects/mobile-moe-ako/patches/failed_attempts/ before starting the next hypothesis.
12. Revert only your own failed edits before the next iteration.

Failure handling:
Archive and diagnose:
- compile failure
- deployment failure
- deploy verification failure
- correctness failure
- generated-token mismatch
- decode_tok_s regression
- normalized transfer regression
- no metric movement
- wrong file localization
- forbidden-surface edit
- hypothesis/metric mismatch
- diagnostic-only instrumentation that perturbs timing too much

Best patch selection:
After smoke iterations, select the best correctness-passing patch based on:
- decode_tok_s improvement over this experiment's baseline
- no unacceptable mib_per_token regression
- diagnostics consistent with the stated hypothesis
- build/deploy was verified
- small and interpretable code change

Then recheck the best patch with the p32/d32 temperature-gated signal contract:

cd /home/liuxu/projects/mobile-moe-ako
/home/liuxu/projects/tucker/tucker_env/bin/python \
  /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py \
  --serial 10.29.230.131:5555 \
  --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p32.jsonl \
  --decode-tokens 32 \
  --repeats 1 \
  --idle-seconds 30 \
  --sleep-between-runs-s 0 \
  --cooldown-poll-s 30 \
  --cooldown-max-wait-s 600 \
  --max-start-skin-c 37 \
  --max-start-battery-c 34 \
  --context-len 384 \
  --gpu-cache-capacity 8 \
  --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/blackbox_diag_rerun_best_recheck_fasttemp_p32_d32

Do not run the evening verdict benchmark unless explicitly asked.

Reporting:
At the end, summarize:
- branch and final commit/patch state
- base commit
- baseline metrics
- baseline black-box diagnostic decomposition
- whether any diagnostic-only iteration was needed
- each iteration causal chain, hypothesis, and changed files
- whether build/deploy was verified for each iteration
- each iteration metrics
- failed patches and why they failed
- best patch or no-useful-patch conclusion
- p32/d32 recheck result if run
- whether diagnostics independently narrowed the problem toward transfer/cache/runtime-state bottlenecks
- what additional context or diagnostics still seemed missing
- whether the result is a speedup, no-speedup capability-boundary result, or diagnostic-only finding
