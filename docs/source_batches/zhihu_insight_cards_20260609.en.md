# Zhihu Source Batch: Insight & Method Cards

Updated: 2026-06-10

Related document: [Zhihu Source Candidate Three-Layer Analysis](zhihu_three_layer_analysis_20260608.md)

2026-06-10 revision: (1) `evidence_strength` converged from ZH-L1..L4 to the standard A/B/C/D (see the Evidence Boundary section), and `main_sources` added to each card; (2) added [ZHI ↔ Cross-channel catalog cross-reference] to prevent double-counting; (3) the [Key Traceability Targets] table is now linked to source_ids already registered in the repository and to existing structured notes. Note: Registering candidates into `source_inventory.md` and adding `CHANGELOG.md` entries were omitted this time because those files are being concurrently edited by other channels; they will be added once those files are clean.

Raw artifacts:

- `artifacts/source_search/source_candidates_20260608_132914.jsonl`
- `artifacts/source_search/source_candidates_20260608_132914.md`

## Document Goal

This document rewrites the Zhihu batch from a "source summary" into material closer to the final report: insights, conclusions, helpful methods, anti-patterns, and minimum validation candidates.

The primary value of the Zhihu batch is not to prove that a particular prompt optimizer works, but to observe how the Chinese-language community understands, disseminates, misinterprets, and uses prompt optimization, GEPA, DSPy, context engineering, and agent self-evolution. When incorporated into the final report, Zhihu material should contribute primarily to problem awareness, lay-language articulation, anti-patterns, and deep-read leads; performance, benefit, and applicability boundary claims must be backed by evidence from papers, official documentation, code, or this project's own experiments.

## Evidence Boundary

This batch is based on titles and summaries returned by Brave Search. Direct access to some Zhihu links returned 403 errors, so current evidence levels are low.

**`evidence_strength` uses the standard A/B/C/D scale throughout** (definitions in [insight_field_standard.md](../insight_field_standard.md), Section 4). The ZH-L1..L4 scale previously used for the Zhihu channel indicates only "traceability progress," not an independent evidence-strength scale; it is mapped to the standard grades as shown below. The `evidence_strength` field in each card follows the mapped A/B/C/D values; ZH-Lx values are no longer used.

| Traceability Progress (ZH-Lx) | Meaning | Maps to evidence_strength | Current Use |
| --- | --- | --- | --- |
| ZH-L1 | Based only on search titles, summaries, URLs, and topic clustering | D | Discovering Chinese-community problem awareness, dissemination framing, and traceability candidates |
| ZH-L2 | Full text read; local snapshot path, SHA256, and structured summary recorded | D (single secondary source; still does not prove effectiveness) | May be written up as an industry note |
| ZH-L3 | Traced back to the original paper, official documentation, code, or a runnable example | B (can reach A when a primary source has a structured note) | Can support method background and evidence chains |
| ZH-L4 | Corroborated by another channel or by this project's own experiments | A | May enter the core conclusions of the final report |

Batch note: most cards in this batch remain at ZH-L1 (i.e., evidence_strength D); a few that can already point to structured notes committed in the repository (e.g., GEPA, MemAPO/SePO) are graded B. Each card's `main_sources` lists the in-repository files or source_ids currently traceable; until traceability is complete, any claim involving "surpasses RL," "large improvement," "self-evolving," or "production-ready" must not be written into the core conclusions of the final report.

## Quick Conclusions

1. Zhihu candidates show that the Chinese-language community has shifted prompt optimization from a "prompt-tip" problem to an engineering problem of "samples, scorer, candidates, iteration" — but many articles still lack evaluation fields.
2. GEPA is frequently disseminated as "stronger than RL." A more defensible insight is: for tasks with execution traces, natural-language reflection may provide denser rewrite signals than a single scalar score.
3. The key point of DSPy/MIPRO is not "automatically writing prompts" but turning instruction, examples, metric, and optimizer into composable, evaluable program components.
4. Context engineering is very prominent in Zhihu material, indicating that many real-world failures are not prompt-wording problems but problems with retrieval, memory, tool output, history compression, or output schema.
5. Tool-experience articles can help discover user needs and the domestic tool ecosystem, but only articles that expose dataset, metric, diff, cost, failure, and rollback deserve entry into the evidence chain.
6. Agent self-evolution directions are attracting a lot of attention, but the optimization target must first be defined: task prompt, system prompt, skill, tool description, memory, and workflow policy must not be conflated.

## Plain-Language Summary for General Users

| Specific Insight | What a General User Can Do | Why It Helps | Evidence Boundary |
| --- | --- | --- | --- |
| Don't start by asking AI to "help me optimize this prompt." | First write 10–20 test samples and failure examples, then ask AI to revise the prompt based on those samples. | Without samples and scoring criteria, optimization is just rephrasing. | Zhihu material exposes pain points; effectiveness requires experimental validation. |
| When the model fails, first identify the failure type. | Categorize failures as: misunderstood task, missing context, format drift, tool error, excessive refusal, factual error. | Only by knowing where it went wrong can you decide whether to fix the prompt, context, or tool. | Suggested by context engineering and agent articles together. |
| Don't interpret GEPA-style methods as a universal RL replacement. | For tasks with traces, compare `score-only rewrite` against `trace + critique rewrite`. | Trace reflection can explain the cause of failure and may reduce blind search. | Must be referred back to the GEPA paper and validated in this project. |
| DSPy/MIPRO is not a prompt-template library. | Write the task as a signature, examples, and metric, then let the optimizer search. | prompt, examples, and evaluation function become versioned components. | Zhihu can serve as a terminology entry point; evidence goes back to DSPy/MIPRO. |
| For agent/RAG scenarios, inspect the context first, then adjust the system prompt. | Log retrieval, memory, tool result, history, schema, and prompt separately. | Many failures stem from the model seeing the wrong information, not from insufficiently elegant instructions. | Needs reinforcement from other platforms and engineering source code. |
| When reading tool articles, look for evaluation fields, not demo screenshots. | Extract only: dataset, metric, baseline, candidate diff, cost, failure, rollback. | These fields determine whether a tool can form a reviewable closed loop. | Articles without evaluation fields are treated only as tool leads. |
| Self-evolution is not "let the system memorize everything." | For every memory/skill entry, record its source, applicable scope, validation result, and how to disable it. | Unbounded memory pollutes subsequent tasks and creates unauditable drift. | Requires support from project source code, issues, or experiments. |
| Downgrade generic prompt tips. | Retain a tip only when it can be mapped to samples, metrics, failure patterns, or verifiable actions. | Prevents "experience rules of thumb" from being written up as research conclusions. | Most generic-tip articles in the current batch do not enter the core evidence chain. |

## Insight Card Overview

| id | Candidate Insight | Main Source Cluster | evidence_strength (traceability progress / path to supplementary evidence) | Minimum Validation Priority |
| --- | --- | --- | --- | --- |
| ZHI-01 | Prompt optimization has shifted from a tips problem to eval-driven iteration. | APO/APE/OPRO/EvoPrompt/PRewrite Chinese-language analyses | B (coin-flip / ProTeGi notes already exist; tracing the APO lineage can upgrade to A) | high |
| ZHI-02 | The transferable insight from GEPA is trace-aware reflection, not "comprehensively surpassing RL." | GEPA / reflective prompt evolution articles | B (GEPA note already supports this) | high |
| ZHI-03 | DSPy/MIPRO should be framed as prompt-as-program, not an automatic prompt generator. | DSPy / MIPRO / Prompt-compilation articles | D (DSPy/MIPRO paper note pending; inventory already registered) | high |
| ZHI-04 | Context engineering expands the optimization target from a single prompt to everything the model can see. | Context Engineering / agent context / RAG context | D (context engineering engineering material pending note) | high |
| ZHI-05 | The selection criterion for tool articles is whether they support a reviewable evaluation closed loop. | OPIK / Prompt Optimizer / PromptPilot / Coze | D (official tool documentation pending note) | medium |
| ZHI-06 | Agent self-evolution must first define which objects are mutable and which are frozen. | Hermes / Manus / Skill / agent self-evolution | B (MemAPO / SePO notes already support this) | high |
| ZHI-07 | Chinese-language sources are suited for distilling user language and misconceptions, not for directly supporting performance conclusions. | Entire batch combined | D (channel-level methodological judgment) | medium |
| ZHI-08 | Generic prompt tips are an anti-pattern lead unless they can be integrated into eval and version management. | Generic prompt engineering articles | D (determined after integration with catalog I-07/I-12) | medium |

## ZHI ↔ Cross-Channel Catalog Cross-Reference (Preventing Double-Counting)

The Zhihu ZHI cards and the researcher-oriented [insight_method_catalog](../insight_method_catalog_20260609.md) I- / HM- identifiers are two separate namespaces. When merging into the final report's cross-channel insight pool, duplicates must be removed according to the table below to avoid counting a Chinese-language dissemination of the same insight as an independent insight. `Relationship` values: `duplicate` (same insight), `extension` (supplements an existing insight's boundary/language/cases), `new` (not yet in the catalog).

| Zhihu Entry | Corresponding Catalog | Relationship | Net Increment from Zhihu Channel |
| --- | --- | --- | --- |
| ZHI-01 | I-01, I-02, I-11 | duplicate | User language for the "find a universal template" pain point in the Chinese-language community |
| ZHI-02 | I-02 | extension | Dissemination framing of the "surpasses RL" headline being misread |
| ZHI-03 | I-06 (incl. I-05) | duplicate | Simplified misreading of "automatically writes prompts" |
| ZHI-04 | I-06 | duplicate | Discussion density of context engineering in Chinese-language circles |
| ZHI-05 | I-12, I-04, HM-04 | duplicate | Sample of marketing language in tool-experience posts |
| ZHI-06 | I-08, I-06 | extension | Chinese-language narrative of "mutable objects not disaggregated" in agent self-evolution |
| ZHI-07 | I-12 | duplicate | Channel-level corroboration (Chinese secondary sources = leads, not performance conclusions) |
| ZHI-08 | I-07, I-12 | extension | User pain-point expression for downgrading generic tips |
| HM-ZH-01 | HM-01 | duplicate | — |
| HM-ZH-02 | HM-02 | duplicate | — |
| HM-ZH-03 | (none) | new | Primary-source promotion gate for secondary posts — not yet in the catalog |

Conclusion: the Zhihu channel overlaps heavily with the catalog; the vast majority are `duplicate`/`extension`. The only net-new reusable method is **HM-ZH-03 (primary-source promotion gate)**. In the final report, ZHI-01 through ZHI-08 should be cited as "Chinese-language dissemination / misconception / user-language" supplementary material for the corresponding I- insights, and should not be counted as independent entries.

## Detailed Insight Cards

### ZHI-01: Prompt optimization has shifted to eval-driven iteration

- insight: Zhihu material repeatedly groups APE, APO, OPRO, EvoPrompt, PRewrite, and PromptBreeder together, indicating that the discussion focus is shifting from "write a good prompt" to "generate candidates, evaluate candidates, select candidates, then iterate."
- user_facing_one_liner: Don't optimize a single sentence — optimize a process that includes test samples.
- phenomenon: Chinese-language articles extensively introduce automatic prompt engineering, prompt search, reflective rewriting, and evolutionary candidate generation, but frequently name only the algorithm and omit dataset, metric, and validation split.
- mechanism: A prompt is a discrete text program. Without samples, a scorer, and a candidate ledger, an optimizer cannot distinguish genuine improvement from style variation or lucky coincidence.
- actionable_rule: For any prompt optimization material, first extract `task`, `baseline prompt`, `test cases`, `metric`, `candidate generation`, `selection rule`, `rollback`.
- helpful_method: Eval-first prompt optimization intake.
- exact_action_to_try: Take an existing prompt, pair it with 20 test samples, run the baseline, then ask the model to provide a rewrite rationale and diff based only on failing samples.
- before_after_example: Before: "Help me optimize this customer-service prompt." After: "On 20 customer-service samples, the baseline has 6 format errors and 3 cases of excessive refusal — please revise only the output format and refusal boundary, and retain a rollback version."
- counterexample_or_limit: One-off creative writing, tone polishing, or exploratory brainstorming may not require a full eval closed loop.
- evidence_strength: B (traceability progress ZH-L1, but the mechanism is already supported by structured notes). Can upgrade to A when corroborated with more arXiv/GitHub/other-platform material.
- main_sources: [paper-coin-flip-2026.md](../paper_notes/paper-coin-flip-2026.md), [paper-protegi-2023.md](../paper_notes/paper-protegi-2023.md), [insight_method_catalog](../insight_method_catalog_20260609.md) (I-01, I-02).
- validation_or_demo: Compare one-shot rewrite vs. eval-first rewrite on held-out samples, format drift rate, manual review time, and cost.

### ZHI-02: The core of GEPA is not "replacing RL" but trace-aware reflection

- insight: Zhihu articles about GEPA are often headlined as "surpasses RL" or "stronger than reinforcement learning," but for this project the more valuable takeaway is the mechanistic explanation of trace-aware reflection.
- user_facing_one_liner: For tasks with an execution trace, don't look only at the final score — have the model read the failure trace before revising.
- phenomenon: GEPA is used to connect prompt evolution, DSPy, agent traces, and natural-language reflection; it has high dissemination volume, but secondary articles easily overstate conclusions.
- mechanism: A scalar reward only tells the optimizer whether performance was good or bad; a trace and critique can tell the optimizer where it went wrong, which component to fix, and which behaviors must not be broken.
- actionable_rule: In the report, avoid writing "GEPA is comprehensively superior to RL"; instead write "on certain tasks with trace feedback, language reflection may provide higher-density optimization signals."
- helpful_method: Trace-first agent prompt diagnosis.
- exact_action_to_try: For the same batch of failing tasks, generate prompt diffs using only the final score and using the full trace separately; compare whether the changes are smaller, more auditable, and more stable on held-out cases.
- before_after_example: Before: "Score is low — rewrite the prompt." After: "Step 3 tool-call parameters were wrong and history compression dropped the user's location constraint; therefore only fix the tool instruction and the history summary rubric."
- counterexample_or_limit: When there is no clear trace, evaluation is very noisy, the task is very short, or the output requires only simple format fixes, trace reflection may not be cost-effective.
- evidence_strength: B (traceability progress ZH-L1; GEPA structured note already supports this mechanism). Can upgrade to A after replication in this project.
- main_sources: [paper-gepa-2026.md](../paper_notes/paper-gepa-2026.md), [insight_method_catalog](../insight_method_catalog_20260609.md) (I-02).
- validation_or_demo: Construct two groups — `score-only rewrite` vs. `trace + critique rewrite` — and record sample efficiency, change size, cost, and failure-type migration.

### ZHI-03: DSPy/MIPRO should be explained as prompt-as-program

- insight: Zhihu DSPy/MIPRO material is well suited to helping Chinese-language readers understand that "a prompt is not just text but a combination of signature, examples, metric, and optimizer."
- user_facing_one_liner: Manage prompts as program components, not as a chat-template collection.
- phenomenon: Chinese-language material tends to simplify DSPy/MIPRO as "automatically generating prompts," but higher-quality material usually mentions signature, training examples, metric, optimizer, and the compilation process.
- mechanism: DSPy makes the task interface, examples, and scoring function explicit so the optimizer can search over instructions and few-shot examples.
- actionable_rule: When citing DSPy/MIPRO, you must simultaneously state what is being optimized and what the scoring function is; showing only the optimized prompt is not sufficient.
- helpful_method: Prompt-as-program conversion checklist.
- exact_action_to_try: Rewrite a chat template into five parts: `input fields`, `output schema`, `examples`, `metric`, `optimizer budget`.
- before_after_example: Before: "You are a professional classifier. Please classify." After: "signature: `text -> label, rationale`; metric: label accuracy + JSON validity; examples: 16; optimizer: allowed to change instruction and examples only."
- counterexample_or_limit: If the task has no stable metric, or if samples are too few to distinguish candidates, DSPy/MIPRO can only serve as an organizational framework and cannot automatically guarantee improvement.
- evidence_strength: D (traceability progress ZH-L1; DSPy/MIPRO only registered in inventory — structured paper note pending).
- main_sources: [source_inventory.md](../source_inventory.md) (`paper-dspy-2023`, `paper-miprov2-2024`), [insight_method_catalog](../insight_method_catalog_20260609.md) (I-06).
- validation_or_demo: On the same classification task, compare "hand-written template rewrite" vs. "signature + metric + optimizer" workflow on review cost, format error rate, and held-out performance.

### ZHI-04: Context engineering is a boundary expansion of prompt optimization

- insight: Context engineering is densely discussed in Zhihu candidates, indicating that real-world engineering has already expanded the optimization target from system prompt to retrieval, memory, tool result, history compression, and schema.
- user_facing_one_liner: When the model gives a wrong answer, first look at what it saw, then look at how you instructed it.
- phenomenon: Many articles revolve around context engineering, agent context, Manus experiences, RAG, and tool context — topics no longer limited to prompt wording.
- mechanism: LLM output is governed by its visible context. If retrieval is wrong, tool return format is messy, memory is polluted, or history summaries drop constraints, simply changing the system prompt only masks the problem.
- actionable_rule: Optimization records for RAG/agent tasks must decompose `prompt`, `retrieval`, `memory`, `tool output`, `history`, `output schema` separately.
- helpful_method: Trace-first agent prompt diagnosis.
- exact_action_to_try: For every failure, fill in a context fault table — annotate which context component caused the failure before deciding whether to change the prompt.
- before_after_example: Before: "Make the model follow user constraints more strictly." After: "Retrieved document 2 is outdated and the history summary dropped the user's region restriction — fix the retrieval filter and summary rubric first."
- counterexample_or_limit: For pure text rewriting, short Q&A, or tasks with no external context, the problem may still be primarily instruction quality.
- evidence_strength: D (traceability progress ZH-L1; requires context engineering engineering material to be structured before supplementary evidence can be added).
- main_sources: [source_inventory.md](../source_inventory.md) (`paper-context-engineering-2025`, `practice-anthropic-context-engineering`, `practice-langchain-agent-context-engineering`), [insight_method_catalog](../insight_method_catalog_20260609.md) (I-06).
- validation_or_demo: On a RAG task, compare `prompt-only fix` vs. `context-first fix` on correctness, attribution clarity, and second-order regression.

### ZHI-05: Tool articles must be filtered by evaluation fields

- insight: Zhihu tool-experience articles can surface product requirements but cannot prove a tool works based on demo screenshots. Only material that includes dataset, metric, baseline, trial history, failure, and rollback has research value.
- user_facing_one_liner: When reading a tool article, don't ask "does it work?" — first ask "how was that measured?"
- phenomenon: Candidates such as OPIK, Prompt Optimizer, PromptPilot, and Coze indicate strong demand for tooling, but at the summary level they frequently lack reproducible configurations.
- mechanism: If a prompt optimizer tool does not record candidates, scores, costs, failure samples, and rollback points, users cannot determine whether the optimization generalizes, nor can they post-mortem misuse.
- actionable_rule: Before a tool source enters the list, it must provide at least 3 categories of fields: evaluation input, candidate changes, run results.
- helpful_method: Primary-source promotion gate for posts.
- exact_action_to_try: When reading a tool article, fill in one extraction table only: `dataset`, `metric`, `baseline`, `optimized object`, `diff`, `cost`, `failure`, `rollback`.
- before_after_example: Before: "This tool can optimize a prompt in one click." After: "The tool uses 50 validation data points and records trial history, but does not show held-out results — it can therefore be treated only as medium evidence."
- counterexample_or_limit: Product introductions can be used to discover the ecosystem and user language; they need not be discarded entirely, but they cannot enter the effectiveness evidence chain.
- evidence_strength: D (traceability progress ZH-L1; requires official tool documentation or local run logs to be structured before supplementary evidence can be added).
- main_sources: [insight_method_catalog](../insight_method_catalog_20260609.md) (I-12, HM-04), [source_inventory.md](../source_inventory.md) (`practice-opik-optimizer-overview`, `practice-promptfoo-optimization`).
- validation_or_demo: Sample 10 tool articles and use the field table to determine which can enter `source_inventory.md` and which serve only as leads.

### ZHI-06: Agent self-evolution must first define mutable objects

- insight: Zhihu agent self-evolution material attracts high interest, but "self-evolution" may refer to changes in task prompt, system prompt, skill, tool description, memory, workflow policy, or evaluator. Without disaggregating these, no verifiable conclusion can be formed.
- user_facing_one_liner: A self-evolving system must first declare what it can change and what it cannot change.
- phenomenon: Articles about Hermes, Manus, Skill, and agent context often discuss memory, reflection, tool calls, system prompts, and workflow policies all together.
- mechanism: Different objects carry different risks and require different validation approaches. Changing a task prompt affects local behavior; changing a system prompt affects global boundaries; changing memory can cause long-term pollution; changing the evaluator manufactures false improvements.
- actionable_rule: Self-evolution experiments must freeze the evaluator, data, and safety boundaries, and allow only one mutable object into the search.
- helpful_method: Mutable-object declaration for self-evolution.
- exact_action_to_try: For each self-evolution experiment, write `mutable_object`, `frozen_objects`, `promotion_rule`, `rollback_plan`.
- before_after_example: Before: "The agent will self-improve from experience." After: "This round allows only adding one skill instruction; it does not allow changing the grader, tools, system safety policy, or eval cases."
- counterexample_or_limit: Early-stage exploration may collect failure patterns broadly first, but variables must be disaggregated before entering experiments or conclusions.
- evidence_strength: B (traceability progress ZH-L1; MemAPO/SePO structured notes already support the "mutable-object disaggregation" mechanism). Can upgrade to A after verifying Hermes project source code, issues, and run traces.
- main_sources: [paper-memapo-2026.md](../paper_notes/paper-memapo-2026.md), [paper-sepo-2026.md](../paper_notes/paper-sepo-2026.md), [practice-zhihu-hermes-agent-2026.md](../industry_notes/practice-zhihu-hermes-agent-2026.md), [insight_method_catalog](../insight_method_catalog_20260609.md) (I-08).
- validation_or_demo: Compare "allow multiple objects to change simultaneously" vs. "allow only skill description changes" on metric attribution, rollback difficulty, and safety regression.

### ZHI-07: Chinese-language sources are better suited as an explanation layer and misconception layer

- insight: In the final report, Zhihu material is best suited to the role of "how ordinary users understand this" and "what the common misconceptions are," rather than serving as strong evidence.
- user_facing_one_liner: Chinese-language articles help you understand the problem; proving effectiveness requires going back to primary sources.
- phenomenon: The Chinese-language community disseminates GEPA, DSPy, context engineering, and agent self-evolution rapidly, which can reveal problems users care about and how they accept new terminology.
- mechanism: Secondary-source interpretations compress details and tend to amplify headline claims. They excel at explanation but are poor at preserving experimental setup, negative examples, and applicability boundaries.
- actionable_rule: The final report may cite Zhihu as "dissemination observations" and "misconception reminders," but core conclusions require A/B/C-level evidence.
- helpful_method: Primary-source promotion gate for posts.
- exact_action_to_try: Bind every Zhihu candidate to a `primary_source_needed` field; do not write it into core conclusions until the primary source has been traced.
- before_after_example: Before: "A Zhihu article says GEPA outperforms RL." After: "The Chinese-language community commonly disseminates this; the final judgment goes back to the GEPA paper's task setup, baseline, and budget."
- counterexample_or_limit: A small number of long-form Zhihu posts may contain original engineering practice, code, or real evaluations; in those cases they may be upgraded to ZH-L2 following the industry note template.
- evidence_strength: D (traceability progress ZH-L1; this is a channel-level methodological judgment, which itself corresponds to catalog I-12).
- main_sources: [insight_method_catalog](../insight_method_catalog_20260609.md) (I-12).
- validation_or_demo: Deep-read 10–15 highly relevant Zhihu full-text posts and annotate which are original practice, which are restatements of primary material, and which are generalized headlines.

### ZHI-08: Generic prompt tips that are detached from eval are an anti-pattern to be downgraded

- insight: Generic prompt-tip articles can illustrate user pain points, but if they cannot be mapped to tasks, samples, metrics, or failure types, they should not enter core research conclusions.
- user_facing_one_liner: Don't collect universal templates — collect changes that can be tested.
- phenomenon: The candidates still include a small number of prompt engineering tips, prompt guide, and template-style articles; these typically lack automated optimization, failure cases, and evaluation processes.
- mechanism: General tips easily fail across different tasks, models, and contexts; without versioning and metrics, users mistake subjective satisfaction for stable gains.
- actionable_rule: A generic tip is retained only when it meets at least one of the following: it can serve as a baseline, it constitutes a failure type, it can be converted into an eval case, it explains an anti-pattern.
- helpful_method: Prompt-tip downgrade rule.
- exact_action_to_try: Rewrite each piece of advice in a tip article as a testable assertion; anything that cannot be rewritten is downgraded.
- before_after_example: Before: "Prompts should be specific." After: "In an information-extraction task, the output schema must include a handling rule for missing fields; otherwise JSON validity drops."
- counterexample_or_limit: Introductory educational content may be retained in background material, but should not occupy core space in the final report.
- evidence_strength: D (traceability progress ZH-L1; determined after integration with catalog I-07/I-12).
- main_sources: [insight_method_catalog](../insight_method_catalog_20260609.md) (I-07, I-12).
- validation_or_demo: Extract 20 recommendations from generic-tip articles and count how many can be converted into measurable eval cases.

## Helpful Methods Candidates

### HM-ZH-01: Eval-first prompt optimization intake

```yaml
name: Eval-first prompt optimization intake
insight_supported: ZHI-01, ZHI-05, ZHI-08
problem: Users often ask directly for prompt optimization without samples, metrics, failure types, or rollback points.
recommended_when: The task will run repeatedly and at least 10–50 representative samples can be collected.
not_recommended_when: One-off creative writing, exploratory brainstorming, open-ended expression with no stable evaluation criteria.
required_inputs: baseline prompt, task definition, eval samples, rubric or metric, current failures, target model, cost budget.
implementation_steps: 1. Write out the task and success criteria; 2. Collect samples and failure examples; 3. Run the baseline; 4. Cluster by failure type; 5. Generate candidate prompts targeting only the main failure types; 6. Select using a validation set; 7. Record diff, cost, failures, and rollback point.
evaluation_metrics: task score, JSON or schema validity, refusal boundary, held-out score, judge disagreement, cost, latency.
expected_benefit: Turns subjective rewriting into a reviewable iteration loop; reduces prompt selection by gut feeling.
cost_and_latency: Requires preparing samples and at least one baseline eval; short-term cost is higher than one-shot rewrite.
risks: Too few samples leads to overfitting; an ambiguous rubric induces judge bias.
misuse_or_anti_pattern: Picking the highest-scoring prompt on training samples only, ignoring held-out results and failure examples.
rollback_plan: Retain the baseline prompt, candidate diffs, acceptance rationale, and rejection rationale; after release, rollback to the baseline or the previous stable version is possible.
evidence: Zhihu batch provides ZH-L1 problem leads; cross-validation with GitHub optimizer ledger, Promptfoo/OPIK/Humanloop official documentation, and similar resources is needed.
next_experiment: Compare one-shot rewrite vs. eval-first rewrite on held-out performance, format error rate, and review time.
```

### HM-ZH-02: Trace-first agent prompt diagnosis

```yaml
name: Trace-first agent prompt diagnosis
insight_supported: ZHI-02, ZHI-04, ZHI-06
problem: Agent/RAG failures are often misattributed to poorly written prompts when the actual cause may be context, tools, memory, or history compression.
recommended_when: The task involves multi-step reasoning, tool calls, RAG, memory, long conversations, or agent handoffs.
not_recommended_when: Single-turn short-text tasks, or simple classification tasks with no recordable execution trace.
required_inputs: failed traces, retrieved context, tool calls and outputs, conversation history, prompt versions, expected output schema, evaluator result.
implementation_steps: 1. Save the failed trace; 2. Annotate the step where failure occurred; 3. Classify as prompt/context/tool/memory/schema/evaluator problem; 4. Freeze unrelated components; 5. Change only the most likely causal object; 6. Re-test using the same trace and held-out cases.
evaluation_metrics: task success, step-level failure rate, tool error rate, retrieval relevance, schema validity, prompt diff size, rollback difficulty.
expected_benefit: Reduces the probability of blindly changing the system prompt; aligns the optimization target with the root cause of failure.
cost_and_latency: Requires trace logging and manual or LLM-assisted attribution; initial process is slower than directly editing the prompt.
risks: Very long traces increase cost; LLM attribution may explain coincidental events as stable causes.
misuse_or_anti_pattern: Changing prompt, retrieval, tool schema, and memory all at once, making attribution impossible.
rollback_plan: Each round publishes only one object's change and retains the previous prompt/context/tool policy version.
evidence: Zhihu batch provides ZH-L1 leads; GEPA, LangChain context engineering, GitHub agent harness material, and this project's experiments can provide reinforcement.
next_experiment: Compare score-only rewrite vs. trace-first diagnosis on RAG/agent tasks for sample efficiency and second-order regression.
```

### HM-ZH-03: Primary-source promotion gate for posts

```yaml
name: Primary-source promotion gate for posts
insight_supported: ZHI-05, ZHI-07, ZHI-08
problem: Secondary posts tend to compress paper, tool, or project claims into headlines, causing evidence strength to be overestimated.
recommended_when: Processing Zhihu, Twitter/X, Medium, Substack, blog, tool-promotion, and forum material.
not_recommended_when: Already an original paper, official documentation, fixed-commit source code, or this project's own run logs.
required_inputs: post URL, title, summary, claimed method, claimed result, linked primary source, reproducibility fields.
implementation_steps: 1. Extract the article's claims; 2. Mark whether dataset, metric, baseline, cost, and failure are present; 3. Search for the primary source; 4. If not found, keep at lead level; 5. Once found, write the industry note or paper note; 6. Annotate evidence level in the final report.
evaluation_metrics: promoted source ratio, claims with primary source, claims downgraded, unsupported performance claims removed.
expected_benefit: Prevents dissemination popularity from being treated as evidence of method effectiveness.
cost_and_latency: Requires additional traceability time; may reduce short-term material volume.
risks: Being overly conservative may miss original practice articles.
misuse_or_anti_pattern: Writing a post as a conclusion because it is clearly written or has many likes.
rollback_plan: Retain source_id and evidence level for every conclusion; if supplementary evidence cannot be provided, demote from conclusion to hypothesis or observation.
evidence: The Zhihu batch directly demonstrates this problem; other platforms and Twitter/X batches exhibit the same dissemination noise.
next_experiment: Sample 30 posts and measure the proportion that enter the core evidence chain after passing through the promotion gate, along with reasons for demotion.
```

## Anti-Patterns and Downgrade Rules

| anti-pattern | Why It Is Dangerous | Handling Rule |
| --- | --- | --- |
| "There are many Zhihu articles, so the conclusion is strong." | Volume indicates dissemination popularity, not experimental reproducibility. | Use only as problem awareness; conclusions must be traced back to primary evidence. |
| "GEPA comprehensively surpasses RL." | Ignores differences in task, budget, baseline, rollout, and feedback signal. | Rewrite as a pending-verification mechanistic insight; do not write as a universal conclusion. |
| "The tool can display an optimized prompt, so the tool is effective." | Demo screenshots cannot prove generalization, stability, or cost-benefit. | Upgrade evidence only when evaluation fields are complete. |
| "Context engineering means writing a longer prompt." | Misidentifies retrieval, memory, tool output, and history compression as instruction content to be stuffed in. | Disaggregate context components and record each separately. |
| "Self-evolution means accumulating more and more memory." | Unbounded memory pollutes subsequent tasks and is difficult to roll back. | Every memory/skill entry must have a source, applicable scope, validation result, and disable method. |
| "Prompt tips are universally applicable across tasks." | Different models, tasks, and contexts can invalidate tips. | Only tips that can be converted into eval cases enter core material. |
| "Changing multiple variables at once is faster." | Impossible to determine whether improvement came from prompt, context, examples, or evaluator. | Research experiments change only one variable at a time; note mixed variables when necessary. |

## Key Traceability Targets

The table below connects each traceability target to the source_ids already registered in `docs/source_inventory.md` and (where they already exist) the structured notes in `docs/paper_notes/`, turning ZHI cards from "should be traced" to "already pointing to specific in-repository primary sources."

| Target | Leads Obtained from Zhihu | In-Repository Primary Sources (source_id / note path) | Current Traceability Status | Role in Final Report |
| --- | --- | --- | --- | --- |
| GEPA | Reflective prompt evolution, trace feedback, comparison with RL | `paper-gepa-2025`; note [paper-gepa-2026.md](../paper_notes/paper-gepa-2026.md) | Structured note exists (B) | Core insight and validation candidate |
| DSPy / MIPRO | prompt-as-program, signature, optimizer, metric | `paper-dspy-2023`, `paper-miprov2-2024` (registered in inventory; paper note pending) | Inventory only (D) | Helpful method background |
| APO / ProTeGi / OPRO / EvoPrompt | Index of automated prompt engineering methods | `paper-protegi-2023` (note [paper-protegi-2023.md](../paper_notes/paper-protegi-2023.md)), `paper-evoprompt-2023` (note [paper-evoprompt-2024.md](../paper_notes/paper-evoprompt-2024.md)), `paper-ape-2022`, `paper-opro-2023`, `paper-prewrite-2024` | ProTeGi/EvoPrompt notes exist (B); others registered only (D) | Method taxonomy |
| Context engineering | Boundary expansion from prompt to context/workflow | `paper-context-engineering-2025`, `practice-anthropic-context-engineering`, `practice-langchain-agent-context-engineering` | Inventory only (D) | Engineering conclusions and anti-patterns |
| Hermes / Manus / Skill self-evolution | Agent experience accumulation, skill, memory, and self-evolution | `practice-zhihu-hermes-agent-2026` (note [practice-zhihu-hermes-agent-2026.md](../industry_notes/practice-zhihu-hermes-agent-2026.md)), `paper-memapo-2026`, `paper-sepo-2026` | Hermes note weak + MemAPO/SePO notes (B) | Self-evolution variable disaggregation leads |
| OPIK / Prompt Optimizer / PromptPilot / Coze | Tooling demand, domestic ecosystem, product workflows | `practice-opik-optimizer-overview`, `practice-promptfoo-optimization`, `repo-linshenkx-prompt-optimizer` | Official docs / source code registered; notes pending (D) | Industry tool map |

## Minimum Validation Candidates

| id | Insight/Method to Validate | Minimum Experiment Design | Key Metrics | Notes |
| --- | --- | --- | --- | --- |
| V-ZH-01 | ZHI-01 / HM-ZH-01 | Compare one-shot rewrite vs. eval-first rewrite on the same task. | held-out score, format error rate, manual review time, cost | Can be prioritized as a demonstration experiment for the final report. |
| V-ZH-02 | ZHI-02 / HM-ZH-02 | Compare score-only rewrite vs. trace-first diagnosis on the same batch of agent/RAG failure samples. | sample efficiency, failure-type migration, second-order regression, diff size | Requires trace logging to be set up first. |
| V-ZH-03 | ZHI-04 / HM-ZH-02 | Apply prompt-only fix and context-first fix separately to a RAG task. | answer correctness, retrieval relevance, schema validity | Validates whether context-first is more attributable. |
| V-ZH-04 | ZHI-05 / HM-ZH-03 | Apply the primary-source promotion gate to 30 posts. | promotion rate, demotion reasons, missing field distribution | Can serve as a material-organization quality check. |
| V-ZH-05 | ZHI-08 | Convert 20 generic prompt tips into eval cases and count the convertible proportion. | testable proportion, reasons for non-conversion, redundancy | Used to decide the share of generic tips in the final report. |

## Follow-Up Processing Recommendations

1. Deep-read 10–15 highly relevant Zhihu full-text posts; if login is required or the original text may expire, save snapshots to `local_sources/raw/` and record the SHA256.
2. Add a `primary_source_needed` field to each Zhihu article; prioritize tracing back GEPA, DSPy/MIPRO, APO/ProTeGi, context engineering, and Hermes/agent self-evolution.
3. Articles for which dataset, metric, baseline, failure, and rollback can be filled in should be written up as individual industry notes following `docs/industry_notes/template.md`.
4. The final report should not be presented as a "list of Zhihu articles"; instead, the ZHI cards in this document should be merged into the cross-channel insight pool.
5. ZH-L1 judgments in the current document cannot stand alone as conclusions; they may only serve as observations, hypotheses, or user-facing explanations.
