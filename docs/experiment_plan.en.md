# Experiment Plan

Last updated: 2026-06-08

Status: Candidate-validation design — not entering full benchmark implementation yet. Complete M0 source collection, insight distillation, core conclusions, and helpful method candidates first, then select 1–2 minimal experiments to verify or demo key insights/methods.

## M0: Source Collection and Survey Freeze

Before implementing any full benchmark harness or automated optimization scripts, complete paper, industry experience, engineering framework, and failure case collection per the [Source Collection Plan](source_collection_plan.md), and produce insight / conclusion / helpful method candidates.

M0 completion criteria:

- Collect 50+ candidate sources, recording links, publication dates, types, relevance, and status.
- Complete structured notes for 12–15 core papers or frameworks.
- Organize 10–15 industry practice, tool documentation, or engineering experience sources.
- Produce a frontier-state map and method taxonomy covering candidate generation, candidate selection, feedback signals, optimization targets, memory mechanisms, and governance mechanisms.
- Output an insight / conclusion / helpful method candidate list.
- Output 2–3 reusable methods or recommendations.
- Output 1–2 minimal validation/demo candidates, each specifying the insight or method to validate, the objective, assumptions, input samples, model, evaluation approach, success criteria, and key risks.

Until M0 is complete, do not freeze long-term tasks, datasets, or scorers; however, a small-scale preliminary validation may be designed for key insights or methods identified in the report.

## Preliminary Validation Objective

Build a small, reproducible preliminary validation to observe whether key insights, conclusions, or helpful methods show supporting evidence, while recording cost, failure modes, and overfitting risk.

Preliminary experiments do not bear the burden of "proving a method is effective long-term" — they are used only to support, refine, or demo insights and reusable methods in the final report.

The current validation candidates use the [Insight / Conclusion / Helpful Method Candidate Catalog](insight_method_catalog_20260609.md) as the structured entry point; the reader-facing equivalent is the [Reader Insight Handbook](insight_handbook_20260609.md), whose "First Batch Minimal Validations" table is aligned with the P0–P2 priorities below. Experiments prioritize the following method cards rather than pursuing full benchmark coverage:

- HM-01: Pre-Optimization Gate — validate whether exploitable headroom exists before automated optimization.
- HM-02: Trace-First Critique Rewrite — validate whether failure trace / root-cause hypotheses outperform direct rewrite.
- HM-03: Exemplar Optimization Baseline — prevent exemplar selection gains from being misattributed to instruction rewrite.
- HM-04: Prompt Artifact Ledger — ensure prompt, examples, tool schema, context, and evaluator are traceable and have rollback points.

## Experiment Selection Threshold

Only candidates meeting all of the following criteria enter the experiment plan:

- Clearly maps to an insight, conclusion, or helpful method.
- Can verify one key boundary of that insight via a minimal task.
- Results — whether success or failure — can be fed back into experience summaries, anti-patterns, or a method playbook.
- Does not require implementing a full benchmark harness for demonstration.

## Experiment Discipline

Experiment design follows the [Project Principles](project_principles.md). Each experiment round defaults to documenting objective, assumptions, variables, metrics, and success criteria before running optimization.

- Each experiment should change only one primary variable at a time: prompt wording, few-shot examples, model parameters, or scorer.
- If multiple variables must change simultaneously, label that round a multi-factor experiment; conclusions must not claim single-variable causation.
- Every conclusion must be traceable to run records, metrics, sample outputs, or failure cases.
- Every experiment must record which insight/method it validates, and how the result changes the credibility of that insight or method.
- Experiments that automatically modify prompts must retain the original prompt, candidate prompts, optimization rationale, evaluation results, and rollback point.

## Phase 1 Task Selection Candidates

Prioritize tasks with unambiguous scoring, low run cost, and interpretable errors:

| Task | Input | Output | Scoring |
| --- | --- | --- | --- |
| Text classification | User questions / tickets / reviews | Fixed labels | accuracy / macro-F1 |
| Information extraction | Emails / resumes / product descriptions | JSON schema | exact match / field F1 / JSON validity |
| RAG Q&A | question + retrieved passages | answer + citation | answer correctness / citation precision |
| Tool calling | User request + tool schema | function call args | argument exact match / execution success |

Currently kept as candidates only — no long-term freeze. After M0, select the task that best validates key insights or helpful methods based on literature and industry experience, avoiding premature exclusion of higher-value minimal tasks in RAG, agent, or tool-use settings.

## Baselines

1. Manual prompt: a clear, human-written baseline.
2. Few-shot prompt: manual + 3–5 examples.
3. APE-style: LLM generates N candidate instructions, selects by dev score.
4. ProTeGi-style: generate textual critique from failure samples, then edit prompt.
5. DSPy/MIPROv2: strong baseline if the experiment stack uses Python.
6. GEPA-style: record traces and have the optimizer reflect before generating candidates; use Pareto/validation for selection.
7. Memory APO: maintain a library of successful strategies and failure modes; test cross-task reuse.

## Data Split

- `train`: visible to optimizer; used to generate critiques, candidates, and few-shot examples.
- `dev`: optimizer-visible scores; used to select candidates.
- `validation`: optimizer sees only aggregate score; used to prevent overfitting.
- `test`: fully held out; reported at the end.
- `adversarial`: malformed format, mixed language, boundary conditions, unauthorized-action prompts.

Small-scale starting configuration:

- train: 50–100 samples
- dev: 50 samples
- validation: 50 samples
- test: 100 samples
- adversarial: 30 samples

## Optimization Loop

```text
baseline_prompt
  -> run eval on train/dev
  -> collect failures and traces
  -> optimizer summarizes failure modes
  -> generate K prompt candidates
  -> run candidates on dev
  -> filter by hard constraints
  -> validate top candidates
  -> select winner or keep baseline
  -> write run artifact and prompt diff
```

## Candidate Filtering Rules

- Output schema must not change unless the current experiment round explicitly permits it.
- Safety / refusal / permission rules must not be removed or weakened.
- Test-set answers, specific sample labels, or scorer implementation must not be leaked into the prompt.
- Candidate prompts exceeding the length budget are downgraded or rejected.
- If validation score drops beyond the threshold, the candidate is not adopted even if dev score improves.

## Metrics

Quality metrics:

- Primary task score: accuracy, macro-F1, field F1, exact match.
- Format reliability: JSON validity, schema compliance.
- Robustness: adversarial set score, cross-model score.
- Stability: variance across multiple random seeds or repeated sampling.

Efficiency metrics:

- Number of optimizer calls.
- Number of target model calls.
- Token cost.
- Wall-clock time.
- Cost per unit score improvement.

Governance metrics:

- Prompt diff size.
- Whether automatic modification rationale is interpretable.
- Human review pass rate.
- Number of rollbacks.
- Proportion of production failure cases entering the eval set.

## Run Record Log Fields

Each optimization run must record at minimum:

```yaml
run_id:
date:
insight_or_method_validated:
task:
dataset_version:
target_model:
optimizer_model:
prompt_version_before:
prompt_version_after:
parameters:
optimizer_method:
candidate_count:
train_score:
dev_score:
validation_score:
test_score:
adversarial_score:
token_cost:
latency:
accepted:
rejection_reason:
top_failure_modes:
prompt_diff_summary:
source_files:
```

## Milestones

### M0: Source Collection and Survey Freeze

- Complete the minimum coverage matrix in the source collection plan.
- Update the literature map, industry practice summary, and core paper notes.
- Output frontier-state map, method taxonomy, evidence strength description, and source gap list.
- Output insight / conclusion / helpful method candidate list.
- Output 2–3 reusable methods or recommendations.

### M1: Minimal Validation Freeze

- Select 1–2 minimal validation tasks from M0's experiment candidates.
- Specify the insight/method to validate, validation objective, scorer, and success/failure interpretation criteria.
- Prepare minimal dataset and baseline prompt; do not pursue long-term benchmark completeness.

### M2: Preliminary Experiments

- Implement at least a manual and one improved/optimized baseline.
- Each run produces a traceable artifact.
- Report metrics, cost, failure cases, and conclusion limitations.

### M3: Final Summary and Report

- Integrate frontier state, industry experience, core insights, helpful methods, and preliminary validation results.
- Annotate each key conclusion with an evidence level.
- Output the final report and a follow-up validation roadmap.

### M4: Reflective Evolution

- Introduce trace reflection and failure mode summarization.
- Introduce candidate archive and validation split.
- Compare against MIPROv2/GEPA-style baseline.

### M5: Memory and Self-Evolving

- Maintain a library of successful strategies and failure modes.
- Test cross-task transfer.
- Evaluate long-term drift and rollback mechanisms.

### M6: System-Level Expansion

- Expand to RAG or tool-use.
- Expand the optimization target from a single prompt to prompt + examples + context + tool policy.
- Output a self-evolving prompt system design report.

## First Executable Experiment Recommendation

Start with "structured information extraction":

- Input: short email or user request.
- Output: strict JSON, e.g. `{intent, entities, urgency}`.
- Baseline: handwritten system prompt + JSON schema.
- Optimization targets: field F1, JSON validity, cost.
- Failure reflection: missed fields, wrong labels, format breakage, over-inference.

Round 1 validates only the minimal closed loop:

1. Run zero-shot / manual baseline / 10–20 candidates to form the pre-optimization gate.
2. Fix the instruction; compare no-example, random-example, and optimized-example.
3. On the same failure samples, compare direct rewrite vs. trace-first critique rewrite.
4. Write each candidate into the prompt artifact ledger, recording diff, score, cost, failure samples, accept/reject rationale, and rollback point.

Rationale: scoring is unambiguous, cost is low, errors are interpretable — a solid foundation for the first iteration of the prompt evolution loop.
