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

## s6_minexpert_baseline_fasttemp_p16_d16

Iteration ID: s6_minexpert_baseline_fasttemp_p16_d16
Stage: s6_minexpert_residency_diagnostic
Agent prompt setting: Minimal expert-context ablation: only expert/core residency and eviction churn prior allowed
Baseline bottleneck decomposition: Baseline from da9fa353 rebuilt/deployed/verified: decode_tok_s=0.331595, correct ret=0 generated=16/16, MiB/token=1431.802. Decode cache counters show req_hit=3942 req_miss=6810 evict=6810 hit_rate=0.3666. Required-miss service=24053.492ms total, 1503.343ms/token; page_touch=19423.816ms; enqueue=4570.263ms; core_upload=22908.835MiB.
Targeted bottleneck: Baseline only; no code change yet
Expected diagnostic movement: N/A baseline
Agent hypothesis: Observed low decode throughput is associated with high expert/core demand misses and one eviction per miss under cache capacity 8, indicating residency churn as a plausible bottleneck for later iterations.
Chosen optimization direction: Baseline profiling and provenance capture
Files inspected: SKILL.md, references/constraints.md, references/benchmark_instructions.md, references/metrics_schema.md, target build/deploy files, Tucker runner for contract observation
Files modified: None in runtime repo; wrote results/runs/s6_minexpert_baseline_fasttemp_p16_d16/metrics.json and backed up ITERATIONS.md
Change summary: No runtime change. Preserved ITERATIONS.md, rebuilt Android runner from da9fa353, deployed to Tucker phone base, verified host/phone md5/stat, ran exact p16/d16 contract.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_minexpert_baseline_fasttemp_p16_d16
Compile result: success; forced clean/rebuild of mllm-qwen2-moe-td-qnn-aot-runner from da9fa3534a16c0f34adb6709e2ba871741cbf8cc
Correctness result: pass ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.3315952629461319
  mib_per_token: 1431.8021875
  required_miss_count: 6810.0
  upload_bytes: 24021654568.96
  prewarm_hit_rate: None
  eviction_churn: 6810.0
  required_miss_wait_ms_per_token: 1503.3432500000001
  decode_req_page_touch_ms: 19423.816000000003
  decode_req_mat_enqueue_ms: 4570.263000000003
  decode_req_mat_finish_ms: 13.94199999999998
  decode_req_service_ms: 24053.492000000002
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 30.57364
Result: Baseline valid. Host md5 6d15f401a12e515d066141c3a02ba4ea; phone md5 matched; phone stat size 36912960 mode 0777 shell:shell.
Agent diagnosis: Residency/churn counters are sufficient for a first optimization hypothesis: decode misses and evictions match at 6810, required miss upload is very large, and hit rate is low. No diagnostic-only iteration needed before first optimization.
My diagnosis: The baseline bottleneck is repeated required expert/core residency loss under the fixed cache capacity. The causal evidence is high miss/evict churn plus high normalized transfer and required-miss service. Page-touch/enqueue timing is treated only as observation within the required-miss service, not as an initial mechanism prior.
Needed expert knowledge: Only the allowed residency/eviction-churn concept was used so far. Additional knowledge may be needed if code inspection cannot explain why evictions mirror misses.
Patch / commit: baseline only; no patch

## s6_minexpert_iter_01_causal_chain

Iteration ID: s6_minexpert_iter_01_causal_chain
Stage: s6_minexpert_residency_diagnostic
Agent prompt setting: Minimal expert-context ablation: only expert/core residency and eviction churn prior allowed
Baseline bottleneck decomposition: Observed anomaly: baseline decode_tok_s=0.331595 with high normalized transfer 1431.802 MiB/token. Decode req_hit=3942 req_miss=6810 evict=6810, so every required miss also evicted a resident entry. Required-miss service=24053.492ms total, 1503.343ms/token.
Targeted bottleneck: Verified runtime code path: runColdPostGpu invokes HybridColdGpuShadowExecutor projection cache paths; ensureExpertsCachedBatchGpuV3/ensureExpertsCachedBatch count required hits/misses and call selectCacheVictim when per-projection slots are full. The hot-history threshold is read from MLLM_QNN_TD_HYBRID_GPU_HOT_RESIDENT_MIN_HITS and currently accepts 1.
Expected diagnostic movement: Residency/eviction hypothesis: treating a single prior observation as enough history makes too many candidates equally protected, so required uploads still churn entries that are likely to recur. Tightening the minimum history count should make victim selection more discriminating. Expected metric movement: lower decode_req_miss/decode_evict, lower MiB/token and required-miss service, higher decode_tok_s. Guardrails: ret=0, generated=16, no normalized transfer increase.
Agent hypothesis: A minimum history count of one over-labels entries as hot; requiring stronger reuse evidence should reduce eviction churn under capacity 8.
Chosen optimization direction: Optimization iteration 01: tighten core residency history threshold only
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; mllm/backends/opencl/moe/GpuMoePrefetchPolicy.*; mllm/backends/opencl/moe/HybridResourceManager.cpp
Files modified: Pending source edit
Change summary: Pre-edit causal chain only; runtime edit follows.
Benchmark command: Not run for causal-chain entry
Compile result: not run
Correctness result: not run
Metrics:
  decode_tok_s: 
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
  peak_temp_skin_c_decode: 
Result: Pre-edit causal chain recorded before code change.
Agent diagnosis: Counters are sufficient for this first policy test; no diagnostic-only iteration needed.
My diagnosis: The cache policy has a history signal, but the configured minimum count of one makes it too broad under the observed churn. This iteration tests whether stricter history improves residency selection without changing benchmark semantics.
Needed expert knowledge: No extra expert mechanism used beyond residency and eviction churn.
Patch / commit: pending

## s6_minexpert_iter_01_fasttemp_p16_d16

Iteration ID: s6_minexpert_iter_01_fasttemp_p16_d16
Stage: s6_minexpert_residency_diagnostic
Agent prompt setting: Minimal expert-context ablation: only expert/core residency and eviction churn prior allowed
Baseline bottleneck decomposition: Baseline decode_tok_s=0.331595, MiB/token=1431.802, req_hit=3942 req_miss=6810 evict=6810, required-miss service=1503.343ms/token.
Targeted bottleneck: Expert/core residency churn from required victim selection under cache capacity 8.
Expected diagnostic movement: Expected lower decode_req_miss, decode_evict, MiB/token, and required-miss service; expected decode_tok_s increase; correctness and generated token count stable.
Agent hypothesis: Enabling a short recent-required residency window when hot core residency is active will prevent immediate eviction of recently used required entries and reduce churn.
Chosen optimization direction: Tighten recent required-entry residency protection
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; mllm/backends/opencl/moe/GpuMoePrefetchPolicy.*; mllm/backends/opencl/moe/HybridResourceManager.cpp
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Defaulted MLLM_QNN_TD_HYBRID_GPU_RESIDENT_RECENT on when hot core residency is enabled unless explicitly overridden.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_minexpert_iter_01_fasttemp_p16_d16
Compile result: success; host md5 2361b39db0365fbedd5b93b054c6205c; phone md5 matched; phone stat size 36913120
Correctness result: pass ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.3353207795939869
  mib_per_token: 1431.8021875
  required_miss_count: 6810.0
  upload_bytes: 24021654568.96
  prewarm_hit_rate: None
  eviction_churn: 6810.0
  required_miss_wait_ms_per_token: 1473.3996249999996
  decode_req_page_touch_ms: 19209.330000000005
  decode_req_mat_enqueue_ms: 4306.779000000002
  decode_req_mat_finish_ms: 14.312000000000001
  decode_req_service_ms: 23574.393999999993
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 31.62548
Result: No-signal/hypothesis mismatch. decode_tok_s=0.335321 (+1.1%) but req_miss=6810, evict=6810, MiB/token=1431.802, and cache_hit_rate=0.3666 were unchanged. Service timing moved slightly but not the targeted residency/churn counters.
Agent diagnosis: The change did not alter the victim set or transfer volume. The recent-residency guard was either already ineffective under per-projection epoch progression/capacity pressure or all viable victims remained equivalent.
My diagnosis: The observed speed movement is timing noise because the intended diagnostic counters did not move. Archive and revert before next hypothesis.
Needed expert knowledge: Still only residency/eviction churn was used. Next iteration needs a more specific code-derived residency state invariant rather than broader recency protection.
Patch / commit: archived patches/failed_attempts/s6_minexpert_iter_01_fasttemp_p16_d16.patch; not committed

## s6_minexpert_iter_02_causal_chain

Iteration ID: s6_minexpert_iter_02_causal_chain
Stage: s6_minexpert_residency_diagnostic
Agent prompt setting: Minimal expert-context ablation: only expert/core residency and eviction churn prior allowed
Baseline bottleneck decomposition: After iteration 01, counters did not move: decode req_miss=6810 evict=6810 MiB/token=1431.802 hit_rate=0.3666. This shows generic recent-entry protection did not affect the actual residency state.
Targeted bottleneck: Verified runtime code path: runProjectionImplGpuV3 binds a shared expert/core payload arena but then uses ensureExpertsCachedBatchGpuV3 for only the current projection cache. The grouped-cache helper exists and marks gate/up/down cache maps together, but this path was not used by the runtime projection execution path.
Expected diagnostic movement: Residency/eviction hypothesis: after a grouped expert/core upload, companion cache maps must be marked resident immediately. Expected lower decode_req_miss, decode_evict, MiB/token, and required-miss service; correctness and generated token count must remain stable.
Agent hypothesis: Incomplete resident bookkeeping after grouped expert/core upload causes later companion accesses to be counted as required misses and evictions even though the payload is already present in the shared arena.
Chosen optimization direction: Optimization iteration 02: use grouped cache-state marking for external expert/core payload arena path
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp ensureExpertsCachedBatchGpuV3, ensureExpertsPackedCachedBatchGpuV3, runProjectionImplGpuV3, materializeCoreSlotBatchGpuV3
Files modified: Pending source edit
Change summary: Pre-edit causal chain only; runtime edit follows.
Benchmark command: Not run for causal-chain entry
Compile result: not run
Correctness result: not run
Metrics:
  decode_tok_s: 
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
  peak_temp_skin_c_decode: 
Result: Pre-edit causal chain recorded before code change.
Agent diagnosis: This hypothesis is code-derived from the unchanged counters in iteration 01 and the verified cache-state path.
My diagnosis: The runtime has the data movement grouping but the resident cache maps can remain incomplete, producing artificial miss/evict churn. This is a direct residency-state repair, not a benchmark or transfer-mechanism edit.
Needed expert knowledge: Only residency/eviction churn plus this experiment code inspection were used.
Patch / commit: pending

## s6_minexpert_iter_02_fasttemp_p16_d16

Iteration ID: s6_minexpert_iter_02_fasttemp_p16_d16
Stage: s6_minexpert_residency_diagnostic
Agent prompt setting: Minimal expert-context ablation: only expert/core residency and eviction churn prior allowed
Baseline bottleneck decomposition: Baseline decode_tok_s=0.331595, MiB/token=1431.802, req_miss=6810, evict=6810, required-miss service=1503.343ms/token. Iteration 01 left these unchanged.
Targeted bottleneck: Incomplete resident cache-state accounting after grouped expert/core payload upload.
Expected diagnostic movement: Expected lower decode_req_miss, decode_evict, MiB/token, and required-miss service with correctness stable.
Agent hypothesis: Marking grouped expert/core payload residency across the projection cache maps should prevent later companion accesses from becoming required misses.
Chosen optimization direction: Grouped resident cache-state marking for external expert/core payload arena path
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp ensureExpertsPackedCachedBatchGpuV3 and runProjectionImplGpuV3
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: When external payload arena base projection runs, used grouped cache-state helper; for companion projections, reused the existing entry rather than uploading again.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_minexpert_iter_02_fasttemp_p16_d16
Compile result: success; host md5 fe718d8b983947531a37c9331ec71d17; phone md5 matched; phone stat size 37183640
Correctness result: pass ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.32836255363289246
  mib_per_token: 1431.8021875
  required_miss_count: 2270.0
  upload_bytes: 24021654568.96
  prewarm_hit_rate: None
  eviction_churn: 2270.0
  required_miss_wait_ms_per_token: 1534.8158749999984
  decode_req_page_touch_ms: 19454.248000000018
  decode_req_mat_enqueue_ms: 5055.100999999994
  decode_req_mat_finish_ms: 18.39399999999995
  decode_req_service_ms: 24557.053999999975
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 2270.0
  decode_req_hit: 1314.0
  decode_evict: 2270.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 32.37712
Result: Failed/hypothesis mismatch. decode_req_miss moved 6810 -> 2270 and evict 6810 -> 2270, but normalized transfer stayed 1431.802 MiB/token, required-miss service worsened to 1534.816ms/token, and decode_tok_s regressed to 0.328363. Not eligible as best patch.
Agent diagnosis: The counter movement was mostly accounting/state-shape movement; it did not reduce actual core_upload_mib or write calls, so throughput regressed.
My diagnosis: Residency bookkeeping alone was insufficient because the grouped path still performed the same materialization volume. The minimal concept localized a relevant state issue but did not identify a profitable repair.
Needed expert knowledge: The next useful step would require knowing which residency-state changes correspond to actual transfer elimination, not just counter relabeling.
Patch / commit: archived patches/failed_attempts/s6_minexpert_iter_02_fasttemp_p16_d16.patch; not committed

## s6_minexpert_final_conclusion

Iteration ID: s6_minexpert_final_conclusion
Stage: s6_minexpert_residency_diagnostic
Agent prompt setting: Minimal expert-context ablation: only expert/core residency and eviction churn prior allowed
Baseline bottleneck decomposition: Valid baseline from da9fa3534a16c0f34adb6709e2ba871741cbf8cc showed decode_tok_s=0.331595, ret=0 generated=16/16, MiB/token=1431.8021875, decode req_hit=3942 req_miss=6810 evict=6810, hit_rate=0.366629, required service=1503.343ms/token, decode core_upload_mib=22908.835, write_calls=2270.
Targeted bottleneck: Expert/core residency and eviction churn under cache capacity 8.
Expected diagnostic movement: A useful patch needed to improve decode_tok_s while preserving correctness and not worsening normalized transfer; strongest acceptable signal would lower actual core_upload_mib or write_calls, not only relabel miss/evict counters.
Agent hypothesis: After two code-derived attempts, the allowed minimal concept localized the pressure but did not expose a safe runtime-policy repair that reduces actual materialized bytes.
Chosen optimization direction: Stop early with no-useful-patch conclusion rather than run a speculative third optimization.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; current experiment metrics/summary files for baseline, iter01, iter02; archived failed patches.
Files modified: ITERATIONS.md only for this conclusion entry. Runtime repo unchanged and clean.
Change summary: No code change. Closed the ablation after two correctness-passing but no-useful-signal/regression attempts.
Benchmark command: No additional benchmark. p32/d32 recheck not run because no correctness-passing useful patch existed.
Compile result: N/A for conclusion; last runtime repo status clean on exp/s6-minexpert-residency-diagnostic at da9fa353.
Correctness result: Baseline, iter01, and iter02 all passed ret=0 generated=16/16; no final patch selected.
Metrics:
  baseline_decode_tok_s: 0.3315952629461319
  baseline_mib_per_token: 1431.8021875
  baseline_decode_core_upload_mib: 22908.835
  baseline_decode_req_mat_writes: 2270
  iter01_decode_tok_s: 0.3353207795939869
  iter01_mib_per_token: 1431.8021875
  iter01_decode_core_upload_mib: 22908.835
  iter01_decode_req_mat_writes: 2270
  iter02_decode_tok_s: 0.32836255363289246
  iter02_mib_per_token: 1431.8021875
  iter02_decode_core_upload_mib: 22908.835
  iter02_decode_req_mat_writes: 2270
Result: No useful patch. Iter01 had unchanged residency/transfer counters, so the small speed increase was not accepted as causal. Iter02 reduced logical req_miss/evict counters but kept actual upload volume and write count unchanged and regressed decode_tok_s. No p32/d32 recheck was run.
Agent diagnosis: The minimal residency/eviction-churn concept was sufficient to localize the bottleneck class and reject accounting-only changes, but insufficient to identify a profitable repair. Existing diagnostics showed actual transfer volume remained fixed at 22908.835 MiB and 2270 decode write calls across both attempts.
My diagnosis: Additional expert knowledge or diagnostics were missing about which resident cache states correspond to real transfer elimination under the packed/external payload arena path. The experiment should report that residency/churn alone was not sufficient for a coding agent to repair this whole-system bottleneck under the allowed context.
Needed expert knowledge: A mechanism-level understanding of actual payload grouping/materialization and how cache ledger entries map to physical uploads would be needed; this was not used as an initial prior in this ablation.
Patch / commit: No commit. Failed patches archived at patches/failed_attempts/s6_minexpert_iter_01_fasttemp_p16_d16.patch and patches/failed_attempts/s6_minexpert_iter_02_fasttemp_p16_d16.patch.

## s6_ablation_c_baseline_fasttemp_p16_d16

Iteration ID: s6_ablation_c_baseline_fasttemp_p16_d16
Stage: s6_ablation_c_transfer_guardrail
Agent prompt setting: minimal expert context: core residency/eviction churn plus physical-transfer guardrail
Baseline bottleneck decomposition: Correct baseline from clean base da9fa3534; decode_tok_s=0.331361683, generated=16, MiB/token=1431.8021875, decode_req_miss=6810, decode_req_hit=3942, decode_evict=6810, decode_req_service_ms=23274.682, decode_core_upload_mib=22908.835, decode_req_mat_writes=2270, peak decode skin=32.862C.
Targeted bottleneck: Baseline profiling only before source edits: required miss/eviction churn with large physical core upload and materialization work.
Expected diagnostic movement: Future useful patches must reduce or at least move physical transfer/service signals in expected direction: MiB/token, decode_core_upload_mib, decode_req_mat_writes, or required-miss service.
Agent hypothesis: Baseline measurement establishes high required miss and eviction churn under cache capacity 8; accounting-only counter changes are insufficient for this ablation.
Chosen optimization direction: No optimization yet; establish clean provenance and allowed profiling report.
Files inspected: SKILL.md; references/constraints.md; references/benchmark_instructions.md; references/metrics_schema.md; Tucker runner only to identify fixed phone-base and binary name; baseline summary/log.
Files modified: None in runtime; created results/runs/s6_ablation_c_baseline_fasttemp_p16_d16/metrics.json and copied ITERATIONS backup before baseline.
Change summary: Fresh base runner rebuilt and deployed from da9fa3534; no source edits.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_ablation_c_baseline_fasttemp_p16_d16
Compile result: fresh build succeeded; host md5 6d15f401a12e515d066141c3a02ba4ea
Correctness result: ret=0 generated=16/16; phone md5 matched host; phone stat size=36912960 mode=0777
Metrics:
  decode_tok_s: 0.3313616829959288
  mib_per_token: 1431.8021875
  required_miss_count: 6810.0
  upload_bytes: 24021654568.96
  prewarm_hit_rate: None
  eviction_churn: 6810.0
  required_miss_wait_ms_per_token: 1454.6676250000005
  decode_req_page_touch_ms: 18629.398000000005
  decode_req_mat_enqueue_ms: 4589.121000000001
  decode_req_mat_finish_ms: 13.723999999999998
  decode_req_service_ms: 23274.682000000008
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 32.862
Result: Valid baseline. Physical-transfer guardrail exposes large decode transfer/service cost rather than accepting cache counters alone.
Agent diagnosis: Required misses and evictions are equal in decode, and misses are dominated by physical core materialization/upload: 22908.835 MiB core upload, 2270 materialization writes, 23274.682 ms service.
My diagnosis: The first optimization must target real residency/cache-state behavior that reduces physical movement or service work, not merely relabeling logical hit/miss counters.
Needed expert knowledge: Only allowed prior used: core residency/eviction churn plus transfer guardrail. Missing: detailed mechanism explaining why repeated required misses persist under current residency state.
Patch / commit: baseline only; no runtime patch

## s6_ablation_c_iter_01_prechange

Iteration ID: s6_ablation_c_iter_01_prechange
Stage: s6_ablation_c_transfer_guardrail
Agent prompt setting: minimal expert context: core residency/eviction churn plus physical-transfer guardrail
Baseline bottleneck decomposition: Baseline decode has required miss/evict churn: req_miss=6810, evict=6810, MiB/token=1431.8021875, decode_core_upload_mib=22908.835, req_mat_writes=2270, req_service_ms=23274.682.
Targeted bottleneck: Runtime cache-state consistency for required expert-core residency under shared expert-payload arena.
Expected diagnostic movement: Expected: decode_req_miss and decode_evict decrease only if the residency state is made consistent; physical guardrail requires lower or stable MiB/token, lower decode_core_upload_mib, fewer req_mat_writes, or lower required service.
Agent hypothesis: Observed anomaly: repeated required miss/evict churn coincides with high physical core upload. Verified runtime code path: ensureExpertsPackedCachedBatchGpuV3 uploads one expert-payload object into a shared device arena and then records multiple logical entries derived from that upload; eviction erases those logical entries as a coupled set. Physical-transfer guardrail: accept only if upload/service/write counters move in the expected direction. Expected metric movement: fewer required misses/evicts, lower core upload MiB and materialization writes, improved decode_tok_s. Guardrails that must remain stable: ret=0, generated=16, unchanged p16/d16 contract, no MiB/token regression.
Chosen optimization direction: Keep logical residency state coupled to the physical expert-payload upload so future required probes do not force avoidable re-materialization.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp around HybridColdGpuShadowExecutor, expert-payload arena binding, required miss materialization, and packed required cache path; GpuMoePrefetchPolicy.cpp.
Files modified: pending
Change summary: pre-change causal chain only
Benchmark command: pending
Compile result: pending
Correctness result: pending
Metrics:
  decode_tok_s: 
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
  peak_temp_skin_c_decode: 
Result: pre-change log
Agent diagnosis: Existing counters are sufficient; no diagnostic-only iteration needed before iter_01.
My diagnosis: The physical-transfer guardrail points away from accounting-only counter edits and toward the upload/materialization path where cache-state consistency can reduce actual writes.
Needed expert knowledge: Still minimal: no external hints used; code inspection supplied the concrete coupling issue.
Patch / commit: pending

## s6_ablation_c_iter_01_fasttemp_p16_d16

Iteration ID: s6_ablation_c_iter_01_fasttemp_p16_d16
Stage: s6_ablation_c_transfer_guardrail
Agent prompt setting: minimal expert context: core residency/eviction churn plus physical-transfer guardrail
Baseline bottleneck decomposition: Baseline: decode_tok_s=0.331361683, MiB/token=1431.8021875, decode_req_miss=6810, decode_evict=6810, decode_core_upload_mib=22908.835, req_mat_writes=2270, req_service_ms=23274.682.
Targeted bottleneck: Runtime cache-state consistency for required expert-core residency under shared expert-payload arena.
Expected diagnostic movement: Expected cache hits to increase only if physical movement also decreased: lower MiB/token/core_upload_mib/req_mat_writes/service and improved decode_tok_s.
Agent hypothesis: Observed anomaly: required miss/evict churn plus high physical core upload. Verified path: required GpuV3 expert payload materialization and cache entries in a shared payload arena. Physical-transfer guardrail: reject logical hit improvements unless upload/service moves.
Chosen optimization direction: Route external expert-payload arena required path through packed cache helper to couple logical entries to the physical expert payload.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; GpuMoePrefetchPolicy.cpp
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Used ensureExpertsPackedCachedBatchGpuV3 for external expert payload arena path instead of per-projection ensureExpertsCachedBatchGpuV3.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_ablation_c_iter_01_fasttemp_p16_d16
Compile result: build succeeded; host md5 cfae825ef1f6388c14cd840e9f08b5a7
Correctness result: ret=0 generated=16/16; phone md5 matched host; phone stat size=37175912 mode=0777
Metrics:
  decode_tok_s: 0.27871529667936856
  mib_per_token: 1431.8021875
  required_miss_count: 2270.0
  upload_bytes: 24021654568.96
  prewarm_hit_rate: None
  eviction_churn: 2270.0
  required_miss_wait_ms_per_token: 1946.3956875000006
  decode_req_page_touch_ms: 20811.482999999982
  decode_req_mat_enqueue_ms: 10269.243999999979
  decode_req_mat_finish_ms: 32.40399999999985
  decode_req_service_ms: 31142.33100000001
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 2270.0
  decode_req_hit: 8482.0
  decode_evict: 2270.0
  cache_hit_rate: 0.7888764880952381
  peak_temp_skin_c_decode: 35.40648
Result: Failed physical-transfer guardrail. Correctness passed and logical cache counters improved, but decode speed regressed and normalized transfer/core upload did not decrease.
Agent diagnosis: decode_req_miss improved 6810->2270 and hit rate 0.3666->0.7889, but MiB/token remained 1431.8021875, decode_core_upload_mib remained 22908.835, req_mat_writes stayed 2270, service worsened 23274.682->31142.331 ms, decode_tok_s fell to 0.278715.
My diagnosis: This is the accounting-only failure mode the ablation guardrail was designed to catch: cache counters got better without reducing physical transfer or service work.
Needed expert knowledge: Need deeper mechanism for reducing actual physical payload movement, not only reconciling logical entries.
Patch / commit: archived failed patch: patches/failed_attempts/s6_ablation_c_iter_01_fasttemp_p16_d16.patch

## s6_ablation_c_iter_02_prechange

Iteration ID: s6_ablation_c_iter_02_prechange
Stage: s6_ablation_c_transfer_guardrail
Agent prompt setting: minimal expert context: core residency/eviction churn plus physical-transfer guardrail
Baseline bottleneck decomposition: Baseline and iter_01 show physical transfer unchanged at MiB/token=1431.8021875 and decode_core_upload_mib=22908.835; iter_01 logical hits improved but service worsened, so counters alone are rejected.
Targeted bottleneck: Required-miss materialization service on the physical upload path: req_mat_enqueue_ms and req_service_ms dominate while writes/bytes remain honest.
Expected diagnostic movement: Expected: lower decode_req_mat_enqueue_ms and decode_req_service_ms, stable or lower decode_req_mat_writes and decode_core_upload_mib, decode_tok_s improves; correctness and generated tokens stable.
Agent hypothesis: Observed anomaly: the failed iter_01 improved logical hit counters but kept physical bytes/writes unchanged and worsened service. Verified runtime code path: materializePackedExpertSlotBatchGpuV3 interleaved path touches each mmap payload and immediately enqueues one span at a time before a final finish. Physical-transfer guardrail: accept only if service timing or write/byte counters move in the expected direction with no MiB/token regression. Expected metric movement: req_mat_enqueue_ms/service decrease; core_upload_mib unchanged or lower; decode_tok_s up. Guardrails that must remain stable: ret=0, generated=16, unchanged p16/d16 contract.
Chosen optimization direction: Batch the physical upload spans after page-touch within the existing required materialization path, reducing upload service overhead without changing model work or transfer accounting.
Files inspected: HybridOpenCLMaterializer.cpp/.hpp; examples/qwen2_moe_td_qnn_aot/aot_run.cpp materializePackedExpertSlotBatchGpuV3 and required batch paths.
Files modified: pending
Change summary: pre-change causal chain only
Benchmark command: pending
Compile result: pending
Correctness result: pending
Metrics:
  decode_tok_s: 
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
  peak_temp_skin_c_decode: 
Result: pre-change log
Agent diagnosis: iter_02 targets a physical service counter after the transfer guardrail rejected a logical-only iter_01.
My diagnosis: Existing diagnostics are sufficient to justify a materialization-service attempt; no parser or benchmark changes needed.
Needed expert knowledge: Could use deeper OpenCL transfer behavior knowledge, but this hypothesis is derived from current code and counters.
Patch / commit: pending

## s6_ablation_c_iter_02_fasttemp_p16_d16

Iteration ID: s6_ablation_c_iter_02_fasttemp_p16_d16
Stage: s6_ablation_c_transfer_guardrail
Agent prompt setting: minimal expert context: core residency/eviction churn plus physical-transfer guardrail
Baseline bottleneck decomposition: Baseline: decode_tok_s=0.331361683, MiB/token=1431.8021875, decode_req_miss=6810, decode_evict=6810, decode_core_upload_mib=22908.835, req_mat_writes=2270, req_mat_enqueue_ms=4589.121, req_service_ms=23274.682.
Targeted bottleneck: Required-miss physical materialization service.
Expected diagnostic movement: Expected lower req_mat_enqueue_ms/service and improved decode_tok_s, with transfer bytes still accounted.
Agent hypothesis: After iter_01 showed logical-only improvement, iter_02 targeted physical upload service by batching device upload spans after page-touch in materializePackedExpertSlotBatchGpuV3.
Chosen optimization direction: Batch physical upload spans within the required expert payload materialization loop.
Files inspected: HybridOpenCLMaterializer.cpp/.hpp; examples/qwen2_moe_td_qnn_aot/aot_run.cpp materialization paths.
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Collected DeviceUploadSpan entries after touching mmap pages and called uploadDeviceSpans once per chunk instead of enqueueing each span and finishing separately.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_ablation_c_iter_02_fasttemp_p16_d16
Compile result: build succeeded; host md5 d97012e5555228b53e68add3df28d7cf
Correctness result: ret=0 generated=16/16; phone md5 matched host; phone stat size=36912944 mode=0777
Metrics:
  decode_tok_s: 0.32287193944391485
  mib_per_token: 1431.8021875
  required_miss_count: 6810.0
  upload_bytes: 24021654568.96
  prewarm_hit_rate: None
  eviction_churn: 6810.0
  required_miss_wait_ms_per_token: 1540.6688124999991
  decode_req_page_touch_ms: 19232.496999999996
  decode_req_mat_enqueue_ms: 5355.3809999999985
  decode_req_mat_finish_ms: 20.224999999999977
  decode_req_service_ms: 24650.700999999986
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 35.8564
Result: Failed/no-speedup. Correctness passed and transfer accounting remained visible, but decode_tok_s regressed and physical service counters did not improve.
Agent diagnosis: decode_tok_s=0.322872 below baseline 0.331362. MiB/token and core_upload_mib unchanged. decode_req_miss/evict unchanged. req_mat_enqueue_ms worsened 4589.121->5355.381, req_service_ms worsened 23274.682->24650.701, req_mat_writes unchanged 2270.
My diagnosis: The physical-transfer guardrail rejected this too: it touched the physical path but did not reduce physical movement or service enough to be useful.
Needed expert knowledge: Need a mechanism that reduces actual required-miss service or bytes, not just rearranges upload calls.
Patch / commit: archived failed patch: patches/failed_attempts/s6_ablation_c_iter_02_fasttemp_p16_d16.patch

## s6_ablation_c_final_no_useful_patch

Iteration ID: s6_ablation_c_final_no_useful_patch
Stage: s6_ablation_c_transfer_guardrail
Agent prompt setting: minimal expert context: core residency/eviction churn plus physical-transfer guardrail
Baseline bottleneck decomposition: Baseline valid from da9fa3534: decode_tok_s=0.331361683, MiB/token=1431.8021875, decode_req_miss=6810, decode_evict=6810, decode_core_upload_mib=22908.835, req_mat_writes=2270, req_service_ms=23274.682.
Targeted bottleneck: Experiment closure after two failed attempts.
Expected diagnostic movement: Useful patch required decode_tok_s improvement plus stable/lower normalized transfer and at least one physical-transfer/service signal moving in expected direction.
Agent hypothesis: Physical-transfer guardrail prevented accepting iter_01 logical cache-counter improvement and iter_02 physical-path rearrangement without speed/transfer benefit.
Chosen optimization direction: Stop without useful patch; no p32/d32 recheck because no correctness-passing patch improved decode_tok_s under guardrails.
Files inspected: Runtime repo /home/liuxu/projects/mllm; allowed references; benchmark summaries for baseline, iter_01, iter_02.
Files modified: No runtime files remain modified; ITERATIONS.md appended; failed patches archived.
Change summary: Final experiment closure: runtime tree clean at base commit; no useful patch selected.
Benchmark command: No additional benchmark; p32/d32 skipped because no best patch.
Compile result: No final build needed; last useful state is clean base da9fa3534
Correctness result: Baseline and both attempts correct, but attempts rejected by performance/physical-transfer guardrails
Metrics:
  decode_tok_s: 
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
  peak_temp_skin_c_decode: 
Result: No useful patch found within justified attempts. Stop early after repeated hypothesis/guardrail mismatch rather than running weak extra iterations.
Agent diagnosis: iter_01: logical req_miss/hit improved but physical MiB/token/core upload unchanged and service/speed worsened. iter_02: physical upload batching did not improve service or speed; transfer unchanged.
My diagnosis: The physical-transfer guardrail was sufficient to catch accounting-only fixes. It was not sufficient to derive the real transfer-reducing mechanism from minimal residency/eviction context alone.
Needed expert knowledge: Additional mechanism-level knowledge or diagnostics are needed to explain how to reduce actual core upload/service under fixed cache capacity, beyond knowing residency/eviction churn and transfer counters.
Patch / commit: no commit; failed patches archived under patches/failed_attempts/s6_ablation_c_iter_01_fasttemp_p16_d16.patch and s6_ablation_c_iter_02_fasttemp_p16_d16.patch

## s6_ablation_d_baseline_fasttemp_p16_d16

Iteration ID: s6_ablation_d_baseline_fasttemp_p16_d16
Stage: s6_ablation_d
Agent prompt setting: Minimal expert context: residency/eviction churn plus logical-vs-physical residency distinction
Baseline bottleneck decomposition: Base da9fa3534a16c0f34adb6709e2ba871741cbf8cc; branch exp/s6-ablation-d-logical-physical-residency; host md5 6d15f401a12e515d066141c3a02ba4ea and phone md5 matched; phone stat size=36912960 mode=0777; decode_tok_s=0.3319027426; ret=0 generated=16; mib_per_token=1431.8021875; decode_req_miss=6810; decode_req_hit=3942; decode_evict=6810; decode_core_upload_mib=22908.835; decode_req_service_ms=23318.037; page_touch_ms=18385.344; enqueue_ms=4873.325; finish_ms=14.653; peak_skin_decode=33.84468C.
Targeted bottleneck: Baseline/profiling only; required-miss physical upload and eviction churn identified before any source edit.
Expected diagnostic movement: Future useful patch must move physical transfer or required-miss service, not just hit/miss accounting.
Agent hypothesis: Existing metrics are sufficient to distinguish logical cache counters from physical core upload; no diagnostic-only iteration needed before first optimization attempt.
Chosen optimization direction: Inspect required expert-core residency bookkeeping controlling whether actual device upload is skipped.
Files inspected: SKILL.md; references/constraints.md; references/benchmark_instructions.md; references/metrics_schema.md; Tucker runner parse path; examples/qwen2_moe_td_qnn_aot/aot_run.cpp required-cache path; baseline summary/log.
Files modified: results/runs/s6_ablation_d_baseline_fasttemp_p16_d16/metrics.json; ITERATIONS.md only.
Change summary: Backed up prior ITERATIONS.md, rebuilt/deployed verified base runner, ran valid p16/d16 baseline, generated metrics.json.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_ablation_d_baseline_fasttemp_p16_d16
Compile result: success; rebuilt Android runner from exact base
Correctness result: ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.33190274262230507
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1457.3773124999989
  decode_req_page_touch_ms: 18385.344
  decode_req_mat_enqueue_ms: 4873.324999999997
  decode_req_mat_finish_ms: 14.653
  decode_req_service_ms: 23318.036999999982
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 33.84468
Result: Valid baseline established.
Agent diagnosis: High physical transfer and required-miss service coincide with high logical miss/evict churn; logical counters and physical movement are both visible in existing metrics.
My diagnosis: Baseline supports a residency/cache-state investigation. The first useful patch must reduce real device upload or required-miss service, not only improve counters.
Needed expert knowledge: No extra expert knowledge used beyond allowed core residency/eviction churn and logical-vs-physical residency distinction.
Patch / commit: none; baseline only

## s6_ablation_d_iter_01_fasttemp_p16_d16

Iteration ID: s6_ablation_d_iter_01_fasttemp_p16_d16
Stage: s6_ablation_d
Agent prompt setting: Minimal expert context: residency/eviction churn plus logical-vs-physical residency distinction
Baseline bottleneck decomposition: Baseline decode_tok_s=0.3319027426; mib_per_token=1431.8021875; decode_req_miss=6810; decode_evict=6810; decode_core_upload_mib=22908.835; decode_req_service_ms=23318.037.
Targeted bottleneck: Required-miss logical residency for shared device-side expert payload slots.
Expected diagnostic movement: Expected real reduction in decode_req_miss/decode_evict plus lower decode_core_upload_mib, mib_per_token, page_touch_ms, req_service_ms, and higher decode_tok_s.
Agent hypothesis: When a required upload establishes a physical expert payload slot, all logical runtime views reading that slot must be marked consistently so later required probes skip upload.
Chosen optimization direction: Route shared expert-payload device-buffer case through the packed shared-slot required-cache path.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp getProjectionCacheGpuV3, bindExpertPayloadArenaNoLock, ensureExpertsCachedBatchGpuV3, ensureExpertsPackedCachedBatchGpuV3, runProjectionImplGpuV3; baseline summary/log.
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; results/runs/s6_ablation_d_iter_01_fasttemp_p16_d16/metrics.json; ITERATIONS.md; patches/failed_attempts/s6_ablation_d_iter_01_fasttemp_p16_d16.patch.
Change summary: For external shared payload arena, use ensureExpertsPackedCachedBatchGpuV3 so logical entries are created together for the shared physical expert slot.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_ablation_d_iter_01_fasttemp_p16_d16
Compile result: success; host md5 6406a8f9ce372eaf555627053ed22947; phone md5 matched; phone stat size=37175736 mode=0777
Correctness result: ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.3324583307117609
  mib_per_token: 1431.8021875
  required_miss_count: 4912.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 4688.0
  required_miss_wait_ms_per_token: 1458.248437500001
  decode_req_page_touch_ms: 18589.38600000001
  decode_req_mat_enqueue_ms: 4697.7620000000015
  decode_req_mat_finish_ms: 16.95899999999998
  decode_req_service_ms: 23331.975000000017
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 2270.0
  decode_req_hit: 8482.0
  decode_evict: 2270.0
  cache_hit_rate: 0.7888764880952381
  peak_temp_skin_c_decode: 34.95656
Result: Archived as hypothesis mismatch/no physical-transfer improvement. decode_tok_s=0.3324583307 (+0.17%); correct, but mib_per_token stayed 1431.8021875 and decode_core_upload_mib stayed 22908.835. Logical req_miss fell 6810->2270 and hit rate rose 0.3666->0.7889, but required service was flat/slightly worse 23318.037->23331.975 ms.
Agent diagnosis: The patch improved logical bookkeeping but did not reduce physical upload/service. It is not a useful repair under the logical-vs-physical rule.
My diagnosis: The active counters show a distinction between logical residency accounting and physical movement: fewer logical misses/evictions alone did not reduce the transfer metric or service time. Next hypothesis must target the code that decides/counts/executes actual device upload, not only cache-entry presence.
Needed expert knowledge: Allowed logical-vs-physical residency distinction was sufficient to reject this patch; additional knowledge is needed to identify why the physical upload path remains unchanged.
Patch / commit: patches/failed_attempts/s6_ablation_d_iter_01_fasttemp_p16_d16.patch

## s6_ablation_d_iter_02_fasttemp_p16_d16

Iteration ID: s6_ablation_d_iter_02_fasttemp_p16_d16
Stage: s6_ablation_d
Agent prompt setting: Minimal expert context: residency/eviction churn plus logical-vs-physical residency distinction
Baseline bottleneck decomposition: Baseline decode_tok_s=0.3319027426; mib_per_token=1431.8021875; decode_req_miss=6810; decode_evict=6810; decode_core_upload_mib=22908.835; decode_req_service_ms=23318.037.
Targeted bottleneck: Async prewarm completion visibility before required-miss service.
Expected diagnostic movement: If physical prewarm uploads complete before required service but are not reaped in time, pre-required reap should reduce decode_req_miss, decode_core_upload_mib, mib_per_token, and req_service_ms.
Agent hypothesis: Completed async core prewarm may be physically present but not logically visible until after required routing; reaping before fillRoutingFromHidden should let the required path hit and skip upload.
Chosen optimization direction: Move a nonblocking async core prewarm reap before required routing.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp submitAsyncPrewarmHybridColdGpuLayer, fillRoutingWithBandwidthPriority, fillHybridColdDeltaSync, runProjectionImplGpuV3, required materialize path; baseline and iter_01 metrics.
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; results/runs/s6_ablation_d_iter_02_fasttemp_p16_d16/metrics.json; ITERATIONS.md; patches/failed_attempts/s6_ablation_d_iter_02_fasttemp_p16_d16.patch.
Change summary: Added a nonblocking gpu->reapAsync(false) immediately before fillRoutingFromHidden.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_ablation_d_iter_02_fasttemp_p16_d16
Compile result: success; host md5 e5747e00b6ff617f71ba4431817df515; phone md5 matched; phone stat size=36914224 mode=0777
Correctness result: ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.3236469378438281
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1538.5041875000006
  decode_req_page_touch_ms: 19010.557999999994
  decode_req_mat_enqueue_ms: 5537.940000000005
  decode_req_mat_finish_ms: 26.261999999999848
  decode_req_service_ms: 24616.06700000001
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 35.7728
Result: Archived as regression/no-signal. decode_tok_s=0.3236469378 (-2.49%); correct, but mib_per_token stayed 1431.8021875, decode_core_upload_mib stayed 22908.835, req_miss stayed 6810, and req_service worsened 23318.037->24616.067 ms.
Agent diagnosis: Pre-required reap did not make physical prewarm residency useful for this contract. It added timing/log overhead and/or ran too late without changing logical or physical residency.
My diagnosis: The physical upload path still executed baseline-like writes. The hypothesis that prewarm completion was merely unreaped before required service is not supported.
Needed expert knowledge: Allowed logical-vs-physical distinction helped reject the attempt; missing knowledge is the exact physical resource granularity that controls upload byte accounting.
Patch / commit: patches/failed_attempts/s6_ablation_d_iter_02_fasttemp_p16_d16.patch

## s6_ablation_d_final_summary

Iteration ID: s6_ablation_d_final_summary
Stage: s6_ablation_d
Agent prompt setting: Minimal expert context: residency/eviction churn plus logical-vs-physical residency distinction
Baseline bottleneck decomposition: Valid baseline from base da9fa3534a16c0f34adb6709e2ba871741cbf8cc: decode_tok_s=0.3319027426; mib_per_token=1431.8021875; decode_core_upload_mib=22908.835; decode_req_miss=6810; decode_evict=6810; decode_req_service_ms=23318.037; correct ret=0 generated=16.
Targeted bottleneck: Physical expert/core transfer under required-miss service.
Expected diagnostic movement: Useful patch required decode_tok_s improvement with stable/lower mib_per_token and actual movement in decode_core_upload_mib or decode_req_service_ms.
Agent hypothesis: The logical-vs-physical distinction can help reject bookkeeping-only changes, but this minimal context did not reveal a verified code change that reduces real device upload.
Chosen optimization direction: Stop early with no useful patch after two justified attempts: one logical-only hypothesis mismatch and one physical-handoff regression/no-signal.
Files inspected: Allowed references; runtime repo /home/liuxu/projects/mllm; aot_run.cpp required-cache, physical upload, async prewarm/reap, and summary metric paths; this experiment baseline/iter_01/iter_02 artifacts.
Files modified: No runtime files remain modified; ITERATIONS.md appended; metrics JSON files written; failed patch archives written.
Change summary: No useful runtime patch selected; runtime repo returned to clean base state. p32/d32 recheck skipped because there is no best correctness-passing patch that improves the primary metric under transfer guardrails.
Benchmark command: No additional benchmark; p32/d32 recheck skipped.
Compile result: No final build required; baseline and both attempts built/deployed/md5-verified before benchmarking.
Correctness result: Baseline, iter_01, and iter_02 all ret=0 generated=16/16; iter_01 and iter_02 rejected by guardrails.
Metrics:
  decode_tok_s: 
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
  peak_temp_skin_c_decode: 
Result: No-useful-patch conclusion for S6-Ablation-D. iter_01 improved logical hit/miss/evict counters but physical upload and required service did not improve. iter_02 did not move hit/miss or transfer and regressed decode_tok_s.
Agent diagnosis: Allowed logical-vs-physical residency context was sufficient to identify and reject accounting-only repair behavior. It was insufficient to find a real transfer-reducing repair from this minimal context alone.
My diagnosis: The decisive boundary is that logical state movement did not imply lower decode_core_upload_mib or mib_per_token. Additional mechanism-level knowledge or targeted diagnostics about the physical upload granularity/resource aliasing would be needed before another optimization attempt is justified.
Needed expert knowledge: Missing: exact mapping between runtime logical cache entries, shared device-side payload resources, and byte-accounted upload spans; current metrics expose the mismatch but not the repair mechanism.
Patch / commit: no commit; failed patches archived under patches/failed_attempts/s6_ablation_d_iter_01_fasttemp_p16_d16.patch and s6_ablation_d_iter_02_fasttemp_p16_d16.patch

## s6_ablation_e_baseline_fasttemp_p16_d16

Iteration ID: s6_ablation_e_baseline_fasttemp_p16_d16
Stage: s6_ablation_e
Agent prompt setting: Minimal expert-context ablation E: physical payload may map to multiple logical runtime cache entries; no prior S6 fix material read
Baseline bottleneck decomposition: Correct baseline from da9fa3534a16c0f34adb6709e2ba871741cbf8cc; decode_tok_s=0.329312, generated=16, ret=0. Decode required-miss service dominates: req_service_ms=24060.511, page_touch_ms=18724.170, enqueue_ms=5281.115, req_miss=6810, req_hit=3942, evict=6810 decode / 14064 overall, mib_per_token=1431.802, peak_skin_decode=34.966C.
Targeted bottleneck: baseline measurement only
Expected diagnostic movement: none; establishes provenance and profiling report
Agent hypothesis: Baseline should reproduce high miss/evict churn and high normalized transfer under fixed p16/d16 contract before code edits.
Chosen optimization direction: baseline-provenance-and-profiling
Files inspected: SKILL.md; references/constraints.md; references/benchmark_instructions.md; references/metrics_schema.md; Tucker Qwen2 TD runner; qwen2_moe_td_qnn_aot CMake target
Files modified: none
Change summary: Built and deployed clean-base runner only; no source edits.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_ablation_e_baseline_fasttemp_p16_d16
Compile result: build ok; host md5 6d15f401a12e515d066141c3a02ba4ea; phone md5 6d15f401a12e515d066141c3a02ba4ea; phone stat size 36912960 mode 0777 modify 2026-07-03 02:01:02 +0800
Correctness result: ret=0; generated=16/16
Metrics:
  decode_tok_s: 0.3293120286837363
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1503.7819375000006
  decode_req_page_touch_ms: 18724.169999999995
  decode_req_mat_enqueue_ms: 5281.115
  decode_req_mat_finish_ms: 12.277999999999993
  decode_req_service_ms: 24060.51100000001
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 34.96568
Result: valid baseline
Agent diagnosis: The allowed counters show high required misses and evictions with large decode core upload volume; existing metrics are sufficient to inspect residency/cache bookkeeping before adding diagnostic-only counters.
My diagnosis: Miss/evict churn and zero resident_skip suggest logical residency state is not preventing repeated uploads for entries whose physical payload may already be present, but this must be verified in runtime code before naming a concrete mechanism.
Needed expert knowledge: The abstract physical-payload/logical-entry mapping concept is enough to motivate inspecting whether logical cache keys and uploaded device resources are one-to-one or many-to-one; no additional mechanism-level prior used.
Patch / commit: none; baseline only

## s6_ablation_e_iter_01_fasttemp_p16_d16

Iteration ID: s6_ablation_e_iter_01_fasttemp_p16_d16
Stage: s6_ablation_e
Agent prompt setting: Minimal expert-context ablation E: physical payload may map to multiple logical runtime cache entries; no prior S6 fix material read
Baseline bottleneck decomposition: Baseline decode_tok_s=0.329312, mib_per_token=1431.802, decode req_miss=6810, req_hit=3942, decode_evict=6810, req_service_ms=24060.511, page_touch_ms=18724.170, enqueue_ms=5281.115.
Targeted bottleneck: Logical residency bookkeeping for multiple cache entries backed by one physical expert-payload arena/resource.
Expected diagnostic movement: Lower required misses/evictions or higher resident-skip/hit behavior; lower required-miss service and lower or unchanged MiB/token.
Agent hypothesis: Observed anomaly: high miss/evict churn and transfer. Verified runtime code path: full expert-payload materialization inserts gate/up/down logical cache entries while the scheduler records only the physical payload key. Physical/logical mapping hypothesis: make companion logical entries share the same physical resource key so eviction and residency checks follow physical payload lifetime. Guardrails: ret=0, generated=16, unchanged p16/d16 contract.
Chosen optimization direction: physical-payload-key-aliasing-for-logical-cache-entries
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; mllm/backends/opencl/moe/HybridResourceManager.{hpp,cpp}
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Changed full expert-payload cache bookkeeping so up/down logical cache entries use the same resource key as the physical payload entry rather than derived suffix keys.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_ablation_e_iter_01_fasttemp_p16_d16
Compile result: build ok; host md5 7a73704051ef16d7b6821640c297a598; phone md5 7a73704051ef16d7b6821640c297a598; phone stat size 36912960 mode 0777 modify 2026-07-03 02:07:23 +0800
Correctness result: ret=0; generated=16/16
Metrics:
  decode_tok_s: 0.33652410769318297
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1488.1978749999992
  decode_req_page_touch_ms: 18687.207999999995
  decode_req_mat_enqueue_ms: 5061.713999999997
  decode_req_mat_finish_ms: 19.61699999999993
  decode_req_service_ms: 23811.165999999987
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 35.86172
Result: correct but no useful diagnostic movement; speedup 1.0219x is below the 3 percent signal threshold and target cache/transfer counters are unchanged
Agent diagnosis: The physical/logical resource-key alias alone did not change cache hit/miss/evict or transfer volume. The small decode_tok_s improvement appears timing noise or incidental lower service time, not evidence that this bookkeeping path controlled the observed churn.
My diagnosis: This verified one many-to-one mapping site, but the changed resource key is not the controlling state for the repeated required uploads in this path. The next hypothesis should inspect the actual cache-entry population/eviction semantics around full payload slots, not only scheduler resource keys.
Needed expert knowledge: The abstract physical-payload/logical-entry concept was sufficient to find a plausible aliasing patch, but not sufficient to identify the controlling residency state from metrics alone.
Patch / commit: /home/liuxu/projects/mobile-moe-ako/patches/failed_attempts/s6_ablation_e_iter_01_fasttemp_p16_d16.patch

## s6_ablation_e_iter_02_fasttemp_p16_d16

Iteration ID: s6_ablation_e_iter_02_fasttemp_p16_d16
Stage: s6_ablation_e
Agent prompt setting: Minimal expert-context ablation E: physical payload may map to multiple logical runtime cache entries; no prior S6 fix material read
Baseline bottleneck decomposition: Baseline decode_tok_s=0.329312, mib_per_token=1431.802, decode req_miss=6810, req_hit=3942, decode_evict=6810, req_service_ms=24060.511. Iter01 showed resource-key aliasing alone left these counters unchanged.
Targeted bottleneck: Logical projection cache entries not populated when one full physical expert payload is materialized.
Expected diagnostic movement: Required misses/evictions should drop because gate/up/down logical entries are populated together with one physical payload upload; MiB/token may remain stable if physical upload count is unchanged.
Agent hypothesis: Observed anomaly: iter01 no-signal on scheduler resource key, but code showed the main path still calls per-projection cache fill. Verified runtime code path: runProjectionImplGpuV3 uses ensureExpertsCachedBatchGpuV3 even in external expert-payload mode, while ensureExpertsPackedCachedBatchGpuV3 can populate all logical projection entries for one physical payload. Physical/logical mapping hypothesis: route full-payload mode through the packed helper so all logical cache entries match the physical payload lifetime. Guardrails: ret=0, generated=16, unchanged p16/d16 contract.
Chosen optimization direction: populate-all-logical-cache-entries-on-physical-payload-materialization
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp around runProjectionImplGpuV3, ensureExpertsCachedBatchGpuV3, ensureExpertsPackedCachedBatchGpuV3, materializePackedExpertSlotBatchGpuV3
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: In full expert-payload mode, runProjectionImplGpuV3 now calls ensureExpertsPackedCachedBatchGpuV3 with gate/up/down caches instead of the per-projection cache-fill helper.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_ablation_e_iter_02_fasttemp_p16_d16
Compile result: build ok; host md5 a273fd62a5d5cc3191ae2e4dfce6b9c9; phone md5 a273fd62a5d5cc3191ae2e4dfce6b9c9; phone stat size 37173312 mode 0777 modify 2026-07-03 02:13:57 +0800
Correctness result: ret=0; generated=16/16
Metrics:
  decode_tok_s: 0.32728525857898016
  mib_per_token: 1431.8021875
  required_miss_count: 4912.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 4688.0
  required_miss_wait_ms_per_token: 1492.3685625000007
  decode_req_page_touch_ms: 18708.241999999995
  decode_req_mat_enqueue_ms: 5127.975999999999
  decode_req_mat_finish_ms: 13.875000000000004
  decode_req_service_ms: 23877.89700000001
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 2270.0
  decode_req_hit: 8482.0
  decode_evict: 2270.0
  cache_hit_rate: 0.7888764880952381
  peak_temp_skin_c_decode: 36.26604
Result: correct but speed regression: decode_tok_s=0.327285 vs baseline 0.329312; MiB/token unchanged. Diagnostic movement matched logical-entry hypothesis: decode_req_miss 6810 -> 2270, decode_evict 6810 -> 2270, hit rate 0.367 -> 0.789.
Agent diagnosis: The abstract mapping concept was sufficient to find a real logical-bookkeeping inconsistency. However, the physical upload volume stayed identical, so improving logical hit accounting did not improve the benchmark and slightly regressed throughput.
My diagnosis: This patch proves logical entries can be made consistent with a physical payload, but the measured bottleneck is physical page-touch/upload volume rather than logical miss accounting alone. A useful speed patch must affect the physical upload decision or payload reuse, not just counters/bookkeeping.
Needed expert knowledge: Additional knowledge needed: which cache-entry state actually controls skipping physical payload upload across tokens/layers, beyond the logical-vs-physical mapping abstraction.
Patch / commit: /home/liuxu/projects/mobile-moe-ako/patches/failed_attempts/s6_ablation_e_iter_02_fasttemp_p16_d16.patch

## s6_ablation_e_iter_03_fasttemp_p16_d16

Iteration ID: s6_ablation_e_iter_03_fasttemp_p16_d16
Stage: s6_ablation_e
Agent prompt setting: Minimal expert-context ablation E: physical payload may map to multiple logical runtime cache entries; no prior S6 fix material read
Baseline bottleneck decomposition: Baseline decode_tok_s=0.329312, mib_per_token=1431.802, decode req_miss=6810, decode_evict=6810, req_service_ms=24060.511. Iter02 reduced logical misses/evictions but did not reduce physical transfer or improve speed.
Targeted bottleneck: Avoid extra overhead from all-entry full-payload helper while preserving logical-entry population for physical payload materialization.
Expected diagnostic movement: Keep iter02 lower logical misses/evictions, recover speed above baseline, and keep MiB/token stable.
Agent hypothesis: Observed anomaly: iter02 proved logical-entry population but regressed throughput while physical transfer stayed unchanged. Verified runtime code path: the full-payload helper can be called only when the current projection lacks entries. Physical/logical mapping hypothesis: guarded full-payload population should maintain many-to-one bookkeeping consistency with less overhead. Guardrails: ret=0, generated=16, unchanged p16/d16 contract.
Chosen optimization direction: guarded-logical-entry-population-for-full-physical-payload
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp around ProjectionCache, runProjectionImplGpuV3, ensureExpertsCachedBatchGpuV3, ensureExpertsPackedCachedBatchGpuV3
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Added a guarded full-payload cache fill: only call the all-logical-entry helper when the current projection has a missing expert entry, otherwise use the original per-projection cache path.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_ablation_e_iter_03_fasttemp_p16_d16
Compile result: build ok; host md5 ef56dddf4acf8335673a5752d2b53139; phone md5 ef56dddf4acf8335673a5752d2b53139; phone stat size 37176256 mode 0777 modify 2026-07-03 02:19:44 +0800
Correctness result: ret=0; generated=16/16
Metrics:
  decode_tok_s: 0.33315714872784774
  mib_per_token: 1431.8021875
  required_miss_count: 4912.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 4688.0
  required_miss_wait_ms_per_token: 1465.159249999999
  decode_req_page_touch_ms: 18664.780000000006
  decode_req_mat_enqueue_ms: 4707.372
  decode_req_mat_finish_ms: 43.1540000000002
  decode_req_service_ms: 23442.547999999984
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 2270.0
  decode_req_hit: 8482.0
  decode_evict: 2270.0
  cache_hit_rate: 0.7888764880952381
  peak_temp_skin_c_decode: 36.39524
Result: correct but not a useful speed patch: decode_tok_s=0.333157 is only 1.17 percent over baseline, below signal threshold; MiB/token unchanged. Logical counters remain improved: decode_req_miss=2270, decode_evict=2270, hit_rate=0.789.
Agent diagnosis: The guarded variant preserved the logical bookkeeping effect and avoided the iter02 speed regression, but it still did not reduce physical upload/page-touch volume. The apparent 1.17 percent speedup is too small/noisy to select as best.
My diagnosis: The physical-payload/logical-entry mapping concept was enough to find and improve a real logical accounting issue, but the successful speed class appears to require knowing how to skip or coalesce physical uploads, not just how to mark logical cache entries consistent after upload.
Needed expert knowledge: Missing knowledge: the exact physical payload reuse mechanism and which logical entries must be updated before the upload decision so that the runtime skips movement, not merely reports fewer logical misses after movement.
Patch / commit: /home/liuxu/projects/mobile-moe-ako/patches/failed_attempts/s6_ablation_e_iter_03_fasttemp_p16_d16.patch

## s6_ablation_e_final_summary

Iteration ID: s6_ablation_e_final_summary
Stage: s6_ablation_e
Agent prompt setting: Minimal expert-context ablation E: physical payload may map to multiple logical runtime cache entries; no prior S6 fix material read
Baseline bottleneck decomposition: Valid baseline from base da9fa3534a16c0f34adb6709e2ba871741cbf8cc: decode_tok_s=0.3293120287; mib_per_token=1431.8021875; decode_core_upload_mib=22908.835; decode_req_miss=6810; decode_req_hit=3942; decode_evict=6810; cache_hit_rate=0.3666294643; decode_req_service_ms=24060.511; decode_req_page_touch_ms=18724.170; decode_req_mat_enqueue_ms=5281.115; correct ret=0 generated=16.
Targeted bottleneck: Decode required-miss churn and physical payload transfer under limited device cache capacity.
Expected diagnostic movement: A useful patch needed to improve decode_tok_s while keeping correctness and avoiding worse mib_per_token; ideally decode_core_upload_mib, decode_req_service_ms, or both would move with the stated physical/logical cache-state hypothesis.
Agent hypothesis: The abstract physical-payload/logical-entry mapping concept can reveal whether runtime bookkeeping keeps multiple logical cache entries consistent with a shared physical payload lifetime.
Chosen optimization direction: Stop early with no useful patch after three consecutive rejected attempts: one unchanged-cache-counter alias attempt, one logical-counter improvement with speed regression, and one guarded logical-counter improvement below signal threshold with unchanged physical transfer.
Files inspected: Allowed references; Tucker Qwen2 TD runner for contract confirmation; runtime repo /home/liuxu/projects/mllm; examples/qwen2_moe_td_qnn_aot/aot_run.cpp; mllm/backends/opencl/moe/HybridResourceManager.{hpp,cpp}.
Files modified: No runtime files remain modified; ITERATIONS.md appended; failed patch archives written under patches/failed_attempts/.
Change summary: No runtime patch selected or committed. Runtime repo is clean on exp/s6-ablation-e-payload-logical-mapping at da9fa3534a16c0f34adb6709e2ba871741cbf8cc. p32/d32 recheck skipped because no correctness-passing patch met best-patch selection criteria.
Benchmark command: No additional benchmark for final summary; p32/d32 recheck skipped.
Compile result: Baseline and all three optimization attempts built, deployed, and md5-verified before benchmarking. Baseline host/phone md5=6d15f401a12e515d066141c3a02ba4ea; phone stat size=36912960 mode=0777 modify=2026-07-03 02:01:02 +0800.
Correctness result: Baseline and iter_01/iter_02/iter_03 all ret=0 and generated 16/16.
Metrics:
  baseline_decode_tok_s: 0.3293120286837363
  iter_01_decode_tok_s: 0.33652410769318297
  iter_02_decode_tok_s: 0.32728525857898016
  iter_03_decode_tok_s: 0.33315714872784774
  baseline_mib_per_token: 1431.8021875
  iter_01_mib_per_token: 1431.8021875
  iter_02_mib_per_token: 1431.8021875
  iter_03_mib_per_token: 1431.8021875
  baseline_decode_req_miss: 6810.0
  iter_01_decode_req_miss: 6810.0
  iter_02_decode_req_miss: 2270.0
  iter_03_decode_req_miss: 2270.0
  baseline_decode_core_upload_mib: 22908.835
  iter_01_decode_core_upload_mib: 22908.835
  iter_02_decode_core_upload_mib: 22908.835
  iter_03_decode_core_upload_mib: 22908.835
Result: No-useful-patch conclusion for S6-Ablation-E. The mapping concept was sufficient to find a real logical-cache bookkeeping effect, but not sufficient to find a speed-relevant repair in this minimal context because physical upload volume remained unchanged.
Agent diagnosis: The successful class of repair was not discovered under this context budget. The best logical-counter movement did not reduce mib_per_token or decode_core_upload_mib, so it was not selected despite correctness.
My diagnosis: Physical-payload/logical-entry reasoning helped distinguish logical cache accounting from physical transfer behavior. Additional profiling or expert knowledge is still needed about the exact runtime state that controls whether physical payload movement can be skipped before upload service occurs.
Needed expert knowledge: More direct knowledge of the physical upload-skip decision and its relationship to logical cache entries; existing counters show the mismatch but do not identify the speed-relevant repair by themselves.
Patch / commit: no commit; failed patches archived as patches/failed_attempts/s6_ablation_e_iter_01_fasttemp_p16_d16.patch, patches/failed_attempts/s6_ablation_e_iter_02_fasttemp_p16_d16.patch, and patches/failed_attempts/s6_ablation_e_iter_03_fasttemp_p16_d16.patch
