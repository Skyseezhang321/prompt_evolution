# arXiv 候选论文搜索

`scripts/arxiv_prompt_paper_search.py` 用于在资料搜集阶段批量发现 arXiv 上与 prompt optimization、prompt evolution、context engineering、agent prompt optimization 和 eval-driven prompt iteration 相关的候选论文。

脚本只抓取 arXiv 元数据，不下载或再分发 PDF/源码。输出是待人工粗筛的候选清单，不代表研究结论。

## 设计目标

- 使用 arXiv 官方 Atom API，而不是抓取网页 HTML。
- 按渠道广搜，优先提高召回率，再用轻量关键词打分辅助排序。
- 按 arXiv ID 去重，合并多个查询命中的同一论文。
- 对照 `docs/source_inventory.md` 标记已经登记过的 arXiv 论文。
- 输出 JSON、CSV、Markdown 总表和可复制进来源清单的候选行。
- 遵守 arXiv API 限速，默认请求间隔 3 秒。

## 默认查询覆盖

默认查询集合包括：

- `apo-core`: automatic prompt optimization / automatic prompt engineering。
- `prompt-evolution`: prompt evolution、evolutionary prompt、self-evolving prompt。
- `textual-gradient-critique`: textual gradient、natural language gradient、critique-suggestion、reflective prompt。
- `llm-optimizer`: LLM-as-optimizer、Optimization by Prompting。
- `instruction-search`: instruction induction、instruction optimization、prompt rewriting。
- `named-methods-classic`: AutoPrompt、RLPrompt、GrIPS、ProTeGi、OPRO、PromptBreeder、EvoPrompt。
- `named-methods-recent`: DSPy、MIPRO、TextGrad、GEPA、MemAPO、SePO、MASPO、AutoPDL、Promptomatix、promptolution、CriSPO。
- `agent-system-tool`: system prompt、agent prompt、multi-agent prompt、tool-use prompt optimization。
- `context-rag`: context engineering、RAG prompt optimization、retrieval prompt optimization。
- `eval-judge-governance`: prompt evaluation、LLM-as-judge、prompt overfitting、prompt selection。
- `human-feedback`: prompt optimization with human or preference feedback。
- `application-studies`: application-specific automatic prompt optimization。
- `broad-llm-prompt-optimization`: broad recall query for prompt + optimization + LLM.

## 使用方式

列出查询集合：

```bash
python scripts/arxiv_prompt_paper_search.py --list-queries
```

小流量连通性检查：

```bash
python scripts/arxiv_prompt_paper_search.py \
  --query-label apo-core \
  --max-results-per-query 5 \
  --page-size 5 \
  --output-dir outputs/arxiv_prompt_search_smoke
```

完整一轮广搜：

```bash
python scripts/arxiv_prompt_paper_search.py \
  --max-results-per-query 1000 \
  --page-size 200 \
  --delay-seconds 3 \
  --output-dir outputs/arxiv_prompt_search
```

输出目录位于 `outputs/` 下，默认不会提交到 git。

## 输出文件

每次运行会生成一组带 UTC 时间戳的文件：

- `arxiv_prompt_papers_*.json`: 完整结构化候选元数据。
- `arxiv_prompt_papers_*.csv`: 适合表格筛选的候选清单。
- `arxiv_prompt_papers_*.md`: 带查询覆盖、数量摘要和候选表的 Markdown 报告。
- `arxiv_inventory_rows_*.md`: 可复制到 `docs/source_inventory.md` 的新中/高相关候选行。
- `arxiv_search_summary_*.json`: 查询命中数、去重数、相关性分布和分类分布。

## 聚焦到 100 篇以内

广搜输出会保留大量边界内容。进入人工快筛前，使用 `scripts/arxiv_focus_candidates.py` 从广搜 JSON 中生成更聚焦的优先阅读清单：

```bash
python scripts/arxiv_focus_candidates.py \
  outputs/arxiv_prompt_search/arxiv_prompt_papers_YYYYMMDDTHHMMSSZ.json \
  --top-n 80 \
  --output-dir outputs/arxiv_prompt_search \
  --prefix arxiv_focus_top80
```

聚焦排序会提高这些信号的权重：

- 标题或摘要直指 automatic prompt optimization、prompt evolution、textual gradients、system/agent prompt optimization、prompt-as-program、eval governance。
- 命中多个查询渠道。
- 已在 `docs/source_inventory.md` 登记的核心锚点。
- 摘要中出现 benchmark、baseline、failure、overfitting、cost、generalization、code availability 等可复查信号。

聚焦排序会降低这些噪声：

- visual/soft prompt tuning。
- diffusion、text-to-image、text-to-video、segmentation 等偏图像生成方向。
- 仅由 broad query 命中且没有直接项目主题信号的论文。

输出文件包括 Markdown、CSV、JSON 和新候选的 `source_inventory` 行。该清单仍是人工快筛入口，不是深读结论。

## 粗筛口径

脚本的 `high`、`medium`、`low` 只是初筛信号。进入正式来源清单前仍需人工判断：

- 论文是否真的优化自然语言 prompt，而不是 soft prompt tuning、视觉 prompt 或无关 optimization。
- 是否报告可复现的任务、数据集、模型、指标、baseline 和成本。
- 是否包含失败案例、过拟合控制、验证集/测试集隔离或跨任务泛化。
- 是否能改变当前研究假设、风险判断、评估方式或实验优先级。
