# MobileMoE-AKO Iterations - S5 Rerun Profiled Codex

Active stage: S5 rerun, expert-knowledge-guided with updated profiling metrics.

Isolation rules:
- Do not read or use S6 branch, commit, patches, logs, or result artifacts.
- Do not read iterations/s6_* or results/runs/s6_*.
- This file is the active S5 rerun log only.


## s5_rerun_profiled_iter_01_fasttemp_p16_d16

Iteration ID: s5_rerun_profiled_iter_01_fasttemp_p16_d16
Stage: s5_rerun_profiled
Agent prompt setting: S5 expert-knowledge-guided rerun with updated profiling metrics; no S6 trajectory knowledge
Baseline bottleneck decomposition: 
Targeted bottleneck: 
Expected diagnostic movement: 
Agent hypothesis: Baseline required-miss service is dominated by decode page-touch (~18.85s of ~23.79s service). Switching default core page-touch mode away from the explicit CPU touch path should reduce decode_req_page_touch_ms and improve decode_tok_s without changing transfer volume.
Chosen optimization direction: mmap/page-touch and OpenCL required-core upload interaction
Files inspected: references/constraints.md; references/benchmark_instructions.md; references/metrics_schema.md; references/expert_hints/coremoe_required_core.md; references/expert_hints/diagnostic_instrumentation.md; examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Changed default hybrid_gpu_core_page_touch_mode_ from 0 to 1, leaving env override intact.
Benchmark command: cd /home/liuxu/projects/mobile-moe-ako && /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s5_rerun_profiled_iter_01_fasttemp_p16_d16
Compile result: 
Correctness result: 
Metrics:
  decode_tok_s: 0.33977586600055304
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
  peak_temp_skin_c_decode: 34.13728
Result: correct ret=0 generated=16; decode_tok_s=0.3397758660 vs baseline 0.3441633657; mib_per_token=1431.8021875 unchanged; required_miss_service_ms_per_token=1498.4335 worse; page_touch_ms=18802.538 ~ unchanged; enqueue_ms=5086.722 worse; peak_skin_decode=34.137C hotter.
Agent diagnosis: Hypothesis mismatch/no useful speed signal. The updated profile shows explicit page-touch accounting did not fall, so the default change did not remove the dominant page-touch path and instead slightly worsened enqueue/service time under comparable transfer volume.
My diagnosis: Archive and revert. Next direction should target cache churn/required miss count or required upload batching/residency, because decode_req_miss==decode_evict==6810 and transfer volume did not move.
Needed expert knowledge: Allowed S5 expert context: required-core serving, mmap/page-touch/OpenCL upload interaction, expert/core residency and eviction churn. Local evidence came from baseline summary.jsonl and aot_run.cpp materialize/page-touch paths.
Patch / commit: archived patches/failed_attempts/s5_rerun_profiled_iter_01_fasttemp_p16_d16.patch; not committed

## s5_rerun_profiled_iter_02_fasttemp_p16_d16

Iteration ID: s5_rerun_profiled_iter_02_fasttemp_p16_d16
Stage: s5_rerun_profiled
Agent prompt setting: S5 expert-knowledge-guided rerun with updated profiling metrics; no S6 trajectory knowledge
Baseline bottleneck decomposition: 
Targeted bottleneck: 
Expected diagnostic movement: 
Agent hypothesis: Baseline has high required upload fragmentation (decode_req_mat_writes=2270 and enqueue_ms~4882). Raising the default required batch upload experts from 4 to top-k 8 should reduce materializer write calls and enqueue/service time without changing MiB/token.
Chosen optimization direction: required-miss upload batching / transfer scheduling
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp materializeCoreSlotBatchGpuV3 and ensureExpertsCachedBatchGpuV3 paths; baseline and iter_01 summary.jsonl
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Changed default hybrid_gpu_required_batch_upload_experts_ from 4 to 8.
Benchmark command: cd /home/liuxu/projects/mobile-moe-ako && /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s5_rerun_profiled_iter_02_fasttemp_p16_d16
Compile result: 
Correctness result: 
Metrics:
  decode_tok_s: 0.33462376806691235
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
  peak_temp_skin_c_decode: 35.18228
Result: correct ret=0 generated=16; decode_tok_s=0.3346237681 vs baseline 0.3441633657; mib_per_token=1431.8021875 unchanged; req_miss=6810 req_hit=3942 evict=6810 unchanged; req_mat_writes=2270 unchanged; enqueue_ms=5113.144 worse; service_ms=24026.85 worse; peak_skin_decode=35.182C.
Agent diagnosis: Hypothesis mismatch/no useful signal. Increasing required_batch_upload_experts did not reduce decode write count, so the active materializer span granularity is not controlled by this default in the measured path. Thermal was also hotter, but diagnostics moved in the wrong direction independent of volume.
My diagnosis: Archive and revert. Updated profiling suggests the bottleneck is dominated by required miss count/cache churn and page-touch volume, not this simple batching knob.
Needed expert knowledge: Allowed S5 expert context: OpenCL host upload batching, required-miss service, cache churn. Local evidence: decode_req_mat_writes stayed fixed while enqueue/service worsened.
Patch / commit: archived patches/failed_attempts/s5_rerun_profiled_iter_02_fasttemp_p16_d16.patch; not committed

## s5_rerun_profiled_iter_03_fasttemp_p16_d16

Iteration ID: s5_rerun_profiled_iter_03_fasttemp_p16_d16
Stage: s5_rerun_profiled
Agent prompt setting: S5 expert-knowledge-guided rerun with updated profiling metrics; no S6 trajectory knowledge
Baseline bottleneck decomposition: 
Targeted bottleneck: 
Expected diagnostic movement: 
Agent hypothesis: Baseline decode has severe cache churn (decode_req_miss=6810 and decode_evict=6810) with repeated required overlap. Enabling the existing hot-resident core eviction policy by default should protect recently/current required experts inside the fixed 8-slot cache, reducing req_miss/evict, MiB/token, and service time.
Chosen optimization direction: expert/core residency and eviction policy
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp selectCacheVictim hot-resident policy and default knob; baseline, iter_01, iter_02 summary.jsonl
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Changed default hybrid_gpu_hot_resident_core_ from false to true; did not change cache capacity.
Benchmark command: cd /home/liuxu/projects/mobile-moe-ako && /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s5_rerun_profiled_iter_03_fasttemp_p16_d16
Compile result: 
Correctness result: 
Metrics:
  decode_tok_s: 0.3345692600607695
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
  peak_temp_skin_c_decode: 35.75684
Result: correct ret=0 generated=16; decode_tok_s=0.3345692601 vs baseline 0.3441633657; mib_per_token=1431.8021875 unchanged; req_miss=6810 req_hit=3942 evict=6810 unchanged; hit_rate=0.366629 unchanged; page_touch_ms=19047.959 worse; enqueue_ms=5272.879 worse; service_ms=24382.587 worse; peak_skin_decode=35.757C.
Agent diagnosis: Hypothesis mismatch/no useful signal. The hot-resident policy did not alter aggregate residency under this workload and fixed cache capacity; required miss/evict/transfer counters were unchanged and service worsened.
My diagnosis: Archive and revert. This is the third consecutive no-signal/hypothesis mismatch; stop early per protocol. Updated profiling made the failure mode clearer: simple page-touch, upload batch, and hot-residency knobs do not reduce the dominant required-miss volume in this path.
Needed expert knowledge: Allowed S5 expert context: expert/core residency, eviction churn, required-miss service. Local evidence: unchanged req_miss/evict/hit/MiB counters after enabling hot-resident eviction protection.
Patch / commit: archived patches/failed_attempts/s5_rerun_profiled_iter_03_fasttemp_p16_d16.patch; not committed
