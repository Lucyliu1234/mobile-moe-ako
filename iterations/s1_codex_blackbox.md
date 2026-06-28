# MobileMoE-AKO Iterations

Use this file as the durable research log. Every benchmarked attempt gets one entry, including failed or no-signal attempts.

## Template

```text
Iteration ID:
Stage:
Agent prompt setting:
Baseline bottleneck decomposition:
Targeted bottleneck:
Expected diagnostic movement:
Agent hypothesis:
Chosen optimization direction:
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

## s1_baseline_day_smoke_p16_d16

Iteration ID: s1_baseline_day_smoke_p16_d16
Stage: s1
Agent prompt setting: S1 black-box, no expert hints
Baseline bottleneck decomposition: 
Targeted bottleneck: 
Expected diagnostic movement: 
Agent hypothesis: Baseline — no change. Establish primary metric and diagnostic decomposition.
Chosen optimization direction: None (baseline)
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp, mllm/backends/opencl/moe/HybridPrefetchScheduler.hpp, mllm/backends/qnn/aot_rt/TokenGenerator.cpp
Files modified: none
Change summary: No change. Baseline binary dated 2026-06-02 already on device.
Benchmark command: python run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --context-len 384 --gpu-cache-capacity 8 --out-dir results/runs/s1_baseline_day_smoke_p16_d16
Compile result: True
Correctness result: True
Metrics:
  decode_tok_s: 0.3447300513768432
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1402.9009374999987
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 32.40828
Result: correct
Agent diagnosis: decode_tok_s=0.345. mib_per_token=1431.8 (very high — 1.4 GiB transferred per generated token). required_miss_count=14736 out of 16 decode steps (920 misses/step), suggesting nearly all expert cores are fetched from host DRAM on each decode token. cache_hit_rate=0.367 — only 37% of required expert lookups are served from GPU cache. required_miss_wait_ms_per_token=1403ms, meaning the decode loop spends ~1.4s/token waiting for required expert cores to upload. eviction_churn=14064 suggests the GPU cache is under heavy pressure and evicting resident cores frequently. With gpu_cache_capacity=8 slots and top-8 routing across 28 layers, the 224 expert activations per token heavily exceed the cache capacity, causing high miss rate and large transfer volume. Suspected primary bottleneck: expert core upload latency on required-miss path dominating decode time.
My diagnosis: High required_miss_count and mib_per_token indicate that expert cores are not being kept resident between decode steps. With 8 cache slots and 64 experts across 28 layers, the cache is too small to cover the hot expert set. The 37% hit rate means only ~3 of 8 slots are being reused across consecutive tokens. The 1403ms/token service cost on miss path is the primary decode bottleneck.
Needed expert knowledge: Unknown: what is the total GPU cache memory and how is slot capacity related to MiB? Is 8 cache slots 8 expert cores total or 8 per layer? What is the typical temporal locality of expert selection across decode steps for this model/prompt?
Patch / commit: none (baseline)

## s1_iter_01

Iteration ID: s1_iter_01
Stage: s1
Agent prompt setting: S1 black-box, no expert hints
Baseline bottleneck decomposition: 
Targeted bottleneck: 
Expected diagnostic movement: 
Agent hypothesis: Enabling hybrid_gpu_resident_recent_ by default (true, steps=4) would protect recently-used GPU shadow expert slots from eviction, reducing required-miss rate and upload volume.
Chosen optimization direction: Change default for hybrid_gpu_resident_recent_ from false to true, resident_recent_steps from 2 to 4
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp:13938, mllm/backends/opencl/moe/GpuMoePrefetchPolicy.cpp
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp:13938-13939
Change summary: Changed hybrid_gpu_resident_recent_ default from false to true, resident_recent_steps from 2 to 4.
Benchmark command: python run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --context-len 384 --gpu-cache-capacity 8 --out-dir results/runs/s1_iter_01
Compile result: True
Correctness result: True
Metrics:
  decode_tok_s: 0.33805447536586475
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1446.7378125000018
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 33.25188
Result: no-signal regression
Agent diagnosis: decode_tok_s=0.338 (-2% vs baseline, within noise). GPU shadow metrics unchanged: same cache_hit_rate=0.367, same upload_mib_tok=1431.8, same required_miss_count=14736. The resident_recent flag is read by HybridColdGpuShadowExecutor's prefetch_policy_ but the benchmark sets PREWARM_NO_EVICT=1, which prevents prewarm eviction entirely. With PREWARM_NO_EVICT, the resident_recent flag only applies to choosing eviction victims among non-prewarm entries. With 8 cache slots and 8 top-k experts per layer per token, the cache is fully replaced each step and resident_recent has no room to protect anyone. Wrong file localization: the eviction policy is not the bottleneck at this cache capacity.
My diagnosis: hypothesis/metric mismatch. The resident_recent flag is structurally correct but has no effect when cache_capacity=8 equals top-k=8 and all slots are replaced every step. Need to understand whether the 8 slots are shared across all layers or per-layer. If per-layer and the model has 28 MoE layers, then 8*28=224 slots exist, and there may be cross-token reuse opportunity within a layer. But PREWARM_NO_EVICT already protects prewarm entries, and resident_recent adds protection at the Required level which is irrelevant when every slot is used each step.
Needed expert knowledge: Is cache_capacity=8 per layer or global? How many experts are active at each layer per decode step (top-k=8 total, or per layer)? What is the expert temporal locality profile?
Patch / commit: patches/failed_attempts/s1_iter_01_resident_recent_default.patch

## s1_iter_02

Iteration ID: s1_iter_02
Stage: s1
Agent prompt setting: S1 black-box, no expert hints
Baseline bottleneck decomposition: required_miss_wait_ms_per_token=1403ms dominates decode. With gpu_cache_capacity=8 slots and top-k=8 routing, all 8 slots are replaced each step (cache_hit_rate=0.367 → ~63% upload). mib_per_token=1431.8 (1.4 GiB/token from UFS). required_miss_count=14736 across 16 decode steps (~920 misses/step).
Targeted bottleneck: async prewarm thread missing GPU V3 mmap coverage — prefetchLayerExperts() had no branch for ld.using_gpu_v3_mmap(), causing the early-return guard to skip all GPU V3 experts, so madvise(WILLNEED) hints were never issued for GPU V3 mmap pages before required-miss materialisation.
Expected diagnostic movement: lower required_miss_wait_ms_per_token if OS page-cache prefetch reduces UFS latency at time of touchMmapPages() call; possibly lower mib_per_token if prewarm overlaps with NPU execution and reduces required-miss count.
Agent hypothesis: prefetchLayerExperts() was early-returning before issuing madvise(WILLNEED) for GPU V3 format experts because the guard condition checked only ld.using_mmap(), using_fp16_mmap(), using_tile_quant_mmap(), using_panel_i8_mmap() — not using_gpu_v3_mmap(). Adding GPU V3 madvise hints would allow the OS to prefetch GPU V3 pages from UFS while the NPU runs earlier subgraphs, reducing stall at required-miss touchMmapPages().
Chosen optimization direction: Fix early-exit guard in prefetchLayerExperts() to include using_gpu_v3_mmap(), then add per-expert madvise(WILLNEED) branch for packed_gpu_v3 / per-projection GPU V3 formats.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp:23885–23935
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp:23891, :23912–23935
Change summary: (1) Guard fix: added !ld.using_gpu_v3_mmap() to early-return condition so GPU V3 experts are not skipped. (2) Added madvise(WILLNEED) branch at top of prefetch loop: if packed_gpu_v3.loaded(), advises entire packed payload per expert; else advises per-projection (gate/up/down) GPU V3 expert offsets.
Benchmark command: python run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --context-len 384 --gpu-cache-capacity 8 --out-dir results/runs/s1_iter_02
Compile result: True
Correctness result: True
Metrics:
  decode_tok_s: 0.34564790403431594
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1412.9550625
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 33.32028
Result: no-signal (identical GPU shadow metrics, +0.3% tok_s noise-level)
Agent diagnosis: All GPU shadow metrics are unchanged vs baseline. The madvise(WILLNEED) hints issued by the async prewarm thread via prefetchLayerExperts() had no observable effect on required_miss_wait_ms_per_token or mib_per_token. Root cause: touchMmapPages() at aot_run.cpp:115 is a synchronous blocking call that itself issues madvise(WILLNEED) followed by a sequential page-touch loop. The prewarm thread's earlier madvise is therefore redundant — the required-miss path blocks in touchMmapPages() regardless, completing the page-in before the GPU upload starts. The bottleneck is not the absence of upstream madvise hints; it is the synchronous blocking nature of touchMmapPages() itself on the critical path.
My diagnosis: prefetchLayerExperts() coverage was a real gap but it's the wrong bottleneck. The async prewarm thread calls madvise ahead of time, but required-miss service still blocks synchronously in touchMmapPages(). The only way to reduce required_miss_wait_ms_per_token is to reduce the number of required misses (improve cache_hit_rate) or to overlap the touchMmapPages() work with other computation. The prewarm thread is already supposed to do this overlap — the real question is why prewarm_hit_rate is 0/null (no prewarm hits at all in baseline and iter 02). This suggests either the prewarm thread is not issuing uploads for the right experts, or its uploads complete but are evicted before the required-miss lookup.
Needed expert knowledge: Why is prewarm_hit_rate null/0? Is the async prewarm thread actually uploading GPU expert cores to device, or only issuing host-side madvise? Are prewarm uploads completing before the required-miss lookup, or are they being evicted? What is the timing relationship between prewarm completion and required-miss lookup in HybridColdGpuShadowExecutor?
Patch / commit: patches/failed_attempts/s1_iter_02_gpu_v3_prefetch_madvise.patch

## s1_codex_baseline_fasttemp_p16_d16

Iteration ID: s1_codex_baseline_fasttemp_p16_d16
Stage: S1-blackbox-codex
Agent prompt setting: Fresh Codex S1 black-box; no Claude results or expert hints used
Baseline bottleneck decomposition: Raw p16/d16 baseline: decode_tok_s=0.3176794154, correct ret=0 generated=16/16, mib_per_token=1431.8021875, decode_s=50.36524, required_miss_count=6810, required_miss_wait_ms_per_token=1502.305625, cache_hit_rate=0.366629, eviction_churn=6810, start_skin=28.41448C, peak_skin_decode=32.9418C, start_battery=29.1C, peak_battery_decode=30.0C. Missing/limited diagnostics: no prewarm_hit_rate in normalized metrics, sampled power/energy zero, no repeated baseline for noise estimate by contract.
Targeted bottleneck: none - baseline only
Expected diagnostic movement: none - baseline only
Agent hypothesis: Baseline measurement for exact fixed Tucker p16/d16 contract before runtime edits.
Chosen optimization direction: Measure raw benchmark-exposed performance and guardrails only.
Files inspected: references/system_overview.md; references/constraints.md; references/benchmark_instructions.md; references/metrics_schema.md; results/runs/s1_codex_baseline_fasttemp_p16_d16/summary.jsonl; results/runs/s1_codex_baseline_fasttemp_p16_d16/logs/r01_instruction_0000_p16.log tail
Files modified: results/runs/s1_codex_baseline_fasttemp_p16_d16/metrics.json; ITERATIONS.md
Change summary: No runtime source changes.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s1_codex_baseline_fasttemp_p16_d16
Compile result: baseline runtime already deployed; benchmark launch succeeded and ret observed
Correctness result: PASS ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.31767941540633976
  mib_per_token: 1431.8021875
  required_miss_count: 6810.0
  upload_bytes: 24021654568.96
  prewarm_hit_rate: None
  eviction_churn: 6810.0
  required_miss_wait_ms_per_token: 1502.3056250000004
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 32.9418
Result: Baseline established under fixed p16/d16 thermal-gated contract.
Agent diagnosis: Black-box inference: decode time is dominated by raw runtime-side service/upload timing counters exposed by the benchmark, with high normalized transfer volume and low hit-rate-like counters. Treating this only as raw S1 feedback, not as supplied expert direction.
My diagnosis: S1 should inspect runner-visible runtime code around qwen2_moe_td_qnn_aot and QNN/backend deployment path. First hypothesis should target one small runtime policy knob that could reduce per-token service/upload work or scheduling overhead without changing benchmark semantics.
Needed expert knowledge: A noise model for this exact thermal-gated p16/d16 contract and deeper knowledge of which runtime counters are causally actionable would help; S1 lacks expert file hints by design.
Patch / commit: baseline only; no source patch

## s1_codex_iter_01_fasttemp_p16_d16

Iteration ID: s1_codex_iter_01_fasttemp_p16_d16
Stage: S1-blackbox-codex
Agent prompt setting: Fresh Codex S1 black-box; no Claude results or expert hints used
Baseline bottleneck decomposition: Codex baseline decode_tok_s=0.3176794154, correct ret=0 generated=16/16, mib_per_token=1431.8021875, required_miss_count=6810, required_miss_wait_ms_per_token=1502.305625, cache_hit_rate=0.366629, eviction_churn=6810.
Targeted bottleneck: Raw per-miss service/materialization overhead while preserving selected payload volume.
Expected diagnostic movement: decode_tok_s up; mib_per_token unchanged; materializer_pool_reuses/recycles should become nonzero; required_miss_wait_ms_per_token should fall.
Agent hypothesis: Auto-enabling the existing materializer buffer pool for the hybrid GPU path under a core arena budget will reduce repeated OpenCL buffer allocation/release overhead without changing payload selection or transfer accounting.
Chosen optimization direction: Enable existing materializer buffer pool by default when hybrid GPU path and core arena budget are active, unless environment explicitly overrides it.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; mllm/backends/opencl/moe/HybridOpenCLMaterializer.hpp; mllm/backends/opencl/moe/HybridOpenCLMaterializer.cpp; fixed Tucker runner env/export section; phone md5 deployment state
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; results/runs/s1_codex_iter_01_fasttemp_p16_d16/metrics.json; ITERATIONS.md; patches/failed_attempts/s1_codex_iter_01_fasttemp_p16_d16.patch
Change summary: Set hybrid_gpu_materializer_pool_=true by default when the hybrid GPU path and core arena budget are active.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s1_codex_iter_01_fasttemp_p16_d16
Compile result: PASS: cmake --build build-android-arm64-v8a-qnn --target mllm-qwen2-moe-td-qnn-aot-runner succeeded; deployed runner md5 243271b98a74c7cdf6c5316bfea51351 verified on phone
Correctness result: PASS ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.3363168774255935
  mib_per_token: 1431.8021875
  required_miss_count: 6810.0
  upload_bytes: 24021654568.96
  prewarm_hit_rate: None
  eviction_churn: 6810.0
  required_miss_wait_ms_per_token: 1482.3414999999984
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 33.67824
Result: Correct and faster than Codex baseline (+5.87% decode_tok_s) with unchanged mib_per_token, but archived as hypothesis/metric mismatch because materializer pool counters remained zero and required_miss_wait_ms_per_token did not improve.
Agent diagnosis: The primary metric improved, but the expected pool diagnostics did not move. The speed difference may be thermal/noise or some indirect effect not captured by the expected counters; this is not strong evidence for the hypothesis.
My diagnosis: Treat as no-signal/hypothesis mismatch. The pool may not have accepted buffers because the default max poolable buffer is too small or the benchmark path does not release through the pool; a follow-up must target a more directly exposed diagnostic.
Needed expert knowledge: Need exact buffer size distribution and whether materializer stats are reported for the per-miss path; S1 lacks that implementation map.
Patch / commit: archived patch; no commit

## s1_codex_iter_02_fasttemp_p16_d16

Iteration ID: s1_codex_iter_02_fasttemp_p16_d16
Stage: S1-blackbox-codex
Agent prompt setting: Fresh Codex S1 black-box; no Claude results or expert hints used
Baseline bottleneck decomposition: Codex baseline decode_tok_s=0.3176794154, correct ret=0 generated=16/16, mib_per_token=1431.8021875, required_miss_count=6810, required_miss_wait_ms_per_token=1502.305625, cache_hit_rate=0.366629, eviction_churn=6810.
Targeted bottleneck: Raw per-miss materialization buffer allocation/reuse under large buffer sizes.
Expected diagnostic movement: decode_tok_s up; mib_per_token unchanged; materializer_pool_reuses/recycles nonzero; required_miss_wait_ms_per_token down or stable.
Agent hypothesis: The iteration 01 pool did not engage because the default max poolable buffer was likely too small; auto-enabling the pool and increasing the max poolable buffer to 128 MiB should expose reuse on the measured path.
Chosen optimization direction: Auto-enable materializer pool under hybrid GPU/core budget and raise default max poolable buffer to 128 MiB when not explicitly configured.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; mllm/backends/opencl/moe/HybridOpenCLMaterializer.cpp; results/runs/s1_codex_iter_01_fasttemp_p16_d16/metrics.json; results/runs/s1_codex_iter_02_fasttemp_p16_d16/summary.jsonl
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; results/runs/s1_codex_iter_02_fasttemp_p16_d16/metrics.json; ITERATIONS.md; patches/failed_attempts/s1_codex_iter_02_fasttemp_p16_d16.patch
Change summary: Auto-enabled materializer pool and lifted default max poolable buffer cap from 32 MiB to 128 MiB under active hybrid GPU core-budget policy.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s1_codex_iter_02_fasttemp_p16_d16
Compile result: PASS: cmake --build build-android-arm64-v8a-qnn --target mllm-qwen2-moe-td-qnn-aot-runner succeeded; deployed runner md5 0a305e0121f42b1c01dc6c860462287d verified on phone
Correctness result: PASS ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.3348008421496683
  mib_per_token: 1431.8021875
  required_miss_count: 6810.0
  upload_bytes: 24021654568.96
  prewarm_hit_rate: None
  eviction_churn: 6810.0
  required_miss_wait_ms_per_token: 1497.2333750000005
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 34.70804
Result: Correct and faster than Codex baseline (+5.39% decode_tok_s) with unchanged mib_per_token, but archived as no-signal/hypothesis mismatch because materializer pool counters remained zero and service timing did not improve.
Agent diagnosis: The expected materializer-pool diagnostic still did not move. The speedup is not attributable to the modified policy from exposed counters.
My diagnosis: This runtime surface appears inactive or unreported for the measured path. Stop pursuing materializer-pool variants in S1 and try a different exposed policy surface.
Needed expert knowledge: Need implementation-level knowledge of which OpenCL buffers are persistent versus released through the materializer pool; S1 did not localize this from black-box counters.
Patch / commit: archived patch; no commit

## s1_codex_iter_03_fasttemp_p16_d16

Iteration ID: s1_codex_iter_03_fasttemp_p16_d16
Stage: S1-blackbox-codex
Agent prompt setting: Fresh Codex S1 black-box; no Claude results or expert hints used
Baseline bottleneck decomposition: Codex baseline decode_tok_s=0.3176794154, correct ret=0 generated=16/16, mib_per_token=1431.8021875, required_miss_count=6810, decode_hybrid_pre_hit=0, required_miss_wait_ms_per_token=1502.305625, cache_hit_rate=0.366629, eviction_churn=6810.
Targeted bottleneck: Lack of decode pre-hit movement and persistent required-miss service cost.
Expected diagnostic movement: decode_hybrid_pre_hit should increase or required_miss_service_ms_per_token should decrease; decode_tok_s should improve; mib_per_token should not regress.
Agent hypothesis: Defaulting the existing next-layer prewarm path on when async hybrid GPU prewarm is active will move predicted work before the required path and improve exposed pre-hit/service counters.
Chosen optimization direction: Change only the default for MLLM_QNN_TD_HYBRID_GPU_NEXT_LAYER_PREWARM from false to active when hybrid async prewarm and cold delta are enabled, preserving explicit env override.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; results/runs/s1_codex_baseline_fasttemp_p16_d16/summary.jsonl; results/runs/s1_codex_iter_03_fasttemp_p16_d16/summary.jsonl
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; results/runs/s1_codex_iter_03_fasttemp_p16_d16/metrics.json; ITERATIONS.md; patches/failed_attempts/s1_codex_iter_03_fasttemp_p16_d16.patch
Change summary: Defaulted next-layer prewarm to enabled under active async hybrid GPU cold-delta mode.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s1_codex_iter_03_fasttemp_p16_d16
Compile result: PASS: cmake --build build-android-arm64-v8a-qnn --target mllm-qwen2-moe-td-qnn-aot-runner succeeded; deployed runner md5 1640672dda654be6fb3662a5b889f6df verified on phone
Correctness result: PASS ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.33490031796692066
  mib_per_token: 1431.8021875
  required_miss_count: 6810.0
  upload_bytes: 24021654568.96
  prewarm_hit_rate: 0.0
  eviction_churn: 6810.0
  required_miss_wait_ms_per_token: 1467.176124999999
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 35.14808
Result: Correct and faster than Codex baseline (+5.42% decode_tok_s) with unchanged mib_per_token, but archived as no-signal/hypothesis mismatch: decode_hybrid_pre_hit/pre_miss remained 0 and required miss count/transfer stayed unchanged.
Agent diagnosis: Next-layer prewarm submit/complete counters exist globally, but the expected decode-phase pre-hit counters did not move. The patch did not localize the measured bottleneck.
My diagnosis: This is the third consecutive no-signal/hypothesis-mismatch smoke attempt. Stop S1 per early-stop rule; black-box exploration failed to identify a causal runtime surface despite finding runner/build/deploy plumbing.
Needed expert knowledge: Need stage-appropriate expert context on which prewarm path maps to decode pre-hit counters and which files control required-path core residency. S1 black-box inspection was insufficient.
Patch / commit: archived patch; no commit; early stop
