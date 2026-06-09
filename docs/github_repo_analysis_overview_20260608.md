# GitHub 仓库分析概述：2026-06-08

本页是 GitHub 仓库渠道的第一层分析概述。它基于 `github_repo_discovery_validation_20260608_v4` 的 85 个 raw candidates，以及后续人工快筛后的 8 个严格保留仓库和 2 个宽松场景候选。

2026-06-09 内容整理补充：本页保留为样本口径和快筛背景。按最新 insight-first 原则整理后的 GitHub 渠道结论、helpful methods、反模式和最小验证候选见 [GitHub 渠道洞见综合](github_repo_channel_synthesis_20260609.md)。

相关文档：

- 洞见综合：[GitHub 渠道洞见综合](github_repo_channel_synthesis_20260609.md)
- 快筛记录：[GitHub 仓库候选快筛](github_repo_triage_20260608.md)
- 结构化 catalog：[GitHub 仓库内容 catalog](github_repo_catalog_20260608.md)
- 重点仓库深读：[GitHub 重点仓库深读](github_repo_deep_dives_20260608.md)
- 证据矩阵：[GitHub 仓库证据矩阵](github_repo_evidence_matrix_20260608.md)

本地 artifacts：

- 首批 raw candidates：`local_sources/raw/github_repo_discovery/github_repo_discovery_validation_20260608_v4.json`
- 时间元数据：`local_sources/raw/github_repo_discovery/github_repo_triage_time_metadata_20260608.json`
- README/API 快照：`local_sources/raw/github_repo_analysis_20260608/`

## 样本口径

首轮 GitHub Search API 搜索得到 240 条原始结果，去重后 85 个仓库。人工快筛后：

- 严格保留集：8 个仓库，覆盖 A / A- / B / B-。
- 宽松保留集：10 个仓库，在严格保留集基础上增加 `google-gemini/gemini-cli` 和 `browser-use/browser-use`，仅作为 agent eval 场景候选。
- 剔除或暂不处理：75 个 raw candidates，主要是 awesome list、通用模型/框架、RAG 周边、crawler、CLI 或无强相关 README 证据的高 star 仓库。

严格保留集：

| 仓库 | 初步角色 | 处理方向 |
| --- | --- | --- |
| [`linshenkx/prompt-optimizer`](https://github.com/linshenkx/prompt-optimizer) | prompt optimizer 产品/工具 | 核心深读 |
| [`karpathy/autoresearch`](https://github.com/karpathy/autoresearch) | self-evolving research agent 案例 | 核心深读 |
| [`dair-ai/Prompt-Engineering-Guide`](https://github.com/dair-ai/Prompt-Engineering-Guide) | prompt/context engineering 资料库 | taxonomy / 背景 |
| [`humanlayer/12-factor-agents`](https://github.com/humanlayer/12-factor-agents) | agent/context engineering 原则 | 治理和 eval 维度 |
| [`shanraisshan/claude-code-best-practice`](https://github.com/shanraisshan/claude-code-best-practice) | Claude Code agentic engineering 汇编 | workflow 参考 |
| [`affaan-m/ECC`](https://github.com/affaan-m/ECC) | agent harness / skills / memory / token optimization | 需核验重点候选 |
| [`f/prompts.chat`](https://github.com/f/prompts.chat) | prompt library / prompt dataset | prompt 样本和资产参考 |
| [`pathwaycom/llm-app`](https://github.com/pathwaycom/llm-app) | RAG / AI pipeline templates | context/RAG 参考 |

## 类型分布

这批仓库不是一个“APO 工具集合”，而是一个混合工程样本。按对本项目的价值可以分成六类：

| 类型 | 仓库 | 对本项目的意义 |
| --- | --- | --- |
| 直接 prompt 优化工具 | `linshenkx/prompt-optimizer` | 最接近自动/半自动 prompt optimization 产品形态，可分析优化对象、eval、保存与复用。 |
| self-evolving agent 实验闭环 | `karpathy/autoresearch` | 虽然优化对象不是 prompt 本身，但有“生成变体 -> 运行实验 -> 评估 -> 保留/丢弃”的自进化闭环。 |
| prompt/context engineering taxonomy | `dair-ai/Prompt-Engineering-Guide` | 用于梳理方法分类、术语和背景，不应当作实证证据。 |
| agent/context 工程治理 | `humanlayer/12-factor-agents`、`shanraisshan/claude-code-best-practice`、`affaan-m/ECC` | 提供 prompt/context/memory/tool policy 的工程约束，可转为 eval 维度和治理规则。 |
| prompt 资产/样本库 | `f/prompts.chat` | 可作为真实 prompt 样本来源或 prompt asset 管理参考，但不是优化方法。 |
| context/RAG pipeline | `pathwaycom/llm-app` | 提醒本项目不要只优化 prompt 字符串，还要区分检索、索引、数据更新和 prompt 的贡献。 |

## 时间与活跃度

严格保留集 8 个仓库创建时间分布：

| 2022 | 2023 | 2024 | 2025 | 2026 |
| ---: | ---: | ---: | ---: | ---: |
| 2 | 1 | 0 | 3 | 2 |

最近 push 分布：

| 0-7 天 | 8-30 天 | 31-90 天 | 91-180 天 | >180 天 |
| ---: | ---: | ---: | ---: | ---: |
| 5 | 0 | 2 | 0 | 1 |

观察：

- 2022-2023 的仓库主要是 prompt guide、prompt library 和 RAG pipeline，偏资料/资产/工程模板。
- 2025-2026 的仓库更集中在 agentic engineering、agent harness、prompt optimizer 和 self-evolving research agent。
- 8 个严格保留仓库中 5 个在最近 7 天内有 push，说明样本整体仍活跃。
- `updated_at` 在本轮 API 中几乎全部刷新到 2026-06-08，可能受 stars、issues、metadata 等影响；后续活跃度判断应优先用 `pushed_at`。

## 初步判断

1. GitHub 上直接面向 prompt optimization 的高相关仓库并不多。首轮严格保留样本里，真正直接做 prompt optimizer 的主要是 `linshenkx/prompt-optimizer`。

2. 工程侧的主线正在从“优化 prompt 字符串”转向“管理 prompt/context/agent workflow 的整体行为”。`humanlayer/12-factor-agents`、`shanraisshan/claude-code-best-practice` 和 `affaan-m/ECC` 都把 prompt 放在 context、memory、tool、subagent、verification loop 的系统中讨论。

3. 对 prompt self-evolution 最有启发的是 `karpathy/autoresearch`，不是因为它优化 prompt，而是因为它把 agent 的可编辑上下文、实验执行、评价和保留/丢弃动作组织成闭环。这个形态比单纯 prompt rewrite 更接近本项目想研究的“自进化”。

4. 公开 GitHub 仓库中经常提到 eval、benchmark、testing、comparison，但很多没有可复现实验记录、固定数据集或失败案例。它们更像工程经验或产品能力描述，证据等级不能直接等同论文实验。

5. `f/prompts.chat` 这类 prompt library 不是优化方法，但对本项目有潜在数据价值：可以抽取真实 prompt 样本、任务类型、prompt 结构，作为后续评测数据或 prompt asset 分析对象。

## 风险与边界

- 首轮搜索使用 `in:readme` 增加召回，但 GitHub API 不返回 README 命中片段，因此 raw candidates 噪声很高。
- star 数不能代表研究价值；`affaan-m/ECC`、`shanraisshan/claude-code-best-practice` 等传播很强，但仍需核验核心文件、license、commit 历史和可复现 eval。
- RAG/crawler/agent CLI 容易被误纳入 prompt optimization；这类仓库只能作为 context engineering 或 agent eval 场景参考。
- GitHub API 匿名 rate limit 已触发，下一轮批量抓取必须配置 `GITHUB_TOKEN` 或分批运行。

## 下一步

1. 先把 `linshenkx/prompt-optimizer`、`karpathy/autoresearch`、`humanlayer/12-factor-agents`、`dair-ai/Prompt-Engineering-Guide` 作为第一批深读对象。
2. 对 `affaan-m/ECC` 做真实性和证据核验：license、核心实现、eval 文件、版本历史、README 指标是否与 GitHub API 一致。
3. 把 `f/prompts.chat` 暂作为 prompt 样本库候选，不进入方法深读。
4. 把 `pathwaycom/llm-app` 暂放在 context/RAG 章节，只在讨论“prompt vs context vs retrieval”的边界时使用。
5. 下一轮 GitHub 搜索分成“核心 APO 强信号”和“周边生态”两套查询，不再把 raw candidates 直接混入核心排序。
