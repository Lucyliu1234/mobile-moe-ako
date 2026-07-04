Use $mobile-moe-ako.

You are running:
S6-Causal-Control-Surface-Gate MobileMoE-AKO.

This is a controllability experiment for agentic systems optimization.
The purpose is not to provide more task-specific answer knowledge. The purpose is to test whether a general causal hypothesis gate can make the AKO loop more controllable, reduce false positives, and reduce control-surface drift.

Research question:
When optimizing a whole-system mobile MoE runtime, does requiring an explicit causal control-surface hypothesis before every patch make the coding agent more reliable than a normal expert-description prompt?

Target runtime repo:
/home/liuxu/projects/mllm

Harness package:
/home/liuxu/projects/mobile-moe-ako

Branch:
exp/s6-causal-control-surface-gate

Base:
Use da9fa3534a16c0f34adb6709e2ba871741cbf8cc as the clean pre-success base.
Do not start from prior best, prior followup, or any commit that already contains a known prior fix.

Iteration log isolation:
Before running the baseline or editing source code, preserve the existing MobileMoE-AKO iteration log by copying:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS.md

to a uniquely named backup file, for example:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS_BEFORE_s6_causal_gate_<timestamp>.md

Then continue appending this experiment's entries to /home/liuxu/projects/mobile-moe-ako/ITERATIONS.md.
Do not delete or overwrite old iteration logs.

Goal:
Improve decode_tok_s on the fixed benchmark while preserving correctness and not worsening normalized transfer volume.

Secondary goal:
Evaluate whether the causal gate improves controllability:

- better localization of the bottleneck and code path
- fewer false-positive patches
- less drift into unrelated control surfaces
- clearer failure diagnosis when no useful patch is found

General causal gate:
Before every source edit, answer this gate explicitly in the iteration notes. Do not edit source code until the gate is answered.

Patch hypothesis gate:

1. What system bottleneck does this patch target?
2. What runtime state, policy decision, or resource path will this patch change?
3. Where is that state, decision, or path read or executed in code?
4. Why is this on the critical path for the fixed benchmark?
5. What primary metric should improve?
6. What secondary diagnostics should move consistently with the hypothesis?
7. What guardrail metrics must not regress?
8. What result would falsify the hypothesis?
9. What kind of false positive could this patch create?
10. If the expected diagnostic movement does not appear, will this patch be rejected?

Hard rules:

- Do not edit until the gate is answered.
- Every patch must name a causal path from code change to metric movement.
- Do not accept a patch based only on the primary metric if diagnostics contradict it.
- Do not accept a patch based only on a local diagnostic if the end-to-end metric and guardrails do not support it.
- If the expected diagnostic movement does not appear, reject or archive the patch before trying another hypothesis.
- A patch that changes metrics by less than normal smoke noise should not be treated as a useful speedup unless diagnostics strongly support the hypothesis.
- Do not stack unrelated ideas in one iteration.

MobileMoE instantiation of the causal gate:

For this MobileMoE task, likely system bottlenecks and diagnostics include:

- dynamic transfer volume
- cache hit/miss/eviction behavior
- required-miss service time
- page-touch, enqueue, finish, and materialization-write decomposition
- scheduling or prewarm contention
- thermal state

For this task, typical false positives include:

- logical hit/miss counters improve but normalized transfer volume does not decrease
- page-touch time decreases but enqueue or finish time increases by a similar amount
- a small decode_tok_s gain appears without consistent diagnostics
- speculative work decreases but required work does not improve
- local cache behavior improves while end-to-end service time worsens
- benchmark or parser behavior changes rather than runtime behavior

Treat these as examples, not as fixed answers. Use code inspection and benchmark diagnostics to determine the actual bottleneck for this run.

Allowed concepts:
You may use general systems optimization concepts:

- runtime state
- policy decision
- critical path
- resource path
- cache behavior
- transfer volume
- scheduling contention
- diagnostic consistency
- guardrail metrics
- false positive
- falsifiable hypothesis

Allowed MobileMoE concepts:

- batch-1 mobile MoE decode
- selected experts can vary by layer/token
- limited device-side cache capacity
- dynamic expert/core transfer can affect end-to-end throughput
- cache hit/miss/eviction counters are useful but not sufficient by themselves
- normalized transfer volume and required-miss service time are important guardrails
- prewarm and scheduling can help or hurt depending on whether they reduce critical-path service or add contention

Do not use answer-level prior mechanisms:
Do not use these as initial hypotheses, terms, or solution descriptions before independently deriving them from this experiment's own code inspection and diagnostics:

- sibling residency
- packed payload sibling marking
- projection sibling bookkeeping
- marking gate/up/down projections resident together
- the concrete claim that one packed payload upload already contains a particular set of projection payloads
- any prior successful S6 patch description
- any prior S6 final report, prior S6 commit diff, or prior conversation content about the successful mechanism

Do not read or reuse as direct patch guidance:

- branch exp/s6-integrated-diagnostic-codex-mobile-moe-ako
- commit 902e8d9c
- branch exp/s6-followup-codex-mobile-moe-ako
- commit 2a23c3f0
- branch exp/s6-integrated-diagnostic-rerun-verify
- branch exp/s6-integrated-diagnostic-rerun-verify2
- commit 382f732d
- branch exp/s6-detailed-expert-mechanism
- commit 1f9a9be6
- iterations/s6_*
- results/runs/s6_*
- patches/failed_attempts/s6_*
- previous S6 summaries or reports

If broad git status or directory listings reveal those names, ignore them and do not open their contents.

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
- references/prompts/s6_diagnostic_driven_verify.md
- references/prompts/s6_diagnostic_driven_verify2.md
- references/prompts/s6_detailed_expert_mechanism.md
- references/prompts/s6_ablation_*.md
- references/experiment_protocol.md unless needed only for log-format conventions

Baseline provenance rule:
Before running the baseline benchmark, do not reuse any existing phone-side runner.
The baseline is valid only if it is built and deployed from da9fa3534a16c0f34adb6709e2ba871741cbf8cc in this experiment.

Before the baseline run, you must:

1. Check out da9fa3534a16c0f34adb6709e2ba871741cbf8cc on branch exp/s6-causal-control-surface-gate.
2. Build the Android runner from that exact source.
3. Record the host-side runner md5sum.
4. Push the runner to the phone-side benchmark directory used by the Tucker runner.
5. Record the phone-side runner md5sum and stat.
6. Confirm the host and phone md5 values match.
7. Only then run s6_causal_gate_baseline_fasttemp_p16_d16.

The baseline is invalid if it only cites a git commit or branch without rebuilding, redeploying, and verifying the phone-side runner.
Every optimization iteration must repeat build, deploy, host md5, phone md5, and phone stat verification before benchmarking.

Benchmark contract:
Use the Tucker Qwen2 TD end-to-end runner as the fixed benchmark harness.
Baseline and optimized versions must use the same host-side runner path and the same thermal gate.
Do not use a non-temperature-controlled benchmark for performance comparison.
Do not modify the Tucker runner, dataset, prompts, correctness checks, generated-token accounting, metric parser semantics, model artifacts, or benchmark contract.

p16/d16 temperature-gated smoke contract:

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

- s6_causal_gate_baseline_fasttemp_p16_d16
- s6_causal_gate_diag_01_fasttemp_p16_d16
- s6_causal_gate_iter_01_fasttemp_p16_d16
- s6_causal_gate_iter_02_fasttemp_p16_d16
- s6_causal_gate_iter_03_fasttemp_p16_d16
- s6_causal_gate_iter_04_fasttemp_p16_d16
- s6_causal_gate_iter_05_fasttemp_p16_d16

Only replace <iteration_id> with the current ID.
Do not change the runner, serial, temperature gate, context length, gpu cache capacity, dataset, decode tokens, repeats, or correctness behavior within this p16/d16 contract.

Expected build command:

cmake --build /home/liuxu/projects/mllm/build-android-arm64-v8a-qnn --target mllm-qwen2-moe-td-qnn-aot-runner

Expected deploy path:

/data/local/tmp/qwen2_moe_td_w8a16_clean_20260527/mllm-qwen2-moe-td-qnn-aot-runner

Before editing source code:

1. Confirm the runtime repo is on branch exp/s6-causal-control-surface-gate and clean.
2. Confirm the base is da9fa3534a16c0f34adb6709e2ba871741cbf8cc.
3. Build, deploy, and md5-verify the baseline runner from that base.
4. Run baseline s6_causal_gate_baseline_fasttemp_p16_d16 using the exact p16/d16 contract.
5. Produce a baseline profiling report using available metrics.
6. Choose the first source edit only after answering the causal gate.

Baseline profiling report:
After baseline, record:

- decode_tok_s
- mib_per_token
- required_miss_count
- required_miss_wait_ms_per_token
- decode_req_page_touch_ms
- decode_req_mat_enqueue_ms
- decode_req_mat_finish_ms
- decode_req_service_ms
- decode_req_mat_writes
- decode_req_page_touch_mib
- decode_core_upload_mib
- decode_req_miss
- decode_req_hit
- decode_evict
- cache_hit_rate
- eviction_churn
- peak_temp_skin_c_decode
- missing diagnostics
- whether existing counters are enough to choose an optimization iteration, or whether a diagnostic iteration is required first

Allowed diagnostic-only iteration:
If existing metrics cannot distinguish competing causal hypotheses, you may add one minimal diagnostic-only counter set.

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
2. Answer the causal gate before editing.
3. Make one coherent runtime-policy change only.
4. Do not combine unrelated mechanisms in one iteration.
5. Build and deploy the changed runtime to the phone-side setup used by the benchmark.
6. Verify deployment before benchmarking by reporting host md5, phone md5, and phone stat.
7. Do not edit benchmark inputs, prompts, generated-token accounting, correctness checks, metric parser semantics, Tucker runner files, model artifacts, or the benchmark contract.
8. Run the same p16/d16 temperature-gated benchmark contract.
9. Immediately append /home/liuxu/projects/mobile-moe-ako/ITERATIONS.md with metrics, the causal gate answers, and diagnosis.
10. Commit a useful correctness-passing change, or archive the failed/no-signal patch under /home/liuxu/projects/mobile-moe-ako/patches/failed_attempts/ before starting the next hypothesis.
11. Revert only your own failed edits before the next iteration.

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
- local diagnostic improvement contradicted by end-to-end metrics
- primary metric improvement contradicted by guardrails or diagnostics
- diagnostic-only instrumentation that perturbs timing too much

Best patch selection:
After smoke iterations, select the best correctness-passing patch based on:

- decode_tok_s improvement over this experiment's baseline
- no unacceptable MiB/token regression
- diagnostic movement consistent with the causal gate
- no evidence that the result is only a false positive
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
  --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_causal_gate_best_recheck_fasttemp_p32_d32

Do not run the evening verdict benchmark unless explicitly asked.

Reporting:
At the end, summarize both optimization result and controllability result:

- baseline provenance and md5/stat verification
- baseline metrics and profiling report
- each iteration's causal gate answers
- each iteration's changed files and build/deploy verification
- each iteration's metrics
- failed patches and why they failed
- whether the causal gate reduced false positives
- whether the causal gate reduced control-surface drift
- whether any patch was accepted despite contradictory diagnostics
- best optimization patch or no-useful-patch conclusion
- what this run suggests about prompt-level control versus tool/harness-level control for agentic systems optimization
