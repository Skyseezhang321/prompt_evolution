# GitHub 仓库证据矩阵：2026-06-08

2026-06-09 补充：同步说明具体洞见入口已转移到 insight 证据卡的用户方法层；本矩阵继续作为横向证据快筛视图。

本矩阵用于把 GitHub 仓库从“资料介绍”转成可比较的研究证据。评分是第一轮人工快筛判断，不是最终结论。

2026-06-08 源码审计补充：本矩阵仍保留为横向快筛视图。`linshenkx/prompt-optimizer`、`karpathy/autoresearch`、`humanlayer/12-factor-agents` 和 `affaan-m/ECC` 已进入固定 commit 后的源码审计流程，后续 insight 优先以 [GitHub 仓库源码审计流程](github_repo_source_audit_workflow_20260608.md) 和 `docs/github_repo_audit_notes/` 为证据入口。

2026-06-08 insight 提炼补充：core4 源码审计后的 12 条候选方法/经验已整理到 [GitHub 仓库候选 insight 证据卡](github_repo_insight_cards_20260608.md)。该文档已补充“普通用户一眼看懂版”，用于把源码结构转写成具体可试方法；本矩阵不再单独承载结论提炼。

标记说明：

- `yes`：README / repo metadata 已看到明确证据。
- `partial`：有相关迹象，但需要深读或运行核验。
- `no`：当前未看到。
- `n/a`：该仓库类型不适用。
- `unknown`：本轮信息不足。

| 仓库 | 角色 | 直接优化 prompt | 自动迭代闭环 | eval / feedback | 版本 / 回滚 | 失败案例 | 可复现入口 | 实验候选价值 | 证据等级 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `linshenkx/prompt-optimizer` | prompt optimizer 工具 | yes | partial | partial | partial | unknown | yes | high | medium |
| `karpathy/autoresearch` | self-evolving research agent | no | yes | yes | partial | unknown | yes | high | medium-high |
| `humanlayer/12-factor-agents` | agent/context 工程原则 | partial | no | partial | partial | partial | n/a | high | medium |
| `dair-ai/Prompt-Engineering-Guide` | taxonomy / resource | partial | no | no | n/a | no | n/a | medium | medium as index, low as evidence |
| `affaan-m/ECC` | agent harness / skills / memory | partial | partial | partial | partial | unknown | partial | medium-high if verified | low-medium pending verification |
| `shanraisshan/claude-code-best-practice` | agentic engineering 汇编 | partial | no | partial | partial | unknown | partial | medium | low-medium |
| `f/prompts.chat` | prompt library / dataset | no | no | no | partial | no | yes | medium as data source | medium as dataset, low as method |
| `pathwaycom/llm-app` | RAG / AI pipeline templates | no | no | partial | n/a | unknown | yes | medium for context/RAG boundary | medium |
| `google-gemini/gemini-cli` | agent CLI scenario | no | no | partial | unknown | unknown | yes | low-medium as scenario | low for current scope |
| `browser-use/browser-use` | browser-agent scenario | no | no | unknown | unknown | unknown | yes | low-medium as scenario | low for current scope |

## 横向观察

1. 直接优化 prompt 的强证据很少。首轮样本中只有 `linshenkx/prompt-optimizer` 明确属于 prompt optimizer。

2. 自动迭代闭环最清晰的是 `karpathy/autoresearch`，但它优化的是研究代码和 agent program/context，不是 prompt text。它更适合作为 self-evolving loop 的结构参考。

3. eval / feedback 在 README 中常出现，但强度差异很大：
   - `karpathy/autoresearch` 有训练实验反馈闭环。
   - `linshenkx/prompt-optimizer` 有评估和比较能力描述，但需要核验实现。
   - `humanlayer/12-factor-agents`、`affaan-m/ECC` 更像工程原则或能力声明，需要转化为测试。

4. 版本、回滚、失败案例是当前最大缺口。大多数仓库即使提到 prompt、memory 或 eval，也没有显式记录 prompt diff、失败样例、成本和回滚点。

5. 最适合转成最小实验的组合不是单仓库复刻，而是跨仓库抽取：
   - `linshenkx/prompt-optimizer`：prompt asset / compare evaluation 产品闭环。
   - `karpathy/autoresearch`：self-evolving experiment loop。
   - `humanlayer/12-factor-agents`：workflow/governance eval 维度。

## 推荐进入下一步的研究问题

1. 工程产品型 prompt optimizer 是否真的优于人工 baseline，还是主要做 prompt expansion？
2. self-evolving loop 如果只允许修改 prompt/context，而不允许修改 evaluator/data，能否稳定提升 held-out 任务？
3. agent/context governance 约束会降低任务成功率，还是减少越界修改、工具误用和不可回滚失败？
4. prompt library 中真实 prompt 的结构分布能否用于构造更贴近生产的 eval 样本？
