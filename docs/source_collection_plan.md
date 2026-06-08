# 资料搜集计划

更新时间：2026-06-08

## 目标

在进入 prompt 优化实验前，先广泛搜集和整理相关学术论文、行业经验、工程框架、产品文档和失败案例。该阶段的目标不是证明某个 prompt 优化方法有效，而是建立可追溯的证据库，帮助后续实验选择问题、baseline、指标和风险控制方式，并支撑最终形成可执行方案或建议。

资料搜集阶段必须产出：

- 来源清单：在 `docs/source_inventory.md` 中记录每个来源的链接、发布日期、类型、相关性和处理状态。
- 共创线索：外部贡献先通过 `Research Signal` issue 或来源清单登记，并记录贡献者、关联 issue 和项目内新颖性判断。
- 方法分类：把来源映射到候选生成、候选选择、反馈信号、优化对象、记忆机制和治理机制。
- 结构化笔记：核心论文使用 `docs/paper_notes/template.md` 记录，重要行业经验使用 `docs/industry_notes/template.md` 记录。
- 原文快照：对登录后可见、用户粘贴或后续可能失效的来源，将原文保存到本地忽略目录 `local_sources/raw/`，在笔记中记录路径和 SHA256；不要把第三方全文提交到 git。
- 缺口分析：明确哪些方法、场景或风险尚未覆盖。
- 方案候选：把资料总结转化为可实际执行的方案或建议。
- 实验候选：围绕最重要判断提出最小可复现实验候选。

## 五天交付范围

五天交付版采用“广搜 + 快筛 + 核心深读 + 初步验证”的范围控制：

- 广搜不能少：候选来源数量要足够覆盖主要方向，避免只跟随少数热门论文。
- 深读要克制：优先深读能改变方案选择的核心来源，不追求完整综述。
- 结论要分级：把证据支持、初步观察和待验证推测分开写。
- 方案要可执行：最终产出必须包含实际可做的流程、指标、风险和回滚建议。
- 实验要最小：只验证最影响方案判断的 1-2 个问题，不实现完整 benchmark harness。

## 收集范围

学术来源：

- Automatic Prompt Optimization / Automatic Prompt Engineering。
- 文本梯度、自然语言 critique、反思式 prompt 改写。
- 进化算法、遗传搜索、self-referential prompt optimization。
- DSPy、MIPRO、GEPA、TextGrad 等 prompt-as-program 或 optimizer 框架。
- Context engineering、agent workflow、RAG prompt optimization、tool-use prompt optimization。
- 评测、LLM-as-judge、数据泄漏、过拟合和 benchmark 治理。

行业来源：

- 模型厂商的 prompt engineering、eval、prompt optimizer、agent 和 safety 文档。
- Prompt 管理、版本控制、observability、eval 和 rollback 工具实践。
- 工程团队公开复盘、事故报告、迁移经验和反面案例。
- 开源框架的 examples、benchmarks、issues、release notes 和 design docs。

## 来源渠道

- 论文：arXiv、ACL Anthology、OpenReview、Semantic Scholar、Papers with Code、Google Scholar。
- 工程：GitHub repos、官方文档、release notes、examples、benchmark reports。
- 行业：OpenAI、Anthropic、Google、LangSmith、Promptfoo、DSPy 等官方或半官方实践材料。
- 经验：高质量工程博客、会议分享、迁移记录和公开 incident/postmortem。

优先使用原始来源；二手综述只作为线索，不直接作为结论证据。

## 共创线索处理

公共贡献采用“低门槛线索 + 高标准沉淀”的方式。贡献者可以只提交来源和有价值的点，维护者或 reviewer 负责项目内新颖性判断。

每条外部线索至少判断：

- 它是否已经存在于 `docs/source_inventory.md`、结构化笔记或综述中。
- 它是已有观点的重复、补充、冲突、新假设，还是可执行实验。
- 它是否改变当前研究假设、风险判断、评估方式或实验优先级。
- 它下一步应该关闭、合并引用、进入深读、进入综述，还是进入实验计划。

新颖性标记使用：

- `duplicate`：已有内容，补充引用即可。
- `extension`：补充已有观点的边界、案例、指标或反例。
- `contradiction`：与已有判断冲突，需要讨论、证据或实验。
- `new-hypothesis`：形成新的可验证假设。
- `actionable-experiment`：可以直接转成最小实验候选。

完整流程见 [共创工作流](contribution_workflow.md)。

## 记录字段

每个来源至少记录：

```yaml
source_id:
suggested_by:
linked_issue:
type: paper | docs | tool | blog | benchmark | incident | repo
title:
authors_or_org:
date:
url:
status: candidate | skimmed | noted | rejected
novelty_status: unknown | duplicate | extension | contradiction | new-hypothesis | actionable-experiment
relevance: high | medium | low
method_category:
optimization_object:
feedback_signal:
selection_method:
datasets_or_tasks:
models:
baselines:
cost_reported:
safety_or_governance:
failure_cases:
local_note:
decision:
raw_snapshot_path:
raw_snapshot_sha256:
```

## 覆盖矩阵

第一轮搜集不设上限，但设置最低覆盖门槛，避免只围绕少数熟悉方法打转：

| 类别 | 第一轮最低覆盖 |
| --- | --- |
| APO / APE 综述 | 5 个来源 |
| 经典自动 prompt 优化方法 | 8 篇论文或项目 |
| 文本梯度 / 反思式优化 | 6 篇论文或项目 |
| 进化 / 自指 / 自进化方法 | 6 篇论文或项目 |
| DSPy / prompt-as-program 框架 | 5 个来源 |
| Context engineering / RAG / agent 优化 | 8 个来源 |
| Eval / judge / benchmark 治理 | 8 个来源 |
| 行业产品和工程实践 | 15 个来源 |
| 失败案例 / 风险 / 反面经验 | 5 个来源 |

## 工作流

1. 线索：外部贡献优先提交 `Research Signal` issue；内部搜集可直接登记到 `docs/source_inventory.md`。
2. 广搜：记录标题、链接、日期、摘要和初步分类，不急于写结论。
3. 留存：对登录后可见、用户粘贴或后续可能失效的来源，保存本地原文快照并记录 SHA256。
4. 去重：合并同一论文的 arXiv、会议版、项目页和代码仓库。
5. 新颖性判断：标记为 `duplicate`、`extension`、`contradiction`、`new-hypothesis` 或 `actionable-experiment`。
6. 粗筛：按相关性、可复现性、是否报告 eval 和是否包含失败分析排序。
7. 深读：高优先级论文进入 `docs/paper_notes/`，高优先级行业材料进入 `docs/industry_notes/`，跨来源综合判断再写入 `docs/industry_practices.md`。
8. 综合：更新 `docs/literature_map.md` 和 `docs/industry_practices.md`，把来源归入方法分类、工程实践和开放问题。
9. 方案化：把资料总结转化为 2-3 个可执行方案或建议。
10. 冻结：只有在关键判断、证据等级和实验候选明确后，才更新 `docs/experiment_plan.md` 进入最小实验。

## 阶段完成标准

五天交付版 M0 完成时，应至少具备：

- 50 个以上候选来源。
- 12-15 篇核心论文或框架的结构化笔记。
- 10-15 个行业实践、工具文档或工程经验来源的结构化整理，其中重要单一来源进入 `docs/industry_notes/`。
- 一份当前前沿状态图和方法 taxonomy。
- 一份证据强度说明。
- 一份资料缺口清单。
- 2-3 个可执行方案或建议。
- 1-2 个最小可复现实验候选，每个候选说明目标、假设、输入样本、模型、评估方式和成功标准。

未达到这些标准前，不实现完整 benchmark harness，不冻结长期数据集，也不声称任何 prompt 自进化方法稳定有效。

长期扩展版可继续把核心笔记扩展到 20 篇以上，并补齐更多失败案例、跨模型迁移和生产监控材料。
