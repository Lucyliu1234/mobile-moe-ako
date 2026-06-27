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
- `energy_j_per_token_decode`: optional energy per generated token.
- `peak_temp_skin_c_decode`: optional thermal diagnostic.

## Definitions

- `baseline_decode_tok_s`: loaded from the JSON file named by `AKO_BASELINE_METRICS`, if provided.
- `speedup_vs_baseline`: only emitted when the baseline metrics JSON contains a positive `decode_tok_s`.
- `upload_bytes`: total dynamic expert/core payload uploaded during the measured run.
- `mib_per_token`: dynamic payload normalized by generated decode tokens. The parser accepts `uploaded_expert_mib_per_token_metric`, `uploaded_expert_mib_per_token_est`, or derives it from available upload MiB counters.
- `prewarm_hit_rate`: default parser maps this from `prefetch_already_loaded_rate`, not from demand cache hit rate.

If a metric is unavailable, keep it as `null`; do not fabricate it.
