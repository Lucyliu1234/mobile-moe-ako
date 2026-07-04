Use $mobile-moe-ako.

You are running S2: Concept-Guided Whole-System Exploration for MobileMoE-AKO.

Target runtime repo:
/home/liuxu/projects/mllm

Harness package:
/home/liuxu/projects/mobile-moe-ako

Branch:
exp/s2-concept-guided-codex-mobile-moe-ako

Goal:
Improve decode_tok_s on the fixed benchmark while preserving correctness and not worsening normalized transfer volume.

Stage definition:
S2 differs from S1 by allowing high-level mobile MoE runtime concepts, but still does not provide key files or prior failed patches. Your task is to test whether concept-level expert guidance helps you localize the right runtime policy surface.

Allowed S2 concepts:
- dynamic expert/core serving
- expert/core residency
- eviction churn
- prewarm and prefetch hit rate
- required miss service latency
- transfer scheduling / overlap
- heterogeneous CPU/GPU/NPU execution
- GPU expert path as optional comparison

You may interpret benchmark metrics using these concepts. You may inspect the runtime repo and MobileMoE-AKO base harness files.

Do not read or use:
- iterations/s1_*
- patches/failed_attempts/s1_*
- previous Claude/Codex S1 failed patches
- S1 logs as optimization guidance
- references/prompts/s3_key_file_set.md
- references/prompts/s4_single_file.md

You may read:
- /home/liuxu/projects/mobile-moe-ako/SKILL.md
- references/constraints.md
- references/benchmark_instructions.md
- references/metrics_schema.md
- references/prompts/s2_concept_guided.md
- references/expert_hints/coremoe_required_core.md if you need more S2 domain context

Do not ask for key files. Discover relevant code paths yourself.

Search policy:
Avoid broad web search. If local context is insufficient, you may search only for stage-relevant systems material: mobile MoE serving, expert caching, expert prefetching, residency, transfer scheduling, heterogeneous CPU/GPU/NPU execution, Android thermal benchmarking, Qualcomm QNN/OpenCL behavior, or MoE serving systems. Prefer local project notes, official vendor documentation, and systems papers. Record any external knowledge used.

Benchmark contract:
Use the fixed temperature-gated Tucker end-to-end runner. Do not modify the runner, dataset, prompts, correctness checks, generated-token accounting, metric parser semantics, model artifacts, or benchmark contract.

For S2 baseline and smoke iterations, use this exact command shape:

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
- s2_codex_baseline_fasttemp_p16_d16
- s2_codex_iter_01_fasttemp_p16_d16
- s2_codex_iter_02_fasttemp_p16_d16
- s2_codex_iter_03_fasttemp_p16_d16
- s2_codex_iter_04_fasttemp_p16_d16
- s2_codex_iter_05_fasttemp_p16_d16

Before editing source code:
1. Create or switch to branch exp/s2-concept-guided-codex-mobile-moe-ako in /home/liuxu/projects/mllm.
2. Verify the runtime repo is clean or explicitly report existing changes.
3. Run S2 baseline s2_codex_baseline_fasttemp_p16_d16 using the exact benchmark contract above.
4. Analyze the S2 baseline diagnostic decomposition before the first source edit. Record:
   - decode_tok_s
   - mib_per_token
   - required_miss_count
   - required_miss_wait_ms_per_token
   - cache_hit_rate
   - prewarm_hit_rate if available
   - eviction_churn
   - thermal state
   - missing diagnostics
   - suspected dominant bottleneck using S2 concepts

Build/deploy rule:
Before the first source edit, explicitly identify the build and deploy command that updates the phone-side runtime binary/artifacts used by the Tucker runner. After every source edit, rebuild and deploy. Verify deployment by reporting a changed phone-side checksum, timestamp, or equivalent artifact identity. If you cannot verify that the optimized binary is actually running on the phone, stop and report a blocker.

Iteration rules:
Run up to 5 S2 smoke iterations, but early-stop after 3 consecutive no-signal or hypothesis-mismatch iterations.

For each iteration:
1. Inspect the repo yourself.
2. Form one concrete hypothesis from S2 baseline or previous iteration diagnostics.
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
After the S2 smoke iterations, select the best correctness-passing patch based on:
- decode_tok_s improvement over S2 baseline
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
  --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s2_codex_best_recheck_fasttemp_p32_d32

Do not run the evening verdict benchmark unless explicitly asked.

Reporting:
At the end, summarize:
- S2 baseline metrics
- each iteration hypothesis and S2 concept used
- changed files
- build/deploy verification
- each iteration metrics
- failed patches and why they failed
- best patch or no-useful-patch conclusion
- whether S2 concept guidance improved localization compared with S1
- what additional expert knowledge would be needed for S3
