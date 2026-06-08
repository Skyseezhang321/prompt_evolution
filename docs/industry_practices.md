# 行业实践整理

更新时间：2026-06-08

## 总体判断

主流实践已经从“手写 prompt 技巧”转向“eval-driven development + prompt versioning + observability + controlled optimization”。自动优化工具有价值，但前提是有高质量测试集、评分器、日志和回滚机制。

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

## 工程原则

1. Eval 先行：没有评分器和数据集，就不要谈自动优化。
2. Prompt 即代码：prompt、模型名、temperature、tools、输出 schema 都是版本的一部分。
3. 单变量实验：一次只优化一个 prompt/provider pair 或一个组件，否则难以归因。
4. 保留失败轨迹：失败输入、模型输出、工具调用、judge 解释和人工评论是 optimizer 的燃料。
5. 分层约束：业务目标和安全边界不可自动改写；策略、示例和措辞可以在约束内搜索。
6. 自动建议，人工发布：候选 prompt 可以自动产生，但进入主分支或生产前要经过 eval gate 和人工审查。
7. 持续监控：模型升级、数据分布变化和工具 API 改动都会让 prompt 性能衰退。

## 推荐仓库规范

- `prompts/`：存放 prompt 模板，包含 model、parameters、tools、schema。
- `evals/`：存放评测数据、评分器、rubric 和运行配置。
- `runs/`：存放每次优化运行的候选、分数、成本和轨迹摘要。
- `docs/paper_notes/`：论文笔记。
- `docs/decisions/`：记录关键研究和工程决策。

## 自进化系统的生产发布门槛

- 有 hidden test set，且优化器无法读取答案。
- 有安全和合规回归集。
- 有跨模型或跨快照稳定性测试。
- 有 prompt diff 和修改理由。
- 有成本预算上限。
- 有失败自动回滚或人工审批机制。
- 有线上监控指标：成功率、拒答率、工具错误率、延迟、成本、投诉/人工差评。
