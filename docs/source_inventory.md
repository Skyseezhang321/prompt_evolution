# 来源清单

更新时间：2026-06-08

本文件记录资料搜集阶段的候选来源。详细收集范围、字段含义和阶段门槛见 [资料搜集计划](source_collection_plan.md)。

## 状态说明

- `candidate`：只登记线索，尚未粗读。
- `skimmed`：已快速浏览，确认相关性。
- `noted`：已写入 `docs/paper_notes/`、`docs/industry_notes/` 或行业实践整理。
- `rejected`：已排除，并记录原因。

## 共创线索说明

外部贡献的来源优先通过 `Research Signal` issue 进入，再按 [共创工作流](contribution_workflow.md) 做项目内新颖性判断。登记到本文件时，尽量在 `local_note` 或 `decision` 中附上：

- `suggested_by`：线索贡献者。
- `linked_issue`：对应 issue 或 PR。
- `novelty_status`：`duplicate`、`extension`、`contradiction`、`new-hypothesis` 或 `actionable-experiment`。
- `next_action`：关闭、补充引用、深读、更新综述或进入实验计划。

## 学术论文与框架

| source_id | status | relevance | title | date | url | method_category | local_note | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| paper-autoprompt-2020 | skimmed | medium | AutoPrompt: Eliciting Knowledge from Language Models with Automatically Generated Prompts | 2020 | https://aclanthology.org/2020.emnlp-main.346/ | gradient-guided prompt search |  | 需深读历史脉络 |
| paper-rlprompt-2022 | skimmed | medium | RLPrompt: Optimizing Discrete Text Prompts | 2022 | https://aclanthology.org/2022.emnlp-main.222/ | reinforcement learning prompt search |  | 需判断相关性 |
| paper-grips-2022 | skimmed | high | GrIPS: Gradient-free, Edit-based Instruction Search for Prompting Large Language Models | 2022/2023 | https://aclanthology.org/2023.eacl-main.277/ | gradient-free instruction search |  | 需深读 |
| paper-ape-2022 | skimmed | high | Large Language Models are Human-Level Prompt Engineers / APE | 2022 | https://arxiv.org/abs/2211.01910 | automatic prompt generation |  | 需深读 |
| paper-protegi-2023 | skimmed | high | Automatic Prompt Optimization with Gradient Descent and Beam Search / ProTeGi | 2023 | https://arxiv.org/abs/2305.03495 | textual gradient / beam search |  | 需深读 |
| paper-opro-2023 | candidate | high | Optimization by PROmpting / OPRO | 2023 | https://arxiv.org/abs/2309.03409 | LLM-as-optimizer |  | 需深读 |
| paper-promptbreeder-2023 | candidate | high | PromptBreeder | 2023 | https://arxiv.org/abs/2309.16797 | evolutionary / self-referential optimization |  | 需深读 |
| paper-evoprompt-2023 | skimmed | high | Connecting Large Language Models with Evolutionary Algorithms Yields Powerful Prompt Optimizers / EvoPrompt | 2023 | https://arxiv.org/abs/2309.08532 | evolutionary prompt optimization |  | 需深读 |
| paper-dspy-2023 | candidate | high | DSPy | 2023/2024 | https://arxiv.org/abs/2310.03714 | prompt-as-program |  | 需深读 |
| paper-intent-calibration-2024 | candidate | medium | Intent-based Prompt Calibration: Enhancing prompt optimization with synthetic boundary cases | 2024 | https://arxiv.org/abs/2402.03099 | synthetic boundary cases |  | 需核验 |
| paper-crispo-2024 | candidate | medium | CriSPO: Multi-Aspect Critique-Suggestion-guided Automatic Prompt Optimization for Text Generation | 2024 | https://arxiv.org/abs/2410.02748 | critique-suggestion APO |  | 需核验 |
| paper-human-feedback-2024 | skimmed | high | Prompt Optimization with Human Feedback | 2024 | https://arxiv.org/abs/2405.17346 | human preference feedback / dueling bandits |  | 需深读 |
| paper-prompt-report-2024 | skimmed | medium | The Prompt Report: A Systematic Survey of Prompting Techniques | 2024 | https://arxiv.org/abs/2406.06608 | prompting survey |  | 需判断与 APO 的边界 |
| paper-textgrad-2024 | candidate | high | TextGrad | 2024 | https://arxiv.org/abs/2406.07496 | textual gradient |  | 需深读 |
| paper-miprov2-2024 | candidate | high | MIPROv2 | 2024 | https://arxiv.org/abs/2406.11695 | instruction and example optimization |  | 需深读 |
| paper-prewrite-2024 | candidate | medium | PRewrite: Prompt Rewriting with Reinforcement Learning | 2024 | https://aclanthology.org/2024.acl-short.54/ | RL-based prompt rewriting |  | 需核验 |
| paper-synthetic-data-apo-2025 | skimmed | medium | Automatic Prompt Optimization Techniques: Exploring the Potential for Synthetic Data Generation | 2025 | https://arxiv.org/abs/2502.03078 | APO for synthetic data |  | 需判断是否纳入核心 |
| paper-apo-survey-2025 | candidate | high | A Systematic Survey of Automatic Prompt Optimization Techniques | 2025 | https://arxiv.org/abs/2502.16923 | survey |  | 需深读 |
| paper-ape-survey-2025 | candidate | high | A Survey of Automatic Prompt Engineering: An Optimization Perspective | 2025 | https://arxiv.org/abs/2502.11560 | survey |  | 需深读 |
| paper-autopdl-2025 | skimmed | high | AutoPDL: Automatic Prompt Optimization for LLM Agents | 2025 | https://arxiv.org/abs/2504.04365 | agent prompt optimization |  | 需深读 |
| paper-efficient-accurate-apo-2025 | candidate | medium | Efficient and Accurate Prompt Optimization | 2025 | https://aclanthology.org/2025.acl-long.37/ | efficient APO |  | 需核验 |
| paper-kg-apo-2025 | candidate | medium | Automatic Prompt Optimization for Knowledge Graph Construction: Insights from an Empirical Study | 2025 | https://www.vldb.org/2025/Workshops/VLDB-Workshops-2025/LLM%2BGraph/LLMGraph-7.pdf | empirical APO case study |  | 需核验 |
| paper-gepa-2025 | skimmed | high | GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning | 2025 | https://arxiv.org/abs/2507.19457 | reflective prompt evolution |  | 需深读 |
| paper-promptomatix-2025 | skimmed | medium | Promptomatix: An Automatic Prompt Optimization Framework for Large Language Models | 2025 | https://arxiv.org/abs/2507.14241 | prompt generation framework |  | 需深读 |
| paper-context-engineering-2025 | candidate | high | A Survey of Context Engineering for LLMs | 2025 | https://arxiv.org/abs/2507.13334 | context engineering survey |  | 需核验并深读 |
| paper-modular-prompt-optimization-2026 | skimmed | high | Modular Prompt Optimization: Optimizing Structured Prompts with Section-Local Textual Gradients | 2026 | https://arxiv.org/abs/2601.04055 | modular prompt optimization |  | 需深读 |
| paper-memapo-2026 | skimmed | high | Generalizable Self-Evolving Memory for Automatic Prompt Optimization / MemAPO | 2026 | https://arxiv.org/abs/2603.21520 | memory-based APO |  | 需深读 |
| paper-maspo-2026 | skimmed | high | MASPO: Joint Prompt Optimization for LLM-based Multi-Agent Systems | 2026 | https://arxiv.org/abs/2605.06623 | multi-agent prompt optimization |  | 需深读 |
| paper-promptolution-2026 | candidate | medium | promptolution | 2026 | https://aclanthology.org/2026.eacl-demo.21/ | prompt optimization tool |  | 需核验 |
| paper-sepo-2026 | skimmed | high | SePO: Self-Evolving Prompt Agent for System Prompt Optimization | 2026 | https://arxiv.org/abs/2606.04465 | self-evolving prompt optimization |  | 需深读 |

## 行业实践与工具

| source_id | status | relevance | title | date | url | method_category | local_note | decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| practice-zhihu-hermes-agent-2026 | noted | high | 知乎文章：Hermes Agent 自我进化机制与 OpenClaw 对比 | 未提供 | https://zhuanlan.zhihu.com/p/2026106192003437649 | agent self-evolution / procedural memory | user_provided；原文快照 `local_sources/raw/practice-zhihu-hermes-agent-2026.txt`；SHA256 `0D8600F0973328351BA945F1B1B29098DF6C30587DBE9455711C32D2B9B46335` | 已建行业笔记，需核验 Hermes / OpenClaw 原始项目资料 |
| practice-github-karpathy-guidelines-2026 | noted | high | multica-ai/andrej-karpathy-skills | 2026 | https://github.com/multica-ai/andrej-karpathy-skills/tree/main | coding agent behavioral guidelines | public GitHub；固定 commit `2c606141936f1eeef17fa3043a72095b4765b9c2`；约 170k stars / 17k forks at 2026-06-08 | 已建行业笔记，可作为 coding-agent 行为规则 eval 候选 |
| practice-openai-prompt-engineering | skimmed | high | OpenAI Prompt engineering guide |  | https://platform.openai.com/docs/guides/prompt-engineering | prompt engineering |  | 需整理 |
| practice-openai-evals | candidate | high | OpenAI Evaluation best practices |  | https://platform.openai.com/docs/guides/evaluation-best-practices | eval-driven development |  | 需核验 |
| practice-openai-graders | skimmed | high | OpenAI Graders guide |  | https://platform.openai.com/docs/guides/graders | graders / judge design |  | 需整理 |
| practice-openai-prompting | skimmed | high | OpenAI Prompting guide |  | https://platform.openai.com/docs/guides/prompting | prompt object / versioning |  | 需整理 |
| practice-openai-prompt-optimizer | skimmed | high | OpenAI Prompt optimizer |  | https://platform.openai.com/docs/guides/prompt-optimizer/ | prompt optimizer product |  | 需整理 |
| practice-anthropic-prompt-engineering | skimmed | high | Anthropic Prompt engineering overview |  | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview | prompt engineering |  | 需整理 |
| practice-anthropic-evals | skimmed | high | Anthropic Define success criteria and build evaluations |  | https://platform.claude.com/docs/en/test-and-evaluate/develop-tests | eval-driven development |  | 需整理 |
| practice-anthropic-context-engineering | skimmed | high | Anthropic Effective context engineering for AI agents | 2025 | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | context engineering / agents |  | 需整理 |
| practice-google-prompt-design | skimmed | high | Google Vertex AI Prompt design strategies |  | https://cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/prompt-design-strategies | prompt design |  | 需整理 |
| practice-google-structure-prompts | candidate | medium | Google Vertex AI Structure prompts |  | https://cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/structure-prompts | prompt structure |  | 需核验 |
| practice-google-data-driven-optimizer | skimmed | high | Google Vertex AI Data-driven prompt optimizer |  | https://cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/data-driven-optimizer | prompt optimizer product |  | 需整理 |
| practice-dspy-docs | candidate | high | DSPy documentation |  | https://dspy.ai/ | prompt-as-program |  | 需核验 |
| practice-langsmith-prompts | skimmed | high | LangSmith Manage prompts |  | https://docs.langchain.com/langsmith/manage-prompts | prompt versioning |  | 需整理 |
| practice-langfuse-prompt-management | skimmed | high | Langfuse Prompt Management |  | https://langfuse.com/docs/prompt-management/get-started | prompt versioning / runtime fetch |  | 需整理 |
| practice-langfuse-prompt-experiments | skimmed | high | Langfuse Prompt Experiments |  | https://langfuse.com/docs/datasets/prompt-experiments | prompt experiments / datasets |  | 需整理 |
| practice-promptfoo-optimization | skimmed | high | Promptfoo Prompt optimization |  | https://www.promptfoo.dev/docs/usage/prompt-optimization/ | eval-backed prompt optimization |  | 需整理 |
| practice-humanloop-prompts | skimmed | high | Humanloop Prompts |  | https://humanloop.com/docs/explanation/prompts | prompt versioning / logs / datasets |  | 需整理 |
| practice-humanloop-evaluation | skimmed | high | Humanloop Run an Evaluation via the UI |  | https://humanloop.com/docs/guides/evals/run-evaluation-ui | prompt comparison / evaluators |  | 需整理 |
| practice-arize-phoenix-prompt-learning | skimmed | high | Arize Phoenix Optimize Prompts Automatically |  | https://arize.com/docs/phoenix/prompt-engineering/tutorial/optimize-prompts-automatically | prompt learning / feedback loop |  | 需整理 |
| practice-parea-docs | skimmed | medium | Parea AI Docs |  | https://docs.parea.ai/ | experiments / observability |  | 需判断相关性 |
| practice-parea-deployed-prompts | skimmed | medium | Parea AI Deployed Prompts |  | https://docs.parea.ai/platform/deployment | prompt deployment |  | 需判断相关性 |

## 待补缺口

- 更多真实生产事故、prompt 漂移和回滚案例。
- 更多 agent/tool-use 场景的失败轨迹和优化实践。
- 更多非英文任务、跨模型迁移和多模型 routing 的 prompt 优化经验。
- 更多成本、延迟和人工审核成本的定量报告。
- 更多安全边界、合规约束和不可自动改写规则的工程实践。
