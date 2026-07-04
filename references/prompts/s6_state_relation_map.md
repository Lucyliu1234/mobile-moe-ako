Use $mobile-moe-ako.

You are running:
S6-State-Relation-Map MobileMoE-AKO.

This run tests whether explicit state-relation mapping improves discovery beyond a code-backed control-surface map.
The purpose is not to add answer-level expert knowledge. The purpose is to force the agent to reason about relationships among logical runtime state, physical resources, upload/materialization actions, and later accesses before patching.

Target runtime repo:
/home/liuxu/projects/mllm

Harness package:
/home/liuxu/projects/mobile-moe-ako

Branch:
exp/s6-state-relation-map

Base:
Use da9fa3534a16c0f34adb6709e2ba871741cbf8cc as the clean pre-success base.
Do not start from prior best, prior followup, or any commit that already contains a known prior fix.

Iteration log isolation:
Before running the baseline or editing source code, preserve the existing MobileMoE-AKO iteration log by copying:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS.md

to a uniquely named backup file, for example:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS_BEFORE_s6_state_relation_map_<timestamp>.md

Then continue appending this experiment's entries to /home/liuxu/projects/mobile-moe-ako/ITERATIONS.md.
Do not delete or overwrite old iteration logs.

Research question:
Does requiring a state-relation map before patching help the agent move beyond broad control-surface selection and reason about whether a patch can reduce real physical work?

Goal:
Improve decode_tok_s on the fixed benchmark while preserving correctness and not worsening normalized transfer volume.

Secondary controllability goal:
Evaluate whether the state-relation map improves:

- distinguishing logical cache/accounting state from physical resources
- identifying which runtime state is consulted before materialization/upload
- identifying which state is updated after materialization/upload
- identifying whether later accesses can reuse a physical resource
- rejecting patches that improve counters without changing physical work

Required workflow:
Follow /home/liuxu/projects/mobile-moe-ako/SKILL.md exactly, especially the Diagnosis-Aware Control Loop section.

Additional state-relation-map requirement:
After the baseline and before the first source edit, inspect the runtime code and write a state-relation map.
Do not edit source code until this map is written and appended or summarized in /home/liuxu/projects/mobile-moe-ako/ITERATIONS.md.

The map must include at least these columns:

| logical state | lookup/read site | update/write site | physical resource/action | later access that would reuse it | expected metrics if relation is repaired | false-positive risk |

Use actual code symbols, function names, state variables, or call paths from the runtime repo.
Do not write only broad categories such as "cache" or "transfer".

At minimum, inspect and map relevant relations among:

- logical cache entries or residency state
- cache keys, expert ids, projection/category names, slot ids, resource keys, or equivalent runtime identifiers
- physical buffers, arenas, slots, payloads, upload spans, or materialized resources
- materialization and upload actions
- eviction or resource lifetime actions
- later accesses that query the logical state before deciding hit versus miss
- stats/logging updates that could move counters without changing physical work

State-relation questions:
Before any optimization patch, answer these questions from code inspection:

1. What logical runtime state is read before deciding hit versus miss, reuse versus materialize, or required versus speculative work?
2. What physical resource or action does that logical state represent?
3. Is the mapping one-to-one, many-to-one, or unclear?
4. After materialization/upload, which logical states are updated?
5. Which later accesses read those logical states?
6. If a physical resource can be reused, what state must be updated for a later access to observe that reuse?
7. If counters improve, what non-counter metric should prove that physical work was actually reduced?
8. If this relation cannot be established from code and current diagnostics, what minimal diagnostic would establish it?

Patch selection rule:
Before each source edit, select exactly one state relation from the map.
The patch hypothesis gate must reference:

- selected state relation
- logical read site
- logical write/update site
- physical resource/action
- later access expected to change behavior
- active benchmark path evidence
- expected primary metric movement
- expected diagnostic movement
- rejection condition

Do not patch a relation that is not in the map unless you first update the map and explain why the new relation is relevant.

Acceptance rules by state relation:

- Logical-cache to physical-resource relation:
  Accept only if physical-transfer, service, or primary metrics support that real runtime work changed. Hit/miss counter movement alone is insufficient.

- Materialization/update relation:
  Accept only if the patch changes which later accesses avoid materialization/upload, or total service/physical transfer improves.

- Scheduling relation:
  Accept as a scheduling win only if service or scheduling diagnostics and primary metric improve consistently. Do not describe it as a transfer win unless transfer diagnostics improve.

- Stats/logging relation:
  Do not accept as an optimization unless it also changes real runtime work and is supported by non-counter diagnostics.

- Benchmark/parser/correctness relation:
  Treat edits here as forbidden unless the user explicitly changes the experiment contract.

Allowed context:
Use only general MobileMoE runtime concepts and the skill-level workflow:

- runtime policy
- caching behavior
- logical runtime state
- physical resource or upload action
- transfer volume
- required miss/service diagnostics
- scheduling/prewarm behavior
- heterogeneous execution
- thermal/noise guardrails
- correctness and metric guardrails
- code-backed state-relation mapping

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
- references/prompts/s6_skill_control_loop.md
- references/prompts/s6_control_surface_map.md
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

1. Confirm the runtime repo is on branch exp/s6-state-relation-map.
2. Confirm the base is da9fa3534a16c0f34adb6709e2ba871741cbf8cc.
3. Build the Android runner from that exact source.
4. Record the host-side runner md5sum.
5. Push the runner to the phone-side benchmark directory used by the Tucker runner.
6. Record the phone-side runner md5sum and stat.
7. Confirm the host and phone md5 values match.
8. Only then run s6_state_relation_map_baseline_fasttemp_p16_d16.

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

- s6_state_relation_map_baseline_fasttemp_p16_d16
- s6_state_relation_map_diag_01_fasttemp_p16_d16
- s6_state_relation_map_iter_01_fasttemp_p16_d16
- s6_state_relation_map_iter_02_fasttemp_p16_d16
- s6_state_relation_map_iter_03_fasttemp_p16_d16
- s6_state_relation_map_iter_04_fasttemp_p16_d16
- s6_state_relation_map_iter_05_fasttemp_p16_d16

Only replace <iteration_id> with the current ID.
Do not change the runner, serial, temperature gate, context length, gpu cache capacity, dataset, decode tokens, repeats, or correctness behavior within this p16/d16 contract.

Expected build command:

cmake --build /home/liuxu/projects/mllm/build-android-arm64-v8a-qnn --target mllm-qwen2-moe-td-qnn-aot-runner

Expected deploy path:

/data/local/tmp/qwen2_moe_td_w8a16_clean_20260527/mllm-qwen2-moe-td-qnn-aot-runner

Iteration budget:

- Run at most 1 p16/d16 baseline.
- Run at most 1 diagnostic-only iteration before the first optimization attempt, only if the state-relation map identifies an observation gap that blocks a causal patch hypothesis.
- Run up to 5 p16/d16 optimization iterations.
- Stop early after 3 consecutive compile failures, correctness failures, no-signal regressions, hypothesis-mismatch iterations, repeated blockers, or rejected false positives.
- Run at most 1 p32/d32 recheck for the best correctness-passing patch.
- Do not run the 4mix p32/d64 evening verdict benchmark unless explicitly asked.

Best patch selection:
After smoke iterations, select the best correctness-passing patch only if:

- decode_tok_s improves over this experiment's baseline beyond expected noise, or a diagnostic-specific goal is clearly met
- correctness passes
- MiB/token does not regress
- result classification is compatible with accepting the patch
- diagnostics support the selected state relation and causal hypothesis
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
  --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_state_relation_map_best_recheck_fasttemp_p32_d32

Do not run the evening verdict benchmark unless explicitly asked.

Reporting:
At the end, summarize both optimization result and relation-localization result:

- baseline provenance and md5/stat verification
- baseline metrics
- code-backed state-relation map
- selected state relation for each iteration
- each iteration's patch hypothesis gate answers
- each iteration's changed files and build/deploy verification
- each iteration's metrics and result classification
- failed patches and why they failed
- whether the state-relation map reduced wrong-path localization
- whether it improved physical-vs-logical reasoning
- whether it exposed missing diagnostics or missing mechanism knowledge
- best optimization patch or no-useful-patch conclusion
- what this suggests about state-relation localization as a harness discipline
