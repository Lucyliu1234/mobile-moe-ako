Use $mobile-moe-ako.

You are running S3: Key-File-Set Guided Whole-System Exploration for MobileMoE-AKO.

Target runtime repo:
/home/liuxu/projects/mllm

Harness package:
/home/liuxu/projects/mobile-moe-ako

Branch:
exp/s3-key-files-codex-mobile-moe-ako

Goal:
Improve decode_tok_s on the fixed benchmark while preserving correctness and not worsening normalized transfer volume.

Stage definition:
S3 differs from S2 by providing a candidate key-file set and a static file-to-mechanism map. You may use high-level mobile MoE runtime concepts and the supplied key-file map, but you must not use prior S1/S2 failed patches or trajectory knowledge.

Allowed S3 concepts:
- dynamic expert/core serving
- expert/core residency
- eviction churn
- prewarm and prefetch hit rate
- required miss service latency
- transfer scheduling / overlap
- heterogeneous CPU/GPU/NPU execution
- GPU expert path as optional comparison

Do not read or use:
- iterations/s1_*
- iterations/s2_*
- patches/failed_attempts/s1_*
- patches/failed_attempts/s2_*
- previous Claude/Codex S1 or S2 failed patches
- previous S1/S2 logs as optimization guidance
- references/prompts/s4_single_file.md

You may read:
- /home/liuxu/projects/mobile-moe-ako/SKILL.md
- references/constraints.md
- references/benchmark_instructions.md
- references/metrics_schema.md
- references/prompts/s3_key_file_set.md
- references/expert_hints/coremoe_required_core.md if you need more S3 domain context

Key file candidates and static mechanism map:

1. examples/qwen2_moe_td_qnn_aot/aot_run.cpp
   Main Qwen2 TD QNN AOT runner and high-level runtime policy surface.
   Contains GPU shadow cache behavior, required-miss path, page-touch mode,
   hot-resident logic, decode counters, environment defaults, and high-level
   prewarm/runtime toggles.

2. mllm/backends/opencl/moe/HybridOpenCLMaterializer.cpp
   mllm/backends/opencl/moe/HybridOpenCLMaterializer.hpp
   Controls OpenCL materialization, host-to-device writes, staging/resource
   creation, enqueue/finish behavior, and upload sequencing.
   Relevant for required miss service latency and transfer overlap.

3. mllm/backends/opencl/moe/HybridOpenCLMaterializedResource.cpp
   mllm/backends/opencl/moe/HybridOpenCLMaterializedResource.hpp
   Defines materialized OpenCL resource ownership, lifetime, and release behavior.
   Relevant for resource reuse or release timing.

4. mllm/backends/opencl/moe/HybridPrefetchScheduler.cpp
   mllm/backends/opencl/moe/HybridPrefetchScheduler.hpp
   Controls prefetch scheduling, pending/resident/protected accounting,
   budget throttling, and speculative core/factor prewarm decisions.
   Relevant for prewarm hit rate, wasted prefetch, and residency pressure.

5. mllm/backends/opencl/moe/HybridResourceManager.cpp
   mllm/backends/opencl/moe/HybridResourceManager.hpp
   Tracks external resources and cache/resource ownership.
   Relevant for residency bookkeeping and resource reuse.

6. mllm/backends/opencl/moe/HybridExternalStorage.cpp
   mllm/backends/opencl/moe/HybridExternalStorage.hpp
   Controls mmap/external storage backing for expert payloads.
   Relevant if page-touch, mmap residency, or host storage access is suspected.

Read-mostly context unless the call path proves an edit is necessary:
- mllm/backends/qnn/aot_rt/TokenGenerator.cpp
- mllm/backends/qnn/aot_rt/TokenGenerator.hpp
These files help understand QNN decode-loop boundaries, but avoid editing them unless they clearly control the benchmarked runtime policy bottleneck.

Before editing:
1. Create or switch to branch exp/s3-key-files-codex-mobile-moe-ako in /home/liuxu/projects/mllm.
2. Do not continue from any S1 or S2 experiment branch.
3. If currently on an S1/S2 branch, switch back to the clean base branch first, then create S3 from that clean base.
4. Verify the runtime repo is clean or explicitly report existing changes.
5. Do not merge, cherry-pick, or reuse S1/S2 patches.
6. Map each candidate file to the runtime behavior it controls.
7. Identify the most likely policy bottleneck from the S3 baseline diagnostics.
8. Choose one file or one tightly coupled file group for one coherent change.

Benchmark contract:
Use the fixed temperature-gated Tucker end-to-end runner. Do not modify the runner, dataset, prompts, correctness checks, generated-token accounting, metric parser semantics, model artifacts, or benchmark contract.

For S3 baseline and smoke iterations, use this exact command shape:

cd /home/liuxu/projects/mobile-moe-ako
/home/liuxu/projects/tucker/tucker_env/bin/python \
  /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py \
  --serial 10.29.230.131:5555 \
  --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl \
  --decode-tokens 16 \
  --repeats 1 \
  --idle-seconds 30 \
  --sleep-between-runs-s 0 \
  --cooldown-poll-s 30 \
  --cooldown-max-wait-s 600 \
  --max-start-skin-c 37 \
  --max-start-battery-c 34 \
  --context-len 384 \
  --gpu-cache-capacity 8 \
  --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/<iteration_id>

Use these iteration IDs:
- s3_codex_baseline_fasttemp_p16_d16
- s3_codex_iter_01_fasttemp_p16_d16
- s3_codex_iter_02_fasttemp_p16_d16
- s3_codex_iter_03_fasttemp_p16_d16
- s3_codex_iter_04_fasttemp_p16_d16
- s3_codex_iter_05_fasttemp_p16_d16

Before the first source edit:
1. Run S3 baseline s3_codex_baseline_fasttemp_p16_d16 using the exact benchmark contract above.
2. Analyze the S3 baseline diagnostic decomposition. Record:
   - decode_tok_s
   - mib_per_token
   - required_miss_count
   - required_miss_wait_ms_per_token
   - cache_hit_rate
   - prewarm_hit_rate if available
   - eviction_churn
   - thermal state
   - missing diagnostics
   - suspected dominant bottleneck using S3 concepts and the key-file map

Build/deploy rule:
Before the first source edit, explicitly identify the build and deploy command that updates the phone-side runtime binary/artifacts used by the Tucker runner. After every source edit, rebuild and deploy. Verify deployment by reporting a changed phone-side checksum, timestamp, or equivalent artifact identity. If you cannot verify that the optimized binary is actually running on the phone, stop and report a blocker.

Iteration rules:
Run up to 5 S3 smoke iterations, but early-stop after 3 consecutive no-signal or hypothesis-mismatch iterations.

For each iteration:
1. Inspect the candidate key files and verify the relevant call path.
2. Form one concrete hypothesis from S3 baseline or previous S3 iteration diagnostics.
3. Name the targeted bottleneck and expected diagnostic movement.
4. Make one coherent runtime-policy change only.
5. Do not combine unrelated mechanisms in one iteration.
6. Rebuild, deploy, and verify the phone-side artifact changed.
7. Run the same p16/d16 temperature-gated benchmark.
8. Immediately append /home/liuxu/projects/mobile-moe-ako/ITERATIONS.md with metrics and diagnosis.
9. Commit a useful correctness-passing change, or archive the failed/no-signal patch under /home/liuxu/projects/mobile-moe-ako/patches/failed_attempts/ before starting the next hypothesis.
10. Revert only your own failed edits before the next iteration.

Failure handling:
Archive and diagnose:
- compile failure
- deploy verification failure
- correctness failure
- generated-token mismatch
- decode_tok_s regression
- no metric movement
- hypothesis/metric mismatch
- wrong file localization
- forbidden-surface edit

Best patch selection:
After the S3 smoke iterations, select the best correctness-passing patch based on:
- decode_tok_s improvement over S3 baseline
- no unacceptable mib_per_token regression
- diagnostics consistent with the hypothesis
- small and interpretable code change

Then recheck the best patch with the daytime signal contract:

cd /home/liuxu/projects/mobile-moe-ako
/home/liuxu/projects/tucker/tucker_env/bin/python \
  /home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py \
  --serial 10.29.230.131:5555 \
  --dataset /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p32.jsonl \
  --decode-tokens 32 \
  --repeats 1 \
  --idle-seconds 30 \
  --sleep-between-runs-s 0 \
  --cooldown-poll-s 30 \
  --cooldown-max-wait-s 600 \
  --max-start-skin-c 37 \
  --max-start-battery-c 34 \
  --context-len 384 \
  --gpu-cache-capacity 8 \
  --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s3_codex_best_recheck_fasttemp_p32_d32

Do not run the evening verdict benchmark unless explicitly asked.

Reporting:
At the end, summarize:
- S3 baseline metrics
- file-to-mechanism mapping used
- each iteration hypothesis and selected key file
- changed files
- build/deploy verification
- each iteration metrics
- failed patches and why they failed
- best patch or no-useful-patch conclusion
- whether S3 key-file guidance improved localization compared with S2
- what additional expert knowledge would be needed for S4
