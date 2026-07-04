Use $mobile-moe-ako.

You are running S5: Expert-Knowledge-Guided MobileMoE Optimization.

Target runtime repo:
/home/liuxu/projects/mllm

Harness package:
/home/liuxu/projects/mobile-moe-ako

Branch:
exp/s5-expert-knowledge-codex-mobile-moe-ako

Goal:
Improve decode_tok_s on the fixed benchmark while preserving correctness and not worsening normalized transfer volume.

Stage definition:
S5 differs from S4 by explicitly requiring expert knowledge before changing code. You should first identify the missing mechanism-level knowledge needed to reason about the required-miss service path, then use that knowledge to choose one local runtime-policy change. Do not continue blind local search.

Core performance target:
Required-miss service path for GPU-v3 expert payloads in:
examples/qwen2_moe_td_qnn_aot/aot_run.cpp

Mechanism focus:
mmap page-touch + OpenCL upload interaction, including whether page-touch is front-loading page faults, whether OpenCL upload is forcing implicit faults, and whether batching/interleaving can actually overlap on this device stack.

Allowed expert knowledge sources:
- Android/Linux mmap and page fault behavior
- madvise(WILLNEED) semantics
- OpenCL host-pointer upload semantics
- Qualcomm/QNN/OpenCL queue and event behavior
- MoE runtime residency/eviction invariants
- relevant official vendor docs, project notes, and systems papers

What you must do in S5:
1. Start from the S4 baseline and the required-miss service decomposition.
2. Identify the precise expert knowledge gap blocking a correct hypothesis.
3. Gather only the minimum expert knowledge needed to resolve that gap.
4. Use that knowledge to form one concrete hypothesis.
5. Make one coherent local runtime-policy change.
6. Rebuild, deploy, verify phone-side artifact identity, benchmark, log, and archive exactly like the earlier stages.

Important S5 invariant:
Do not count a patch as useful if it only moves latency among:
- req_page_touch_ms
- req_mat_enqueue_ms
- req_mat_finish_ms
without improving end-to-end decode_tok_s or total required-miss service latency.

You may inspect:
- /home/liuxu/projects/mobile-moe-ako/SKILL.md
- references/constraints.md
- references/benchmark_instructions.md
- references/metrics_schema.md
- references/experiment_protocol.md if needed for staged context
- references/expert_hints/coremoe_required_core.md
- official vendor docs and systems references relevant to mmap/OpenCL/Qualcomm behavior

Do not read or reuse:
- iterations/s1_*
- iterations/s2_*
- iterations/s3_*
- iterations/s4_*
- patches/failed_attempts/s1_*
- patches/failed_attempts/s2_*
- patches/failed_attempts/s3_*
- patches/failed_attempts/s4_*
- previous stage failed patches as direct patch guidance

Before editing:
1. Create or switch to branch exp/s5-expert-knowledge-codex-mobile-moe-ako from clean main.
2. Verify the runtime repo is clean or explicitly report existing changes.
3. Run or cite a baseline for the exact same benchmark contract.
4. Record the S4-derived bottleneck decomposition and the missing expert knowledge.
5. Decide which expert source you will use and why.
6. State the precise mechanism invariant and expected diagnostic movement.

Benchmark contract:
Use the fixed temperature-gated Tucker end-to-end runner. Do not modify the runner, dataset, prompts, correctness checks, generated-token accounting, metric parser semantics, model artifacts, or benchmark contract.

For S5 baseline and smoke iterations, use this exact command shape:

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
- s5_codex_baseline_fasttemp_p16_d16
- s5_codex_iter_01_fasttemp_p16_d16
- s5_codex_iter_02_fasttemp_p16_d16
- s5_codex_iter_03_fasttemp_p16_d16
- s5_codex_iter_04_fasttemp_p16_d16
- s5_codex_iter_05_fasttemp_p16_d16

Before the first source edit:
1. Run S5 baseline s5_codex_baseline_fasttemp_p16_d16 using the exact benchmark contract above.
2. Analyze the S5 baseline diagnostic decomposition. Record:
   - decode_tok_s
   - mib_per_token
   - required_miss_count
   - required_miss_wait_ms_per_token
   - decode_hybrid_req_page_touch_ms
   - decode_hybrid_req_mat_enqueue_ms
   - decode_hybrid_req_mat_finish_ms
   - decode_hybrid_req_service_ms
   - cache_hit_rate
   - eviction_churn
   - thermal state
   - missing diagnostics
   - exact expert knowledge gap you need to close before editing

Expert-knowledge phase:
Before the first code edit, you must consult and record at least one expert source relevant to the mechanism gap. Prefer official documentation or project-local notes. Summarize the concrete claim you learned and how it changes your hypothesis. If the source does not resolve the gap, do not guess; gather the next most relevant source.

Build/deploy rule:
Before the first source edit, explicitly identify the build and deploy command that updates the phone-side runtime binary/artifacts used by the Tucker runner. After every source edit, rebuild and deploy. Verify deployment by reporting a changed phone-side checksum, timestamp, or equivalent artifact identity. If you cannot verify that the optimized binary is actually running on the phone, stop and report a blocker.

Iteration rules:
Run up to 5 S5 smoke iterations, but early-stop after 3 consecutive no-signal or hypothesis-mismatch iterations.

For each iteration:
1. Use expert knowledge to form the hypothesis first.
2. Keep the edit within the required-miss service mechanism unless a tightly coupled helper is proven necessary.
3. Make one coherent local mechanism change only.
4. Rebuild, deploy, and verify the phone-side artifact changed.
5. Run the same p16/d16 temperature-gated benchmark.
6. Immediately append /home/liuxu/projects/mobile-moe-ako/ITERATIONS.md with metrics and diagnosis.
7. Commit a useful correctness-passing change, or archive the failed/no-signal patch under /home/liuxu/projects/mobile-moe-ako/patches/failed_attempts/ before starting the next hypothesis.
8. Revert only your own failed edits before the next iteration.

Instrumentation:
One instrumentation-only iteration is allowed if the existing counters are insufficient to resolve the expert knowledge gap. Instrumentation must be lightweight, must not change benchmark semantics, and must be archived or committed only with a clear reason.

Failure handling:
Archive and diagnose:
- compile failure
- deploy verification failure
- correctness failure
- generated-token mismatch
- decode_tok_s regression
- no metric movement
- latency shifting among page_touch/enqueue/finish without net improvement
- hypothesis/metric mismatch
- forbidden-surface edit

Best patch selection:
After the S5 smoke iterations, select the best correctness-passing patch based on:
- decode_tok_s improvement over S5 baseline
- no unacceptable mib_per_token regression
- reduced total required-miss service latency
- diagnostics consistent with the expert-informed hypothesis
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
  --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s5_codex_best_recheck_fasttemp_p32_d32

Do not run the evening verdict benchmark unless explicitly asked.

Reporting:
At the end, summarize:
- S5 baseline metrics
- the expert knowledge gap and the source used to close it
- each iteration hypothesis and local edit region
- changed files
- build/deploy verification
- each iteration metrics
- failed patches and why they failed
- best patch or no-useful-patch conclusion
- whether expert-knowledge-first guidance improved optimization compared with S4
- what remaining expert knowledge or instrumentation would be needed
