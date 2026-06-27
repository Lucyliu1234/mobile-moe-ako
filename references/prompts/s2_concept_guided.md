# S2 Concept-Guided Prompt

Use the S1 instructions plus these system concepts:

- dynamic expert/core serving
- expert/core residency
- eviction churn
- prewarm and prefetch hit rate
- required miss service latency
- GPU expert path as optional comparison

If more domain context is needed, read `references/expert_hints/coremoe_required_core.md`.

Prefer hypotheses that explain which diagnostic should move, for example:

- reduce required misses by improving residency
- reduce miss wait by interleaving miss service
- reduce upload bytes by avoiding wasteful prewarm
- improve prewarm hit rate without increasing eviction churn

Keep each round to one coherent mechanism. Do not combine multiple concept changes in one iteration.
