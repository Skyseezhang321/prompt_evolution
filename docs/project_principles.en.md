# Project Building Principles

Last updated: 2026-06-08

This file defines the long-term building principles for `prompt_evolution`. The principles are adapted from Karpathy-inspired coding agent guidelines, but have been reoriented from "reducing LLM coding errors" to "reducing false assumptions, over-engineering, irreproducible conclusions, and evidence-free changes in prompt optimization research."

The project's core output priority is: actionable insights, credible conclusions, reusable helpful methods, anti-patterns, and risk boundaries. Experiments, scripts, and benchmarks are verification and demonstration tools that serve these outputs — they are not the project's end goal.

Reference source: [andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills/tree/main)

## 1. Define the Problem First, Write the Prompt Second

A prompt is not an isolated piece of copy — it is the combined result of the task, model, context, examples, constraints, and scorer. Before adding or modifying a prompt, write out clearly:

- What the target task is.
- What the current hypothesis is.
- Where the input samples come from.
- What model and parameters are being used.
- What metric determines whether things improved or degraded.
- Which constraints must not be rewritten by automated optimization.

Check question: If someone else only sees the record, can they understand why this round of experiments was conducted and how to judge success?

## 2. Insights and Methods First; Minimal Experiments Serve Verification

Before adding material or experiments, state which insight, conclusion, or reusable method it is meant to support. First articulate the transferable experience clearly, then choose the minimal experiment that can verify that experience. Do not pursue a complete platform, complex agent workflow, or general-purpose optimization framework from the start.

- Prefer tasks with clear scoring, cheap execution, and interpretable errors.
- Prefer handwriting a baseline before introducing automated candidate generation.
- Do not abstract logic in advance if it has no reuse value.
- Do not expand the search space before a clear failure mode has been identified.
- Experiment conclusions must be able to feed back into an insight card, method playbook, anti-pattern, or risk boundary.

Check question: Does the current work produce a clearer insight, conclusion, or helpful method? Is the current implementation the minimal runnable version needed to verify that insight or method?

## 3. Change One Variable at a Time

The most common problem in prompt optimization is that multiple variables change simultaneously, making it impossible to attribute where the gain came from. By default, change the following variables separately:

- prompt copy.
- few-shot examples.
- system prompt.
- retrieval context.
- tool policy.
- model and sampling parameters.
- data split.
- scorer and evaluation criteria.

If multiple variables must be changed simultaneously, the round must be flagged as a multi-factor experiment, and single-variable causal conclusions must be avoided.

Check question: If the metric changes, can you identify which change was the primary cause?

## 4. Every Conclusion Must Have Evidence

Conclusions in project documentation require a source — they cannot rest on impressions or a single output sample.

- Paper conclusions must point to the paper, experimental setup, and limitations.
- Experiment conclusions must point to run artifacts, metrics, sample outputs, and failure cases.
- Engineering judgments must state the impact scope, risks, and alternatives.
- Method recommendations must state the applicable scenario, usage steps, counter-examples, misuse risks, and verification method.
- Distinguish between observations, inferences, and conclusions.

Check question: Can a reader follow the documentation to find the evidence supporting the conclusion?

## 5. Goal-Driven Execution

Do not use vague goals such as "optimize the prompt," "improve performance," or "make it more stable." Translate them into verifiable goals:

```text
On baseline X,
using dataset version D and scorer E,
raise primary metric Y from A to B,
while format error rate, cost, or safety failure type Z does not degrade.
```

Every multi-step task should include a plan and a verification method. Verification can take the form of tests, metric comparisons, sample inspection, manual review, or documentation consistency checks.

Check question: After this round of work is complete, can you clearly determine success, failure, or whether further experiments are needed?

## 6. Changes Are Traceable

Prompt self-evolution without versioning, evaluation, and rollback can easily become non-auditable behavior drift. Important changes should record at minimum:

- Before and after prompt versions.
- Model, parameters, and tool configuration.
- Dataset version and split.
- Scorer or judge rubric.
- Candidate generation method.
- Metric changes and cost.
- Failure modes.
- Reasons for adoption or rejection.
- Rollback point.

Changes meaningful to research tracking should be written into the `Unreleased` section of `CHANGELOG.md`.

Check question: If the new version performs worse, can you find the reason for the change and roll back?

## 7. Precise Changes

Every change should be directly traceable to the current goal. Do not mix in unrelated refactoring, formatting cleanup, terminology substitution, or experiment ideas in the same change.

- Match existing documentation and code style.
- Only clean up dead content caused by your own changes.
- If you discover an unrelated issue, record or flag it — do not delete it opportunistically.
- When modifying shared workflows, scorers, or data structures, broaden the verification scope.

Check question: Can every diff item be explained as serving the current request or experiment goal?

## Signals It Is Working

When these principles are effective, the project should exhibit:

- Experiment records are reproducible.
- Prompt versions are comparable.
- Conclusions can be traced back to evidence.
- Insights can be converted into reusable methods or anti-patterns.
- Experiments can explain which insight was verified, not just display scores.
- Diffs are clean and focused.
- Automated optimization does not bypass safety, permission, or evaluation constraints.
- Failure cases feed into the next eval round or risk record.

## Trade-offs

These principles lean toward caution and traceability, which may slow down simple tasks. For low-risk changes such as spelling corrections or single-line documentation updates, the process may be simplified. For experiment design, prompt rewriting, scorer adjustment, and conclusion synthesis, the full principles must be followed.
