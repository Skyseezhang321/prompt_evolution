# Co-creation Workflow

**English** | [简体中文](contribution_workflow.md)

Updated: 2026-06-08

This document defines the co-creation mechanism for `prompt_evolution` as a public project. The goal is to let anyone contribute reading discoveries, insights, and useful methods at low cost, while allowing maintainers to manage leads, judge novelty, organize deep-reads, consolidate helpful methods, drive necessary validation, and prevent unsupported opinions from entering the project's conclusions.

## Design Summary

The co-creation mechanism uses a four-layer closed loop:

```text
research signal -> novelty check -> structured note -> insight/method card -> validation if needed -> evidence-backed conclusion
```

Where:

- `research signal` is a low-barrier entry point that lets contributors "flag something."
- `novelty check` determines whether a given point is a duplicate, extension, contradiction, new hypothesis, actionable method, or experiment candidate relative to existing project content.
- `structured note` organizes a single source into a reviewable paper note or industry experience note.
- `insight/method card` distills phenomena, mechanisms, transferable rules, counter-examples, and method steps from a source.
- `validation if needed` converts an insight or method into a target, hypothesis, sample, model, scorer, and success criteria only when validation or demonstration is required.
- `evidence-backed conclusion` accepts only conclusions supported by sources, experiments, failure cases, or counter-examples.

## Goals and Non-Goals

Goals:

- Lower the participation barrier so that anyone who encounters valuable material can quickly submit a lead.
- Link each lead to its source, judgment, note, experiment, and conclusion.
- Prioritize distilling insights, conclusions, helpful methods, anti-patterns, and risk boundaries.
- Keep prompt optimization research measurable, reproducible, and rollback-able.
- Let maintainers manage collaboration via GitHub issues, labels, PRs, and document status.

Non-Goals:

- Do not turn the issue tracker into a collection of unsupported opinions.
- Do not require every contributor to complete a deep-read and run experiments.
- Do not write something directly into project conclusions just because its source looks authoritative.
- Do not implement large benchmarks or optimization frameworks without an experiment plan.

## Contribution Tiers

| Tier | What the contributor does | Deliverable | Management entry point |
| --- | --- | --- | --- |
| Lead | Submit a source and noteworthy points | `Research Signal` issue | label: `signal`, `needs-novelty-check` |
| Novelty judgment | Compare against existing docs, source inventory, insights/methods, and experiment plan | Issue comment or status label | label: `duplicate`, `extension`, `contradiction`, `new-hypothesis`, `actionable-method`, `experiment-candidate` |
| Deep-read | Summarize a single source using the template | `docs/paper_notes/` or `docs/industry_notes/` | PR |
| Synthesis | Distill insights, helpful methods, risks, and open questions across sources | `docs/literature_map.md`, `docs/industry_practices.md`, report page | PR |
| Experiment | Convert a key insight/method into a minimal validation and record results | `docs/experiment_plan.md`, scripts, run log | issue + PR |
| Conclusion | Consolidate evidence-backed principles or solutions | README, final report, project principles, or changelog | PR review |

## State Flow

| State | Entry condition | Completion condition | Next step |
| --- | --- | --- | --- |
| `submitted` | Someone submits a lead issue | Source, key points, and related questions are readable | `needs-novelty-check` |
| `needs-novelty-check` | Lead requires in-project deduplication | Determined to be duplicate, extension, contradiction, new hypothesis, method candidate, or experiment candidate | Corresponding novelty label |
| `duplicate` | An equivalent source or conclusion already exists | Linked to existing document or issue | Close or merge reference |
| `extension` | Adds supplementary value to an existing point | Points to the note or survey that needs updating | `needs-deep-dive` or PR |
| `contradiction` | Conflicts with an existing judgment | Conflict point and required evidence are marked | `evidence-needed` or experiment candidate |
| `new-hypothesis` | Forms a new testable hypothesis | Goal, variables, and evaluation direction are clearly stated | `needs-deep-dive`, `actionable-method`, or `experiment-candidate` |
| `actionable-method` | Can be distilled into a reusable method, playbook, anti-pattern, or governance recommendation | Applicable scenarios, steps, risks, counter-examples, and validation approach are clearly stated | PR review or `experiment-candidate` |
| `needs-deep-dive` | Source warrants systematic reading | Structured note produced | PR review |
| `experiment-candidate` | Can be converted into a minimal validation/demonstration | `docs/experiment_plan.md` updated, stating which insight/method is being validated | Experiment implementation or backlog |
| `evidence-backed` | Supported by sources, metrics, failure cases, or counter-examples | Conclusion entered into the appropriate document with evidence level noted | changelog entry |

## Novelty Review Rules

Review in the following order:

1. Does `docs/source_inventory.md` already contain the same source, a different version of the same paper, or the same product documentation?
2. Do `docs/paper_notes/` or `docs/industry_notes/` already contain a structured note?
3. Do `docs/literature_map.md`, `docs/industry_practices.md`, or `docs/research_brief.md` already contain the same point?
4. Does `docs/experiment_plan.md` already contain the same or a similar experimental hypothesis?
5. Can this lead change the current insight, method recommendation, risk judgment, evaluation criteria, or experiment priority?

Judgment criteria:

- `duplicate`: The point already exists; no new research judgment is added; a citation may be supplemented.
- `extension`: A new boundary, new scenario, new metric, new failure case, or stronger evidence for an existing point.
- `contradiction`: Conflicts with an existing judgment; cannot directly change the conclusion; the conflict and evidence requirements must be preserved.
- `new-hypothesis`: Can form a new testable hypothesis but is not yet ready for an experiment.
- `actionable-method`: Can be distilled into a reusable method, playbook, anti-pattern, or governance recommendation.
- `actionable-experiment`: Goal, variables, sample, model, and scoring approach are sufficiently clear to enter the experiment plan.

## Role Responsibilities

| Role | Responsibility | Not required |
| --- | --- | --- |
| Finder | Discover sources and submit research leads | Not required to write complete notes |
| Triage reviewer | Make in-project novelty judgments; add labels and next steps | Not required to do the deep-read themselves |
| Deep reader | Deep-read a single source and write a structured note | Not required to run experiments |
| Synthesizer | Distill sources and deep-read results into insight cards, method playbooks, or anti-patterns | Not required to run experiments |
| Experimenter | Convert a key insight/method into a minimal validation and record results | Not required to change project principles |
| Maintainer | Decide whether something enters the README, final report, or project principles | Not required to adopt every point |

One person can take on multiple roles. PRs should preserve `suggested_by`, `reviewed_by`, linked issues, and source links where possible to facilitate future tracking.

## Branch and Merge Rules

The `main` branch represents the project's current stable baseline — reproducible, reviewable, and rollback-able. After this round of workflow rule changes has been committed and pushed, all contributors and coding agents must create a personal or task branch from the latest `main` before starting any new task or independent contribution. That branch is the smallest unit that can be merged into `main`; it may carry multiple sessions, multiple batches of changes, and multiple commits — all modifications, verifications, and commits happen within the branch, without creating a new branch from `main` for each change.

This rule serves three goals:

- Isolate parallel work so that different contributors or different experimental variables do not end up in the same diff.
- Protect `main` so that research conclusions, experiment plans, and tooling scripts always have a stable rollback point.
- Concentrate review, verification records, and merge decisions in PRs/merge requests for easy tracking of impact scope and responsibility boundaries.

After completing changes, contributors should request a merge into `main` via a PR/merge request. The PR should describe the branch origin, the corresponding issue/source/experimental hypothesis, the scope of changes, verification results, whether prompt/data/model parameters/scorer were changed, and the necessary rollback point. Changes already in the working tree that do not belong to the current task must not be mixed into the PR.

## GitHub Management Plan

Recommended issue templates:

- `Research Signal`: Submit leads such as papers, documentation, threads, issues, and incident post-mortems.
- `Deep Dive Note`: Claim or submit a deep-read note.
- `Experiment Proposal`: Propose a minimal testable experiment.

Recommended labels:

| label | Purpose |
| --- | --- |
| `signal` | Raw research lead |
| `needs-novelty-check` | Awaiting in-project deduplication and novelty judgment |
| `needs-deep-dive` | Requires a structured note |
| `experiment-candidate` | Can enter the experiment plan |
| `actionable-method` | Can be distilled into a helpful method, playbook, or anti-pattern |
| `duplicate` | Content already exists; merge citation |
| `extension` | Supplements an existing point |
| `contradiction` | Conflicts with an existing judgment |
| `new-hypothesis` | New hypothesis |
| `evidence-needed` | Requires sources, experiments, or failure cases for support |
| `ready-for-pr` | Scope is clear; can be implemented or documented |

## Document Update Matrix

| Situation | Must-update documents | May need updating |
| --- | --- | --- |
| New source lead | `docs/source_inventory.md` or issue | `docs/contribution_workflow.md` does not need updating each time |
| New paper deep-read | `docs/paper_notes/<source_id>.md`, `docs/source_inventory.md` | `docs/literature_map.md` |
| New industry experience deep-read | `docs/industry_notes/<source_id>.md`, `docs/source_inventory.md` | `docs/industry_practices.md` |
| New insight or helpful method | Corresponding survey/report document, `docs/source_inventory.md` | README, final report structure, `docs/project_principles.md` |
| New experiment proposal | `docs/experiment_plan.md`, stating which insight/method is being validated | README, final report structure |
| Experiment completed | Experiment log, `docs/experiment_plan.md` | `docs/industry_practices.md`, final report |
| Project conclusion changed | Corresponding conclusion document, `CHANGELOG.md` | README, `docs/project_principles.md` |

## Quality Threshold

Leads can be lightweight, but before entering project conclusions they must satisfy:

- There is an original source or a reviewable artifact.
- In-project novelty judgment has been completed.
- Author claims, project observations, project inferences, and project conclusions have been distinguished.
- If prompt or experiments are involved, model, parameters, dataset, scorer, cost, and failure cases have been recorded.
- If project recommendations are changed, impact scope, risks, and rollback point have been stated.

## Minimal Example

A qualified `Research Signal` issue can be brief:

```text
Source: <paper or document link>
Point I find valuable: The authors use failure samples to generate natural-language critiques, then rewrite the prompt.
Possible connection: This project's judgment on "whether natural-language reflection is more suitable than scalar reward for prompt optimization."
My novelty guess: Likely an extension, related to the ProTeGi/GEPA direction.
Suggested next step: Check whether this is already covered in literature_map; if not, add to the deep-read candidate list.
```

A disqualified lead typically only says "this looks great, worth reading" — no source, no point, no related question. Such a lead can be retained but cannot enter the downstream workflow.
