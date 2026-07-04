Use $mobile-moe-ako.

You are running:
S6-Detailed-Expert-Mechanism MobileMoE-AKO.

This is a controlled expert-context experiment for whole-system mobile MoE runtime optimization.

Research question:
Can a coding agent find a real transfer-reducing runtime repair when it is given a more detailed mechanism model of residency, cache state, and physical transfer, but is not given the known final patch or exact successful mechanism?

Target runtime repo:
/home/liuxu/projects/mllm

Harness package:
/home/liuxu/projects/mobile-moe-ako

Branch:
exp/s6-detailed-expert-mechanism

Base:
Use da9fa3534a16c0f34adb6709e2ba871741cbf8cc as the clean pre-success base.
Do not start from prior best, prior followup, or any commit that already contains a known prior fix.

Iteration log isolation:
Before running the baseline or editing source code, preserve the existing MobileMoE-AKO iteration log by copying:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS.md

to a uniquely named backup file, for example:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS_BEFORE_s6_detailed_expert_<timestamp>.md

Then continue appending this experiment's entries to /home/liuxu/projects/mobile-moe-ako/ITERATIONS.md.
Do not delete or overwrite old iteration logs.

Goal:
Improve decode_tok_s on the fixed benchmark while preserving correctness and not worsening normalized transfer volume.

What counts as a real win:
A patch is useful only if it improves decode_tok_s or materially reduces total required-miss service while preserving correctness and without increasing normalized transfer volume.

A patch is not useful if it only improves logical counters while physical transfer volume stays unchanged.
A patch is not useful if it only moves latency from page-touch to enqueue or finish.
A patch is not useful if it relies on changing the benchmark, parser, correctness checks, generated-token accounting, prompt set, model artifacts, or thermal contract.

Detailed expert context:

This system is a mobile MoE inference runtime with limited device-side cache capacity. During batch-1 decode, the selected experts vary by token/layer. The runtime must decide whether required expert/core data is already resident on the device or must be materialized and uploaded before compute can proceed.

Use the following expert concepts as system priors.

1. Logical residency versus physical residency

The runtime may maintain logical cache entries such as "expert X for projection/category Y is resident", while the actual device-side data may be stored in physical resources such as buffer slots, payload arenas, packed payloads, or materialized upload spans.

Logical residency is the runtime bookkeeping used by the policy.
Physical residency is whether the bytes needed by a later compute path are already present in device-accessible memory.

These two can diverge. A logical hit counter can improve without reducing physical bytes uploaded. Conversely, a physically reusable payload can still be uploaded repeatedly if the logical state consulted before materialization does not represent that reuse.

2. The upload-skip decision is the key control point

For this task, the important state is not merely any cache counter. The important state is the state checked before the runtime schedules materialization or host-to-device upload.

When inspecting code, locate the decision point where the runtime chooses between:

- hit path: reuse already-resident device-side data
- miss path: materialize data, touch/read host pages if needed, enqueue device upload, and update cache state

A useful repair should change the state that this decision reads, or change how that state is updated after a successful materialization, so that later accesses that can safely reuse physical data enter the hit path and skip real upload work.

3. Many logical runtime entries may share one physical payload or resource

Do not assume a one-to-one mapping between logical cache keys and physical device-side payloads. In optimized runtimes, one physical resource may serve more than one logical access path.

When reading code, explicitly identify:

- the logical key used by cache lookup
- the physical resource or slot that backs that logical key
- the lifetime or eviction rule for that physical resource
- whether more than one logical key can be backed by the same physical resource
- whether cache updates after materialization keep all relevant logical entries consistent with the physical resource lifetime

This is mechanism-level expert knowledge, not a patch instruction. You must derive the actual mapping from code and diagnostics in this experiment.

4. Eviction churn can indicate inconsistent or incomplete residency accounting

High miss and eviction counts under a fixed cache capacity can mean true capacity pressure. It can also mean that the runtime is failing to represent reuse correctly.

If every apparent miss also causes an eviction, inspect whether the cache is repeatedly cycling entries whose physical data could have been reused. A repair should reduce miss/evict churn only when it also reduces real upload volume or total required-miss service.

5. Required-miss service is an end-to-end path, not a single kernel

Required-miss service can include host-side page access, materialization bookkeeping, OpenCL or device upload enqueue, queue synchronization, and follow-up runtime state updates.

Do not optimize one subcounter in isolation. If page-touch drops but enqueue/finish rises and total service or decode_tok_s does not improve, treat it as latency shifting, not a win.

6. Existing diagnostics are validation signals, not the whole mechanism

Use diagnostics to test causal hypotheses:

- decode_tok_s
- correctness status and generated-token count
- normalized transfer volume / MiB per token
- decode_core_upload_mib
- required miss count and required miss wait/service time
- decode_req_miss, decode_req_hit, decode_evict
- cache_hit_rate and eviction churn
- page-touch, enqueue, finish, materialization write counts
- thermal state

Do not accept a patch based only on one improved counter. Prefer changes where multiple signals support the same causal story.

7. Diagnostic gaps to consider

If existing counters cannot distinguish logical-counter improvement from physical-transfer elimination, a diagnostic-only iteration may add lightweight counters to answer one of these questions:

- Which cache lookup decides hit versus miss for the currently hot path?
- Which runtime state is consulted before materialization or upload is scheduled?
- After materialization, which logical entries are marked resident?
- Which physical resource or upload span backs each logical entry?
- Which later accesses take the hit path because of that update?
- Did the number of physical upload spans or uploaded MiB decrease?

Diagnostic-only changes must preserve benchmark semantics and are not eligible as best speedup patches.

Forbidden known-answer leakage:
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
- references/prompts/s6_ablation_*.md
- references/experiment_protocol.md unless needed only for log-format conventions

Baseline provenance rule:
Before running the baseline benchmark, do not reuse any existing phone-side runner.
The baseline is valid only if it is built and deployed from da9fa3534a16c0f34adb6709e2ba871741cbf8cc in this experiment.

Before the baseline run, you must:

1. Check out da9fa3534a16c0f34adb6709e2ba871741cbf8cc on branch exp/s6-detailed-expert-mechanism.
2. Build the Android runner from that exact source.
3. Record the host-side runner md5sum.
4. Push the runner to the phone-side benchmark directory used by the Tucker runner.
5. Record the phone-side runner md5sum and stat.
6. Confirm the host and phone md5 values match.
7. Only then run s6_detailed_expert_baseline_fasttemp_p16_d16.

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

- s6_detailed_expert_baseline_fasttemp_p16_d16
- s6_detailed_expert_diag_01_fasttemp_p16_d16
- s6_detailed_expert_iter_01_fasttemp_p16_d16
- s6_detailed_expert_iter_02_fasttemp_p16_d16
- s6_detailed_expert_iter_03_fasttemp_p16_d16
- s6_detailed_expert_iter_04_fasttemp_p16_d16
- s6_detailed_expert_iter_05_fasttemp_p16_d16

Only replace <iteration_id> with the current ID.
Do not change the runner, serial, temperature gate, context length, gpu cache capacity, dataset, decode tokens, repeats, or correctness behavior within this p16/d16 contract.

Expected build command:

cmake --build /home/liuxu/projects/mllm/build-android-arm64-v8a-qnn --target mllm-qwen2-moe-td-qnn-aot-runner

Expected deploy path:

/data/local/tmp/qwen2_moe_td_w8a16_clean_20260527/mllm-qwen2-moe-td-qnn-aot-runner

Before editing source code:

1. Confirm the runtime repo is on branch exp/s6-detailed-expert-mechanism and clean.
2. Confirm the base is da9fa3534a16c0f34adb6709e2ba871741cbf8cc.
3. Build, deploy, and md5-verify the baseline runner from that base.
4. Run baseline s6_detailed_expert_baseline_fasttemp_p16_d16 using the exact p16/d16 contract.
5. Produce a baseline profiling report using the allowed profiling signals.
6. Write the first causal hypothesis before editing source code.

Causal hypothesis template:

Observed anomaly:
Verified runtime code path:
Logical cache key:
Physical resource or upload span:
State checked before materialization/upload:
State updated after materialization/upload:
Why the current state could cause repeated upload or service:
Expected metric movement:
Guardrails that must remain stable:

The hypothesis must come from this experiment's baseline, diagnostics, and verified runtime code paths.

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
- logical counter improvement without physical transfer or total service improvement
- diagnostic-only instrumentation that perturbs timing too much

Best patch selection:
After smoke iterations, select the best correctness-passing patch based on:

- decode_tok_s improvement over this experiment's baseline
- no unacceptable MiB/token regression
- reduction in decode_core_upload_mib, normalized transfer volume, or total required-miss service
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
  --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_detailed_expert_best_recheck_fasttemp_p32_d32

Do not run the evening verdict benchmark unless explicitly asked.

Reporting:
At the end, summarize:

- baseline provenance and md5/stat verification
- baseline metrics and profiling report
- each iteration type, hypothesis/gap, changed files, and build/deploy verification
- each iteration's metrics
- failed patches and why they failed
- diagnostic findings, if any
- whether any patch reduced physical transfer or only changed logical counters
- best optimization patch or no-useful-patch conclusion
- what this says about the amount and type of expert knowledge needed for agentic systems optimization
