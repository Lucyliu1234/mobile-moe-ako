# S6 Residency Case

This case is the compact reference archive for the S6-family MobileMoE-AKO
experiments. It exists so future agents can read a small, structured memory
instead of mining the full `ITERATIONS.md` log.

## Core Question

How can the harness distinguish a real reduction in physical runtime work from
changes that only improve logical counters, shift latency between subcounters,
or modify an inactive control surface?

## Useful Result

The original S6 success identified a runtime cache-state relation bug: one
physical packed expert payload upload can cover multiple logical projection
requests, but the runtime state may record only the projection that triggered the
miss. Later sibling accesses can then look like logical misses even though the
physical payload relation says more work may already have been covered.

The exact lesson for the harness is broader than this one bug:

```text
logical request improvement is not enough;
the patch must prove movement in the physical action it claims to control.
```

## Reference Files

- `baseline.json`: representative S6 baseline metrics.
- `state_relation.md`: logical-request vs physical-action relation to inspect.
- `failed_patterns.md`: known false-positive classes.
- `traps.md`: audit traps for future prompts/runs.
- `true_patch.md`: summary of the original useful patch mechanism.

## How Future Runs Should Use This Case

Before a transfer/residency patch, require:

1. A bounded task from `harness/localize_boundary.py`.
2. A state-relation statement naming logical request, physical action, coverage,
   lifetime, invalidation, phase, and reuse/skip decision.
3. A classifier verdict from `harness/classify_result.py`.

Reject patches that improve hit/miss counters but leave physical bytes, write
count, and total service unchanged.
