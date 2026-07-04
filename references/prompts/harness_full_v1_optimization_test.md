# Harness Full V1 Optimization Test Prompt

This prompt is for formally testing the current MobileMoE-AKO harness as an
optimization environment. It is not a legacy `bounded_task.json` or
`localize_boundary.py` prompt.

## English Prompt

```text
Use $mobile-moe-ako.

Run a complete MobileMoE harness optimization test, not a no-op smoke test.

Harness repo:
`/home/liuxu/projects/mobile-moe-ako`

Runtime repo:
`/home/liuxu/projects/mllm`

Experiment label:
`harness_full_v1_optimization_test`

Use the current profiler-first harness flow from the skill:
baseline benchmark -> trace extraction -> detail_profile.json ->
mobile_profile.json -> boundary_form.md -> agent-filled boundary/hypothesis ->
one coherent runtime optimization patch per iteration -> candidate benchmark ->
acceptance gate -> commit or archive.

Important constraints:
- Preserve `ITERATIONS.md` under `iterations/backups/` before running.
- Use event trace in the baseline and candidate runs when the runtime binary
  supports it.
- The harness should provide profiling facts and an empty boundary form, not
  fixed bottleneck categories or suggested causes.
- The agent must infer the boundary from profile facts and code inspection, then
  fill the boundary/hypothesis before patching.
- Do not edit benchmark, parser, prompt, dataset, generated-token accounting, or
  correctness semantics.
- Make at most one coherent runtime optimization patch per iteration.
- Stop after one accepted patch or three consecutive non-accepted optimization
  attempts.
- Do not run p32/d32 unless a p16/d16 patch is accepted.
- Append all baseline, candidate, verdict, archive, and commit results to
  `ITERATIONS.md`.

At the end, report whether the harness improved controllability, not only
whether it found a speedup:
- Did the agent produce a concrete boundary before patching?
- Did profile evidence justify the patch?
- Did the candidate verdict prevent false acceptance?
- Were failures easier to explain than old free-form runs?
```

## 中文翻译

```text
使用 $mobile-moe-ako。

运行一次完整的 MobileMoE harness 优化测试，不是 no-op 冒烟测试。

Harness 仓库：
`/home/liuxu/projects/mobile-moe-ako`

Runtime 仓库：
`/home/liuxu/projects/mllm`

实验标签：
`harness_full_v1_optimization_test`

使用 skill 中当前的 profiler-first harness 流程：
baseline benchmark -> trace extraction -> detail_profile.json ->
mobile_profile.json -> boundary_form.md -> agent 填写 boundary/hypothesis ->
每轮一个 coherent runtime optimization patch -> candidate benchmark ->
acceptance gate -> commit 或 archive。

重要约束：
- 运行前把 `ITERATIONS.md` 备份到 `iterations/backups/`。
- 如果 runtime binary 支持，在 baseline 和 candidate 中都启用 event trace。
- Harness 只提供 profiling facts 和空的 boundary form，不提供固定瓶颈类别或建议病因。
- Agent 必须根据 profile facts 和代码检查自己推断 boundary，并在 patch 前填写
  boundary/hypothesis。
- 不要修改 benchmark、parser、prompt、dataset、generated-token accounting 或
  correctness semantics。
- 每个 iteration 最多只做一个 coherent runtime optimization patch。
- 找到一个 accepted patch 后停止，或者连续三个 optimization attempt 未被接受后停止。
- 除非 p16/d16 patch 被接受，否则不要跑 p32/d32。
- 把所有 baseline、candidate、verdict、archive 和 commit 结果追加到
  `ITERATIONS.md`。

最后报告 harness 是否提升了可控性，而不仅仅是是否找到 speedup：
- Agent 是否在 patch 前产生了具体 boundary？
- Profile evidence 是否支撑了这个 patch？
- Candidate verdict 是否阻止了 false acceptance？
- 相比旧 free-form run，失败是否更容易解释？
```
