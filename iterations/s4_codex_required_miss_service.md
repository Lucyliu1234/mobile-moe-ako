# MobileMoE-AKO Iterations

## Current Stage

S4: Single-Mechanism Local Optimization.

Mechanism focus: required-miss service path in `examples/qwen2_moe_td_qnn_aot/aot_run.cpp`, especially mmap page-touch plus OpenCL upload interaction for GPU-v3 expert payloads.

This root `ITERATIONS.md` is the active S4 working log only.

Archived previous-stage logs:

- `iterations/s1_codex_blackbox.md`
- `iterations/s1_codex_blackbox_completed.md`
- `iterations/s2_codex_concept_guided.md`
- `iterations/s3_codex_key_file_set.md`

S4 agents must not read `iterations/s1_*`, `iterations/s2_*`, `iterations/s3_*`, `patches/failed_attempts/s1_*`, `patches/failed_attempts/s2_*`, or `patches/failed_attempts/s3_*` as patch-level guidance unless the user explicitly allows it. S4 may use the mechanism-level context in the S4 prompt, fixed benchmark contract, durable constraints, metrics schema, and stage-allowed expert concepts.

## Template

```text
Iteration ID:
Stage: S4-single-mechanism
Agent prompt setting:
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


## s4_codex_baseline_fasttemp_p16_d16

Iteration ID: s4_codex_baseline_fasttemp_p16_d16
Stage: S4-single-mechanism
Agent prompt setting: S4 single-mechanism required-miss service baseline; no source edit
Baseline bottleneck decomposition: decode_tok_s=0.335468, mib_per_token=1431.802, req_miss=14736, req_wait_ms_per_token=1449.086; decode req_service=23185.381ms, page_touch=18630.476ms, mat_enqueue=4495.200ms, mat_finish=15.338ms; page_touch dominates service but invariant forbids counting a shift into enqueue/finish as useful.
Targeted bottleneck: Baseline only: GPU-v3 required-miss mmap page-touch plus OpenCL upload interaction.
Expected diagnostic movement: No movement expected for baseline; establishes S4 reference decomposition and deployed artifact md5 6d15f401a12e515d066141c3a02ba4ea.
Agent hypothesis: Baseline diagnostic pass: required-miss service appears dominated by explicit mmap page touching before OpenCL upload.
Chosen optimization direction: Measure fixed p16/d16 contract before edits.
Files inspected: SKILL.md; constraints.md; benchmark_instructions.md; metrics_schema.md; s4_single_file.md; coremoe_required_core.md; aot_run.cpp required-miss path; HybridOpenCLMaterializer.{cpp,hpp}; Tucker runner build/env path
Files modified: results/runs/s4_codex_baseline_fasttemp_p16_d16/metrics.json; ITERATIONS.md
Change summary: Generated normalized metrics from baseline summary and recorded S4 baseline decomposition; no runtime source edit.
Benchmark command: cd /home/liuxu/projects/mobile-moe-ako && /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s4_codex_baseline_fasttemp_p16_d16
Compile result: PASS: no edit; pre-edit phone artifact verified md5 6d15f401a12e515d066141c3a02ba4ea size 36912960 timestamp 1782637572
Correctness result: PASS: ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.3354680282195705
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1449.0863125000014
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 36.17788
Result: Baseline correctness passing; service decomposition recorded.
Agent diagnosis: Dominant decode required-miss subcomponent is explicit page touch (18630.476ms of 23185.381ms service), with enqueue also material at 4495.200ms and finish negligible.
My diagnosis: The first local variant should reduce explicit touch work only if total req_service or decode_tok_s improves; page_touch-only reductions are invalid if enqueue/finish/service rise by the same amount.
Needed expert knowledge: Need OpenCL/Android mmap behavior: whether sparse/coarse touching with MADV_WILLNEED preserves enough residency to avoid blocking inside clEnqueueWriteBuffer.
Patch / commit: baseline-only log; no patch

## s4_codex_iter_01_fasttemp_p16_d16

Iteration ID: s4_codex_iter_01_fasttemp_p16_d16
Stage: S4-single-mechanism
Agent prompt setting: S4 single-mechanism required-miss service; local page-touch granularity variant
Baseline bottleneck decomposition: Baseline decode req_service=23185.381ms, page_touch=18630.476ms, mat_enqueue=4495.200ms, mat_finish=15.338ms, decode_tok_s=0.335468, mib_per_token=1431.802.
Targeted bottleneck: CPU explicit mmap page-touch cost in GPU-v3 required payload service path.
Expected diagnostic movement: Lower req_page_touch_ms without a matching increase in req_mat_enqueue_ms/req_mat_finish_ms/req_service_ms; stable mib_per_token and correctness.
Agent hypothesis: Coarser required-payload touching can retain useful MADV_WILLNEED/page residency while reducing CPU touch overhead on large GPU-v3 payloads.
Chosen optimization direction: Required-miss mmap page-touch granularity in examples/qwen2_moe_td_qnn_aot/aot_run.cpp.
Files inspected: aot_run.cpp touchMmapPages, materializeCoreSlotBatchGpuV3, materializePackedExpertSlotBatchGpuV3; HybridOpenCLMaterializer enqueue/finish paths; baseline and iter01 summaries
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; results/runs/s4_codex_iter_01_fasttemp_p16_d16/metrics.json; ITERATIONS.md; patches/failed_attempts/s4_codex_iter_01_fasttemp_p16_d16.patch
Change summary: Added touchRequiredMmapPayloadPages with 64KiB stride for >=1MiB required payloads and used it only at the two GPU-v3 required packed payload touch sites.
Benchmark command: cd /home/liuxu/projects/mobile-moe-ako && /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s4_codex_iter_01_fasttemp_p16_d16
Compile result: PASS: rebuilt cmake target; deployed phone md5 changed 6d15f401a12e515d066141c3a02ba4ea -> bee56769f76e1c9a6cc6ff3d18c3d121, size 36913312, timestamp 1782638870
Correctness result: PASS: ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.3374448243440457
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1475.2752499999997
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 36.37776
Result: Failed/no-signal: decode_tok_s +0.59% but required-miss service worsened and diagnostic movement contradicted hypothesis.
Agent diagnosis: decode req_page_touch rose 18630.476->18748.862ms, enqueue rose 4495.200->4750.162ms, finish rose 15.338->61.274ms, req_service rose 23185.381->23604.404ms; mib_per_token unchanged 1431.802 and correctness passed.
My diagnosis: The small throughput increase is not a useful S4 win because total required-miss service worsened and latency did not move in the expected direction. Coarser sparse touching likely did not reduce the dominant residency cost and may have left more blocking for OpenCL enqueue/finish.
Needed expert knowledge: Need finer evidence separating madvise cost, CPU load loop cost, and OpenCL pin/page fault behavior for clEnqueueWriteBuffer on mmap-backed host pointers.
Patch / commit: archived failed patch: patches/failed_attempts/s4_codex_iter_01_fasttemp_p16_d16.patch

## s4_codex_iter_02_fasttemp_p16_d16

Iteration ID: s4_codex_iter_02_fasttemp_p16_d16
Stage: S4-single-mechanism
Agent prompt setting: S4 single-mechanism required-miss service; required-payload touch without madvise
Baseline bottleneck decomposition: Baseline decode req_service=23185.381ms, page_touch=18630.476ms, mat_enqueue=4495.200ms, mat_finish=15.338ms, decode_tok_s=0.335468, mib_per_token=1431.802.
Targeted bottleneck: Per-required-payload MADV_WILLNEED overhead inside synchronous page-touch before OpenCL upload.
Expected diagnostic movement: Lower req_page_touch_ms with stable enqueue/finish and lower total req_service_ms; stable mib_per_token and correctness.
Agent hypothesis: Because the required path immediately reads every mmap page, per-payload MADV_WILLNEED may be redundant syscall/hint overhead; removing it may reduce page_touch without shifting cost to OpenCL.
Chosen optimization direction: Required-miss mmap page-touch/MADV_WILLNEED behavior in examples/qwen2_moe_td_qnn_aot/aot_run.cpp.
Files inspected: aot_run.cpp touchMmapPages, materializeCoreSlotBatchGpuV3, materializePackedExpertSlotBatchGpuV3; baseline/iter02 summaries
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; results/runs/s4_codex_iter_02_fasttemp_p16_d16/metrics.json; ITERATIONS.md; patches/failed_attempts/s4_codex_iter_02_fasttemp_p16_d16.patch
Change summary: Added required-payload-only touch helper that keeps 4KiB page loads but omits MADV_WILLNEED; used it only at the two GPU-v3 required packed payload touch sites.
Benchmark command: cd /home/liuxu/projects/mobile-moe-ako && /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s4_codex_iter_02_fasttemp_p16_d16
Compile result: PASS: rebuilt cmake target; deployed phone md5 changed bee56769f76e1c9a6cc6ff3d18c3d121 -> 0e64c1e0ff89be105c7d6b590f326ac1, size 36912408, timestamp 1782639609
Correctness result: PASS: ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.33618454245325796
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1496.6011874999988
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 36.30632
Result: Failed latency-shift: decode_tok_s +0.21% but total required-miss service worsened; page_touch drop was outweighed by enqueue increase.
Agent diagnosis: decode req_page_touch fell 18630.476->18399.062ms, but enqueue rose 4495.200->5481.628ms, finish rose 15.338->20.819ms, and req_service rose 23185.381->23945.619ms; mib_per_token unchanged 1431.802.
My diagnosis: MADV_WILLNEED was not merely overhead; removing it moved or increased required-miss latency in OpenCL enqueue, so this is not useful under the S4 invariant.
Needed expert knowledge: Need direct separation of madvise syscall latency from OpenCL host-pointer page/pin behavior to know whether any hint timing can help.
Patch / commit: archived failed patch: patches/failed_attempts/s4_codex_iter_02_fasttemp_p16_d16.patch

## s4_codex_iter_03_fasttemp_p16_d16

Iteration ID: s4_codex_iter_03_fasttemp_p16_d16
Stage: S4-single-mechanism
Agent prompt setting: S4 single-mechanism required-miss service; batch enqueue after touch loop
Baseline bottleneck decomposition: Baseline decode req_service=23185.381ms, page_touch=18630.476ms, mat_enqueue=4495.200ms, mat_finish=15.338ms, decode_tok_s=0.335468, mib_per_token=1431.802.
Targeted bottleneck: OpenCL nonblocking enqueue overhead/interaction after required-miss page touch.
Expected diagnostic movement: req_page_touch_ms roughly unchanged, req_mat_enqueue_ms lower, req_mat_finish_ms not worse, total req_service_ms lower, stable mib_per_token and correctness.
Agent hypothesis: Touching all required payloads first and submitting one batch of DeviceUploadSpan entries can reduce enqueue overhead while preserving the same upload bytes and finish boundary.
Chosen optimization direction: Required-miss OpenCL enqueue batching in examples/qwen2_moe_td_qnn_aot/aot_run.cpp.
Files inspected: aot_run.cpp materializeCoreSlotBatchGpuV3 and materializePackedExpertSlotBatchGpuV3; HybridOpenCLMaterializer enqueueDeviceSpans/finishDeviceUploads; baseline/iter03 summaries
Files modified: examples/qwen2_moe_td_qnn_aot/aot_run.cpp; results/runs/s4_codex_iter_03_fasttemp_p16_d16/metrics.json; ITERATIONS.md; patches/failed_attempts/s4_codex_iter_03_fasttemp_p16_d16.patch
Change summary: Changed mode-2 GPU-v3 required payload path to collect spans while touching payloads, then call enqueueDeviceSpans once before the existing finishDeviceUploads.
Benchmark command: cd /home/liuxu/projects/mobile-moe-ako && /home/liuxu/projects/tucker/tucker_env/bin/python /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py --serial 10.29.230.131:5555 --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl --decode-tokens 16 --repeats 1 --idle-seconds 30 --sleep-between-runs-s 0 --cooldown-poll-s 30 --cooldown-max-wait-s 600 --max-start-skin-c 37 --max-start-battery-c 34 --context-len 384 --gpu-cache-capacity 8 --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s4_codex_iter_03_fasttemp_p16_d16
Compile result: PASS: rebuilt cmake target; deployed phone md5 changed 0e64c1e0ff89be105c7d6b590f326ac1 -> ea00366ff3a59dcad75686a3bade89bb, size 36902504, timestamp 1782640281
Correctness result: PASS: ret=0 generated=16/16
Metrics:
  decode_tok_s: 0.3338770381784637
  mib_per_token: 1431.8021875
  required_miss_count: 14736.0
  upload_bytes: 52181244837.888
  prewarm_hit_rate: None
  eviction_churn: 14064.0
  required_miss_wait_ms_per_token: 1496.0939375000014
  cache_hit_rate: 0.3666294642857143
  peak_temp_skin_c_decode: 36.16876
Result: Failed/regression: decode_tok_s regressed to 0.333877 and total required-miss service worsened despite lower enqueue time.
Agent diagnosis: decode enqueue fell 4495.200->3123.662ms, but page_touch rose 18630.476->19903.703ms and finish rose 15.338->865.795ms; req_service rose 23185.381->23937.503ms; mib_per_token unchanged 1431.802.
My diagnosis: Batching enqueue after all page touches removed some enqueue overhead but changed timing enough to increase finish/page-touch costs and hurt end-to-end decode. This is not useful under the S4 invariant and completes three consecutive no-signal/hypothesis-mismatch attempts.
Needed expert knowledge: Need OpenCL command queue/event-level profiling and page-fault/pin timing to know whether enqueue should be interleaved with touching, batched differently, or overlapped with another independent required-miss step.
Patch / commit: archived failed patch: patches/failed_attempts/s4_codex_iter_03_fasttemp_p16_d16.patch
