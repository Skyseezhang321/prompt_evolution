# 行业实践整理

更新时间：2026-06-09

状态：初始种子清单，尚未覆盖完整行业经验。新增来源应先进入 `source_inventory.md`，重要单一来源使用 `docs/industry_notes/template.md` 记录，稳定的跨来源判断再汇总到本文。

## 总体判断

主流实践已经从“手写 prompt 技巧”转向“eval-driven development + prompt versioning + observability + controlled optimization”。自动优化工具有价值，但前提是有高质量测试集、评分器、日志和回滚机制。

## 可直接尝试的实践卡片

这一节面向普通用户和早期实验者，先写“今天可以怎么做”。后面的官方文档和工具条目用于解释这些卡片的来源、证据强度和产品边界。

| 具体做法 | 适用场景 | 操作步骤 | 判断是否有效 |
| --- | --- | --- | --- |
| 先建 20 条小 eval，再改 prompt。 | 任何反复使用的客服、分类、摘要、抽取、问答 prompt。 | 收集 10 条正常样本、5 条边界样本、5 条历史失败样本；写清预期输出；每次改 prompt 都跑这 20 条。 | 不是看单次对话是否顺眼，而是看通过率、格式错误和失败类型是否稳定改善。 |
| 给 prompt 建版本号和 diff。 | 团队协作或会长期复用的 prompt。 | 每次改动记录 `prompt_vX`、修改原因、diff、模型版本、参数、数据集版本和回滚点。 | 任何线上下降都能在 5 分钟内定位到是哪次 prompt/model/schema 改动。 |
| 用 validation split 防止优化器背答案。 | 使用 Promptfoo、Promptim、Vertex、Arize、OPIK 等优化工具时。 | 优化器只看 train split；选择候选看 dev split；最后只跑一次 test/hidden split。 | dev 提升但 test 掉分时，不能发布；要回到失败样本分析。 |
| 把失败输出转成 trace，而不是只保存最终答案。 | RAG、agent、工具调用、长上下文任务。 | 记录检索命中文档、工具输入输出、中间判断、judge 理由、最终输出。 | 能指出失败来自检索、工具、上下文、格式还是 instruction。 |
| 自动生成候选，人工批准发布。 | 自动 prompt optimizer 或 self-evolving agent。 | 机器可生成候选和建议，但进入主分支/生产前必须经过 eval gate、人工审查和回滚准备。 | 新 prompt 不仅指标更好，而且没有破坏安全、格式、成本和可解释性约束。 |
| 不采信厂商提升比例，采信可复现流程。 | 阅读工具博客、产品 benchmark、营销文章时。 | 抽取 dataset、metric、baseline、模型、成本、失败样例、rollback；缺一项就降级为线索。 | 同样流程能否在本项目任务上复跑，比原文提升百分比更重要。 |

## 官方与工具实践

### OpenAI

- [Prompt engineering guide](https://platform.openai.com/docs/guides/prompt-engineering) 强调不同模型和不同快照可能需要不同 prompt；复杂应用应固定模型快照，并建立测试和评估套件。
- [Evaluation best practices](https://platform.openai.com/docs/guides/evaluation-best-practices) 建议采用 eval-driven development，收集真实分布数据，持续评估，避免 vibe-based evals。
- [Prompt optimizer](https://platform.openai.com/docs/guides/prompt-optimizer/) 体现了“dataset + graders + text critiques + repeat optimization”的闭环，但文档也提示 dataset-backed Evals prompt optimizer 已进入迁移/弃用时间线，因此研究不应绑定单一托管产品。

### Anthropic / Claude

- [Prompt engineering overview](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview) 把成功标准和经验性测试放在 prompt engineering 之前。
- Claude for Sheets 支持批量运行 prompts，适合早期并行测试、人工标注和对比实验。
- 实践重点：清晰指令、示例、结构化输入、系统 prompt、输出控制，以及先定义“何为成功”。

### Google / Gemini / Vertex AI

- [Prompt design strategies](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/prompt-design-strategies) 把 prompt engineering 定义为测试驱动、迭代过程，并拆分 objective、instructions、system instructions、constraints、context、output format、few-shot examples 等组件。
- [Structure prompts](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/structure-prompts) 建议复杂 prompt 使用前缀、XML 或其他 delimiter 组织信息。
- [Data-driven prompt optimizer](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/data-driven-optimizer) 提供 prompt template、system instructions、sample prompts、custom metrics、optimization job、result analysis 的完整流程。

### DSPy

- [DSPy](https://dspy.ai/) 的核心口号是 program, don't prompt：用 typed signatures、modules 和 metrics 描述任务，再 compile 优化。
- DSPy 的 optimizer 生态包含 BootstrapFewShot、MIPROv2、GEPA 等，适合作为本项目实验 harness 的基线框架。

### LangSmith

- [Manage prompts](https://docs.langchain.com/langsmith/manage-prompts) 把 prompt 管理成版本、环境、commit tags、rollback、owners、webhooks。
- 对研究的启发：prompt 变体不应只存在于 notebook 或聊天记录里，要有 commit、diff、staging/production、自动触发 eval 的流程。

### Promptfoo

- [Prompt optimization](https://www.promptfoo.dev/docs/usage/prompt-optimization/) 使用已有 eval config 中的测试和断言优化单个 prompt/provider pair。
- 实践建议包括：先有可度量测试；优化目标保持窄；使用 validation split；避免只让优化器适配测试集。

### 其它平台快筛补充

基于 `docs/source_batches/web_search_platform_analysis_20260608.md`，其它平台批次的稳定信号不是“更多 prompt 技巧”，而是工具生态正在把 prompt 优化拆成四层：optimizer、eval/dataset、prompt versioning 和 observability。

面向最终报告的卡片化版本见 `docs/source_batches/web_search_platform_insight_cards_20260609.md`；本文只保留跨来源行业实践摘要。

- [Hugging Face DSPy GEPA cookbook](https://huggingface.co/learn/cookbook/en/dspy_gepa) 提供可运行的 GEPA 示例，包含数据集、train/val/test 切分、main LM / reflection LM、metric 和 baseline/optimized evaluation。适合作为最小复现实验参考，但结果仍需本项目重跑。
- [Arize Phoenix Prompt Optimization Techniques](https://arize.com/docs/phoenix/cookbook/prompt-engineering/prompt-optimization) 把 few-shot、meta prompting、prompt gradient 和 DSPy prompt tuning 放到同一 dataset/evaluator/experiment 框架下比较，体现了“同一任务、同一评分器、多个 prompt 版本”的工程闭环。
- [Arize AX Prompt Learning](https://arize.com/docs/ax/prompts/prompt-optimization) 把 prompt optimization 描述为 initial prompt -> outputs -> evaluators -> optimized prompt -> repeat，并强调 prompt hub versioning、rollback 和 side-by-side experiments。厂商提升比例只作为线索，不直接作为本项目结论。
- [LangChain Promptim](https://www.langchain.com/blog/promptim) 代表“只优化 prompt rewrite”的轻量库：输入 initial prompt、dataset、custom evaluators 和可选 human feedback，并把结果接入 LangSmith 追踪。
- [OPIK optimizer overview](https://www.comet.com/docs/opik/agent_optimization/algorithms/overview) 覆盖 MetaPrompt、HRPO、Few-Shot Bayesian、Evolutionary、GEPA 和 Parameter optimizer，统一输入是 `ChatPrompt`、dataset、metric，输出包括 best prompt、history、scores 和 metadata。
- [Langfuse prompt experiments](https://langfuse.com/docs/evaluation/experiments/experiments-via-ui) 和 [prompt tracing](https://langfuse.com/faq/all/link-prompt-management-with-tracing) 强调 dataset item 与 prompt variables 对齐、可选 evaluator、实验对比，以及 prompt version 与 trace/output quality 的关联。
- [Humanloop Prompts](https://humanloop.com/docs/explanation/prompts) 和 [Evaluators](https://humanloop.com/docs/explanation/evaluators) 把 prompt 的 template、model、parameters、tools 都纳入版本，并用 logs、datasets 和 evaluators 连接开发期离线评估与生产期监控。
- [Weaviate DSPy optimizers](https://weaviate.io/blog/dspy-optimizers) 和 [context engineering](https://weaviate.io/blog/context-engineering) 说明 RAG/agent 场景里 prompt optimizer 需要和 retrieval、memory、tools、context compression 区分变量；context engineering 不是单纯 prompt 改写。

因此，后续实验不应只比较“原 prompt vs 新 prompt”。每个 prompt 变体至少要绑定：数据集版本、评分器版本、模型和参数、候选生成方法、验证集/held-out 设置、成本、失败样例、prompt diff 和回滚点。

## 工程原则

1. Eval 先行：没有评分器和数据集，就不要谈自动优化。
2. Prompt 即代码：prompt、模型名、temperature、tools、输出 schema 都是版本的一部分。
3. 单变量实验：一次只优化一个 prompt/provider pair 或一个组件，否则难以归因。
4. 保留失败轨迹：失败输入、模型输出、工具调用、judge 解释和人工评论是 optimizer 的燃料。
5. 分层约束：业务目标和安全边界不可自动改写；策略、示例和措辞可以在约束内搜索。
6. 自动建议，人工发布：候选 prompt 可以自动产生，但进入主分支或生产前要经过 eval gate 和人工审查。
7. 持续监控：模型升级、数据分布变化和工具 API 改动都会让 prompt 性能衰退。

## 待核验行业案例

- [Hermes Agent 自我进化机制行业观察](industry_notes/practice-zhihu-hermes-agent-2026.md)：用户提供的知乎全文快照，提出程序性记忆、技能自动生成、技能局部 patch 优化和轨迹反哺模型训练等实践线索。当前证据等级为 weak，需核验 Hermes / OpenClaw 原始项目、issue 和文档后再纳入稳定结论。
- [Karpathy-Inspired Claude Code Guidelines 仓库分析](industry_notes/practice-github-karpathy-guidelines-2026.md)：极小但高传播的 coding agent 行为规则包，核心价值是把常见失败模式转成“先澄清、少抽象、精准改、可验证”的短约束。仓库热度可核验，但效果仍需本项目 eval 验证。

## 推荐仓库规范

- `prompts/`：存放 prompt 模板，包含 model、parameters、tools、schema。
- `evals/`：存放评测数据、评分器、rubric 和运行配置。
- `runs/`：存放每次优化运行的候选、分数、成本和轨迹摘要。
- `docs/paper_notes/`：论文笔记。
- `docs/industry_notes/`：行业经验、工程复盘、thread 和产品实践的单篇深读笔记。
- `docs/decisions/`：记录关键研究和工程决策。

## 自进化系统的生产发布门槛

- 有 hidden test set，且优化器无法读取答案。
- 有安全和合规回归集。
- 有跨模型或跨快照稳定性测试。
- 有 prompt diff 和修改理由。
- 有成本预算上限。
- 有失败自动回滚或人工审批机制。
- 有线上监控指标：成功率、拒答率、工具错误率、延迟、成本、投诉/人工差评。
