---
name: article-deep-read
description: 深读一篇社交/行业文章（知乎、公众号、Twitter/X、Reddit、Hacker News、工程博客、厂商发布等），并落地为合规 industry note：来源登记、原文快照 + SHA256、主张表、证据分级、insight 提炼、下游登记联动。Use when the user gives an article URL or pastes article full text and asks to read, understand, summarize, analyze, or archive it (深读 / 总结 / 理解 / 提炼 / 建笔记 / 入库 / 落地), even if they don't say "industry note" or "行业笔记". 论文深读走 read-paper skill，GitHub 仓库审计走 github-repo-audit skill，批量广搜走 scripts/collect_sources.py，这三类不套用本流程。
---

# 社交/行业文章深读入库

目标：把一篇行业文章变成可追溯的研究证据——一份字段完整的 industry note、一份本地私有快照、三处登记联动。

本 skill 只编排步骤顺序和判断口径；字段细则的单一来源是以下三处，不要在本文件之外另造口径：

- 笔记字段与骨架：`docs/industry_notes/template.md`（目录约束另见 `docs/industry_notes/README.md`）
- 「对本项目的启发」各字段口径：`docs/insight_field_standard.md`
- 原文快照与 SHA256 约束：仓库根 `CLAUDE.md`「工作流约束」

例外：来源证据等级（strong / medium / weak）的判据此前只散落在既有笔记先例中，步骤 4 的判据表是其首个成文出处；若日后沉淀为独立 docs 文档，以 docs 为准并回收本表。

六步都不可跳——git 历史里「收敛知乎渠道证据等级」「接通追溯链」等提交，都是事后补救漏步骤付出的审计成本。

## 步骤

### 1. 登记检查

- 在 `docs/source_inventory.md` 中搜索文章 URL 和关键词，确认是否已有条目。
- 已有条目 → 复用其 `source_id`，深读后把 `status` 升为 `noted`，不要新建重复条目。
- 没有条目 → 新建 `source_id`：`practice-<渠道>-<短slug>-<年份>`（如 `practice-zhihu-hermes-agent-2026`），渠道取 zhihu / wechat / twitter / reddit / github / blog / vendor 等。
- 疑似与既有来源覆盖同一事件/方法 → 先做新颖性判断（duplicate / extension / contradiction / new-hypothesis / actionable-method / actionable-experiment）；duplicate 只更新已有条目，不建新笔记。
- 笔记文件名就是 `source_id`——inventory、笔记、快照三处靠它对齐，这是追溯链的主键。

### 2. 获取原文

按访问状态走三条分支：

1. **用户已粘贴全文 / 给了本地文件** → 访问状态 `user_provided`，直接进步骤 3。
2. **公开 URL** → WebFetch 抓取。个人博客、社交帖、新闻稿等可能失效或改动的内容需要快照；GitHub 仓库和稳定官方文档可用 commit/版本号固定，快照记「未保存；以 commit 固定」、SHA256 记 `n/a`。
3. **抓取失败或登录墙**（知乎、公众号、X 经常如此）→ 不要反复重试或绕过验证，直接请用户粘贴全文，访问状态记 `login_required` 加 `user_provided`，并在笔记中注明「直接访问触发登录/安全验证」。

版权红线：原文全文只进 `local_sources/raw/`（已 gitignore）；git 跟踪的笔记里只保留必要短摘录、段落位置和摘要，不整篇转载。

### 3. 快照 + SHA256

```powershell
# 全文存为 UTF-8（PowerShell 5.1 默认 UTF-16，必须显式指定编码）
Set-Content -Path "local_sources/raw/<source_id>.txt" -Value $fullText -Encoding utf8
(Get-FileHash -Algorithm SHA256 "local_sources/raw/<source_id>.txt").Hash
```

路径和大写 SHA256 写进笔记对应字段。快照是本地私有文件、不进 git，哈希是日后证明「笔记引用的就是这份原文」的唯一凭据——必须先存盘后取哈希，不能凭记忆填。

### 4. 写笔记

路径 `docs/industry_notes/<source_id>.md`，骨架用 `docs/industry_notes/template.md`，逐字段填写。以下是历史上最容易走偏、需要判据的部分：

**头部字段**：阅读日期填今天的绝对日期；发布日期、作者文中没有就写「未提供」，不要推测或从平台昵称臆断身份。

**证据等级（strong / medium / weak）**——对来源本身可信度的分级：

| 等级 | 判据 | 例子 |
| --- | --- | --- |
| strong | 一手来源 + 关键数据可独立核验或有可复现 artifact | 官方 postmortem 附日志/代码 |
| medium | 一手来源（作者本人、官方博客、可核验的仓库元数据），但关键主张未独立核验 | 厂商工程博客 |
| weak | 二手转述，或匿名/数据模糊化/无任何可核验 artifact | 知乎对他人项目的介绍文 |

单篇社交文章默认 weak；升级必须写出理由（如「已回到原项目 issue 核验」），裸标签不合格。

**核心主张表**——每条值得记录的主张一行，四个判断逐条落实：

- 依据位置：原文哪一段，要能让审计者翻快照定位。
- 证据类型：metric / log / case / opinion / architecture claim / design rationale / anecdote——区分「作者展示了数据」和「作者表达了观点」。
- 可信度：逐条评，不继承笔记整体等级；作者自述架构可 medium，单用户性能轶事必须 weak。
- 备注：写清核验路径（「需核验项目文档」），这是后续动作的来源。

明确区分四种话语：作者主张、可观察证据、本项目推测、已验证结论。文章说「提升了 40%」，笔记只能写「文章称提升约 40%（anecdote, weak）」。

**对本项目的启发**——字段口径以 `docs/insight_field_standard.md` 为准，两个高频错误：

- 单源不出 conclusion。单篇文章最多产出 insight（机制层认知，允许待验证）；conclusion 必须跨源证据，不能由一篇文章直接升格。
- insight 的 `evidence_strength` 用 A/B/C/D（与头部 strong/medium/weak 是两套体系，别混用）：单篇行业文章产出的 insight 默认 D（待验证），与已有 paper notes 多源印证才到 B。

helpful method 必须 `insight_supported` 指回它服务的洞见，不允许无洞见支撑的纯操作步骤。

### 5. 下游联动

1. `docs/source_inventory.md`：`status` 升 `noted`；`local_note` 记笔记路径、快照路径和 SHA256；`decision` 记后续动作。inventory 行与笔记头部的 URL、source_id、SHA256 必须逐字一致。
2. 笔记「后续动作」段明确回答：是否写入 `docs/industry_practices.md`（跨来源综合判断才进，单源观察不进）、是否影响 `docs/experiment_plan.md`（产出了实验候选才改）。
3. `CHANGELOG.md` 的 `Unreleased / Added` 增加一条：变更内容、影响范围、证据等级。

### 6. 自检

- 重新执行 `Get-FileHash`，与笔记、inventory 两处记录一致。
- 主张表每行「依据位置」能在快照中定位；引用的数字与原文逐一核对。
- 证据等级有判据句，不是裸标签。
- 没有单源 conclusion；insight 标了 A/B/C/D。
- `git status` 确认原文全文没有进入 git 跟踪目录；笔记中只有短摘录。

## 边界

- 本 skill 针对单篇文章。一次给多个 URL：先全部登记进 inventory（`candidate`），与用户确认深读优先级后逐篇执行，不并行赶工。
- 文章是论文解读 → 笔记照建，但「与论文或框架的关系」段必须指向原论文，decision 写「需深读原论文」（走 read-paper skill）；二手解读不能替代 paper note。
- 文章与已有笔记矛盾 → 新颖性判断记 contradiction，写明与哪份笔记的哪条主张冲突，不要悄悄改写旧结论。
- 粗读后发现低价值 → inventory 记 `rejected` + 原因即可，不必硬写完整笔记。
- 论文本体走 read-paper skill；GitHub 仓库审计走 github-repo-audit skill；批量广搜走 `scripts/collect_sources.py`。
