# GitHub Repository Candidate Insight Evidence Cards: 2026-06-08

2026-06-09 supplement: Added a "plain-language overview" section for translating source-audit insights into concrete, actionable methods; original GHI evidence cards are retained.

2026-06-09 content update: GitHub channel conclusions, helpful methods, anti-patterns, and minimum-verification candidates for the final report have been consolidated in [GitHub Channel Insight Synthesis](github_repo_channel_synthesis_20260609.md). This file continues to serve as the detailed evidence cards for GHI-01 through GHI-12.

This file extracts candidate insights from the core4 source audit. It is not a final-report conclusion; each card retains a source_id, commit, evidence path, evidence level, and convertible-to-experiment approach.

Evidence levels follow the [GitHub Repository Source Audit Workflow](github_repo_source_audit_workflow_20260608.md):

- L1: Read README / docs after fixing a commit.
- L2: Located source code, configs, tests, or example paths after fixing a commit.
- L3: Able to run tests, examples, or a minimal reproduction experiment locally.
- L4: Cross-validated across repositories, papers, or this project's own experiments.

Current cards are primarily L2 and should not be written up as "methods proven effective." They are better suited as a candidate pool for subsequent experiment design, final-report hypotheses, and rule-of-thumb candidates.

## Quick Summary

The five strongest direct takeaways from the first round of source audits are:

1. Prompt optimization should not simply generate a new prompt; a more robust closed loop is "comparative evaluation → evidence compression → evaluation-based rewriting."
2. The evaluator / data / harness must be isolated from the optimizable object; otherwise self-evolution very easily corrupts the metric itself.
3. Calibration samples should deliberately cover overfitting, schema drift, single-run luck, semantic instability, and high-risk conservative boundary cases.
4. Both prompts and context should be treated as first-class engineering objects that are testable, versionable, and rollback-capable — not as things that only exist inside framework black boxes or UI configs.
5. The useful patterns for an agent harness are trace, verifier, candidate decision, and playbook promotion — not vague claims of having a memory / verification loop.

## Plain-Language Overview

The GitHub channel is not well-suited for directly proving that "a given prompt technique will definitely raise scores," but it is well-suited for providing actionable workflows. The cards below should serve as "actionable methods" in the final report and HTML pages; detailed source-code evidence remains in the GHI cards that follow.

| Specific insight | What an ordinary user can do | Why it helps | Evidence boundary |
| --- | --- | --- | --- |
| Do not ask the model to simply "optimize my prompt for me" — first have it compare two outputs. | Provide the baseline prompt and the failing output, have the model judge where it goes wrong; then pass the judgment summary to the rewrite prompt. | The compare step leaves an auditable rationale and prevents the optimization process from becoming a black-box rewrite. | Source-code structure evidence is strong; effectiveness still needs validation through this project's experiments. |
| Divide the prompt into sections for task, input, output format, and candidate output. | Use a JSON payload or clear delimiters to wrap `instruction`, `input`, `candidate_output`, and `rubric`. | Reduces the risk of the model conflating rules, data, and the answer under evaluation. | Derived from a structured compare implementation at a fixed commit. |
| The validation set must include "adversarial examples that would fool the current prompt." | Add cases covering missing fields, format drift, paraphrase rewrites, high-risk conservative boundaries, and sample trigger words. | Optimizers most easily learn local patches; adversarial examples expose overfitting. | Source code / docs contain calibration design; needs this project's task to confirm. |
| Self-evolution may only modify the designated object — not the exam paper. | Only allow changes to `candidate_prompt.md`; prohibit changes to `eval_cases`, the grader, and success criteria. | Otherwise the system will loosen the evaluation rules and produce spurious gains. | Engineering constraint migrated from the autoresearch loop. |
| Every prompt candidate should have a ledger. | Record the prompt diff, source, score, cost, failure cases, accept/reject rationale, and rollback point. | Without a ledger it is impossible to review "why this lesson is worth keeping." | Engineering governance evidence is strong; fields need to be solidified through this project's experiments. |
| Prompt optimization is not just about changing the system prompt. | For agent / RAG tasks, also record context, history compression, tool result format, and output schema. | Many failures arise because the model saw the wrong information, not because the instructions were poorly written. | GitHub channel provides boundary clues; specific variable priorities require experiments. |

## Card Index

| id | Candidate insight | Primary source | Evidence level | Convertible-to-experiment priority |
| --- | --- | --- | --- | --- |
| GHI-01 | Splitting prompt optimization into compare / synthesis / rewrite is more auditable than directly asking the model to "fix the prompt." | `repo-linshenkx-prompt-optimizer` | L2 | high |
| GHI-02 | Evaluation protocols should use structured payloads and a JSON contract to reduce boundary confusion caused by Markdown concatenation. | `repo-linshenkx-prompt-optimizer` | L2 | high |
| GHI-03 | Calibration samples should prioritize attacking overfitting, schema drift, and stability rather than only validating the happy path. | `repo-linshenkx-prompt-optimizer` | L2 | high |
| GHI-04 | The core safeguard of a self-evolving loop is "only the target object may be modified; the evaluator / data may not." | `repo-karpathy-autoresearch` | L2 | high |
| GHI-05 | Every candidate change should have a ledger of commit, metric, resource, status, and a natural-language description. | `repo-karpathy-autoresearch` | L2 | high |
| GHI-06 | When accepting a candidate change, look beyond the metric and also record complexity gains and failure-handling strategy. | `repo-karpathy-autoresearch` | L2 | medium |
| GHI-07 | Prompts should be owned as code assets: readable, testable, versionable, and replaceable for framework black boxes. | `repo-humanlayer-12-factor-agents` | L1/L2 | high |
| GHI-08 | The scope of prompt optimization should extend to context packaging, including RAG, history, tool calls, memory, and output schema. | `repo-humanlayer-12-factor-agents` | L1/L2 | high |
| GHI-09 | Memory / context persistence must have boundaries: local-first, length caps, profile gating, and opt-out. | `repo-affaan-m-ecc` | L2 | medium |
| GHI-10 | Agent experience consolidation should save scenario, trace, verifier result, report, and candidate playbook. | `repo-affaan-m-ecc` | L2 | medium |
| GHI-11 | "Having tests" only demonstrates auditability — it does not mean the method is effective; keep test entry points and effectiveness claims separate. | core4 synthesis | L2 | high |
| GHI-12 | The primary value of the GitHub channel is engineering structure and governance patterns; direct evidence proving prompt optimizer effectiveness is limited. | core4 synthesis | L2 | high |

## Detailed Cards

### GHI-01: Compare / Synthesis / Rewrite Three-Stage Pipeline Is More Auditable Than Directly Editing the Prompt

- source_id: `repo-linshenkx-prompt-optimizer`
- commit: `d7cde6c2fc5c56a579d803d485ad170788a4141e`
- Observation: This repository does not have a single "prompt rewrite" entry point; instead it has a layered implementation of a structured compare-pair judge, synthesis, and rewrite-from-evaluation. The compare stage produces intermediate judgments, the synthesis stage compresses the evidence, and the rewrite stage consumes the upstream conclusions.
- Evidence paths:
  - `local_sources/raw/github_repo_clones/repo-linshenkx-prompt-optimizer/packages/core/src/services/evaluation/structured-compare-prompts.ts`
  - `local_sources/raw/github_repo_clones/repo-linshenkx-prompt-optimizer/packages/core/src/services/template/default-templates/evaluation-structured-compare/`
  - `local_sources/raw/github_repo_clones/repo-linshenkx-prompt-optimizer/packages/core/src/services/evaluation/rewrite-from-evaluation.ts`
- Candidate method: Future experiments should not simply do "input bad prompt → output better prompt"; they should record evaluator output, evidence summary, rewrite reason, and prompt diff.
- Convertible to experiment: On the same batch of failure samples, compare "direct rewrite" versus "compare → rewrite" in terms of held-out scores, schema drift, refusal boundary, and manual review cost.
- Evidence level: L2. Source code structure is present; effect has not yet been reproduced in this project.

### GHI-02: Structured Payload and JSON Contract Are Boundary-Control Tools for the Prompt Optimization Closed Loop

- source_id: `repo-linshenkx-prompt-optimizer`
- commit: `d7cde6c2fc5c56a579d803d485ad170788a4141e`
- Observation: The repository's compare / rewrite documentation shows the protocol layer migrating from Markdown concatenation to "rule description + JSON payload"; the source code also contains a compare JSON contract, structured mode, and compare metadata.
- Evidence paths:
  - `local_sources/raw/github_repo_clones/repo-linshenkx-prompt-optimizer/docs/workspace/compare-evaluation-analysis/README.md:28`
  - `local_sources/raw/github_repo_clones/repo-linshenkx-prompt-optimizer/packages/core/src/services/evaluation/types.ts`
  - `local_sources/raw/github_repo_clones/repo-linshenkx-prompt-optimizer/packages/core/src/services/evaluation/service.ts`
- Candidate method: The evaluator prompt of a prompt optimizer should explicitly separate instruction, payload, schema contract, reference output, and candidate output to prevent the model from merging context into a single freely interpretable blob.
- Convertible to experiment: Construct a Markdown version and a JSON payload version of the same comparison task; test field renaming, wrapper drift, JSON-only boundary, and judge parse failure rate.
- Evidence level: L2. Protocol migration and structural fields are present; effectiveness still requires validation in this project.

### GHI-03: Calibration Samples Should Actively Test Overfitting, Schema Drift, and Semantic Stability

- source_id: `repo-linshenkx-prompt-optimizer`
- commit: `d7cde6c2fc5c56a579d803d485ad170788a4141e`
- Observation: The structured compare calibration does not merely test that functionality runs; it covers high-risk overfitting, schema / contract drift, synonym-flat, replica semantic instability, and real boundary-control scenarios.
- Evidence paths:
  - `local_sources/raw/github_repo_clones/repo-linshenkx-prompt-optimizer/docs/workspace/compare-evaluation-analysis/structured-compare-calibration/README.md`
  - `local_sources/raw/github_repo_clones/repo-linshenkx-prompt-optimizer/docs/workspace/compare-evaluation-analysis/real-api-samples/`
- Candidate method: The validation set for a prompt optimizer should include at least negative examples that "fool the current samples but harm generality," not only measure improvement on target examples.
- Convertible to experiment: Add 4 categories of adversarial calibration cases to the first version of this project's benchmark: schema drift, latent trigger overfit, single-run luck, and high-risk conservative boundary.
- Evidence level: L2. Calibration design is present; its generalization effect needs to be reproduced in this project.

### GHI-04: A Self-Evolving Loop Must Freeze the Evaluator / Data / Harness

- source_id: `repo-karpathy-autoresearch`
- commit: `228791fb499afffb54b46200aca536f79142f117`
- Observation: `program.md` explicitly constrains the agent to only modify `train.py` and prohibits modification of `prepare.py`, dependencies, or the evaluation harness; `prepare.py` provides fixed metrics.
- Evidence paths:
  - `local_sources/raw/github_repo_clones/repo-karpathy-autoresearch/program.md:13`
  - `local_sources/raw/github_repo_clones/repo-karpathy-autoresearch/program.md:26`
  - `local_sources/raw/github_repo_clones/repo-karpathy-autoresearch/program.md:31`
  - `local_sources/raw/github_repo_clones/repo-karpathy-autoresearch/prepare.py`
- Candidate method: In prompt self-evolution experiments, the mutable object may be only one of: prompt / context / tool policy; eval data, grader, success criteria, and logging schema must be frozen.
- Convertible to experiment: Implement a prompt-only optimizer where the model may only edit `candidate_prompt.md` and may not modify `eval_cases.jsonl`, the grader, or the runner; compare against a setting that allows modifying the evaluator to check whether reward hacking occurs.
- Evidence level: L2. Structural closed loop is clear; migrating to a prompt task remains an open experimental question for this project.

### GHI-05: Candidate Changes Need a Ledger of commit + metric + resource + status + description

- source_id: `repo-karpathy-autoresearch`
- commit: `228791fb499afffb54b46200aca536f79142f117`
- Observation: `program.md` requires each experiment to be written into `results.tsv` with fields covering commit, metric, memory, status, and a natural-language description; failures and crashes also have a recording format.
- Evidence paths:
  - `local_sources/raw/github_repo_clones/repo-karpathy-autoresearch/program.md:64`
  - `local_sources/raw/github_repo_clones/repo-karpathy-autoresearch/program.md:71`
  - `local_sources/raw/github_repo_clones/repo-karpathy-autoresearch/program.md:77`
- Candidate method: Every candidate version of a prompt optimizer should record prompt diff, candidate source, eval score, cost, latency, status, failure cases, and rollback point.
- Convertible to experiment: Add a `prompt_runs.tsv` or JSONL ledger to the first version of this project's optimizer runner, starting with three candidate categories: manual prompt, direct rewrite, and compare rewrite.
- Evidence level: L2. Ledger specification is present; prompt version fields need to be defined by this project.

### GHI-06: Accepting a Candidate Change Should Explicitly Consider Complexity and Failure Handling

- source_id: `repo-karpathy-autoresearch`
- commit: `228791fb499afffb54b46200aca536f79142f117`
- Observation: `program.md` does not only require the metric to improve; it also includes a simplicity criterion, timeout handling, crash handling, and discard / revert rules.
- Evidence paths:
  - `local_sources/raw/github_repo_clones/repo-karpathy-autoresearch/program.md:37`
  - `local_sources/raw/github_repo_clones/repo-karpathy-autoresearch/program.md:96`
  - `local_sources/raw/github_repo_clones/repo-karpathy-autoresearch/program.md:103`
  - `local_sources/raw/github_repo_clones/repo-karpathy-autoresearch/program.md:108`
- Candidate method: Prompt optimization cannot consider only the score; if a new prompt is longer, more brittle, more dependent on special-case samples, or harder to audit, the complexity cost should be factored into the decision.
- Convertible to experiment: Add `prompt_length_delta`, `rule_count_delta`, `manual_review_risk`, and `rollback_reason` fields to the runner.
- Evidence level: L2. Rules are present; how to quantify complexity metrics still needs to be defined by this project.

### GHI-07: Prompts Should Be Owned as First-Class Code Assets, Not Outsourced to Framework Black Boxes

- source_id: `repo-humanlayer-12-factor-agents`
- commit: `d20c728368bf9c189d6d7aab704744decb6ec0cc`
- Observation: Factor 02 explicitly argues for treating prompts as first-class code to enable control, testing / eval, iteration, and transparency; the repository also includes a create-agent template and BAML examples.
- Evidence paths:
  - `local_sources/raw/github_repo_clones/repo-humanlayer-12-factor-agents/content/factor-02-own-your-prompts.md:33`
  - `local_sources/raw/github_repo_clones/repo-humanlayer-12-factor-agents/content/factor-02-own-your-prompts.md:77`
  - `local_sources/raw/github_repo_clones/repo-humanlayer-12-factor-agents/packages/create-12-factor-agent/template/`
- Candidate method: In this project's final solution, prompts should not exist only in a UI or platform prompt hub; at minimum, the core system prompt, evaluation prompt, and rewrite prompt should be checked into the version repository or exported as a versionable artifact.
- Convertible to experiment: Compare "prompt text is invisible / not diffable" against "prompt file + prompt diff ledger" in terms of review cost and rollback speed.
- Evidence level: L1/L2. Primarily engineering-principle and template evidence, not an effectiveness proof.

### GHI-08: The Scope of Prompt Optimization Should Extend to Context Packaging

- source_id: `repo-humanlayer-12-factor-agents`
- commit: `d20c728368bf9c189d6d7aab704744decb6ec0cc`
- Observation: Factor 03 decomposes context into prompt / instructions, RAG documents, past state / tool calls / history, memory, and structured output instructions, and emphasizes that the context format can be customized.
- Evidence paths:
  - `local_sources/raw/github_repo_clones/repo-humanlayer-12-factor-agents/content/factor-03-own-your-context-window.md:14`
  - `local_sources/raw/github_repo_clones/repo-humanlayer-12-factor-agents/content/factor-03-own-your-context-window.md:71`
  - `local_sources/raw/github_repo_clones/repo-humanlayer-12-factor-agents/content/factor-03-own-your-context-window.md:227`
- Candidate method: Going forward, "prompt optimization" should not be narrowly defined as "editing system prompt copy"; for agent tasks, context selection, history compression, tool result formatting, and output schema should also be treated as optimization targets.
- Convertible to experiment: On the same agent task, compare: changing only the system prompt vs. changing only the context packing vs. changing both simultaneously — measure success rate, token cost, tool misuse, and auditability.
- Evidence level: L1/L2. Principles are clear; experiments are needed to validate which type of context change is most effective.

### GHI-09: Memory / Context Persistence Must Have Boundaries and an Off Switch

- source_id: `repo-affaan-m-ecc`
- commit: `90dfd9505dc860714cf3cc8216ad7bbb96d93365`
- Observation: ECC's memory-persistence documentation treats session start, pre-compact, session end, tool observation, and activity tracking as lifecycle hooks, and records local-first storage, length caps, opt-out, and profile gating.
- Evidence paths:
  - `local_sources/raw/github_repo_clones/repo-affaan-m-ecc/hooks/memory-persistence/README.md`
  - `local_sources/raw/github_repo_clones/repo-affaan-m-ecc/scripts/hooks/session-start.js`
  - `local_sources/raw/github_repo_clones/repo-affaan-m-ecc/scripts/hooks/pre-compact.js`
  - `local_sources/raw/github_repo_clones/repo-affaan-m-ecc/tests/hooks/observer-memory.test.js`
- Candidate method: Memory in prompt self-evolution should not be appended without limit; each memory entry needs a source, scope, expiry policy, and an off switch.
- Convertible to experiment: Compare no-memory, bounded-summary-memory, and raw-history-memory across three settings in terms of prompt drift, token cost, and error inheritance.
- Evidence level: L2. Hook and test paths are present; actual effectiveness requires running and verifying.

### GHI-10: Agent Experience Consolidation Should Save Scenario, Trace, Verifier Result, Report, and Playbook

- source_id: `repo-affaan-m-ecc`
- commit: `90dfd9505dc860714cf3cc8216ad7bbb96d93365`
- Observation: `examples/evaluator-rag-prototype/` saves scenario, trace, verifier-result, report, and candidate-playbook; verifier results distinguish accepted from rejected candidates, and only one candidate is promoted.
- Evidence paths:
  - `local_sources/raw/github_repo_clones/repo-affaan-m-ecc/examples/evaluator-rag-prototype/scenario.json`
  - `local_sources/raw/github_repo_clones/repo-affaan-m-ecc/examples/evaluator-rag-prototype/trace.json`
  - `local_sources/raw/github_repo_clones/repo-affaan-m-ecc/examples/evaluator-rag-prototype/verifier-result.json`
  - `local_sources/raw/github_repo_clones/repo-affaan-m-ecc/examples/evaluator-rag-prototype/report.json`
  - `local_sources/raw/github_repo_clones/repo-affaan-m-ecc/examples/evaluator-rag-prototype/candidate-playbook.md`
- Candidate method: Lessons learned after prompt optimization should not be consolidated only as a "new prompt"; retain why it was accepted, why it was rejected, source evidence, verification commands, and a reusable playbook.
- Convertible to experiment: Generate `scenario.json`, `trace.jsonl`, `verifier_result.json`, and `candidate_prompt.md` for each optimizer run in this project.
- Evidence level: L2. Example artifacts are present; not proof of general effectiveness.

### GHI-11: "Having Tests" Does Not Mean "The Method Is Effective," but It Does Improve Auditability

- source_id: core4 synthesis, with emphasis on `repo-affaan-m-ecc` and `repo-linshenkx-prompt-optimizer`
- commits:
  - `repo-affaan-m-ecc`: `90dfd9505dc860714cf3cc8216ad7bbb96d93365`
  - `repo-linshenkx-prompt-optimizer`: `d7cde6c2fc5c56a579d803d485ad170788a4141e`
- Observation: Both repositories have a substantial test / example surface, but these paths only demonstrate that there are auditable entry points — they do not demonstrate that the method claims of the prompt optimizer or agent harness have been validated.
- Evidence paths:
  - `local_sources/raw/github_repo_clones/repo-affaan-m-ecc/package.json:348`
  - `local_sources/raw/github_repo_clones/repo-affaan-m-ecc/tests/`
  - `local_sources/raw/github_repo_clones/repo-linshenkx-prompt-optimizer/tests/e2e/`
  - `docs/github_repo_audit_notes/repo-affaan-m-ecc.md`
  - `docs/github_repo_audit_notes/repo-linshenkx-prompt-optimizer.md`
- Candidate method: When analyzing a GitHub repository, "test coverage of engineering completeness" and "experimental results proving the method effective" should be recorded separately.
- Convertible to experiment: Do a smoke run of the runnable test entry points in core4; label which are unit / e2e, and which can genuinely evaluate optimizer behavior.
- Evidence level: L2. Test paths are present; whether they pass and whether they cover key behaviors still requires running.

### GHI-12: The GitHub Channel Is Better Suited for Extracting Engineering Structure Than for Drawing Effectiveness Conclusions Directly

- source_id: core4 synthesis
- Observation: In core4, only `linshenkx/prompt-optimizer` directly belongs to prompt optimizers; `karpathy/autoresearch` is a structural reference for a self-evolving experiment loop; `humanlayer/12-factor-agents` covers agent / context engineering principles; `affaan-m/ECC` provides clues about the harness and memory / verifier. All of these can contribute to method design, but none alone can prove that "prompt self-evolution is effective."
- Coverage boundary (2026-06-10 supplement): This judgment is based on a single constrained-recall discovery (no tokens, 8 queries) + core4 audit; canonical optimizer repositories such as `gepa-ai/gepa`, `microsoft/PromptWizard`, `SalesforceAIResearch/promptomatix`, and `Eladlev/AutoPrompt` have not yet been audited, so "sparse effectiveness evidence" cannot rule out insufficient coverage as the cause. See [Channel Insight Synthesis · Channel Coverage and Known Biases](github_repo_channel_synthesis_20260609.md).
- Evidence paths:
  - [GitHub Repository Source Audit Workflow](github_repo_source_audit_workflow_20260608.md)
  - [repo-linshenkx-prompt-optimizer audit note](github_repo_audit_notes/repo-linshenkx-prompt-optimizer.md)
  - [repo-karpathy-autoresearch audit note](github_repo_audit_notes/repo-karpathy-autoresearch.md)
  - [repo-humanlayer-12-factor-agents audit note](github_repo_audit_notes/repo-humanlayer-12-factor-agents.md)
  - [repo-affaan-m-ecc audit note](github_repo_audit_notes/repo-affaan-m-ecc.md)
- Candidate method: When the final report cites the GitHub channel, prioritize writing "reusable engineering methods" and "experiment design constraints," and reserve effectiveness-class conclusions for papers, official benchmarks, or this project's own experiments.
- Convertible to experiment: Combine GHI-01, GHI-04, GHI-05, and GHI-08 into the first version of a minimum prompt self-evolution harness.
- Evidence level: L2. A synthesis judgment derived from fixed-commit source-code observations; upgrading to L4 requires cross-validation with paper deep-reads and this project's own experiments.

## First Batch of Experiment Candidates

The highest-priority minimum experiments can be frozen in the following order:

1. **Frozen Evaluator Prompt Loop**: Allow optimization of `candidate_prompt.md` only; freeze eval cases, grader, runner, and ledger schema. Validates GHI-04 / GHI-05.
2. **Direct Rewrite vs Compare Rewrite**: Compare direct rewriting against the compare / synthesis / rewrite three-stage pipeline on the same failure samples. Validates GHI-01 / GHI-03.
3. **Markdown vs JSON Payload Judge**: Compare Markdown concatenation against a structured payload using the same compare prompt. Validates GHI-02.
4. **Prompt-only vs Context-packaging**: On the same agent task, change the system prompt separately versus changing the context format. Validates GHI-08.

For the first batch, directly replicating ECC or the full UI tool is not recommended. A more controllable path is to first borrow the structural fields of ledger, trace, verifier, and bounded memory.
