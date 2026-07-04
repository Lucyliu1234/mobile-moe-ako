Use $mobile-moe-ako. You are running S6-State-Level-Residency-Profiling:
MobileMoE-AKO with diagnostic instrumentation for runtime cache residency and
physical payload movement.

Experiment question:
Can state-level residency profiling make the S6 optimization loop more
controllable by showing which logical cache entries, materialization requests,
and physical payload uploads form the bottleneck chain?

Runtime repo:
/home/liuxu/projects/mllm

Harness package:
/home/liuxu/projects/mobile-moe-ako

Branch:
exp/s6-state-level-residency-profiling

Base:
Use the clean pre-success S6 base commit:
da9fa3534a16c0f34adb6709e2ba871741cbf8cc

Iteration log isolation:
Before running the profiled baseline or editing optimization code, preserve the
existing MobileMoE-AKO iteration log by copying:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS.md

to:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS_BEFORE_s6_state_level_residency_profiling_<timestamp>.md

Then append this experiment's entries to:

/home/liuxu/projects/mobile-moe-ako/ITERATIONS.md

Do not delete or overwrite the old iteration log.

Diagnostic instrumentation:
This experiment uses a diagnostic-only runtime patch that exposes state-level
residency counters. The instrumentation patch is not an optimization attempt
and must not count as iteration 01.

The profiled baseline must run with:

MLLM_QNN_TD_RESIDENCY_TRACE=1

Expected new normalized metrics include:

- res_probe
- res_hit
- res_miss
- res_mat_req
- res_upload
- res_dup_upload
- res_record
- res_evict
- res_base_record
- res_sibling_missing
- res_later_sibling_miss
- res_later_sibling_hit

Fixed benchmark contract:
- dataset: /home/liuxu/projects/mobile-moe-ako/references/datasets/ds2_cold20_prompts_quick_1_p16.jsonl
- decode tokens: 16
- repeats: 1
- context length: 384
- gpu cache capacity: 8
- correctness: ret=0 and generated=16
- thermal guard: use the same fast-temp daytime contract as prior S6 runs

Baseline command shape:

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
  --out-dir /home/liuxu/projects/mobile-moe-ako/results/runs/s6_state_level_residency_profiled_baseline_fasttemp_p16_d16

Use the normal build/deploy process before running the baseline. Verify host and
phone runner md5 match.

Allowed edit surface:
- Runtime/policy code only, primarily:
  /home/liuxu/projects/mllm/examples/qwen2_moe_td_qnn_aot/aot_run.cpp
- Harness parser/schema edits are allowed only for diagnostic fields.
- Do not edit dataset, correctness rules, model files, benchmark parser logic
  that changes semantics, or prompt/decode contract.

Workflow:

1. Confirm the runtime repo is on branch exp/s6-state-level-residency-profiling.
2. Confirm the runtime repo is based on da9fa3534a16c0f34adb6709e2ba871741cbf8cc.
3. Confirm the diagnostic instrumentation is present and controlled by
   MLLM_QNN_TD_RESIDENCY_TRACE=1.
4. Build and deploy the runner. Verify host/phone md5.
5. Run the profiled baseline with MLLM_QNN_TD_RESIDENCY_TRACE=1.
6. Append a baseline entry to ITERATIONS.md. Include normal metrics and the
   new res_* state-level metrics.
7. Before any optimization edit, write a state-chain interpretation:
   - Which logical probes miss?
   - Which misses trigger materialization?
   - Which materialization requests trigger physical uploads?
   - Are there duplicate physical payload uploads?
   - Are base packed-payload records followed by missing companion logical
     entries?
   - Do later sibling accesses hit or miss after base records?
8. Only after that interpretation, start optimization iteration 01.

Patch hypothesis gate:
Before every optimization edit, answer:

1. What exact state chain does this patch target?
2. Which runtime state or policy decision will change?
3. Where is that state read before materialization/upload is scheduled?
4. Which later access should become a hit or skip materialization?
5. Which res_* metrics should move?
6. Which physical metrics should move: mib_per_token, decode_core_upload_mib,
   decode_req_mat_writes, or decode_req_service_ms?
7. What result would prove this is only a logical-counter change?
8. If res_* counters or physical upload metrics do not support the hypothesis,
   will this patch be rejected?

Acceptance criteria:
A useful optimization patch must:

- pass correctness
- improve decode_tok_s beyond smoke noise
- preserve or reduce mib_per_token
- show consistent diagnostic movement in both state-level res_* counters and
  physical transfer/service counters

Reject patches that:

- improve hit/miss counters but leave physical upload/service unchanged
- reduce one subcounter while moving the same cost into another subcounter
- affect scheduling/prewarm without explaining the required upload state chain
- touch benchmark/correctness semantics

Best-patch recheck:
If a useful p16/d16 patch is selected, run the p32/d32 signal recheck under the
same instrumentation and correctness rules. Treat p32/d32 as signal, not final
evening verdict, unless the user explicitly asks for a verdict benchmark.

Final report:
Summarize:

- profiled baseline state chain
- whether state-level profiling revealed repeated physical upload or only
  logical counter inconsistency
- each optimization iteration and classification
- whether the selected patch is a transfer win, scheduling win,
  logical-counter-only result, latency shift, regression, or no-useful-patch
- remaining missing diagnostics or expert knowledge
