# GitHub Repository Source Audit Workflow: 2026-06-08

This workflow addresses a core risk identified in the GitHub channel analysis: insights cannot be distilled solely from repository names, stars, READMEs, or second-hand summaries. All conclusions from the GitHub channel must first pin the source version, then pass through machine scan, manual audit, and where necessary, local execution verification.

## Current Objectives

- Pin the commit, README SHA256, license, and local path for key repositories.
- First record "what actually exists in the source code," then synthesize "what implications it has for prompt optimization / prompt self-evolution."
- Clearly distinguish among three types of statements: source observations, inferred structural transfers, and adoptable conclusions.

## Execution Commands

The first round clones only 4 core repositories to avoid degrading evidence quality by deep-reading 8–10 repositories at once.

```powershell
python scripts/github_repo_clone.py --preset core4 --output-root local_sources\raw\github_repo_clones --manifest-prefix github_repo_clone_core4
```

The local clones are then machine-scanned to produce an ignored JSON audit result and a committable draft audit note.

```powershell
python scripts/github_repo_audit.py --clone-root local_sources\raw\github_repo_clones --audit-root local_sources\raw\github_repo_audits --notes-dir docs\github_repo_audit_notes --force-notes
```

Raw clones and JSON audits are stored under `local_sources/raw/` and are not committed to the repository; committable manual audit entry points are stored under `docs/github_repo_audit_notes/`.

## Round 1 Pinned Repositories

| source_id | repository | commit | branch | Round 1 audit entry | Current assessment |
| --- | --- | --- | --- | --- | --- |
| `repo-linshenkx-prompt-optimizer` | `linshenkx/prompt-optimizer` | `d7cde6c2fc5c` | `develop` | [audit note](github_repo_audit_notes/repo-linshenkx-prompt-optimizer.md) | Source evidence shows the compare evaluation, structured judge, rewrite-from-evaluation, calibration, and E2E test pipeline exist; cannot yet conclude "task performance improves after optimization." |
| `repo-karpathy-autoresearch` | `karpathy/autoresearch` | `228791fb499a` | `master` | [audit note](github_repo_audit_notes/repo-karpathy-autoresearch.md) | Source evidence shows an autonomous experiment loop, fixed evaluator, result logging, and rollback rules; however the optimization target is training code, not prompts — any transfer to prompt self-evolution must be labeled as a structural reference. |
| `repo-humanlayer-12-factor-agents` | `humanlayer/12-factor-agents` | `d20c728368bf` | `main` | [audit note](github_repo_audit_notes/repo-humanlayer-12-factor-agents.md) | Documentation and template evidence supports treating prompt/context as a first-class engineering object; this is a source of agent prompt/context design principles, not evidence of method effectiveness. |
| `repo-affaan-m-ecc` | `affaan-m/ECC` | `90dfd9505dc8` | `main` | [audit note](github_repo_audit_notes/repo-affaan-m-ecc.md) | Implementation, test, and example traces support directions such as memory, verification loop, and harness governance; README claims are strong and the execution entry points and true method validity still require further verification. |

Round 1 clone manifest: `local_sources/raw/github_repo_clones/_manifests/github_repo_clone_core4_20260608T140910Z.md`.

Round 1 audit manifest: `local_sources/raw/github_repo_audits/github_repo_audit_manifest_20260608T141030Z.md`.

## Round 2 Pending Repositories (canonical prompt optimizers, not yet cloned/audited)

The repositories below are registered in `docs/source_inventory.md` (most back-filled via the Twitter/X channel) but have not yet entered the clone/audit pipeline. They are more directly decisive for the question "does the GitHub channel actually have effectiveness evidence" than the remaining documentation/asset-type repositories from strict8, and should be prioritized as the next clone/audit batch. The same approach applies: pin the commit, README SHA256, and license first, then perform the machine scan and manual audit.

| source_id | repository | Associated paper / arXiv | Priority | Audit focus |
| --- | --- | --- | --- | --- |
| `repo-gepa-ai-gepa` | `gepa-ai/gepa` | GEPA (2507.19457, deep-read as `paper-gepa-2026`) | High | Paper ↔ source cross-verification: whether reflective evolution, Pareto / validation selection, rollout, and cost are consistent with the paper (L4 candidate). |
| `repo-microsoft-promptwizard` | `microsoft/PromptWizard` | PromptWizard (2405.18369, no note registered) | High | Joint instruction/example optimization, self-evolving refinement, API dependencies; add paper note first. |
| `repo-salesforce-promptomatix` | `SalesforceAIResearch/promptomatix` | Promptomatix (2507.14241, skimmed) | High | DSPy dependency, synthetic data, feedback, CLI/API; deep-read the paper first. |
| `repo-eladlev-autoprompt` | `Eladlev/AutoPrompt` | Intent-based Prompt Calibration (2402.03099, candidate) | Medium | Whether there is a reproducible eval; distinguish the name from LangChain Promptim to avoid confusion. |
| `repo-scale3-dspyground` | `Scale3-Labs/dspyground` | No independent paper (GEPA harness) | Medium | samples / metrics / runs history, AI SDK agent porting — treat as an engineering case study of an agent prompt optimizer. |

These source_ids match those in `docs/source_inventory.md`; after auditing, back-fill the draft audit notes into `docs/github_repo_audit_notes/` and upgrade the evidence level according to the table below.

## Evidence Levels

Subsequent GitHub channel insights are handled according to the following thresholds:

| Level | Meaning | What can be written |
| --- | --- | --- |
| L0 | Search results, stars, repo metadata, or repository-name associations | Can only serve as candidate leads. |
| L1 | README / docs read after pinning the commit | Can write "the repository claims / documentation states." |
| L2 | Source code, configuration, test, or example paths located after pinning the commit | Can write "source observation supports the existence of a mechanism." |
| L3 | Tests, examples, or minimal reproduction experiments runnable locally | Can write "a certain behavior is reproducible under a given environment and settings." |
| L4 | Cross-repository, paper, or in-project experiment corroboration | Can enter the final report as a strong-conclusion candidate. |

The current 4 repositories mostly reach only L2; `karpathy/autoresearch` has the clearest structural closed loop, but it still requires a prompt/context-version reproduction experiment within this project to be upgraded to L3/L4.

## Insight Distillation Rules

1. Every insight must carry a source_id, commit, file path, and observation type.
2. If an insight is transferred from a non-prompt task, the transfer boundary must be stated explicitly.
3. Do not treat README performance claims, star counts, project popularity, or marketing copy as conclusions.
4. Do not equate "eval/test code exists" directly with "the method is effective"; it only indicates the repository has an auditable structure.
5. Questions that can be turned into experiments should be entered into `docs/experiment_plan.md` first, then scripts implemented or experiments run.

## Round 1 Preliminary Conclusions

- The GitHub channel is better suited to providing engineering structure, governance processes, and real code organization patterns; direct evidence proving that a prompt optimizer is effective is scarce.
- The most valuable combination at present is not copying a single repository wholesale, but extracting three types of mechanisms: the compare/evaluation/rewrite pipeline from `prompt-optimizer`, the separation of optimization target from evaluator in `autoresearch`, and the prompt/context governance boundary from `12-factor-agents`.
- ECC-type agent harnesses can serve as leads for memory, verification loop, and subagent orchestration, but should enter the conclusion layer later than the three mechanism types above.

## Next Steps

Completed: 12 candidate insights extracted from 4 audit notes, with evidence levels, applicability boundaries, and experiment-conversion potential annotated in the [GitHub Repository Candidate Insight Evidence Cards](github_repo_insight_cards_20260608.md).

To continue (priority re-ordered 2026-06-10):

1. (High) Prioritize cloning/auditing the canonical prompt optimizer repositories: `gepa-ai/gepa`, `microsoft/PromptWizard`, `SalesforceAIResearch/promptomatix`, `Eladlev/AutoPrompt` (all registered in `docs/source_inventory.md` but not yet audited). They are more directly decisive than the remaining documentation-type repositories from strict8 for determining "whether the GitHub channel truly has effectiveness evidence"; among them, `gepa-ai/gepa` is simultaneously the official implementation of the already deep-read paper GEPA, enabling paper ↔ source cross-verification (L4 candidate).
2. (High) Configure `GITHUB_TOKEN` and re-run full discovery; correct the script recall by applying the "core / peripheral dual-track" recommendations from the quick-filter document, and verify whether "few optimizer repositories" is an artifact of low recall.
3. (Low, intentionally deferred) The remaining 4 documentation/asset-type repositories from strict8 (`dair-ai/Prompt-Engineering-Guide`, `shanraisshan/claude-code-best-practice`, `f/prompts.chat`, `pathwaycom/llm-app`) can be re-audited on demand and should not block conclusions.
4. Select 2–4 of the 12 candidate insights to enter `docs/experiment_plan.md`, prioritizing the freezing of the evaluator / data / ledger schema.
5. Choose 1 minimal experiment to transfer `autoresearch`'s principle of "only allow modification of the optimization target, disallow modification of the evaluator/data" into a prompt/context optimization closed loop.
