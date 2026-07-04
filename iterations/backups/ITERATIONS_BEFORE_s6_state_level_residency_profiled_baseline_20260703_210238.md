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

## s6_verify_baseline_fasttemp_p16_d16

Iteration ID: s6_verify_baseline_fasttemp_p16_d16
Stage: s6_verify
Agent prompt setting: S6 Verify integrated diagnostic AKO baseline
Baseline bottleneck decomposition: Baseline from da9fa3534a16c0f34adb6709e2ba871741cbf8cc rebuilt and deployed: decode_tok_s=0.3321737356, mib_per_token=1431.8021875, required_miss_count=6810, required_miss_wait_ms_per_token=1463.2388125, decode_req_service_ms=23411.821, page_touch_ms=18400.226, enqueue_ms=4957.628, finish_ms=11.568, writes=2270, page_touch_mib=22908.835, core_upload_mib=22908.835, req_hit=3942, req_miss=6810, evict=6810, cache_hit_rate=0.3666294643, peak_skin_decode=34.73236.
Targeted bottleneck: Baseline profiling report only before first edit.
Expected diagnostic movement: Existing counters are enough for an initial optimization: total required-miss service, page-touch, enqueue, writes, transfer volume, hits/misses/evictions, and thermal are present. Missing diagnostics: madvise_us, CPU touch-loop split from page-touch, per-layer/per-projection required-miss service, page fault counts, enqueue latency distribution.
Agent hypothesis: Required miss service dominates decode; first optimization should target required miss churn/service rather than celebrating subcounter movement.
Chosen optimization direction: Profile first, then choose one runtime-policy change tied to total service or decode_tok_s.
Files inspected: references/metrics_schema.md; references/expert_hints/diagnostic_instrumentation.md; references/expert_hints/coremoe_required_core.md; examples/qwen2_moe_td_qnn_aot/aot_run.cpp via symbol search; baseline summary.jsonl.
Files modified: None in runtime repo. Created results/runs/s6_verify_baseline_fasttemp_p16_d16/metrics.json for logging only.
Change summary: No code change; baseline built, deployed, md5-verified, benchmarked, and profiled.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_verify_baseline_fasttemp_p16_d16
Compile result: build OK; host md5 6d15f401a12e515d066141c3a02ba4ea; phone md5 matched; phone stat size 36912960
Correctness result: ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.33217373558327057
  mib_per_token: 1431.8021875
  required_miss_count: 6810.0
  upload_bytes: None
  prewarm_hit_rate: None
  eviction_churn: 6810.0
  required_miss_wait_ms_per_token: 1463.2388124999982
  decode_req_page_touch_ms: 18400.225999999995
  decode_req_mat_enqueue_ms: 4957.628000000001
  decode_req_mat_finish_ms: 11.56799999999999
  decode_req_service_ms: 23411.82099999997
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 34.73236
Result: Baseline valid. Existing counters sufficient for first optimization, but missing lower-level page-fault/madvise/per-layer diagnostics if policy changes only shift latency.
Agent diagnosis: Decode is dominated by required miss service. Page-touch is the largest subcounter, enqueue is also material, finish is tiny. Misses equal evictions in decode, indicating severe residency churn at cache capacity 8.
My diagnosis: Do not treat page-touch/enqueue movement alone as success. The next change should reduce decode_req_service_ms or improve decode_tok_s without increasing mib_per_token; otherwise archive it.
Needed expert knowledge: Need exact residency policy and required miss materialization path in qwen2_moe_td_qnn_aot; if first policy attempt mismatches metrics, add diagnostic counters for madvise/touch/per-layer service.
Patch / commit: No patch; baseline provenance recorded.

## s6_verify_iter_01_fasttemp_p16_d16

Iteration ID: s6_verify_iter_01_fasttemp_p16_d16
Stage: s6_verify
Agent prompt setting: S6 Verify integrated diagnostic AKO loop
Baseline bottleneck decomposition: Baseline decode_tok_s=0.3321737356; mib_per_token=1431.8021875; req_miss=6810; req_hit=3942; evict=6810; service=23411.821ms; page_touch=18400.226ms; enqueue=4957.628ms; finish=11.568ms; writes=2270; peak_skin_decode=34.73236.
Targeted bottleneck: Required miss explicit CPU page-touch before mmap-backed OpenCL upload.
Expected diagnostic movement: If CPU pre-touch is redundant, decode_req_page_touch_ms should fall and total decode_req_service_ms or decode_tok_s should improve without changing mib_per_token, req_miss, hit, or evict.
Agent hypothesis: Bypassing explicit touchMmapPages in interleaved GPU-v3 payload upload keeps the same OpenCL writes but avoids duplicate CPU page sweeps.
Chosen optimization direction: optimization: remove explicit page-touch work in page_touch_mode=2 interleaved upload path.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp materializeCoreSlotBatchGpuV3/materializePackedExpertSlotBatchGpuV3; Tucker env confirmed page_touch_mode=2 and hot_resident_core=1.
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Removed explicit touchMmapPages calls from interleaved mmap-backed upload paths; retained same per-span enqueue and finish behavior.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_verify_iter_01_fasttemp_p16_d16
Compile result: build OK; host md5 6459e6399d7274e5a640650b62560749; phone md5 matched; phone stat size 36916440; artifact changed from baseline.
Correctness result: ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.3301415591294159
  mib_per_token: 1431.8021875
  required_miss_count: 6810.0
  upload_bytes: None
  prewarm_hit_rate: None
  eviction_churn: 6810.0
  required_miss_wait_ms_per_token: 1435.8852499999987
  decode_req_page_touch_ms: 0.0
  decode_req_mat_enqueue_ms: 14617.167000000009
  decode_req_mat_finish_ms: 8313.371000000003
  decode_req_service_ms: 22974.16399999998
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 0.0
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 35.62156
Result: Failed/no-signal optimization: decode_tok_s regressed 0.33217 -> 0.33014 and mib_per_token unchanged. Total service improved only slightly while cost shifted from page_touch into enqueue/finish; peak decode skin was hotter.
Agent diagnosis: The explicit page-touch counter was not an independent removable cost. Removing it caused clEnqueueWriteBuffer/finish to absorb the page residency cost, exactly matching the prior-stage caution.
My diagnosis: Archive and revert. Do not count page_touch_ms=0 as a win because throughput regressed and transfer/cache metrics did not move.
Needed expert knowledge: Need diagnostics that split madvise, CPU touch-loop, and OpenCL page fault/driver copy behavior if further page-residency work is attempted.
Patch / commit: Archived failed patch: patches/failed_attempts/s6_verify_iter_01_fasttemp_p16_d16.patch

## s6_verify_iter_02_fasttemp_p16_d16

Iteration ID: s6_verify_iter_02_fasttemp_p16_d16
Stage: s6_verify
Agent prompt setting: S6 Verify integrated diagnostic AKO loop
Baseline bottleneck decomposition: After iter 01 latency-shift failure, baseline still shows page_touch=18400.226ms, enqueue=4957.628ms, finish=11.568ms, service=23411.821ms; missing split is madvise vs CPU touch-loop/page faults.
Targeted bottleneck: Diagnostic-only split of required-miss mmap page-touch behavior.
Expected diagnostic movement: Expose req_page_touch_madvise_ms, req_page_touch_loop_ms, touched pages, minor faults, and major faults in summary.jsonl without changing benchmark semantics.
Agent hypothesis: The visible page-touch cost is mostly CPU touch-loop/page faults rather than madvise syscall time, explaining why removing pre-touch shifts latency into OpenCL upload.
Chosen optimization direction: diagnostic: lightweight aggregate counters for mmap touch subcomponents; not eligible as best patch.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp touchMmapPages and required GPU-v3 page-touch sites; Tucker parser generic key=value extraction.
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Added MmapTouchProfile counters for madvise time, touch-loop time, page count, and rusage minor/major fault deltas; exposed them through existing Hybrid GPU shadow and hybrid-cold log lines.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_verify_iter_02_fasttemp_p16_d16
Compile result: build OK; host md5 58e2d4620d05fa2654fb6271731a01ae; phone md5 matched; phone stat size 36920248; artifact changed from baseline.
Correctness result: ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.3302707260103988
  mib_per_token: 1431.8021875
  required_miss_count: 6810.0
  upload_bytes: None
  prewarm_hit_rate: None
  eviction_churn: 6810.0
  required_miss_wait_ms_per_token: 1507.6558124999997
  decode_req_page_touch_ms: 19119.702999999994
  decode_req_mat_enqueue_ms: 4943.759
  decode_req_mat_finish_ms: 15.796000000000006
  decode_req_service_ms: 24122.492999999995
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 36.03728
Result: Diagnostic succeeded: counters appeared. Decode page-touch split: madvise_ms=500.841, touch_loop_ms=18592.076, pages=5865542, minflt=533660, majflt=2512. Throughput slower than baseline as expected for instrumentation and not eligible as best patch.
Agent diagnosis: Required-miss page-touch time is overwhelmingly CPU touch-loop/page residency fault work, not advisory madvise overhead. This explains iter 01: eliminating the pre-touch made the OpenCL upload path pay the same residency cost.
My diagnosis: Next optimization should target reducing physical page residency churn/bytes touched or changing residency timing, not merely removing madvise or moving touch work across subcounters.
Needed expert knowledge: Need a policy that reduces required miss count/bytes or pre-residences pages earlier without increasing transfer volume; per-layer/projection service could further localize the worst churn.
Patch / commit: Archived diagnostic-only patch: patches/failed_attempts/s6_verify_iter_02_fasttemp_p16_d16.patch

## s6_verify_iter_03_fasttemp_p16_d16

Iteration ID: s6_verify_iter_03_fasttemp_p16_d16
Stage: s6_verify
Agent prompt setting: S6 Verify integrated diagnostic AKO loop
Baseline bottleneck decomposition: Baseline decode_tok_s=0.3321737356; mib_per_token=1431.8021875; req_miss=6810; req_hit=3942; evict=6810; service=23411.821ms; hit_rate=0.3666. Iter 02 diagnostic showed page_touch dominated by CPU touch-loop/page faults, so reducing logical/physical miss churn is preferable to shifting page-touch.
Targeted bottleneck: Logical required-miss duplication across gate/up/down projections when packed full-expert payload arena is enabled.
Expected diagnostic movement: Reduce decode_req_miss and decode_evict while keeping decode_core_upload_mib and mib_per_token unchanged; ideally improve decode_tok_s and/or service.
Agent hypothesis: When full expert payload arena is enabled, a gate miss uploads gate+up+down together, so the cache should populate all three projection caches together to avoid up/down being counted and served as separate required misses.
Chosen optimization direction: optimization: route GPU-v3 packed full-expert payload caching through ensureExpertsPackedCachedBatchGpuV3.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp runProjectionImplGpuV3, ensureExpertsPackedCachedBatchGpuV3, materializePackedExpertSlotBatchGpuV3; Tucker env confirmed packed payload arena and expert miss full enabled.
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Use the existing packed full-expert cache helper when gate/up/down packed payload arena is active; fall back to old per-projection cache path otherwise.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_verify_iter_03_fasttemp_p16_d16
Compile result: build OK; host md5 aa3cd1d51ccbbde3c767efbd65d6ebcd; phone md5 matched; phone stat size 37173568; artifact changed from baseline.
Correctness result: ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.3332703174708049
  mib_per_token: 1431.8021875
  required_miss_count: 2270.0
  upload_bytes: None
  prewarm_hit_rate: None
  eviction_churn: 2270.0
  required_miss_wait_ms_per_token: 1470.5728749999985
  decode_req_page_touch_ms: 18730.728999999978
  decode_req_mat_enqueue_ms: 4759.7829999999985
  decode_req_mat_finish_ms: 10.876
  decode_req_service_ms: 23529.165999999976
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 2270.0
  decode_req_hit: 8482.0
  decode_evict: 2270.0
  cache_hit_rate: 0.7888764880952381
  peak_temp_skin_c_decode: 36.1224
Result: Correctness-passing small positive signal: decode_tok_s 0.33217 -> 0.33327, mib_per_token unchanged, req_miss 6810 -> 2270, evict 6810 -> 2270, cache_hit_rate 0.3666 -> 0.7889. Total decode_req_service_ms was roughly flat/slightly worse, so improvement is small and noisy but diagnostically consistent.
Agent diagnosis: The change fixed a logical residency/accounting mismatch: full payload upload can make up/down immediately resident, reducing required miss churn without increasing transfer bytes.
My diagnosis: Commit as useful but require p32/d32 recheck before calling it best. The speed gain is below 3%, but the cache/miss movement is strong and transfer guardrail holds.
Needed expert knowledge: Need repeat or longer-contract recheck to distinguish small throughput signal from thermal/noise; further work may target physical bytes/page residency because service did not fall with logical miss count.
Patch / commit: Commit 382f732d ([s6 verify iter 03] Share packed expert payload cache).

## s6_verify_best_recheck_fasttemp_p32_d32

Iteration ID: s6_verify_best_recheck_fasttemp_p32_d32
Stage: s6_verify
Agent prompt setting: Best patch daytime p32/d32 signal recheck
Baseline bottleneck decomposition: Recheck of committed best candidate 382f732d after p16/d16 showed small speedup and large miss/hit movement.
Targeted bottleneck: Signal validation for packed full-expert cache sharing under longer decode.
Expected diagnostic movement: Preserve correctness and high hit rate on p32/d32; no evening verdict requested.
Agent hypothesis: If iter 03 fixed logical packed-payload cache population, p32/d32 should also show high cache hit rate without correctness failure.
Chosen optimization direction: recheck only; no new patch.
Files inspected: results/runs/s6_verify_best_recheck_fasttemp_p32_d32/summary.jsonl
Files modified: None
Change summary: No code change; rechecked committed iter 03 artifact.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p32.jsonl --decode-tokens 32 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_verify_best_recheck_fasttemp_p32_d32
Compile result: reused committed iter 03 artifact already verified before p16 run: host/phone md5 aa3cd1d51ccbbde3c767efbd65d6ebcd, phone size 37173568
Correctness result: ret=0 generated=32/32
Metrics:
  decode_tok_s: 0.29699168031637335
  mib_per_token: 1551.1785312499956
  required_miss_count: 4885.0
  upload_bytes: None
  prewarm_hit_rate: None
  eviction_churn: 4885.0
  required_miss_wait_ms_per_token: 1600.147562499999
  decode_req_page_touch_ms: 40149.254
  decode_req_mat_enqueue_ms: 10960.955999999996
  decode_req_mat_finish_ms: 34.19299999999986
  decode_req_service_ms: 51204.721999999965
  decode_req_mat_writes: 4885.0
  decode_req_page_touch_mib: 49637.71299999986
  decode_core_upload_mib: 49637.71299999986
  decode_req_miss: 4885.0
  decode_req_hit: 16619.0
  decode_evict: 4885.0
  cache_hit_rate: 0.7728329613095238
  peak_temp_skin_c_decode: 37.8134
Result: Correctness passed; decode_tok_s=0.29699, mib_per_token=1551.1785, req_miss=4885, req_hit=16619, hit_rate=0.7728. Thermal exceeded clean envelope by decode end (peak_skin_decode=37.8134), so treat as signal not verdict.
Agent diagnosis: The cache-sharing behavior survives p32/d32: hit rate remains high and miss count is much lower than the original p16 baseline scale would suggest, but thermal comparability is poor.
My diagnosis: Best candidate remains 382f732d. It needs cleaner thermal repeat or evening verdict if a publication-quality claim is required.
Needed expert knowledge: Need controlled p32/d32 baseline/repeat under comparable thermal state, and possibly per-layer/projection diagnostics to reduce physical page-touch volume next.
Patch / commit: Commit 382f732d; no new patch.

## s6_verify2_baseline_fasttemp_p16_d16

Iteration ID: s6_verify2_baseline_fasttemp_p16_d16
Stage: s6_verify2
Agent prompt setting: S6 Verify2 integrated diagnostic AKO baseline
Baseline bottleneck decomposition: decode_tok_s=0.335097; mib_per_token=1431.802; required_miss_count=14736 overall, decode_req_miss=6810; decode_req_service_ms=22813.152; page_touch_ms=18504.307 dominates, enqueue_ms=4252.927, finish_ms=13.694; decode_evict=6810, cache_hit_rate=0.366629; peak_temp_skin_decode=32.503C
Targeted bottleneck: Baseline profiling only: required-miss service and cache churn for GPU-v3 expert payloads
Expected diagnostic movement: No runtime change; establish provenance and diagnose whether existing counters are sufficient
Agent hypothesis: Baseline built and deployed from da9fa3534a16c0f34adb6709e2ba871741cbf8cc; existing counters should show whether page-touch, enqueue, finish, misses, evictions, or transfer volume dominate.
Chosen optimization direction: Optimization should target total required-miss service or miss/eviction count, not isolated latency shifting.
Files inspected: references/constraints.md; references/benchmark_instructions.md; references/metrics_schema.md; references/expert_hints/diagnostic_instrumentation.md; references/expert_hints/coremoe_required_core.md; examples/qwen2_moe_td_qnn_aot/aot_run.cpp; scripts/parse_metrics.py
Files modified: None in runtime; appended ITERATIONS.md and wrote metrics.json
Change summary: Baseline/profiling report only. Rebuilt runner, deployed to phone, verified host/phone md5 match 6d15f401a12e515d066141c3a02ba4ea and phone stat size 36912960.
Benchmark command: cd /home/liuxu/projects/mobile-moe-ako && /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_verify2_baseline_fasttemp_p16_d16
Compile result: success: cmake build target mllm-qwen2-moe-td-qnn-aot-runner at da9fa3534a16c0f34adb6709e2ba871741cbf8cc
Correctness result: correct: ret=0, generated=16/16
Metrics:
  decode_tok_s: 0.3350972994801845
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1425.822000000001
  decode_req_page_touch_ms: 18504.307000000015
  decode_req_mat_enqueue_ms: 4252.926999999999
  decode_req_mat_finish_ms: 13.694000000000004
  decode_req_service_ms: 22813.152000000016
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 32.50252
Result: Baseline valid and correctness-passing.
Agent diagnosis: Existing counters are enough for the first optimization: page-touch dominates total decode required-miss service, but transfer volume and eviction churn are equally large, so a win must improve decode_tok_s or total req_service without increasing mib_per_token.
My diagnosis: Diagnostic iteration not required before the first edit. Missing diagnostics: explicit madvise_us vs CPU touch-loop time, per-layer/projection service distribution, and page-fault counts. However available counters already distinguish page_touch, enqueue, finish, total service, writes, MiB, hits/misses, evictions, and thermal state.
Needed expert knowledge: Need causal policy knowledge about GPU-v3 core residency and required-batch/materialization scheduling; avoid treating subcounter shifts as wins.
Patch / commit: baseline only; no runtime patch

## s6_verify2_iter_01_fasttemp_p16_d16

Iteration ID: s6_verify2_iter_01_fasttemp_p16_d16
Stage: s6_verify2
Agent prompt setting: S6 Verify2 integrated diagnostic AKO
Baseline bottleneck decomposition: Baseline decode_tok_s=0.335097; mib_per_token=1431.802; decode_req_service_ms=22813.152 with page_touch_ms=18504.307 and enqueue_ms=4252.927; decode_req_miss=6810, decode_evict=6810.
Targeted bottleneck: GPU-v3 required-core full expert payload cache bookkeeping and eviction churn
Expected diagnostic movement: If successful: decode_req_miss and decode_evict should fall, physical decode_core_upload_mib and mib_per_token should not rise, and total decode_req_service_ms or decode_tok_s should improve materially.
Agent hypothesis: Using the existing packed full-expert cache path when expert payload arena/full materialize mode is active would avoid counting/serving gate/up/down as separate required cache misses and reduce redundant eviction churn.
Chosen optimization direction: Optimization iteration: route GPU-v3 full-payload mode through ensureExpertsPackedCachedBatchGpuV3 for coherent expert-level slot/cache decisions.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; references/expert_hints/coremoe_required_core.md; summary.jsonl baseline counters
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Changed runProjectionImplGpuV3 to call ensureExpertsPackedCachedBatchGpuV3 when expert_payload_arena_ and expert_miss_full_materialize_ are active.
Benchmark command: cd /home/liuxu/projects/mobile-moe-ako && /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_verify2_iter_01_fasttemp_p16_d16
Compile result: success; host md5 937bbd80a0db0521173a36591cbb500c, phone md5 matched, phone size 37176048
Correctness result: correct: ret=0, generated=16/16
Metrics:
  decode_tok_s: 0.3372406100674205
  mib_per_token: 1431.8021875
  required_miss_count: 4912.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 4688.0
  required_miss_wait_ms_per_token: 1432.123187499999
  decode_req_page_touch_ms: 18357.271999999997
  decode_req_mat_enqueue_ms: 4514.224999999994
  decode_req_mat_finish_ms: 13.942999999999996
  decode_req_service_ms: 22913.970999999983
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 2270.0
  decode_req_hit: 8482.0
  decode_evict: 2270.0
  cache_hit_rate: 0.7888764880952381
  peak_temp_skin_c_decode: 33.7702
Result: Failed/no-signal optimization: correctness passed and decode_tok_s rose only 0.64%, but total decode_req_service_ms worsened from 22813.152 to 22913.971 and mib_per_token stayed unchanged.
Agent diagnosis: Logical cache hit/miss accounting improved strongly: decode_req_miss 6810->2270 and decode_evict 6810->2270, cache_hit_rate 0.367->0.789. But physical transfer stayed at 22908.835 MiB and page_touch remained about 18.36s, so the change mostly changed bookkeeping/cache coherence and shifted enqueue upward.
My diagnosis: This confirms the previous-stage lesson: a subcounter/cache-hit improvement is not a win without total service or throughput improvement. The packed path reduced logical churn but did not reduce physical payload bytes touched/uploaded, so it is not a useful patch.
Needed expert knowledge: Need to distinguish logical expert-level misses from physical payload page-touch/upload volume; next direction should target physical bytes/service or add diagnostic detail if that cannot be separated.
Patch / commit: Archived failed patch: patches/failed_attempts/s6_verify2_iter_01_fasttemp_p16_d16.patch; reverted runtime edit

## s6_verify2_iter_02_fasttemp_p16_d16

Iteration ID: s6_verify2_iter_02_fasttemp_p16_d16
Stage: s6_verify2
Agent prompt setting: S6 Verify2 integrated diagnostic AKO
Baseline bottleneck decomposition: Baseline decode_tok_s=0.335097; mib_per_token=1431.802; decode_req_service_ms=22813.152 with page_touch_ms=18504.307, enqueue_ms=4252.927, finish_ms=13.694; decode_req_miss=6810, decode_evict=6810.
Targeted bottleneck: Explicit CPU page-touch cost in GPU-v3 required external payload uploads
Expected diagnostic movement: If page-touch is redundant overhead, decode_req_page_touch_ms should fall and total decode_req_service_ms/decode_tok_s should improve without mib_per_token rising. If page faults simply move into OpenCL, enqueue/finish will rise and total service will not materially improve.
Agent hypothesis: The explicit touchMmapPages loop before clEnqueueWriteBuffer may double-walk the same mapped payload pages; removing it might let OpenCL host-to-device upload service faults directly and reduce total miss service.
Chosen optimization direction: Optimization iteration: remove explicit CPU page-touch in the GPU-v3 external payload required upload paths.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; baseline and iter01 summary.jsonl
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Removed touchMmapPages and page-touch accounting from the two GPU-v3 external payload enqueue loops.
Benchmark command: cd /home/liuxu/projects/mobile-moe-ako && /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_verify2_iter_02_fasttemp_p16_d16
Compile result: success; host md5 b5081bfa566e84a7308c289b47204cf7, phone md5 matched, phone size 36912032
Correctness result: correct: ret=0, generated=16/16
Metrics:
  decode_tok_s: 0.3357465466106963
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1393.2621875
  decode_req_page_touch_ms: 0.0
  decode_req_mat_enqueue_ms: 14946.603999999988
  decode_req_mat_finish_ms: 7304.369999999999
  decode_req_service_ms: 22292.195
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 0.0
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 34.72856
Result: Failed/no-signal optimization: correctness passed, mib_per_token unchanged, total service fell only 2.3% and decode_tok_s improved only 0.19%, below meaningful/noise threshold; page-touch latency largely shifted into enqueue/finish.
Agent diagnosis: decode_req_page_touch_ms 18504->0, but enqueue rose 4253->14947 and finish rose 14->7304. decode_req_service_ms 22813->22292 is not enough to select, especially with peak skin 34.73C vs baseline 32.50C and decode_tok_s nearly unchanged.
My diagnosis: This validates that explicit page-touch is mostly a placement of page-fault cost rather than a removable bottleneck under this contract. Existing counters were sufficient to detect latency shifting, so no diagnostic patch is needed for this specific question.
Needed expert knowledge: Need lower-level evidence on OpenCL host pointer faulting and page residency if trying to tune page-touch further; otherwise target physical bytes or scheduling overlap.
Patch / commit: Archived failed patch: patches/failed_attempts/s6_verify2_iter_02_fasttemp_p16_d16.patch; reverted runtime edit

## s6_verify2_iter_03_fasttemp_p16_d16

Iteration ID: s6_verify2_iter_03_fasttemp_p16_d16
Stage: s6_verify2
Agent prompt setting: S6 Verify2 integrated diagnostic AKO
Baseline bottleneck decomposition: After two optimization attempts, existing counters showed latency shifting and no physical MiB reduction: baseline decode_req_service_ms=22813.152, page_touch_ms=18504.307, decode_core_upload_mib=22908.835.
Targeted bottleneck: Diagnostic-only: page-touch granularity for GPU-v3 required payload service
Expected diagnostic movement: Expose req_page_touch_calls, average touch size/time, and max touch size/time in existing runtime logs/summary without changing model work or benchmark semantics.
Agent hypothesis: A diagnostic counter can determine whether page-touch cost is dominated by a few pathological spans/layers or by many medium-size required payload touches, guiding whether to target outliers or physical upload volume.
Chosen optimization direction: Diagnostic iteration only: add lightweight page-touch granularity counters; not eligible as best patch.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; iter02 metrics and logs
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Added core_page_touch_calls/max counters and emitted req_page_touch_calls/avg/max fields in existing hybrid GPU summary and per-layer log lines.
Benchmark command: cd /home/liuxu/projects/mobile-moe-ako && /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_verify2_iter_03_fasttemp_p16_d16
Compile result: success; host md5 171b25bf08b952262aa74bb1afe20940, phone md5 matched, phone size 36925952
Correctness result: correct: ret=0, generated=16/16
Metrics:
  decode_tok_s: 0.3372471355229511
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1437.8875625
  decode_req_page_touch_ms: 18458.982999999993
  decode_req_mat_enqueue_ms: 4481.860000000006
  decode_req_mat_finish_ms: 22.463999999999945
  decode_req_service_ms: 23006.201
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 35.37608
Result: Diagnostic succeeded but is not a speed patch. New fields appeared in summary/logs. Decode had 2270 page-touch calls for 22908.835 MiB; whole-run line had 4912 calls for 49763.913 MiB, average about 10374 KiB/call and 8480 us/call, max 50.663 ms and 13.307 MiB. The parser sums per-line avg/max fields in decode aggregate, so raw line values are the reliable diagnostic.
Agent diagnosis: Page-touch cost is distributed across many medium-sized required payload touches rather than one huge outlier. This makes a per-outlier optimization unlikely; physical payload volume or overlap/scheduling would need to change to get a meaningful win.
My diagnosis: The integrated diagnostic iteration improved the AKO loop by preventing another blind page-touch tweak. It also revealed a future parser/schema improvement need for average/max diagnostic fields if they are to be consumed automatically.
Needed expert knowledge: Need an expert policy for reducing physical GPU-v3 payload bytes or safely overlapping required uploads with compute; parser support for non-additive avg/max diagnostics would help.
Patch / commit: Archived diagnostic patch: patches/failed_attempts/s6_verify2_iter_03_fasttemp_p16_d16.patch; reverted instrumentation

## s6_detailed_expert_baseline_fasttemp_p16_d16

Iteration ID: s6_detailed_expert_baseline_fasttemp_p16_d16
Stage: s6_detailed_expert
Agent prompt setting: S6-Detailed-Expert-Mechanism MobileMoE-AKO
Baseline bottleneck decomposition: Baseline from rebuilt/deployed base da9fa3534a16c0f34adb6709e2ba871741cbf8cc: decode_tok_s=0.337842, correct=true generated=16/16, mib_per_token=1431.802, decode_core_upload_mib=22908.835, decode_req_service_ms=23010.815 with page_touch_ms=18198.863, enqueue_ms=4724.848, finish_ms=45.097, writes=2270; decode_req_hit=3942, decode_req_miss=6810, decode_evict=6810, cache_hit_rate=0.366629, peak_skin_decode=33.649C.
Targeted bottleneck: Baseline/profiling only before source edits: required-miss service and physical upload volume under cache capacity 8.
Expected diagnostic movement: N/A baseline. Future useful patch must improve decode_tok_s or reduce required-miss service/physical upload without increasing normalized transfer.
Agent hypothesis: Baseline profiling report: every decode required miss is paired with an eviction and each miss services physical core upload/page-touch; this may reflect true cache pressure or incomplete residency accounting. Need fresh runtime code inspection to identify the logical key, physical resource, hit/miss state, and materialization update before editing.
Chosen optimization direction: No optimization direction yet; baseline provenance and profiling.
Files inspected: Allowed references; runtime git branch/status; baseline summary.jsonl/summary.csv/metrics.json.
Files modified: None in runtime. ITERATIONS.md appended; ITERATIONS.md was backed up to ITERATIONS_BEFORE_s6_detailed_expert_20260703_codex.md before baseline.
Change summary: Baseline built/deployed/verified only; no source changes.
Benchmark command: cd /home/liuxu/projects/mobile-moe-ako && /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_detailed_expert_baseline_fasttemp_p16_d16
Compile result: success; host md5 6d15f401a12e515d066141c3a02ba4ea, phone md5 matched, host size 36912960, phone size 36912960, phone mode 0777
Correctness result: correct: ret=0, generated=16/16
Metrics:
  decode_tok_s: 0.33784234620698483
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1438.1759375000004
  decode_req_page_touch_ms: 18198.86300000001
  decode_req_mat_enqueue_ms: 4724.848000000001
  decode_req_mat_finish_ms: 45.09700000000026
  decode_req_service_ms: 23010.815000000006
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 33.64936
Result: Valid rebuilt baseline. Physical transfer is high: decode_core_upload_mib equals decode_req_page_touch_mib and mib_per_token is 1431.802. Miss/evict churn is one-to-one in decode.
Agent diagnosis: The baseline bottleneck is required-miss service dominated by page-touch plus upload enqueue, not a missing correctness or benchmark issue. Existing counters are sufficient to start localizing the hit/miss upload decision, but code inspection is required before forming the first patch hypothesis.
My diagnosis: Useful patch must affect the state consulted before materialization/upload or the materialization update that records physical residency. Logical counter-only improvements are insufficient unless decode_core_upload_mib, mib_per_token, or total required service also move.
Needed expert knowledge: Detailed residency model: distinguish logical cache keys from physical payload/storage resources and verify whether post-materialization state reflects reusable physical data lifetime.
Patch / commit: No runtime patch. Baseline provenance: branch exp/s6-detailed-expert-mechanism at da9fa3534a16c0f34adb6709e2ba871741cbf8cc; host and phone md5 6d15f401a12e515d066141c3a02ba4ea.

## s6_detailed_expert_iter_01_fasttemp_p16_d16

Iteration ID: s6_detailed_expert_iter_01_fasttemp_p16_d16
Stage: s6_detailed_expert
Agent prompt setting: S6-Detailed-Expert-Mechanism MobileMoE-AKO
Baseline bottleneck decomposition: Baseline decode_tok_s=0.337842; mib_per_token=1431.802; decode_core_upload_mib=22908.835; decode_req_service_ms=23010.815; decode_req_miss=6810; decode_evict=6810; decode_req_mat_writes=2270.
Targeted bottleneck: Hit/miss upload decision for GPU-v3 shared full-expert payload arena logical residency.
Expected diagnostic movement: If the existing full-expert payload materialization was physically reusable across projections but incompletely represented in logical state, then using the all-projection cache update should reduce decode_core_upload_mib, decode_req_page_touch_mib, decode_req_mat_writes, total required miss service, and improve decode_tok_s without correctness loss.
Agent hypothesis: Observed anomaly: miss/evict churn was one-to-one at decode and the code had a shared ExpertPayloadArena bound to gate/up/down projection caches, while runProjectionImplGpuV3 called the single-projection ensureExpertsCachedBatchGpuV3. Verified runtime code path: runProjectionImplGpuV3 -> bindExpertPayloadArenaNoLock -> ensureExpertsCachedBatchGpuV3 -> materializeCoreSlotBatchGpuV3. Logical cache key: per-projection pc.entries[expert]. Physical resource/upload span: shared layer ExpertPayloadArena payload_arena with full expert stride. State checked before upload: pc.entries.find(expert) for current projection. State updated after upload: single projection entry, while ensureExpertsPackedCachedBatchGpuV3 would update gate/up/down entries. Expected real metric movement: lower physical upload/page-touch/write count and service, not just hit counters.
Chosen optimization direction: Optimization iteration: route shared full-expert arena miss handling through the existing packed full-expert batch helper so logical entries for gate/up/down are updated together.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; baseline summary.jsonl/summary.csv/metrics.json.
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: When expert_payload_arena + expert_miss_full_materialize are active, runProjectionImplGpuV3 called ensureExpertsPackedCachedBatchGpuV3 over gate/up/down caches instead of ensureExpertsCachedBatchGpuV3 for the current projection.
Benchmark command: cd /home/liuxu/projects/mobile-moe-ako && /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_detailed_expert_iter_01_fasttemp_p16_d16
Compile result: success; host md5 4e95081db98ca9c6f0071ab35a5db934, phone md5 matched, host/phone size 37175888, phone mode 0777
Correctness result: correct: ret=0, generated=16/16
Metrics:
  decode_tok_s: 0.3358276653319476
  mib_per_token: 1431.8021875
  required_miss_count: 4912.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 4688.0
  required_miss_wait_ms_per_token: 1468.2503125
  decode_req_page_touch_ms: 18003.323999999997
  decode_req_mat_enqueue_ms: 5450.539
  decode_req_mat_finish_ms: 10.424000000000001
  decode_req_service_ms: 23492.005
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 2270.0
  decode_req_hit: 8482.0
  decode_evict: 2270.0
  cache_hit_rate: 0.7888764880952381
  peak_temp_skin_c_decode: 34.49448
Result: Failed/no-signal optimization: correctness passed and logical hit rate improved, but decode_tok_s regressed 0.60%, mib_per_token unchanged, decode_core_upload_mib unchanged, decode_req_page_touch_mib unchanged, and decode_req_mat_writes unchanged.
Agent diagnosis: The patch changed logical accounting strongly: decode_req_miss 6810->2270, decode_evict 6810->2270, cache_hit_rate 0.367->0.789. But physical transfer did not change: decode_core_upload_mib stayed 22908.835, page_touch_mib stayed 22908.835, writes stayed 2270, and service rose 23010.815->23492.005 ms. This is explicitly not a useful win under the S6 contract.
My diagnosis: The current physical upload count was already one full-expert payload per expert miss/write. Marking all projection logical entries together only removed subsequent logical misses that were not causing additional physical uploads. The real upload-skip control point for physical bytes is earlier/narrower than the per-projection counter state changed here.
Needed expert knowledge: Need to distinguish logical projection hits from physical upload span elimination. Existing counters were enough to reject this patch because physical MiB/write count stayed unchanged.
Patch / commit: Archived failed patch: patches/failed_attempts/s6_detailed_expert_iter_01_fasttemp_p16_d16.patch; will revert runtime edit before next iteration.

## s6_detailed_expert_iter_02_fasttemp_p16_d16

Iteration ID: s6_detailed_expert_iter_02_fasttemp_p16_d16
Stage: s6_detailed_expert
Agent prompt setting: S6-Detailed-Expert-Mechanism MobileMoE-AKO
Baseline bottleneck decomposition: Baseline decode_tok_s=0.337842; mib_per_token=1431.802; decode_core_upload_mib=22908.835; decode_req_service_ms=23010.815; page_touch_ms=18198.863; enqueue_ms=4724.848; finish_ms=45.097; decode_req_miss=6810; decode_evict=6810; async submit/complete=177/177.
Targeted bottleneck: Decode-phase speculative asynchronous core prewarm work that submits and completes jobs without producing decode prewarm hits.
Expected diagnostic movement: If decode speculative prewarm is adding queue/service pressure without useful hit-path reuse, then disabling decode-only prewarm should reduce async submit/complete counts and required-miss service timing while leaving physical transfer volume, demand miss counts, generated tokens, and correctness stable.
Agent hypothesis: Observed anomaly: baseline whole-run async submit/complete=177/177, but decode pre_hit/pre_miss=0/0 and decode required physical upload volume stayed high. Verified runtime code path: submitAsyncPrewarmHybridColdGpuLayer is called with a phase string and gates prefill/decode async prewarm before layer resource setup and async work submission. Logical cache key: demand lookup remains the existing per-layer/expert/projection required cache state used by the hot path. Physical resource or upload span: unchanged required GPU-v3 core payload materialization/upload spans. State checked before materialization/upload: unchanged demand cache state in the required projection path. State updated after materialization/upload: unchanged required cache/materialization updates. Why the current state could cause repeated upload or service: decode speculative prewarm may enqueue extra work that competes with required materialization but is not represented as decode prewarm hits or physical upload avoidance in the measured hot path. Expected metric movement: async submit/complete drop; decode_req_service_ms and decode_tok_s improve; mib_per_token, decode_core_upload_mib, decode_req_mat_writes, decode_req_miss, and correctness remain stable. Guardrails that must remain stable: ret=0, generated=16/16, benchmark contract unchanged, mib_per_token no worse, physical upload not hidden.
Chosen optimization direction: Optimization iteration: disable decode-phase speculative async prewarm only, preserving prefill behavior and all required decode materialization.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; baseline and iter_02 metrics/summary files.
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Added an early decode-phase return in submitAsyncPrewarmHybridColdGpuLayer so decode speculative prewarm jobs are not submitted; required demand work and upload/cache logic are unchanged.
Benchmark command: cd /home/liuxu/projects/mobile-moe-ako && /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_detailed_expert_iter_02_fasttemp_p16_d16
Compile result: success; host md5 3d1abfa67ed9be97e18b3765e374987a, phone md5 matched, host/phone size 36912072, phone mode 0777
Correctness result: correct: ret=0, generated=16/16
Metrics:
  decode_tok_s: 0.34631229568386224
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1392.162437499999
  decode_req_page_touch_ms: 17905.768999999986
  decode_req_mat_enqueue_ms: 4308.959999999999
  decode_req_mat_finish_ms: 17.70499999999997
  decode_req_service_ms: 22274.598999999984
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 34.81672
Result: Correctness-passing modest win. decode_tok_s improved from 0.337842 to 0.346312 (+2.51%) and decode_req_service_ms improved from 23010.815 to 22274.599 (-736.216 ms, -3.20%). Normalized transfer and physical upload counters did not regress: mib_per_token stayed 1431.8021875, decode_core_upload_mib stayed 22908.835, page_touch_mib stayed 22908.835, and writes stayed 2270. Whole-run async submit/complete dropped from 177/177 to 27/27, while decode prewarm hits remained 0.
Agent diagnosis: This patch does not reduce physical transfer volume. It reduces unnecessary decode scheduling pressure around required-miss service. The causal signal is consistent because async work drops, total required service drops, enqueue/finish drop, correctness is stable, and physical transfer counters are unchanged rather than merely hidden. It is useful under the experiment rule allowing decode_tok_s improvement or material required-miss service reduction without transfer regression, but it is not a transfer-reducing residency repair.
My diagnosis: Best current patch is a scheduling/latency cleanup, not the desired physical-upload elimination. It avoids a logical-counter-only trap: the important physical counters are stable and the win comes from reduced service time, not reduced MiB.
Needed expert knowledge: The detailed residency model helped reject iter_01, but iter_02 needed scheduling-level knowledge: distinguish prewarm jobs that create actual future hit-path reuse from speculative work that only contends with required materialization.
Patch / commit: Committed useful runtime patch in mllm: 1f9a9be6 ([s6 detailed iter 02] Disable decode speculative prewarm). p32/d32 recheck required before final best selection.

## s6_detailed_expert_best_recheck_fasttemp_p32_d32

Iteration ID: s6_detailed_expert_best_recheck_fasttemp_p32_d32
Stage: s6_detailed_expert
Agent prompt setting: S6-Detailed-Expert-Mechanism MobileMoE-AKO
Baseline bottleneck decomposition: Best p16/d16 patch from iter_02 improved decode_tok_s 0.337842->0.346312 (+2.51%) and decode_req_service_ms 23010.815->22274.599 without changing mib_per_token or decode_core_upload_mib. Recheck is a p32/d32 signal run for the committed best patch, not a new optimization iteration.
Targeted bottleneck: Recheck committed decode speculative prewarm disablement at longer prompt/decode length.
Expected diagnostic movement: Correctness should hold at generated=32/32; async submit/complete should remain low at the prefill-only level; physical transfer remains visible rather than hidden.
Agent hypothesis: If iter_02 is a safe scheduling cleanup rather than benchmark-specific behavior, p32/d32 should complete correctly with the same runner md5 and no evidence of hidden required work. This recheck does not establish p32 speedup because no p32 baseline was run under this experiment's budget.
Chosen optimization direction: Best-patch recheck only; no source changes after commit 1f9a9be6.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; p32/d32 summary.jsonl; mllm git status/log.
Files modified: None in runtime.
Change summary: Rebuilt/deployed committed iter_02 runner and ran the fixed p32/d32 temperature-gated signal contract.
Benchmark command: cd /home/liuxu/projects/mobile-moe-ako && /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p32.jsonl --decode-tokens 32 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_detailed_expert_best_recheck_fasttemp_p32_d32
Compile result: success; committed source 1f9a9be651d0d5b0a0e96441290044429eeb0ae5; cmake/ninja reported no work to do for already-built runner; host md5 3d1abfa67ed9be97e18b3765e374987a, phone md5 matched, host/phone size 36912072, phone mode 0777.
Correctness result: correct: ret=0, generated=32/32
Metrics:
  decode_tok_s: 0.32041716713074586
  uploaded_expert_mib_per_token_metric: 1551.1785312499956
  required_miss_mib_per_token_metric: 1551.1785312499956
  overall_uploaded_expert_mib_per_token_metric: 3193.3838125
  overall_required_miss_service_ms_per_token_metric: 2992.251375
  decode_req_page_touch_ms: 39504.12499999997
  decode_req_mat_enqueue_ms: 9799.340999999986
  decode_req_mat_finish_ms: 28.749999999999762
  decode_req_service_ms: 49421.55499999998
  decode_req_mat_writes: 4885.0
  decode_req_page_touch_mib: 49637.71299999986
  decode_core_upload_mib: 49637.71299999986
  decode_req_miss: 14655.0
  decode_req_hit: 6849.0
  decode_evict: 14655.0
  cache_hit_rate: 0.31849888392857145
  hybrid_submit: 27
  hybrid_complete: 27
  peak_temp_skin_c_decode: 36.98804
Result: Best patch recheck passed correctness and deployment verification. The low async submit/complete signature from iter_02 persisted at p32/d32 (27/27). Physical transfer remained explicit: decode_core_upload_mib equaled decode_req_page_touch_mib, and no physical MiB reduction is claimed.
Agent diagnosis: The recheck supports iter_02 as a safe committed scheduling cleanup, but it does not convert it into a transfer-reducing runtime repair. The patch is best among this experiment's correctness-passing attempts because p16/d16 improved decode throughput and required-miss service without normalized-transfer regression.
My diagnosis: Stop after the recheck rather than running additional smoke attempts: iter_01 already showed the main logical-residency hypothesis can improve counters without moving physical bytes, and iter_02 provides a small useful win with a clean causal signature. Further transfer-reduction work likely needs deeper evidence about physical payload lifetime or a new diagnostic that was outside the remaining useful scope.
Needed expert knowledge: Detailed logical/physical residency knowledge was sufficient to avoid accepting a false hit-rate win, but finding an actual physical-transfer reduction appears to need more concrete knowledge of payload lifetime, cache capacity tradeoffs, or upload-span reuse than the inspected signals exposed.
Patch / commit: Best runtime patch remains mllm commit 1f9a9be6. No p32/d32 baseline was run; no evening verdict was run.

## s6_causal_gate_baseline_fasttemp_p16_d16

Iteration ID: s6_causal_gate_baseline_fasttemp_p16_d16
Stage: s6_causal_gate
Agent prompt setting: S6 causal control-surface gate baseline; no source edits
Baseline bottleneck decomposition: decode_tok_s=0.342980; mib_per_token=1431.802; required_miss_count=14736; decode_req_miss=6810; decode_req_hit=3942; decode_evict=6810; cache_hit_rate=0.3666; required_miss_wait_ms_per_token=1397.619; decode_req_service_ms=22361.906; page_touch=17971.771 ms/22908.835 MiB; mat_enqueue=4335.017 ms; mat_finish=12.516 ms; mat_writes=2270; decode_core_upload_mib=22908.835; peak_temp_skin_c_decode=32.2882; missing prewarm_hit_rate only. Existing counters are enough for first optimization; no diagnostic-only iteration needed.
Targeted bottleneck: Baseline/profiling only
Expected diagnostic movement: None; provenance and profiling entry only
Agent hypothesis: Baseline built and deployed from da9fa3534a16c0f34adb6709e2ba871741cbf8cc with verified host/phone md5 6d15f401a12e515d066141c3a02ba4ea and phone size 36912960 bytes.
Chosen optimization direction: Profile decode required-miss transfer/cache surface before any patch.
Files inspected: references/constraints.md; references/benchmark_instructions.md; references/metrics_schema.md; references/system_overview.md; summary.jsonl; parse_metrics.py; append_iteration.py; aot_run.cpp counter/cache path
Files modified: None
Change summary: No source change. ITERATIONS.md was backed up to ITERATIONS_BEFORE_s6_causal_gate_20260703_145932.md before baseline.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_causal_gate_baseline_fasttemp_p16_d16
Compile result: build ok; warnings only; host md5=6d15f401a12e515d066141c3a02ba4ea; phone md5=6d15f401a12e515d066141c3a02ba4ea; phone stat size=36912960 mode=0777
Correctness result: ret=0; generated=16/16
Metrics:
  decode_tok_s: 0.34298011347711416
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1397.6191249999993
  decode_req_page_touch_ms: 17971.771000000004
  decode_req_mat_enqueue_ms: 4335.016999999999
  decode_req_mat_finish_ms: 12.515999999999988
  decode_req_service_ms: 22361.905999999988
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 32.2882
Result: Valid baseline. Required-miss transfer service dominates decode-phase time; enough diagnostics exist to choose a first optimization without diagnostic-only instrumentation.
Agent diagnosis: Baseline decode bottleneck is dynamic required-miss core upload/page-touch/materialization service under cache pressure: 6810 decode misses and 6810 decode evictions with 22908.835 MiB uploaded in decode.
My diagnosis: The causal gate should focus first on a runtime policy path that changes required-miss/cache residency behavior and predicts reduced decode_req_miss/decode_evict/mib_per_token/service time, not on parser or benchmark surfaces.
Needed expert knowledge: No prior S6 mechanism used. Need only code-local knowledge of executor cache/eviction policy and benchmark counters.
Patch / commit: baseline only; no patch

## s6_causal_gate_iter_01_gate

Iteration ID: s6_causal_gate_iter_01_gate
Stage: s6_causal_gate
Agent prompt setting: S6 causal control-surface gate; pre-edit gate for iter_01
Baseline bottleneck decomposition: Baseline decode path: decode_tok_s=0.342980; mib_per_token=1431.802; decode_req_miss=6810; decode_evict=6810; cache_hit_rate=0.3666; decode_req_service_ms=22361.906; page_touch=17971.771 ms; mat_enqueue=4335.017 ms; mat_finish=12.516 ms; decode_core_upload_mib=22908.835.
Targeted bottleneck: Required-miss materialization batching/enqueue overhead in decode core uploads, not logical cache hit rate.
Expected diagnostic movement: Primary: decode_tok_s up. Diagnostics: decode_req_mat_enqueue_ms and decode_req_service_ms should fall; decode_req_page_touch_mib/decode_core_upload_mib and decode_req_miss may stay similar; mat_writes may fall if larger chunks coalesce writes; cache_hit_rate should not be the claimed mechanism. Guardrails: correct true, generated=16, mib_per_token must not increase materially, peak temp comparable.
Agent hypothesis: Gate answers: 1 bottleneck required-miss upload materialization service, especially enqueue time after page touch. 2 Patch changes runtime policy decision required_batch_upload_experts_, the max required misses grouped per materializeCoreSlotBatchGpuV3 chunk. 3 The state is initialized in Qwen2MoeTDAOTRunner defaults/env parsing and executed in ensureExpertsCachedBatchGpuV3/materializeCoreSlotBatchGpuV3 in examples/qwen2_moe_td_qnn_aot/aot_run.cpp. 4 It is on the fixed benchmark critical path because baseline decode has 6810 required misses, 2270 materialization writes, and 22.36 s required-miss service for 16 decode tokens. 5 Primary metric decode_tok_s should improve. 6 Secondary diagnostics should show lower decode_req_mat_enqueue_ms, lower decode_req_service_ms, possibly fewer decode_req_mat_writes; transfer MiB and miss count should not be used as the win. 7 Guardrails are correct=true, generated token count, mib_per_token, required transfer volume, thermal, unchanged benchmark contract. 8 Falsified if enqueue/service do not fall, correctness fails, or speed does not improve beyond smoke noise. 9 False positive risk: small tok/s gain from thermal/noise while transfer and service diagnostics do not move, or enqueue falls while page touch/finish rises similarly. 10 Yes: if expected diagnostic movement does not appear, reject/archive this patch.
Chosen optimization direction: Increase required core upload batch size from 4 to 8 to reduce per-batch enqueue overhead while preserving the same required uploads and model work.
Files inspected: aot_run.cpp: defaults/env parsing, HybridColdGpuShadowExecutor constructor, ensureExpertsCachedBatchGpuV3, materializeCoreSlotBatchGpuV3, baseline summary metrics
Files modified: Pending: examples/qwen2_moe_td_qnn_aot/aot_run.cpp only
Change summary: Pre-edit gate only; no source change yet.
Benchmark command: pending exact p16/d16 Tucker contract for s6_causal_gate_iter_01_fasttemp_p16_d16
Compile result: not run yet
Correctness result: not run yet
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
Result: Gate answered before edit.
Agent diagnosis: The patch is falsifiable through service/enqueue diagnostics and does not rely on parser or benchmark changes.
My diagnosis: This is a narrow control-surface patch: required upload batching. It should be rejected if only cache counters or noisy tok/s move.
Needed expert knowledge: No prior S6 mechanism used; code-local batching path only.
Patch / commit: pending

## s6_causal_gate_iter_01_fasttemp_p16_d16

Iteration ID: s6_causal_gate_iter_01_fasttemp_p16_d16
Stage: s6_causal_gate
Agent prompt setting: S6 causal control-surface gate optimization iter 01
Baseline bottleneck decomposition: Baseline decode_tok_s=0.342980; mib_per_token=1431.802; decode_req_miss=6810; decode_evict=6810; decode_req_service_ms=22361.906; decode_req_mat_enqueue_ms=4335.017; decode_req_page_touch_ms=17971.771; decode_req_mat_finish_ms=12.516; decode_core_upload_mib=22908.835.
Targeted bottleneck: Required-miss materialization batching/enqueue overhead.
Expected diagnostic movement: Expected decode_req_mat_enqueue_ms and decode_req_service_ms down, mat_writes possibly down, decode_tok_s up, mib_per_token not worse. Rejection criterion: reject if enqueue/service do not improve even if primary has a small noisy gain.
Agent hypothesis: Increase required_batch_upload_experts_ from 4 to 8 to reduce per-batch enqueue overhead in ensureExpertsCachedBatchGpuV3/materializeCoreSlotBatchGpuV3 without changing required uploads or benchmark work.
Chosen optimization direction: Required core upload batching policy.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp required miss batching path; baseline metrics; iter_01 summary/metrics.
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Changed default hybrid_gpu_required_batch_upload_experts_ from 4 to 8.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_causal_gate_iter_01_fasttemp_p16_d16
Compile result: build ok; warnings only; host md5=3e5c5a1dbf5c479a6d549f096ab0e0ee; phone md5=3e5c5a1dbf5c479a6d549f096ab0e0ee; phone stat size=36912960 mode=0777
Correctness result: ret=0; generated=16/16
Metrics:
  decode_tok_s: 0.3454545042355421
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1407.8427499999984
  decode_req_page_touch_ms: 17922.46600000001
  decode_req_mat_enqueue_ms: 4548.768000000004
  decode_req_mat_finish_ms: 12.377999999999993
  decode_req_service_ms: 22525.483999999975
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 33.76336
Result: Rejected/archived despite correct run and +0.72% tok/s: expected diagnostics contradicted hypothesis. decode_req_mat_enqueue worsened 4335.017 -> 4548.768 ms; decode_req_service worsened 22361.906 -> 22525.484 ms; required_miss_wait worsened 1397.619 -> 1407.843 ms/token; mib_per_token unchanged. Primary improvement is below normal smoke noise and unsupported.
Agent diagnosis: The causal gate prevented accepting a noisy primary-only gain. Larger batch size did not reduce enqueue/service; it slightly worsened the targeted path.
My diagnosis: False positive type observed: small decode_tok_s gain without consistent diagnostics. Reject and revert before next hypothesis.
Needed expert knowledge: No extra expert knowledge; the failure is visible from code-local service decomposition.
Patch / commit: archived patches/failed_attempts/s6_causal_gate_iter_01_fasttemp_p16_d16.patch; reverted before next iteration

## s6_causal_gate_iter_02_gate

Iteration ID: s6_causal_gate_iter_02_gate
Stage: s6_causal_gate
Agent prompt setting: S6 causal control-surface gate; pre-edit gate for iter_02
Baseline bottleneck decomposition: Baseline decode_tok_s=0.342980; mib_per_token=1431.802; decode_req_miss=6810; decode_evict=6810; cache_hit_rate=0.3666; required_miss_wait_ms_per_token=1397.619; decode_req_service_ms=22361.906; decode_req_page_touch_ms=17971.771; decode_req_mat_enqueue_ms=4335.017; decode_req_mat_finish_ms=12.516; decode_req_page_touch_mib=22908.835; decode_core_upload_mib=22908.835. Prior iter_01 rejected: source default was also an env-overridden surface and diagnostics contradicted batching hypothesis.
Targeted bottleneck: Explicit host page-touch in the required core upload path.
Expected diagnostic movement: Expected decode_req_page_touch_ms and decode_req_page_touch_mib sharply down. The patch is only useful if decode_req_service_ms and required_miss_wait_ms_per_token fall too. decode_req_mat_enqueue_ms/finish may rise if page faults move into OpenCL writes; accept only if total service and decode_tok_s improve without mib_per_token regression.
Agent hypothesis: Gate answers: 1 bottleneck targeted is decode required-miss service dominated by explicit mmap page-touch before required OpenCL payload writes. 2 Patch changes the resource path for required packed payload upload by removing explicit touchMmapPages from the mode-2 required upload loop; payload bytes are still uploaded to the same OpenCL arena. 3 The path is executed in HybridColdGpuShadowExecutor::materializeCoreSlotBatchGpuV3 from ensureExpertsCachedBatchGpuV3/runProjectionImplGpuV3 in examples/qwen2_moe_td_qnn_aot/aot_run.cpp when the fixed Tucker runner sets CORE_PAGE_TOUCH_MODE=2 and expert payload arena flags. 4 It is on the fixed benchmark critical path because baseline decode reports 22908.835 MiB page-touched and 17971.771 ms page-touch inside required-miss service. 5 Primary metric decode_tok_s should improve. 6 Secondary diagnostics should show page-touch ms/MiB down and total required service down; enqueue/finish must not increase by a similar or larger amount. 7 Guardrails: correct=true, generated=16, mib_per_token and decode_core_upload_mib not worse, same benchmark contract and verified deployment. 8 Falsified if page-touch drops but enqueue/finish or service time absorbs the work, if correctness fails, if transfer volume worsens, or if speed gain is only noisy. 9 False positive risk: local page-touch counter improves because accounting moved to enqueue/finish while end-to-end throughput does not improve. 10 Yes: if expected total-service movement does not appear, reject/archive this patch.
Chosen optimization direction: Remove explicit page-touch from the active required packed payload upload loop while leaving the OpenCL writes and bytes unchanged.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp materializeCoreSlotBatchGpuV3, runProjectionImplGpuV3, Tucker qwen env flags, baseline summary/log diagnostics
Files modified: Pending: examples/qwen2_moe_td_qnn_aot/aot_run.cpp only
Change summary: Pre-edit gate only; no source change yet.
Benchmark command: pending exact p16/d16 Tucker contract for s6_causal_gate_iter_02_fasttemp_p16_d16
Compile result: not run yet
Correctness result: not run yet
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
Result: Gate answered before edit.
Agent diagnosis: This patch directly tests a page-touch resource-path hypothesis and has a built-in false-positive check.
My diagnosis: Do not accept local page-touch improvement alone; total required service and primary metric must support it.
Needed expert knowledge: No prior S6 mechanism used; code-local page-touch path and benchmark counters only.
Patch / commit: pending

## s6_causal_gate_iter_02_fasttemp_p16_d16

Iteration ID: s6_causal_gate_iter_02_fasttemp_p16_d16
Stage: s6_causal_gate
Agent prompt setting: S6 causal control-surface gate optimization iter 02
Baseline bottleneck decomposition: Baseline decode_tok_s=0.342980; mib_per_token=1431.802; decode_req_miss=6810; decode_evict=6810; decode_req_page_touch_ms=17971.771; decode_req_page_touch_mib=22908.835; decode_req_mat_enqueue_ms=4335.017; decode_req_service_ms=22361.906.
Targeted bottleneck: Explicit host page-touch in required packed payload upload path.
Expected diagnostic movement: Expected decode_req_page_touch_ms/MiB down and decode_req_service_ms down; reject if page-touch did not move or if enqueue/service contradicted.
Agent hypothesis: Remove explicit touchMmapPages from the presumed active materializeCoreSlotBatchGpuV3 packed-payload upload loop while preserving OpenCL writes and transfer bytes.
Chosen optimization direction: Required upload page-touch resource path.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp materializeCoreSlotBatchGpuV3; Tucker environment flags; baseline/iter metrics.
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Removed touchMmapPages/accounting from one packed-payload upload loop.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_causal_gate_iter_02_fasttemp_p16_d16
Compile result: build ok; warnings only; host md5=7d5f144ea71b1e6ccfe20f9e9c3ce5e8; phone md5=7d5f144ea71b1e6ccfe20f9e9c3ce5e8; phone stat size=36912952 mode=0777
Correctness result: ret=0; generated=16/16
Metrics:
  decode_tok_s: 0.3447258400780201
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1414.297999999999
  decode_req_page_touch_ms: 17744.887999999995
  decode_req_mat_enqueue_ms: 4833.260000000002
  decode_req_mat_finish_ms: 9.539999999999996
  decode_req_service_ms: 22628.767999999985
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 34.5036
Result: Rejected/archived. decode_tok_s +0.51% is below smoke noise and unsupported. Expected page-touch diagnostic did not move materially: page_touch_ms 17971.771 -> 17744.888, page_touch_mib unchanged 22908.835, while enqueue worsened 4335.017 -> 4833.260 and service worsened 22361.906 -> 22628.768. This falsifies the edited path/hypothesis.
Agent diagnosis: The gate exposed wrong file/path localization: the active benchmark still reported the same page-touch MiB, so the patch did not change the intended resource path.
My diagnosis: False positive avoided: small primary gain plus local-diagnostic mismatch. Next attempt must either edit the actual active page-touch path or switch hypotheses; do not accept this.
Needed expert knowledge: No external expert hint needed; the mismatch is visible from page_touch_mib and service counters.
Patch / commit: archived patches/failed_attempts/s6_causal_gate_iter_02_fasttemp_p16_d16.patch; reverted before next iteration

## s6_causal_gate_iter_03_gate

Iteration ID: s6_causal_gate_iter_03_gate
Stage: s6_causal_gate
Agent prompt setting: S6 causal control-surface gate; pre-edit gate for iter_03
Baseline bottleneck decomposition: Baseline decode_tok_s=0.342980; mib_per_token=1431.802; decode_req_miss=6810; decode_evict=6810; decode_req_page_touch_ms=17971.771; decode_req_page_touch_mib=22908.835; decode_req_mat_enqueue_ms=4335.017; decode_req_service_ms=22361.906. Iter_02 proved the second page-touch loop was not the active page-touch source because page_touch_mib stayed unchanged.
Targeted bottleneck: Explicit host page-touch in the other required packed payload upload loop, now localized by the failed iter_02 diagnostic.
Expected diagnostic movement: Expected decode_req_page_touch_ms and decode_req_page_touch_mib near zero or sharply down. Accept only if decode_req_service_ms and required_miss_wait_ms_per_token fall, decode_tok_s improves meaningfully, and mib_per_token/decode_core_upload_mib/correctness do not regress. Reject if enqueue/finish absorbs the cost or if only local page-touch improves.
Agent hypothesis: Gate answers: 1 bottleneck is decode required-miss service dominated by explicit mmap page-touch. 2 Patch changes the active required resource path by skipping touchMmapPages in materializeCoreSlotBatchGpuV3 when external payload arena path has pc.payload_base==0. 3 This code is executed from ensureExpertsCachedBatchGpuV3/runProjectionImplGpuV3 in examples/qwen2_moe_td_qnn_aot/aot_run.cpp under fixed Tucker flags CORE_PAGE_TOUCH_MODE=2, PACKED_PAYLOAD_ARENA=1, EXPERT_PAYLOAD_ARENA=1. 4 It is on the benchmark critical path because baseline and iter_02 still report 22908.835 MiB page-touch in decode. 5 Primary metric decode_tok_s should improve. 6 Secondary diagnostics: page_touch_ms/MiB down, service ms down; enqueue/finish must not rise enough to cancel it. 7 Guardrails: correct true, generated=16, mib_per_token unchanged/not worse, transfer MiB unchanged, thermal comparable, exact benchmark contract. 8 Falsified if page-touch does not move, service does not improve, correctness fails, or primary gain is noisy/unsupported. 9 False positive: page-touch accounting drops while end-to-end service/throughput do not improve because faults move into clEnqueueWriteBuffer. 10 Yes, reject/archive if expected diagnostic movement does not appear.
Chosen optimization direction: Remove explicit page-touch from the now-localized active required payload upload loop only.
Files inspected: aot_run.cpp two page-touch loops; iter_02 metrics proving previous localization was wrong; Tucker env flags; baseline diagnostics.
Files modified: Pending: examples/qwen2_moe_td_qnn_aot/aot_run.cpp only
Change summary: Pre-edit gate only; no source change yet.
Benchmark command: pending exact p16/d16 Tucker contract for s6_causal_gate_iter_03_fasttemp_p16_d16
Compile result: not run yet
Correctness result: not run yet
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
Result: Gate answered before edit.
Agent diagnosis: This is a localization-correction experiment on the same page-touch bottleneck, with strict rejection if service/throughput do not support it.
My diagnosis: The causal gate is preventing a local-counter-only acceptance; total service remains the decisive diagnostic.
Needed expert knowledge: No prior S6 mechanism used; only direct code path localization from iter_02 diagnostics.
Patch / commit: pending

## s6_causal_gate_iter_03_fasttemp_p16_d16

Iteration ID: s6_causal_gate_iter_03_fasttemp_p16_d16
Stage: s6_causal_gate
Agent prompt setting: S6 causal control-surface gate optimization iter 03
Baseline bottleneck decomposition: Baseline decode_tok_s=0.342980; mib_per_token=1431.802; decode_req_miss=6810; decode_evict=6810; decode_req_page_touch_ms=17971.771; decode_req_page_touch_mib=22908.835; decode_req_mat_enqueue_ms=4335.017; decode_req_mat_finish_ms=12.516; decode_req_service_ms=22361.906.
Targeted bottleneck: Explicit host page-touch in the active required packed payload upload loop.
Expected diagnostic movement: Expected page_touch_ms/MiB down, total service down, and no compensating enqueue/finish increase. Reject if page-touch accounting merely shifts into OpenCL enqueue/finish.
Agent hypothesis: Remove touchMmapPages/accounting from the materializeCoreSlotBatchGpuV3 external-payload loop localized by iter_02.
Chosen optimization direction: Required upload page-touch resource path, localization-corrected.
Files inspected: aot_run.cpp two page-touch loops; iter_02 metrics; iter_03 metrics.
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Removed explicit touchMmapPages/accounting from the first packed-payload required upload loop.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_causal_gate_iter_03_fasttemp_p16_d16
Compile result: build ok; warnings only; host md5=74081522a41f802faee6a2745ad81f46; phone md5=74081522a41f802faee6a2745ad81f46; phone stat size=36912032 mode=0777
Correctness result: ret=0; generated=16/16
Metrics:
  decode_tok_s: 0.3460339844734119
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1380.4202499999988
  decode_req_page_touch_ms: 0.0
  decode_req_mat_enqueue_ms: 14324.9
  decode_req_mat_finish_ms: 7719.218999999998
  decode_req_service_ms: 22086.72399999998
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 0.0
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 35.09868
Result: Rejected/archived. Page-touch local counter moved as expected (17971.771 ms/22908.835 MiB -> 0), but diagnostics contradicted a real speedup: decode_req_mat_enqueue worsened 4335.017 -> 14324.900 ms, decode_req_mat_finish worsened 12.516 -> 7719.219 ms, required_miss_wait improved only 1397.619 -> 1380.420 ms/token while overall metric summary showed overall required service worse in raw summary. Primary +0.89% is below smoke-noise acceptance threshold and unsupported by the resource-path decomposition.
Agent diagnosis: The gate caught a local diagnostic false positive: removing explicit touch moved page-fault/synchronization cost into enqueue/finish rather than reducing the critical path.
My diagnosis: No useful patch on the page-touch surface. Together with iter_01, three attempts produced hypothesis mismatch/no-signal; stop rather than drift into unrelated control surfaces.
Needed expert knowledge: No prior S6 mechanism used. A better path likely needs deeper model/runtime-specific cache residency knowledge beyond this prompt gate.
Patch / commit: archived patches/failed_attempts/s6_causal_gate_iter_03_fasttemp_p16_d16.patch; reverted; no accepted patch

## s6_causal_gate_final_summary

Iteration ID: s6_causal_gate_final_summary
Stage: s6_causal_gate
Agent prompt setting: S6 causal control-surface gate final closure
Baseline bottleneck decomposition: Valid baseline from da9fa3534a16c0f34adb6709e2ba871741cbf8cc: decode_tok_s=0.342980; mib_per_token=1431.802; required_miss_count=14736; decode_req_miss=6810; decode_req_hit=3942; decode_evict=6810; cache_hit_rate=0.3666; required_miss_wait_ms_per_token=1397.619; decode_req_page_touch_ms=17971.771; decode_req_mat_enqueue_ms=4335.017; decode_req_mat_finish_ms=12.516; decode_req_service_ms=22361.906; decode_req_mat_writes=2270; decode_req_page_touch_mib=22908.835; decode_core_upload_mib=22908.835; peak_temp_skin_c_decode=32.2882.
Targeted bottleneck: No accepted target after three falsified/no-signal attempts.
Expected diagnostic movement: Final conclusion: causal gate required diagnostic consistency; none of the small primary gains was accepted because diagnostics contradicted or failed the hypothesis.
Agent hypothesis: The experiment tested whether explicit causal gates improve controllability. Evidence: iter_01 rejected a primary-only +0.72% gain because service/enqueue worsened; iter_02 rejected wrong-path localization because page_touch_mib did not move; iter_03 rejected local page-touch success because cost shifted into enqueue/finish and speedup was <1%.
Chosen optimization direction: Stop early after three consecutive no-signal/hypothesis-mismatch iterations; no p32/d32 recheck because no correctness-passing patch met acceptance criteria.
Files inspected: mllm aot_run.cpp; OpenCL MoE policy helpers; Tucker runner env flags; baseline/iteration metrics and logs.
Files modified: None remaining; runtime repo clean after reverting failed edits.
Change summary: No useful patch selected. Failed attempts archived under patches/failed_attempts/s6_causal_gate_iter_01/02/03_fasttemp_p16_d16.patch.
Benchmark command: No final benchmark; p32/d32 skipped because no accepted best patch.
Compile result: All benchmarked iterations built and deployed with host/phone md5 verification. Baseline md5=6d15f401a12e515d066141c3a02ba4ea; iter01=3e5c5a1dbf5c479a6d549f096ab0e0ee; iter02=7d5f144ea71b1e6ccfe20f9e9c3ce5e8; iter03=74081522a41f802faee6a2745ad81f46.
Correctness result: Baseline and iterations 01-03 all ret=0 generated=16/16.
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
Result: No useful patch. The causal gate reduced false positives and control-surface drift by forcing rejection of unsupported primary gains and stopping before unrelated edits.
Agent diagnosis: Prompt-level causal gating improved iteration hygiene: it localized failed hypotheses, made falsification explicit, and prevented accepting noisy or local-counter-only wins. It did not itself supply the missing runtime-specific optimization mechanism.
My diagnosis: This suggests prompt-level control helps reliability but tool/harness-level controls remain essential: md5 deployment checks, fixed thermal benchmark, structured diagnostics, and parser guardrails were what made contradictions visible.
Needed expert knowledge: A productive next direction likely needs deeper runtime-specific cache-residency reasoning beyond this allowed prompt context; not prior S6 content.
Patch / commit: No commit; repo clean. ITERATIONS.md appended; backup preserved at ITERATIONS_BEFORE_s6_causal_gate_20260703_145932.md.

## s6_skill_loop_baseline_fasttemp_p16_d16

Iteration ID: s6_skill_loop_baseline_fasttemp_p16_d16
Stage: s6_skill_control_loop
Agent prompt setting: S6 skill-level diagnosis-aware control loop; baseline rebuilt from clean pre-success base
Baseline bottleneck decomposition: Baseline reference before edits. Provenance: branch exp/s6-skill-control-loop at da9fa3534a16c0f34adb6709e2ba871741cbf8cc; rebuilt target mllm-qwen2-moe-td-qnn-aot-runner; host md5 6d15f401a12e515d066141c3a02ba4ea; phone md5 6d15f401a12e515d066141c3a02ba4ea; phone stat size 36912960 mode 0777 path /data/local/tmp/qwen2_moe_td_w8a16_clean_20260527/mllm-qwen2-moe-td-qnn-aot-runner.
Targeted bottleneck: none: baseline only
Expected diagnostic movement: none: baseline only
Agent hypothesis: No source edits; establish fixed p16/d16 thermal-gated baseline from exact clean source.
Chosen optimization direction: baseline provenance and metric capture
Files inspected: SKILL.md; references/constraints.md; references/benchmark_instructions.md; references/metrics_schema.md; baseline summary artifacts
Files modified: none
Change summary: No source changes. Backed up ITERATIONS.md before run and recorded baseline metrics.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_skill_loop_baseline_fasttemp_p16_d16
Compile result: success; rebuilt from da9fa3534a16c0f34adb6709e2ba871741cbf8cc
Correctness result: ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.3349094731321387
  mib_per_token: 1431.8021875
  required_miss_count: 6810.0
  upload_bytes: 24021654568
  prewarm_hit_rate: None
  eviction_churn: 6810.0
  required_miss_wait_ms_per_token: 1463.085687499999
  decode_req_page_touch_ms: 18437.081999999988
  decode_req_mat_enqueue_ms: 4888.876999999998
  decode_req_mat_finish_ms: 41.505000000000145
  decode_req_service_ms: 23409.370999999985
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 32.30796
Result: baseline_reference: correct p16/d16 baseline, not an optimization result class
Agent diagnosis: Baseline is transfer/service dominated: decode_tok_s 0.334909; mib_per_token 1431.802; decode_req_miss 6810; decode_evict 6810; required_miss_wait_ms_per_token 1463.086; cache_hit_rate 0.3666; peak skin decode 32.31C.
My diagnosis: Use this as the single experiment baseline. The result is valid because build/deploy/md5/stat were verified before benchmarking.
Needed expert knowledge: None beyond allowed general MobileMoE runtime concepts and skill workflow.
Patch / commit: no patch; log backup /home/liuxu/projects/mobile-moe-ako/ITERATIONS_BEFORE_s6_skill_control_loop_20260703_162926.md

## s6_skill_loop_bottleneck_localization

Iteration ID: s6_skill_loop_bottleneck_localization
Stage: s6_skill_control_loop
Agent prompt setting: Diagnosis-aware control loop report before first source edit
Baseline bottleneck decomposition: Observed bottleneck pattern: transfer-heavy decode with demand-miss service and cache churn. Evidence: decode_tok_s 0.334909; mib_per_token 1431.802; decode_req_miss 6810; decode_req_hit 3942; decode_evict 6810; cache_hit_rate 0.3666; decode_req_service_ms 23409.371; required_miss_wait_ms_per_token 1463.086; decode_req_page_touch_ms 18437.082; decode_req_mat_enqueue_ms 4888.877; decode_core_upload_mib 22908.835; peak_temp_skin_c_decode 32.31C.
Targeted bottleneck: Candidate control surfaces: cache admission/residency state for decode payloads, demand-miss materialization/upload path, eviction policy under gpu-cache-capacity=8, and prewarm/scheduling decisions if they affect required-miss pressure.
Expected diagnostic movement: A valid optimization should improve decode_tok_s and reduce or at least not worsen mib_per_token, decode_req_miss/evict, decode_req_service_ms, page_touch/enqueue service, or physical upload MiB consistently with its hypothesis.
Agent hypothesis: No patch yet. Search code for counter-linked runtime state before choosing a control surface.
Chosen optimization direction: code search targets: req_miss, req_hit, evict, resident, page_touch, mat_enqueue, gpu_cache_capacity, cache slot/arena state, decode hybrid execution
Files inspected: baseline metrics and summary artifacts only; source inspection begins after this report
Files modified: none
Change summary: Logged pre-edit bottleneck localization report. Avoid-first directions: no benchmark/parser/correctness/model/accounting edits, no generic kernel or lm-head tuning first, no acceptance based on logical counters alone.
Benchmark command: none: localization report only
Compile result: not applicable
Correctness result: not applicable
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
Result: localization_report: required pre-edit control-loop artifact
Agent diagnosis: Observation gap: prewarm_hit_rate unavailable, but required-miss decomposition is sufficient for first optimization hypothesis; no diagnostic-only iteration needed before code inspection.
My diagnosis: The report translates baseline metrics into candidate runtime control surfaces and search targets before any source edit, satisfying the skill-level gate.
Needed expert knowledge: None beyond allowed runtime policy, caching behavior, transfer volume, service diagnostics, scheduling/prewarm concepts, thermal/noise guardrails.
Patch / commit: no patch

## s6_skill_loop_iter_01_fasttemp_p16_d16

Iteration ID: s6_skill_loop_iter_01_fasttemp_p16_d16
Stage: s6_skill_control_loop
Agent prompt setting: S6 skill-level diagnosis-aware control loop
Baseline bottleneck decomposition: Baseline transfer/service bottleneck: decode_tok_s 0.334909; mib_per_token 1431.802; decode_req_miss 6810; decode_evict 6810; cache_hit_rate 0.3666; decode_req_service_ms 23409.371; decode_core_upload_mib 22908.835.
Targeted bottleneck: Decode required-miss service and transfer churn from evicting recently reused/hot required core payloads.
Expected diagnostic movement: Expected lower mib_per_token, decode_req_miss/evict, decode_req_service_ms, page_touch/enqueue, and physical upload MiB; hot-resident counters could move but were not sufficient alone.
Agent hypothesis: Enable the existing hot-resident core cache policy by default so required decode payloads are less likely to be evicted under gpu-cache-capacity=8.
Chosen optimization direction: cache residency/eviction policy default
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp around Qwen2MoeTDRunner env wiring, HybridColdGpuShadowExecutor constructor, selectCacheVictim, noteRequiredExperts, required cache paths, and baseline/iter logs.
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Changed hybrid_gpu_hot_resident_core_ default false->true. Active run logs later showed both baseline and iter already had hot_resident_core=true from environment, so this did not change the active policy.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_skill_loop_iter_01_fasttemp_p16_d16
Compile result: success; host md5 6040c0c0ae9d300dac0cbe2cad102a8c; phone md5 6040c0c0ae9d300dac0cbe2cad102a8c; phone stat size 36912952 mode 0777
Correctness result: ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.34194973283360514
  mib_per_token: 1431.8021875
  required_miss_count: 6810.0
  upload_bytes: 24021654568
  prewarm_hit_rate: None
  eviction_churn: 6810.0
  required_miss_wait_ms_per_token: 1425.304187500001
  decode_req_page_touch_ms: 18139.502999999997
  decode_req_mat_enqueue_ms: 4600.84
  decode_req_mat_finish_ms: 23.094999999999956
  decode_req_service_ms: 22804.867000000017
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 33.42668
Result: noise_or_no_signal: decode_tok_s +2.1%, but mib_per_token, decode_req_miss, decode_evict, cache hit rate, and physical upload MiB were unchanged; logs show the intended knob was already active in baseline, so the patch hypothesis was not actually exercised.
Agent diagnosis: Do not accept. This is a controlled false-positive catch: small throughput improvement without causal diagnostic movement and without an active control-surface change.
My diagnosis: Rejected/archive. The patch is a hypothesis mismatch because benchmark environment already set hot_resident_core=true; physical transfer/service counters contradict accepting it as a system win.
Needed expert knowledge: No forbidden prior mechanism used. General cache-policy inspection plus log provenance was sufficient to reject.
Patch / commit: archived /home/liuxu/projects/mobile-moe-ako/patches/failed_attempts/s6_skill_loop_iter_01_fasttemp_p16_d16.patch; no commit

## s6_skill_loop_iter_02_fasttemp_p16_d16

Iteration ID: s6_skill_loop_iter_02_fasttemp_p16_d16
Stage: s6_skill_control_loop
Agent prompt setting: S6 skill-level diagnosis-aware control loop
Baseline bottleneck decomposition: Baseline transfer/service bottleneck: decode_tok_s 0.334909; mib_per_token 1431.802; decode_req_miss 6810; decode_evict 6810; cache_hit_rate 0.3666; decode_req_service_ms 23409.371; decode_req_page_touch_mib/core_upload_mib 22908.835.
Targeted bottleneck: Inflated logical required misses/evictions from filling one external expert-payload arena through separate projection cache paths.
Expected diagnostic movement: Expected lower decode_req_miss, decode_evict, mib_per_token, decode_core_upload_mib, decode_req_page_touch_mib/ms, decode_req_mat_writes, and decode_req_service_ms, with correctness preserved.
Agent hypothesis: Use existing full expert-payload cache-fill helper for the active gate projection path so the shared payload arena records gate/up/down cache entries from a single combined required payload fill.
Chosen optimization direction: required cache fill path for GPU v3 external expert-payload arena
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp: getProjectionCacheGpuV3, bindExpertPayloadArenaNoLock, ensureExpertsCachedBatchGpuV3, ensureExpertsPackedCachedBatchGpuV3, runProjectionImplGpuV3; baseline logs confirming packed_payload=1 external_payload=1 expert payload arenas.
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: In runProjectionImplGpuV3, routed the gate/external-payload path through ensureExpertsPackedCachedBatchGpuV3; up/down then saw populated cache entries. No benchmark or parser changes.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_skill_loop_iter_02_fasttemp_p16_d16
Compile result: success; host md5 83fa8d8ab41b48368977b219eed70612; phone md5 83fa8d8ab41b48368977b219eed70612; phone stat size 37175104 mode 0777
Correctness result: ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.3412670310644927
  mib_per_token: 1431.8021875
  required_miss_count: 2270.0
  upload_bytes: 24021654568
  prewarm_hit_rate: None
  eviction_churn: 2270.0
  required_miss_wait_ms_per_token: 1430.9593750000001
  decode_req_page_touch_ms: 18111.241000000013
  decode_req_mat_enqueue_ms: 4723.864999999996
  decode_req_mat_finish_ms: 32.97099999999991
  decode_req_service_ms: 22895.350000000002
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 2270.0
  decode_req_hit: 8482.0
  decode_evict: 2270.0
  cache_hit_rate: 0.7888764880952381
  peak_temp_skin_c_decode: 33.98984
Result: logical_counter_only: decode_req_miss 6810->2270 and cache_hit_rate 0.3666->0.7889, but mib_per_token, decode_core_upload_mib, decode_req_page_touch_mib, decode_req_mat_writes, and physical transfer volume were unchanged; decode_tok_s +1.9% is not enough without physical diagnostic support.
Agent diagnosis: Rejected/archive. The patch improved logical hit/miss accounting but did not reduce real transfer or page-touch volume, contradicting the acceptance hypothesis.
My diagnosis: This is a useful false-positive catch: correctness passed and counters looked better, but diagnostics show no physical transfer win. Do not select as best patch.
Needed expert knowledge: No forbidden prior mechanism used; conclusion came from current code path and diagnostics. More detailed physical upload accounting would help separate logical entry bookkeeping from actual bytes written.
Patch / commit: archived /home/liuxu/projects/mobile-moe-ako/patches/failed_attempts/s6_skill_loop_iter_02_fasttemp_p16_d16.patch; no commit

## s6_skill_loop_iter_03_compile_fail

Iteration ID: s6_skill_loop_iter_03_compile_fail
Stage: s6_skill_control_loop
Agent prompt setting: S6 skill-level diagnosis-aware control loop
Baseline bottleneck decomposition: Baseline transfer/service bottleneck: decode_tok_s 0.334909; mib_per_token 1431.802; decode_req_page_touch_ms 18437.082; decode_req_page_touch_mib/core_upload_mib 22908.835; decode_req_service_ms 23409.371.
Targeted bottleneck: Explicit required mmap page-touch before OpenCL payload writes.
Expected diagnostic movement: Expected page-touch ms/MiB down sharply, total required service down, decode_tok_s up, with decode_core_upload_mib and mib_per_token still explicit and correctness preserved.
Agent hypothesis: Add an env-guarded early return in touchMmapPages so the required upload path skips synchronous pre-touch while preserving the same upload spans.
Chosen optimization direction: required payload resource path: page-touch behavior
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp touchMmapPages; materializeCoreSlotBatchGpuV3 page-touch loops; baseline required page-touch diagnostics.
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: First iter_03 patch used td_env_bool inside a file-scope helper before td_env_bool was declared.
Benchmark command: not run: compile failed before deploy/benchmark
Compile result: failed: use of undeclared identifier td_env_bool in touchMmapPages
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
Result: invalid: compile failure before benchmark
Agent diagnosis: Compile failure due to helper declaration order, not a benchmark result. Archive before repairing.
My diagnosis: This is a straightforward implementation error. It does not falsify the page-touch hypothesis, but counts as one compile failure in stop budget.
Needed expert knowledge: None.
Patch / commit: archived /home/liuxu/projects/mobile-moe-ako/patches/failed_attempts/s6_skill_loop_iter_03_compile_fail.patch; no commit

## s6_skill_loop_iter_03_fasttemp_p16_d16

Iteration ID: s6_skill_loop_iter_03_fasttemp_p16_d16
Stage: s6_skill_control_loop
Agent prompt setting: S6 skill-level diagnosis-aware control loop
Baseline bottleneck decomposition: Baseline transfer/service bottleneck: decode_tok_s 0.334909; mib_per_token 1431.802; decode_req_page_touch_ms 18437.082; decode_req_page_touch_mib/core_upload_mib 22908.835; decode_req_service_ms 23409.371; decode_req_mat_enqueue_ms 4888.877; decode_req_mat_finish_ms 41.505.
Targeted bottleneck: Explicit required mmap page-touch before OpenCL payload writes.
Expected diagnostic movement: Expected page-touch ms/MiB down sharply, total required service down, decode_tok_s up beyond noise, with decode_core_upload_mib and mib_per_token explicit and correctness preserved; reject if enqueue/finish absorbs the cost.
Agent hypothesis: Skip synchronous touchMmapPages by default while preserving the same required OpenCL upload spans and payload bytes.
Chosen optimization direction: required payload resource path: page-touch behavior
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp touchMmapPages and materializeCoreSlotBatchGpuV3 page-touch/upload loops; baseline page-touch diagnostics.
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Added MLLM_QNN_TD_SKIP_REQUIRED_PAGE_TOUCH guard in touchMmapPages; default skips the explicit page walk, MLLM_QNN_TD_SKIP_REQUIRED_PAGE_TOUCH=0 restores previous behavior. No benchmark/parser/model changes.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_skill_loop_iter_03_fasttemp_p16_d16
Compile result: success after one archived compile repair; host md5 0c8413c787301bebc3213a3f598b860e; phone md5 0c8413c787301bebc3213a3f598b860e; phone stat size 36911136 mode 0777
Correctness result: ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.3425296844787811
  mib_per_token: 1431.8021875
  required_miss_count: 6810.0
  upload_bytes: 24021654568
  prewarm_hit_rate: None
  eviction_churn: 6810.0
  required_miss_wait_ms_per_token: 1402.9991875
  decode_req_page_touch_ms: 4.835999999999987
  decode_req_mat_enqueue_ms: 18027.146000000008
  decode_req_mat_finish_ms: 4371.697999999998
  decode_req_service_ms: 22447.987
  decode_req_mat_writes: 2270.0
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810.0
  decode_req_hit: 3942.0
  decode_evict: 6810.0
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 34.35768
Result: latency_shift: page-touch ms collapsed 18437.082->4.836, but enqueue/finish rose 4930.382 combined to 22398.844 combined; total service improved 23409.371->22447.987 and decode_tok_s improved +2.3%, below conservative acceptance threshold and with hotter run. Physical transfer stayed unchanged: mib_per_token and decode_core_upload_mib 22908.835.
Agent diagnosis: Rejected/archive. The patch mostly moved latency from page-touch accounting into OpenCL enqueue/finish; physical bytes remained unchanged and speed signal is not strong enough.
My diagnosis: This is not an accepted best patch. It demonstrates the diagnosis-aware loop avoiding a local-counter false positive even when one subcounter improves dramatically.
Needed expert knowledge: No forbidden prior mechanism used. More precise separation of page fault cost inside enqueue/finish would be useful but not enough to accept this patch.
Patch / commit: archived /home/liuxu/projects/mobile-moe-ako/patches/failed_attempts/s6_skill_loop_iter_03_fasttemp_p16_d16.patch; no commit
## s6_control_surface_map_baseline_fasttemp_p16_d16

Iteration ID: s6_control_surface_map_baseline_fasttemp_p16_d16
Stage: s6_control_surface_map
Agent prompt setting: S6-Control-Surface-Map MobileMoE-AKO
Branch/base: /home/liuxu/projects/mllm on exp/s6-control-surface-map at da9fa3534a16c0f34adb6709e2ba871741cbf8cc
Iteration log isolation: backed up ITERATIONS.md to /home/liuxu/projects/mobile-moe-ako/ITERATIONS_BEFORE_s6_control_surface_map_20260703_171025.md before baseline/build/source edits.
Baseline provenance:
  build command: cmake --build /home/liuxu/projects/mllm/build-android-arm64-v8a-qnn --target mllm-qwen2-moe-td-qnn-aot-runner
  host runner: /home/liuxu/projects/mllm/build-android-arm64-v8a-qnn/bin/mllm-qwen2-moe-td-qnn-aot-runner
  host md5: 6d15f401a12e515d066141c3a02ba4ea
  host stat: size 36912960, mode 0775, mtime 2026-07-03 17:11:07 +0800
  phone runner: /data/local/tmp/qwen2_moe_td_w8a16_clean_20260527/mllm-qwen2-moe-td-qnn-aot-runner
  phone md5: 6d15f401a12e515d066141c3a02ba4ea
  phone stat: size 36912960, mode 0777, ctime 2026-07-03 17:11:27 +0800
  md5 verification: host and phone match.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_control_surface_map_baseline_fasttemp_p16_d16
Correctness result: ret=0 generated=16/16
Baseline metrics:
  decode_tok_s: 0.3465791554299206
  uploaded_expert_mib_per_token_metric: 1431.8021875
  required_miss_mib_per_token_metric: 1431.8021875
  required_miss_service_ms_per_token_metric: 1369.4251249999998
  metric_required_hit_rate: 0.3666294642857143
  decode_hybrid_req_hit: 3942
  decode_hybrid_req_miss: 6810
  decode_hybrid_evict: 6810
  decode_hybrid_req_page_touch_ms: 17765.002
  decode_hybrid_req_mat_enqueue_ms: 4092.269
  decode_hybrid_req_mat_finish_ms: 10.834
  decode_hybrid_req_service_ms: 21910.802
  decode_hybrid_req_mat_writes: 2270
  decode_hybrid_req_page_touch_mib: 22908.835
  decode_hybrid_core_upload_mib: 22908.835
  decode_hybrid_core_upload_ms: 21874.267
  decode_hybrid_factor_upload_mib: 0.0
  decode_hybrid_input_upload_mib: 48.832
  peak_temp_skin_c_decode: 33.64936

Bottleneck localization report:
  Observed bottleneck pattern: decode throughput is dominated by required cold-core cache misses and physical upload/service work. Required hit rate is only 0.3666, decode misses and evictions both equal 6810, and physical core upload is 22908.835 MiB for 16 generated tokens.
  Evidence: decode_req_service_ms=21910.802, decode_req_page_touch_ms=17765.002, decode_req_mat_enqueue_ms=4092.269, decode_core_upload_mib=22908.835, mib_per_token=1431.802, decode_tok_s=0.346579.
  Candidate control surfaces: required cache lookup and eviction in ProjectionCache::entries; materialization/upload calls through HybridOpenCLMaterializePlan/HybridOpenCLMaterializer; prewarm scheduling through HybridResourceManager pending/resident ledger and submitHybridGpu*Prewarm functions; logging/parser surfaces that expose counters; kernel/operator compute path only as a guardrail because upload/service dominates baseline diagnostics.
  Code search targets: HybridColdGpuShadowExecutor::{ensureExpertCached,ensureExpertCachedGpuV3,ensureExpertsCachedBatch,ensureExpertsCachedBatchGpuV3,ensureExpertsPackedCachedBatchGpuV3,selectCacheVictim,materializeCoreSlotBatchGpuV3,materializePackedExpertSlotBatchGpuV3}; HybridResourceManager::{beginPending,finishPending,touchResident,eraseResource,residentVictimsOverBudgetWithPrefix}; HybridOpenCLMaterializer::{enqueueDeviceSpans,uploadDeviceSpans,finishDeviceUploads}; Qwen2MoeTDAotModel::{submitHybridGpuFactorPrewarm,submitAsyncPrewarmHybridColdGpuLayer,submitNextLayerCorePrewarm,fillHybridColdDeltaSync}; Tucker parser parse_log in run_qwen2_moe_td_end2end.py.
  Avoid-first directions: benchmark/parser/correctness edits are forbidden; counter-only hit/miss edits are not acceptable; pure logging/stat changes are not optimizations; compute-kernel edits are not first because baseline diagnostics point to upload/service, not kernel time; latency shifts between page-touch/enqueue/finish must be rejected unless total service or physical transfer improves.
  Observation gaps: existing counters are sufficient for a first causal patch on physical upload/service because they expose required hit/miss/evict, page-touch, enqueue, finish, service, writes, upload MiB, and temperature. No diagnostic-only iteration is needed before iter_01.

Code-backed control-surface map:

| control surface | code read site | code write/action site | controls what | expected metrics if fixed | false-positive risk |
| --- | --- | --- | --- | --- | --- |
| cache lookup / residency state for per-projection tile core | HybridColdGpuShadowExecutor::ensureExpertCached reads pc.entries.find(expert) in examples/qwen2_moe_td_qnn_aot/aot_run.cpp:7154; ensureExpertsCachedBatch reads pc.entries.find(expert) at aot_run.cpp:7448 | ensureExpertCached inserts pc.entries.emplace(expert, entry) at aot_run.cpp:7270; ensureExpertsCachedBatch inserts pc.entries.emplace(miss.expert, entry) at aot_run.cpp:7571; evicts with pc.entries.erase(victim) and scheduler_->eraseResource at aot_run.cpp:7215-7219 and 7508-7512 | Whether a required expert takes hit path or triggers payload read, slot selection, OpenCL materialization, and scheduler residency update | decode_hybrid_req_hit up, decode_hybrid_req_miss/evict down, decode_core_upload_mib and mib_per_token down, decode_req_service_ms down, decode_tok_s up, correctness unchanged | Updating hit/miss counters or entries without preserving actual buffer residency can fake cache improvement, break correctness, or leave physical upload unchanged |
| cache lookup / residency state for GPU v3 per-projection core | HybridColdGpuShadowExecutor::ensureExpertCachedGpuV3 reads pc.entries.find(expert) at aot_run.cpp:7293; ensureExpertsCachedBatchGpuV3 reads pc.entries.find(expert) at aot_run.cpp:7603 | ensureExpertCachedGpuV3 inserts pc.entries.emplace(expert, entry) at aot_run.cpp:7417; ensureExpertsCachedBatchGpuV3 inserts pc.entries.emplace(miss.expert, entry) at aot_run.cpp:7763; evicts with pc.entries.erase(victim) and scheduler_->eraseResource at aot_run.cpp:7360-7364 and 7669-7673 | Same as above for GPU v3 layout; determines whether required GPU v3 core payloads are uploaded again | Same transfer/service/throughput metrics as above; especially decode_hybrid_core_upload_mib, decode_req_mat_writes, decode_req_service_ms | Counter-only hit improvements or stale pc.entries can hide real misses or use stale slots |
| cache update / eviction state for packed expert payload arena | HybridColdGpuShadowExecutor::ensureExpertsPackedCachedBatchGpuV3 checks gate_pc.entries.find(expert), up_pc.entries.find(expert), down_pc.entries.find(expert) at aot_run.cpp:7801-7805 and selects victims via selectCacheVictim at aot_run.cpp:7884 | Inserts gate_pc/up_pc/down_pc entries at aot_run.cpp:7983-7989; erases old gate/up/down entries and scheduler resources at aot_run.cpp:7893-7908; scheduler touchResident at aot_run.cpp:7991-7999 | Whether one expert-level payload slot is treated as resident for the required packed-path lookup and eviction policy | If truly fixed: required misses/evictions and decode_core_upload_mib fall together; service and throughput improve; correctness remains pass | Very high false-positive risk if only logical entries are changed; must prove physical transfer and correctness because stale multi-entry state can look like a hit |
| materialization / physical upload path | HybridColdGpuShadowExecutor::materializeCoreSlotBatchGpuV3 builds spans and calls materializer_.uploadDeviceSpans at aot_run.cpp:6392-6398 or enqueueDeviceSpans/finishDeviceUploads at aot_run.cpp:6341-6367; materializePackedExpertSlotBatchGpuV3 uses enqueueDeviceSpans/finishDeviceUploads at aot_run.cpp:6492-6518; HybridOpenCLMaterializer::uploadDeviceSpans records bytes/write calls in mllm/backends/opencl/moe/HybridOpenCLMaterializer.cpp:330-358 | OpenCL write action is HybridOpenCLMaterializer::enqueueDeviceSpans and finishDeviceUploads in HybridOpenCLMaterializer.cpp:246-324; caller updates stats_.core_upload_bytes/core_upload_us/required_materialize_bytes at aot_run.cpp:7750-7755 and 7970-7975 | Physical bytes and wait time spent uploading required core payloads to OpenCL buffers | decode_core_upload_mib or decode_req_service_ms down, decode_req_mat_enqueue/finish total down or stable, decode_tok_s up, mib_per_token not worse | Moving latency from page-touch to enqueue/finish or reducing one subcounter while total service and bytes do not improve |
| scheduling / prewarm path | Qwen2MoeTDAotModel::submitAsyncPrewarmHybridColdGpuLayer reads hybrid_prefetch_scheduler_.decide at aot_run.cpp:15979-15985; submitNextLayerCorePrewarm reads decision and candidate/upload counts at aot_run.cpp:16100-16131; submitHybridGpuFactorPrewarm reads decision.allow_factor_preload at aot_run.cpp:15441-15445 | beginPending core/factor requests at aot_run.cpp:16031 and 16154 and factor at 15474; submitPrewarmAsync at aot_run.cpp:16047 and 16171; finishPending callbacks at aot_run.cpp:16049-16054 and 16173-16178 | Whether speculative work is submitted early enough and within ledger budgets, and whether pending/resident state is recorded | prewarm submit/complete up, required misses/service down or wait shifted off critical path, decode_tok_s up, transfer not worse unless justified | More prewarm can increase uploads/evictions or hide as scheduling success while mib_per_token worsens |
| statistics / logging / bookkeeping path | Qwen2MoeTDAotModel::fillHybridColdDeltaSync reads HybridGpuShadowStats deltas at aot_run.cpp:16953-16955 and prints [TD-RUN][hybrid-cold] at aot_run.cpp:17129-17198; parser parse_log reads HYBRID_COLD_RE and aggregates decode_hybrid_totals in /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py:95-149 | Stats are incremented in cache/materialization sites such as aot_run.cpp:7167-7173, 7253-7263, 7750-7755, 7970-7975; parser computes mib/token from logged MiB/generated at run_qwen2_moe_td_end2end.py:107-149 | What the benchmark reports as hit/miss/transfer/service metrics | Accepted only as diagnostics: added counters should clarify causality without changing decode_tok_s or physical work | Can create logical-counter-only wins or parser artifacts; forbidden as an optimization by itself |
| benchmark / parser / correctness path | Tucker parser parse_log extracts RET, Generated tokens, Decode, and hybrid counters in /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py:54-149 | write_summary and printed result path in run_qwen2_moe_td_end2end.py:471-483; runtime prints RET and generated-token lines | Benchmark semantics, generated-token accounting, correctness, and metric normalization | Not an optimization surface under this contract; should remain unchanged | Any edit here invalidates comparisons by changing measurement or correctness rules |
| kernel/operator compute path | fillHybridColdDeltaSync executes GPU core calls runColdFullGpu/runColdPostGpu/runProjectionRealGpuV3 at aot_run.cpp:16782-16902; kernel diagnostics printed at aot_run.cpp:17044-17051 | Kernel implementations below HybridColdGpuShadowExecutor and OpenCL kernels run the actual expert projection math | Arithmetic/compute time once payloads are resident | Would show kernel_ms or gpu_total_ms down with stable transfer and correctness | Baseline kernel_ms is not the dominant exposed bottleneck; compute edits risk correctness and are not justified first |

Patch selection rule status before iter_01: the map is written. Any source edit must select exactly one mapped control surface and answer the patch hypothesis gate against its read site, write/action site, active benchmark evidence, expected primary/diagnostic movement, and rejection condition.

## s6_control_surface_map_iter_01_fasttemp_p16_d16

Iteration ID: s6_control_surface_map_iter_01_fasttemp_p16_d16
Stage: s6_control_surface_map
Agent prompt setting: S6-Control-Surface-Map MobileMoE-AKO
Selected control surface: cache update / eviction state for packed expert payload arena
Patch hypothesis gate:
  System bottleneck: required cold-core miss/upload service, not parser/counter reporting.
  Runtime state/path changed: packed expert payload cache population for gate/up/down cache entries in the required GPU v3 path.
  Read site: HybridColdGpuShadowExecutor::ensureExpertsPackedCachedBatchGpuV3 reads gate_pc.entries/up_pc.entries/down_pc.entries at examples/qwen2_moe_td_qnn_aot/aot_run.cpp:7801-7805; current active runProjectionImplGpuV3 path reads only current projection through ensureExpertsCachedBatchGpuV3 at aot_run.cpp:9113.
  Write/action site: ensureExpertsPackedCachedBatchGpuV3 inserts gate_pc/up_pc/down_pc entries at aot_run.cpp:7983-7989 and scheduler_->touchResident at aot_run.cpp:7991-7999.
  Active benchmark path evidence: rebuilt baseline log showed packed external payload arenas active with packed_payload=1 external_payload=1 and expert payload arenas created; baseline decode_core_upload_mib=22908.835 and decode_req_miss/decode_evict=6810.
  Expected primary movement: decode_tok_s should improve beyond noise.
  Expected diagnostic movement: decode_req_miss, decode_evict, decode_core_upload_mib, mib_per_token, decode_req_page_touch_mib, and decode_req_service_ms should fall together.
  Guardrails: ret=0, generated=16, no mib_per_token regression, unchanged p16/d16 contract.
  Falsification/rejection: if only hit/miss counters improve while physical upload MiB, page-touch MiB, writes, and service do not improve, reject as logical_counter_only.
  False positive risk: logical cache entries can make hit-rate look better while OpenCL writes and physical bytes remain unchanged.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp runProjectionImplGpuV3, ensureExpertsCachedBatchGpuV3, ensureExpertsPackedCachedBatchGpuV3; baseline summary.csv/log.
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Temporarily routed packed external payload gate projection path through ensureExpertsPackedCachedBatchGpuV3 so gate/up/down cache entries were populated together before compute. No benchmark/parser/model changes.
Build/deploy verification:
  build command: cmake --build /home/liuxu/projects/mllm/build-android-arm64-v8a-qnn --target mllm-qwen2-moe-td-qnn-aot-runner
  compile result: success
  host md5: babbe78fffe524a76c8a57e62319c115
  host stat: size 37175888, mode 0775, mtime 2026-07-03 17:19:35 +0800
  phone md5: babbe78fffe524a76c8a57e62319c115
  phone stat: size 37175888, mode 0777, ctime 2026-07-03 17:19:53 +0800
  md5 verification: host and phone match.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_control_surface_map_iter_01_fasttemp_p16_d16
Correctness result: ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.34161281087326245
  uploaded_expert_mib_per_token_metric: 1431.8021875
  required_miss_mib_per_token_metric: 1431.8021875
  required_miss_service_ms_per_token_metric: 1430.7379999999994
  metric_required_hit_rate: 0.7888764880952381
  decode_hybrid_req_hit: 8482
  decode_hybrid_req_miss: 2270
  decode_hybrid_evict: 2270
  decode_hybrid_req_page_touch_ms: 18046.888
  decode_hybrid_req_mat_enqueue_ms: 4806.574
  decode_hybrid_req_mat_finish_ms: 10.740
  decode_hybrid_req_service_ms: 22891.808
  decode_hybrid_req_mat_writes: 2270
  decode_hybrid_req_page_touch_mib: 22908.835
  decode_hybrid_core_upload_mib: 22908.835
  decode_hybrid_core_upload_ms: 22870.595
  peak_temp_skin_c_decode: 34.2034
Result classification: logical_counter_only
Agent diagnosis: The selected surface changed logical hit/miss/evict counters as expected, but physical upload volume did not move: mib_per_token, decode_core_upload_mib, decode_req_page_touch_mib, and req_mat_writes were unchanged. decode_tok_s regressed from 0.346579 to 0.341613 and required service worsened from 21910.802ms to 22891.808ms.
My diagnosis: Rejected and archived. This is exactly the false-positive class the control-surface map was meant to catch: cache bookkeeping looked better, but real system work did not decrease.
Needed expert knowledge: No forbidden prior mechanism used. The map and current diagnostics were sufficient to reject the wrong-path/logical-counter patch.
Patch / commit: archived /home/liuxu/projects/mobile-moe-ako/patches/failed_attempts/s6_control_surface_map_iter_01_fasttemp_p16_d16.patch; no commit; source edit reverted.

## s6_control_surface_map_iter_02_fasttemp_p16_d16

Iteration ID: s6_control_surface_map_iter_02_fasttemp_p16_d16
Stage: s6_control_surface_map
Agent prompt setting: S6-Control-Surface-Map MobileMoE-AKO
Selected control surface: materialization / physical upload path
Patch hypothesis gate:
  System bottleneck: required materialization/upload service on decode miss path.
  Runtime state/path changed: explicit mmap page-touch action before required OpenCL payload writes.
  Read site: HybridColdGpuShadowExecutor::materializeCoreSlotBatchGpuV3 reads core_page_touch_mode_ at examples/qwen2_moe_td_qnn_aot/aot_run.cpp:6322 and packed payload spans at aot_run.cpp:6326-6345.
  Write/action site: touchMmapPages action at aot_run.cpp:6336 plus materializer_.enqueueDeviceSpans and finishDeviceUploads at aot_run.cpp:6346-6367; physical write accounting via stats_.core_upload_* at aot_run.cpp:6371-6373 and caller stats at aot_run.cpp:7750-7755.
  Active benchmark path evidence: baseline decode_req_page_touch_ms=17765.002, decode_req_mat_enqueue_ms=4092.269, decode_req_mat_finish_ms=10.834, decode_req_service_ms=21910.802, decode_core_upload_mib=22908.835.
  Expected primary movement: decode_tok_s up if explicit page touch is redundant.
  Expected diagnostic movement: total decode_req_service_ms and/or decode_core_upload_ms down; page_touch decrease alone is insufficient; mib_per_token must not regress.
  Guardrails: ret=0, generated=16, unchanged physical bytes or lower, unchanged benchmark contract.
  Falsification/rejection: if page-touch disappears but enqueue/finish absorb the cost, classify latency_shift or regression and archive.
  False positive risk: moving page-fault cost from page-touch counter into OpenCL enqueue/finish while real bytes and total service remain unchanged.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp touchMmapPages, materializeCoreSlotBatchGpuV3, HybridOpenCLMaterializer upload path; baseline and iter_01 metrics.
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Temporarily added MLLM_QNN_TD_SKIP_REQUIRED_PAGE_TOUCH default true around touchMmapPages in materializeCoreSlotBatchGpuV3 mode 2, preserving upload spans and byte accounting. No benchmark/parser/model changes.
Build/deploy verification:
  build command: cmake --build /home/liuxu/projects/mllm/build-android-arm64-v8a-qnn --target mllm-qwen2-moe-td-qnn-aot-runner
  compile result: success
  host md5: 749411ab1a70761d7f73f1d342164c51
  host stat: size 36922320, mode 0775, mtime 2026-07-03 17:26:05 +0800
  phone md5: 749411ab1a70761d7f73f1d342164c51
  phone stat: size 36922320, mode 0777, ctime 2026-07-03 17:26:27 +0800
  md5 verification: host and phone match.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_control_surface_map_iter_02_fasttemp_p16_d16
Correctness result: ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.3360641768315928
  uploaded_expert_mib_per_token_metric: 1431.8021875
  required_miss_mib_per_token_metric: 1431.8021875
  required_miss_service_ms_per_token_metric: 1404.105812499999
  metric_required_hit_rate: 0.3666294642857143
  decode_hybrid_req_hit: 3942
  decode_hybrid_req_miss: 6810
  decode_hybrid_evict: 6810
  decode_hybrid_req_page_touch_ms: 0.0
  decode_hybrid_req_mat_enqueue_ms: 14506.519
  decode_hybrid_req_mat_finish_ms: 7916.287
  decode_hybrid_req_service_ms: 22465.693
  decode_hybrid_req_mat_writes: 2270
  decode_hybrid_req_page_touch_mib: 22908.835
  decode_hybrid_core_upload_mib: 22908.835
  decode_hybrid_core_upload_ms: 22426.886
  peak_temp_skin_c_decode: 34.80456
Result classification: latency_shift / regression
Agent diagnosis: Page-touch ms collapsed to zero, but enqueue+finish rose from baseline 4103.103ms to 22422.806ms. Physical upload volume, page-touch MiB, materialization writes, and mib_per_token were unchanged; decode_tok_s regressed from 0.346579 to 0.336064.
My diagnosis: Rejected and archived. The control surface was real, but the patch only moved page-fault/wait accounting into OpenCL upload time and worsened the primary metric.
Needed expert knowledge: No forbidden prior mechanism used. Existing diagnostics were sufficient to reject this materialization-path attempt.
Patch / commit: archived /home/liuxu/projects/mobile-moe-ako/patches/failed_attempts/s6_control_surface_map_iter_02_fasttemp_p16_d16.patch; no commit; source edit reverted.

## s6_control_surface_map_iter_03_fasttemp_p16_d16

Iteration ID: s6_control_surface_map_iter_03_fasttemp_p16_d16
Stage: s6_control_surface_map
Agent prompt setting: S6-Control-Surface-Map MobileMoE-AKO
Selected control surface: scheduling / prewarm path
Patch hypothesis gate:
  System bottleneck: required cold-core miss service remains high on the decode critical path, with baseline decode_req_service_ms=21910.802 and decode_core_upload_mib=22908.835.
  Runtime state/path changed: the existing next-layer speculative core prewarm decision is enabled by default so decode can submit prewarm work for the next subgraph from the predecessor input before the required path reaches that layer.
  Read site: Qwen2MoeTDAotModel::runDecode checks hybrid_gpu_next_layer_prewarm_ before calling submitNextLayerCorePrewarm in examples/qwen2_moe_td_qnn_aot/aot_run.cpp around the decode sg loop; submitNextLayerCorePrewarm checks hybrid_gpu_next_layer_prewarm_ and hybrid_prefetch_scheduler_.decide before selecting candidate/upload experts.
  Write/action site: submitNextLayerCorePrewarm calls hybrid_prefetch_scheduler_.beginPending, HybridColdGpuShadowExecutor::submitPrewarmAsync, and finishPending callback for the speculative core request.
  Active benchmark path evidence: baseline runtime reported gpu_async_prewarm=true and async_decode=true but next_layer_prewarm=false; decode pre_hit=0 and pre_miss=0 while required misses/evictions were 6810 and required service dominated decode time. The code path is in the decode loop before runSubgraph and before the next layer routing/required materialization path.
  Expected primary movement: decode_tok_s should improve beyond noise if useful prewarm work comes off the critical path.
  Expected diagnostic movement: scheduling/prewarm submit/complete or next_layer_prewarm timing should appear; decode_req_service_ms or required wait should fall, or required hit/pre-hit behavior should improve, without a mib_per_token increase. This is a scheduling hypothesis, not a transfer-volume hypothesis unless decode_core_upload_mib also falls.
  Guardrails: ret=0, generated=16, unchanged p16/d16 contract, no regression in uploaded_expert_mib_per_token_metric or physical upload diagnostics.
  Falsification/rejection: if throughput regresses or remains within noise, if service does not improve consistently, or if transfer volume/eviction churn worsens, reject as noise_or_no_signal or regression. If only prewarm counters appear without primary/service improvement, do not accept.
  False positive risk: speculative prewarm may add uploads or evictions that make scheduling counters look active while increasing total work or merely moving waits.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp runDecode, submitAsyncPrewarmHybridColdGpuLayer, submitNextLayerCorePrewarm, hybrid_gpu_next_layer_prewarm_ config/default; baseline and iter_02 summaries for prewarm/service/transfer metrics.
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Temporarily changed the default for MLLM_QNN_TD_HYBRID_GPU_NEXT_LAYER_PREWARM from false to true, leaving the env override intact. No benchmark/parser/model changes.
Build/deploy verification:
  build command: cmake --build /home/liuxu/projects/mllm/build-android-arm64-v8a-qnn --target mllm-qwen2-moe-td-qnn-aot-runner
  compile result: success
  host md5: 606b390a55bd68d97badd3d9e79be38c
  host stat: size 36912960, mode 0775, mtime 2026-07-03 17:33:57 +0800
  phone md5: 606b390a55bd68d97badd3d9e79be38c
  phone stat: size 36912960, mode 0777, ctime 2026-07-03 17:34:18 +0800
  md5 verification: host and phone match.
Benchmark command: /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_control_surface_map_iter_03_fasttemp_p16_d16
Correctness result: ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.33915295066776563
  uploaded_expert_mib_per_token_metric: 1431.8021875
  required_miss_mib_per_token_metric: 1431.8021875
  required_miss_service_ms_per_token_metric: 1434.050187500001
  metric_required_hit_rate: 0.3666294642857143
  decode_hybrid_req_hit: 3942
  decode_hybrid_req_miss: 6810
  decode_hybrid_evict: 6810
  decode_hybrid_pre_hit: 0
  decode_hybrid_pre_miss: 0
  decode_hybrid_prewarm_evict: 0
  decode_hybrid_req_page_touch_ms: 18308.289
  decode_hybrid_req_mat_enqueue_ms: 4550.402
  decode_hybrid_req_mat_finish_ms: 42.565
  decode_hybrid_req_service_ms: 22944.803
  decode_hybrid_req_mat_writes: 2270
  decode_hybrid_req_page_touch_mib: 22908.835
  decode_hybrid_core_upload_mib: 22908.835
  decode_hybrid_core_upload_ms: 22907.683
  peak_temp_skin_c_decode: 35.0584
Result classification: regression / hypothesis-mismatch
Agent diagnosis: Enabling next-layer prewarm by default did not produce the expected scheduling diagnostic movement in the captured decode metrics: decode pre_hit/pre_miss remained 0/0, misses and evictions stayed 6810, physical upload volume and MiB/token were unchanged, and required service worsened from 21910.802ms to 22944.803ms. decode_tok_s regressed from 0.346579 to 0.339153, with a hotter decode peak.
My diagnosis: Rejected and archived. The mapped scheduling surface was a plausible read/action site, but this small default flip did not put useful prewarm work on the measured critical path and did not meet the scheduling acceptance rule.
Needed expert knowledge: No forbidden prior mechanism used. The control-surface map and current diagnostics were enough to reject this as not a scheduling win.
Patch / commit: archived /home/liuxu/projects/mobile-moe-ako/patches/failed_attempts/s6_control_surface_map_iter_03_fasttemp_p16_d16.patch; no commit; source edit reverted.

## s6_control_surface_map_stop_summary

Iteration ID: s6_control_surface_map_stop_summary
Stage: s6_control_surface_map
Agent prompt setting: S6-Control-Surface-Map MobileMoE-AKO
Optimization result: no useful optimization patch selected. Three mapped optimization attempts were rejected: iter_01 as logical_counter_only, iter_02 as latency_shift/regression, and iter_03 as scheduling regression/hypothesis-mismatch. No p32/d32 recheck was run because there is no correctness-passing accepted best patch.
Localization result: the code-backed control-surface map improved result discipline more than optimization outcome. It forced each attempt to name exact read and write/action sites before editing, separated cache bookkeeping from physical transfer, separated page-touch accounting from total materialization service, and separated scheduling activity from transfer wins.
False-positive handling: the map reduced wrong-path acceptance. Iter_01 would have looked attractive from hit/miss counters alone but was rejected because physical upload and service diagnostics did not move. Iter_02 would have looked attractive from page-touch counters alone but was rejected because enqueue/finish absorbed the cost and throughput regressed. Iter_03 was rejected because enabling the mapped scheduling surface did not produce expected prewarm/service movement.
Best patch conclusion: no-useful-patch. Baseline remains the best source state for this experiment contract: decode_tok_s=0.3465791554299206, MiB/token=1431.8021875, correctness ret=0 generated=16/16.
Harness discipline conclusion: the control-surface-map requirement appears useful as a localization and rejection discipline. It did not find a speedup in this run, but it prevented logical-counter-only and latency-shift changes from being misclassified as wins and made the failure mode concrete.
## s6_state_relation_map_baseline_fasttemp_p16_d16

Iteration ID: s6_state_relation_map_baseline_fasttemp_p16_d16
Stage: S6-State-Relation-Map
Agent prompt setting: Required state-relation-map MobileMoE-AKO run; no source edits before baseline/map.
Baseline provenance: runtime repo `/home/liuxu/projects/mllm` on branch `exp/s6-state-relation-map` at `da9fa3534a16c0f34adb6709e2ba871741cbf8cc`; built with `cmake --build /home/liuxu/projects/mllm/build-android-arm64-v8a-qnn --target mllm-qwen2-moe-td-qnn-aot-runner`; host runner `/home/liuxu/projects/mllm/build-android-arm64-v8a-qnn/bin/mllm-qwen2-moe-td-qnn-aot-runner` md5 `6d15f401a12e515d066141c3a02ba4ea`, size `36912960`; pushed to `/data/local/tmp/qwen2_moe_td_w8a16_clean_20260527/mllm-qwen2-moe-td-qnn-aot-runner`; phone md5 `6d15f401a12e515d066141c3a02ba4ea`, size `36912960`, mode `0777`.
Baseline bottleneck decomposition: p16/d16 temperature-gated run passed correctness (`ret=0`, `generated=16`). Primary throughput `decode_tok_s=0.33411581168205445`. Normalized transfer was high: `uploaded_expert_mib_per_token_metric=1431.8021875` in decode and overall metric `3110.2445625`. Required miss service was high: `required_miss_service_ms_per_token_metric=1441.6930625000018`, `decode_hybrid_req_service_ms=23067.08900000003`, `decode_hybrid_req_miss=6810`, `decode_hybrid_req_hit=3942`, `decode_hybrid_evict=6810`, `decode_hybrid_req_mat_writes=2270`, `decode_hybrid_req_page_touch_mib=22908.835`, `decode_hybrid_core_upload_mib=2602.6799999999976`. Thermal start/end was comparable under gate: start skin `29.85088`, peak decode skin `34.27484`, end skin `34.31132`.
Targeted bottleneck: none, baseline only.
Expected diagnostic movement: none.
Agent hypothesis: baseline establishes high required-miss/materialization/upload work and cache churn before any state-relation patching.
Chosen optimization direction: write code-backed state-relation map before choosing any patch.
Files inspected: `/home/liuxu/projects/mobile-moe-ako/references/constraints.md`, `/home/liuxu/projects/mobile-moe-ako/references/benchmark_instructions.md`, `/home/liuxu/projects/mobile-moe-ako/references/metrics_schema.md`, `/home/liuxu/projects/mobile-moe-ako/references/system_overview.md`, initial search of `/home/liuxu/projects/mllm/mllm/models/qwen2_moe/modeling_qwen2_moe_td_qnn_aot.hpp` and `/home/liuxu/projects/mllm/examples/qwen2_moe_td_qnn_aot/aot_run.cpp`.
Files modified: none in runtime repo; `/home/liuxu/projects/mobile-moe-ako/ITERATIONS.md` appended. Existing iteration log backed up to `/home/liuxu/projects/mobile-moe-ako/ITERATIONS_BEFORE_s6_state_relation_map_20260703_174618.md`.
Change summary: baseline build/deploy/benchmark/log only.
Benchmark command: `/home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_state_relation_map_baseline_fasttemp_p16_d16`
Compile result: success
Correctness result: pass
Metrics:
  decode_tok_s: 0.33411581168205445
  mib_per_token: 1431.8021875
  required_miss_count: 6810
  upload_bytes:
  prewarm_hit_rate:
  eviction_churn: 6810
  required_miss_wait_ms_per_token: 1441.6930625000018
  decode_req_page_touch_ms: 23031.477999999992
  decode_req_mat_enqueue_ms: 17.58599999999999
  decode_req_mat_finish_ms: 3.7849999999999837
  decode_req_service_ms: 23067.08900000003
  decode_req_mat_writes: 2270
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 2602.6799999999976
  decode_req_miss: 6810
  decode_req_hit: 3942
  decode_evict: 6810
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 34.27484
Result: valid_baseline
Agent diagnosis: Before patching, inspect which logical residency/key state controls later materialization/upload, because counter-only improvements are explicitly insufficient for this run.
My diagnosis: Baseline points to repeated required materialization/page-touch and upload under cache pressure; the relation map must determine whether logical hit/miss state actually corresponds to reusable physical buffers or only diagnostic/accounting state.
Needed expert knowledge: no answer-level prior mechanism used; need only code-backed relation between logical runtime state, physical resources/actions, and later lookup paths.
Patch / commit: none

## s6_state_relation_map_before_edits

Iteration ID: s6_state_relation_map_before_edits
Stage: S6-State-Relation-Map
Agent prompt setting: Required state-relation map after baseline and before first source edit.
Baseline bottleneck decomposition: Baseline p16/d16 shows `decode_tok_s=0.33411581168205445`, `uploaded_expert_mib_per_token_metric=1431.8021875`, `decode_hybrid_req_miss=6810`, `decode_hybrid_req_hit=3942`, `decode_hybrid_evict=6810`, `decode_hybrid_req_service_ms=23067.08900000003`, `decode_hybrid_req_page_touch_mib=22908.835`, and `decode_hybrid_core_upload_mib=2602.6799999999976`.
Observed bottleneck pattern: repeated required expert-core materialization/page-touch/upload and eviction churn, not merely a missing hit counter. Candidate control surfaces are (1) QNN routing input slot reuse via `SubgraphIO::routed_slot_experts`/`ExpertLRUCache`, (2) GPU cold-core physical cache via `HybridColdGpuShadowExecutor::ProjectionCache::entries`, (3) factor/core sidecar lifetime and cache releases, and (4) diagnostics/stats that must not be accepted without physical counter movement.
Avoid-first directions: do not edit Tucker runner, parser, prompt, generated-token accounting, or correctness; do not treat `HybridGpuShadowStats::{cache_hits,cache_misses}` or `ExpertLRUCache` hit/miss changes as speedups unless `decode_hybrid_core_upload_mib`, `decode_hybrid_req_service_ms`, `decode_hybrid_req_page_touch_mib`, materializer upload bytes/calls, or `decode_tok_s` also move.
Observation gaps: baseline already has enough non-counter metrics for one causal patch (`decode_hybrid_core_upload_mib`, `decode_hybrid_req_service_ms`, `decode_hybrid_req_page_touch_mib`, `decode_hybrid_req_mat_writes`, materializer counters in summary). A diagnostic-only iteration is not required before the first optimization attempt unless a selected relation cannot be tied to these fields.

State-relation map:

| logical state | lookup/read site | update/write site | physical resource/action | later access that would reuse it | expected metrics if relation is repaired | false-positive risk |
| --- | --- | --- | --- | --- | --- | --- |
| `SubgraphIO::routed_slot_experts[flat_slot]` for per-token top-k routing slots | `fillRoutingFromHidden`: `same_slot_ready` check around `io.routed_slot_experts[slot] == eid`; `findExistingPackedCoreSlotForExpert`; `copyPackedTileCoreSlotFromExisting` | `fillPackedTileCoreSlot`; `fillAllPanelI8FromPanelSidecar`; `copyPackedTileCoreSlotFromExisting`; fallback copy/dequant path in `fillRoutingFromHidden`; initialized in `initSubgraphIO`; cleared by `clearSubgraphIO`/`evictSubgraphIO` | Physical QNN input buffers in `SubgraphIO` (`gate_core_w_slots`, `up_core_w_slots`, `down_core_w_slots`, `*_panel_i8*`, `gate_core`, `up_core`, `down_core`) already containing a routed expert payload for a slot | Later `fillRoutingFromHidden` for same `SubgraphIO`/token slot can skip CPU memcpy/dequant or copy from an existing slot before QNN graph launch | `copied_slots`/`skipped_slots` logs may improve; real proof requires lower routing `expert_core_fill` time or decode time. Transfer metrics may not move because these are host/QNN input fills, not GPU cold-core OpenCL uploads | Counter/log improvement without reducing physical transfer; unsafe if `routed_slot_experts` survives after `evictSubgraphIO` or different tensor allocation |
| `ExpertLRUCache::last_slot_active[layer][slot]` and `last_active[layer]` | `was_active_in_slot`; `prefetchLayerSelective`; `prefetchLayerFromHistory`; `startDecodeHistoryCorePrefill`; history/predictive prefill logic | `lru_cache_.update(moe_layer_idx, all_active, &slot_active)` at end of `fillRoutingFromHidden`; `ExpertLRUCache::init` | Logical history of selected expert IDs, not itself a physical resource; can guide `madvise` prefetch and slot skip decisions when paired with `SubgraphIO::routed_slot_experts` | Future routing/prefetch calls read history before deciding `madvise`, predictive fill, or skip/copy behavior | If useful, `decode_hybrid_req_page_touch_ms/mib` or routing fill time should fall; `decode_tok_s` should improve or remain stable; `mib_per_token` must not regress | Updating history alone can improve apparent prediction/hit logs while actual QNN input buffers or mmap pages are not resident |
| `HybridColdGpuShadowExecutor::ProjectionCache::entries[eid]` (`CacheEntry{slot, expert, resource_key, state, last_use}`) | `ensureExpertCached` / `ensureExpertCachedGpuV3` in `runProjectionImpl*` and `prewarmLayer`; hit/miss accounting in executor | Same ensure functions after materializer/upload into `ProjectionCache` arenas; eviction through projection-cache eviction paths and `releaseLayerCachesForSidecarSwitch`/`releaseLayerCachesForFactorSwitch` | OpenCL core payload buffers/arenas (`weight_arena`, `scale_arena`, `scale2_arena`, `payload_arena`) holding materialized expert projection data | Later `runProjection`/`prewarmLayer` for same `(layer, projection, expert)` can reuse OpenCL buffer instead of materializing/uploading again | Physical proof: lower `decode_hybrid_core_upload_mib`, lower `decode_hybrid_req_mat_writes`, lower `decode_hybrid_req_service_ms`, lower materializer upload bytes/calls, possibly higher `decode_tok_s`; hit counter alone insufficient | Marking an entry resident without backing buffer validity would only move counters or break correctness; resource-key mismatch can claim reuse after sidecar/factor switch |
| `ProjectionCache::key`, `arena_resource_key`, `CacheEntry::resource_key`, and materializer request storage refs | `getProjectionCache*`; `ensureExpertCached*`; scheduler/materializer request submission paths | cache construction in `getProjectionCache*`; materializer writes device buffers; release on sidecar/factor switches | Identity mapping from logical `(layer, proj_name, layout/storage)` to physical OpenCL allocations and external sidecar spans | Later materialize/check can detect compatible cached resource instead of creating/uploading a new one | Real proof: lower materializer create/upload/release counters or resident bytes stable with lower required misses/service | Over-broad keys can alias incompatible payloads; too-narrow keys prevent reuse with no correctness change |
| sidecar/layer lifetime state: `expert_cores_gpu_v3_active_layer_`, `expert_cores_gpu_v3_layer_maps_`, `td_factors_active_layer_`, `td_factors_layer_maps_`, `td_factors_layer_last_use_` | `ensureLayerGpuV3SidecarLoaded`; `ensureLayerTDFactorsLoaded`; `ensureHybridGpuMoeLayerResources` called at start of `fillRoutingFromHidden` | sidecar map load functions; `trimLayerGpuV3SidecarWindowNoLock`; `trimLayerTDFactorsWindowNoLock`; release functions call `hybrid_gpu_shadow_->releaseLayerCachesForSidecarSwitch` / `releaseLayerCachesForFactorSwitch` and scheduler erase | Host mmap storage and any dependent GPU caches for a layer’s core/factor sidecars | Later `fillRoutingFromHidden` / GPU cold path can reuse same layer sidecar and compatible GPU caches if not released | If repaired, fewer cache evictions/releases and lower service/transfer; `core_arena_resident_*` may remain useful; `decode_tok_s` can improve | Keeping sidecars/caches too long can raise memory pressure or stale resources; release suppression may hide evictions without lowering uploads |
| `HybridPrefetchScheduler` resource records and materialize requests | scheduler calls from prewarm/materializer paths; `eraseLayerResources(ResourceKind::Factor/Core, layer)` from factor/core sidecar window trims | materializer request creation in `ensureExpertCached*`/prewarm paths; erase on layer switches | Scheduled future materialization/upload work and external storage refs for OpenCL buffers | Later required miss can benefit if prewarm materialized the same resource before demand | Expected lower required miss service or async prewarm hits with stable or lower transfer; scheduling win only if service/scheduling diagnostics and primary metric improve | Moving work earlier can improve required wait but not total transfer; should not be called transfer win unless upload bytes fall |
| `HybridGpuShadowStats` counters (`required_cache_hits`, `required_cache_misses`, `materializer_*`, `core_upload_*`, `required_*`) | parser reads log-derived summary fields; `stats()` aggregates counters and live resident bytes | executor increments in required/prewarm/materializer/upload paths; stats are subtracted by phase deltas | Measurements of actions/resources, not the resources themselves | Later benchmark comparison uses diagnostics to accept/reject a patch | Non-counter proof is `decode_tok_s`, `decode_hybrid_core_upload_mib`, `decode_hybrid_req_service_ms`, `decode_hybrid_req_page_touch_mib`, materializer bytes/calls | Stats-only patch can improve reported hit/miss without changing physical work; forbidden as optimization |

State-relation questions answered from code inspection:

1. Logical runtime state read before hit/miss/reuse/materialize decisions: `SubgraphIO::routed_slot_experts`, `ExpertLRUCache::{last_active,last_slot_active}`, `ProjectionCache::entries`, `CacheEntry::{resource_key,state,last_use}`, sidecar active/window maps, scheduler resource records, and stats counters.
2. Physical resources/actions represented: QNN input tensors, mmap sidecar spans, OpenCL materialized core arenas/buffers, factor buffers, scheduled materialization/upload actions, and diagnostic records.
3. Mapping cardinality: `routed_slot_experts` is one logical expert id per physical input slot; `last_active` is many experts per layer with no physical buffer guarantee; `ProjectionCache::entries` is one logical expert per projection-cache entry but shares arenas and resource keys; sidecar maps are one active/windowed host mapping per layer; scheduler records may be many-to-one with shared physical buffers.
4. After materialization/upload, logical states updated: `ProjectionCache::entries[eid]` and `CacheEntry` fields, materializer stats, scheduler resource completion, and resident byte counts in `stats()`. After routing input fill, `io.routed_slot_experts[slot]` and `lru_cache_` are updated.
5. Later accesses read those states in `fillRoutingFromHidden`, `findExistingPackedCoreSlotForExpert`, `copyPackedTileCoreSlotFromExisting`, `prefetchLayerSelective`, `startDecodeHistoryCorePrefill`, `runProjection*`, `prewarmLayer`, and sidecar ensure/release paths.
6. For reuse to be observed, the relevant logical resident state must be updated at the same granularity as the physical payload: QNN slot id for `SubgraphIO`, `(layer, projection, expert/resource_key)` for GPU cache entries, and layer/resource kind for sidecar/scheduler state.
7. If counters improve, non-counter proof must come from `decode_tok_s`, `decode_hybrid_core_upload_mib`, `decode_hybrid_req_service_ms`, `decode_hybrid_req_page_touch_mib`, `decode_hybrid_req_mat_writes`, materializer upload bytes/calls, or comparable service/scheduling diagnostics.
8. Minimal extra diagnostic if relation is unclear: per required miss, log `(layer, projection, expert, resource_key, was_entry_hit, did_upload_bytes, materializer_write)` as a bounded aggregate. Current baseline already exposes enough aggregate physical counters for a first patch.

## s6_state_relation_map_iter_01_fasttemp_p16_d16

Iteration ID: s6_state_relation_map_iter_01_fasttemp_p16_d16
Stage: S6-State-Relation-Map
Agent prompt setting: state-relation-map gated optimization iteration.
Selected state relation: `HybridColdGpuShadowExecutor::ProjectionCache::entries[eid]` to physical OpenCL payload buffers/arenas, specifically the external packed expert-payload arena relation shared by gate/up/down projection caches.
Patch hypothesis gate: logical read site `runProjectionImplGpuV3`/`ensureExpertsCachedBatchGpuV3`; logical write site `ensureExpertsPackedCachedBatchGpuV3`; physical action `materializePackedExpertSlotBatchGpuV3` and OpenCL core upload into shared payload arena; later access expected to change behavior was subsequent up/down/gate projection cache lookups observing populated `CacheEntry` state; active benchmark evidence was baseline `decode_hybrid_req_miss=6810`, `decode_hybrid_req_mat_writes=2270`, `decode_hybrid_core_upload_mib=22908.835`; expected primary movement was higher `decode_tok_s`; expected diagnostic movement was lower `decode_hybrid_core_upload_mib`, `decode_hybrid_req_mat_writes`, or `decode_hybrid_req_service_ms`; rejection condition was hit-rate-only improvement without physical counter movement.
Baseline bottleneck decomposition: same as baseline, high required miss service and fixed physical core upload volume.
Targeted bottleneck: repeated logical misses for packed physical payload resources.
Expected diagnostic movement: required miss count and physical upload/materialization work should both fall if the logical relation repaired real reuse.
Agent hypothesis: If one packed physical expert payload already backs all projection caches in the external payload arena path, then populating gate/up/down `ProjectionCache::entries` together should allow later projection accesses to reuse the physical payload and avoid upload/materialization.
Chosen optimization direction: materialization/update relation.
Files inspected: `/home/liuxu/projects/mllm/examples/qwen2_moe_td_qnn_aot/aot_run.cpp` (`runProjectionImplGpuV3`, `ensureExpertsCachedBatchGpuV3`, `ensureExpertsPackedCachedBatchGpuV3`, `ProjectionCache`, `CacheEntry`, `getProjectionCacheGpuV3`, `releaseLayerCachesForSidecarSwitch`).
Files modified: `/home/liuxu/projects/mllm/examples/qwen2_moe_td_qnn_aot/aot_run.cpp` during the attempt; reverted after classification.
Change summary: Routed the external packed payload arena path through `ensureExpertsPackedCachedBatchGpuV3` so gate/up/down cache entries were updated together for the same physical payload.
Build/deploy verification: build success with `cmake --build /home/liuxu/projects/mllm/build-android-arm64-v8a-qnn --target mllm-qwen2-moe-td-qnn-aot-runner`; host md5 `9d977b82ce9bc1736dff25d399706af2`, host size `37175784`; pushed to `/data/local/tmp/qwen2_moe_td_w8a16_clean_20260527/mllm-qwen2-moe-td-qnn-aot-runner`; phone md5 `9d977b82ce9bc1736dff25d399706af2`, phone size `37175784`.
Benchmark command: `/home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_state_relation_map_iter_01_fasttemp_p16_d16`
Compile result: success
Correctness result: pass (`ret=0`, `generated=16`)
Metrics:
  decode_tok_s: 0.33630144581876836
  mib_per_token: 1431.8021875
  required_miss_count: 2270
  upload_bytes:
  prewarm_hit_rate:
  eviction_churn: 2270
  required_miss_wait_ms_per_token: 1456.620750000001
  decode_req_page_touch_ms: 18377.522999999994
  decode_req_mat_enqueue_ms: 4887.693999999996
  decode_req_mat_finish_ms: 12.604000000000001
  decode_req_service_ms: 23305.932000000015
  decode_req_mat_writes: 2270
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 2270
  decode_req_hit: 8482
  decode_evict: 2270
  cache_hit_rate: 0.7888764880952381
  peak_temp_skin_c_decode: 35.06524
Result: logical_counter_only
Agent diagnosis: The patch moved logical cache accounting strongly (`decode_req_miss 6810 -> 2270`, hit rate `0.3666 -> 0.7889`) but did not reduce physical transfer (`decode_hybrid_core_upload_mib` unchanged at `22908.835`, `uploaded_expert_mib_per_token_metric` unchanged at `1431.8021875`, `decode_hybrid_req_mat_writes` unchanged at `2270`). Required service slightly worsened (`23067.089 ms -> 23305.932 ms`), so the apparent speed movement is noise or latency shift.
My diagnosis: This is exactly the false-positive risk in the map: the logical relation was updated for projection entries, but physical packed payload writes remained one per expert payload miss. The state-relation map prevented accepting a counter-only improvement as an optimization.
Needed expert knowledge: Need a relation that changes the number of physical payload writes/page touches or total service, not only the projection-level logical entry count.
Patch / commit: archived at `/home/liuxu/projects/mobile-moe-ako/patches/failed_attempts/s6_state_relation_map_iter_01_logical_counter_only.patch`; runtime source reverted.

## s6_state_relation_map_iter_02_fasttemp_p16_d16

Iteration ID: s6_state_relation_map_iter_02_fasttemp_p16_d16
Stage: S6-State-Relation-Map
Agent prompt setting: state-relation-map gated optimization iteration.
Selected state relation: `HybridPrefetchScheduler` speculative core pending/resource records plus `ProjectionCache::entries` populated by `submitAsyncPrewarmHybridColdGpuLayer` / `prewarmLayer`, later read by required decode `ensureExpertsCachedBatchGpuV3`.
Patch hypothesis gate: logical read site `runProjectionImplGpuV3` -> `ensureExpertsCachedBatchGpuV3` reads `ProjectionCache::entries` before required materialization; logical write/update site `submitAsyncPrewarmHybridColdGpuLayer` calls `hybrid_prefetch_scheduler_.beginPending`, `HybridColdGpuShadowExecutor::submitPrewarmAsync`, `prewarmLayer`, and then scheduler completion; physical action is speculative OpenCL core payload upload into the same projection/payload arenas used by later required decode accesses; later access expected to change behavior is later required decode materialization either seeing a resident entry or avoiding contention from ineffective speculative uploads; active benchmark evidence was baseline decode `decode_hybrid_pre_hit=0`, `decode_hybrid_pre_miss=0`, `decode_hybrid_req_service_ms=23067.08900000003`, `decode_hybrid_core_upload_mib=22908.835`, with total-run prewarm submits/completes but no decode pre-hit signal; expected primary movement was higher `decode_tok_s`; expected diagnostic movement was lower required service / upload scheduling time with unchanged MiB/token and core upload MiB; rejection condition was flat/regressed throughput, no service improvement, transfer regression, or only scheduler-counter movement.
Baseline bottleneck decomposition: baseline required decode materialization/service remained dominant (`decode_hybrid_req_service_ms=23067.08900000003`, `decode_hybrid_req_page_touch_mib=22908.835`, `decode_hybrid_core_upload_mib=22908.835`) and iter_01 proved that logical hit/miss movement alone is insufficient.
Targeted bottleneck: scheduling contention from decode-phase speculative core prewarm that did not produce measured decode prewarm hits.
Expected diagnostic movement: scheduling/service win only; `decode_hybrid_req_service_ms`, core upload enqueue/finish, or GPU/decode time should improve while `uploaded_expert_mib_per_token_metric` and `decode_hybrid_core_upload_mib` do not regress. This is not a transfer-volume hypothesis.
Agent hypothesis: If decode-phase same-layer speculative core prewarm is submitted after the required routing/materialization path and does not create later decode pre-hits, disabling that speculative core path during decode should reduce contention without reducing required work. Prefill and factor/window prewarm remain unchanged.
Chosen optimization direction: scheduling relation.
Files inspected: `/home/liuxu/projects/mllm/examples/qwen2_moe_td_qnn_aot/aot_run.cpp` (`fillRoutingWithBandwidthPriority`, `submitAsyncPrewarmHybridColdGpuLayer`, `prewarmLayer`, `ensureExpertsCachedBatchGpuV3`, decode loop); `/home/liuxu/projects/mobile-moe-ako/results/runs/s6_state_relation_map_baseline_fasttemp_p16_d16/summary.jsonl`; `/home/liuxu/projects/mobile-moe-ako/results/runs/s6_state_relation_map_iter_01_fasttemp_p16_d16/summary.jsonl`.
Files modified: `/home/liuxu/projects/mllm/examples/qwen2_moe_td_qnn_aot/aot_run.cpp`
Change summary: Changed `speculative_core_has_future_use` so same-layer speculative core prewarm is not submitted during decode; prefill speculative core and factor prewarm paths are unchanged.
Build/deploy verification: build success with `cmake --build /home/liuxu/projects/mllm/build-android-arm64-v8a-qnn --target mllm-qwen2-moe-td-qnn-aot-runner`; host md5 `a218e5eba1a9471d97822b3572fa0a99`, host size `36912952`, mode `775`, mtime `2026-07-03 18:07:28.914029001 +0800`; pushed to `/data/local/tmp/qwen2_moe_td_w8a16_clean_20260527/mllm-qwen2-moe-td-qnn-aot-runner`; phone md5 `a218e5eba1a9471d97822b3572fa0a99`, phone size `36912952`, mode `777`, mtime `2026-07-03 18:07:28.000000000 +0800`; md5 verification matched.
Benchmark command: `/home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_state_relation_map_iter_02_fasttemp_p16_d16`
Compile result: success
Correctness result: pass (`ret=0`, `generated=16`)
Metrics:
  decode_tok_s: 0.3421510579385557
  mib_per_token: 1431.8021875
  required_miss_count: 6810
  eviction_churn: 6810
  required_miss_wait_ms_per_token: 1421.0867499999997
  decode_req_page_touch_ms: 18189.54200000002
  decode_req_mat_enqueue_ms: 4492.971
  decode_req_mat_finish_ms: 12.256999999999998
  decode_req_service_ms: 22737.387999999995
  decode_req_mat_writes: 2270
  decode_req_page_touch_mib: 22908.835
  decode_core_upload_mib: 22908.835
  decode_req_miss: 6810
  decode_req_hit: 3942
  decode_evict: 6810
  decode_hybrid_pre_hit: 0
  decode_hybrid_pre_miss: 0
  hybrid_submit: 27
  hybrid_complete: 27
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 34.44508
Result: tentative_scheduling_signal / below_3pct_primary_threshold
Agent diagnosis: The patch preserved correctness and transfer volume, reduced total prewarm submissions (`hybrid_submit 177 -> 27` overall), improved decode throughput (`0.33411581168205445 -> 0.3421510579385557`, about +2.4%), and reduced required decode service (`23067.089 ms -> 22737.388 ms`) with lower enqueue time (`4838.285 ms -> 4492.971 ms`). Physical transfer (`decode_hybrid_core_upload_mib=22908.835`, `uploaded_expert_mib_per_token_metric=1431.8021875`) and required miss/materialization write counts were unchanged, matching a scheduling rather than transfer hypothesis.
My diagnosis: Keep as the current best candidate but do not declare a final optimization win from p16/d16 alone because the primary gain is below the skill's rough 3% meaningful-improvement rule and physical bytes did not change. It is not a logical-counter-only false positive: the relevant non-counter support is lower service time and stable guardrails. A p32/d32 recheck is required before accepting it as best.
Needed expert knowledge: The state-relation map helped reject counter-only changes and forced this patch to be framed as scheduling/resource contention rather than transfer reduction. No additional answer-level mechanism is needed for this candidate, but stronger diagnostics would separate speculative core upload time from factor/window prewarm time in decode.
Patch / commit: pending best-candidate patch in working tree; no commit yet pending p32/d32 recheck or later archive.

## s6_state_relation_map_best_recheck_fasttemp_p32_d32

Iteration ID: s6_state_relation_map_best_recheck_fasttemp_p32_d32
Stage: S6-State-Relation-Map
Agent prompt setting: p32/d32 signal recheck for best correctness-passing state-relation candidate.
Selected state relation: same as iter_02, `HybridPrefetchScheduler` speculative core prewarm records / `ProjectionCache::entries` versus later required decode materialization.
Patch hypothesis gate: no new source edit; rechecked iter_02 scheduling candidate. The expected behavior was continued correctness, no MiB/token regression relative to the p32 contract's own measured transfer, no decode prewarm counter-only false positive, and sustained reduction of decode-phase speculative submits (`hybrid_submit`) compared with baseline p16 pattern. Because no clean p32 baseline is run in this experiment, this recheck cannot by itself prove p32 speedup over baseline.
Baseline bottleneck decomposition: p16 baseline/iter_02 comparison showed stable physical transfer and modest service reduction from disabling decode-phase speculative core prewarm.
Targeted bottleneck: scheduling contention / ineffective decode speculative core prewarm.
Expected diagnostic movement: correctness and stable physical-transfer accounting under the longer p32/d32 signal contract; no transfer win claim without a same-contract baseline.
Agent hypothesis: The small iter_02 patch should remain correctness-safe on longer decode and keep speculative prewarm submissions limited without changing required physical upload volume semantics.
Chosen optimization direction: scheduling relation recheck.
Files inspected: `/home/liuxu/projects/mobile-moe-ako/results/runs/s6_state_relation_map_best_recheck_fasttemp_p32_d32/summary.jsonl`
Files modified: none beyond iter_02 source patch.
Change summary: Reused the already verified iter_02 binary (`a218e5eba1a9471d97822b3572fa0a99`) for the p32/d32 fixed signal contract.
Build/deploy verification: host md5 `a218e5eba1a9471d97822b3572fa0a99`, host size `36912952`, mode `775`, mtime `2026-07-03 18:07:28.914029001 +0800`; phone md5 `a218e5eba1a9471d97822b3572fa0a99`, phone size `36912952`, mode `777`, mtime `2026-07-03 18:07:28.000000000 +0800`; md5 verification matched before the recheck.
Benchmark command: `/home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p32.jsonl --decode-tokens 32 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_state_relation_map_best_recheck_fasttemp_p32_d32`
Compile result: reused verified build
Correctness result: pass (`ret=0`, `generated=32`)
Metrics:
  decode_tok_s: 0.3113455828750278
  mib_per_token: 1551.1785312499956
  required_miss_count: 14655
  eviction_churn: 14655
  required_miss_wait_ms_per_token: 1546.96234375
  decode_req_page_touch_ms: 39706.21599999999
  decode_req_mat_enqueue_ms: 9676.030000000006
  decode_req_mat_finish_ms: 27.137999999999952
  decode_req_service_ms: 49502.795
  decode_req_mat_writes: 4885
  decode_req_page_touch_mib: 49637.71299999986
  decode_core_upload_mib: 49637.71299999986
  decode_req_miss: 14655
  decode_req_hit: 6849
  decode_evict: 14655
  decode_hybrid_pre_hit: 0
  decode_hybrid_pre_miss: 0
  hybrid_submit: 27
  hybrid_complete: 27
  cache_hit_rate: 0.31849888392857145
  peak_temp_skin_c_decode: 37.06632
Result: correctness_passing_recheck / supports_scheduling_candidate_with_thermal_caveat
Agent diagnosis: The candidate survived the longer p32/d32 run with correctness and stable semantics: no decode pre-hit/pre-miss counter-only story, no benchmark/parser changes, and the same reduced speculative submit pattern. The run is not a same-contract speed comparison because this experiment did not run a p32/d32 baseline; additionally the decode peak skin temperature reached `37.06632 C`, so this recheck should be treated as signal rather than a clean verdict.
My diagnosis: The p32/d32 run supports keeping iter_02 as the best small, interpretable scheduling patch, but acceptance remains modest: the actual baseline comparison is the p16/d16 result (+2.4% decode throughput, stable MiB/token, lower required service), below the rough 3% threshold but backed by relation-consistent service diagnostics.
Needed expert knowledge: No extra mechanism required; the state-relation map was useful mainly as a rejection/causal-framing discipline.
Patch / commit: iter_02 candidate remains in working tree for final best-patch decision.

## s6_state_relation_map_stop_summary

Iteration ID: s6_state_relation_map_stop_summary
Stage: S6-State-Relation-Map
Agent prompt setting: final summary for state-relation-map gated MobileMoE-AKO run.
Optimization result: best candidate is commit `eba65d7a` in `/home/liuxu/projects/mllm` (`[s6 state relation] Reduce decode speculative core prewarm`). It is a small scheduling-service candidate, not a transfer-volume win. The p16/d16 baseline was rebuilt/deployed from `da9fa3534a16c0f34adb6709e2ba871741cbf8cc` with host/phone md5 `6d15f401a12e515d066141c3a02ba4ea`. Baseline `decode_tok_s=0.33411581168205445`, `uploaded_expert_mib_per_token_metric=1431.8021875`, `decode_hybrid_req_service_ms=23067.08900000003`, `decode_hybrid_core_upload_mib=22908.835`, correctness pass. Best p16/d16 candidate md5 `a218e5eba1a9471d97822b3572fa0a99` improved `decode_tok_s` to `0.3421510579385557` (+2.4%), held MiB/token at `1431.8021875`, held `decode_hybrid_core_upload_mib=22908.835`, and reduced `decode_hybrid_req_service_ms` to `22737.387999999995`. The effect is below the rough 3% threshold, so classify as modest/tentative scheduling signal rather than a strong win.
Relation-localization result: The required state-relation map was useful. Iter_01 selected the logical-cache-to-physical-payload relation and produced a large logical hit/miss improvement, but physical upload/page-touch volume and materialization writes did not move; the map correctly forced rejection as `logical_counter_only`. Iter_02 selected the scheduler/materialization relation and was accepted only because a non-counter service diagnostic moved with stable transfer and correctness.
Failed patches: iter_01 archived as `/home/liuxu/projects/mobile-moe-ako/patches/failed_attempts/s6_state_relation_map_iter_01_logical_counter_only.patch`; rejected because it improved cache counters without reducing physical work or service.
Best patch classification: `tentative_scheduling_signal`. Commit `eba65d7a` disables decode-phase same-layer speculative core prewarm while preserving prefill speculative core and factor/window prewarm. It reduced overall prewarm submissions (`hybrid_submit 177 -> 27`) and lowered p16 required service without changing physical bytes. p32/d32 recheck passed correctness (`ret=0`, `generated=32`) and preserved the reduced submit pattern, but it is not a same-contract speed proof because no p32 baseline was run and decode peak skin reached `37.06632 C`.
Harness discipline conclusion: State-relation localization improved physical-vs-logical reasoning. It did not uncover a strong transfer-reducing patch, but it prevented accepting counter-only cache bookkeeping and forced the accepted candidate to be framed as scheduling/service only. The main missing diagnostic is a sharper split of speculative core upload/service contention versus required materialization time, ideally with per-phase speculative-core upload/service attribution.
