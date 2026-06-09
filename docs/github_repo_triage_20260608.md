# GitHub 仓库候选快筛：2026-06-08

本页快筛 `github_repo_discovery_validation_20260608_v4` 批次中的 85 个去重仓库。该批次来自 GitHub Search API 的前 8 个查询，每个查询取 30 条结果；它是“召回优先”的 raw candidate 批次，不是已采信来源清单。

后续分析：

- [GitHub 仓库分析概述](github_repo_analysis_overview_20260608.md)
- [GitHub 仓库内容 catalog](github_repo_catalog_20260608.md)
- [GitHub 重点仓库深读](github_repo_deep_dives_20260608.md)
- [GitHub 仓库证据矩阵](github_repo_evidence_matrix_20260608.md)

参考本地 artifacts：

- JSON：`local_sources/raw/github_repo_discovery/github_repo_discovery_validation_20260608_v4.json`
- CSV：`local_sources/raw/github_repo_discovery/github_repo_discovery_validation_20260608_v4.csv`
- Markdown：`local_sources/raw/github_repo_discovery/github_repo_discovery_validation_20260608_v4.md`
- JSON SHA256：`23f49c1ff390f2bec3f247e2443f4a52c4d49160851abd18c14b21ae0053e33b`

## 为什么会混入不相关仓库

GitHub repository search 支持 `in:readme`，但 Search API 返回的 repository item 不包含 README 命中片段。也就是说，脚本知道某个仓库被查询命中，却无法直接知道命中的是 README 中哪一句。因此 v0 批次保留了所有去重结果，并用 `kept_by_min_score`、`relevance_score` 和 `keyword_hits` 做后续快筛。

这造成两类噪声：

- 热门但泛化的 awesome list、模型、框架或开发者工具仓库：README 可能包含 “prompt optimization” 或 “instruction optimization” 字样，但仓库本体不是 prompt 优化工具。
- RAG、agent、crawler、CLI 这类周边工具：对 context engineering 有边缘价值，但不是 automatic prompt optimization 或 prompt self-evolution 来源。

`unclecode/crawl4ai` 是典型例子：它在 CSV 中 `matched_queries=instruction-optimization`，但 `keyword_hits` 为空，`relevance_score=2.0`，`kept_by_min_score=False`。README 核验后，它主要是 LLM-friendly web crawler / scraper，用于把网页转成 RAG、agent 和数据管线可用的 Markdown；它可以作为 context/data-ingestion 周边工具，但不应进入 prompt optimization 核心深读。

## 快筛结论

| 层级 | 仓库 | 判断 | 处理建议 |
| --- | --- | --- | --- |
| A | `linshenkx/prompt-optimizer` | 真正命中 prompt optimizer：仓库 topics 包含 `prompt-optimization`、`prompt-optimizer`、`prompt-testing`，README 明确描述优化、测试、评估和保存 reusable prompt assets。 | 进入 `source_inventory.md`，优先深读；重点看优化流程、评估机制、prompt 版本/资产管理和是否有可复现实验。 |
| A | `karpathy/autoresearch` | 低分但重要的 raw 候选：不是 prompt optimizer，但 README 明确描述 agent 自动改代码、训练、评估、保留/丢弃实验，并把 `program.md` 作为 agent context / research org code。 | 作为 self-evolving agent / context-programming 案例进入候选；需要独立登记，不应被分数过滤掉。 |
| A- | `dair-ai/Prompt-Engineering-Guide` | 高质量 prompt engineering / context engineering 资料库，不是优化器。适合作为 taxonomy、术语和学习路径来源。 | 可进入来源清单，但标注为 survey/resource，不作为 APO 方法证据。 |
| A- | `humanlayer/12-factor-agents` | 生产 agent/context engineering 原则；README 强调可靠 LLM 应用、context window、memory、orchestration。 | 作为行业经验/工程原则候选；重点看可转化为 eval/governance 的规则。 |
| B | `shanraisshan/claude-code-best-practice` | Claude Code agentic engineering 资料汇编，包含 subagents、memory、commands、skills、context engineering 链接。 | 可作 coding-agent workflow 参考；不作为 prompt optimizer 核心来源。 |
| B | `affaan-m/ECC` | agent harness / skills / memory / token optimization / evals / system prompt slimming 方向相关，但 README 的传播指标和叙述需要核验。 | 暂作边缘重要候选；先核验真实性、license、核心文件和是否有实际 eval。 |
| B | `f/prompts.chat` | 大型 prompt library / prompt dataset；不优化 prompt，但可作为 prompt 样本来源或 prompt asset 管理参考。 | 暂不深读方法；若后续需要真实 prompt 样本，再登记。 |
| B- | `pathwaycom/llm-app` | RAG/AI pipeline templates，和 prompt 优化关系弱；更偏 context engineering、retrieval、cost/accuracy tradeoff。 | 仅在 RAG/context optimization 章节使用，不进入 APO 核心深读。 |
| C | `google-gemini/gemini-cli`、`browser-use/browser-use` | agent framework / CLI / browser automation，对 prompt 自进化不是直接证据。 | 保留为 agent eval 场景候选，当前不深读。 |
| C | `unclecode/crawl4ai` | LLM-friendly crawler/scraper，属于数据摄取工具。 | 从 prompt optimization 核心候选剔除；仅在 context/RAG 数据源工具缺口时回看。 |

## 时间分布

2026-06-08 重新通过 GitHub API 拉取了快筛后候选仓库的 `created_at`、`updated_at` 和 `pushed_at`。本地元数据：

- JSON：`local_sources/raw/github_repo_discovery/github_repo_triage_time_metadata_20260608.json`
- CSV：`local_sources/raw/github_repo_discovery/github_repo_triage_time_metadata_20260608.csv`
- JSON SHA256：`7CC9EDF94825441FF56A51854E1232ED50F56D1A23E216F5A038B293262DA28B`

统计口径：

- 严格保留集：A / A- / B / B-，共 8 个仓库。
- 宽松保留集：严格保留集 + C 级 agent eval 场景候选，共 10 个仓库。
- 最近活跃优先看 `pushed_at`，因为本轮所有候选的 `updated_at` 都在 2026-06-08 刷新，容易受到 stars、issues、metadata 等非代码活动影响。

严格保留集 8 个仓库：

| 仓库 | 创建时间 | 最近 push | 备注 |
| --- | --- | --- | --- |
| `f/prompts.chat` | 2022-12-05 | 2026-06-08 | prompt library / dataset |
| `dair-ai/Prompt-Engineering-Guide` | 2022-12-16 | 2026-03-11 | prompt engineering / context engineering 资料库 |
| `pathwaycom/llm-app` | 2023-07-19 | 2026-06-03 | RAG / AI pipeline templates |
| `linshenkx/prompt-optimizer` | 2025-02-12 | 2026-06-08 | prompt optimizer |
| `humanlayer/12-factor-agents` | 2025-03-30 | 2025-09-21 | agent/context engineering 原则 |
| `shanraisshan/claude-code-best-practice` | 2025-10-31 | 2026-06-08 | Claude Code agentic engineering 汇编 |
| `affaan-m/ECC` | 2026-01-18 | 2026-06-07 | agent harness / skills / memory / token optimization |
| `karpathy/autoresearch` | 2026-03-06 | 2026-03-26 | self-evolving research agent / context-programming 案例 |

创建时间分布：

| 口径 | 2022 | 2023 | 2024 | 2025 | 2026 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 严格保留集 8 个 | 2 | 1 | 0 | 3 | 2 |
| 宽松保留集 10 个 | 2 | 1 | 1 | 4 | 2 |

严格保留集按季度看，集中在 `2022Q4`、`2025Q1` 和 `2026Q1`：`2022Q4=2`、`2023Q3=1`、`2025Q1=2`、`2025Q4=1`、`2026Q1=2`。

最近 push 分布：

| 口径 | 0-7 天 | 8-30 天 | 31-90 天 | 91-180 天 | >180 天 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 严格保留集 8 个 | 5 | 0 | 2 | 0 | 1 |
| 宽松保留集 10 个 | 7 | 0 | 2 | 0 | 1 |

观察：

- 严格保留集不是集中在单一年份：早期 prompt 资源库多在 2022-2023，agent/context/self-evolving 相关仓库主要集中在 2025-2026。
- 8 个严格保留仓库中有 5 个在最近 7 天内有 push，说明候选集整体仍然活跃。
- 只有 `humanlayer/12-factor-agents` 的最近 push 超过 180 天，但它的内容属于原则/文档型来源，活跃度低不一定降低参考价值。
- `updated_at` 当前全部为 2026-06-08，不适合作为主要活跃度指标；后续建议固定使用 `pushed_at` 评估代码/文档更新活跃度。

## 应剔除或暂不处理的主要噪声

以下类型不应进入本阶段核心深读，除非后续问题定义转向工具生态或数据摄取：

- 泛化 awesome list：`sindresorhus/awesome`、`vinta/awesome-python`、`awesome-selfhosted/awesome-selfhosted`、`avelino/awesome-go`、`vuejs/awesome-vue` 等。
- 非 prompt 优化的模型/框架：`huggingface/transformers`、`ggml-org/llama.cpp`、`hiyouga/LlamaFactory`、`deepspeedai/DeepSpeed` 等。
- 通用开发工具或课程：`microsoft/terminal`、`junegunn/fzf`、`microsoft/Web-Dev-For-Beginners`、`mlabonne/llm-course` 等。
- RAG/agent 周边但非 prompt 优化：`HKUDS/LightRAG`、`NirDiamant/RAG_Techniques`、`QuivrHQ/quivr`、`browser-use/browser-use`、`unclecode/crawl4ai` 等。

## 对脚本的修正建议

下一轮 GitHub 搜索不应只看 raw candidate 数量，应分成两条线：

1. 高精度核心搜索：必须命中仓库 name/description/topics 中的 `prompt optimizer`、`prompt optimization`、`automatic prompt engineering`、`textgrad`、`promptbreeder`、`dspy`、`mipro`、`gepa` 等强信号。
2. 周边生态搜索：RAG、agent、context engineering、crawler、CLI、prompt library 仍可收集，但默认标为 `peripheral`，不混入核心候选排序。

CSV 的人工快筛规则：

- `kept_by_min_score=True`：优先看，但仍需人工核验。
- `keyword_hits` 为空且 `relevance_score<=2`：默认剔除，除非仓库名已知重要或人工发现强相关 README 证据。
- `matched_queries` 很多但 `keyword_hits` 为空：通常是 README 泛命中或 GitHub search 召回噪声，不应解释为强相关。
