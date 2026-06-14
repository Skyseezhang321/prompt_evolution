# Insight / Conclusion / Helpful Method Field Definition Standard

Last updated: 2026-06-10

## What This Standard Is

This document is the **sole authoritative reference** for the fields of four core output types: `insight`, `conclusion`, `helpful method`, and `anti-pattern`. Its purpose is to resolve a long-standing problem: these four concepts appear repeatedly across `docs/research_brief.md`, `docs/project_principles.md`, both deep-read templates, and `docs/insight_method_catalog_20260609.md`, yet previously there were **only field names — no unified "definition + evaluation criteria + required fields"** — causing the same judgment to be classified as different types in different documents, with slight inconsistencies in field naming.

Governed scope (field definitions in the following documents all defer to this standard):

- The "Implications for This Project" sections in `docs/paper_notes/template.md` and `docs/industry_notes/template.md`.
- The YAML fields in `docs/insight_method_catalog_20260609.md`.
- The "Insight Fields" and "Actionable Plan Fields" in `docs/final_report_outline.md`.

Relationship to upstream documents: this document **inherits** the one-sentence definitions of the three output types from lines 25–27 of `docs/research_brief.md` and does not start from scratch; it builds on that foundation by adding evaluation criteria, filling in the missing `conclusion` field schema, and unifying field naming. Evidence grading follows the A/B/C/D scheme from `docs/final_report_outline.md` and is not redefined here.

## I. Definitions and Distinctions Among the Four Core Output Types

| Type | One-sentence definition | Question answered | Discriminating question (if matched, assign to this type) |
| --- | --- | --- | --- |
| `insight` | A specific, transferable, verifiable cognition: **why** a phenomenon occurs and what the mechanism is | "What happened / why?" | Does it explain a mechanism or a counter-intuitive phenomenon? Could it still hold for a different task or model? |
| `conclusion` | A **judgment** with an evidence level, counterexamples, and scope, which can be directly adopted or refuted | "What can we now determine?" | Is it a claim that can be supported or refuted by evidence? Can an evidence level and applicable scope be assigned to it? |
| `helpful method` | Directly reusable operational steps / playbook, anchored to a specific insight | "What exactly should I do?" | Can the reader follow the steps and execute them? Are there applicable scenarios, metrics, and a rollback plan? |
| `anti-pattern` | A known practice that leads to incorrect conclusions or degradation, along with its trigger conditions | "What not to do, and why?" | Does it describe a **specific practice to avoid** and its consequences? |

### Easily Confused Boundaries (Evaluation Criteria)

- **insight vs conclusion**: An insight is a mechanism-level "why" — it may come from a single source and may remain a hypothesis awaiting validation. A conclusion is a judgment-level "what has been determined" — it **must** carry an evidence level and applicable scope, and **cannot** be directly elevated from a single paper or a single example (see item 4 of `docs/project_principles.md`). The same material often first crystallizes as an insight, and is only elevated to a conclusion after cross-source evidence accumulates.
- **insight vs helpful method**: An insight is a cognition; a helpful method is an operation that can be copied verbatim. An insight may temporarily have no associated method; however, **every helpful method must reference the insight it serves via `insight_supported`** — "pure operational steps with no supporting insight" are not permitted.
- **conclusion vs helpful method**: A conclusion is "whether something holds or not"; a helpful method is "what you should therefore do." A conclusion may not produce a method (e.g., it only delineates a boundary); a method should trace back to a supporting conclusion or insight.
- **Placement of anti-pattern**: An anti-pattern can stand as its own entry or appear as the `counterexample_or_limit` / `misuse_or_anti_pattern` field of an insight or method. The standard for standing as its own entry is that it carries cross-scenario warning value in its own right.

## II. Fields for Each Type (Required / Optional)

Field names are defined by the table below. If a **required** field is missing, that entry may not appear in the final report or project conclusions.

### Insight

| Field | Required | Description |
| --- | --- | --- |
| `insight` | Required | One-sentence insight |
| `user_facing_one_liner` | Required | Plain-language version for non-researcher readers |
| `phenomenon` | Required | The observed phenomenon |
| `mechanism` | Required | The mechanism behind the phenomenon |
| `actionable_rule` | Required | The transferable rule |
| `evidence_strength` | Required | A/B/C/D |
| `main_sources` | Required | File paths of supporting sources, to ensure traceability |
| `counterexample_or_limit` | Required | Counterexamples or conditions under which it does not hold |
| `helpful_method` | Optional | Points to the name of an associated method (if any) |
| `exact_action_to_try` | Optional | The smallest action a reader can try immediately |
| `before_after_example` | Optional | A before/after example for report display |
| `validation_or_demo` | Optional | Intended validation / demonstration approach |

### Conclusion

The previous three documents all lacked an independent `conclusion` schema; this standard supplies the following minimum set:

| Field | Required | Description |
| --- | --- | --- |
| `conclusion` | Required | A one-sentence judgment that can be adopted or refuted |
| `scope` | Required | Applicable scope: task type, model, sample size, and other conditions for validity |
| `evidence_strength` | Required | A/B/C/D |
| `main_sources` | Required | Supporting sources |
| `counterexample_or_limit` | Required | Counterexamples, failure cases, or conditions under which it does not hold |
| `supersedes_or_conflicts` | Optional | Which existing judgment this replaces or conflicts with |

### Helpful Method

| Field | Required | Description |
| --- | --- | --- |
| `name` | Required | Method name |
| `insight_supported` | Required | Points back to the insight this method serves |
| `problem` | Required | What problem it solves |
| `recommended_when` | Required | Applicable scenarios |
| `not_recommended_when` | Required | Non-applicable scenarios (paired with `recommended_when` to form evaluation criteria) |
| `required_inputs` | Required | Required data / prerequisites |
| `implementation_steps` | Required | Steps that can be copied verbatim |
| `evaluation_metrics` | Required | Evaluation metrics |
| `risks` | Required | Risks |
| `misuse_or_anti_pattern` | Required | Misuse patterns / corresponding anti-pattern |
| `rollback_plan` | Required | Rollback strategy |
| `evidence` | Required | Evidence (source / experiment / level) |
| `cost_and_latency` | Optional | Cost and latency |
| `expected_benefit` | Optional | Expected benefit |
| `next_experiment` | Optional | Follow-up validation experiment |

### Anti-pattern

| Field | Required | Description |
| --- | --- | --- |
| `anti_pattern` | Required | The specific practice to avoid |
| `why_harmful` | Required | Why it leads to incorrect conclusions or degradation |
| `trigger_condition` | Required | Under what conditions it occurs |
| `instead_do` | Required | The alternative practice (typically points to a helpful method) |
| `evidence_or_source` | Optional | Source or observed cases |

## III. Field Naming Mapping (Resolving Existing Inconsistencies)

The table below aligns three existing schemas; the naming in this standard is authoritative. Names that are inconsistent or absent should converge to this standard in subsequent revisions:

| Unified field (this standard) | paper/industry template | insight_method_catalog | final_report_outline |
| --- | --- | --- | --- |
| `insight` | `insight` | `insight` | `insight` |
| `conclusion` | `conclusion` | (no independent field — split into `user_facing_one_liner` + `exact_action_to_try`) | (no independent field) |
| `helpful_method` | `helpful method` | `helpful_method` | see "Actionable Plan Fields" |
| `anti_pattern` | `anti-pattern / limit` | `counterexample_or_limit` | `misuse_or_anti_pattern` |
| `validation_or_demo` | minimal validation / demo | `next_validation` | `validation_or_demo` |
| `evidence_strength` | (implicit in evidence level) | `evidence_strength` | `evidence_strength` |

> Known pending convergence: the abbreviated schema in the introductory "Usage" section of `insight_method_catalog_20260609.md` is missing `phenomenon` / `mechanism` / `actionable_rule` (individual entries in the body do include these), and uses `next_validation` rather than `validation_or_demo`; its title contains "Conclusion" but there is no independent `conclusion` field. Supplement these per this standard when revising that file.

## IV. Evidence Grading

Follows the definitions from lines 39–42 of `docs/final_report_outline.md` and is not repeated here: A (original paper / official documentation / open-source documentation + structured notes completed), B (engineering practice appearing repeatedly across multiple sources), C (preliminary experimental observation within this project), D (inference synthesized from materials — must be marked as pending validation). Every key judgment in a conclusion, insight, or helpful method must be annotated with an evidence level, and D-level inferences must not be presented as definitive conclusions.

## V. Minimum Compliant Example

```yaml
# insight
insight: Prompt optimization is not beneficial by default; on many tasks the optimized result may fall below zero-shot.
user_facing_one_liner: First check whether there is room to improve, then spend money on automatic optimization.
phenomenon: In small-sample dev selection, the difference between candidates may not exceed the noise.
mechanism: When zero-shot is already near the capability ceiling, prompt search mainly amplifies evaluation noise.
actionable_rule: Estimate headroom and the noise floor before running APO.
evidence_strength: A
main_sources: [docs/paper_notes/paper-coin-flip-2026.md]
counterexample_or_limit: Tasks whose combinatorial structure requires multi-round search may be underestimated.

# conclusion
conclusion: On small-sample, free-text tasks, the expected gain of automatic prompt optimization is not significantly higher than zero-shot.
scope: Small-sample dev (~20-30 items), free-generation tasks; excludes strict JSON/rubric output tasks.
evidence_strength: A
main_sources: [docs/paper_notes/paper-coin-flip-2026.md]
counterexample_or_limit: On strict-rubric tasks such as HelpSteer2, all six methods beat zero-shot.

# helpful_method
name: pre-optimization gate
insight_supported: "First confirm whether there is room to improve, then spend money running the optimizer"
problem: Avoid wasting optimizer calls and introducing overfitting on tasks with no room to optimize.
recommended_when: The task has an objectively scorable held-out set and you suspect headroom is limited.
not_recommended_when: Tasks whose gains depend on multi-round search to discover combinatorial structure.
required_inputs: 20 held-out samples, 10-20 candidate prompts, zero-shot baseline.
implementation_steps: Run baseline -> generate candidates -> score on the same sample batch -> compare headroom against the noise floor -> stop if below threshold.
evaluation_metrics: best gain over zero-shot, score variance across candidates.
risks: Hard-coding the threshold across tasks causes misjudgment.
misuse_or_anti_pattern: Estimating headroom on the training set instead of the held-out set.
rollback_plan: When the gate verdict is unreliable, fall back to the fixed-budget standard optimization flow.
evidence: docs/paper_notes/paper-coin-flip-2026.md (A).
```
