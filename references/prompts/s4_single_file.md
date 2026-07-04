Use $mobile-moe-ako.

You are running S4: Single-Mechanism Local Optimization for MobileMoE-AKO.

Target runtime repo:
/home/liuxu/projects/mllm

Harness package:
/home/liuxu/projects/mobile-moe-ako

Branch:
exp/s4-required-miss-service-codex-mobile-moe-ako

The S4 branch has already been created from clean main and checked out:
/home/liuxu/projects/mllm
branch: exp/s4-required-miss-service-codex-mobile-moe-ako
worktree should start clean

Goal:
Improve decode_tok_s on the fixed benchmark while preserving correctness and not worsening normalized transfer volume.

Stage definition:
S4 differs from S3 by fixing the core mechanism. Do not spend time searching for broad optimization directions. Your task is to optimize one local mechanism:

Core mechanism:
Required-miss service path in:
examples/qwen2_moe_td_qnn_aot/aot_run.cpp

Focus:
mmap page-touch plus OpenCL upload interaction for GPU-v3 expert payloads.

Mechanism context:
During decode, some required expert payloads are missing from the GPU shadow cache. The runtime must service those required misses by accessing expert payload bytes from mmap/external storage and uploading them to GPU/OpenCL buffers. This required-miss service path is on the decode critical path.

The relevant latency may appear across several counters:
- decode_hybrid_req_page_touch_ms
- decode_hybrid_req_mat_enqueue_ms
- decode_hybrid_req_mat_finish_ms
- decode_hybrid_req_service_ms
- required_miss_wait_ms_per_token
- decode_tok_s

Important mechanism invariant:
Do not count a patch as useful if it only moves latency from page_touch_ms into enqueue/finish/service time. A useful patch must improve end-to-end decode_tok_s or reduce total required-miss service latency while preserving correctness and not increasing mib_per_token.

Allowed S4 concepts:
- required miss service latency
- mmap page faults and page residency
- CPU page-touch / MADV_WILLNEED behavior
- OpenCL host-to-device upload
- clEnqueueWriteBuffer / enqueue / finish timing
- transfer scheduling and overlap
- lightweight instrumentation if it does not change benchmark semantics

Primary edit target:
- examples/qwen2_moe_td_qnn_aot/aot_run.cpp

Allowed tightly coupled context files, read mostly:
- mllm/backends/opencl/moe/HybridOpenCLMaterializer.cpp
- mllm/backends/opencl/moe/HybridOpenCLMaterializer.hpp
- mllm/backends/opencl/moe/HybridExternalStorage.cpp
- mllm/backends/opencl/moe/HybridExternalStorage.hpp

Do not broaden the optimization to:
- cache capacity changes
- changing --gpu-cache-capacity semantics
- prewarm policy redesign
- resident-recent or victim-ordering policy
- QNN decode loop redesign
- benchmark scripts
- dataset, prompt, decode length, correctness checks, metric parser, generated-token accounting, or model artifacts

Do not read or use:
- iterations/s1_*
- iterations/s2_*
- iterations/s3_*
- patches/failed_attempts/s1_*
- patches/failed_attempts/s2_*
- patches/failed_attempts/s3_*
- previous S1/S2/S3 failed patches as patch-level guidance

You may use this S4-level mechanism knowledge:
- Explicit CPU page touching may front-load mmap page faults before OpenCL upload.
- Removing page-touch may reduce page_touch_ms while shifting the same cost into OpenCL enqueue/finish.
- Therefore, evaluate total required-miss service latency and decode_tok_s, not page_touch_ms alone.
- Keep payload bytes, required work, generated-token accounting, and correctness unchanged.
- Prefer small changes to ordering, granularity, timing, or instrumentation within the required-miss service path.

You may read:
- /home/liuxu/projects/mobile-moe-ako/SKILL.md
- references/constraints.md
- references/benchmark_instructions.md
- references/metrics_schema.md
- references/prompts/s4_single_file.md if present
- references/expert_hints/coremoe_required_core.md if you need stage-allowed expert context

Before editing:
1. Confirm /home/liuxu/projects/mllm is on branch exp/s4-required-miss-service-codex-mobile-moe-ako.
2. Verify the runtime repo is clean or explicitly report existing changes.
3. Do not merge, cherry-pick, or reuse S1/S2/S3 patches.
4. Inspect the required-miss service call path in aot_run.cpp.
5. Identify the exact edit region before changing code.
6. State the mechanism invariant and the expected diagnostic movement.

Benchmark contract:
Use the fixed temperature-gated Tucker end-to-end runner. Do not modify the runner, dataset, prompts, correctness checks, generated-token accounting, metric parser semantics, model artifacts, or benchmark contract.

For S4 baseline and smoke iterations, use this exact command shape:

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
- s4_codex_baseline_fasttemp_p16_d16
- s4_codex_iter_01_fasttemp_p16_d16
- s4_codex_iter_02_fasttemp_p16_d16
- s4_codex_iter_03_fasttemp_p16_d16
- s4_codex_iter_04_fasttemp_p16_d16
- s4_codex_iter_05_fasttemp_p16_d16

Before the first source edit:
1. Run S4 baseline s4_codex_baseline_fasttemp_p16_d16 using the exact benchmark contract above.
2. Analyze the S4 baseline diagnostic decomposition. Record:
   - decode_tok_s
   - mib_per_token
   - required_miss_count
   - required_miss_wait_ms_per_token
   - decode_hybrid_req_page_touch_ms
   - decode_hybrid_req_mat_enqueue_ms
   - decode_hybrid_req_mat_finish_ms
   - decode_hybrid_req_service_ms
   - cache_hit_rate
   - eviction_churn
   - thermal state
   - missing diagnostics
   - suspected dominant subcomponent within the required-miss service path

Build/deploy rule:
Before the first source edit, explicitly identify the build and deploy command that updates the phone-side runtime binary/artifacts used by the Tucker runner. After every source edit, rebuild and deploy. Verify deployment by reporting a changed phone-side checksum, timestamp, or equivalent artifact identity. If you cannot verify that the optimized binary is actually running on the phone, stop and report a blocker.

Iteration rules:
Run up to 5 S4 smoke iterations, but early-stop after 3 consecutive no-signal or hypothesis-mismatch iterations.

For each iteration:
1. Stay within the required-miss service mechanism unless a tightly coupled helper is proven necessary.
2. Form one concrete hypothesis from S4 baseline or previous S4 diagnostics.
3. Name the targeted subcomponent and expected diagnostic movement.
4. Make one coherent local mechanism change only.
5. Do not combine unrelated mechanisms in one iteration.
6. Rebuild, deploy, and verify the phone-side artifact changed.
7. Run the same p16/d16 temperature-gated benchmark.
8. Immediately append /home/liuxu/projects/mobile-moe-ako/ITERATIONS.md with metrics and diagnosis.
9. Commit a useful correctness-passing change, or archive the failed/no-signal patch under /home/liuxu/projects/mobile-moe-ako/patches/failed_attempts/ before starting the next hypothesis.
10. Revert only your own failed edits before the next iteration.

Instrumentation:
One instrumentation-only iteration is allowed if the existing counters are insufficient. Instrumentation must be lightweight, must not change benchmark semantics, and must be archived or committed only with a clear reason. If instrumentation affects timing materially, mark the result as diagnostic-only, not an optimization win.

Failure handling:
Archive and diagnose:
- compile failure
- deploy verification failure
- correctness failure
- generated-token mismatch
- decode_tok_s regression
- no metric movement
- latency shifting from page_touch_ms to enqueue/finish/service without net improvement
- hypothesis/metric mismatch
- forbidden-surface edit

Best patch selection:
After the S4 smoke iterations, select the best correctness-passing patch based on:
- decode_tok_s improvement over S4 baseline
- no unacceptable mib_per_token regression
- reduced total required-miss service latency, not just moved latency
- diagnostics consistent with the hypothesis
- small and interpretable code change

Then recheck the best patch with the daytime signal contract:

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
  --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s4_codex_best_recheck_fasttemp_p32_d32

Do not run the evening verdict benchmark unless explicitly asked.

Reporting:
At the end, summarize:
- S4 baseline metrics
- required-miss service decomposition
- each iteration hypothesis and local edit region
- changed files
- build/deploy verification
- each iteration metrics
- failed patches and why they failed
- best patch or no-useful-patch conclusion
- whether mechanism-level expert guidance improved optimization compared with S3
- what remaining expert knowledge or instrumentation would be needed
