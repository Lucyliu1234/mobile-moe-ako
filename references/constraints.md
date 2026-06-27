# Constraints

## Allowed

- Runtime policy edits related to caching behavior, transfer scheduling, heterogeneous execution, and runtime coordination.
- Additional diagnostics that do not change benchmark semantics.
- Small build/deploy wrapper changes needed to run the same benchmark contract.
- Stage-specific commits on `exp/s*` branches.

## Forbidden Unless Explicitly Approved

- Editing benchmark prompts, dataset, decode length, correctness logic, metric parser semantics, or generated-token accounting.
- Changing the model, tokenizer, quantization artifact, or prompt set inside a stage.
- Removing required work, hiding data movement, short-circuiting model execution, or weakening correctness.
- Committing failed/correctness-breaking patches as if they were useful results.

## Failure Handling

For correctness failures or no-signal changes:

1. Save `git diff` under `patches/failed_attempts/<iteration>.patch`.
2. Append `ITERATIONS.md` with the failure and diagnosis.
3. Revert only the agent's own failed edits, preserving unrelated user changes.

Do not erase failed attempts from the log; they are part of the research data.
