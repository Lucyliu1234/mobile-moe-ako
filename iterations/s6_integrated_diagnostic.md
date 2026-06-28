# MobileMoE-AKO Iterations

## Current Stage

S6: Integrated Diagnostic AKO Loop.

This root `ITERATIONS.md` is the active S6 working log only.

Archived previous-stage logs:

- `iterations/s1_codex_blackbox.md`
- `iterations/s1_codex_blackbox_completed.md`
- `iterations/s2_codex_concept_guided.md`
- `iterations/s3_codex_key_file_set.md`
- `iterations/s4_codex_required_miss_service.md`
- `iterations/s5_codex_expert_knowledge.md`

S6 uses a single integrated AKO loop where each iteration is either an optimization iteration or a diagnostic iteration. Diagnostic iterations are inside the workflow, not a separate stage outside it.

S6 agents must not read previous-stage iteration logs or failed patches as direct patch guidance unless the user explicitly allows it. S6 may use the high-level previous-stage lesson supplied in the prompt, fixed benchmark contract, durable constraints, metrics schema, diagnostic instrumentation hints, and stage-allowed expert sources.

## Template

```text
Iteration ID:
Stage: S6-integrated-diagnostic
Iteration type: optimization | diagnostic
Agent prompt setting:
Observation gap:
Expert/source context:
Core mechanism:
Mechanism invariant:
Profiling report:
Baseline bottleneck decomposition:
Targeted bottleneck:
Expected diagnostic movement:
Agent hypothesis:
Chosen optimization direction:
Selected edit region:
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
  eviction_churn:
  peak_temp_skin_c_decode:
Result:
Agent diagnosis:
My diagnosis:
Needed expert knowledge:
Patch / commit:
```


## s6_codex_baseline_fasttemp_p16_d16

Iteration ID: s6_codex_baseline_fasttemp_p16_d16
Stage: S6-integrated-diagnostic
Agent prompt setting: MobileMoE-AKO S6 integrated diagnostic loop
Baseline bottleneck decomposition: 
Targeted bottleneck: 
Expected diagnostic movement: 
Agent hypothesis: Baseline profiling before first edit; determine whether required-miss counters are enough to choose an optimization iteration.
Chosen optimization direction: No code change; profile fixed p16/d16 benchmark and decompose required-miss service.
Files inspected: /home/liuxu/projects/mobile-moe-ako/references/constraints.md, /home/liuxu/projects/mobile-moe-ako/references/benchmark_instructions.md, /home/liuxu/projects/mobile-moe-ako/references/metrics_schema.md, /home/liuxu/projects/mobile-moe-ako/references/expert_hints/diagnostic_instrumentation.md, /home/liuxu/projects/mobile-moe-ako/results/runs/s6_codex_baseline_fasttemp_p16_d16/summary.jsonl
Files modified: /home/liuxu/projects/mobile-moe-ako/ITERATIONS.md
Change summary: Baseline run only; no runtime source edit.
Benchmark command: cd /home/liuxu/projects/mobile-moe-ako && /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_codex_baseline_fasttemp_p16_d16
Compile result: 
Correctness result: 
Metrics:
  decode_tok_s: 0.3366028337961447
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
  peak_temp_skin_c_decode: 32.43108
Result: Baseline correctness passed: ret=0, generated=16. decode_tok_s=0.3366028338, mib_per_token=1431.8021875, required_miss_count=6810, required_miss_wait_ms_per_token=1493.98425, decode_req_service_ms=23903.748. Existing counters include page_touch/enqueue/finish/write count/MiB/cache/churn and are sufficient for one initial optimization iteration; missing finer diagnostics include madvise vs touch-loop split, page fault counts, and per-layer/projection service.
Agent diagnosis: MobileMoE profiling report: required-miss service dominates decode. Page touch is the largest visible component at 18940.471 ms, enqueue is also material at 4903.351 ms, finish is tiny at 14.628 ms. Transfer volume is high at 1431.802 MiB/token with 22908.835 decode core upload MiB. Cache hit rate is 0.3666 and evictions equal misses at 6810, indicating heavy churn under capacity 8.
My diagnosis: Use existing counters before adding diagnostics: because service is dominated by page-touch and transfer volume/churn, the first optimization should target reducing redundant required misses or page-touch/upload work, not merely shifting latency among page_touch/enqueue/finish. Treat subcounter-only movement as failure unless decode_tok_s or total service improves without mib_per_token regression.
Needed expert knowledge: Need code-local understanding of GPU-v3 required payload selection, residency keys, eviction policy, and whether same-token/same-layer duplicate materialization can be avoided safely. If that is unclear after one attempt, add diagnostic counters for per-layer or per-projection required-miss service rather than guessing.
Patch / commit: baseline only; no patch

## s6_codex_iter_01_fasttemp_p16_d16

Iteration ID: s6_codex_iter_01_fasttemp_p16_d16
Stage: S6-integrated-diagnostic
Agent prompt setting: MobileMoE-AKO S6 integrated diagnostic loop
Baseline bottleneck decomposition: Baseline decode required-miss service 23903.748 ms; page_touch 18940.471 ms; enqueue 4903.351 ms; finish 14.628 ms; 6810 misses and 6810 evictions.
Targeted bottleneck: Reduce required miss churn by marking sibling projection cache entries when a full external packed expert payload is uploaded.
Expected diagnostic movement: Expected decode_req_miss/decode_evict/decode_req_mat_writes/mib_per_token/decode_req_service_ms to fall, with decode_tok_s improving if full payload residency was under-recorded.
Agent hypothesis: The gate projection external packed-payload path uploads gate/up/down payload in one write but may only record residency for the current projection, causing sibling up/down required misses and redundant service.
Chosen optimization direction: Optimization iteration: mirror full external expert payload residency into sibling projection caches.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; baseline summary.jsonl
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Added markExternalExpertPayloadResidentNoLock helper and attempted to call it after miss materialization.
Benchmark command: Not run; compile failed before deploy.
Compile result: Failed: call was inserted in the TileCoreMiss batch path, where miss has no packed_payload or packed_payload_bytes fields and cannot convert to GpuV3CoreMiss.
Correctness result: Not run
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
Result: compile failure; archived patch
Agent diagnosis: The policy idea may still be plausible, but this attempt localized the call to the wrong materialization loop. The compiler caught that TileCoreMiss and GpuV3CoreMiss paths are separate.
My diagnosis: Close as failed optimization iteration before further edits. Revert the failed hunks, then if continuing, place the same concept only in the GpuV3CoreMiss path or inspect whether the packed full path is already active.
Needed expert knowledge: Need exact distinction between legacy tile quant misses, per-projection GPU-v3 misses, and packed full-expert GPU-v3 misses before making cache-residency policy edits.
Patch / commit: /home/liuxu/projects/mobile-moe-ako/patches/failed_attempts/s6_codex_iter_01_fasttemp_p16_d16.patch

## s6_codex_iter_02_fasttemp_p16_d16

Iteration ID: s6_codex_iter_02_fasttemp_p16_d16
Stage: S6-integrated-diagnostic
Agent prompt setting: MobileMoE-AKO S6 integrated diagnostic loop
Baseline bottleneck decomposition: Baseline decode required-miss service 23903.748 ms; page_touch 18940.471 ms; enqueue 4903.351 ms; finish 14.628 ms; 6810 misses and 6810 evictions; mib_per_token 1431.8021875.
Targeted bottleneck: Required miss churn caused by under-recorded sibling projection residency after full external GPU-v3 expert payload upload.
Expected diagnostic movement: decode_req_miss, decode_evict, decode_req_mat_writes, decode_core_upload_mib, page_touch_mib, total service, and mib_per_token should fall; decode_tok_s should improve.
Agent hypothesis: When the base projection uploads a full packed expert payload into a shared external payload arena, sibling up/down projection caches should mark the same expert/slot resident so later projection calls hit instead of re-uploading.
Chosen optimization direction: Optimization iteration: mirror full external packed-payload residency into sibling GPU-v3 projection caches and remove the shared slot from sibling free slot lists.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; run_qwen2_moe_td_end2end.py env defaults; baseline and iteration summary.jsonl
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp
Change summary: Added markExternalExpertPayloadResidentNoLock and call in ensureExpertsCachedBatchGpuV3 after successful full external packed-payload materialization.
Benchmark command: cd /home/liuxu/projects/mobile-moe-ako && /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_codex_iter_02_fasttemp_p16_d16
Compile result: Passed. Host md5 ca804754b6e9ccddd0c0c5e65c3f6d39; deployed phone md5 ca804754b6e9ccddd0c0c5e65c3f6d39; phone ctime updated 2026-06-28 21:37:43 +0800.
Correctness result: Passed: ret=0 generated=16.
Metrics:
  decode_tok_s: 0.4131141538976739
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
  peak_temp_skin_c_decode: 33.07556
Result: Useful optimization. decode_tok_s 0.4131141539 vs baseline 0.3366028338 (+22.7%). mib_per_token 316.56725 vs 1431.8021875. decode_req_service_ms 16411.697 vs 23903.748; misses/evictions 1553/1553 vs 6810/6810; cache_hit_rate 0.85556 vs 0.36663.
Agent diagnosis: The expected counters moved together: miss count, writes, upload MiB, page-touch MiB, page-touch time, enqueue time, and total required-miss service all fell, while decode throughput improved and correctness passed. This is not just latency moving between subcounters.
My diagnosis: Best patch so far. The integrated baseline diagnostics directly pointed to required-miss service, and the code inspection found a residency accounting gap in the full external payload arena path. Remaining risk is whether bytes=0 sibling entries under-report resident slot bytes in final resident diagnostics, though transfer and scheduler accounting are intentionally not double-counted.
Needed expert knowledge: For further improvement, inspect whether the remaining 1553 decode misses are true new experts or residual eviction/core-pressure misses by layer/projection; per-layer/projection required-miss counters would help.
Patch / commit: 902e8d9c [s6 iter 02] Mark packed payload sibling residency
