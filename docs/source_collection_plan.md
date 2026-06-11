# 资料搜集计划

更新时间：2026-06-08

## 目标

在进入 prompt 优化实验前，先广泛搜集和整理相关学术论文、行业经验、工程框架、产品文档和失败案例。该阶段的目标不是证明某个 prompt 优化方法有效，也不是堆砌来源数量，而是建立可追溯的证据库，优先沉淀有效 insights、可信 conclusions、可复用 helpful methods、反模式和风险边界。后续实验用于验证和演示这些产出。

资料搜集阶段必须产出：

- 来源清单：在 `docs/source_inventory.md` 中记录每个来源的链接、发布日期、类型、相关性和处理状态。
- 共创线索：外部贡献先通过 `Research Signal` issue 或来源清单登记，并记录贡献者、关联 issue 和项目内新颖性判断。
- 方法分类：把来源映射到候选生成、候选选择、反馈信号、优化对象、记忆机制和治理机制。
- 结构化笔记：核心论文使用 `docs/paper_notes/template.md` 记录，重要行业经验使用 `docs/industry_notes/template.md` 记录。
- 原文快照：对登录后可见、用户粘贴或后续可能失效的来源，将原文保存到本地忽略目录 `local_sources/raw/`，在笔记中记录路径和 SHA256；不要把第三方全文提交到 git。
- 缺口分析：明确哪些方法、场景或风险尚未覆盖。
- 洞见候选：把来源中的现象、机制、反直觉发现、边界和失败案例转化为 insight cards。
- 方法候选：把资料总结转化为 helpful methods、操作 playbook、反模式和治理建议。
- 实验候选：围绕最重要洞见或方法提出最小验证/演示候选。

## 五天交付范围

五天交付版采用“广搜 + 快筛 + 核心深读 + 初步验证”的范围控制：

- 广搜不能少：候选来源数量要足够覆盖主要方向，避免只跟随少数热门论文。
- 深读要克制：优先深读能产出高价值洞见、结论或方法的核心来源，不追求完整综述。
- 结论要分级：把证据支持、初步观察和待验证推测分开写。
- 方法要可复用：最终产出必须包含实际可做的流程、指标、风险、误用边界和回滚建议。
- 实验要最小：只验证最影响洞见可信度或方法可用性的 1-2 个问题，不实现完整 benchmark harness。

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

## 自动化辅助广搜

可使用 `scripts/collect_sources.py` 按渠道批量收集通用 posts、Q&A、论坛讨论、博客/RSS 条目和社媒线索。脚本默认只抓公开 API/RSS 中的元数据和摘要，输出到 git 忽略的 `artifacts/source_search/`，不直接修改正式来源清单。GitHub 和 arXiv 由独立渠道处理，本脚本暂不负责。

示例：

```bash
python scripts/collect_sources.py --channels hackernews,stackexchange,devto,rss --query "prompt optimization" --per-query 10 --max-results 50
```

默认渠道包含 Hacker News、DEV、Stack Exchange 和 RSS。知乎、Twitter/X、Reddit 等通用 posts 渠道需要显式指定并配置对应访问方式：

- `zhihu` / `twitter_web` / `web_search`：通过 Brave Search API 做域名限定搜索，需设置 `BRAVE_SEARCH_API_KEY`。`zhihu` 默认查 `zhihu.com` 和 `zhuanlan.zhihu.com`，`twitter_web` 默认查 `x.com` 和 `twitter.com`，`web_search` 可用 `--web-domains` 自定义域名。
- `x_api`：通过 X API v2 recent search 获取最近 7 天 posts，需设置 `X_BEARER_TOKEN`。
- `reddit`：通过 Reddit OAuth 搜索，需设置 `REDDIT_BEARER_TOKEN`，或设置 `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` 获取 app-only token。
- `stackexchange`：可选设置 `STACKEXCHANGE_KEY` 提高配额。

示例：

```bash
python scripts/collect_sources.py --channels zhihu,twitter_web,web_search --query "提示词优化" --query "prompt evolution" --web-domains medium.com substack.com
```

脚本输出仍属于候选线索，后续必须按本计划进行去重、新颖性判断、快筛和结构化笔记沉淀。不得把自动采集数量直接当作证据强度，也不得把登录后可见或受版权保护的全文写入仓库。

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
- `actionable-method`：可以直接沉淀为 helpful method、playbook、反模式或治理建议。
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
novelty_status: unknown | duplicate | extension | contradiction | new-hypothesis | actionable-method | actionable-experiment
relevance: high | medium | low
method_category:
insight_candidate:
conclusion_candidate:
helpful_method_candidate:
anti_pattern_or_limit:
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
5. 新颖性判断：标记为 `duplicate`、`extension`、`contradiction`、`new-hypothesis`、`actionable-method` 或 `actionable-experiment`。
6. 粗筛：按相关性、可复现性、是否报告 eval 和是否包含失败分析排序。
7. 深读：高优先级论文进入 `docs/paper_notes/`，高优先级行业材料进入 `docs/industry_notes/`，跨来源综合判断再写入 `docs/industry_practices.md`。
8. 综合：更新 `docs/literature_map.md` 和 `docs/industry_practices.md`，把来源归入方法分类、工程实践和开放问题。
9. 洞见化：把资料总结转化为 insight cards、核心 conclusions、helpful methods、反模式和风险边界。
10. 冻结：只有在关键洞见、证据等级、方法候选和验证候选明确后，才更新 `docs/experiment_plan.md` 进入最小实验。

## 阶段完成标准

五天交付版 M0 完成时，应至少具备：

- 50 个以上候选来源。
- 12-15 篇核心论文或框架的结构化笔记。
- 10-15 个行业实践、工具文档或工程经验来源的结构化整理，其中重要单一来源进入 `docs/industry_notes/`。
- 一份当前前沿状态图和方法 taxonomy。
- 一份证据强度说明。
- 一份资料缺口清单。
- 一份 insight / conclusion / helpful method 候选清单，并标注证据等级、适用场景、反例和误用风险。
- 2-3 个可复用方法或建议。
- 1-2 个最小验证/演示候选，每个候选说明要验证的洞见或方法、目标、假设、输入样本、模型、评估方式和成功标准。

未达到这些标准前，不实现完整 benchmark harness，不冻结长期数据集，也不声称任何 prompt 自进化方法稳定有效。

长期扩展版可继续把核心笔记扩展到 20 篇以上，并补齐更多失败案例、跨模型迁移和生产监控材料。
