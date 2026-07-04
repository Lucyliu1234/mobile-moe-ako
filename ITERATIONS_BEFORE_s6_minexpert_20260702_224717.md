# ITERATIONS - K3 Fine Factor/Support Kernel AKO

Active log for K3-fine: selected TD factor/support dispatch-level profiling and optimization for Qwen2MoE hybrid MoE OpenCL kernels.

Previous active logs are archived under `iterations/`.

## blackbox_diag_rerun_baseline_fasttemp_p16_d16

Iteration ID: blackbox_diag_rerun_baseline_fasttemp_p16_d16
Stage: blackbox_diag_rerun
Agent prompt setting: Black-box diagnostic-driven MobileMoE-AKO rerun, base context only
Baseline bottleneck decomposition: Baseline built from confirmed base da9fa3534a16c0f34adb6709e2ba871741cbf8cc; host/device runner md5 6d15f401a12e515d066141c3a02ba4ea matched. decode_tok_s=0.3253207510, generated=16, ret=0, decode_s=49.18223, uploaded_expert_mib_per_token=1431.8021875, required_miss_service_ms_per_token=1547.63325, decode_req_miss=6810, decode_req_hit=3942, decode_evict=6810, decode_req_page_touch_ms=19629.259, decode_req_mat_enqueue_ms=5049.663, decode_req_mat_finish_ms=37.306, decode_core_upload_mib=22908.835, peak_start within gate: skin 26.2538C battery 26.5C.
Targeted bottleneck: none baseline
Expected diagnostic movement: none baseline
Agent hypothesis: Baseline black-box decomposition only; no optimization hypothesis applied yet.
Chosen optimization direction: Establish rebuilt/deployed baseline and inspect runtime code path for high required-miss transfer/cache churn.
Files inspected: SKILL.md, constraints.md, benchmark_instructions.md, metrics_schema.md, Tucker run_qwen2_moe_td_end2end.py, mllm run_qwen2_moe_td_push.sh, qwen2_moe_td_qnn_aot CMakeLists, baseline summary/log
Files modified: None; ITERATIONS.md appended after prior log backup ITERATIONS_BEFORE_blackbox_diagnostic_rerun_20260702_203047.md
Change summary: No runtime change. Rebuilt/relinked Android runner from base and deployed to /data/local/tmp/qwen2_moe_td_w8a16_clean_20260527.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/blackbox_diag_rerun_baseline_fasttemp_p16_d16
Compile result: 
Correctness result: 
Metrics:
  decode_tok_s: 0.32532075101108676
  mib_per_token: 
  required_miss_count: 
  upload_bytes: 
  prewarm_hit_rate: 
  eviction_churn: 
  required_miss_wait_ms_per_token: 
  decode_req_page_touch_ms: 
  decode_req_mat_enqueue_ms: 
  decode_req_mat_finish_ms: 
  decode_req_service_ms: 
  decode_req_mat_writes: 
  decode_req_page_touch_mib: 
  decode_core_upload_mib: 
  decode_req_miss: 
  decode_req_hit: 
  decode_evict: 
  cache_hit_rate: 
  peak_temp_skin_c_decode: 31.05168
Result: Baseline valid: rebuilt, deployed, md5-verified, correct ret=0 generated=16. Existing diagnostics sufficient for first code-path localization; no diagnostic-only iteration used before iter_01.
Agent diagnosis: Observed anomaly: very slow decode with high transfer per token and high required-miss service. Verified black-box runtime output shows decode misses and evictions at the same count, large page-touch time, large core upload MiB, and low required hit rate. This points toward runtime cache/transfer-state churn rather than thermal gating or correctness failure.
My diagnosis: Start from runtime path that handles required expert-core materialization and eviction policy. The first optimization hypothesis must be derived from this run only and should target fewer required misses/evictions or lower required-miss service without increasing mib_per_token.
Needed expert knowledge: No prior solution text used. Additional context likely needed only if code inspection cannot map the counters to policy decisions.
Patch / commit: baseline only; no patch

## blackbox_diag_rerun_iter_01_fasttemp_p16_d16

Iteration ID: blackbox_diag_rerun_iter_01_fasttemp_p16_d16
Stage: blackbox_diag_rerun
Agent prompt setting: Black-box diagnostic-driven MobileMoE-AKO rerun, base context only
Baseline bottleneck decomposition: Baseline decode_tok_s=0.3253207510, uploaded_expert_mib_per_token=1431.8021875, decode_req_miss=6810, decode_evict=6810, decode_core_upload_mib=22908.835, decode_req_page_touch_ms=19629.259, decode_req_service_ms=24762.132.
Targeted bottleneck: Required cold expert-core cache churn across packed gate/up/down payload path.
Expected diagnostic movement: Expected fewer decode required misses/evictions plus lower decode_core_upload_mib, mib_per_token, req_page_touch_ms, and req_service_ms; decode_tok_s should improve if transfer volume/service was reduced.
Agent hypothesis: Observed anomaly: high required miss and eviction counts with large page-touch/upload volume. Verified runtime code path: fillRoutingWithBandwidthPriority -> runProjectionImplGpuV3 -> ensureExpertsCachedBatchGpuV3/packed payload materialization. Suspected wasteful behavior: packed payloads for gate/up/down were not synchronized as a combined required-cache entry, causing repeated local cache misses. Guardrails: ret=0, generated=16, unchanged benchmark contract, no normalized transfer regression.
Chosen optimization direction: Synchronize required packed expert payload cache population for the gate projection when shared packed payload arena is active.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp, HybridResourceManager, GpuMoeCachePolicy, GpuMoePrefetchPolicy, baseline summary/log
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: For gate projection in packed external payload mode, route required cache population through ensureExpertsPackedCachedBatchGpuV3 so gate/up/down cache entries are created together.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/blackbox_diag_rerun_iter_01_fasttemp_p16_d16
Compile result: success; host md5 59d267c36067596fad8d2eafdd795f25, phone md5 matched, phone stat size 37175952 modify 2026-07-02 20:39:08
Correctness result: ret=0 generated=16
Metrics:
  decode_tok_s: 0.33127697979249765
  mib_per_token: 
  required_miss_count: 
  upload_bytes: 
  prewarm_hit_rate: 
  eviction_churn: 
  required_miss_wait_ms_per_token: 
  decode_req_page_touch_ms: 
  decode_req_mat_enqueue_ms: 
  decode_req_mat_finish_ms: 
  decode_req_service_ms: 
  decode_req_mat_writes: 
  decode_req_page_touch_mib: 
  decode_core_upload_mib: 
  decode_req_miss: 
  decode_req_hit: 
  decode_evict: 
  cache_hit_rate: 
  peak_temp_skin_c_decode: 32.26768
Result: Correctness-passing but hypothesis mismatch/no meaningful speedup: decode_tok_s 0.3312769798 (+1.83%) but uploaded_expert_mib_per_token remained 1431.8021875 and decode_core_upload_mib remained 22908.835. Cache hit counters improved, but transfer volume and required upload/page-touch payload did not move.
Agent diagnosis: The edit improved local cache accounting/hit rate (decode req_miss 6810 -> 2270, evict 6810 -> 2270) but did not reduce actual upload MiB or page-touch MiB. This means the bottleneck is not merely duplicated cache-entry bookkeeping in this path; bytes are still being materialized for the same payload volume.
My diagnosis: Archive rather than commit. The next hypothesis should target page-touch/upload service or actual materialization volume, not just cache hit bookkeeping.
Needed expert knowledge: No prior solution used. Existing diagnostics were enough to reject this hypothesis because transfer volume stayed unchanged.
Patch / commit: archived patches/failed_attempts/blackbox_diag_rerun_iter_01_fasttemp_p16_d16.patch

## blackbox_diag_rerun_iter_02_fasttemp_p16_d16

Iteration ID: blackbox_diag_rerun_iter_02_fasttemp_p16_d16
Stage: blackbox_diag_rerun
Agent prompt setting: Black-box diagnostic-driven MobileMoE-AKO rerun, base context only
Baseline bottleneck decomposition: Baseline decode_tok_s=0.3253207510, uploaded_expert_mib_per_token=1431.8021875, decode_req_page_touch_ms=19629.259, decode_req_service_ms=24762.132, decode_core_upload_mib=22908.835.
Targeted bottleneck: Explicit mmap page-touch in packed expert payload materialization path.
Expected diagnostic movement: Lower decode_req_page_touch_ms and decode_req_service_ms, stable mib_per_token/decode_core_upload_mib, improved decode_tok_s.
Agent hypothesis: Observed anomaly after iter_01: hit counters can move without actual byte movement; stable waste is page-touch/upload service. Verified candidate code path: Tucker sets CORE_PAGE_TOUCH_MODE=2; materializePackedExpertSlotBatchGpuV3 touches mmap pages before enqueue. Suspected wasteful behavior: explicit touch duplicates upload traversal. Guardrails: ret=0 generated=16, unchanged p16/d16 benchmark, no transfer-volume regression.
Chosen optimization direction: Skip explicit page-touch in packed expert payload materialization path by default.
Files inspected: Tucker qwen_env, examples/qwen2_moe_td_qnn_aot/aot_run.cpp materialization functions, iter_01 summary/log
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Added MLLM_QNN_TD_HYBRID_GPU_SKIP_EXPLICIT_PAGE_TOUCH default true around materializePackedExpertSlotBatchGpuV3 page touch.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/blackbox_diag_rerun_iter_02_fasttemp_p16_d16
Compile result: success; host md5 911f09f103a0869b93044598e114b6f3, phone md5 matched, phone stat size 36912960 modify 2026-07-02 20:45:16
Correctness result: ret=0 generated=16
Metrics:
  decode_tok_s: 0.32495186345880145
  mib_per_token: 
  required_miss_count: 
  upload_bytes: 
  prewarm_hit_rate: 
  eviction_churn: 
  required_miss_wait_ms_per_token: 
  decode_req_page_touch_ms: 
  decode_req_mat_enqueue_ms: 
  decode_req_mat_finish_ms: 
  decode_req_service_ms: 
  decode_req_mat_writes: 
  decode_req_page_touch_mib: 
  decode_core_upload_mib: 
  decode_req_miss: 
  decode_req_hit: 
  decode_evict: 
  cache_hit_rate: 
  peak_temp_skin_c_decode: 33.34004
Result: Correctness-passing but wrong localization/no signal: decode_tok_s=0.3249518635, uploaded_expert_mib_per_token=1431.8021875, decode_req_page_touch_ms=19345.446, decode_req_service_ms=24716.598, decode_core_upload_mib=22908.835. Metrics stayed baseline-like.
Agent diagnosis: The changed packed full-cache function was not the dominant active path under the fixed harness. The active path remains projection-level materializeCoreSlotBatchGpuV3, where page-touch counters still accumulate. Archive and target the verified active materialization function next.
My diagnosis: Wrong file/localization within the runner, not a useful speed patch. This is research evidence that diagnostic names must be mapped to the exact active function, not just nearby similarly named paths.
Needed expert knowledge: No prior solution used; existing counters and logs identified the mismatch after the run.
Patch / commit: archived patches/failed_attempts/blackbox_diag_rerun_iter_02_fasttemp_p16_d16.patch

## blackbox_diag_rerun_iter_03_fasttemp_p16_d16

Iteration ID: blackbox_diag_rerun_iter_03_fasttemp_p16_d16
Stage: blackbox_diag_rerun
Agent prompt setting: Black-box diagnostic-driven MobileMoE-AKO rerun, base context only
Baseline bottleneck decomposition: Baseline decode_tok_s=0.3253207510, uploaded_expert_mib_per_token=1431.8021875, decode_req_page_touch_ms=19629.259, decode_req_mat_enqueue_ms=5049.663, decode_req_mat_finish_ms=37.306, decode_req_service_ms=24762.132, decode_core_upload_mib=22908.835.
Targeted bottleneck: Explicit mmap page-touch in active projection-level materializeCoreSlotBatchGpuV3 path.
Expected diagnostic movement: decode_req_page_touch_ms should fall sharply; if upload absorbs page faults then enqueue/finish may rise. Useful only if total decode_req_service_ms and decode_tok_s improve while mib_per_token stays stable.
Agent hypothesis: Observed anomaly: iter_02 wrong-path edit left active counters unchanged; active decode path is runProjectionImplGpuV3 -> ensureExpertsCachedBatchGpuV3 -> materializeCoreSlotBatchGpuV3. Suspected wasteful behavior: explicit touchMmapPages in active mode 2 serializes memory traversal before upload. Guardrails: ret=0 generated=16, fixed benchmark, no transfer-volume regression.
Chosen optimization direction: Skip explicit page-touch in active projection-level packed payload upload path by default.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp, iter_02 summary/log
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Added default skip around touchMmapPages in materializeCoreSlotBatchGpuV3 mode 2.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/blackbox_diag_rerun_iter_03_fasttemp_p16_d16
Compile result: success; host md5 5ff1e91a211fe7a1cdc20e386ab65450, phone md5 matched, phone stat size 36914272 modify 2026-07-02 20:50:59
Correctness result: ret=0 generated=16
Metrics:
  decode_tok_s: 0.32399735626257226
  mib_per_token: 
  required_miss_count: 
  upload_bytes: 
  prewarm_hit_rate: 
  eviction_churn: 
  required_miss_wait_ms_per_token: 
  decode_req_page_touch_ms: 
  decode_req_mat_enqueue_ms: 
  decode_req_mat_finish_ms: 
  decode_req_service_ms: 
  decode_req_mat_writes: 
  decode_req_page_touch_mib: 
  decode_core_upload_mib: 
  decode_req_miss: 
  decode_req_hit: 
  decode_evict: 
  cache_hit_rate: 
  peak_temp_skin_c_decode: 34.28624
Result: Correctness-passing regression/no-useful patch: decode_tok_s=0.3239973563 below baseline 0.3253207510, uploaded_expert_mib_per_token unchanged at 1431.8021875. decode_req_page_touch_ms dropped to 0, but decode_req_mat_enqueue_ms rose to 16099.427 and finish to 8153.036; decode_req_service_ms stayed similar/worse at 24299.545. Overall required service worsened.
Agent diagnosis: The removed page-touch cost moved into OpenCL enqueue/finish rather than disappearing. The page-touch diagnostic was accounting where page faults happened, not standalone removable work. This rejects the page-touch-removal hypothesis.
My diagnosis: Archive and stop after three consecutive no-signal/regression/hypothesis-mismatch optimization attempts. Diagnostics independently localized transfer/cache/runtime-state as the bottleneck, but available black-box policy edits did not produce a useful speedup.
Needed expert knowledge: No prior solution used. Additional missing context: exact relationship between cache ledger entries and actual upload volume, and a safe policy that reduces materialized bytes rather than moving page-fault accounting.
Patch / commit: archived patches/failed_attempts/blackbox_diag_rerun_iter_03_fasttemp_p16_d16.patch
