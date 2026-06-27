# System Overview

MobileMoE-AKO evaluates whether a coding agent can participate in whole-system systems research optimization for mobile MoE inference.

## Positioning

AKO4ALL is a single-kernel optimization loop. MobileMoE-AKO adapts the loop discipline to a mobile runtime, Android device deployment, and structured system metrics.

Project title:

```text
MobileMoE-AKO: Evaluating Agentic Coding for Whole-System Mobile MoE Inference Optimization
```

Base target:

```text
Whole-system mobile MoE runtime policy
```

The base skill intentionally avoids stage-specific expert mechanisms. Progressive stages may add domain context through prompt files or expert hints.

## Research Questions

- RQ1: Can an agent autonomously explore a mobile MoE inference system in a low-context/black-box setting?
- RQ2: Can an agent map high-level mobile MoE concepts to concrete code?
- RQ3: Does optimization quality improve as context grows from repo-level to concept-guided to file-guided?
- RQ4: Where does the agent fail in whole-system systems research, and what expert knowledge is needed?

## Optional Progressive Context Protocol

The progressive context protocol is a project-specific research design, not part of vanilla AKO4ALL and not required for every MobileMoE-AKO run. See `experiment_protocol.md` when running that evaluation.

## Expected Deliverables

- MobileMoE-AKO skill/context package
- `scripts/agent_bench.sh` harness
- `ITERATIONS.md`
- metrics JSONL files
- stage branches and useful commits
- failed patch archive
- final AI-generated detailed report and short human-written summary
