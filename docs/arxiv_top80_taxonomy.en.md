# arXiv Top80 Taxonomy Overview and Cross-Sectional Matrix

Updated: 2026-06-08

Data source: `outputs/arxiv_prompt_search/arxiv_focus_top80_20260608T131514Z.csv`

Evidence level: title + arXiv abstract + first-pass matrix via automated classification. This document is for coarse filtering and deep-read scheduling, not for final conclusions.

## Analysis Framework

All papers in this batch are analyzed along the following dimensions:

| Dimension | Focus Question |
| --- | --- |
| Optimization target | Whether the target is instruction, few-shot examples, system prompt, structured prompt section, workflow, agent role, tool policy, memory, or the optimizer itself. |
| Feedback signal | Whether the signal used is task score, natural-language critique, textual gradient, pairwise preference, human feedback, judge score, execution trajectory, tool error, failure samples, or memory. |
| Candidate generation | Whether the approach uses LLM rewrite, beam search, evolutionary operators, bandit/Bayesian, program compiler, agentic tool loop, code analysis, or synthetic data. |
| Candidate selection | Whether selection is based on dev set score, Pareto frontier, successive halving, pairwise preference, joint agent outcome, guard metric, cost-aware objective, or archive. |
| Evaluation credibility | Whether the paper reports dataset, model, baseline, train/dev/test isolation, cost, failure cases, generalization, and code. |
| Value to this project | Whether it can serve as a baseline, taxonomy source, risk evidence, engineering design reference, or minimal experiment candidate. |

## Method Cluster 1: Classic APO and Baseline Anchors

Representative papers:

- [ProTeGi](https://arxiv.org/abs/2305.03495): criticizes prompts with natural-language "gradients," then performs beam search.
- [AutoHint](https://arxiv.org/abs/2307.07415): automatic prompt optimization via hint generation.
- [EvoPrompt](https://arxiv.org/abs/2309.08532): connects LLMs with evolutionary algorithms for discrete prompt search.
- [PromptBreeder](https://arxiv.org/abs/2309.16797): co-evolves task prompts and mutation prompts.
- [Are Large Language Models Good Prompt Optimizers?](https://arxiv.org/abs/2402.02101): directly evaluates the capability boundary of LLMs as prompt optimizers.

First-pass assessment:

These papers form the historical baseline. Their value lies not merely in performance numbers but in problem formalization: prompts can be generated, evaluated, selected, and rolled back as discrete natural-language objects. Any future experiment establishing a baseline should cover at least 2–3 of the following classes: manual prompt, APE/LLM rewrite, ProTeGi-style textual feedback, and evolutionary search.

## Method Cluster 2: Textual Gradient and Reflection-Based Optimization

Representative papers:

- [Scaling Textual Gradients via Sampling-Based Momentum](https://arxiv.org/abs/2506.00400): discusses context-wall and stability issues when scaling textual gradients to larger training data.
- [CriSPO](https://arxiv.org/abs/2410.02748): guides prompt revision with multi-aspect critique-suggestion for generation tasks.
- [Modular Prompt Optimization](https://arxiv.org/abs/2601.04055): decomposes structured prompts into sections and optimizes each with local textual gradients.
- [Reflection in the Dark](https://arxiv.org/abs/2603.18388): identifies black-box trajectory and failure modes in reflective APO, and separates hypothesis generation from rewriting using a multi-agent design.
- [TextReg](https://arxiv.org/abs/2605.21318): treats prompt distributional overfitting as a regularization problem in text-space optimization.
- [Textual Gradients are a Flawed Metaphor](https://arxiv.org/abs/2512.13598): challenges the textual gradient analogy itself and warns against treating natural-language feedback as differentiable gradients.

First-pass assessment:

The true value of textual gradients may not lie in the "gradient analogy" but in converting failure samples into readable, auditable, and locally applicable revision suggestions. The direction most worth adapting into this project's experiments is: comparing scalar score, free-form critique, and section-local critique as three feedback signals on the same task, while tracking prompt growth, generalization, and failure modes.

## Method Cluster 3: Evolutionary, Self-Referential, and Memory-Based Self-Evolution

Representative papers:

- [EvoPrompt](https://arxiv.org/abs/2309.08532): population + evolutionary operators.
- [PromptBreeder](https://arxiv.org/abs/2309.16797): self-referentially optimizes the mutation prompt.
- [GEPA](https://arxiv.org/abs/2507.19457): combines trajectory reflection, Pareto frontier, and prompt evolution.
- [MemAPO](https://arxiv.org/abs/2603.21520): distills successful strategies and failure patterns into a dual memory.
- [SePO](https://arxiv.org/abs/2606.04465): includes the prompt agent's own system prompt as an optimization target.
- [Prompt Codebooks](https://arxiv.org/abs/2605.28360): organizes reusable instruction units into a codebook and routes them per instance.
- [C-MOP](https://arxiv.org/abs/2602.10874): applies momentum and clustering to prompt evolution.

First-pass assessment:

Self-evolution in this batch of papers targets three distinct objects: task prompt, optimizer prompt, and experience memory. Future documentation and experiments must record these separately; otherwise it is impossible to determine whether gains come from a better prompt, a larger search budget, or experience transfer in the optimizer itself.

## Method Cluster 4: Prompt-as-Program, Structured Prompts, and Framework-Level Tooling

Representative papers:

- [Promptomatix](https://arxiv.org/abs/2507.14241): generates prompts from task descriptions, combining a meta-prompt optimizer and DSPy compiler.
- [AutoPDL](https://arxiv.org/abs/2504.04365): encodes agentic prompting patterns and demonstration search as executable PDL programs.
- [promptolution](https://arxiv.org/abs/2512.02840): a unified, modular prompt optimization framework.
- [Is It Time To Treat Prompts As Code?](https://arxiv.org/abs/2507.03620): a multi-use-case prompt optimization case study using DSPy.
- [A Comparative Study of DSPy Teleprompter Algorithms](https://arxiv.org/abs/2412.15298): compares DSPy teleprompter algorithms with human evaluation alignment.
- [Composing Policy Gradients and Prompt Optimization for Language Model Programs](https://arxiv.org/abs/2508.04660): discusses prompt optimization within language model programs.

First-pass assessment:

This cluster of papers elevates prompts from text fragments to compilable, composable, executable, and reusable program components. For this project, the engineering value of prompt-as-program outweighs single-run score improvements because it naturally supports version tracking, local rollback, and experiment isolation.

## Method Cluster 5: Agent, System Prompt, Multi-Agent, and Tool-Chain Optimization

Representative papers:

- [SPEAR](https://arxiv.org/abs/2605.26275): an agentic optimizer that uses evaluate/python/set_prompt/finish tools and provides auto-rollback and guard metrics.
- [AutoPDL](https://arxiv.org/abs/2504.04365): searches over agentic and non-agentic prompting patterns.
- [System Prompt Optimization with Meta-Learning](https://arxiv.org/abs/2505.09666): focuses specifically on system prompt optimization.
- [MASPO](https://arxiv.org/abs/2605.06623): jointly optimizes role prompts in a multi-agent system.
- [MAPRO](https://arxiv.org/abs/2510.07475): reformulates multi-agent prompt optimization as MAP inference.
- [MASPOB](https://arxiv.org/abs/2603.02630): bandit-based multi-agent prompt optimization.
- [JTPRO](https://arxiv.org/abs/2604.19821): joint tool-prompt reflective optimization.

First-pass assessment:

In agent settings, the optimization target is no longer a "response prompt" but the credit assignment between role, tool policy, workflow, local agent output, and global success. This direction is well suited for minimal experiments in this project: choose a small tool-use task and compare manual prompts, local role-prompt rewriting, and an agentic optimizer with guard metrics.

## Method Cluster 6: Preference, Human Feedback, Judge, and Governance

Representative papers:

- [PrefPO](https://arxiv.org/abs/2603.19311): supports label-free optimization via pairwise preference and an LLM discriminator.
- [PROMST](https://arxiv.org/abs/2402.08702): combines human feedback and heuristic sampling for multi-step tasks.
- [LLM Prompt Duel Optimizer](https://arxiv.org/abs/2510.13907): uses label-free dueling / preference for prompt optimization.
- [When Prompt Optimization Becomes Jailbreaking](https://arxiv.org/abs/2603.19247): connects prompt optimization with adaptive red-teaming.
- [When Gradients Collide](https://arxiv.org/abs/2605.26046): analyzes multi-objective prompt optimization failure modes in LLM judges.
- [Exploiting LLM-as-a-Judge Disposition](https://arxiv.org/abs/2604.20726): warns that optimizers may exploit judge disposition.

First-pass assessment:

This cluster is the core evidence source for the risk section in future documentation. Whenever an optimizer targets a judge or preference signal, it is essential to guard against prompt hacking, judge gaming, overfitting to rubrics, safety boundary erosion, and prompt length inflation.

## Method Cluster 7: Application-Domain APO and Empirical Studies

Representative papers:

- [APO for Knowledge Graph Construction](https://arxiv.org/abs/2506.19773): compares DSPy, APE, and TextGrad on triple extraction.
- [AutoMedPrompt](https://arxiv.org/abs/2502.15944): medical prompt optimization.
- [Clinical QA / ArchEHR-QA series](https://arxiv.org/abs/2506.10751): agentic prompt optimization for medical evidence-grounded QA.
- [Knowledge Restoration-driven Prompt Optimization](https://arxiv.org/abs/2601.15037): targets open-domain relation triplet extraction.
- [Political Science Text Classification](https://arxiv.org/abs/2409.01466): text classification and dynamic exemplar selection.
- [APRIL](https://arxiv.org/abs/2509.25196): APO + RL in API synthesis.

First-pass assessment:

The value of application papers lies not in proposing general-purpose algorithms but in providing task boundaries, metric choices, cross-model performance, and failure cases. They are appropriate as reference scenarios for future experiments but should not take priority as core evidence in the method taxonomy.

## Cross-Sectional Evidence Matrix: Priority Deep-Read Candidates

| Paper | Optimization Target | Feedback Signal | Search / Selection | Value to This Project |
| --- | --- | --- | --- | --- |
| ProTeGi | task prompt | textual critique / task score | semantic edit + beam search | classic textual-gradient baseline |
| EvoPrompt | task prompt population | dev score | evolutionary operators | classic evolutionary baseline |
| PromptBreeder | task prompt + mutation prompt | fitness on train set | self-referential evolution | starting point for self-referential optimization |
| GEPA | prompts in AI system | trajectory reflection | Pareto / evolutionary search | current strong baseline and experiment candidate |
| SePO | task agent prompt + prompt agent system prompt | task benchmark score / self-evolution archive | open-ended evolutionary search | core evidence that the optimizer itself can be optimized |
| MemAPO | prompt + reusable memory | success strategies + failure patterns | memory retrieval/editing | mechanism for accumulating long-term experience |
| Modular Prompt Optimization | structured prompt sections | section-local textual gradients | schema-preserving local edits | reference for rollback-capable structured prompt approach |
| Scaling Textual Gradients | prompt updates | minibatch textual gradients | momentum sampling / Gumbel-Top-k | evidence for textual gradient scalability |
| Textual Gradients are a Flawed Metaphor | textual-gradient methods | behavioral experiments | critique / case study | counter-evidence and terminology risk |
| PrefPO | prompt | pairwise preference | LLM discriminator + optimizer loop | label-free optimization and prompt hacking risk |
| CriSPO | generation task prompt | multi-aspect critique-suggestion | optimizer + suffix tuning | APO for multi-metric generation tasks |
| SPEAR | prompt + optimizer workflow | eval dataframe / code analysis | agentic tool loop + rollback | reference for engineering-grade agent optimizer |
| AutoPDL | agent configuration / PDL prompt program | task score | successive halving over prompt programs | prompt-as-program baseline |
| MASPO | multi-agent role prompts | joint downstream outcome | evolutionary beam search | multi-agent credit assignment |
| TextReg | prompt edits | regularized textual gradients | OOD-aware regularized update | prompt overfitting governance |
| Why Prompt Optimization Works... | prompt edit families | cross-task observational analysis | causal-inspired analysis | explaining failure and transfer boundaries |
| Prompt Codebooks | reusable instruction units | structured critic verdict | codebook + router + generator | reusable experience units |
| Reflection in the Dark | reflective APO trajectory | labeled hypotheses / minibatch verification | multi-agent explore-exploit | interpretability of reflective optimizer |
| Prompt Optimization Is a Coin Flip | compound AI prompts | task outcomes / failure diagnosis | diagnostic analysis | when not to auto-optimize |
| When Prompt Optimization Becomes Jailbreaking | adversarial prompts | safety eval / red-team signal | adaptive optimization | safety boundary evidence |

## Preliminary Deep-Read Priority

### P0: Directly Affects Solution Design

- ProTeGi, GEPA, SePO, MemAPO, Modular Prompt Optimization, SPEAR, AutoPDL, MASPO, TextReg, PrefPO.

### P1: Affects Taxonomy and Risk Sections

- Textual Gradients are a Flawed Metaphor, Why Prompt Optimization Works, Reflection in the Dark, Prompt Optimization Is a Coin Flip, When Prompt Optimization Becomes Jailbreaking, When Gradients Collide.

### P2: Application and Scenario Reference

- Knowledge Graph APO, AutoMedPrompt, ArchEHR-QA series, Political Science Text Classification, APRIL, Knowledge Restoration-driven Prompt Optimization.

## Current Gaps

- ~~Need to supplement classic anchors not necessarily in the top80: APE, OPRO, DSPy, MIPROv2, TextGrad original papers.~~（Closed 2026-06-10: all 5 papers completed full evidence-level deep reads; notes at `docs/paper_notes/paper-ape-2022.md`, `paper-opro-2023.md`, `paper-dspy-2023.md`, `paper-miprov2-2024.md`, `paper-textgrad-2024.md`; together with existing ProTeGi/EvoPrompt/PromptBreeder they form the baseline trunk APE→ProTeGi→OPRO→PromptBreeder/EvoPrompt→DSPy→TextGrad→MIPROv2→GEPA. Still-pending earlier anchors: AutoPrompt, RLPrompt; GrIPS supplemented 2026-06-12 (`docs/paper_notes/paper-grips-2022.md`, pre-history positioning: gradient-free edit search predates APE, no LLM generator), same date PromptAgent supplemented (`docs/paper_notes/paper-promptagent-2023.md`, MCTS planning search missing link).)
- 2026-06-10 completed **external completeness verification** against 3 survey papers (APO survey 2502.16923, APE survey 2502.11560, Context Engineering survey 2507.13334); conclusions in `docs/arxiv_taxonomy_completeness_check_20260610.md`: the 7 clusters have no whole-block omissions within the scope of "discrete natural-language prompt optimization"; identified issues are: under-coverage of sub-mechanisms within clusters (learned scoring / token-level editing / bandit filtering / MoE routing), frontiers to register (task-agnostic/online, constrained optimization, bi-level/thought-driven reasoning models, multi-task), and intentional boundaries to declare explicitly (soft prompts, multimodal, full context-engineering systems). Highest-priority single-item follow-up: bi-level/thought-driven (o1/R1 reasoning model) prompt optimization.
- The current matrix has not yet verified train/dev/test splits, cost, and code availability for each paper.
- P0 papers need to be converted one by one into `docs/paper_notes/` template notes before selecting minimal experiment candidates.
- To move from paper taxonomy into insights and experience synthesis, start with `docs/arxiv_top80_insights.md`, which distills the main paper entries into verifiable insight cards.
- To move from taxonomy into an executable workflow, start with `docs/arxiv_top80_action_playbook.md`, which breaks down major problems into specific symptoms, solutions, and minimal experiments.
