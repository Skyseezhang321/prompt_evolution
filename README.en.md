# Prompt Evolution Research

**English** | [简体中文](README.md)

This repository is for researching, summarizing, and (where necessary) validating work on "prompt optimization / prompt self-evolution." The core deliverables are effective insights, trustworthy conclusions, and reusable helpful methods; experiments mainly serve to validate key insights, demonstrate methods, and calibrate boundaries.

Last updated: 2026-06-12

> Note on language: docs that already have an English version link to the English file; docs that are not yet translated link to their Chinese source. Themed HTML pages carry a 中文/EN toggle in the top bar.

## Public build board

This is a research project being built openly and in real time. The README puts the important analysis, research process, and intermediate results up front so that onlookers can quickly understand current progress without first reading the whole document tree.

| Item | Current status |
| --- | --- |
| Current phase | A five-day delivery, insight-first research loop: quickly track the state of the art, and distill effective insights, core conclusions, and reusable methods. |
| Current main thread | Build a traceable chain from source -> note -> insight card -> conclusion -> helpful method -> validation/demo -> final report. |
| First batch of experiments | Not aiming for a complete benchmark; only picking 1-2 minimal tasks that can validate an insight or demonstrate a method. |
| Main risks | eval overfitting, LLM-as-judge bias, prompt drift, runaway cost, automatic optimization breaking safety boundaries. |
| Want the conclusions fast | Open [Cross-channel Synthesis Report v4](docs/analysis_report_v4_20260611.en.html): a four-layer structure — method map (evolution of seven methods / side-by-side comparison / selection guide), workflow insights (14), engineering implementation (the five-piece kit / tool tiering / release gate), and pitfalls & boundaries (12 misreading clarifications + frontier gaps). The older [v3](docs/analysis_report_v3_20260610.html) is frozen and kept for comparison; if you only want the 12 insights, read the [Reader-facing Insight Handbook](docs/insight_handbook_20260609.en.md). |
| Want optimization advice directly | [Prompt Optimization Advisor](advisor/advisor.html): describe your scenario in a chat, and the system gives layered, traceable advice grounded in an evidence-graded knowledge base. Two forms — open `advisor.html` directly (deterministic, free); or run the FastAPI backend (`uvicorn server:app --app-dir advisor`) for **grounded LLM Q&A** (OpenRouter/deepseek, answers forced to cite insight IDs and evidence levels). Source and build in [advisor/](advisor/README.en.md). |
| Reading path | Read this README first; for the conclusions fast, read the [Reader-facing Insight Handbook](docs/insight_handbook_20260609.en.md); to co-create, read the [Contribution Guide](CONTRIBUTING.en.md) and the [Co-creation Workflow](docs/contribution_workflow.en.md); for research details, read the [Source Collection Plan](docs/source_collection_plan.md), [Source Inventory](docs/source_inventory.md), [Research Brief](docs/research_brief.en.md), [Experiment Plan](docs/experiment_plan.en.md), [Final Report Outline](docs/final_report_outline.en.md), and the [Changelog](CHANGELOG.md). |

## Five-day delivery goals

The current goal of this project is not to exhaustively reproduce every prompt optimization method, nor to make experiments the main thread, but to complete a trustworthy, executable research delivery within a limited time:

- Keep up with the frontier: clarify the main progress in automatic prompt optimization, reflective prompt evolution, self-evolving prompts, context engineering, and eval-driven prompt iteration.
- Distill effective insights: turn papers, source code, and industry material into concrete, counter-intuitive, transferable, verifiable insights, rather than mere summaries.
- Form an experience summary: organize industry practice and paper conclusions into reusable principles, method playbooks, anti-patterns, and risk checklists.
- Produce helpful methods: give 2-3 methods or recommendations with real reuse value, explaining their applicable scenarios, prerequisites, cost, risk, and misuse boundaries.
- Do minimal validation: pick 1-2 key insights or methods for a minimal experiment, providing observational evidence, failure cases, and a path for further validation.
- Form the final report: with insights, conclusions, and helpful methods as the main thread, distinguishing "evidence-supported conclusions," "preliminary validation observations," and "still-to-be-verified speculation."

## Key analysis and judgments

As of 2026-06-08, the following are the frontier judgments most worth tracking after the current material collection and preliminary verification:

1. The main bottleneck of prompt optimization is shifting from "prompt wording" toward "eval quality, failure trajectories, context organization, and version governance."
2. Natural-language reflection may be more suitable for prompt-level optimization than a pure scalar reward, because the prompt itself is a readable, editable, auditable text object.
3. A truly production-grade self-evolving system must include constrained search, candidate isolation, offline evaluation, human review, version rollback, and continuous monitoring.
4. For agent systems, the optimization objective should include not only final-answer accuracy but also tool-call correctness, refusal boundaries, cost, latency, stability, and cross-model transfer.

These judgments are not yet final conclusions. The final report must annotate each judgment with an evidence level and justify its strength of support through material sources, preliminary experiments, failure cases, or counter-examples.

## How the analysis proceeds

The project currently advances along the following route:

1. First define the research problem: a prompt is not isolated text but a combination of instruction, examples, context, tool policy, model parameters, and evaluator.
2. Then collect material: broadly gather academic papers, engineering frameworks, product docs, industry cases, and negative experience, recording the screening criteria.
3. Then distill insights: from APE, ProTeGi, OPRO, PromptBreeder, DSPy/MIPROv2 to GEPA, MemAPO, SePO, MASPO and other directions, extract transferable phenomena, mechanisms, methods, and boundaries.
4. Then form method recommendations: turn paper methods and industry practice into helpful methods, operational playbooks, anti-patterns, evaluation criteria, and governance recommendations.
5. Finally do minimal validation: only validate the 1-2 judgments that most affect the credibility of an insight or the usability of a method, recording prompt diff, model, parameters, dataset, scorer, cost, failure mode, and rollback point.

## Intermediate results

Already done:

- Established the research framework, literature map, industry practices, experiment plan, paper-note template, and industry-experience-note template.
- Established a source collection plan to guide systematic collection of papers, product docs, engineering frameworks, and industry cases.
- Established a final report structure to constrain the final delivery to include frontier state, experience summary, solution recommendations, and preliminary validation.
- Established the project building principles, written into `AGENTS.md` / `CLAUDE.md` for Codex and Claude Code to read.
- Established a WeCom (Enterprise WeChat) notification entry point for unified messaging across later scripts, experiment tasks, scheduled jobs, and CI.
- Established a minimal OpenAI / OpenRouter LLM API client and a dry-run smoke test, for provider configuration checks before later experiments.
- Established the first batch of experiment candidate directions, but has not yet frozen specific tasks.
- Established a clone / audit process for key GitHub repositories, having pinned commits for 4 core repos and generated source-audit drafts, to avoid drawing conclusions from README or popularity alone.

Not yet done:

- Deep-reading notes for core sources, the frontier-state diagram, and evidence-level annotation are not yet complete.
- The first stable list of insights / conclusions / helpful methods is not yet frozen.
- The material review has not yet been turned into 2-3 high-priority reusable methods or recommendations.
- The benchmark harness is not yet implemented.
- The first version of the dataset and scorer is not yet frozen.
- Comparable experimental results for manual, few-shot, APE-style, and ProTeGi-style approaches have not yet been produced.
- No empirical conclusion that can support "self-evolution works" has yet been formed.

## Next steps

1. Per the [Source Collection Plan](docs/source_collection_plan.md), complete source quick-screening, deep-reading of core sources, and evidence-level annotation.
2. Expand the [Literature Map](docs/literature_map.en.md) and [Industry Practices](docs/industry_practices.md), prioritizing the distillation of reusable insights, anti-patterns, and method playbooks.
3. Aggregate 2-3 helpful methods or recommendations, explaining applicable scenarios, implementation steps, cost, risk, misuse boundaries, and rollback points.
4. Design a minimal validation for the 1-2 most important insights or methods, avoiding an oversized benchmark harness built for completeness' sake.
5. Per the [Final Report Outline](docs/final_report_outline.en.md), output the full write-up and report.

## Public co-creation mechanism

This project will subsequently accept external leads and PRs in the manner of a public project. The basic idea of the co-creation mechanism is: low barrier for receiving "I read about a valuable point," high bar for distilling "a research conclusion the project can rely on."

Recommended flow:

```text
Research Signal issue -> in-project novelty judgment -> structured note -> insight/method card -> necessary validation -> evidence-backed conclusion
```

Contributors may submit only a lead, insight, or useful method, without taking on full deep-reading or experiments; maintainers will tag leads as `duplicate`, `extension`, `contradiction`, `new-hypothesis`, `actionable-method`, or `experiment-candidate`. Only after source recording, evidence organization, and necessary validation will a viewpoint enter the README, final report, or project principles.

How to participate: see the [Contribution Guide](CONTRIBUTING.en.md); the full management process is in the [Co-creation Workflow](docs/contribution_workflow.en.md).

## Research goals

The core question is not "how to write a prettier prompt," but:

- How to turn prompt design into a measurable, reproducible, rollback-able optimization problem.
- How to use the LLM's natural-language reflection ability to produce better instructions from failure samples, execution traces, human feedback, and automatic evaluation.
- How to let prompt / system prompt / examples / context / tool policy keep improving as experience accumulates, while controlling drift, overfitting, and safety risk.

## Basic principles

This project adopts the [Project Building Principles](docs/project_principles.en.md) as a shared constraint for subsequent document, experiment, and code work. The short version:

1. Define the problem first; don't write the prompt first.
2. Insights and methods first; experiments serve validation.
3. Change only one variable at a time.
4. Every conclusion must have evidence.
5. Goal-driven execution.
6. Changes must be traceable.
7. Precise edits, no unrelated refactoring.

## Current documents

- [Project Building Principles](docs/project_principles.en.md): basic working principles for prompt optimization/self-evolution research and the agent execution constraints.
- [Contribution Guide](CONTRIBUTING.en.md): entry-point instructions for external contributors submitting leads, notes, experiments, and PRs.
- [Co-creation Workflow](docs/contribution_workflow.en.md): the management process for lead deduplication, novelty judgment, deep-reading, experiments, and conclusion distillation.
- [Source Collection Plan](docs/source_collection_plan.md): the collection scope, fields, and stage gates for papers, industry experience, engineering frameworks, and negative cases.
- [Source Inventory](docs/source_inventory.md): candidate papers, industry practices, tool docs, and remaining gaps during the collection phase.
- [GitHub Repo Discovery Script](docs/github_repo_discovery.md): batch-discover candidate prompt-optimization repos via the GitHub Search API.
- [GitHub Repo Triage](docs/github_repo_triage_20260608.md): a core/peripheral/excluded tiering of the first 85 GitHub raw candidates.
- [GitHub Repo Analysis Overview](docs/github_repo_analysis_overview_20260608.md): the first layer of a three-layer analysis of the screened GitHub repos.
- [GitHub Repo Content Catalog](docs/github_repo_catalog_20260608.md): introduces the screened repos' positioning, evidence, and handling recommendations using unified fields.
- [GitHub Key-Repo Deep Dives](docs/github_repo_deep_dives_20260608.md): analyzes key prompt-optimizer, self-evolving-agent, and agent/context-engineering repos.
- [GitHub Repo Evidence Matrix](docs/github_repo_evidence_matrix_20260608.md): a horizontal comparison of prompt optimization, auto-iteration, eval, rollback, and reproducibility evidence.
- [GitHub Repo Source-Audit Workflow](docs/github_repo_source_audit_workflow_20260608.en.md): pins key-repo commits, generates a clone/audit manifest and manual audit notes, serving as the evidence entry point for GitHub insight distillation.
- [GitHub Repo Candidate Insight Evidence Cards](docs/github_repo_insight_cards_20260608.en.md): distills 12 candidate methods/lessons from the core4 source audit, annotated with evidence level, boundaries, and convertibility into experiments.
- [GitHub Channel Insight Synthesis](docs/github_repo_channel_synthesis_20260609.en.md): organizes the GitHub channel's conclusions, helpful methods, anti-patterns, and minimal-validation candidates per the latest insight-first principle.
- [Research Brief](docs/research_brief.en.md): problem definition, research hypotheses, technical route, and risks.
- [Final Report Outline](docs/final_report_outline.en.md): the content boundaries, evidence levels, and acceptance criteria for the final write-up and report.
- [Reader-facing Insight Handbook](docs/insight_handbook_20260609.en.md): for non-specialist readers, the 12 core insights written in learning order as "counter-intuitive point + concrete example + real numbers + copy-able steps + boundaries," with all prompt examples marked as illustrative and all numbers attributed.
- [Cross-channel Synthesis Report v4](docs/analysis_report_v4_20260611.en.html): the current main report. It upgrades v3's "single-layer 12-insight structure" into a four-layer knowledge system — (1) method map (the seven-method evolution lineage, six-method side-by-side comparison, selection guide, 7 method clusters); (3) 14 workflow insights (numbered 01–12 consistent with the unified TOC, adding 13 zero-cost structural transforms and 14 optimizer/judge versioning); (4) engineering implementation (the five-piece kit, tool-maturity tiering, research->tool mapping, release gates and ledger); (6)(9) 12 pitfall clarifications and the "scope boundary + frontier gap" statement, plus a repo<->paper cross-reference table. The older [Report v3](docs/analysis_report_v3_20260610.html) (frozen), [Report v2](docs/analysis_report_v2_20260609.html) (organized by insight, arXiv-centric), and [Report v1](docs/analysis_report_v1_20260608.html) (organized by channel) are kept for comparison and rollback; the editable mind-map source is the [Mermaid Mind Map](docs/prompt_evolution_mindmap_20260610.en.md) (v3 structure, pending update to v4).
- [Insight / Conclusion / Helpful Method Candidate List](docs/insight_method_catalog_20260609.en.md): per the latest insight-first principle, aggregates papers, source code, and industry material into reusable insights, core conclusions, helpful methods, anti-patterns, and validation candidates (a structured middle layer for researchers and the final report).
- [Literature Map](docs/literature_map.en.md): the lineage of papers on automatic prompt optimization, self-evolution, and context engineering.
- [APO Seven-Method Primer](docs/apo_seven_methods_primer_20260611.en.md): strings the repeatedly-cited baseline backbone APE->ProTeGi->OPRO->DSPy->TextGrad->MIPROv2->GEPA into a single narrative, giving each method's positioning, mechanism, representative results, and limitations, with numbers consistent with the individual deep-reading notes.
- [Industry Practices](docs/industry_practices.md): cross-source practice summaries from OpenAI, Anthropic, Google, DSPy, LangSmith, Promptfoo, and others.
- [Other-Platform Channel Insight Synthesis](docs/source_batches/web_search_platform_insight_cards_20260609.en.md): the other-platforms (web_search/tools + general community broad search) channel entry point, with a conclusion overview, insight/helpful-method cards, anti-patterns, broad-search channel coverage and gaps, and validation candidates, organized by A/B/C/D grade.
- [Other-Platform Candidate Source Structured Analysis](docs/source_batches/web_search_platform_analysis_20260608.en.md): the evidence layer; quick-screen tiering and an evidence index for sources such as Hugging Face, Arize, Promptfoo, Langfuse, Humanloop, LangChain, OPIK, and Weaviate.
- [Industry-Experience Note Template](docs/industry_notes/template.md): a unified format for later deep-reading of industry sources such as Zhihu, Twitter/X, engineering blogs, and incident retrospectives.
- [Experiment Plan](docs/experiment_plan.en.md): the minimal experiment design, baselines, metrics, log fields, and milestones for validating key insights and demonstrating helpful methods.
- [Paper-Note Template](docs/paper_notes/template.md): a unified format for later paper reading.
- [WeCom Notification](docs/wecom_notification.md): the unified Enterprise WeChat bot notification entry point, configuration, and usage.
- [LLM API Clients & Smoke Test](docs/llm_clients.md): the minimal OpenAI / OpenRouter call entry points, configuration, and connectivity checks.
- [Changelog](CHANGELOG.md): records important changes to research material, experiments, and document structure.

## Subsequent workflow

1. External contributions are preferably submitted as a `Research Signal` issue; maintainers do the in-project novelty judgment per the [Co-creation Workflow](docs/contribution_workflow.en.md).
2. New sources are first registered and classified per the [Source Collection Plan](docs/source_collection_plan.md), then a decision is made on whether to deep-read.
3. New papers go into `docs/paper_notes/`, with a 1-2 page summary per the template.
4. New industry experience goes into `docs/industry_notes/`, recording source background, core claims, reusable insights, evidence level, and convertible methods per the template.
5. New experiments must state which insight, conclusion, or helpful method they validate, and must first update the [Experiment Plan](docs/experiment_plan.en.md) before writing code.
6. Every prompt variant must record model, parameters, dataset, scorer, cost, and failure cases.
7. Any "automatically change the prompt" experiment must keep the original prompt, candidate prompt, optimization reason, evaluation results, and rollback point.

## Notifications

Message notifications for all scripts, experiment tasks, scheduled jobs, and CI flows uniformly call `scripts/wecom_notify.py`, which sends them to the Enterprise WeChat bot. The real webhook goes in the local `.env` under `WECOM_BOT_WEBHOOK` and is not committed to the repo.

Command-line and Git-hook notifications by default attach git's "main changes": first generating a natural-language summary by change scope, then listing the files involved; when the working tree is clean, they show the most recent commit summary.

```bash
python scripts/wecom_notify.py "### Prompt Evolution notification-channel test"
```

## LLM API smoke test

`.env.example` contains local configuration templates for OpenAI and OpenRouter. By default the smoke test only outputs a dry-run payload and does not send a real request:

```bash
python scripts/llm_smoke_test.py
```

After filling in the local `.env`, use `--live` to check provider connectivity. This check only validates configuration and basic response parsing; it is not a prompt-experiment conclusion.

## License

This project uses the MIT License. See [LICENSE](LICENSE) for details.
