# Expert Hint: CoreMoE Required-Core Serving

Read this only when a staged protocol or user prompt intentionally provides expert domain context, such as S2/S3/S4. Do not read it for S1 black-box exploration.

The project-specific expert hypothesis is that mobile MoE decode performance is often dominated by the runtime policy around required-core serving and related data movement.

Relevant mechanisms include:

- required-core serving
- expert/core residency
- eviction and cache churn
- prewarm/prefetch timing and hit rate
- required-first bandwidth arbitration
- required miss service latency
- interleaved miss service
- optional OpenCL/GPU expert-path comparison

Treat these as hypotheses to test with the fixed benchmark and diagnostics, not as guaranteed bottlenecks.
