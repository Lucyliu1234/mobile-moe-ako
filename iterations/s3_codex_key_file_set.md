# MobileMoE-AKO Iterations

## Current Stage

S3: Key-File-Set Guided Whole-System Exploration.

This root `ITERATIONS.md` is the active S3 working log only.

Archived previous-stage logs:

- `iterations/s1_codex_blackbox.md`
- `iterations/s1_codex_blackbox_completed.md`
- `iterations/s2_codex_concept_guided.md`

S3 agents must not read `iterations/s1_*`, `iterations/s2_*`, `patches/failed_attempts/s1_*`, or `patches/failed_attempts/s2_*` as optimization guidance or evidence unless the user explicitly allows it. S3 may read the current stage prompt, fixed benchmark contract, durable constraints, metrics schema, stage-allowed expert concepts, and the S3 key-file map.

## Template

```text
Iteration ID:
Stage: S3-key-file-set
Agent prompt setting:
File-to-mechanism mapping:
Baseline bottleneck decomposition:
Targeted bottleneck:
Expected diagnostic movement:
Agent hypothesis:
Chosen optimization direction:
Selected key file or file group:
Files inspected:
Files modified:
Change summary:
Benchmark command:
Compile result:
Correctness result:
Metrics:
  decode_tok_s:
  mib_per_token:
  required_miss_count:
  upload_bytes:
  prewarm_hit_rate:
  eviction_churn:
  required_miss_wait_ms_per_token:
  cache_hit_rate:
  peak_temp_skin_c_decode:
Result:
Agent diagnosis:
My diagnosis:
Needed expert knowledge:
Patch / commit:
```


## s3_codex_baseline_fasttemp_p16_d16

Iteration ID: s3_codex_baseline_fasttemp_p16_d16
Stage: s3_codex
Agent prompt setting: S3 key-file-set guided; no S1/S2 optimization guidance used
Baseline bottleneck decomposition: decode_tok_s=0.3390; mib_per_token=1431.802; required_miss_count=14736; required_miss_wait_ms_per_token=1464.685; cache_hit_rate=0.3666; prewarm_hit_rate missing/null; eviction_churn=14064; thermal start skin/battery 30.68C/32.2C, peak decode skin 34.97C; decode req_page_touch_ms=18946.085 and req_mat_ms=23396.806 dominate.
Targeted bottleneck: Baseline only; suspected dominant bottleneck is required miss service latency, especially synchronous mmap page-touch before OpenCL expert-payload upload.
Expected diagnostic movement: Baseline record; first edit should reduce req_page_touch_ms and required_miss_wait_ms_per_token without increasing mib_per_token.
Agent hypothesis: S3 baseline shows repeated required misses and eviction churn; page-touch inside required miss path is large enough to dominate decode.
Chosen optimization direction: Map key files, localize bottleneck to aot_run.cpp required-miss GPU-v3 payload path.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; HybridOpenCLMaterializer.{cpp,hpp}; HybridOpenCLMaterializedResource.{cpp,hpp}; HybridPrefetchScheduler.{cpp,hpp}; HybridResourceManager.{cpp,hpp}; HybridExternalStorage.{cpp,hpp}; TokenGenerator.{cpp,hpp} read-mostly; fixed Tucker runner for deploy identity only
Files modified: none
Change summary: Baseline run only. Candidate map: aot_run.cpp=policy/page-touch/hot-resident/decode counters; materializer=OpenCL enqueue/finish/upload; materialized resource=buffer ownership/lifetime; scheduler=prewarm/pending/resident decisions; resource manager=resident bookkeeping/eviction; external storage=mmap backing/page access; TokenGenerator=QNN decode boundaries read-mostly.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s3_codex_baseline_fasttemp_p16_d16
Compile result: Baseline: repo clean; phone runner matched local md5 6d15f401a12e515d066141c3a02ba4ea before edit
Correctness result: PASS ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.3390215642717717
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1464.6849999999997
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 34.96644
Result: baseline recorded
Agent diagnosis: Dominant S3 bottleneck is required miss service, with page-touch plus materialization/upload on the critical path; transfer volume is high but fixed by required misses and cache pressure.
My diagnosis: File localization points to aot_run.cpp first because the expensive synchronous touchMmapPages calls occur in the runner's GPU-v3 interleaved required-miss path, above the generic OpenCL materializer.
Needed expert knowledge: Need S4-level knowledge on Android mmap fault behavior versus clEnqueueWriteBuffer from mapped host pages, and whether page-touch mode 2 is required for correctness/stability on this device.
Patch / commit: baseline/no patch

## s3_codex_iter_01_fasttemp_p16_d16

Iteration ID: s3_codex_iter_01_fasttemp_p16_d16
Stage: s3_codex
Agent prompt setting: S3 key-file-set guided; one coherent aot_run.cpp page-touch policy change
Baseline bottleneck decomposition: Baseline decode_tok_s=0.3390, required_miss_wait_ms_per_token=1464.685, mib_per_token=1431.802, req_page_touch_ms decode=18946.085, req_mat_enqueue_ms decode=4429.144, req_mat_finish_ms decode=14.799.
Targeted bottleneck: Required miss service latency from synchronous mmap page touching before required GPU-v3 expert-payload upload.
Expected diagnostic movement: req_page_touch_ms and required_miss_wait_ms_per_token should fall; mib_per_token, required_miss_count, cache_hit_rate unchanged; decode_tok_s should improve.
Agent hypothesis: Replacing the CPU page walk in interleaved page-touch mode with MADV_WILLNEED-only would preserve payload upload volume but reduce serial required-miss latency.
Chosen optimization direction: Required-miss page-touch scheduling in examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Files inspected: aot_run.cpp touchMmapPages, materializeCoreSlotBatchGpuV3, materializePackedExpertSlotBatchGpuV3; fixed runner qwen_env; baseline/iter summaries
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Added hintMmapPages() and used it instead of touchMmapPages() at the two interleaved required-miss payload upload sites.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s3_codex_iter_01_fasttemp_p16_d16
Compile result: PASS: cmake target rebuilt; deployed phone md5 changed 6d15f401a12e515d066141c3a02ba4ea -> 7ed43f31b6c3875da591fb8233897ca3
Correctness result: PASS ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.329963743583855
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1516.828125
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 35.95824
Result: Archived failed patch: correctness passed but decode_tok_s regressed to 0.32996 (speedup 0.973x) and required_miss_wait_ms_per_token worsened to 1516.83; mib_per_token unchanged.
Agent diagnosis: Hypothesis mismatch: page-touch accounting dropped from 18.95s to 0.67s in decode, but req_mat_enqueue/finish rose from 4.44s/0.015s to 17.36s/6.19s, so the same page-fault cost shifted into OpenCL upload and worsened throughput.
My diagnosis: File localization was correct but the policy was wrong for this device: explicit CPU page touching appears to front-load faults before clEnqueueWriteBuffer; removing the page walk does not remove I/O work and makes upload blocking worse.
Needed expert knowledge: Need S4 knowledge of Android mmap paging plus Qualcomm/OpenCL host copy behavior, specifically whether page touching is intentionally used to avoid driver-side faults during clEnqueueWriteBuffer.
Patch / commit: patches/failed_attempts/s3_codex_iter_01_fasttemp_p16_d16.patch

## s3_codex_iter_02_fasttemp_p16_d16

Iteration ID: s3_codex_iter_02_fasttemp_p16_d16
Stage: s3_codex
Agent prompt setting: S3 key-file-set guided; one coherent aot_run.cpp required-miss upload scheduling change
Baseline bottleneck decomposition: Baseline decode_tok_s=0.3390, required_miss_wait_ms_per_token=1464.685, mib_per_token=1431.802, decode req_mat_enqueue_ms=4429.144, req_mat_finish_ms=14.799, req_page_touch_ms=18946.085.
Targeted bottleneck: Required-miss OpenCL upload scheduling overhead while preserving explicit mmap page-touch.
Expected diagnostic movement: req_mat_enqueue_ms should fall with same page_touch, misses, cache_hit_rate, and mib_per_token; decode_tok_s should improve.
Agent hypothesis: Collecting page-touched spans into one uploadDeviceSpans call per required-miss chunk should reduce per-expert enqueue overhead without changing transfer volume.
Chosen optimization direction: Transfer scheduling / OpenCL enqueue batching in examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Files inspected: aot_run.cpp materializeCoreSlotBatchGpuV3, materializePackedExpertSlotBatchGpuV3; HybridOpenCLMaterializer uploadDeviceSpans/enqueueDeviceSpans; baseline and iter summaries
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: In core_page_touch_mode==2 paths, accumulate DeviceUploadSpan entries after CPU page-touch and call uploadDeviceSpans once per chunk instead of enqueueDeviceSpans once per expert then finish.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s3_codex_iter_02_fasttemp_p16_d16
Compile result: PASS: cmake target rebuilt; deployed phone md5 changed 6d15f401a12e515d066141c3a02ba4ea -> a6b04005fe2230e99f4c35b222ee3be6
Correctness result: PASS ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.3329209968070796
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1487.9285624999982
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 36.20752
Result: Archived failed patch: correctness passed but decode_tok_s regressed to 0.33292 (speedup 0.982x); mib_per_token unchanged; required_miss_wait_ms_per_token worsened to 1487.93.
Agent diagnosis: Partial diagnostic movement only: decode req_mat_enqueue_ms dropped to 3297ms, but req_page_touch_ms rose to 19648ms and req_mat_finish_ms rose to 817ms; no cache or transfer-volume movement.
My diagnosis: The file and call path were correct, but batching enqueue calls does not address the dominant work under fixed cache capacity; the apparent enqueue savings are absorbed by page-touch/finish variability and thermal-start differences.
Needed expert knowledge: Need S4 knowledge of actual OpenCL command queue behavior and whether interleaving touch/enqueue intentionally pipelines page faults with driver copies on this device.
Patch / commit: patches/failed_attempts/s3_codex_iter_02_fasttemp_p16_d16.patch

## s3_codex_iter_03_fasttemp_p16_d16

Iteration ID: s3_codex_iter_03_fasttemp_p16_d16
Stage: s3_codex
Agent prompt setting: S3 key-file-set guided; one coherent aot_run.cpp resident-recent cache eviction policy change
Baseline bottleneck decomposition: Baseline decode_tok_s=0.3390, required_miss_count=14736, eviction_churn=14064, cache_hit_rate=0.3666, mib_per_token=1431.802, required_miss_wait_ms_per_token=1464.685; decode-specific counters showed 6810 required misses and 6810 evictions.
Targeted bottleneck: Eviction churn and repeated required misses under fixed gpu_cache_capacity=8.
Expected diagnostic movement: required_miss_count and eviction_churn should fall, cache_hit_rate should rise, mib_per_token should fall or stay no worse, and decode_tok_s should improve beyond noise.
Agent hypothesis: Enabling recent-resident protection for demand cache victims should preserve recently used expert/core slots under fixed cache pressure, reducing required misses and eviction churn.
Chosen optimization direction: Dynamic expert/core residency and eviction churn in examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp selectCacheVictim/env/default wiring; mllm/backends/opencl/moe/GpuMoePrefetchPolicy.cpp isRecentResident/preferVictim
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Changed the compiled default MLLM_QNN_TD_HYBRID_GPU_RESIDENT_RECENT policy from false to true, leaving the env override intact.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s3_codex_iter_03_fasttemp_p16_d16
Compile result: PASS: cmake target rebuilt; deployed phone md5 changed stale iter02 a6b04005fe2230e99f4c35b222ee3be6 -> a6cf5cf03490c0bbc01b9b997b6ca341
Correctness result: PASS ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.34194209603837
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1462.1884375000009
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 36.34128
Result: Archived failed/no-signal patch: correctness passed and decode_tok_s rose only 0.86%, but required_miss_count, cache_hit_rate, eviction_churn, and mib_per_token were identical to baseline, so the expected diagnostic movement did not occur.
Agent diagnosis: File path was active, but recent-resident protection skipped no victims in the measured decode path: hybrid_resident_skip and decode_hybrid_resident_skip remained 0, while hot-resident skip/evict behavior dominated eviction accounting.
My diagnosis: Hypothesis mismatch and no useful patch. The fixed top-k/cache-capacity pattern appears to be governed by current/hot required protection and unavoidable slot replacement, not by the generic resident_recent policy.
Needed expert knowledge: Need S4 knowledge of the intended hot_resident_core policy, top-k/cache-capacity invariants, and which eviction counters correspond to movable versus compulsory core evictions.
Patch / commit: patches/failed_attempts/s3_codex_iter_03_fasttemp_p16_d16.patch
