# State Relation

Use this as the state-relation schema for S6-like transfer/residency work.

```text
logical_request_identity:
  A runtime request for a layer/expert/projection or equivalent logical resource.

physical_action_identity:
  The actual payload materialization, mmap page touch, OpenCL/device upload,
  physical slot write, or other operation that consumes time/bytes.

coverage_relation:
  One physical action may satisfy more than one later logical request. In the S6
  case, a packed expert payload upload can cover sibling projection accesses.

effect_lifetime:
  The physical effect is reusable until its physical slot/resource is evicted,
  invalidated, overwritten, or crosses a phase/path boundary that makes the
  effect unavailable.

reuse_skip_decision:
  A later logical request should skip physical work only if the runtime read site
  observes state proving the previous physical effect still covers it.

invalidation_reason:
  Capacity eviction, slot overwrite, phase reset, divergent state tables,
  physical key mismatch, or genuine absence of the physical resource.

execution_phase:
  Prefill vs decode, required path vs speculative/prewarm path, synchronous vs
  async queue, and active materialization path.
```

Patch gate:

```text
Which state read happens before physical materialization/upload?
Which state write records the physical effect after upload?
Which later logical request should hit because of that write?
Which physical metric should decrease if the relation is real?
What metric pattern proves this was only logical accounting?
```
