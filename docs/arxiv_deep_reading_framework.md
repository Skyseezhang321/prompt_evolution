# arXiv 重点论文全文深读框架

更新时间：2026-06-08

输入：

- PDF 和全文抽取文本：`local_sources/raw/arxiv_papers/`
- 下载 manifest：`outputs/arxiv_paper_downloads/arxiv_key_papers_default15_20260608T140027Z.md`
- 候选清单：`outputs/arxiv_prompt_search/arxiv_focus_top80_20260608T131514Z.csv`

原则：深读结论必须来自 PDF 全文证据。摘要、标题和自动分类只能作为线索；不能把工程推演写成论文结论。

## 分层阅读流程

### L0：元数据确认

记录：

- arXiv ID、版本、标题、作者、发布时间。
- 本地 PDF 路径、文本路径、SHA256。
- 是否有代码、数据或附录。

目的：确保后续引用的是同一个版本。

### L1：问题和方法精读

必须回答：

- 论文真正要解决的问题是什么？
- 它优化的对象是什么：task prompt、system prompt、examples、workflow、tool policy、memory、optimizer prompt？
- 它使用什么反馈信号：分数、critique、textual gradient、trajectory、preference、human feedback、judge？
- 候选 prompt 如何生成？
- 候选如何选择？
- 有没有 archive、memory、beam、Pareto、bandit 或 rollback？

输出：方法机制图或 5-8 条方法要点。

### L2：实验和证据核验

必须记录：

- 数据集和任务。
- optimizer 模型与 task model。
- baselines。
- train/dev/test 切分。
- 搜索预算、调用次数、token 成本或运行时间。
- 主结果表。
- ablation。
- 失败案例或局限。

输出：证据矩阵，标注“论文直接报告”“需要推断”“未报告”。

### L3：洞见提炼

每篇论文至少产出 1-3 条 insight cards：

```yaml
insight:
evidence_type: direct-result | ablation | failure-case | author-claim | our-inference
paper_evidence:
  section:
  table_or_figure:
  quote_or_paraphrase:
mechanism:
actionable_rule:
counterexample_or_limit:
minimal_experiment:
confidence: high | medium | low
```

要求：

- `paper_evidence` 必须能追溯到论文 section、table、figure 或明确段落。
- `our-inference` 必须显式标注，不能写成论文结论。
- 如果没有实验支撑，只能作为 hypothesis。

## 论文笔记输出格式

优先使用 `docs/paper_notes/template.md`，但额外增加：

```yaml
local_pdf_path:
local_pdf_sha256:
local_text_path:
local_text_sha256:
evidence_level:
insight_cards:
```

## 深读优先顺序

第一批 P0：

1. ProTeGi：经典 textual critique + beam baseline。
2. Modular Prompt Optimization：结构化 prompt 和 section-local edit。
3. GEPA：轨迹反思 + Pareto prompt evolution。
4. SePO：optimizer prompt 自进化。
5. SPEAR：agentic optimizer + Python error analysis + rollback。

第二批 P0/P1：

- MemAPO、AutoPDL、MASPO、TextReg、PrefPO、PromptBreeder、EvoPrompt。

## 防止过度总结的规则

- 只读摘要时，结论标为 `summary-only`。
- 读了方法但没核验表格时，结论标为 `method-read`。
- 核验了实验表和 ablation 后，才能标为 `evidence-backed`。
- 如果结论来自本项目工程经验而非论文，标为 `our-engineering-inference`。
- 如果论文没有报告成本、失败或 split，不替它补。

## 本轮试读目标

本轮先验证流程，不追求读完 15 篇：

- 读 ProTeGi，产出一篇结构化深读笔记。
- 读 Modular Prompt Optimization，产出一篇结构化深读笔记。
- 更新 `arxiv_top80_insights.md` 时，只把有 PDF 证据支撑的洞见升级证据等级；其它仍保留为一读假设。
