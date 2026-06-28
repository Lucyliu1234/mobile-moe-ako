# MobileMoE-AKO Iterations

## Current Stage

S5: Expert-Knowledge-Guided MobileMoE Optimization.

This root `ITERATIONS.md` is the active S5 working log only.

Archived previous-stage logs:

- `iterations/s1_codex_blackbox.md`
- `iterations/s1_codex_blackbox_completed.md`
- `iterations/s2_codex_concept_guided.md`
- `iterations/s3_codex_key_file_set.md`
- `iterations/s4_codex_required_miss_service.md`

S5 agents must not read previous-stage iteration logs or failed patches as direct patch guidance unless the user explicitly allows it. S5 may use the mechanism-level summary provided in the S5 prompt, fixed benchmark contract, durable constraints, metrics schema, and stage-allowed expert sources.

## Template

```text
Iteration ID:
Stage: S5-expert-knowledge-guided
Agent prompt setting:
Expert knowledge gap:
Expert source used:
Expert claim learned:
Core mechanism:
Mechanism invariant:
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
  cache_hit_rate:
  eviction_churn:
  peak_temp_skin_c_decode:
Result:
Agent diagnosis:
My diagnosis:
Needed expert knowledge:
Patch / commit:
```


## s5_codex_baseline_fasttemp_p16_d16

Iteration ID: s5_codex_baseline_fasttemp_p16_d16
Stage: S5-expert-knowledge-guided
Agent prompt setting: Expert-knowledge-first required-miss service optimization.
Expert knowledge gap: Whether explicit mmap page-touch before OpenCL upload is necessary to front-load faults and keep host-pointer upload safe, or whether nonblocking OpenCL upload will fault/pin/copy from mmap pages itself such that page-touch only shifts latency among req_page_touch_ms, req_mat_enqueue_ms, and req_mat_finish_ms.
Expert source used: Linux madvise(2) semantics and Khronos OpenCL clEnqueueWriteBuffer semantics.
Expert claim learned: MADV_WILLNEED is a best-effort near-future access/read-ahead hint, not a synchronous residency guarantee. For nonblocking clEnqueueWriteBuffer, the implementation may keep using the host pointer until command completion, so host memory must remain valid until the queued write completes.
Core mechanism: GPU-v3 required-miss service uses mmap-backed expert payload pointers, explicit CPU page touching, nonblocking OpenCL write enqueue, then clFinish before the required core is used.
Mechanism invariant: A useful patch must reduce end-to-end decode_tok_s denominator or total required-miss service latency, not merely move time among req_page_touch_ms, req_mat_enqueue_ms, and req_mat_finish_ms. Host payload pointers must remain valid until clFinish completes.
Baseline bottleneck decomposition: decode_tok_s=0.3409916651; generated=16; decode_s=46.921968s; mib_per_token=1431.8021875; required_miss_count=6810 decode req misses; required_miss_wait_ms_per_token=1486.4373125; decode_hybrid_req_page_touch_ms=18749.696; decode_hybrid_req_mat_enqueue_ms=4975.179; decode_hybrid_req_mat_finish_ms=13.547; decode_hybrid_req_service_ms=23782.997; cache_hit_rate=0.3666294643; eviction_churn=6810 decode evictions; peak_temp_skin_c_decode=34.65636C; start_battery_c=31.6C; start_skin_c=30.08876C.
Targeted bottleneck: req_page_touch_ms dominates required-miss service; finish wait is negligible, so queue overlap is not currently the limiting diagnostic.
Expected diagnostic movement: First edit should reduce req_page_touch_ms and total req_service_ms with no increase in mib_per_token, no correctness failure, and no equal/opposite increase in req_mat_enqueue_ms or req_mat_finish_ms.
Agent hypothesis: Full 4 KiB page-touch over 22.9 GiB of decode payload front-loads more CPU-side fault/read work than the OpenCL write path needs. A sparser touch policy can retain a light WILLNEED/fault hint and pointer lifetime safety while shrinking total required-miss service.
Chosen optimization direction: Expert-knowledge-guided mmap page-touch policy for required GPU-v3 payloads.
Selected edit region: examples/qwen2_moe_td_qnn_aot/aot_run.cpp touchMmapPages and GPU-v3 required-miss materialization paths.
Files inspected: SKILL.md; references/constraints.md; references/benchmark_instructions.md; references/metrics_schema.md; references/expert_hints/coremoe_required_core.md; examples/qwen2_moe_td_qnn_aot/aot_run.cpp; mllm/backends/opencl/moe/HybridOpenCLMaterializer.cpp; Tucker runner source.
Files modified: none.
Change summary: Baseline only; no source edit.
Benchmark command: cd /home/liuxu/projects/mobile-moe-ako && /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s5_codex_baseline_fasttemp_p16_d16
Compile result: not rebuilt; clean main branch binary matched phone artifact md5 6d15f401a12e515d066141c3a02ba4ea.
Correctness result: ret=0; generated=16/16.
Metrics:
  decode_tok_s: 0.340991665140729
  mib_per_token: 1431.8021875
  required_miss_count: 6810
  upload_bytes: 22908.835 MiB decode core upload
  required_miss_wait_ms_per_token: 1486.437312500001
  decode_req_page_touch_ms: 18749.695999999996
  decode_req_mat_enqueue_ms: 4975.178999999996
  decode_req_mat_finish_ms: 13.547000000000002
  decode_req_service_ms: 23782.997000000018
  cache_hit_rate: 0.3666294642857143
  eviction_churn: 6810
  peak_temp_skin_c_decode: 34.65636
Result: Correct S5 baseline established before any source edit.
Agent diagnosis: Required-miss service is about half of decode time; page touch is the largest subcomponent, enqueue second, finish negligible.
My diagnosis: The right first hypothesis is page-touch policy, not queue batching/interleaving, because the current stack already batches/interleaves and clFinish wait is tiny.
Needed expert knowledge: Need device-specific evidence whether sparse touch reduces total req_service or simply moves implicit faults into OpenCL enqueue. Iteration 01 will test this directly under the fixed contract.
Patch / commit: none

## s5_codex_iter_01_fasttemp_p16_d16

Iteration ID: s5_codex_iter_01_fasttemp_p16_d16
Stage: S5-expert-knowledge-guided
Agent prompt setting: Expert-knowledge-first required-miss service optimization.
Expert knowledge gap: Does explicit 4 KiB mmap page touching over-front-load page faults, or does the OpenCL upload path implicitly fault/pin the same pages such that reducing touch density only shifts latency?
Expert source used: Linux madvise(2); Khronos OpenCL clEnqueueWriteBuffer.
Expert claim learned: MADV_WILLNEED is advisory read-ahead, and nonblocking OpenCL writes keep host-pointer lifetime requirements until completion.
Core mechanism: Sparse explicit touching of GPU-v3 mmap payload before nonblocking OpenCL upload, preserving clFinish.
Mechanism invariant: Must improve total required-miss service and decode throughput, not just shift req_page_touch/enqueue/finish.
Baseline bottleneck decomposition: baseline decode_tok_s=0.3409916651; decode req_service_ms=23782.997; req_page_touch_ms=18749.696; req_mat_enqueue_ms=4975.179; req_mat_finish_ms=13.547; mib_per_token=1431.8021875; req_miss=6810.
Targeted bottleneck: req_page_touch_ms.
Expected diagnostic movement: Lower req_page_touch_ms and lower req_service_ms, without a compensating enqueue/finish increase.
Agent hypothesis: Touching one cache line per 64 KiB should reduce CPU page-touch work while retaining enough MADV_WILLNEED/read-ahead hinting and host-pointer lifetime safety.
Chosen optimization direction: Reduce explicit mmap page-touch density for GPU-v3 required payloads.
Selected edit region: examples/qwen2_moe_td_qnn_aot/aot_run.cpp touchMmapPages call sites for GPU-v3 packed payload materialization.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; mllm/backends/opencl/moe/HybridOpenCLMaterializer.cpp.
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp.
Change summary: Added touchMmapPagesSparse with 64 KiB stride and used it for GPU-v3 packed payload required-miss uploads.
Benchmark command: cd /home/liuxu/projects/mobile-moe-ako && /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s5_codex_iter_01_fasttemp_p16_d16
Compile result: success; deployed phone artifact changed from baseline md5 6d15f401a12e515d066141c3a02ba4ea to e472a7985007efd517b11715dad796a1, size 36913280, mtime 1782643120.
Correctness result: ret=0; generated=16/16.
Metrics:
  decode_tok_s: 0.3430878130469905
  mib_per_token: 1431.8021875
  required_miss_count: 6810
  upload_bytes: 22908.835 MiB decode core upload
  required_miss_wait_ms_per_token: 1492.2098749999993
  decode_req_page_touch_ms: 18709.34199999999
  decode_req_mat_enqueue_ms: 5105.732000000006
  decode_req_mat_finish_ms: 16.93999999999997
  decode_req_service_ms: 23875.35799999999
  cache_hit_rate: 0.3666294642857143
  eviction_churn: 6810
  peak_temp_skin_c_decode: 36.1414
Result: Failed/no-useful patch. Correctness passed and decode_tok_s was +0.61%, but total required-miss service worsened by 92.361 ms and required_miss_wait_ms_per_token worsened.
Agent diagnosis: The intended page-touch reduction did not materialize in decode; page_touch moved only -40.354 ms while enqueue and finish rose +133.946 ms, causing worse total required-miss service.
My diagnosis: The expert-informed hypothesis was mostly falsified for the decode metric. The high page-touch time likely comes from MADV_WILLNEED/read-ahead or unavoidable faulting, not just loop granularity. The tiny throughput gain is not accepted under the S5 invariant.
Needed expert knowledge: Need to test whether removing the synchronous MADV_WILLNEED call, while still explicitly reading every page to satisfy host-pointer upload safety, reduces read-ahead pressure without deferring faults into enqueue.
Patch / commit: archived patches/failed_attempts/s5_codex_iter_01_fasttemp_p16_d16.patch; source reverted.

## s5_codex_iter_02_fasttemp_p16_d16

Iteration ID: s5_codex_iter_02_fasttemp_p16_d16
Stage: S5-expert-knowledge-guided
Agent prompt setting: Expert-knowledge-first required-miss service optimization.
Expert knowledge gap: Is MADV_WILLNEED itself the costly part of explicit page-touch, or is explicit page faulting unavoidable for this mmap-to-OpenCL upload path?
Expert source used: Linux madvise(2) semantics.
Expert claim learned: MADV_WILLNEED is advisory and may initiate near-future read-ahead, but explicit loads are what deterministically fault mmap pages into the process.
Core mechanism: Required GPU-v3 miss service with per-page explicit load and nonblocking OpenCL upload.
Mechanism invariant: Throughput must improve and total required-miss service must not regress; tiny service movement under thermal regression is not useful.
Baseline bottleneck decomposition: baseline decode_tok_s=0.3409916651; decode req_service_ms=23782.997; req_page_touch_ms=18749.696; req_mat_enqueue_ms=4975.179; req_mat_finish_ms=13.547; mib_per_token=1431.8021875; req_miss=6810.
Targeted bottleneck: req_page_touch_ms, specifically the MADV_WILLNEED part.
Expected diagnostic movement: Lower page_touch and req_service without deferring faults into enqueue/finish.
Agent hypothesis: Removing MADV_WILLNEED while preserving per-page touch may avoid costly read-ahead without violating host-pointer upload safety.
Chosen optimization direction: Disable MADV_WILLNEED inside required page touch while keeping explicit page reads.
Selected edit region: examples/qwen2_moe_td_qnn_aot/aot_run.cpp touchMmapPages.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; iteration 01 diagnostics.
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp.
Change summary: Removed the madvise(MADV_WILLNEED) call from touchMmapPages.
Benchmark command: cd /home/liuxu/projects/mobile-moe-ako && /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s5_codex_iter_02_fasttemp_p16_d16
Compile result: success; deployed phone artifact changed from baseline md5 6d15f401a12e515d066141c3a02ba4ea to 683448d43fe07ed0eb072988ec977754, size 36911176, mtime 1782643581.
Correctness result: ret=0; generated=16/16.
Metrics:
  decode_tok_s: 0.3380786546328978
  mib_per_token: 1431.8021875
  required_miss_count: 6810
  upload_bytes: 22908.835 MiB decode core upload
  required_miss_wait_ms_per_token: 1486.2166875000005
  decode_req_page_touch_ms: 18695.824999999983
  decode_req_mat_enqueue_ms: 5014.293000000001
  decode_req_mat_finish_ms: 22.147999999999985
  decode_req_service_ms: 23779.467000000008
  cache_hit_rate: 0.3666294642857143
  eviction_churn: 6810
  peak_temp_skin_c_decode: 36.4074
Result: Failed/no-useful patch. Correctness passed and req_service moved -3.530 ms, but decode_tok_s regressed -0.85% and thermal state was worse.
Agent diagnosis: Removing MADV_WILLNEED slightly reduced page_touch (-53.871 ms) but enqueue/finish rose (+47.716 ms), so total service was effectively unchanged and decode regressed.
My diagnosis: MADV_WILLNEED is not a useful local policy lever under this contract; page touching and upload are bound to the same memory-read cost.
Needed expert knowledge: Need a mechanism that changes when required-miss service happens, not merely how page faults are bucketed. Candidate: preserve correctness while serving less than the full per-call miss batch before GPU execution only if the executor does not need all 8 slots immediately; this requires code-path verification.
Patch / commit: archived patches/failed_attempts/s5_codex_iter_02_fasttemp_p16_d16.patch; source reverted.

## s5_codex_stop_no_useful_patch

Iteration ID: s5_codex_stop_no_useful_patch
Stage: S5-expert-knowledge-guided
Agent prompt setting: Expert-knowledge-first required-miss service optimization.
Expert knowledge gap: After page-touch variants failed, whether another local runtime-policy lever remains inside the required-miss mmap/OpenCL mechanism without changing correctness or benchmark semantics.
Expert source used: Code-path verification plus Linux/OpenCL source claims from prior S5 entries.
Expert claim learned: Top-8 required experts are consumed together by the cold GPU execution; reducing required service batch size would not safely reduce required work and would risk serializing or changing semantics. Nonblocking OpenCL host-pointer lifetime still requires preserving source memory until completion.
Core mechanism: Required GPU-v3 miss service path for packed payloads.
Mechanism invariant: Stop rather than continue blind local search after consecutive no-useful/hypothesis-mismatch attempts and no safe next local lever.
Baseline bottleneck decomposition: baseline decode_tok_s=0.3409916651; mib_per_token=1431.8021875; required_miss_count=6810; required_miss_wait_ms_per_token=1486.4373125; req_page_touch_ms=18749.696; req_mat_enqueue_ms=4975.179; req_mat_finish_ms=13.547; req_service_ms=23782.997; cache_hit_rate=0.3666294643; eviction_churn=6810; peak_temp_skin_c_decode=34.65636.
Targeted bottleneck: No further safe edit selected.
Expected diagnostic movement: none.
Agent hypothesis: No third patch is justified without deeper instrumentation/device-stack knowledge; page-touch changes only moved or preserved latency and required batch-size changes are not semantically safe.
Chosen optimization direction: Early stop with no useful patch.
Selected edit region: none.
Files inspected: examples/qwen2_moe_td_qnn_aot/aot_run.cpp required miss batching/execution path.
Files modified: none remaining; failed edits reverted.
Change summary: Stopped after two failed page-touch policy attempts and a code-path check rejected required-batch modification as unsafe.
Benchmark command: not run for stop entry.
Compile result: clean baseline rebuild success; phone restored to md5 6d15f401a12e515d066141c3a02ba4ea, size 36912960, mtime 1782644097.
Correctness result: last useful baseline correct; failed attempts both correctness-passing but not useful.
Metrics:
  decode_tok_s: baseline 0.340991665140729; iter01 0.3430878130469905; iter02 0.3380786546328978
  mib_per_token: all 1431.8021875
  required_miss_count: all 6810 decode required misses
  upload_bytes: all 22908.835 MiB decode core upload
  required_miss_wait_ms_per_token: baseline 1486.4373125; iter01 1492.209875; iter02 1486.2166875
  decode_req_page_touch_ms: baseline 18749.696; iter01 18709.342; iter02 18695.825
  decode_req_mat_enqueue_ms: baseline 4975.179; iter01 5105.732; iter02 5014.293
  decode_req_mat_finish_ms: baseline 13.547; iter01 16.940; iter02 22.148
  decode_req_service_ms: baseline 23782.997; iter01 23875.358; iter02 23779.467
  cache_hit_rate: all 0.3666294643
  eviction_churn: all 6810
  peak_temp_skin_c_decode: baseline 34.65636; iter01 36.1414; iter02 36.4074
Result: No useful S5 patch selected; no p32/d32 recheck run because there is no candidate satisfying the best-patch criteria.
Agent diagnosis: Expert-knowledge-first prevented a blind third edit: the page-fault/OpenCL interaction appears to be a real floor for this local path, and batching/interleaving is already present with negligible finish wait.
My diagnosis: S5 improved the research conclusion versus S4 by producing mechanism evidence: explicit page-touch is not a standalone removable bottleneck under this device stack; OpenCL enqueue and mmap fault/read-ahead costs are coupled.
Needed expert knowledge: To move further, add instrumentation or consult vendor/device-stack detail for whether clEnqueueWriteBuffer copies synchronously from pageable mmap memory on this Qualcomm OpenCL stack, whether pinned/staging host buffers can overlap with QNN execution, and whether prefetch timing can shift required misses earlier without increasing transfer volume or evictions.
Patch / commit: no useful commit; failed patches archived as patches/failed_attempts/s5_codex_iter_01_fasttemp_p16_d16.patch and patches/failed_attempts/s5_codex_iter_02_fasttemp_p16_d16.patch.
