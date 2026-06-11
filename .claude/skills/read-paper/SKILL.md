---
name: read-paper
description: 深读一篇 prompt 优化 / prompt 自进化相关论文，并产出标准化深读笔记与登记。Use when the user asks to read, deep-read, or take notes on a paper (读论文 / 精读 / 深读 / 写论文笔记), gives an arXiv ID or paper link to study, or asks to add a paper to docs/paper_notes/.
---

# 读论文并产出标准笔记

目标：把一篇论文变成一篇可追溯、字段完整的深读笔记，并完成来源登记。

本 skill 只编排步骤顺序和必填项清单；细则的单一来源是以下三处，不要在本文件之外另造口径：

- 分层精读方法与防过度总结规则：`docs/arxiv_deep_reading_framework.md`
- 「对本项目的启发」各字段口径：`docs/insight_field_standard.md`
- 原文快照与 SHA256 约束：仓库根 `CLAUDE.md`「工作流约束」

## 步骤

### 1. 查重与定位

- 在 `docs/paper_notes/` 和 `docs/source_inventory.md` 中搜索标题、arXiv ID、方法名，确认是否已有笔记或登记行。
- 已有笔记 → 转为增量更新该笔记（补证据等级、补章节），不要新建重复笔记。
- 确定 `source_id`：`paper-<方法或主题slug>-<年份>`，与 `source_inventory.md` 保持一致。

### 2. 获取原文快照（先于阅读）

- arXiv 论文：运行 `python scripts/download_arxiv_papers.py --arxiv-id <ID>`，产出 `local_sources/raw/arxiv_papers/<ID>/paper.pdf`、`paper.txt`、`metadata.json`，并在 `outputs/arxiv_paper_downloads/` 写带 SHA256 的 manifest。
- 非 arXiv 来源：手动保存到 `local_sources/raw/` 下，用 `Get-FileHash -Algorithm SHA256` 计算哈希。
- 仓库文档中只记录本地路径 + SHA256；第三方 PDF 不入库。

### 3. 分层精读（L0 → L3）

按 `docs/arxiv_deep_reading_framework.md` 执行四层：L0 元数据确认 → L1 问题和方法精读 → L2 实验和证据核验 → L3 洞见提炼。核心纪律：

- 结论必须来自 PDF 全文证据；摘要、标题、自动分类只能作线索。
- 证据矩阵区分「论文直接报告 / 需要推断 / 未报告」；论文没报告的成本、失败案例、split，不要替它补。
- 本项目自己的推断必须显式标注为 our-inference，不能写成论文结论。

### 4. 写笔记

- 路径：`docs/paper_notes/paper-<slug>-<年份>.md`，骨架用 `docs/paper_notes/template.md`，全部字段必填（含 `local_pdf_path`、`local_pdf_sha256`、`local_text_path`、`local_text_sha256`、`evidence_level`）。
- `evidence_level` 诚实描述本轮实际读到的层级。既有笔记惯用值：`method-and-results-read`、`method-results-ablation-read`、`taxonomy-read`、`summary-only` 等；建议加括号说明精读了哪些节、略读了哪些。
- 新颖性判断取值：`unknown | duplicate | extension | contradiction | new-hypothesis | actionable-method | actionable-experiment`。
- 「对本项目的启发」中 insight / conclusion / helpful method 的区分按 `docs/insight_field_standard.md`，不要混写。
- 与既有笔记的派生、对比、互证关系用 `[[source_id]]` 互链。

### 5. 登记与追踪

- `docs/source_inventory.md`：对应来源行 `status` 升为 `noted`，`local_note` 写笔记路径和日期，`decision` 写一句深读结论；无该行则按表格格式新增。
- 属于核心脉络的论文，在 `docs/literature_map.md` 核心论文表增补一行。
- `CHANGELOG.md` 的 `Unreleased / Added` 增加一条：变更内容、影响范围、证据等级。

### 6. 自检

- 笔记内的本地路径、互链 `[[source_id]]`、外部链接全部真实可达。
- 主结果数字与论文表格逐一核对；没有把单篇单次结果写成稳定规律。
- 纯文档改动不需要跑测试，但术语要与既有笔记一致（如 optimizer / task model、textual gradient 等译法）。

## 边界

- 本 skill 针对单篇论文。批量深读与跨论文综合（batch synthesis）不在范围内，另行规划。
- 行业博客、工程实践帖等非论文来源走 `docs/industry_notes/template.md`，不套用本流程。
