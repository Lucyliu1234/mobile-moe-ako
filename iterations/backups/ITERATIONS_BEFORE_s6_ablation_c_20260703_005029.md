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
