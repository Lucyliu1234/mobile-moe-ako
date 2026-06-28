# Metrics Schema

The harness prints and stores one normalized metrics JSON per run.

## Primary

- `decode_tok_s`: generated decode tokens per second. Higher is better.
- `speedup_vs_baseline`: `decode_tok_s / baseline_decode_tok_s` when `AKO_BASELINE_METRICS` is provided. Higher than 1.0 is better.

## Guardrails

- `compile_success`: build and benchmark launch succeeded.
- `correct`: all benchmark rows returned success (`ret == 0`) and, when available, generated exactly `decode_tokens_requested` tokens.
- `mib_per_token`: normalized dynamic expert/core transfer MiB per generated decode token. Lower is better or no worse.

## Diagnostics

- `required_miss_count`: total required/demand miss events.
- `upload_bytes`: total uploaded expert/core bytes for the run.
- `prewarm_hit_rate`: mean prefetch already-loaded rate when available.
- `eviction_churn`: total demand evicts.
- `cache_hit_rate`: demand cache hit rate when available.
- `required_miss_wait_ms_per_token`: estimated required-miss service time per generated token.
- `decode_req_page_touch_ms`: decode-phase required payload mmap/page-touch time.
- `decode_req_mat_enqueue_ms`: decode-phase OpenCL/materializer enqueue time for required payload writes.
- `decode_req_mat_finish_ms`: decode-phase OpenCL/materializer finish wait time for required payload writes.
- `decode_req_service_ms`: decode-phase total required-miss service time.
- `decode_req_mat_writes`: decode-phase required payload write count.
- `decode_req_page_touch_mib`: decode-phase payload MiB covered by page-touch accounting.
- `decode_core_upload_mib`: decode-phase core payload MiB uploaded.
- `decode_req_miss`: decode-phase required miss count.
- `decode_req_hit`: decode-phase required hit count.
- `decode_evict`: decode-phase eviction count.
- `energy_j_per_token_decode`: optional energy per generated token.
- `peak_temp_skin_c_decode`: optional thermal diagnostic.

## Baseline Diagnostic Decomposition

Before the first source edit in a stage, decompose the baseline with the fields that are available:

Stage boundary:

- S1 uses these fields only as raw benchmark feedback. Do not turn this list into supplied MoE optimization directions for S1.
- S2-S4 may interpret these fields with stage-provided expert categories.

- throughput: `decode_tok_s`, `decode_s`, generated token count
- transfer: `mib_per_token`, `upload_bytes`, uploaded MiB/token
- demand misses: `required_miss_count`, `cache_hit_rate`, required hit/miss counts
- miss service: `required_miss_wait_ms_per_token`, materialization/upload/page-touch timing when exposed
- required-miss service decomposition: `decode_req_page_touch_ms`, `decode_req_mat_enqueue_ms`, `decode_req_mat_finish_ms`, `decode_req_service_ms`, `decode_req_mat_writes`
- churn: `eviction_churn`, demand evicts, hot evicts, arena/window evicts when exposed
- prefetch usefulness: `prewarm_hit_rate`, pre-hit/pre-miss, submit/complete/skip counters when exposed
- other runtime costs: lm_head, shared expert, QNN/GPU timing when exposed
- thermal comparability: `peak_temp_skin_c_decode`, start/end skin or battery temperature when exposed

Missing fields are instrumentation gaps, not zeros. Record missing diagnostics instead of inventing a bottleneck.

## Definitions

- `baseline_decode_tok_s`: loaded from the JSON file named by `AKO_BASELINE_METRICS`, if provided.
- `speedup_vs_baseline`: only emitted when the baseline metrics JSON contains a positive `decode_tok_s`.
- `upload_bytes`: total dynamic expert/core payload uploaded during the measured run.
- `mib_per_token`: dynamic payload normalized by generated decode tokens. The parser accepts `uploaded_expert_mib_per_token_metric`, `uploaded_expert_mib_per_token_est`, or derives it from available upload MiB counters.
- `prewarm_hit_rate`: default parser maps this from `prefetch_already_loaded_rate`, not from demand cache hit rate.

If a metric is unavailable, keep it as `null`; do not fabricate it.

## Diagnostic Iterations

Some iterations are diagnostic-only rather than optimization attempts. Use them when existing counters cannot distinguish competing hypotheses, such as latency moving between page-touch, enqueue, finish, and total service.

Diagnostic-only results are not eligible as best patches. They should preserve benchmark semantics and expose enough counters to form the next optimization hypothesis.
