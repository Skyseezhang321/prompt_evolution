# Literature Map

Last updated: 2026-06-12

Status: Full directory of paper_notes. The main table below covers all 39 completed deep-read notes (each row links to the arXiv source and the in-repo note). A separate candidate list of registered-but-not-yet-deep-read papers is appended. New sources should first be registered and categorized per the [Source Collection Plan](source_collection_plan.md) before deciding whether to proceed to a deep-read note; for full processing status see the [Source Inventory](source_inventory.md).

Inclusion criteria: Priority is given to papers or frameworks that directly address automatic prompt optimization, prompt evolution, self-improving/self-evolving prompts, prompt-as-program, context engineering, or eval-driven prompt iteration.

Scope note: The main table is organized by "deep-read note written," including two types of special entries outside the two main threads, each annotated in the positioning column — reference baseline entries (e.g., Prompt Repetition: a zero-cost structural transform, not an APO method itself, serving as the comparison floor before any optimizer reports gains) and internal baselines (PROSE: the coin-flip authors' own reference implementation, not an independent publication).

## Quick Lineage

> For detailed per-method coverage of the seven main-thread methods (APE→ProTeGi→OPRO→DSPy→TextGrad→MIPROv2→GEPA), see [APO Seven-Method Main Thread Primer](apo_seven_methods_primer_20260611.md); all numbers are aligned with the individual deep-read notes.

1. Early automatic prompt generation: treating instructions as searchable programs.
2. Textual gradients and black-box search: generating natural-language critique from error feedback, then editing the prompt.
3. Evolutionary and self-referential optimization: co-evolving the task prompt and the mutation/optimizer prompt.
4. Programmatic prompt systems: DSPy abstracts the LM pipeline as a compilable program, optimizing prompts and demonstrations via a metric.
5. Reflective evolution: methods such as GEPA use execution trajectories for natural-language diagnosis and Pareto search.
6. Memory and self-evolution: MemAPO, SePO, and similar methods incorporate successful experiences, failure patterns, and the optimizer's own prompt into long-term improvement.
7. Context engineering: the object of study expands from the prompt string to the overall context including retrieval, memory, tools, and agent workflows.

## Current Frontier Focus

As of 2026-06-12, priority follow-up directions:

- Reflective prompt evolution: methods such as GEPA use full execution trajectories as natural-language feedback, rewriting prompts via reflection and Pareto/evolutionary search.
- Memory-based self-evolution: methods such as MemAPO distill successful strategies and failure patterns into reusable memory, with the goal of reducing the cost of starting optimization from scratch each time.
- Optimizer self-evolution: methods such as SePO begin to include the prompt agent's own system prompt as an optimization target.
- Multi-agent / system-level optimization: directions such as MASPO and AutoPDL extend the optimization target from a single prompt to agent configurations or multi-agent prompts.
- Modular prompt optimization: decomposing the prompt into locally editable, constraint-protected structures to reduce drift and unbounded-growth risk.
- Context engineering: both industry and academia are advancing the problem from "write a good prompt" toward "control what context the model sees at each step."
- Confirmed coverage gaps: bi-level / thought-driven (prompt optimization in the era of o1/R1-style reasoning models) is entirely absent and is the highest-priority targeted search direction; task-agnostic/online and constrained optimization are also only indirectly addressed. Criteria and lists are in the [Taxonomy External Completeness Audit](arxiv_taxonomy_completeness_check_20260610.md).

## Full Deep-Read Note Directory (39 Papers)

All evidence grades are at the paper level (method + results deep-read, not reproduced conclusions from this project); each entry includes a local PDF/text SHA256, main result figures, ablations, failure cases, and a minimal verification plan. Batch attribution and integrated assessment are in [Batch 3 Synthesis](arxiv_deep_reading_batch3_synthesis.md); the time-slice synthesis for the 25 papers from 2025/2026 (four turns + two tensions + gap inventory) is in [arXiv 2025/2026 Frontier Deep-Read Synthesis](arxiv_2025_2026_frontier_synthesis_20260612.md).

| Year | Paper | One-line positioning | Deep-read note |
| --- | --- | --- | --- |
| 2022 | [GrIPS](https://arxiv.org/abs/2203.07281) | Historical anchor (v1 predates APE): gradient-free phrase-level edit search, no LLM generator; semantically incoherent edits still improve scores. | [paper-grips-2022](paper_notes/paper-grips-2022.md) |
| 2022 | [APE](https://arxiv.org/abs/2211.01910) | Starting point of two-stage black-box search (propose + select), establishing "instruction as searchable program"; the LLM-as-generator lineage begins here. | [paper-ape-2022](paper_notes/paper-ape-2022.md) |
| 2023 | [ProTeGi](https://arxiv.org/abs/2305.03495) | Compresses failure examples into natural-language critique, beam search + data selection; classic textual critique baseline. | [paper-protegi-2023](paper_notes/paper-protegi-2023.md) |
| 2023 | [OPRO](https://arxiv.org/abs/2309.03409) | LLM-as-optimizer: uses a "history of candidates + scores" trajectory to generate entirely new instructions. | [paper-opro-2023](paper_notes/paper-opro-2023.md) |
| 2023 | [PromptBreeder](https://arxiv.org/abs/2309.16797) | Co-evolves the task prompt and mutation prompt simultaneously; the classic starting point of self-referential optimization. | [paper-promptbreeder-2023](paper_notes/paper-promptbreeder-2023.md) |
| 2023 | [DSPy](https://arxiv.org/abs/2310.03714) | Writes the LM pipeline as a declarative program and compiles it; prompt engineering shifts toward compilable AI programs. | [paper-dspy-2023](paper_notes/paper-dspy-2023.md) |
| 2023 | [PromptAgent](https://arxiv.org/abs/2310.16427) | Models prompt optimization as MDP + MCTS planning; tree search beats beam/greedy at equal exploration budget, adding a "search structure" dimension to the lineage. | [paper-promptagent-2023](paper_notes/paper-promptagent-2023.md) |
| 2024 | [EvoPrompt](https://arxiv.org/abs/2309.08532) | Translates classical GA/DE evolutionary operators into natural-language operators executable by an LLM. | [paper-evoprompt-2024](paper_notes/paper-evoprompt-2024.md) |
| 2024 | [TextGrad](https://arxiv.org/abs/2406.07496) | Abstracts textual feedback as a "textual gradient" that can be back-propagated through a computation graph, generalizing to arbitrary text variables. | [paper-textgrad-2024](paper_notes/paper-textgrad-2024.md) |
| 2024 | [MIPROv2](https://arxiv.org/abs/2406.11695) | Joint instruction + demonstration optimization and credit assignment for multi-stage LM programs. | [paper-miprov2-2024](paper_notes/paper-miprov2-2024.md) |
| 2024 | [CriSPO](https://arxiv.org/abs/2410.02748) | Multi-dimensional critique-suggestion feedback for generation tasks, replacing a single aggregate score. | [paper-crispo-2024](paper_notes/paper-crispo-2024.md) |
| 2024 | [ERM](https://arxiv.org/abs/2411.07446) | Historical feedback and error examples are filtered, retrieved, and selectively forgotten before being used for reflection. | [paper-erm-memory-2024](paper_notes/paper-erm-memory-2024.md) |
| 2024 | [Are LLMs Good Prompt Optimizers?](https://arxiv.org/abs/2402.02101) | Counter-example: LLM reflection does not necessarily identify the true error causes for the target model. | [paper-llm-prompt-optimizers-2024](paper_notes/paper-llm-prompt-optimizers-2024.md) |
| 2024 | [Teach Better or Show Smarter?](https://arxiv.org/abs/2406.15708) | When a labeled dev set is available, exemplar selection often matters more than instruction rewriting. | [paper-teach-better-show-smarter-2024](paper_notes/paper-teach-better-show-smarter-2024.md) |
| 2025 | [APO Survey](https://arxiv.org/abs/2502.16923) | Systematic survey organized around the optimization process anatomy (5 stages); external reference taxonomy for this project. | [paper-apo-survey-2025](paper_notes/paper-apo-survey-2025.md) |
| 2025 | [APE Survey](https://arxiv.org/abs/2502.11560) | Unified optimization-perspective framework (variable × objective × method), naming underexplored frontiers. | [paper-ape-survey-2025](paper_notes/paper-ape-survey-2025.md) |
| 2025 | [Context Engineering Survey](https://arxiv.org/abs/2507.13334) | Positions context engineering as a superset of prompt engineering; confirms the scope boundary of this project. | [paper-context-engineering-2025](paper_notes/paper-context-engineering-2025.md) |
| 2025 | [Scaling Textual Gradients](https://arxiv.org/abs/2506.00400) | Full-batch textual gradients hit a context wall; TSGD-M uses high-scoring historical prompts as momentum sampling. | [paper-scaling-textual-gradients-2025](paper_notes/paper-scaling-textual-gradients-2025.md) |
| 2025 | [Textual Gradients are a Flawed Metaphor](https://arxiv.org/abs/2512.13598) | Deflates the textual gradient narrative: gains typically come from formatting, meta-instructions, and candidate discovery, not gradient-style learning. | [paper-textual-gradients-flawed-metaphor-2025](paper_notes/paper-textual-gradients-flawed-metaphor-2025.md) |
| 2025 | [APO for KG Construction](https://arxiv.org/abs/2506.19773) | APO as a "robustness tool under complexity amplification": the more complex the schema and the longer the input, the larger the gains. | [paper-apo-kg-construction-2025](paper_notes/paper-apo-kg-construction-2025.md) |
| 2025 | [AutoPDL](https://arxiv.org/abs/2504.04365) | Treats prompting patterns themselves (Zero-Shot/CoT/ReAct/ReWOO, etc.) as search variables. | [paper-autopdl-2025](paper_notes/paper-autopdl-2025.md) |
| 2025 | [DistillPrompt](https://arxiv.org/abs/2508.18992) | First distills task principles from examples, then compresses them into an instruction; used as a reference against direct few-shot. | [paper-distillprompt-2025](paper_notes/paper-distillprompt-2025.md) |
| 2025 | [MAPRO](https://arxiv.org/abs/2510.07475) | Formalizes multi-agent prompt optimization as MAP inference with credit propagated along the topology. | [paper-mapro-2025](paper_notes/paper-mapro-2025.md) |
| 2025 | [Prompt Repetition](https://arxiv.org/abs/2512.14982) | Reference baseline (not an APO method): repeating the prompt once, 47/70 wins significantly vs. 0 losses in non-reasoning mode; the zero-cost structural transform comparison floor. | [paper-prompt-repetition-2025](paper_notes/paper-prompt-repetition-2025.md) |
| 2026 | [GEPA](https://arxiv.org/abs/2507.19457) | Execution-trajectory reflection + Pareto candidate retention; outperforms RL with fewer rollouts; currently the strongest baseline most worth reproducing. | [paper-gepa-2026](paper_notes/paper-gepa-2026.md) |
| 2026 | [ACE](https://arxiv.org/abs/2510.04618) | Context-as-playbook incremental evolution (delta + deterministic merge) prevents context collapse and brevity bias; directly demarcates a paradigm boundary against GEPA-class candidates on agent/knowledge-intensive tasks. | [paper-ace-2026](paper_notes/paper-ace-2026.md) |
| 2026 | [SePO](https://arxiv.org/abs/2606.04465) | Includes the optimizer's own system prompt in the evolutionary loop; direct evidence for "optimizer/judge versioning." | [paper-sepo-2026](paper_notes/paper-sepo-2026.md) |
| 2026 | [SPEAR](https://arxiv.org/abs/2605.26275) | Optimizer writes Python for structured error analysis (confusion matrix/groupby); auto-rollback protects the performance floor. | [paper-spear-2026](paper_notes/paper-spear-2026.md) |
| 2026 | [Modular Prompt Optimization](https://arxiv.org/abs/2601.04055) | Fixed schema with per-section local textual gradients; the most direct rollback-friendly prompt optimization experiment design. | [paper-modular-prompt-optimization-2026](paper_notes/paper-modular-prompt-optimization-2026.md) |
| 2026 | [PrefPO](https://arxiv.org/abs/2603.19311) | Pairwise preference replaces absolute scores; incorporates prompt hygiene and prompt hacking into evaluation. | [paper-prefpo-2026](paper_notes/paper-prefpo-2026.md) |
| 2026 | [TextReg](https://arxiv.org/abs/2605.21318) | Regularization perspective on prompt overfitting: a regularization gradient is needed in addition to the task gradient. | [paper-textreg-2026](paper_notes/paper-textreg-2026.md) |
| 2026 | [Edit-Level Causal Analysis](https://arxiv.org/abs/2605.26655) | Causal analysis of edit families: complexification and meta-instructions may be harmful on math/multi-hop tasks. | [paper-causal-edit-level-2026](paper_notes/paper-causal-edit-level-2026.md) |
| 2026 | [JTPRO](https://arxiv.org/abs/2604.19821) | Optimization target for tool agents = joint context of global policy + per-tool schema + shared slot semantics. | [paper-jtpro-2026](paper_notes/paper-jtpro-2026.md) |
| 2026 | [MASPO](https://arxiv.org/abs/2605.06623) | Explicitly models the multi-agent "locally correct, globally wrong" problem; uses misalignment cases to drive joint optimization. | [paper-maspo-2026](paper_notes/paper-maspo-2026.md) |
| 2026 | [MemAPO](https://arxiv.org/abs/2603.21520) | Dual memory of successful templates and error patterns with cross-task retrieval and reuse; memory becomes an experiential asset for the optimizer. | [paper-memapo-2026](paper_notes/paper-memapo-2026.md) |
| 2026 | [Prompt Codebooks](https://arxiv.org/abs/2605.28360) | Prompt decomposed into reusable instinct codebooks, routed and assembled by input; reduces length and aids attribution. | [paper-prompt-codebooks-2026](paper_notes/paper-prompt-codebooks-2026.md) |
| 2026 | [Temporal/Structural Credit in MAS](https://arxiv.org/abs/2605.30227) | Multi-agent "who to update and at which round": only update roles or rounds with low credit. | [paper-temporal-structural-credit-mas-2026](paper_notes/paper-temporal-structural-credit-mas-2026.md) |
| 2026 | [VISTA / Reflection in the Dark](https://arxiv.org/abs/2603.18388) | Counter-example: when the root cause lies outside the hypothesis space, more reflection makes things worse; hypothesis generation and rewriting must be decoupled. | [paper-vista-reflection-dark-2026](paper_notes/paper-vista-reflection-dark-2026.md) |
| 2026 | [Prompt Optimization Is a Coin Flip](https://arxiv.org/abs/2604.14585) | Run headroom/noise-floor/coupling diagnostics before optimizing; in many compound AI settings, optimization underperforms zero-shot. | [paper-coin-flip-2026](paper_notes/paper-coin-flip-2026.md) |
| 2026 | [PROSE](https://arxiv.org/abs/2604.14585) | Internal baseline (not an independent publication): risk-aware evolutionary optimizer built by the coin-flip authors; conclusion is no measurable robustness advantage. | [paper-prose-2026](paper_notes/paper-prose-2026.md) |

## Registered Candidates Not Yet Deep-Read

Aligned with the repo↔paper cross-reference table in main report v4; the full candidate pool is in the [Source Inventory](source_inventory.md).

| Paper/Project | Registration status | Notes |
| --- | --- | --- |
| [PromptWizard](https://arxiv.org/abs/2405.18369) | skimmed (repo side) | microsoft/PromptWizard pending audit; write paper note first, then audit code. |
| [Promptomatix](https://arxiv.org/abs/2507.14241) | skimmed | Low-barrier auto-optimization framework; deep-read paper first, then audit repo. |
| [Intent-based Prompt Calibration](https://arxiv.org/abs/2402.03099) | candidate | Corresponding paper for Eladlev/AutoPrompt; note the naming distinction from LangChain Promptim. |
| [promptolution](https://aclanthology.org/2026.eacl-demo.21/) | candidate | Unified, modular, framework-agnostic prompt optimization tool (EACL demo). |

## Key Extraction Points When Reading Papers

- Optimization target: which of instruction, examples, system prompt, workflow, context, tool policy is modified.
- Search algorithm: how candidates are generated, how they are selected, whether an archive is used, whether a validation split is used.
- Feedback source: scores, human labels, LLM critique, execution trajectories, tool errors, cost.
- Anti-overfitting: how train/dev/test are split; whether cross-task or cross-model generalization is reported.
- Engineering cost: number of calls, tokens, latency, whether a strong optimizer model is required.
- Safety and governance: whether the optimizer's modifiable scope is constrained; whether rollback and human review are preserved.
- Failure cases: which tasks it fails on and why.

## Priority Reading Order

1. Surveys: `2502.16923` and `2502.11560` — establish the global taxonomy first.
2. Classic methods: APE, ProTeGi, OPRO, PromptBreeder.
3. Engineering frameworks: DSPy, MIPROv2, promptolution, Promptomatix.
4. Self-evolution focus: GEPA, MemAPO, SePO.
5. Extended perspective: context engineering survey.

## Open Questions

- Whether the gains from reflective prompt evolution come from better search or from the optimizer model's implicit task knowledge.
- Whether successful strategy libraries can truly generalize across tasks, or only transfer across closely related benchmarks.
- How to set an "immutable constitution" for prompt self-evolution while allowing local strategies to change flexibly.
- Whether LLM-as-judge scoring noise leads the optimizer to learn prompts that pander to the judge.
- How prompt versions can be tracked alongside production data distributions, model versions, and tool versions over long-running deployments.
