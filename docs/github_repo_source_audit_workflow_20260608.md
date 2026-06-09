# GitHub 仓库源码审计流程：2026-06-08

本流程用于回应 GitHub 渠道分析中的一个核心风险：不能只根据仓库名、stars、README 或二手摘要直接提炼 insight。GitHub 渠道后续结论必须先固定源码版本，再经过机器扫描、人工审计和必要运行核验。

## 当前目标

- 固定重点仓库的 commit、README SHA256、license 和本地路径。
- 先记录“源码中实际存在什么”，再归纳“它对 prompt 优化 / prompt 自进化有什么启发”。
- 明确区分三类表述：源码观察、结构迁移推断、可采信结论。

## 执行命令

第一轮只克隆 4 个核心仓库，避免一次把 8-10 个仓库全部纳入深读导致证据质量下降。

```powershell
python scripts/github_repo_clone.py --preset core4 --output-root local_sources\raw\github_repo_clones --manifest-prefix github_repo_clone_core4
```

随后对本地 clone 做机器扫描，生成 ignored JSON 审计结果和可提交的审计草稿笔记。

```powershell
python scripts/github_repo_audit.py --clone-root local_sources\raw\github_repo_clones --audit-root local_sources\raw\github_repo_audits --notes-dir docs\github_repo_audit_notes --force-notes
```

原始 clone 和 JSON audit 保存在 `local_sources/raw/`，不提交到仓库；可提交的人工审计入口保存在 `docs/github_repo_audit_notes/`。

## 第一轮固定仓库

| source_id | repository | commit | branch | 第一轮审计入口 | 当前判断 |
| --- | --- | --- | --- | --- | --- |
| `repo-linshenkx-prompt-optimizer` | `linshenkx/prompt-optimizer` | `d7cde6c2fc5c` | `develop` | [audit note](github_repo_audit_notes/repo-linshenkx-prompt-optimizer.md) | 有源码证据显示 compare evaluation、structured judge、rewrite-from-evaluation、calibration 和 E2E 测试链路存在；尚不能推出“优化后任务效果提升”。 |
| `repo-karpathy-autoresearch` | `karpathy/autoresearch` | `228791fb499a` | `master` | [audit note](github_repo_audit_notes/repo-karpathy-autoresearch.md) | 有源码证据显示 autonomous experiment loop、固定 evaluator、结果日志和回滚规则；但优化对象是训练代码，不是 prompt，迁移到 prompt self-evolution 时必须标注为结构参考。 |
| `repo-humanlayer-12-factor-agents` | `humanlayer/12-factor-agents` | `d20c728368bf` | `main` | [audit note](github_repo_audit_notes/repo-humanlayer-12-factor-agents.md) | 有文档与模板证据支持 prompt/context 应作为一等工程对象治理；这是 agent prompt/context 设计原则来源，不是方法效果证据。 |
| `repo-affaan-m-ecc` | `affaan-m/ECC` | `90dfd9505dc8` | `main` | [audit note](github_repo_audit_notes/repo-affaan-m-ecc.md) | 有实现、测试和示例痕迹支持 memory、verification loop、harness governance 等方向；README 主张较强，仍需继续核验运行入口和真实方法有效性。 |

第一轮 clone manifest：`local_sources/raw/github_repo_clones/_manifests/github_repo_clone_core4_20260608T140910Z.md`。

第一轮 audit manifest：`local_sources/raw/github_repo_audits/github_repo_audit_manifest_20260608T141030Z.md`。

## 证据等级

后续 GitHub 渠道 insight 按以下门槛处理：

| 等级 | 含义 | 能写成什么 |
| --- | --- | --- |
| L0 | 搜索结果、stars、repo metadata 或仓库名相关 | 只能作为候选线索。 |
| L1 | 固定 commit 后读过 README / docs | 可以写“仓库主张 / 文档声称”。 |
| L2 | 固定 commit 后定位到源码、配置、测试或示例路径 | 可以写“源码观察支持某机制存在”。 |
| L3 | 能在本地运行测试、示例或最小复现实验 | 可以写“在某环境和设置下可复现某行为”。 |
| L4 | 跨仓库、论文或本项目实验互相印证 | 可以进入最终报告的强结论候选。 |

当前 4 个仓库多数只达到 L2；`karpathy/autoresearch` 的结构闭环最清楚，但仍需要本项目自己的 prompt/context 版本复现实验才能升级为 L3/L4。

## 洞见提炼规则

1. 每条 insight 必须带 source_id、commit、文件路径和观察类型。
2. 如果 insight 是从非 prompt 任务迁移而来，必须写明迁移边界。
3. 不把 README 性能主张、star 数、项目热度或工具宣传语当作结论。
4. 不把“存在 eval/test 代码”直接等同于“方法有效”；只能说明该仓库具备可审计结构。
5. 能转成实验的问题优先进入 `docs/experiment_plan.md`，再实现脚本或运行实验。

## 第一轮粗结论

- GitHub 渠道更适合提供工程结构、治理流程和真实代码组织方式；直接证明 prompt optimizer 有效的证据很少。
- 当前最有价值的组合不是照搬单个仓库，而是抽取三类机制：`prompt-optimizer` 的 compare/evaluation/rewrite 链路、`autoresearch` 的优化对象与 evaluator 隔离、`12-factor-agents` 的 prompt/context 治理边界。
- ECC 类 agent harness 可以作为 memory、verification loop 和 subagent orchestration 的线索，但要晚于前三类机制进入结论层。

## 下一步

已完成：从 4 份 audit note 中提取 12 条候选 insight，并在 [GitHub 仓库候选 insight 证据卡](github_repo_insight_cards_20260608.md) 中标注证据等级、适用边界和可转实验。

后续继续：

1. 继续对 strict8 剩余仓库做相同 clone/audit，而不是直接扩写概述。
2. 从 12 条候选 insight 中选择 2-4 条进入 `docs/experiment_plan.md`，优先冻结 evaluator / data / ledger schema。
3. 选择 1 个最小实验，把 `autoresearch` 的“只允许修改目标对象、不允许修改 evaluator/data”迁移为 prompt/context 优化闭环。
