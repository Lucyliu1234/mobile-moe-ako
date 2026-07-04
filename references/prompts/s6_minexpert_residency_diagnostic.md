Use $mobile-moe-ako.

You are running a controlled post-hoc minimal-context ablation:
S6-MinExpert Residency Diagnostic MobileMoE-AKO.

Research question:
Is the expert/core residency and eviction-churn concept, combined with the diagnostic-driven MobileMoE-AKO workflow, sufficient for a coding agent to localize and repair a whole-system Mobile MoE runtime bottleneck?

This is a minimal expert-context ablation, not a continuation of any prior successful run.

Target runtime repo:
/home/liuxu/projects/mllm

Harness package:
/home/liuxu/projects/mobile-moe-ako

Branch:
exp/s6-minexpert-residency-diagnostic

Base:
Use da9fa3534a16c0f34adb6709e2ba871741cbf8cc as the clean pre-success base.
Do not start from prior best, prior followup, or any commit that already contains a known prior fix.

Iteration log isolation:
Before running the baseline or editing source code, preserve the existing MobileMoE-AKO iteration log by copying:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS.md

to a uniquely named backup file, for example:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS_BEFORE_s6_minexpert_<timestamp>.md

Then continue appending this experiment's entries to /home/liuxu/projects/mobile-moe-ako/ITERATIONS.md.
Do not delete or overwrite old iteration logs.

Goal:
Improve decode_tok_s on the fixed benchmark while preserving correctness and not worsening normalized transfer volume.

Allowed expert concept:
You may use this single expert concept as system-level prior:

- expert/core residency and eviction churn

Meaning:
The Mobile MoE runtime maintains which expert/core parameters are resident in the device-side cache. Because cache capacity is limited, entries may be evicted. High miss/evict churn can indicate repeated movement or inconsistent runtime cache state.

Do not use any other mechanism-level expert knowledge as an initial optimization prior.

Allowed profiling signals and workflow signals:
You may use existing benchmark counters and logs to observe and validate hypotheses, including:

- decode_tok_s
- correctness status and generated token count
- normalized transfer volume / MiB per token
- cache hit, miss, eviction, and churn counters
- required-miss service time
- page-touch, enqueue, finish, upload, and thermal counters as observations

These profiling signals are allowed for measurement and hypothesis validation. Do not treat page-touch, mmap, madvise, OpenCL enqueue/finish, or Qualcomm/QNN queue details as expert mechanisms unless the runtime code and this experiment's own diagnostics force that conclusion.

Forbidden expert concepts and known-answer leakage:
Do not use these as hypotheses, terms, or solution descriptions before independently deriving them from this experiment's own code inspection and diagnostics:

- sibling residency
- packed payload sibling marking
- projection sibling bookkeeping
- marking gate/up/down projections resident together
- the idea that one packed payload upload already contains multiple projection payloads
- any prior successful S6 patch description
- any prior S6 final report, S6 commit diff, or prior conversation content about the S6 successful mechanism

Do not read or reuse as direct patch guidance:

- branch exp/s6-integrated-diagnostic-codex-mobile-moe-ako
- commit 902e8d9c
- branch exp/s6-followup-codex-mobile-moe-ako
- commit 2a23c3f0
- iterations/s6_*
- results/runs/s6_*
- patches/failed_attempts/s6_*
- previous S6 summaries or reports

If broad git status or directory listing reveals those names, ignore them and do not open their contents.

You may read:

- /home/liuxu/projects/mobile-moe-ako/SKILL.md
- references/constraints.md
- references/benchmark_instructions.md
- references/metrics_schema.md
- this prompt file
- the target runtime repo /home/liuxu/projects/mllm

Do not read:

- references/expert_hints/coremoe_required_core.md
- references/expert_hints/diagnostic_instrumentation.md
- references/prompts/s5_expert_diagnostic.md
- references/prompts/s6_diagnostic_driven.md
- references/experiment_protocol.md unless needed only for log-format conventions

Baseline provenance rule:
Before running the baseline benchmark, do not reuse any existing phone-side runner.
The baseline is valid only if it is built and deployed from da9fa3534a16c0f34adb6709e2ba871741cbf8cc in this experiment.

Before the baseline run, you must:
1. Check out da9fa3534a16c0f34adb6709e2ba871741cbf8cc on branch exp/s6-minexpert-residency-diagnostic.
2. Build the Android runner from that exact source.
3. Record the host-side runner md5sum.
4. Push the runner to the phone-side benchmark directory used by the Tucker runner.
5. Record the phone-side runner md5sum and stat.
6. Confirm the host and phone md5 values match.
7. Only then run s6_minexpert_baseline_fasttemp_p16_d16.

The baseline is invalid if it only cites a git commit or branch without rebuilding, redeploying, and verifying the phone-side runner.
Every optimization iteration must repeat build, deploy, host md5, phone md5, and phone stat verification before benchmarking.

Benchmark contract:
Use the Tucker Qwen2 TD end-to-end runner as the fixed benchmark harness.
Baseline and optimized versions must use the same host-side runner and the same thermal gate.
Do not use a non-temperature-controlled benchmark for performance comparison.
Do not modify the Tucker runner, dataset, prompts, correctness checks, generated-token accounting, metric parser semantics, model artifacts, or benchmark contract.

MinExpert p16/d16 temperature-gated smoke contract:

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

- s6_minexpert_baseline_fasttemp_p16_d16
- s6_minexpert_diag_01_fasttemp_p16_d16
- s6_minexpert_iter_01_fasttemp_p16_d16
- s6_minexpert_iter_02_fasttemp_p16_d16
- s6_minexpert_iter_03_fasttemp_p16_d16
- s6_minexpert_iter_04_fasttemp_p16_d16
- s6_minexpert_iter_05_fasttemp_p16_d16

Only replace <iteration_id> with the current ID.
Do not change the runner, serial, temperature gate, context length, gpu cache capacity, dataset, decode tokens, repeats, or correctness behavior within this p16/d16 contract.

Before editing source code:
1. Confirm the runtime repo is on branch exp/s6-minexpert-residency-diagnostic and clean.
2. Confirm the base is da9fa3534a16c0f34adb6709e2ba871741cbf8cc.
3. Build, deploy, and md5-verify the baseline runner from that base.
4. Run baseline s6_minexpert_baseline_fasttemp_p16_d16 using the exact p16/d16 contract.
5. Produce a baseline profiling report using only allowed profiling signals.

Diagnostic-driven workflow:
Before each code-changing iteration, write a short causal chain:

Observed anomaly:
Verified runtime code path:
Residency/eviction hypothesis:
Expected metric movement:
Guardrails that must remain stable:

The hypothesis must come from this experiment's baseline or previous iteration diagnostics and verified runtime code paths.
Do not start from page-touch, madvise, OpenCL, or queue-level expert mechanisms.

Allowed diagnostic-only iteration:
If existing metrics cannot distinguish residency/cache-state hypotheses, you may add one minimal diagnostic-only counter set.
Diagnostic-only changes must:

- preserve benchmark semantics
- preserve generated-token accounting
- preserve model work
- preserve correctness checks
- preserve parser semantics
- be labeled diagnostic-only in ITERATIONS.md
- not be treated as a speedup patch

Iteration budget:

- Run at most 1 p16/d16 baseline.
- Run at most 1 diagnostic-only iteration before the first optimization attempt, only if existing metrics are insufficient.
- Run up to 5 p16/d16 optimization iterations.
- Stop early after 3 consecutive compile failures, correctness failures, no-signal regressions, hypothesis-mismatch iterations, or repeated blockers.
- Run at most 1 p32/d32 recheck for the best correctness-passing patch.
- Do not run the 4mix p32/d64 evening verdict benchmark unless explicitly asked.

Iteration rules:
For each optimization iteration:

1. Inspect the repo yourself.
2. Form one concrete hypothesis from this experiment's baseline or previous iteration feedback only.
3. Name the targeted residency/cache-state behavior and expected diagnostic movement.
4. Make one coherent runtime-policy change only.
5. Do not combine unrelated mechanisms in one iteration.
6. Build and deploy the changed runtime to the phone-side setup used by the benchmark.
7. Verify deployment before benchmarking by reporting host md5, phone md5, and phone stat.
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
- no unacceptable MiB/token regression
- diagnostics consistent with the stated residency/cache-state hypothesis
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
  --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_minexpert_best_recheck_fasttemp_p32_d32

Do not run the evening verdict benchmark unless explicitly asked.

Reporting:
At the end, summarize:

- branch and final commit/patch state
- base commit
- baseline provenance: host md5, phone md5, phone stat
- baseline metrics and profiling report
- whether any diagnostic-only iteration was needed
- each iteration causal chain, hypothesis, changed files, and build/deploy verification
- each iteration metrics
- failed patches and why they failed
- best patch or no-useful-patch conclusion
- p32/d32 recheck result if run
- whether the minimal residency/eviction expert concept was sufficient
- what additional expert knowledge or profiling seemed missing
