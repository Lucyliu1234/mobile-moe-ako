Use $mobile-moe-ako.

You are running a fresh Codex S1: Whole-System Black-Box Exploration for MobileMoE-AKO.

This is NOT a continuation of the previous Claude Code S1 attempt.
Existing Claude S1 logs may exist in ITERATIONS.md, results/runs, and patches/failed_attempts.
Do not use those Claude results as baseline, optimization guidance, or evidence for this run.
Only use existing run names to avoid filename collisions.

Target runtime repo:
/home/liuxu/projects/mllm

Harness package:
/home/liuxu/projects/mobile-moe-ako

Fixed host-side benchmark harness:
/home/liuxu/projects/tucker/scripts/run_qwen2_moe_td_end2end.py

Branch:
exp/s1-blackbox-codex-mobile-moe-ako

Goal:
Improve decode_tok_s on the fixed benchmark while preserving correctness and not worsening normalized transfer volume.

Important distinction:
- The Tucker host-side runner is the fixed benchmark harness. It handles adb, prompt upload, thermal cooldown, logs, and metrics.
- Do not modify the Tucker runner, benchmark prompts, correctness checks, generated-token accounting, or metric parser semantics.
- The optimization target is the runtime source under /home/liuxu/projects/mllm.
- After changing runtime source, verify that the changed runtime is built and deployed to the phone-side setup used by the benchmark before claiming performance results.
- If the build/deploy path is missing or unclear, discover it from existing repo scripts/logs. If it cannot be verified, stop and report the blocker instead of reporting a speed result.

Hard limits:
- Run S1 only.
- Verify /home/liuxu/projects/mllm is on branch exp/s1-blackbox-codex-mobile-moe-ako and clean before editing. If dirty, stop and ask the user.
- Run at most 1 temperature-gated p16/d16 baseline.
- Run up to 5 temperature-gated p16/d16 S1 smoke iterations.
- Stop early if 3 consecutive iterations are compile failures, correctness failures, no-signal regressions, or repeat the same blocker.
- Run at most 1 temperature-gated p32/d32 recheck for the best correctness-passing patch.
- Total benchmark runs must not exceed 7.
- Do not run S2/S3/S4.
- Do not run the 4mix p32/d64 evening verdict benchmark unless explicitly asked.
- If the same blocker repeats for 30 minutes or 3 failed attempts, stop and write the blocker to ITERATIONS.md.

Context policy:
This is a black-box whole-system exploration stage. You may inspect the runtime repo and the MobileMoE-AKO base harness files, but you must not read:
- /home/liuxu/projects/mobile-moe-ako/references/expert_hints/
- /home/liuxu/projects/mobile-moe-ako/references/prompts/s2_concept_guided.md
- /home/liuxu/projects/mobile-moe-ako/references/prompts/s3_key_file_set.md
- /home/liuxu/projects/mobile-moe-ako/references/prompts/s4_single_file.md
- prior human optimization notes, if any

Do not ask for key files. Discover relevant code paths yourself.

Search policy:
Do not use web search for MoE optimization ideas in S1. If the benchmark, build, deploy, or harness cannot run, you may search only for neutral environment/tooling issues such as adb connectivity, Android thermal measurement, QNN runtime errors, shell issues, or build errors.
Do not search for expert caching, expert prefetching, residency, required-core serving, CoreMoE, or MoE-specific optimization mechanisms.

Benchmark contract:
Use the Tucker Qwen2 TD end-to-end runner as the fixed benchmark harness.
Baseline and optimized versions must use the same host-side runner and the same thermal gate.
Do not use a non-temperature-controlled benchmark for performance comparison.

S1 p16/d16 temperature-gated smoke contract:

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

Use this exact p16/d16 contract for:
- s1_codex_baseline_fasttemp_p16_d16
- s1_codex_iter_01_fasttemp_p16_d16
- s1_codex_iter_02_fasttemp_p16_d16
- s1_codex_iter_03_fasttemp_p16_d16
- s1_codex_iter_04_fasttemp_p16_d16
- s1_codex_iter_05_fasttemp_p16_d16

Only replace <iteration_id> with the current ID. Do not change the runner, serial, temperature gate, context length, gpu cache capacity, dataset, decode tokens, repeats, or correctness behavior within this p16/d16 contract.

Before editing source code:
1. Verify the runtime repo is clean and on exp/s1-blackbox-codex-mobile-moe-ako.
2. Run or cite baseline s1_codex_baseline_fasttemp_p16_d16 using the exact p16/d16 contract above.
3. Analyze the baseline using only benchmark-exposed metrics, logs, and device state. Record:
   - primary metric
   - correctness
   - generated-token status
   - normalized transfer guardrail if exposed
   - thermal/device state if exposed
   - any other raw metrics the harness reports
   - missing diagnostics
   - suspected bottleneck inferred by the agent
Do not use supplied MoE-specific categories to interpret the baseline in S1.

Iteration rules:
Run up to 5 S1 smoke iterations unless blocked or early-stop criteria are met.

For each iteration:
1. Inspect the repo yourself.
2. Form one concrete hypothesis from the Codex baseline or previous Codex iteration feedback only.
3. Name the targeted bottleneck and expected metric/diagnostic movement.
4. Make one coherent runtime-policy change only.
5. Build and deploy the changed runtime to the phone-side setup used by the benchmark. Verify deployment before benchmarking. If deployment cannot be verified, stop and report the blocker.
6. Do not edit benchmark inputs, prompts, generated-token accounting, correctness checks, metric parser semantics, Tucker runner files, model artifacts, or the benchmark contract.
7. Run the same p16/d16 temperature-gated benchmark contract.
8. Immediately append ITERATIONS.md with metrics and diagnosis.
9. Commit a useful correctness-passing change, or archive the failed/no-signal patch under /home/liuxu/projects/mobile-moe-ako/patches/failed_attempts/ before starting the next hypothesis.

Failure handling:
Archive and diagnose:
- compile failure
- deployment failure
- correctness failure
- generated-token mismatch
- decode_tok_s regression
- normalized transfer regression
- no metric movement
- wrong file localization
- forbidden-surface edit
- hypothesis/metric mismatch

After smoke iterations:
Select the best correctness-passing patch based on:
- decode_tok_s improvement over Codex baseline
- no unacceptable normalized transfer regression
- diagnostics consistent with the hypothesis
- build/deploy was verified
- small and interpretable code change

Then recheck the best patch with the p32/d32 temperature-gated signal contract:

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
  --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s1_codex_best_recheck_fasttemp_p32_d32

For the p32/d32 recheck, do not change the runner, serial, temperature gate, context length, gpu cache capacity, dataset, decode tokens, repeats, or correctness behavior.

Do not run the 4mix p32/d64 evening verdict benchmark unless explicitly asked. The evening verdict is reserved for comparing Codex baseline vs best patch with:
--dataset /home/liuxu/projects/results/ds_tilemoe/ds2_cold20_prompts_quick_4mix_p32.jsonl
--decode-tokens 64
using the same Tucker runner and stricter thermal-control policy.

Reporting:
At the end, summarize:
- branch and final commit/patch state
- Codex baseline metrics
- Codex baseline black-box bottleneck inference
- each Codex iteration hypothesis and changed files
- whether build/deploy was verified for each iteration
- each Codex iteration metrics
- failed patches and why they failed
- best patch or no-useful-patch conclusion
- p32/d32 recheck result if run
- what expert knowledge seemed missing
- whether S1 black-box exploration localized the right system surface
