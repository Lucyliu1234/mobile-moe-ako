Use $mobile-moe-ako.

You are running S6 Verify: MobileMoE-AKO with an integrated profiling/diagnostic AKO loop.

Target runtime repo:
/home/liuxu/projects/mllm

Harness package:
/home/liuxu/projects/mobile-moe-ako

Branch:
exp/s6-integrated-diagnostic-rerun-verify


Iteration log isolation:
Before running the baseline or editing source code, preserve the existing MobileMoE-AKO iteration log by copying:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS.md

to a uniquely named backup file, for example:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS_BEFORE_s6_verify_<timestamp>.md

Then continue appending this experiment's entries to /home/liuxu/projects/mobile-moe-ako/ITERATIONS.md.
Do not delete or overwrite old iteration logs.

Goal:
Improve decode_tok_s on the fixed benchmark while preserving correctness and not worsening normalized transfer volume.

Stage definition:
This is not a separate manual profiling stage. It is a normal AKO loop where each iteration can be either:
1. optimization iteration: changes runtime policy and may be selected as best patch
2. diagnostic iteration: adds or exposes lightweight counters to improve bottleneck visibility and is not eligible as best patch

The purpose is to make MobileMoE-AKO behave like AKO4ALL's profile -> optimize loop, but adapted to whole-system mobile inference where ncu is not available. Use runtime counters, Android logs, summary.jsonl, and lightweight instrumentation as the profiling substitute.

Core target:
Required-miss service and runtime data movement for GPU-v3 expert payloads, especially:
- required miss service latency
- mmap/page-touch behavior
- OpenCL/materializer enqueue and finish behavior
- transfer volume
- cache hit/miss and eviction churn

Allowed concepts:
- required miss service latency
- mmap page faults and page residency
- madvise(WILLNEED) as advisory readahead, not a residency guarantee
- CPU page-touch behavior
- OpenCL host-to-device upload
- clEnqueueWriteBuffer enqueue/finish timing
- transfer scheduling and overlap
- expert/core residency and eviction churn
- diagnostic instrumentation when existing counters are insufficient

You may read:
- /home/liuxu/projects/mobile-moe-ako/SKILL.md
- references/constraints.md
- references/benchmark_instructions.md
- references/metrics_schema.md
- references/expert_hints/diagnostic_instrumentation.md
- references/expert_hints/coremoe_required_core.md if needed

Do not read or reuse as direct patch guidance:
- iterations/s1_*
- iterations/s2_*
- iterations/s3_*
- iterations/s4_*
- iterations/s5_*
- patches/failed_attempts/s1_*
- patches/failed_attempts/s2_*
- patches/failed_attempts/s3_*
- patches/failed_attempts/s4_*
- patches/failed_attempts/s5_*

Previous-stage high-level lesson allowed:
Prior attempts showed that small page-touch, madvise, and enqueue changes may move latency between page_touch, enqueue, and finish without improving total required-miss service. Therefore, do not count a subcounter improvement as a win unless decode_tok_s or total required-miss service improves.

Before editing:
1. Create or switch to branch exp/s6-integrated-diagnostic-rerun-verify from clean main.
2. Verify /home/liuxu/projects/mllm is clean or explicitly report existing changes.
3. Do not merge, cherry-pick, or reuse S1-S5 patches.
4. Identify the build and deploy path for the phone-side runner.
5. Run a baseline using the exact benchmark contract below.
6. Produce a MobileMoE profiling report from the baseline before the first edit.


Base and baseline provenance rule:
Use da9fa3534a16c0f34adb6709e2ba871741cbf8cc as the clean pre-success base.
Before running the baseline benchmark, do not reuse any existing phone-side runner.
The baseline is valid only if it is built and deployed from da9fa3534a16c0f34adb6709e2ba871741cbf8cc in this verify experiment.

Before the baseline run, you must:
1. Check out da9fa3534a16c0f34adb6709e2ba871741cbf8cc on branch exp/s6-integrated-diagnostic-rerun-verify.
2. Build the Android runner from that exact source.
3. Record the host-side runner md5sum.
4. Push the runner to the phone-side benchmark directory used by the Tucker runner.
5. Record the phone-side runner md5sum and stat.
6. Confirm the host and phone md5 values match.
7. Only then run s6_verify_baseline_fasttemp_p16_d16.

The baseline is invalid if it only cites a git commit or branch without rebuilding, redeploying, and verifying the phone-side runner.
Every optimization iteration must repeat build, deploy, host md5, phone md5, and phone stat verification before benchmarking.

Benchmark contract:
Use the fixed temperature-gated Tucker end-to-end runner. Do not modify the runner, dataset, prompts, correctness checks, generated-token accounting, metric parser semantics, model artifacts, or benchmark contract.

For baseline and smoke iterations, use this exact command shape:

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

Use these iteration IDs:
- s6_verify_baseline_fasttemp_p16_d16
- s6_verify_iter_01_fasttemp_p16_d16
- s6_verify_iter_02_fasttemp_p16_d16
- s6_verify_iter_03_fasttemp_p16_d16
- s6_verify_iter_04_fasttemp_p16_d16
- s6_verify_iter_05_fasttemp_p16_d16

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

Iteration rules:
Run up to 5 iterations total. Early-stop after 3 consecutive no-signal or hypothesis-mismatch optimization iterations unless a diagnostic iteration reveals a new justified direction.

For every iteration:
1. State iteration type: optimization or diagnostic.
2. State the observation gap or optimization hypothesis.
3. State expected diagnostic movement.
4. Make one coherent change only.
5. Rebuild, deploy, and verify phone-side artifact identity changed.
6. Run the same p16/d16 temperature-gated benchmark.
7. Immediately append /home/liuxu/projects/mobile-moe-ako/ITERATIONS.md with metrics and diagnosis.
8. Commit a useful correctness-passing optimization patch, or archive failed/no-signal/diagnostic patches under /home/liuxu/projects/mobile-moe-ako/patches/failed_attempts/.
9. Revert only your own failed edits before the next iteration.
10. Do not start the next hypothesis before closing the current iteration.

Optimization iteration rules:
- May change runtime policy.
- Must preserve correctness and benchmark contract.
- Must improve decode_tok_s or reduce total required-miss service without worsening mib_per_token.
- Do not count latency shifting among page_touch, enqueue, and finish as a win.

Diagnostic iteration rules:
- May add lightweight counters or expose existing counters.
- Must not change benchmark semantics, model work, prompt set, generated-token accounting, correctness checks, or metric parser semantics.
- Must be logged as diagnostic-only.
- Is not eligible as best patch.
- Should answer one concrete observation gap, for example:
  - separating madvise time from CPU touch-loop time
  - separating page-touch cost from OpenCL enqueue/finish cost
  - exposing per-layer required-miss service
  - exposing per-projection gate/up/down required-miss service
  - measuring per-write count or upload granularity

Build/deploy rule:
Use the existing Android runner build target. Before the first source edit, report the exact build and deploy commands.

Expected build command:
cmake --build /home/liuxu/projects/mllm/build-android-arm64-v8a-qnn --target mllm-qwen2-moe-td-qnn-aot-runner

or equivalent:
ninja -C /home/liuxu/projects/mllm/build-android-arm64-v8a-qnn mllm-qwen2-moe-td-qnn-aot-runner

Expected deploy path:
/data/local/tmp/qwen2_moe_td_w8a16_clean_20260527/mllm-qwen2-moe-td-qnn-aot-runner

After every source edit:
- rebuild
- adb push the runner
- chmod +x if needed
- verify phone md5/timestamp changed
- only then benchmark

Failure handling:
Archive and diagnose:
- compile failure
- deploy verification failure
- correctness failure
- generated-token mismatch
- decode_tok_s regression
- no metric movement
- latency shifting without total service improvement
- hypothesis/metric mismatch
- diagnostic counter did not appear
- forbidden-surface edit

Best patch selection:
At the end, select the best correctness-passing optimization patch based on:
- decode_tok_s improvement over baseline
- no unacceptable mib_per_token regression
- reduced total required-miss service or clear diagnostic-consistent improvement
- small and interpretable code change

Do not select diagnostic-only patches as best patches.

If a best optimization patch exists, recheck it with the daytime signal contract:

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
  --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_verify_best_recheck_fasttemp_p32_d32

Do not run the evening verdict benchmark unless explicitly asked.

Reporting:
At the end, summarize:
- baseline metrics
- MobileMoE profiling report
- each iteration type, hypothesis/gap, and changed files
- build/deploy verification
- each iteration metrics
- failed patches and why they failed
- diagnostic findings, if any
- best optimization patch or no-useful-patch conclusion
- whether integrated diagnostic iteration improved the AKO workflow
- what remaining instrumentation or expert knowledge is needed
