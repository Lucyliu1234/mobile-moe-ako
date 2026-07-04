# S6 Residency Traps

- A cache hit-rate improvement is not equivalent to a physical upload skip.
- An eviction counter may count logical entry churn rather than physical slot
  loss.
- A page-touch reduction can move page-fault cost into OpenCL enqueue.
- A prewarm/scheduling change can improve latency without reducing physical
  transfer.
- A diagnostic counter on the wrong helper path can produce zeros while the real
  required path remains active elsewhere.
- A small `decode_tok_s` improvement under hotter thermal conditions is not a
  verdict.
- Do not patch parser, benchmark semantics, generated-token accounting, or
  correctness checks to create a win.
