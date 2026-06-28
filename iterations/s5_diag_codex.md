# MobileMoE-AKO Iterations - S5+Diag Codex

Active stage: S5+Diag, expert-knowledge-guided with integrated diagnostic iterations.

Isolation rules:
- Do not read or use S6 branch, commit, patches, logs, or result artifacts.
- Do not read iterations/s6_* or results/runs/s6_*.
- Do not read previous conversation content about the S6 successful patch.
- This file is the active S5+Diag log only.


## s5_diag_baseline_fasttemp_p16_d16

Iteration ID: s5_diag_baseline_fasttemp_p16_d16
Stage: s5_diag
Agent prompt setting: S5+Diag Expert-Knowledge-Guided MobileMoE Optimization with Integrated Diagnostic Iterations
Baseline bottleneck decomposition: decode_tok_s=0.32741; mib_per_token=1431.802; required_miss_count=14736 total / decode_req_miss=6810; required_miss_wait_ms_per_token=1530.009; decode_req_service_ms=24480.15 dominated by decode_req_page_touch_ms=19473.279 plus decode_req_mat_enqueue_ms=4909.637; decode_req_mat_finish_ms=49.817; decode_req_mat_writes=2270; decode_req_page_touch_mib=22908.835; decode_core_upload_mib=22908.835; decode_req_hit=3942; decode_evict=6810; cache_hit_rate=0.3666; eviction_churn=14064; peak_temp_skin_c_decode=35.039 C
Targeted bottleneck: baseline only
Expected diagnostic movement: baseline decomposition establishes target: reduce decode required misses/evictions and page-touch/core-upload service without increasing mib_per_token
Agent hypothesis: Baseline shows decode is dominated by required-core service and page-touch/core upload under low cache hit rate and high eviction churn; existing counters can distinguish page touch vs enqueue vs finish, so first iteration can be optimization rather than diagnostic.
Chosen optimization direction: baseline diagnostic decomposition; no source change
Files inspected: SKILL.md; references/system_overview.md; references/constraints.md; references/benchmark_instructions.md; references/metrics_schema.md; references/expert_hints/coremoe_required_core.md; references/expert_hints/diagnostic_instrumentation.md; baseline summary.jsonl/summary.csv
Files modified: none
Change summary: No source edits. Built/deployed current branch runner and recorded fixed p16/d16 baseline.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s5_diag_baseline_fasttemp_p16_d16
Compile result: cmake build: no work to do; deployed md5 6d15f401a12e515d066141c3a02ba4ea matched phone
Correctness result: ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.32740975420776786
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1530.009375
  decode_req_page_touch_ms: 19473.279000000002
  decode_req_mat_enqueue_ms: 4909.636999999999
  decode_req_mat_finish_ms: 49.81700000000016
  decode_req_service_ms: 24480.15
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 35.0394
Result: Baseline correct. Throughput low with high normalized transfer and required-miss service.
Agent diagnosis: Competing hypotheses: (1) cache capacity/policy is evicting cores before reuse; supported by decode_evict=decode_req_miss=6810 and hit rate 0.3666. (2) page-touch dominates materialization, so reducing miss count/upload MiB should help more than queue tuning. (3) thermal is unlikely primary for baseline because peak skin decode is 35.039 C under start limits. Missing diagnostics: no per-layer/per-projection miss/service distribution, no madvise/page-fault counts, no per-write latency distribution.
My diagnosis: Existing S5 counters are sufficient for first policy attempt: target required-core residency/eviction churn and page-touch volume. They cannot yet identify which layers/projections cause the worst churn, but aggregate signal is strong enough to test a cache/protection change.
Needed expert knowledge: S5 expert hint used: required-core serving, expert/core residency, eviction/cache churn, required-first bandwidth, and required-miss service latency are likely dominant MobileMoE policy axes. Diagnostic hint used to avoid adding instrumentation while page-touch/enqueue/finish/service counters already exist.
Patch / commit: baseline only; no patch

## s5_diag_iter_01_fasttemp_p16_d16

Iteration ID: s5_diag_iter_01_fasttemp_p16_d16
Stage: s5_diag
Agent prompt setting: S5+Diag Expert-Knowledge-Guided MobileMoE Optimization with Integrated Diagnostic Iterations
Baseline bottleneck decomposition: Baseline decode_tok_s=0.32741; mib_per_token=1431.802; decode_req_service_ms=24480.15 dominated by page_touch=19473.279 plus enqueue=4909.637 and finish=49.817; decode_req_miss=6810; decode_evict=6810; cache_hit_rate=0.3666; peak_temp_skin_decode=35.039 C
Targeted bottleneck: Required GPU-v3 core payload synchronous page-touch during decode required misses
Expected diagnostic movement: decode_req_page_touch_ms and decode_req_page_touch_mib should drop; decode_req_service_ms and decode_tok_s should improve; mib_per_token should stay flat; decode_req_miss may stay flat
Agent hypothesis: The explicit CPU page-touch loop for required packed core payloads is serialized on the critical path and duplicates work that the OpenCL write path can naturally fault in; clamping mode 2 to the normal upload path should reduce critical decode service without changing payload bytes.
Chosen optimization direction: Optimization iteration: bypass explicit required-core page-touch by clamping core_page_touch_mode_ to 0/1 in HybridColdGpuShadowExecutor
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; mllm/backends/opencl/moe/HybridOpenCLMaterializer.cpp; HybridResourceManager/HybridPrefetchScheduler policy files; Tucker runner env contract
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Clamp core_page_touch_mode_ with std::min(1, std::max(0, core_page_touch_mode)) so fixed mode=2 no longer runs the explicit interleaved touchMmapPages loop before required GPU-v3 payload uploads.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s5_diag_iter_01_fasttemp_p16_d16
Compile result: build succeeded; deployed md5 2ccb7bcd84084bb930c7b31b3e52e28e changed from baseline and matched phone
Correctness result: ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.3326288462263289
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1453.4939375000024
  decode_req_page_touch_ms: 0.0
  decode_req_mat_enqueue_ms: 12681.600000000006
  decode_req_mat_finish_ms: 10530.1
  decode_req_service_ms: 23255.90300000004
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 0.0
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 35.3928
Result: Correct, same mib_per_token, decode_tok_s +1.59% versus baseline; not meaningful enough for best patch. Archived as no-meaningful-speedup/hypothesis-partial.
Agent diagnosis: The page-touch subcounter collapsed as expected, but the cost largely moved into OpenCL enqueue/finish: enqueue rose from 4909.6 ms to 12681.6 ms and finish from 49.8 ms to 10530.1 ms. Required service improved only 24480.15 -> 23255.90 ms and decode_tok_s only 0.32741 -> 0.33263. Transfer volume, misses, evictions, and cache hit rate were unchanged.
My diagnosis: This distinguishes explicit CPU page-touch from unavoidable memory residency/driver upload cost. The bottleneck is not merely the explicit touch loop; it is required miss volume and/or page-fault/upload service for the same 22908.835 MiB decode core payload. Next optimization should reduce miss count/churn or transferred bytes, not just shift where page faults are charged.
Needed expert knowledge: S5 required-core serving and diagnostic decomposition: page-touch/enqueue/finish counters can reveal latency migration; cache/eviction policy must be judged by decode speed and normalized transfer, not subcounter wins.
Patch / commit: archived to patches/failed_attempts/s5_diag_iter_01_fasttemp_p16_d16.patch; not committed

## s5_diag_iter_02_fasttemp_p16_d16

Iteration ID: s5_diag_iter_02_fasttemp_p16_d16
Stage: s5_diag
Agent prompt setting: S5+Diag Expert-Knowledge-Guided MobileMoE Optimization with Integrated Diagnostic Iterations
Baseline bottleneck decomposition: Baseline and iter01 show fixed decode_req_miss=6810, decode_evict=6810, cache_hit_rate=0.3666, mib_per_token=1431.802. Iter01 showed page-touch removal only moved cost into OpenCL enqueue/finish, so next uncertainty is which layers/projections drive required miss/churn.
Targeted bottleneck: Diagnostic-only: expose existing per-layer hybrid cold core breakdown lines to localize miss/service distribution.
Expected diagnostic movement: Benchmark semantics unchanged; aggregate metrics comparable; log should contain [hybrid-cold-core-breakdown] lines with per-layer req_miss, miss reasons, service, page-touch/enqueue/finish.
Agent hypothesis: Existing aggregate counters cannot distinguish whether a small set of layers/projections cause most miss churn. Enabling existing lightweight core-breakdown logging should reveal per-layer concentration without changing runtime behavior.
Chosen optimization direction: Diagnostic iteration: enable existing hybrid GPU core breakdown default
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; Tucker qwen_env; current S5 baseline/iter01 logs
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Changed hybrid_gpu_core_breakdown_ default from false to true.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s5_diag_iter_02_fasttemp_p16_d16
Compile result: build succeeded; deployed md5 2d2eba79e6ca7b37efa326fcba18d8af changed and matched phone
Correctness result: ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.33560983075028433
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1512.7376250000007
  decode_req_page_touch_ms: 19177.317000000025
  decode_req_mat_enqueue_ms: 4957.7519999999995
  decode_req_mat_finish_ms: 22.498999999999956
  decode_req_service_ms: 24203.80200000001
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 36.06692
Result: Diagnostic-only, correctness passing, but no [hybrid-cold-core-breakdown] lines were found in pulled logs; diagnostic did not resolve layer/projection uncertainty. Metrics remained comparable: decode_tok_s=0.33561, mib_per_token unchanged, req_miss/evict unchanged.
Agent diagnosis: The attempted instrumentation default did not surface the intended lines under this runner/log path, possibly because the relevant breakdown path is not reached or the logging condition is elsewhere than expected. Aggregate metrics still show fixed miss/churn and page-touch dominated service.
My diagnosis: No useful diagnostic signal. Do not commit. The current counters still cannot localize per-layer churn; next attempt should either add direct counters to the summary line already parsed, or choose a conservative aggregate policy lever.
Needed expert knowledge: Diagnostic-instrumentation hint: diagnostic-only iterations must actually expose missing counters; failed/no-signal instrumentation should be archived rather than treated as a speedup.
Patch / commit: archived to patches/failed_attempts/s5_diag_iter_02_fasttemp_p16_d16.patch; not committed

## s5_diag_iter_03_fasttemp_p16_d16

Iteration ID: s5_diag_iter_03_fasttemp_p16_d16
Stage: s5_diag
Agent prompt setting: S5+Diag Expert-Knowledge-Guided MobileMoE Optimization with Integrated Diagnostic Iterations
Baseline bottleneck decomposition: Baseline decode_tok_s=0.32741; mib_per_token=1431.802; decode_req_miss=6810; decode_evict=6810; cache_hit_rate=0.3666; decode_req_service_ms=24480.15; decode_req_mat_enqueue_ms=4909.637; finish=49.817; page_touch=19473.279. Iter01 showed page-touch cost migration. Iter02 failed to expose per-layer detail.
Targeted bottleneck: Decode-phase required-core upload contention from speculative same-layer core prewarm that yields no decode prewarm hits.
Expected diagnostic movement: mib_per_token unchanged; decode_req_miss/hit may stay unchanged; prewarm hits stay zero; enqueue/finish and required service should drop if speculative prewarm was contending with required uploads; decode_tok_s should improve.
Agent hypothesis: Because decode prewarm hits are zero under the fixed p16/d16 contract, same-layer speculative core prewarm during decode adds queue/bandwidth pressure without improving residency. Disabling decode speculative core prewarm should reduce required-miss service and improve throughput while preserving transfer volume.
Chosen optimization direction: Optimization iteration: disable speculative core prewarm during decode only
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; Tucker qwen_env; baseline/iter01/iter02 metrics
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Changed speculative_core_has_future_use so same-layer async core prewarm is not submitted in decode; non-decode behavior is unchanged.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s5_diag_iter_03_fasttemp_p16_d16
Compile result: build succeeded; deployed md5 a218e5eba1a9471d97822b3572fa0a99 changed and matched phone
Correctness result: ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.3381169556693169
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1473.0876249999994
  decode_req_page_touch_ms: 19325.252
  decode_req_mat_enqueue_ms: 4181.353000000002
  decode_req_mat_finish_ms: 16.429999999999982
  decode_req_service_ms: 23569.40199999999
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 36.56396
Result: Correct; decode_tok_s=0.33812, +3.27% vs baseline; mib_per_token unchanged at 1431.802; required service dropped 24480.15 -> 23569.40 ms; enqueue dropped 4909.64 -> 4181.35 ms; misses/evicts unchanged.
Agent diagnosis: The improvement is consistent with reducing upload queue contention rather than improving residency. Transfer volume and miss count remain unchanged, so this is a scheduling/contention policy win only. Peak skin was higher than baseline but still under guardrail during decode start; thermal could contribute, so p32/d32 recheck is needed before final best selection.
My diagnosis: Small, interpretable, correctness-passing optimization. It meets the rough 3% threshold and does not worsen normalized transfer, so it is eligible as current best pending p32/d32 signal recheck.
Needed expert knowledge: S5 expert knowledge used: prefetch usefulness must be validated by hit/miss and service counters; zero prewarm hits imply speculative core prewarm can be harmful via bandwidth/queue contention even when required miss volume is unchanged.
Patch / commit: a1d21dd8 [s5 diag iter 03] Disable decode speculative core prewarm
