# 来源清单

更新时间：2026-06-09

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
| paper-grips-2022 | noted | high | GrIPS: Gradient-free, Edit-based Instruction Search for Prompting Large Language Models | 2022/2023 | https://aclanthology.org/2023.eacl-main.277/ | gradient-free instruction search | 深读笔记 `docs/paper_notes/paper-grips-2022.md`；2026-06-12 全文证据级 | 已深读；前史锚点——v1 早于 APE 八个月的免梯度短语编辑搜索（无 LLM 生成器），"语义不连贯编辑照样涨分"与 flawed-metaphor 跨年代互证 |
| paper-ape-2022 | noted | high | Large Language Models are Human-Level Prompt Engineers / APE | 2022 | https://arxiv.org/abs/2211.01910 | automatic prompt generation | 深读笔记 `docs/paper_notes/paper-ape-2022.md`；2026-06-10 全文证据级 | 已深读；propose-then-select 最简下限基线与"选择口径=部署场景"过拟合戒律来源 |
| paper-protegi-2023 | skimmed | high | Automatic Prompt Optimization with Gradient Descent and Beam Search / ProTeGi | 2023 | https://arxiv.org/abs/2305.03495 | textual gradient / beam search |  | 需深读 |
| paper-opro-2023 | noted | high | Optimization by PROmpting / OPRO | 2023 | https://arxiv.org/abs/2309.03409 | LLM-as-optimizer | 深读笔记 `docs/paper_notes/paper-opro-2023.md`；2026-06-10 全文证据级 | 已深读；轨迹驱动 LLM-as-optimizer 基线，"默认不留验证集"作反面对照 |
| paper-promptbreeder-2023 | candidate | high | PromptBreeder | 2023 | https://arxiv.org/abs/2309.16797 | evolutionary / self-referential optimization |  | 需深读 |
| paper-evoprompt-2023 | skimmed | high | Connecting Large Language Models with Evolutionary Algorithms Yields Powerful Prompt Optimizers / EvoPrompt | 2023 | https://arxiv.org/abs/2309.08532 | evolutionary prompt optimization |  | 需深读 |
| paper-dspy-2023 | noted | high | DSPy | 2023/2024 | https://arxiv.org/abs/2310.03714 | prompt-as-program | 深读笔记 `docs/paper_notes/paper-dspy-2023.md`；2026-06-10 全文证据级 | 已深读；prompt-as-program 奠基，本版优化 demonstration（instruction 优化见 MIPROv2） |
| paper-promptagent-2023 | noted | high | PromptAgent: Strategic Planning with Language Models Enables Expert-level Prompt Optimization | 2023 | https://arxiv.org/abs/2310.16427 | MCTS planning + error feedback | 深读笔记 `docs/paper_notes/paper-promptagent-2023.md`；2026-06-12 全文证据级 | 已深读；主线结构评审中发现的缺环——critique 线的搜索结构 beam→MCTS→Pareto 演进中的规划搜索一支，同等探索量下 MCTS 胜 beam/greedy |
| paper-intent-calibration-2024 | candidate | medium | Intent-based Prompt Calibration: Enhancing prompt optimization with synthetic boundary cases | 2024 | https://arxiv.org/abs/2402.03099 | synthetic boundary cases |  | 需核验 |
| paper-crispo-2024 | candidate | medium | CriSPO: Multi-Aspect Critique-Suggestion-guided Automatic Prompt Optimization for Text Generation | 2024 | https://arxiv.org/abs/2410.02748 | critique-suggestion APO |  | 需核验 |
| paper-human-feedback-2024 | skimmed | high | Prompt Optimization with Human Feedback | 2024 | https://arxiv.org/abs/2405.17346 | human preference feedback / dueling bandits |  | 需深读 |
| paper-prompt-report-2024 | skimmed | medium | The Prompt Report: A Systematic Survey of Prompting Techniques | 2024 | https://arxiv.org/abs/2406.06608 | prompting survey |  | 需判断与 APO 的边界 |
| paper-textgrad-2024 | noted | high | TextGrad | 2024 | https://arxiv.org/abs/2406.07496 | textual gradient | 深读笔记 `docs/paper_notes/paper-textgrad-2024.md`；2026-06-10 全文证据级 | 已深读；textual-gradient 框架化锚点，instruction↔demo 互补证据 |
| paper-miprov2-2024 | noted | high | MIPROv2 | 2024 | https://arxiv.org/abs/2406.11695 | instruction and example optimization | 深读笔记 `docs/paper_notes/paper-miprov2-2024.md`；2026-06-10 全文证据级 | 已深读；instruction+demo 联合优化基线，proposal/credit-assignment 形式化 |
| paper-prewrite-2024 | candidate | medium | PRewrite: Prompt Rewriting with Reinforcement Learning | 2024 | https://aclanthology.org/2024.acl-short.54/ | RL-based prompt rewriting |  | 需核验 |
| paper-synthetic-data-apo-2025 | skimmed | medium | Automatic Prompt Optimization Techniques: Exploring the Potential for Synthetic Data Generation | 2025 | https://arxiv.org/abs/2502.03078 | APO for synthetic data |  | 需判断是否纳入核心 |
| paper-apo-survey-2025 | noted | high | A Systematic Survey of Automatic Prompt Optimization Techniques | 2025 | https://arxiv.org/abs/2502.16923 | survey | 深读笔记 `docs/paper_notes/paper-apo-survey-2025.md`；2026-06-10 taxonomy 级 | 已读；5 部分优化流程 anatomy，用作 taxonomy 完整性校验外部参照 |
| paper-ape-survey-2025 | noted | high | A Survey of Automatic Prompt Engineering: An Optimization Perspective | 2025 | https://arxiv.org/abs/2502.11560 | survey | 深读笔记 `docs/paper_notes/paper-ape-survey-2025.md`；2026-06-10 taxonomy 级 | 已读；优化理论三轴 + 7 frontier（含 bi-level/thought-driven、constrained opt） |
| paper-autopdl-2025 | skimmed | high | AutoPDL: Automatic Prompt Optimization for LLM Agents | 2025 | https://arxiv.org/abs/2504.04365 | agent prompt optimization |  | 需深读 |
| paper-efficient-accurate-apo-2025 | candidate | medium | Efficient and Accurate Prompt Optimization | 2025 | https://aclanthology.org/2025.acl-long.37/ | efficient APO |  | 需核验 |
| paper-kg-apo-2025 | candidate | medium | Automatic Prompt Optimization for Knowledge Graph Construction: Insights from an Empirical Study | 2025 | https://www.vldb.org/2025/Workshops/VLDB-Workshops-2025/LLM%2BGraph/LLMGraph-7.pdf | empirical APO case study |  | 需核验 |
| paper-gepa-2025 | skimmed | high | GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning | 2025 | https://arxiv.org/abs/2507.19457 | reflective prompt evolution |  | 需深读 |
| paper-promptomatix-2025 | skimmed | medium | Promptomatix: An Automatic Prompt Optimization Framework for Large Language Models | 2025 | https://arxiv.org/abs/2507.14241 | prompt generation framework |  | 需深读 |
| paper-context-engineering-2025 | noted | high | A Survey of Context Engineering for LLMs | 2025 | https://arxiv.org/abs/2507.13334 | context engineering survey | 深读笔记 `docs/paper_notes/paper-context-engineering-2025.md`；2026-06-10 taxonomy 级（166 页，仅读结构） | 已读结构；确认 prompt 优化为 context engineering 子集，用于范围边界声明 |
| paper-modular-prompt-optimization-2026 | skimmed | high | Modular Prompt Optimization: Optimizing Structured Prompts with Section-Local Textual Gradients | 2026 | https://arxiv.org/abs/2601.04055 | modular prompt optimization |  | 需深读 |
| paper-memapo-2026 | skimmed | high | Generalizable Self-Evolving Memory for Automatic Prompt Optimization / MemAPO | 2026 | https://arxiv.org/abs/2603.21520 | memory-based APO |  | 需深读 |
| paper-maspo-2026 | skimmed | high | MASPO: Joint Prompt Optimization for LLM-based Multi-Agent Systems | 2026 | https://arxiv.org/abs/2605.06623 | multi-agent prompt optimization |  | 需深读 |
| paper-promptolution-2026 | candidate | medium | promptolution | 2026 | https://aclanthology.org/2026.eacl-demo.21/ | prompt optimization tool |  | 需核验 |
| paper-sepo-2026 | skimmed | high | SePO: Self-Evolving Prompt Agent for System Prompt Optimization | 2026 | https://arxiv.org/abs/2606.04465 | self-evolving prompt optimization |  | 需深读 |
| paper-prompt-repetition-2025 | noted | high | Prompt Repetition Improves Non-Reasoning LLMs | 2025-12-17 | https://arxiv.org/abs/2512.14982 | prompt repetition / non-reasoning prompt technique | user_provided_example；深读笔记 `docs/paper_notes/paper-prompt-repetition-2025.md`；2026-06-11 方法+结果级（Figure 逐格数字未转录） | 已深读；非推理模式 47/70 显著胜 0 负、零输出成本的结构变换，定位为本项目 APO baseline 变换 + 最小三臂 A/B 候选（baseline/×2/padding）；推理模式收益消失（5/28），长 prompt 与输入计费翻倍是边界 |

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
| practice-google-zero-shot-prompt-optimizer | skimmed | high | Google Vertex AI Zero-shot optimizer | 2025-10-28 | https://cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/zero-shot-optimizer | prompt optimizer product | Twitter/X 批次追溯到官方文档；关注单 prompt 实时改写、applicable_guidelines 和 suggested_prompt | 需与 data-driven optimizer 区分，整理产品化 prompt optimizer 边界 |
| practice-dspy-docs | candidate | high | DSPy documentation |  | https://dspy.ai/ | prompt-as-program |  | 需核验 |
| practice-dspy-ai-control | candidate | high | Prompt optimization can enable AI control research | 2025 | https://www.greaterwrong.com/posts/bALBxf3yGGx4bvvem/prompt-optimization-can-enable-ai-control-research | AI safety / prompt optimization / audit budget | Twitter/X 批次由 DSPy 官方账号指向；涉及 GEPA、monitor eval 和 audit budget，需核验 benchmark 设置 | 进入 eval/governance 深读候选 |
| practice-drew-breunig-dspy-talk | candidate | medium | Let the Model Write the Prompt / DSPy in compound AI pipelines | 2025-06-10 | https://www.dbreunig.com/2025/06/10/let-the-model-write-the-prompt.html | DSPy / prompt-as-program / model switching | Twitter/X 批次由 Simon Willison / Drew Breunig 线索追溯；工程解释价值高，非论文实证 | 作为 practitioner source 深读，抽取 maintainability 和 eval-first 实践 |
| practice-pydantic-gepa-evals | skimmed | high | Automated Prompt Optimization with GEPA, Pydantic AI, and Pydantic Evals | 2026-02-02 | https://pydantic.dev/articles/prompt-optimization-with-gepa | prompt optimizer product / eval harness | Twitter/X 批次追溯到 Pydantic 官方技术博客；包含 Agent.override、Pydantic Evals、metrics 和 tracing 线索 | 进入行业实践深读，抽取 eval/tracing/versioning 字段 |
| practice-langsmith-prompts | skimmed | high | LangSmith Manage prompts |  | https://docs.langchain.com/langsmith/manage-prompts | prompt versioning |  | 需整理 |
| practice-langfuse-prompt-management | skimmed | high | Langfuse Prompt Management |  | https://langfuse.com/docs/prompt-management/get-started | prompt versioning / runtime fetch |  | 需整理 |
| practice-langfuse-prompt-experiments | skimmed | high | Langfuse Prompt Experiments |  | https://langfuse.com/docs/datasets/prompt-experiments | prompt experiments / datasets |  | 需整理 |
| practice-promptfoo-optimization | skimmed | high | Promptfoo Prompt optimization |  | https://www.promptfoo.dev/docs/usage/prompt-optimization/ | eval-backed prompt optimization |  | 需整理 |
| practice-humanloop-prompts | skimmed | high | Humanloop Prompts |  | https://humanloop.com/docs/explanation/prompts | prompt versioning / logs / datasets |  | 需整理 |
| practice-humanloop-evaluation | skimmed | high | Humanloop Run an Evaluation via the UI |  | https://humanloop.com/docs/guides/evals/run-evaluation-ui | prompt comparison / evaluators |  | 需整理 |
| practice-arize-phoenix-prompt-learning | skimmed | high | Arize Phoenix Optimize Prompts Automatically |  | https://arize.com/docs/phoenix/prompt-engineering/tutorial/optimize-prompts-automatically | prompt learning / feedback loop |  | 需整理 |
| practice-hf-dspy-gepa-cookbook | skimmed | high | Hugging Face Cookbook: Prompt Optimization for Language Models with DSPy GEPA |  | https://huggingface.co/learn/cookbook/en/dspy_gepa | DSPy / GEPA / cookbook | 其它平台批次 P1；包含 NuminaMath-1.5、train/val/test split、metric、main/reflection LM 和 GEPA optimizer 配置 | 进入行业笔记候选，可作为最小复现实验参考 |
| practice-hf-dspy-cross-encoders | skimmed | high | Hugging Face Blog: Automatic Prompt Optimization with DSPy and Cross Encoders | 2025-08-03 | https://huggingface.co/blog/dleemiller/auto-prompt-opt-dspy-cross-encoders | DSPy / MIPROv2 / evaluator | 其它平台批次 P1；包含 cross-encoder evaluator、训练集/验证集分工和 MIPROv2 optimization flow | 进入行业笔记候选 |
| practice-arize-gepa-vs-prompt-learning | skimmed | high | Arize Blog: GEPA vs Prompt Learning | 2025-11-17 | https://arize.com/blog/gepa-vs-prompt-learning-benchmarking-different-prompt-optimization-approaches/ | GEPA / prompt learning / benchmark | 厂商 benchmark 和方法比较；可用作工程视角，需标注 vendor caveat | 需整理到行业实践，提升比例不直接当作本项目结论 |
| practice-arize-phoenix-prompt-optimization-techniques | skimmed | high | Arize Phoenix Prompt Optimization Techniques |  | https://arize.com/docs/phoenix/cookbook/prompt-engineering/prompt-optimization | prompt optimization / experiment tracking | 其它平台批次 strong；包含 jailbreak-classification dataset、prompt version、experiment、evaluator 和多种优化技术对比 | 进入行业笔记候选 |
| practice-arize-phoenix-judge-prompt-optimization | skimmed | high | Arize Phoenix LLM-as-a-Judge Prompt Optimization |  | https://arize.com/docs/phoenix/cookbook/prompt-engineering/llm-as-a-judge-prompt-optimization | judge prompt optimization / eval | 包含 dataset、task、evaluators、few-shot/style/self-refinement/combined experiments | 需整理 |
| practice-arize-ax-prompt-learning | skimmed | high | Arize AX Prompt Optimization / Prompt Learning |  | https://arize.com/docs/ax/prompts/prompt-optimization | prompt learning / prompt hub | 记录 initial prompt -> outputs -> evaluators -> optimized prompt -> iteration；含 versioning / rollback / experiments 说明 | 需整理 |
| practice-langchain-promptim | skimmed | high | LangChain Promptim | 2024-11-13 | https://www.langchain.com/blog/promptim | prompt optimization library / LangSmith | 其它平台批次 strong，Twitter/X 批次也追溯到该官方博客；初始 prompt、dataset、custom evaluators、optional human feedback、LangSmith tracking、train/dev/test split | 进入行业笔记候选，区分 Promptim 与第三方 AutoPrompt |
| practice-langchain-exploring-prompt-optimization | skimmed | medium | LangChain Exploring Prompt Optimization | 2025-01-28 | https://www.langchain.com/blog/exploring-prompt-optimization | prompt optimization / promptim | LangChain 官方 blog，适合作为 Promptim 背景和边界材料 | 需整理 |
| practice-langchain-agent-context-engineering | skimmed | high | LangChain Context Engineering in Agents |  | https://docs.langchain.com/oss/python/langchain/context-engineering | context engineering / agents | 其它平台批次 strong；区分 system prompt、messages、tools、model、response format 和 middleware | 作为 prompt optimization 边界材料 |
| practice-langchain-deepagents-context-engineering | skimmed | high | LangChain Deep Agents Context Engineering |  | https://docs.langchain.com/oss/python/deepagents/context-engineering | context engineering / deep agents | 记录 input context、runtime context、context compression、subagent isolation 和 long-term memory | 作为 agent/context 边界材料 |
| practice-langfuse-prompt-tracing | skimmed | high | Langfuse Link Prompt Management with Tracing |  | https://langfuse.com/faq/all/link-prompt-management-with-tracing | prompt versioning / observability | 说明 prompt version 与 trace/output quality 关联方式 | 需整理 |
| practice-langfuse-promptfoo-integration | skimmed | medium | Langfuse Promptfoo Integration |  | https://langfuse.com/integrations/other/promptfoo | eval integration / prompt management | Promptfoo evals + Langfuse-managed prompts；适合作为工具链组合线索 | 需判断是否深读 |
| practice-humanloop-evaluators | skimmed | high | Humanloop Evaluators |  | https://humanloop.com/docs/explanation/evaluators | evaluators / online monitoring / offline eval | 说明 online monitoring、offline evaluation、datasets as test cases、logs 和 aggregated scores | 需整理 |
| practice-weaviate-dspy-optimizers | skimmed | high | Weaviate: Your Language Model Deserves Better Prompting | 2024-04-17 | https://weaviate.io/blog/dspy-optimizers | DSPy / RAG / prompt optimization | 包含 RAG trainset、metric、BootstrapFewShot、COPRO、MIPRO 概念 | 进入行业笔记候选 |
| practice-weaviate-dspy-integration | skimmed | medium | Weaviate DSPy Integration |  | https://weaviate.io/developers/weaviate/more-resources/dspy | RAG / DSPy integration | Weaviate + DSPy notebooks 和资料索引 | 需判断相关性 |
| practice-weaviate-context-engineering | skimmed | high | Weaviate Context Engineering | 2025-12-09 | https://weaviate.io/blog/context-engineering | context engineering / RAG / memory | 记录 context window、retrieval、memory、tools、failure modes 和 context/prompt 边界 | 作为 context engineering 边界材料 |
| practice-opik-optimizer-overview | skimmed | high | Opik Optimization Algorithms Overview |  | https://www.comet.com/docs/opik/agent_optimization/algorithms/overview | OPIK / agent optimizer / prompt optimization | 官方 docs；`ChatPrompt` + dataset + metric，MetaPrompt/HRPO/Few-shot Bayesian/Evolutionary/GEPA/Parameter 等 optimizer | 进入行业笔记候选 |
| practice-opik-g-eval | skimmed | high | Opik G-Eval Metrics |  | https://www.comet.com/docs/opik/evaluation/metrics/g_eval/ | LLM-as-judge / eval metrics | 官方 docs；task introduction、evaluation criteria、score normalization 和多类内置 judge | 需整理 |
| practice-parea-docs | skimmed | medium | Parea AI Docs |  | https://docs.parea.ai/ | experiments / observability |  | 需判断相关性 |
| practice-parea-deployed-prompts | skimmed | medium | Parea AI Deployed Prompts |  | https://docs.parea.ai/platform/deployment | prompt deployment |  | 需判断相关性 |
| practice-aws-bedrock-prompt-optimization | candidate | medium | Amazon Bedrock advanced prompt optimization and migration tool | 2026-05-14 | https://aws.amazon.com/blogs/aws/amazon-bedrock-introduces-new-advanced-prompt-optimization-and-migration-tool/ | prompt optimizer product / vendor | 通用广搜（RSS）净新增；尚未覆盖的厂商 optimizer，补充工具地图 WPI-07/09；仅登记未深读 | 核验是否提供 dataset/metric/baseline/cost/rollback，再决定入工具实践 |
| qa-vertex-prompt-optimizer-lock-sections | candidate | medium | How to Lock Sections of a Prompt Using placeholder_to_content in Vertex AI Prompt Optimizer | 2024-10-29 | https://stackoverflow.com/questions/79138180 | prompt optimizer / frozen-mutable boundary | 通用广搜（Stack Overflow）净新增；对应「冻结/可变段落」边界，呼应 frozen-evaluator / mutable-object 约束 | 作为 frozen/mutable 段落工程线索，深读核验官方 placeholder 机制 |
| signal-hn-ai-evals-half-baked | candidate | low | Ask HN: What tools are you using for AI evals? Everything feels half-baked | 2025-06-05 | https://news.ycombinator.com/item?id=44194187 | community pain signal / eval tooling | 通用广搜（HN）净新增；社区痛点信号，佐证 WPI-01/WPI-05「eval 基础设施不成熟、需自建闭环」；非效果证据 | 作为痛点/问题意识线索，进入最终报告时只标为 social signal |
| repo-linshenkx-prompt-optimizer | skimmed | high | linshenkx/prompt-optimizer | 2025-02-12 | https://github.com/linshenkx/prompt-optimizer | prompt optimizer / prompt asset evaluation | GitHub 快筛严格保留；core4 clone 固定 commit `d7cde6c2fc5c56a579d803d485ad170788a4141e`；审计草稿见 `docs/github_repo_audit_notes/repo-linshenkx-prompt-optimizer.md` | 已完成第一轮源码审计；后续提炼 compare/evaluation/rewrite 链路，但需运行核验效果 |
| repo-gepa-ai-gepa | skimmed | high | gepa-ai/gepa | 2025 | https://github.com/gepa-ai/gepa | reflective text evolution / prompt optimizer | Twitter/X 批次追溯到 GEPA 官方实现；arXiv `2507.19457` 已在论文清单登记 | 进入 GEPA 深读和 baseline 设计，核验 reproduction artifact、tasks、rollout 和 cost |
| repo-salesforce-promptomatix | skimmed | high | SalesforceAIResearch/promptomatix | 2025 | https://github.com/SalesforceAIResearch/promptomatix | automatic prompt optimization framework | Twitter/X 批次由 Salesforce AI Research 发布帖追溯；关联 arXiv `2507.14241` | 进入工具框架深读，核验 DSPy 依赖、synthetic data、feedback 和 CLI/API |
| repo-microsoft-promptwizard | skimmed | high | microsoft/PromptWizard | 2024 | https://github.com/microsoft/PromptWizard | task-aware prompt optimization / self-evolving refinement | Twitter/X 批次由 Microsoft Research 线索追溯；关联 arXiv `2405.18369` | 进入 baseline 候选，核验 instruction/example 联合优化和 API 依赖 |
| repo-scale3-dspyground | candidate | high | Scale3-Labs/dspyground | 2026 | https://github.com/Scale3-Labs/dspyground | agent prompt optimization / GEPA harness | Twitter/X 批次由 Tom Dörr / DSPyground 线索追溯；README 含 samples、metrics、runs history 和 AI SDK agent porting | 需深读实现，判断是否适合 agent prompt optimizer 实践案例 |
| repo-sentient-roma | candidate | medium | sentient-agi/ROMA | 2026 | https://github.com/sentient-agi/ROMA | multi-agent framework / GEPA support | Twitter/X 批次由 Sentient ROMA V2 线索追溯；release 提到 DSPy/GEPA support，但营销主张需核验 | 暂作 agent prompt optimizer 线索，深读前不采信性能主张 |
| repo-eladlev-autoprompt | candidate | medium | Eladlev/AutoPrompt | 2024 | https://github.com/Eladlev/AutoPrompt | prompt optimization framework / intent-based calibration | Twitter/X 批次由 LangChain AutoPrompt 帖追溯；非 LangChain 官方 Promptim，需避免名称混淆 | 仅作工具生态线索，核验是否有可复现 eval |
| repo-karpathy-autoresearch | skimmed | high | karpathy/autoresearch | 2026-03-06 | https://github.com/karpathy/autoresearch | self-evolving agent / experiment loop | GitHub 快筛严格保留；core4 clone 固定 commit `228791fb499afffb54b46200aca536f79142f117`；审计草稿见 `docs/github_repo_audit_notes/repo-karpathy-autoresearch.md` | 已完成第一轮源码审计；可作为“优化对象与 evaluator 隔离”的结构参考，迁移到 prompt/context 需另做实验 |
| repo-dair-ai-prompt-engineering-guide | skimmed | high | dair-ai/Prompt-Engineering-Guide | 2022-12-16 | https://github.com/dair-ai/Prompt-Engineering-Guide | prompt engineering taxonomy / resource | GitHub 快筛严格保留；本地快照 `local_sources/raw/github_repo_analysis_20260608/dair-ai__Prompt-Engineering-Guide/` | 用作 taxonomy 和资料入口，不直接作为实证结论 |
| repo-humanlayer-12-factor-agents | skimmed | high | humanlayer/12-factor-agents | 2025-03-30 | https://github.com/humanlayer/12-factor-agents | agent/context engineering governance | GitHub 快筛严格保留；core4 clone 固定 commit `d20c728368bf9c189d6d7aab704744decb6ec0cc`；审计草稿见 `docs/github_repo_audit_notes/repo-humanlayer-12-factor-agents.md` | 已完成第一轮源码审计；用于提炼 prompt/context 工程治理指标，不直接作为效果证据 |
| repo-shanraisshan-claude-code-best-practice | skimmed | medium | shanraisshan/claude-code-best-practice | 2025-10-31 | https://github.com/shanraisshan/claude-code-best-practice | coding-agent workflow / memory / skills | GitHub 快筛严格保留；本地快照 `local_sources/raw/github_repo_analysis_20260608/shanraisshan__claude-code-best-practice/` | 二级参考，抽取 memory/subagent/orchestration 可评估规则 |
| repo-affaan-m-ecc | skimmed | medium | affaan-m/ECC | 2026-01-18 | https://github.com/affaan-m/ECC | agent harness / memory / eval / system prompt slimming | GitHub 快筛严格保留；core4 clone 固定 commit `90dfd9505dc860714cf3cc8216ad7bbb96d93365`；审计草稿见 `docs/github_repo_audit_notes/repo-affaan-m-ecc.md` | 已完成第一轮源码审计；继续核验运行入口、license、核心实现和 eval 证据后再提炼结论 |
| repo-f-prompts-chat | skimmed | medium | f/prompts.chat | 2022-12-05 | https://github.com/f/prompts.chat | prompt library / prompt dataset | GitHub 快筛严格保留；本地快照 `local_sources/raw/github_repo_analysis_20260608/f__prompts.chat/` | 后续需要真实 prompt 样本时再固定 commit 或 dataset snapshot |
| repo-pathwaycom-llm-app | skimmed | medium | pathwaycom/llm-app | 2023-07-19 | https://github.com/pathwaycom/llm-app | RAG / context pipeline | GitHub 快筛严格保留；本地快照 `local_sources/raw/github_repo_analysis_20260608/pathwaycom__llm-app/` | 用于 context/RAG 边界分析，不进入 APO 核心深读 |

## 待补缺口

- 更多真实生产事故、prompt 漂移和回滚案例。
- 更多 agent/tool-use 场景的失败轨迹和优化实践。
- 更多非英文任务、跨模型迁移和多模型 routing 的 prompt 优化经验。
- 更多成本、延迟和人工审核成本的定量报告。
- 更多安全边界、合规约束和不可自动改写规则的工程实践。
