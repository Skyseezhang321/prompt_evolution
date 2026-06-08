# Prompt Evolution Research

本仓库用于整理和实验「prompt 优化提升 / prompt 自进化」相关研究。范围覆盖学术论文、工程工具、行业最佳实践，以及后续可复现实验。

更新时间：2026-06-08

## 公开构建看板

这是一个公开实时构建中的研究项目。README 优先放置重要分析、研究过程和阶段结果，方便旁观者快速理解当前进展，而不需要先翻完整文档树。

| 项目 | 当前状态 |
| --- | --- |
| 当前阶段 | 研究框架、实验纪律和文档骨架已建立；准备进入最小可复现实验。 |
| 当前主线 | 把 prompt 优化从“改文案”转化为“带 eval、版本、失败分析和回滚的优化问题”。 |
| 第一批实验方向 | 结构化信息抽取或文本分类，先验证 manual / few-shot / APE-style / ProTeGi-style baseline。 |
| 主要风险 | eval 过拟合、LLM-as-judge 偏差、prompt 漂移、成本失控、自动优化破坏安全边界。 |
| 阅读路径 | 先读本 README，再读 [项目构建原则](docs/project_principles.md)、[研究框架](docs/research_brief.md)、[实验计划](docs/experiment_plan.md) 和 [变更记录](CHANGELOG.md)。 |

## 重要分析和判断

截至 2026-06-08，当前最值得优先验证的判断：

1. Prompt 优化的主要瓶颈正在从「prompt 文案」转向「eval 质量、失败轨迹、上下文组织和版本治理」。
2. 自然语言反思可能比纯标量 reward 更适合 prompt 级优化，因为 prompt 本身是可读、可编辑、可审计的文本对象。
3. 真正有生产价值的自进化系统必须包含约束搜索、候选隔离、离线评测、人工审核、版本回滚和持续监控。
4. 对 agent 系统而言，优化目标不应只包含最终答案准确率，还要包含工具调用正确性、拒答边界、成本、延迟、稳定性和跨模型迁移。

这些判断还不是最终结论。后续必须通过可复现实验、失败案例和指标对比来支持或修正。

## 当前分析经过

本项目目前按以下路线推进：

1. 先界定研究问题：prompt 不是孤立文本，而是 instruction、examples、context、tool policy、model parameters 和 evaluator 的组合。
2. 再整理方法脉络：从 APE、ProTeGi、OPRO、PromptBreeder、DSPy/MIPROv2 到 GEPA、Memory APO 等方向，拆解候选生成、反馈信号、候选选择和记忆机制。
3. 然后建立工程纪律：每轮实验记录 prompt diff、模型、参数、数据集、评分器、成本、失败模式和回滚点。
4. 最后做最小实验：先选评分清晰、成本低、失败可解释的任务，避免一开始引入 RAG 或复杂 agent 噪声。

## 阶段结果

已经完成：

- 建立研究框架、文献地图、行业实践、实验计划和论文笔记模板。
- 建立项目构建原则，并写入 `AGENTS.md` / `CLAUDE.md`，方便 Codex 和 Claude Code 读取。
- 建立企业微信通知入口，用于后续脚本、实验任务、定时任务和 CI 的统一消息通知。
- 建立 OpenAI / OpenRouter 最小 LLM API 客户端和 dry-run smoke test，用于后续实验前的 provider 配置检查。
- 明确第一批实验优先从“结构化信息抽取”或“文本分类”开始。

尚未完成：

- 尚未实现 benchmark harness。
- 尚未冻结第一版数据集和评分器。
- 尚未跑出 manual、few-shot、APE-style、ProTeGi-style 的可比实验结果。
- 尚未形成能支持“自进化有效”的实证结论。

## 下一步

1. 冻结首个任务、数据切分和评分器。
2. 实现 manual prompt 与 few-shot baseline。
3. 加入 APE-style 候选生成和 ProTeGi-style 失败反思。
4. 为每次运行生成 artifact，记录指标、成本、失败案例和 prompt diff。
5. 用 validation split 和 hidden test set 检查是否过拟合。

## 研究目标

核心问题不是「怎么写一个更漂亮的 prompt」，而是：

- 如何把 prompt 设计变成可度量、可复现、可回滚的优化问题。
- 如何利用 LLM 的自然语言反思能力，从失败样本、执行轨迹、人工反馈和自动评测中产生更好的指令。
- 如何让 prompt / system prompt / examples / context / tool policy 随经验积累而持续改进，同时控制漂移、过拟合和安全风险。

## 基本原则

本项目采用 [项目构建原则](docs/project_principles.md) 作为后续文档、实验和代码工作的共同约束。简要版本如下：

1. 先定义问题，不先写 prompt。
2. 最小实验优先。
3. 一次只改一个变量。
4. 每个结论必须有证据。
5. 目标驱动执行。
6. 变更可追踪。
7. 精准修改，不做无关重构。

## 当前文档

- [项目构建原则](docs/project_principles.md)：prompt 优化/自进化研究的基本工作原则和代理执行约束。
- [研究框架](docs/research_brief.md)：问题定义、研究假设、技术路线和风险。
- [文献地图](docs/literature_map.md)：自动 prompt 优化、自进化、上下文工程相关论文脉络。
- [行业实践](docs/industry_practices.md)：OpenAI、Anthropic、Google、DSPy、LangSmith、Promptfoo 等实践整理。
- [实验计划](docs/experiment_plan.md)：MVP 实验设计、基线、指标、日志字段和里程碑。
- [论文笔记模板](docs/paper_notes/template.md)：后续阅读论文时统一记录。
- [企业微信通知](docs/wecom_notification.md)：统一的企业微信机器人通知入口、配置和调用方式。
- [LLM API 客户端与 smoke test](docs/llm_clients.md)：OpenAI / OpenRouter 的最小调用入口、配置和连通性检查。
- [变更记录](CHANGELOG.md)：记录研究材料、实验和文档结构的重要变化。

## 后续工作流

1. 新论文放到 `docs/paper_notes/`，按模板写 1-2 页摘要。
2. 新实验先更新 [实验计划](docs/experiment_plan.md)，再写代码。
3. 每个 prompt 变体都要记录模型、参数、数据集、评分器、成本和失败案例。
4. 任何「自动改 prompt」的实验都必须保留原 prompt、候选 prompt、优化原因、评测结果和回滚点。

## 消息通知

所有脚本、实验任务、定时任务和 CI 流程的消息通知统一调用 `scripts/wecom_notify.py`，由它发送到企业微信机器人。真实 webhook 放在本地 `.env` 的 `WECOM_BOT_WEBHOOK` 中，不提交到仓库。

```bash
python scripts/wecom_notify.py "### Prompt Evolution 通知通道测试"
```

## LLM API smoke test

`.env.example` 中包含 OpenAI 与 OpenRouter 的本地配置模板。默认 smoke test 只输出 dry-run payload，不发送真实请求：

```bash
python scripts/llm_smoke_test.py
```

填好本地 `.env` 后，可用 `--live` 检查 provider 连通性。该检查只验证配置和基础响应解析，不作为 prompt 实验结论。
