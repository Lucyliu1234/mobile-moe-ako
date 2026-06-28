# MobileMoE-AKO Iterations

## Current Stage

S2: Concept-Guided Whole-System Exploration.

This root `ITERATIONS.md` is the active S2 working log only.

Archived S1 logs:

- `iterations/s1_codex_blackbox.md`
- `iterations/s1_codex_blackbox_completed.md`

S2 agents must not read `iterations/s1_*` or `patches/failed_attempts/s1_*` as optimization guidance or evidence unless the user explicitly allows it. S2 may read the current stage prompt, fixed benchmark contract, durable constraints, metrics schema, and stage-allowed high-level expert concepts.

## Template

```text
Iteration ID:
Stage: S2-concept-guided
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


## s2_codex_baseline_fasttemp_p16_d16

Iteration ID: s2_codex_baseline_fasttemp_p16_d16
Stage: s2_concept_guided
Agent prompt setting: S2 concept-guided; allowed concepts: residency, eviction churn, prewarm/prefetch hit rate, required miss service latency, transfer scheduling/overlap, heterogeneous CPU/GPU/NPU execution
Baseline bottleneck decomposition: decode_tok_s=0.33992884524429134; mib_per_token=1431.8021875; required_miss_count=14736 whole-run / 6810 decode-only; required_miss_wait_ms_per_token=1467.985; cache_hit_rate=0.3666294643; prewarm_hit_rate unavailable/null; eviction_churn=14064 whole-run / 6810 decode-only; peak_temp_skin_c_decode=33.76488; start_skin=29.26036 end_skin=33.88192; correctness ret=0 generated=16
Targeted bottleneck: baseline only: required miss service latency plus eviction churn from dynamic expert/core residency pressure
Expected diagnostic movement: Before edits, first useful direction should reduce decode_hybrid_req_miss, decode_hybrid_evict, required_miss_wait_ms_per_token, or mib_per_token without correctness loss
Agent hypothesis: Baseline decomposition suggests decode is dominated by required core materialization/upload/page-touch: decode required miss service 23487.76 ms, core upload/page-touch 22908.835 MiB, and 6810 decode evicts.
Chosen optimization direction: Baseline decomposition; next iteration should test expert/core residency or eviction policy
Files inspected: SKILL.md; references/constraints.md; references/benchmark_instructions.md; references/metrics_schema.md; references/prompts/s2_concept_guided.md; Tucker fixed runner env and command; run_qwen2_moe_td_push.sh; linked runner target in build.ninja; baseline summary.jsonl/csv
Files modified: None
Change summary: No source change; ran fixed S2 baseline and parsed metrics
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s2_codex_baseline_fasttemp_p16_d16
Compile result: Baseline runtime already deployed; no source edit yet; branch clean before baseline
Correctness result: PASS ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.33992884524429134
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1467.9850000000008
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 33.76488
Result: Baseline PASS
Agent diagnosis: S2 concepts localize dominant pressure to required miss latency and eviction churn, not thermal or correctness. Missing parser prewarm_hit_rate despite raw hybrid_pre_hit/pre_miss fields; power counters are zero.
My diagnosis: Primary bottleneck appears to be dynamic expert/core residency under too-small effective resident set: every decode miss corresponds to eviction, and most wait is materialization/page-touch/upload. First edit should target one residency/eviction policy knob in linked OpenCL MoE runtime files.
Needed expert knowledge: Need exact meaning of hot/core residency protections, layer window semantics, and whether decode-only counters should supersede whole-run parser counters for policy selection.
Patch / commit: baseline only; no patch

## s2_codex_iter_01_fasttemp_p16_d16

Iteration ID: s2_codex_iter_01_fasttemp_p16_d16
Stage: s2_concept_guided
Agent prompt setting: S2 concept-guided: expert/core residency and eviction churn
Baseline bottleneck decomposition: Baseline decode_tok_s=0.33992884524429134; mib_per_token=1431.8021875; parser required_miss_count=14736; decode_hybrid_req_miss=6810; required_miss_wait_ms_per_token=1467.985; cache_hit_rate=0.3666294643; eviction_churn=14064; decode_hybrid_hot_evict=6810; prewarm_hit_rate unavailable
Targeted bottleneck: Expert/core residency under hot eviction churn
Expected diagnostic movement: Reduce decode_hybrid_hot_evict, decode_hybrid_req_miss, eviction_churn, mib_per_token, or required_miss_wait_ms_per_token; improve cache_hit_rate
Agent hypothesis: First-pass victim selection was evicting history-hot required experts too aggressively; protecting history-hot experts before normal LRU should improve residency without changing transfer accounting semantics.
Chosen optimization direction: Skip history-hot experts in first-pass required victim selection; allow second-pass fallback to preserve progress
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp selectCacheVictim/hot history/cache miss paths; HybridResourceManager; HybridPrefetchScheduler; expert hint coremoe_required_core.md
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Added a first-pass required-miss victim skip for isHistoryHotNoLock experts
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s2_codex_iter_01_fasttemp_p16_d16
Compile result: PASS: cmake target rebuilt; deployed runner md5 changed 6d15f401a12e515d066141c3a02ba4ea -> 3c9c20e1d5a952a6afd9588fc4466c31
Correctness result: PASS ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.34489693725052906
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1454.448250000001
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 35.1762
Result: Archived no-signal/hypothesis-mismatch patch: decode_tok_s +1.46% but below meaningful threshold and target miss/evict/transfer/hit diagnostics unchanged
Agent diagnosis: Patch made hot skip count much larger (decode_hot_skip 54207 vs 15708 baseline) but decode_hot_evict remained 6810, decode_req_miss remained 6810, cache hit unchanged, mib_per_token unchanged. Small speed delta likely noise or minor slot-selection overhead variance, not causal residency improvement.
My diagnosis: The selected first-pass victim filter does not alter the constrained effective resident set; second-pass fallback still evicts a hot expert for every decode miss. Need a mechanism that changes capacity, required miss service, or prefetch timing rather than just first-pass ordering.
Needed expert knowledge: Need the intended role of hot_resident_window versus gpu_cache_capacity=8, and whether slot capacity per projection can be safely adjusted independently of benchmark contract.
Patch / commit: patches/failed_attempts/s2_codex_iter_01_fasttemp_p16_d16.patch

## s2_codex_iter_02_fasttemp_p16_d16

Iteration ID: s2_codex_iter_02_fasttemp_p16_d16
Stage: s2_concept_guided
Agent prompt setting: S2 concept-guided: required miss service latency and transfer scheduling/overlap
Baseline bottleneck decomposition: Baseline decode_tok_s=0.33992884524429134; mib_per_token=1431.8021875; decode_hybrid_req_miss=6810; required_miss_wait_ms_per_token=1467.985; decode_hybrid_req_page_touch_ms=18591.417; decode_hybrid_req_service_ms=23487.760; cache_hit_rate=0.3666294643
Targeted bottleneck: Required miss service latency, especially page-touch/upload sequencing
Expected diagnostic movement: Lower required_miss_wait_ms_per_token, decode_hybrid_req_page_touch_ms, and decode_hybrid_req_service_ms with unchanged mib_per_token and correctness
Agent hypothesis: The runtime has an interleaved page-touch/upload mode (core_page_touch_mode=2) that may overlap page-touch with OpenCL enqueues and lower required miss service latency for packed payloads.
Chosen optimization direction: Default hybrid_gpu_core_page_touch_mode_ to 2 while preserving env override
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp materializeCoreSlotBatchGpuV3/materializePackedExpertSlotBatchGpuV3/page-touch paths; HybridOpenCLMaterializer enqueue/finish paths
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Changed default hybrid_gpu_core_page_touch_mode_ from 0 to 2
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s2_codex_iter_02_fasttemp_p16_d16
Compile result: PASS: cmake target rebuilt; deployed runner md5 changed 3c9c20e1d5a952a6afd9588fc4466c31 -> ae4bbd4644acf758740080e764635e8a
Correctness result: PASS ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.33470526231144276
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1516.9371875000002
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 36.11404
Result: Archived regression: decode_tok_s 0.334705 vs baseline 0.339929; required_miss_wait_ms_per_token worsened to 1516.937; transfer and miss counts unchanged
Agent diagnosis: Interleaved page-touch mode did not reduce page-touch or service latency in decode; decode_hybrid_req_page_touch_ms was 18776.938 vs baseline 18591.417 and decode_hybrid_req_service_ms was 24270.995 vs baseline 23487.760.
My diagnosis: The existing fixed runner likely already uses a path where mode=2 adds scheduling overhead or cannot overlap effectively. Since miss volume and transfer volume are unchanged, this service-path toggle is not useful.
Needed expert knowledge: Need device/OpenCL command queue behavior and whether nonblocking writes on this Qualcomm stack overlap with CPU mmap page-touch or serialize at finish.
Patch / commit: patches/failed_attempts/s2_codex_iter_02_fasttemp_p16_d16.patch

## s2_codex_iter_03_fasttemp_p16_d16

Iteration ID: s2_codex_iter_03_fasttemp_p16_d16
Stage: s2_concept_guided
Agent prompt setting: S2 concept-guided: expert/core residency and eviction churn
Baseline bottleneck decomposition: Baseline decode_tok_s=0.33992884524429134; mib_per_token=1431.8021875; decode_hybrid_req_miss=6810; decode_hybrid_evict=6810; required_miss_wait_ms_per_token=1467.985; cache_hit_rate=0.3666294643; decode_hybrid_core_upload_mib=22908.835
Targeted bottleneck: Required-core residency capacity under eviction churn
Expected diagnostic movement: Reduce decode_hybrid_req_miss, decode_hybrid_evict, mib_per_token, and required_miss_wait_ms_per_token; improve cache_hit_rate without primary throughput loss
Agent hypothesis: The effective per-projection core cache capacity of 8 is too small for hot-resident serving; adding two hot-residency slack slots should reduce required misses and transfer.
Chosen optimization direction: Increase HybridColdGpuShadowExecutor cache_capacity_ by +2 only when hot_resident_core is enabled
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp constructor/cache_capacity; batch required core miss paths; baseline and iteration summaries
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Changed constructor initialization to cache_capacity + 2 when hot_resident_core is true
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s2_codex_iter_03_fasttemp_p16_d16
Compile result: PASS: cmake target rebuilt; deployed runner md5 changed ae4bbd4644acf758740080e764635e8a -> b054f6eb4031df26cf326d9a52161352
Correctness result: PASS ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.3035814701384269
  mib_per_token: 1340.9996249999995
  required_miss_count: 13881.0
  upload_bytes: 49505226457.088
  prewarm_hit_rate: None
  eviction_churn: 13041.0
  required_miss_wait_ms_per_token: 1649.0527499999996
  cache_hit_rate: 0.41127232142857145
  peak_temp_skin_c_decode: 36.67948
Result: Archived regression/tradeoff failure: residency diagnostics improved but decode_tok_s regressed to 0.303581 (0.893x baseline)
Agent diagnosis: Capacity slack reduced whole-run required_miss_count 14736->13881, eviction_churn 14064->13041, mib_per_token 1431.80->1341.00, and improved cache_hit_rate 0.3666->0.4113. However required_miss_wait_ms_per_token worsened 1467.99->1649.05, decode service/core upload time increased, memory/thermal pressure rose, and primary speed regressed.
My diagnosis: S2 concepts successfully localized a real residency/transfer lever, but the lever trades lower transfer for slower service and hotter decode on this phone. Best patch selection rejects it because primary throughput regressed despite improved normalized transfer volume.
Needed expert knowledge: Need an expert policy for balancing resident-set size against OpenCL memory pressure/page-touch cost, plus measured cache-capacity sweep/noise model to find whether a smaller +1 or layer-specific slack could help.
Patch / commit: patches/failed_attempts/s2_codex_iter_03_fasttemp_p16_d16.patch
