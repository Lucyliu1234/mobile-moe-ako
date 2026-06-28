# Diagnostic Instrumentation

Use diagnostic instrumentation inside the same AKO loop when existing counters cannot distinguish competing systems hypotheses.

Diagnostic iterations are for observation, not speedup. They may add lightweight counters or expose existing benchmark fields, but they must not change benchmark semantics, model work, prompt set, generated-token accounting, correctness checks, or metric parser meaning.

## When To Use

- Three consecutive optimization attempts show no signal or hypothesis mismatch.
- A subcounter improves while total service or `decode_tok_s` does not improve.
- Latency appears to move between page-touch, enqueue, finish, and total service.
- The agent cannot tell whether the bottleneck is runtime policy, page faults, OpenCL queue behavior, transfer volume, or thermal noise.

## Required-Miss Service Counters

For GPU-v3 required payload service, prefer counters that separate:

- page-touch time
- OpenCL/materializer enqueue time
- OpenCL/materializer finish wait time
- total required-miss service time
- write count
- payload MiB touched or uploaded
- decode-phase required hits, misses, and evictions

If these counters already exist in `summary.jsonl`, expose them through `scripts/parse_metrics.py` and `scripts/append_iteration.py` before adding runtime instrumentation.

## Missing-Counter Examples

Add runtime instrumentation only when existing counters are insufficient. Useful missing counters may include:

- `madvise_us`
- CPU touch-loop time
- touched page count
- minor/major page faults when safely available
- per-layer required-miss service
- per-projection gate/up/down required-miss service
- per-write enqueue latency distribution

## Success Criteria

A diagnostic iteration succeeds if it makes the next hypothesis more causal and falsifiable. It is not eligible as the best optimization patch unless the user explicitly changes the stage contract.

