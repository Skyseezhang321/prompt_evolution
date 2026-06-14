# Contributing Guide

**English** | [简体中文](CONTRIBUTING.md)

Welcome to `prompt_evolution`. This project studies prompt optimization and prompt self-evolution. The goal of open co-creation is not to incorporate every viewpoint into the conclusions, but to turn valuable reading discoveries into trackable, verifiable, and rollback-able research leads.

Core rule:

> Anyone can submit a research lead at low cost; any project conclusion must go through novelty assessment, evidence organization, and trackable verification.

## What You Can Contribute

| Contribution type | When it fits | Recommended entry point | Minimum requirements |
| --- | --- | --- | --- |
| Research lead | You read a paper, document, thread, issue, or incident post-mortem and found a point that seems helpful | `Research Signal` issue | Source link, the point you find valuable, potentially related project questions |
| Deep-read note | You are willing to systematically summarize a paper or industry source | PR + structured note | Use `docs/paper_notes/template.md` or `docs/industry_notes/template.md` |
| Experiment proposal | A viewpoint can be turned into a minimal eval or prompt experiment | `Experiment Proposal` issue | Goal, hypothesis, input samples, model, evaluation criteria, success criteria |
| Experiment results | You have run reproducible metrics, examples, or failure cases | PR | Run log, prompt diff, model parameters, dataset, scorer, cost, failure cases |
| Principle crystallization | Multiple sources or experiments support the same stable finding | PR | Cite evidence explicitly; distinguish observations, inferences, and conclusions |

## Fastest Way to Get Involved

1. Open a `Research Signal` issue.
2. Fill in the source, key insight, and why you think it is helpful.
3. If you know how it relates to existing project content, note whether it is "likely a duplicate, extension, contradiction, or new hypothesis."
4. A maintainer or reviewer will assess in-project novelty and decide whether it proceeds to deep-read, experiment candidate, supplementary citation, or closure.

You do not need to write a complete paper note from the start. Low-barrier leads are valid contributions, but a lead itself does not directly become a project conclusion.

## Branch and Merge Requirements

After the current round of workflow-rule changes is committed and pushed, all subsequent code, documentation, experiment, and configuration changes must first create a personal or task branch from the latest `main`, then make modifications, verify, and commit within that branch; direct commits to `main` are not permitted.

The purpose of this rule is to keep `main` as a stable, reproducible, reviewable, and rollback-able baseline, while isolating changes from different contributors, different hypotheses, and different variables. This allows reviewers to assess impact scope per PR and to quickly roll back by branch or commit when necessary.

When merging, please submit a PR/merge request targeting `main` and describe the branch origin, scope of changes, verification results, whether prompt/data/model parameters/scorer are affected, and the rollback point. Do not mix unrelated changes into the PR.

## How Novelty Is Assessed

Novelty here means "novel within the project," not whether something is a world-first.

| Label | Meaning | Follow-up action |
| --- | --- | --- |
| `duplicate` | The project already has a similar viewpoint or source | Merge citations; close or link to the existing issue |
| `extension` | Provides boundary, case, metric, or counter-example for an existing viewpoint | Supplement the related note or survey |
| `contradiction` | Conflicts with an existing judgment | Mark as requiring evidence; prioritize for discussion or experiment candidate |
| `new-hypothesis` | Forms a new testable hypothesis | Proceed to deep-read or experiment proposal |
| `actionable-experiment` | Can be directly converted into a minimal experiment | Update `docs/experiment_plan.md` first, then implement |

## Requirements When Writing Notes

- New paper notes go in `docs/paper_notes/`, using `docs/paper_notes/template.md`.
- New industry experience goes in `docs/industry_notes/`, using `docs/industry_notes/template.md`.
- Register all sources in `docs/source_inventory.md` before deciding whether to deep-read them.
- Clearly distinguish the author's claims, observable evidence, project inferences, and verified conclusions.
- Do not present a single-example performance as a stable pattern.
- Preserve original links for papers, documents, blog posts, threads, and issues.

## Requirements When Writing Experiments

New experiments must update `docs/experiment_plan.md` before implementing scripts or running the experiment. Experiment records must include at minimum:

- Goal and hypothesis.
- Baseline prompt and candidate prompt.
- Model, parameters, dataset, scorer.
- Prompt diff, cost, failure cases, and rollback point.
- Conclusion limitations: which findings are only observations, and which remain to be verified.

## PR Requirements

When submitting a PR, please describe:

- The corresponding issue, source, or experiment hypothesis.
- Which files were changed, and why those files needed to change.
- Whether prompt, data, model parameters, scorer, or evaluation criteria were changed.
- Whether `CHANGELOG.md`'s `Unreleased` section was updated.
- Where the evidence comes from: source notes, run logs, metrics tables, failure cases, or counter-examples.

## Security, Privacy, and Copyright

- Do not commit API keys, webhooks, account tokens, or private data.
- Real webhooks must stay in local `.env` files and must not be committed.
- Do not upload un-anonymized user conversations, customer data, internal logs, or trade secrets.
- For sources such as Zhihu, Twitter/X, or paywalled articles, retain only necessary short excerpts, links, and summaries; do not reproduce articles in full.

For the complete co-creation workflow, see [Co-creation Workflow](docs/contribution_workflow.md).
