---
name: github-repo-audit
description: 对 GitHub 仓库执行本项目的证据级源码审计闭环：clone 固定 commit → 机器扫描 → 人工审计笔记 → 按 L0-L4 证据等级提炼 insight 并回填追溯链。当用户要求审计、深读、分析某个 GitHub 仓库，把仓库纳入 GitHub 渠道证据链，跑下一轮 clone/audit（如 gepa-ai/gepa、microsoft/PromptWizard、promptomatix、AutoPrompt、dspyground），或想从某个仓库源码提炼可借鉴的 insight 时使用——即使用户只说"看看这个 repo"或"这个仓库有什么值得学的"，也应走本 skill，避免跳过证据固定直接下结论。
---

# GitHub 仓库证据级审计

## 规则权威

本 skill 只编排步骤顺序和红线清单。证据等级（L0-L4）、洞见提炼规则、各仓库当前状态和待审优先级的单一来源是 `docs/github_repo_source_audit_workflow_20260608.md`，不要在本文件之外另造口径。开始前先读它；本 skill 与它冲突时以它为准，并顺手修正本 skill。

为什么有这条流程：GitHub 渠道最大的风险是把仓库名、stars、README 主张当成证据。所有进入结论层的内容必须能追溯到固定 commit 下的具体文件路径，否则整条 GitHub 渠道的证据链都会被污染。

## 流程

### 0. 登记 source_id

- 检查 `docs/source_inventory.md` 是否已登记该仓库。source_id 格式为 `repo-<owner>-<name>`（全小写、非字母数字字符转 `-`，与 `scripts/github_repo_clone.py` 的 `source_id_for()` 一致，例如 `microsoft/PromptWizard` → `repo-microsoft-promptwizard`）。
- 未登记的先补一行（status 用 `candidate`），再继续。

### 1. Clone 并固定版本

```powershell
python scripts/github_repo_clone.py --preset core4 --repo <owner/name> --output-root local_sources\raw\github_repo_clones --manifest-prefix github_repo_clone_<batch_name>
```

- 新仓库用 `--repo owner/name` 追加，可重复多次；preset 内已 clone 的仓库会复用本地副本（manifest 中 status=existing），不会重复下载。
- 脚本自动固定 commit SHA、branch、README/LICENSE SHA256，并写 manifest 到 `_manifests/`。后续所有引用都基于这次固定的 commit。
- 一轮不要超过 4-5 个新仓库：第一轮的经验是批量过大会稀释审计质量。
- 候选发现（搜索新仓库）用 `scripts/github_repo_discovery.py`，不属于本 skill 的审计单元。

### 2. 机器扫描

```powershell
python scripts/github_repo_audit.py --clone-root local_sources\raw\github_repo_clones --audit-root local_sources\raw\github_repo_audits --notes-dir docs\github_repo_audit_notes --source-id <source_id> --force-notes
```

- `--source-id` 可重复传入，只扫描指定仓库；不传则扫描 clone-root 下全部。
- 产出两类：ignored JSON audit（`local_sources/raw/github_repo_audits/`，不提交）和可提交的审计草稿笔记（`docs/github_repo_audit_notes/<source_id>.md`）。
- 注意：`--force-notes` 会覆盖已有草稿笔记。如果目标笔记已包含人工审计内容，先向用户确认或省略该参数。

### 3. 人工审计

在生成的草稿笔记上补充人工判断。只使用三类表述，且逐条标明是哪一类：

- **源码观察**：固定 commit 下能指到具体文件路径的事实。
- **结构迁移推断**：从非 prompt 任务迁移来的结构启发，必须写明迁移边界（参考 `repo-karpathy-autoresearch` 笔记的写法）。
- **可采信结论**：有跨证据支持时才能写。

重点核对 README 主张与源码实际存在的差距，把存疑处记为待核验问题，不要替仓库圆场。

### 4. 提炼 insight

每条 insight 必须带：source_id、commit、文件路径、观察类型、证据等级（L0-L4，定义见工作流文档）。追加到 `docs/github_repo_insight_cards_20260608.md`（GHI 编号顺延）或为当轮新建证据卡文档。

红线（完整版见工作流文档"洞见提炼规则"）：

- README 性能主张、stars、项目热度不能写成结论。
- 存在 eval/test 代码 ≠ 方法有效，只能说明仓库具备可审计结构。
- 能转成实验的问题进 `docs/experiment_plan.md`——先更新实验计划，再写脚本或跑实验。

### 5. 回填追溯链

三处都要更新，缺一处追溯链就断：

1. `docs/github_repo_source_audit_workflow_20260608.md`：把仓库加入或更新固定仓库表（commit、审计入口链接、当前判断），并同步"下一步"优先级。
2. `docs/source_inventory.md`：更新该 source_id 的状态和 notes（固定 commit、审计草稿路径）。
3. `CHANGELOG.md` 的 `Unreleased`：记录本轮审计范围、证据等级上限和影响面。

## 红线

- `local_sources/raw/` 下的 clone 和 JSON audit 永不提交；可提交的只有 `docs/` 下的审计笔记和 insight 卡。
- 先固定 commit 再读代码；引用一律用固定 commit 下的路径，不引用 GitHub 网页端的浮动内容。
- 审计阶段只记录"存在什么"；"意味着什么"留给 insight 卡和结论层，两者不要混写。
