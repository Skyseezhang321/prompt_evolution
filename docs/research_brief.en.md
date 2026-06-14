# Research Brief

Updated: 2026-06-08

Current phase: Five-day delivery version M0 — source collection, insight distillation, core conclusions, and helpful methods candidate freeze. The research hypotheses in this document serve as navigational threads for organizing materials, not established conclusions; the final report must distinguish evidence-supported claims, preliminary validated observations, and unverified conjectures.

The main line of this project is survey and experience synthesis. Experiments are used to validate key insights, demonstrate methods, and calibrate boundaries — they are not the project goal in themselves.

## Research Questions

Prompt optimization can be viewed as a discrete, black-box, noisy program search problem: given a task, model, context, examples, and evaluation function, find the instruction combination that stably improves the target metric. Self-evolution further requires the system to accumulate experience from historical successes and failures so that, when facing new tasks or new inputs in the future, it can automatically reuse that experience.

This research addresses three levels:

- Single-prompt optimization: automatically rewriting instructions, few-shot examples, and output format constraints.
- Multi-component system optimization: simultaneously optimizing system prompt, retrieval context, tool policy, agent handoff, and judge rubric.
- Self-evolving loop: distilling reusable strategies from execution trajectories and failure modes so that the optimizer itself can also be improved.

The five-day delivery version additionally focuses on an engineering question: how to transform current frontier methods into understandable, reusable, and verifiable insights, conclusions, and helpful methods.

## Output Priorities

Outputs for this phase are ranked in the following order:

1. Insights: concrete, transferable, verifiable insights, e.g., "failure samples should be compressed into editable evidence rather than merely recording scores."
2. Conclusions: conclusions with evidence level, counter-examples, and boundaries — avoid presenting a single paper or single example as a stable pattern.
3. Helpful methods: directly reusable methods or playbooks, including applicable scenarios, steps, metrics, risks, and misuse boundaries.
4. Anti-patterns: seemingly reasonable practices that are easy to mislead, e.g., one-shot rewrite, looking only at average scores, unbounded memory.
5. Validation demos: minimal validations or demonstrations used to calibrate the above four categories of outputs.

The precise definitions, distinction criteria, and required fields for each of the above output types are governed by `docs/insight_field_standard.md`.

## Key Definitions

- Prompt optimization: searching for or generating a better prompt under fixed model weights to improve task metrics.
- Automatic Prompt Optimization/APO: using LLMs, search algorithms, gradient-style text feedback, Bayesian optimization, evolutionary algorithms, and similar approaches to automatically optimize prompts.
- Self-evolving prompt: a system that continuously updates the prompt or prompt-generation strategy from historical execution results, reflection, memory, or a candidate archive.
- Context engineering: extending prompt into information engineering over the entire context window, including retrieval, compression, example selection, memory, tool returns, and format governance.

## Technical Taxonomy

| Dimension | Representative Methods | Research Focus |
| --- | --- | --- |
| Candidate generation | LLM generation, rule mutation, text gradient, reflection rewriting, example resampling | Candidate quality, search space, interpretability |
| Candidate selection | beam search, bandit, Bayesian optimization, Pareto frontier, validation split | Sample efficiency, overfitting control |
| Feedback signals | exact match, rubric judge, human preference, trajectory diagnosis, tool errors, cost/latency | Feedback noise, judge calibration |
| Optimization target | instruction, few-shot, system prompt, context, tool policy, agent workflow | Single-point rewriting vs. system-level coordination |
| Memory mechanism | successful-strategy library, failure-mode library, candidate archive, experience retrieval | Cross-task generalization, contamination prevention |
| Governance mechanism | prompt versioning, eval gate, rollback, approval, monitoring | Production safety, audit, drift detection |

## Research Hypotheses

H1: Natural-language reflection based on execution trajectories is more sample-efficient than optimization that only looks at final scores, especially for multi-step systems such as agent, RAG, and tool-use.

H2: When prompt self-evolution is truly effective, the optimization target is usually not a single string but a combination of "prompt + examples + context + tools + evaluator."

H3: Self-evolving systems need to explicitly distinguish mutable layers from immutable layers. Business objectives, permission boundaries, safety policies, and compliance requirements should serve as constraints that cannot be automatically modified; style, examples, retrieval hints, and local strategies can be optimized.

H4: Memorizing successful strategies and failure modes is more likely to reduce cost and improve cross-task generalization than starting the search from scratch for every task.

H5: Prompt self-evolution without strong eval, versioning, and rollback mechanisms will quickly become unauditable behavior drift.

## Technical Route

1. Source collection: broadly gather papers, engineering frameworks, official documentation, industry practices, and failure cases.
2. Frontier state summary: covering methods from APE, ProTeGi, OPRO, PromptBreeder, DSPy, TextGrad through GEPA, MemAPO, SePO, MASPO and others, forming a method map and evidence grading.
3. Engineering abstraction: treat prompts as versionable code assets and evals as optimization objectives and release gates.
4. Insight distillation: transform source conclusions into insight cards, core conclusions, helpful methods, anti-patterns, and risk boundaries.
5. Preliminary validation: choose 1–2 key insights or methods for minimal validation; avoid implementing an overly large benchmark harness for the sake of completeness.
6. Final report: centered on insights, conclusions, and helpful methods, integrating frontier state, industry experience, validation observations, and follow-on routes.
7. Future extensions: continue with system-level RAG/tool-use experiments, memory-based self-evolution, and cross-task transfer validation.

## Risks and Controls

- Overfitting eval: a validation split and hidden test set must be retained.
- Judge bias: LLM-as-judge requires human sample calibration; critical metrics should mix in rule-based scoring wherever possible.
- Cost overrun: record token count, call count, candidate count, and marginal gain per round.
- Prompt drift: every automatic modification must produce a diff, rationale, evaluation result, and rollback point.
- Safety regression: safety rules and permission boundaries must not be included in the automatic rewriting search space.
- Cross-model fragility: the same prompt should be tested for robustness on at least the target model and one alternative model.

## Expected Outputs

- A continuously updated literature map.
- A traceable source inventory, method taxonomy, and material-gap list.
- A current frontier state summary covering representative papers, tool practices, major debates, and transferable insights.
- A stable insight / conclusion / helpful method list covering applicable scenarios, steps, counter-examples, misuse risks, and validation approaches.
- 2–3 high-priority reusable methods or recommendations, including applicable scenarios, metrics, costs, risks, and rollback strategies.
- 1–2 preliminary validation or demonstration designs, including the insight being validated, failure cases, and conclusion limitations.
- A final statement and report, including a route for expanding into a benchmark harness in the future.
