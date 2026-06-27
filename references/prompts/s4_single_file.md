# S4 Single-File Prompt

Use this only after S1-S3 fail to produce useful signal or when a human expert identifies the core policy file.

The agent should perform local variant search inside the specified file or algorithm:

- keep each variant small and reversible
- change one local policy detail per variant
- run the fixed benchmark after each variant
- compare against baseline and best previous variant
- archive failed variants as patches

This stage measures whether an agent can optimize when expert code localization is already solved.
