Use $mobile-moe-ako.

You are running:
S6-Skill-Control-Loop MobileMoE-AKO.

This run tests the updated skill-level diagnosis-aware control loop.
The purpose is not to add more task-specific answer knowledge. The purpose is to evaluate whether the reusable skill workflow itself makes the agentic optimization loop more controllable.

Target runtime repo:
/home/liuxu/projects/mllm

Harness package:
/home/liuxu/projects/mobile-moe-ako

Branch:
exp/s6-skill-control-loop

Base:
Use da9fa3534a16c0f34adb6709e2ba871741cbf8cc as the clean pre-success base.
Do not start from prior best, prior followup, or any commit that already contains a known prior fix.

Iteration log isolation:
Before running the baseline or editing source code, preserve the existing MobileMoE-AKO iteration log by copying:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS.md

to a uniquely named backup file, for example:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS_BEFORE_s6_skill_control_loop_<timestamp>.md

Then continue appending this experiment's entries to /home/liuxu/projects/mobile-moe-ako/ITERATIONS.md.
Do not delete or overwrite old iteration logs.

Research question:
Does moving the diagnosis-aware control loop into the reusable skill reduce false positives and make the run easier to audit, compared with relying on a long per-experiment prompt?

Goal:
Improve decode_tok_s on the fixed benchmark while preserving correctness and not worsening normalized transfer volume.

Secondary controllability goal:
Evaluate whether the skill-level control loop produces:

- a concrete bottleneck localization report before source edits
- explicit control-surface selection before every patch
- patch hypotheses tied to code paths and diagnostics
- result classification after every benchmark
- fewer accepted false positives
- clearer stop/continue decisions

Required workflow:
Follow /home/liuxu/projects/mobile-moe-ako/SKILL.md exactly, especially the Diagnosis-Aware Control Loop section.

Before the first source edit, you must produce and log a bottleneck localization report with:

- observed bottleneck pattern
- evidence from baseline metrics
- candidate control surfaces
- code search targets
- avoid-first directions
- observation gaps

Before every source edit, answer the skill's patch hypothesis gate.

After every benchmark, classify the result using the skill's result classes:

- true_system_win
- transfer_win
- scheduling_win
- logical_counter_only
- latency_shift
- noise_or_no_signal
- regression
- invalid

Do not accept a patch if the classification and diagnostics contradict the hypothesis.

Allowed context:
Use only general MobileMoE runtime concepts and the skill-level workflow:

- runtime policy
- caching behavior
- transfer volume
- required miss/service diagnostics
- scheduling/prewarm behavior
- heterogeneous execution
- thermal/noise guardrails
- correctness and metric guardrails

Do not use answer-level prior mechanisms:
Do not use these as initial hypotheses, terms, or solution descriptions before independently deriving them from this experiment's own code inspection and diagnostics:

- sibling residency
- packed payload sibling marking
- projection sibling bookkeeping
- marking gate/up/down projections resident together
- the concrete claim that one packed payload upload already contains a particular set of projection payloads
- any prior successful S6 patch description
- any prior S6 final report, prior S6 commit diff, or prior conversation content about the successful mechanism

Do not read or reuse as direct patch guidance:

- branch exp/s6-integrated-diagnostic-codex-mobile-moe-ako
- commit 902e8d9c
- branch exp/s6-followup-codex-mobile-moe-ako
- commit 2a23c3f0
- branch exp/s6-integrated-diagnostic-rerun-verify
- branch exp/s6-integrated-diagnostic-rerun-verify2
- commit 382f732d
- branch exp/s6-detailed-expert-mechanism
- commit 1f9a9be6
- references/prompts/s6_diagnostic_driven.md
- references/prompts/s6_diagnostic_driven_verify.md
- references/prompts/s6_diagnostic_driven_verify2.md
- references/prompts/s6_detailed_expert_mechanism.md
- references/prompts/s6_causal_control_surface_gate.md
- references/prompts/s6_ablation_*.md
- iterations/s6_*
- results/runs/s6_*
- patches/failed_attempts/s6_*
- previous S6 summaries or reports

If broad git status or directory listings reveal those names, ignore them and do not open their contents.

You may read:

- /home/liuxu/projects/mobile-moe-ako/SKILL.md
- references/constraints.md
- references/benchmark_instructions.md
- references/metrics_schema.md
- this prompt file
- the target runtime repo /home/liuxu/projects/mllm

Do not read:

- references/expert_hints/coremoe_required_core.md
- references/expert_hints/diagnostic_instrumentation.md
- references/experiment_protocol.md unless needed only for log-format conventions

Baseline provenance rule:
Before running the baseline benchmark, do not reuse any existing phone-side runner.
The baseline is valid only if it is built and deployed from da9fa3534a16c0f34adb6709e2ba871741cbf8cc in this experiment.

Before the baseline run, you must:

1. Confirm the runtime repo is on branch exp/s6-skill-control-loop.
2. Confirm the base is da9fa3534a16c0f34adb6709e2ba871741cbf8cc.
3. Build the Android runner from that exact source.
4. Record the host-side runner md5sum.
5. Push the runner to the phone-side benchmark directory used by the Tucker runner.
6. Record the phone-side runner md5sum and stat.
7. Confirm the host and phone md5 values match.
8. Only then run s6_skill_loop_baseline_fasttemp_p16_d16.

The baseline is invalid if it only cites a git commit or branch without rebuilding, redeploying, and verifying the phone-side runner.
Every optimization iteration must repeat build, deploy, host md5, phone md5, and phone stat verification before benchmarking.

Benchmark contract:
Use the Tucker Qwen2 TD end-to-end runner as the fixed benchmark harness.
Baseline and optimized versions must use the same host-side runner path and the same thermal gate.
Do not use a non-temperature-controlled benchmark for performance comparison.
Do not modify the Tucker runner, dataset, prompts, correctness checks, generated-token accounting, metric parser semantics, model artifacts, or benchmark contract.

p16/d16 temperature-gated smoke contract:

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

- s6_skill_loop_baseline_fasttemp_p16_d16
- s6_skill_loop_diag_01_fasttemp_p16_d16
- s6_skill_loop_iter_01_fasttemp_p16_d16
- s6_skill_loop_iter_02_fasttemp_p16_d16
- s6_skill_loop_iter_03_fasttemp_p16_d16
- s6_skill_loop_iter_04_fasttemp_p16_d16
- s6_skill_loop_iter_05_fasttemp_p16_d16

Only replace <iteration_id> with the current ID.
Do not change the runner, serial, temperature gate, context length, gpu cache capacity, dataset, decode tokens, repeats, or correctness behavior within this p16/d16 contract.

Expected build command:

cmake --build /home/liuxu/projects/mllm/build-android-arm64-v8a-qnn --target mllm-qwen2-moe-td-qnn-aot-runner

Expected deploy path:

/data/local/tmp/qwen2_moe_td_w8a16_clean_20260527/mllm-qwen2-moe-td-qnn-aot-runner

Iteration budget:

- Run at most 1 p16/d16 baseline.
- Run at most 1 diagnostic-only iteration before the first optimization attempt, only if the bottleneck localization report identifies an observation gap that blocks a causal patch hypothesis.
- Run up to 5 p16/d16 optimization iterations.
- Stop early after 3 consecutive compile failures, correctness failures, no-signal regressions, hypothesis-mismatch iterations, or repeated blockers.
- Run at most 1 p32/d32 recheck for the best correctness-passing patch.
- Do not run the 4mix p32/d64 evening verdict benchmark unless explicitly asked.

Best patch selection:
After smoke iterations, select the best correctness-passing patch only if:

- decode_tok_s improves over this experiment's baseline beyond expected noise, or a diagnostic-specific goal is clearly met
- correctness passes
- MiB/token does not regress
- result classification is compatible with accepting the patch
- diagnostics support the stated causal hypothesis
- build/deploy was verified
- the change is small and interpretable

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
  --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_skill_loop_best_recheck_fasttemp_p32_d32

Do not run the evening verdict benchmark unless explicitly asked.

Reporting:
At the end, summarize both optimization result and workflow-control result:

- baseline provenance and md5/stat verification
- baseline metrics
- bottleneck localization report
- each iteration's selected control surface and patch hypothesis gate answers
- each iteration's changed files and build/deploy verification
- each iteration's metrics and result classification
- failed patches and why they failed
- whether the skill-level control loop reduced false positives
- whether it improved localization and auditability
- best optimization patch or no-useful-patch conclusion
- what this suggests about putting workflow discipline in SKILL.md versus in per-experiment prompts
