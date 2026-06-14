# Insight / Conclusion / Helpful Method Candidate List

Date: 2026-06-09 (I-13 / I-14 appended 2026-06-11, synchronized with main report v4; I-01..12 numbering and content unchanged)

Scope: This document is an intermediate content-organization layer before the final report. It does not replace paper notes, source-code audits, or industry practice notes; instead it compresses existing materials into reusable insights, conclusions, methods, anti-patterns, and validation candidates following the latest insight-first principle.

Evidence boundary:

- `evidence_strength` in this document uses the A/B/C/D grading from `docs/final_report_outline.md`.
- Grade A/B may serve as stronger conclusion or method candidates; grade C requires replication experiments in this project before upgrading; grade D may only be written as an unverified conjecture.
- Without replication experiments in this project, no improvement percentage from any paper may be stated as "proven effective by this project."

## How to Use

Field definitions and the criteria distinguishing insight / conclusion / helpful method are governed by `docs/insight_field_standard.md`. The abbreviated schema below omits `phenomenon` / `mechanism` / `actionable_rule` (each entry below already contains them), and `next_validation` should be unified to `validation_or_demo` per the standard.

The final report should lead with insights and methods that readers can immediately understand, then expand into paper, source-code, and industry evidence. Every judgment entering the final report must retain at least:

```yaml
insight:
user_facing_one_liner:
exact_action_to_try:
helpful_method:
evidence_strength:
counterexample_or_limit:
next_validation:
```

## Core Insight Candidates

### I-01: Test Whether Optimization Is Worth It Before Running an Optimizer

```yaml
insight: prompt optimization does not guarantee gains; many tasks may score below zero-shot after optimization.
user_facing_one_liner: Check whether there is headroom first, then spend money on automatic optimization.
phenomenon: In few-shot dev selection and free-text tasks, candidate differences may not exceed noise; a complex optimizer may select a prompt that happened to score high by chance.
mechanism: When zero-shot already approaches the model's capability ceiling for a given task format, prompt search mainly amplifies evaluation noise.
actionable_rule: Before every APO run, execute zero-shot, a manual baseline, and 10-20 candidates to estimate headroom and noise floor.
exact_action_to_try: Test 10-20 candidates on 20 held-out examples; stop optimization if best gain is below the noise threshold.
helpful_method: pre-optimization gate
evidence_strength: A
main_sources:
  - docs/paper_notes/paper-coin-flip-2026.md
  - docs/arxiv_deep_reading_batch3_synthesis.md
counterexample_or_limit: Tasks requiring many rounds of search to discover combinatorial structure may have their gains underestimated by a simple headroom test; thresholds must be recalibrated per sample size and scorer.
next_validation: Compare the predictive power of the headroom test on subsequent optimization gains across one structured-output task and one free-generation task.
```

### I-02: Turn Failure Examples into Editable Evidence, Not Just Scores

```yaml
insight: A score tells you "something broke"; a trace and critique tell you "what to fix."
user_facing_one_liner: Don't just log accuracy — log failure type, model output, and rewrite rationale.
phenomenon: Methods such as ProTeGi, GEPA, CriSPO, SPEAR, and JTPRO all rely on failed examples, traces, critiques, or tool-call diagnostics to generate candidates.
mechanism: Natural-language feedback compresses failed examples into editable prompt-revision directions, but it is not a mathematical gradient.
actionable_rule: Each eval case must record at minimum: prediction, gold, error_type, critique, candidate_prompt_id, selector_reason.
exact_action_to_try: For 20 failed examples, first write a failure-type table, then let the optimizer revise the prompt based solely on that table.
helpful_method: trace-first critique loop
evidence_strength: A
main_sources:
  - docs/paper_notes/paper-protegi-2023.md
  - docs/paper_notes/paper-crispo-2024.md
  - docs/paper_notes/paper-textual-gradients-flawed-metaphor-2025.md
  - docs/github_repo_insight_cards_20260608.md
counterexample_or_limit: Critiques may carry judge bias and must be anchored to examples and metrics; critiques must not be treated as genuine causal explanations.
next_validation: score-only rewrite vs critique-guided rewrite vs trace-guided rewrite.
```

### I-03: Generate Root-Cause Hypotheses Before Rewriting the Prompt

```yaml
insight: Failures in reflective optimizers often stem from a hypothesis space that is too narrow, not from insufficient information.
user_facing_one_liner: Don't ask the model to "fix the prompt" directly — first list possible failure causes and verify each one.
phenomenon: In VISTA, GEPA with a defective seed failed to identify the true root cause and performance fell from 23.81% to 13.50%; after VISTA decoupled hypothesis generation and rewriting it recovered to 87.57%.
mechanism: A single reflector repeatedly attributes failures within a familiar explanation space; verifying multiple hypotheses in parallel can surface structural prompt bugs.
actionable_rule: Generate one candidate prompt per failure hypothesis and validate with a minibatch, rather than producing a final prompt in one shot.
exact_action_to_try: Generate 3 mutually exclusive root-cause hypotheses for the same batch of failed examples — missing rules, missing context, conflicting format constraints — rewrite and score each separately.
helpful_method: root-cause hypothesis gate
evidence_strength: A
main_sources:
  - docs/paper_notes/paper-vista-reflection-dark-2026.md
  - docs/paper_notes/paper-llm-prompt-optimizers-2024.md
counterexample_or_limit: Root-cause boundaries are vague in open-ended writing tasks; multi-hypothesis validation cost may exceed the benefit.
next_validation: one-shot reflection vs K hypotheses + parallel validation.
```

### I-04: Candidate Selection Mechanism Is as Important as Prompt Rewriting

```yaml
insight: Do not adopt the first optimized prompt the model produces; a candidate pool, selection rationale, and rollback point must be maintained.
user_facing_one_liner: Have the model produce multiple versions, use a validation set to choose, and do not let it self-evaluate as optimal.
phenomenon: ProTeGi, GEPA, PromptBreeder, EvoPrompt, SePO, and MASPO all rely on beam, archive, evolutionary search, Pareto, or bandit selection.
mechanism: LLM candidate variance is high; search and selection structures filter bad rewrites, guard against one-off luck, and preserve tradeoffs.
actionable_rule: Each round must save at minimum: seed, candidates, scores, selection_policy, rejected_reason, best_seen, rollback_point.
exact_action_to_try: Generate 5 candidates and select the Pareto candidate across three dimensions — dev score, format error, and prompt length.
helpful_method: candidate ledger + Pareto selector
evidence_strength: A
main_sources:
  - docs/paper_notes/paper-protegi-2023.md
  - docs/paper_notes/paper-gepa-2026.md
  - docs/paper_notes/paper-promptbreeder-2023.md
  - docs/paper_notes/paper-maspo-2026.md
  - docs/github_repo_insight_cards_20260608.md
counterexample_or_limit: Larger search budgets increase the risk of dev overfitting; dev/validation/test stratification is required.
next_validation: one-shot rewrite vs candidate pool + validation selector.
```

### I-05: With a Dev Set, Exemplar Selection Is a First-Class Optimization Variable

```yaml
insight: Exemplar selection often improves or stabilizes performance more than instruction rewriting.
user_facing_one_liner: If you already have labeled examples, don't just use them for scoring — try optimizing which examples the model sees.
phenomenon: "Teach Better or Show Smarter" shows that No IO + optimized exemplars frequently outperforms SoTA IO + no/random exemplars; ERM and DistillPrompt also support exemplar/feedback reuse.
mechanism: Exemplars directly demonstrate decision boundaries and output format, and may be easier for the model to execute than abstract instructions.
actionable_rule: Every APO experiment must compare at minimum: no-example, random-example, optimized-example, instruction + optimized-example.
exact_action_to_try: Fix the instruction, search for 3 exemplars from a candidate pool, and check whether held-out performance exceeds instruction-only.
helpful_method: exemplar optimization baseline
evidence_strength: A
main_sources:
  - docs/paper_notes/paper-teach-better-show-smarter-2024.md
  - docs/paper_notes/paper-erm-memory-2024.md
  - docs/paper_notes/paper-distillprompt-2025.md
counterexample_or_limit: Tight context budgets, skewed exemplar distributions, or exemplar leakage may hurt generalization.
next_validation: instruction-only vs optimized examples vs combined.
```

### I-06: The Optimization Target Has Expanded from a Prompt String to an Artifact Graph

```yaml
insight: In real systems, failures may originate from examples, context, tool schema, agent role, memory, or the evaluator — not just from a single system prompt.
user_facing_one_liner: First identify which component you are changing — do not call the entire context window a "prompt."
phenomenon: AutoPDL optimizes patterns; JTPRO optimizes tool schemas; Prompt Codebooks optimize codebook/routing; multi-agent papers optimize role/round/topology-aware prompts.
mechanism: Different artifacts control different failure modes; mixing them in a single change makes attribution impossible and can bypass safety and format constraints.
actionable_rule: Version records must separate at minimum: task_prompt, examples, context_packaging, tool_schema, agent_role_prompt, evaluator_prompt, selection_policy.
exact_action_to_try: For an optimization run, generate an artifact manifest that declares mutable/frozen fields.
helpful_method: prompt artifact graph
evidence_strength: A/B
main_sources:
  - docs/paper_notes/paper-autopdl-2025.md
  - docs/paper_notes/paper-jtpro-2026.md
  - docs/paper_notes/paper-prompt-codebooks-2026.md
  - docs/industry_practices.md
  - docs/github_repo_insight_cards_20260608.md
counterexample_or_limit: Simple one-off tasks do not require a complete artifact graph; research and production scenarios do.
next_validation: whole-prompt rewrite vs section-local / artifact-local rewrite.
```

### I-07: Longer, More Complex Prompts with More Meta-Instructions Are Not Necessarily Progress

```yaml
insight: Prompt bloat may be a signal of overfitting, not a capability gain.
user_facing_one_liner: A longer new prompt is not necessarily better; check whether it is merely patching training examples.
phenomenon: TextReg, PrefPO, Edit-Level Analysis, and Flawed Textual Gradients all demonstrate that prompt hacking, rule inflation, meta-instructions, and complexification create spurious gains.
mechanism: Optimizers may encode local failures as global rules, or exploit label distribution, judge preferences, and dev set noise.
actionable_rule: When selecting candidates, record prompt length ratio, repetition ratio, edit family, dev-test gap, and OOD/stress delta.
exact_action_to_try: If a candidate prompt's length increases beyond a threshold, require it to identify which failed examples the new rules address and pass a stress split.
helpful_method: prompt hygiene gate
evidence_strength: A
main_sources:
  - docs/paper_notes/paper-textreg-2026.md
  - docs/paper_notes/paper-prefpo-2026.md
  - docs/paper_notes/paper-causal-edit-level-2026.md
  - docs/paper_notes/paper-textual-gradients-flawed-metaphor-2025.md
counterexample_or_limit: Some complex tasks genuinely require more explicit constraints; the criterion is not brevity but necessity, traceability, and resistance to overfitting.
next_validation: performance-only selector vs performance + hygiene selector.
```

### I-08: Memory Is Useful, but Only Filtered Memory Is Useful

```yaml
insight: Remembering more history does not mean becoming smarter; unfiltered feedback memory corrupts optimization.
user_facing_one_liner: An experience store needs provenance, scope of applicability, a quality score, and an expiry policy.
phenomenon: ERM shows that raw feedback memory is insufficient — filtering and selective forgetting are what produce gains; MemAPO distinguishes successful templates from error patterns.
mechanism: Memory can reduce repeated mistakes and lower candidate generation cost, but erroneous experience can negatively transfer across tasks.
actionable_rule: The memory schema must include: success_template, error_pattern, source_task, applicability_condition, retrieval_reason, quality_score, forget_reason.
exact_action_to_try: Do not inject raw conversation history; retrieve only 3-5 validated memory entries that match the current task.
helpful_method: filtered dual memory
evidence_strength: A/B
main_sources:
  - docs/paper_notes/paper-erm-memory-2024.md
  - docs/paper_notes/paper-memapo-2026.md
  - docs/paper_notes/paper-prompt-codebooks-2026.md
  - docs/github_repo_insight_cards_20260608.md
counterexample_or_limit: In highly non-stationary tasks and safety-sensitive tasks, historical experience may expire quickly or leak privacy.
next_validation: no-memory vs raw-memory vs filtered-memory vs filtered+forgetting.
```

### I-09: In Multi-Agent Optimization, Credit Assignment Is the Core Problem — Not More Agents

```yaml
insight: One agent being locally correct may still cause global failure; role, round, and downstream impact must be recorded.
user_facing_one_liner: In a multi-agent system, find the responsible step first, then revise locally — do not rewrite the entire system at once.
phenomenon: MASPO, MAPRO, and Temporal/Structural Credit all address local–global mismatch, topology-aware reward, and updating low-credit components.
mechanism: An agent's output affects downstream agents; local metrics cannot represent final task success.
actionable_rule: Traces must record: role_id, round_id, local_validity, successor_utility, global_outcome, and local_pass_global_fail.
exact_action_to_try: For a failed trace, identify which role/round first introduced an error and allow the optimizer to revise only that block.
helpful_method: multi-agent credit ledger
evidence_strength: A
main_sources:
  - docs/paper_notes/paper-maspo-2026.md
  - docs/paper_notes/paper-mapro-2025.md
  - docs/paper_notes/paper-temporal-structural-credit-mas-2026.md
counterexample_or_limit: If agent interaction is weak, joint optimization cost may not be worthwhile; run a coupling test first.
next_validation: independent agent optimization vs joint reward vs low-credit block update.
```

### I-10: In Tool-Calling Tasks, the Tool Schema Must Be Treated as an Optimizable Artifact

```yaml
insight: tool-use failures commonly originate from tool descriptions and parameter semantics, not from the agent system prompt.
user_facing_one_liner: When a tool call goes wrong, don't only revise the agent instruction — also revise the tool description and parameter rules.
phenomenon: JTPRO improved TSA/SFA/OSR on ToolACE, ETID, and SEAL-Tools by jointly optimizing the global instruction and per-tool schema.
mechanism: The global instruction addresses selection strategy; tool-local schema addresses tool ambiguity and slot/value format.
actionable_rule: Tool evals must be decomposed into Tool Selection Accuracy, Slot Filling Accuracy, and Overall Success Rate.
exact_action_to_try: Construct a tool-call eval for 20 similar tools and test global-only, schema-only, and joint optimization separately.
helpful_method: tool-schema optimization loop
evidence_strength: A
main_sources:
  - docs/paper_notes/paper-jtpro-2026.md
  - docs/industry_practices.md
counterexample_or_limit: When an external API schema cannot be modified, wrapper docs or retrieval context can carry local rules instead.
next_validation: global-prompt-only vs schema-only vs joint global+schema optimization.
```

### I-11: Structured Tasks Are Better Suited for the First Validation Batch

```yaml
insight: Tasks with strict output formats, complex schemas, tool calls, and structured extraction more readily yield interpretable APO evidence.
user_facing_one_liner: Do not choose open-ended essays for the first batch of experiments; start with JSON extraction or tool calls that can be scored objectively.
phenomenon: The positive examples in KG Construction, JTPRO, AutoPDL, and Coin Flip all concentrate on scenarios where schema, format, tool, or latent capability is well-defined.
mechanism: Failure types, format errors, field F1, and tool slots in structured tasks are decomposable, making it easier to localize the effect of a prompt change.
actionable_rule: M1 should prefer structured extraction or tool-call benchmarks over free-text generation.
exact_action_to_try: Use 100–300 `{intent, entities, urgency}` JSON extraction examples as the minimal validation.
helpful_method: structured-task validation demo
evidence_strength: A/B
main_sources:
  - docs/paper_notes/paper-apo-kg-construction-2025.md
  - docs/paper_notes/paper-jtpro-2026.md
  - docs/paper_notes/paper-autopdl-2025.md
  - docs/paper_notes/paper-coin-flip-2026.md
counterexample_or_limit: Open-ended generation tasks remain important but are unsuitable as the first causally clear validations.
next_validation: Run pre-gate, exemplar baseline, critique rewrite, and hygiene gate on a structured extraction task.
```

### I-12: Social Media and Secondary Articles Are Leads, Not Evidence

```yaml
insight: A method appearing repeatedly across multiple platforms indicates popularity, not effectiveness.
user_facing_one_liner: When you see a viral prompt technique, find the original paper, code, data, and failure cases first.
phenomenon: Twitter/X, Medium/Substack, and some blogs extensively repeat GEPA/DSPy/MIPRO methods, but most do not include reproducible experiments.
mechanism: Secondary dissemination amplifies conclusions while losing boundary conditions and version information.
actionable_rule: Secondary sources may only serve as source pointers; before entering a conclusion, they must be traced back to a paper, official documentation, code, cookbook, or this project's experiments.
exact_action_to_try: When reading about a technique, extract: dataset, metric, baseline, model, cost, failure cases; if fields are missing, downgrade to lead status.
helpful_method: source evidence triage
evidence_strength: B
main_sources:
  - docs/source_batches/twitter_web_analysis_20260608.md
  - docs/source_batches/web_search_platform_analysis_20260608.md
  - docs/source_collection_plan.md
counterexample_or_limit: A high-quality engineering blog that includes code, data, and reproducible experiments can be upgraded to stronger evidence.
next_validation: Build a trace-to-primary-source table for high-impact social claims.
```

### I-13: Before Running Costly Search, Try Zero-Cost Deterministic Structural Transforms

```yaml
insight: "Information-order sensitivity" caused by causal attention is a structural failure source in prompt performance that has nothing to do with wording quality; repeating the entire prompt verbatim can fix it without changing any semantics.
user_facing_one_liner: Before running any costly optimizer, try one free transform — repeat the entire prompt verbatim.
phenomenon: In non-reasoning mode, `<QUERY>` → `<QUERY><QUERY>` achieved 47/70 significant wins and 0 significant losses across 7 mainstream models × 10 benchmark configurations (McNemar p<0.1); options-first configurations gained more than question-first; a padding control (padding to equivalent length) showed no gain; on NameIndex, Gemini 2.0 Flash-Lite improved from 21.33% to 97.33%. With step-by-step reasoning enabled, the transform was largely ineffective (5 wins, 1 loss, 22 draws out of 28 groups).
mechanism: In a causal LM, earlier tokens cannot attend to later tokens; after repetition every token in the second copy can attend to the complete first copy, approximating "full second-pass attention" within the prompt. Reasoning models already commonly re-state the problem spontaneously, so the benefit does not compound. Repetition occurs during the parallelizable prefill stage and does not increase output length or latency.
actionable_rule: Include whole-prompt repetition ×2 (×3 for long-context index tasks) in the set of cheap baseline transforms; for any APO method reporting gains in this project's report, first answer "does it beat this zero-intelligence transform?"
exact_action_to_try: Take 50–100 examples and run a three-arm comparison — baseline / repetition×2 / padding — recording accuracy, output format breakage rate, and cost; use the McNemar test.
helpful_method: zero-cost transform baseline (control baseline for HM-01 health check)
evidence_strength: A
main_sources:
  - docs/paper_notes/paper-prompt-repetition-2025.md
counterexample_or_limit: recent-preprint (2025-12), currently a single arXiv-layer piece of evidence; largely ineffective in reasoning mode with 1 significant drop observed; repeating only a part of the prompt (e.g., only the question) yields no gain (Shaier 2024); input cost doubles when billed per token; repeating very long prompts increases prefill latency and may be infeasible; models tested are a 2025-early-generation cohort; newer models may already have internalized the re-statement behavior.
next_validation: Run a three-arm A/B (baseline / ×2 / padding) on a small task drawn from this project with contemporary 2026 models, and use this as the HM-01 control baseline to measure how much net gain each APO method retains after accounting for it.
```

### I-14: The Optimizer and Judge Are Also Components That Must Be Versioned and Can Be Optimized

```yaml
insight: The "prompt responsible for rewriting prompts" and the "prompt responsible for scoring" also determine optimization outcomes; without versioning them, experiments are not reproducible; without ever auditing them, they are hidden ceilings.
user_facing_one_liner: Don't only version the task prompt — the optimizer prompt used to revise prompts and the judge prompt used to score must also be entered into the version ledger.
phenomenon: SePO incorporated the prompt agent's own system prompt into the same evolutionary pipeline, raising the five-task average from Manual-CoT's 71.89 to 76.38; ablating self-improvement dropped it back to 74.94; TextGrad (70.39) and MetaSPO (71.32) with fixed optimizer prompts averaged below Manual-CoT. PromptBreeder's hyper-mutation (co-evolving the mutation prompt) points in the same direction. WPI-10 in web_search and GHI-05 in the GitHub autoresearch ledger independently proposed versioning of the judge prompt / optimizer configuration.
mechanism: A fixed optimizer prompt constrains the space for error analysis and rewriting strategies; judge drift makes score changes unattributable (is it the task prompt's merit or a changed judge?); once optimizer artifacts enter the version ledger and evaluation loop, the optimization capability itself can be audited, trained, and transferred.
actionable_rule: Run records must treat optimizer_prompt_version, judge_prompt_version, and meta_prompt_version as required fields; the judge in the evaluation pipeline is frozen by default just like the test set — any change triggers an independent review and recalibration and requires rerunning all previous scores; optimizing the judge/optimizer itself is done only on the dev set and is physically isolated from the evaluation pipeline.
exact_action_to_try: Add optimizer_prompt / judge_prompt version fields to the run record schema — no separate experiment needed; take effect alongside any P0 experiment.
helpful_method: HM-04 Prompt Artifact Ledger extension (optimizer_prompt / judge_prompt entered into ledger)
evidence_strength: A/B
main_sources:
  - docs/paper_notes/paper-sepo-2026.md
  - docs/paper_notes/paper-promptbreeder-2023.md
  - docs/source_batches/web_search_platform_insight_cards_20260609.md
  - docs/github_repo_insight_cards_20260608.md
counterexample_or_limit: SePO numbers are from a recent-preprint requiring independent replication; "optimizing the judge" and "frozen evaluator to prevent reward hacking" are not in conflict — what is frozen is the judge in the evaluation pipeline, while what is being optimized is the development-phase auxiliary judge; conflating the two is reward hacking; an optimizer prompt that becomes stronger depends on the training tasks and scorer, and behaviors not covered by the metric will not automatically become safer.
next_validation: Write optimizer_prompt / judge_prompt version fields into the run record schema to take effect with P0 experiments; subsequently ablate fixed optimizer prompt vs self-improved optimizer prompt.
```

## Currently Trustworthy Core Conclusions

| id | conclusion | evidence_strength | Main evidence | Boundary |
| --- | --- | --- | --- | --- |
| C-01 | Automatic prompt optimization must be built on dataset, metric, versioning, and rollback; "optimization" without eval is merely rewriting. | A/B | arXiv deep-reads, GitHub source-code audits, industry tool documentation | Concrete tool effectiveness requires re-running on this project's tasks. |
| C-02 | Textual feedback is useful but should not be interpreted as a real gradient. | A | ProTeGi, Flawed Textual Gradients, Scaling Textual Gradients | Does not negate feedback-driven methods; only limits the interpretive framing. |
| C-03 | One-shot rewrite is a weak baseline and should not be the target form of self-evolution. | A/B | ProTeGi, GEPA, PromptBreeder, GitHub compare/rewrite source code | May be sufficient for small tasks but cannot support strong conclusions. |
| C-04 | Exemplar selection, tool schema, context packaging, and agent role may each be more critical than instruction wording. | A/B | Teach Better, JTPRO, AutoPDL, 12-factor agents, industry docs | First validation batch must control variables. |
| C-05 | Prompt bloat, dev overfitting, judge hacking, and memory pollution are the main risks in prompt self-evolution. | A/B | TextReg, PrefPO, Coin Flip, ERM, industry eval docs | Risk metrics need to be hardened into the experiment runner. |
| C-06 | The GitHub channel is better suited for distilling engineering structure and governance methods, not for proving effectiveness in isolation. | B | core4 source-code audits and insight cards | The "unsuitable for proving effectiveness" part is partly due to limited recall (no token, smoke-discovery of 8 queries) + core4-only audit — the canonical optimizer repos (gepa / PromptWizard / promptomatix) have not yet been audited; can be upgraded after supplementary audit + this project's minimal experiments; see "Channel Coverage and Known Bias" in `github_repo_channel_synthesis_20260609.md`. |

## Helpful Method Candidates

### HM-01: Pre-Optimization Gate

```yaml
name: Pre-Optimization Gate
insight_supported: I-01, I-11
problem: Avoid wasting complex optimizer cost on tasks with no headroom.
recommended_when: Before running any automatic prompt optimizer.
not_recommended_when: One-off low-risk prompt tweaks, or when the user only needs manual rewrite suggestions.
required_inputs:
  - 20-50 held-out examples
  - zero-shot prompt
  - manual baseline prompt
  - 10-20 candidate prompts
implementation_steps:
  - Run zero-shot and manual baseline.
  - Generate or hand-write 10-20 candidates.
  - Evaluate all candidates with the same scorer.
  - Compute best gain, score spread, format error, and cost.
  - If best gain does not exceed the noise threshold, stop APO and return to task definition or eval.
evaluation_metrics:
  - main_score
  - best_gain_over_zero_shot
  - score_spread
  - format_error_rate
  - token_cost
expected_benefit: Early cutoff on tasks with no improvement headroom.
cost_and_latency: Low; typically less than the cost of a full optimizer run.
risks: Small samples may misjudge; thresholds must not be applied rigidly across tasks.
rollback_plan: Retain the zero-shot/manual baseline; do not accept automatic candidates.
evidence: docs/paper_notes/paper-coin-flip-2026.md
next_experiment: Run one gate each on a structured extraction task and an open-generation task.
```

### HM-02: Trace-First Critique Rewrite

```yaml
name: Trace-First Critique Rewrite
insight_supported: I-02, I-03, I-04
problem: Having the LLM revise the prompt directly is not auditable and prone to misidentifying root causes.
recommended_when: Tasks with failed examples, error types, or agent/tool traces.
not_recommended_when: Subjective writing tasks with no verifiable output or scorer.
required_inputs:
  - baseline prompt
  - failed examples
  - gold/reference or judge rubric
  - trace or intermediate outputs
implementation_steps:
  - Generate error_type and critique from failed examples.
  - Generate 2-3 failure hypotheses.
  - Generate one candidate prompt per hypothesis.
  - Select the candidate using dev/validation.
  - Record prompt diff, selection rationale, and rollback point.
evaluation_metrics:
  - main_score
  - failure_type_delta
  - validation_score
  - prompt_length_ratio
  - rejected_reason
expected_benefit: Improves rewrite interpretability and reduces the randomness of one-shot rewriting.
cost_and_latency: Moderate; requires additional critique and candidate evaluation calls.
risks: Critique/judge bias; too many hypotheses causing budget inflation.
rollback_plan: Retain the best_seen prompt; roll back if validation score decreases.
evidence: docs/paper_notes/paper-protegi-2023.md, docs/paper_notes/paper-vista-reflection-dark-2026.md
next_experiment: Compare direct rewrite vs trace-first rewrite on the same structured extraction task.
```

### HM-03: Exemplar Optimization Baseline

```yaml
name: Exemplar Optimization Baseline
insight_supported: I-05
problem: Prevent overestimating the value of instruction rewriting.
recommended_when: A labeled dev set is available and context length allows 3-5 examples.
not_recommended_when: Very tight context, examples may leak sensitive information, or the task strongly depends on zero-shot performance.
required_inputs:
  - exemplar candidate pool
  - fixed instruction
  - dev split
  - hidden/test split
implementation_steps:
  - Fix the instruction.
  - Compare no-example, random examples, and optimized examples.
  - Then compare instruction optimization + optimized examples.
  - Report final generalization on the hidden/test split only.
evaluation_metrics:
  - main_score
  - dev_test_gap
  - context_tokens
  - rare_label_score
  - format_error_rate
expected_benefit: Identify whether gains come from exemplars rather than instruction wording.
cost_and_latency: Moderate; depends on exemplar search budget.
risks: Exemplar selection overfitting; uneven exemplar coverage; increased cost.
rollback_plan: If test/OOD performance drops, revert to no-example or random-example baseline.
evidence: docs/paper_notes/paper-teach-better-show-smarter-2024.md
next_experiment: Compare instruction-only vs exemplar-only on a structured extraction task.
```

### HM-04: Prompt Artifact Ledger

```yaml
name: Prompt Artifact Ledger
insight_supported: I-04, I-06, I-07, I-08, I-10
problem: Mixing prompt, examples, tool schema, context, and evaluator into the same change makes attribution impossible and rollback infeasible.
recommended_when: Any research-grade or production-grade prompt optimization.
not_recommended_when: Temporary one-off chat.
required_inputs:
  - artifact manifest
  - prompt diff
  - evaluation run
  - cost report
implementation_steps:
  - Assign a version number to each artifact.
  - Annotate as mutable/frozen.
  - Record score, failed examples, cost, and accept/reject rationale for each candidate.
  - Save rollback point.
evaluation_metrics:
  - reproducibility
  - rollback_time
  - source_traceability
  - frozen_section_violation
expected_benefit: Makes prompt evolution auditable, reproducible, and rollback-capable.
cost_and_latency: Low to moderate; mainly the cost of record-keeping.
risks: Too many fields slow down execution; the first version should keep fields minimal.
rollback_plan: Restore the previous accepted artifact from the ledger.
evidence: docs/github_repo_insight_cards_20260608.md, docs/industry_practices.md
next_experiment: Have the first experiment runner output `prompt_runs.jsonl`.
```

## Anti-Patterns and Risk Boundaries

| anti-pattern | Why it is dangerous | Corresponding safeguard | Evidence |
| --- | --- | --- | --- |
| Asking the model to "optimize the prompt" directly | No goal, no evaluation, no rollback; output is only polishing or random rewriting. | HM-01, HM-02 | ProTeGi, VISTA, industry eval docs |
| Looking only at average scores | Minority class, format errors, and safety boundaries may deteriorate. | Stratified metrics, stress split | TextReg, PrefPO, Coin Flip |
| Letting the prompt keep growing longer | May be patches for training examples and conflicting rules. | hygiene gate | TextReg, Edit-Level Analysis |
| Allowing the optimizer to modify the evaluator or test cases | Direct reward hacking. | frozen evaluator/data | GitHub autoresearch audit |
| Appending raw memory without bounds | Inherits bad feedback, risks privacy leakage, cross-task pollution. | filtered memory + forgetting | ERM, MemAPO, ECC |
| Using social media popularity as evidence | Popularity indicates spread, not effectiveness. | source evidence triage | source_batches |
| Rewriting multiple agents together | Impossible to determine which role/round caused the change. | credit ledger | MASPO, MAPRO |
| Only modifying the system prompt for tool-calling tasks | tool schema/slot errors cannot be fixed this way. | JTPRO-style schema optimization | JTPRO |

## First Validation Batch Priorities

| priority | validation/demo | validates | Minimal task | What both success and failure can produce |
| --- | --- | --- | --- | --- |
| P0 | Structured extraction pre-gate | I-01, I-11, I-13 (control baseline), HM-01 | 100-300 JSON extraction examples | Determines whether there is optimization headroom and calibrates noise floor; run I-13 zero-cost transform in parallel as control baseline during the health check. |
| P0 | Exemplar baseline | I-05, HM-03 | Same extraction task | Prevents mistaking exemplar selection gains for instruction rewrite gains. |
| P1 | Direct rewrite vs trace-first rewrite | I-02, I-03, HM-02 | Extraction/classification task with clear failure examples | Determines whether critique/hypothesis improves held-out performance. |
| P1 | Performance-only vs hygiene selector | I-07 | Same candidate pool | Determines whether the prompt bloat safeguard reduces spurious gains. |
| P2 | Tool schema mini benchmark | I-10 | 20-50 similar tools | Determines whether schema-only/joint outperforms global prompt-only. |
| P2 | Filtered memory | I-08 | Two similar tasks + one heterogeneous task | Determines whether memory reduces cost or causes negative transfer. |

## Gaps Before Entering the Final Report

- Each A/B-grade insight needs to be traced to 2-3 of its strongest sources rather than piling in every reference.
- At least 1 HM needs a minimal validation or demonstration record from this project before it can earn grade-C project evidence.
- Minimum fields for `prompt_runs` / `artifact ledger` must be defined so that helpful methods do not remain at the level of slogans.
- For 2026 new arXiv papers, the final report should annotate `recent-preprint` to avoid over-reliance.
- Industry tool documentation needs version numbers and access dates, especially for hosted prompt optimizer products that may have migrated or been deprecated.
