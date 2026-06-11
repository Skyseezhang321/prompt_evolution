# Paper Note: CriSPO / Multi-Aspect Critique-Suggestion Prompt Optimization

论文：CriSPO: Multi-Aspect Critique-Suggestion-guided Automatic Prompt Optimization for Text Generation

链接：https://arxiv.org/abs/2410.02748

source_id：paper-crispo-2024

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：extension

阅读日期：2026-06-08

reviewed_by：Codex

local_pdf_path：`local_sources/raw/arxiv_papers/2410.02748/paper.pdf`

local_pdf_sha256：`AC76754C1E8C2265A3BE58BEA6D53A7E9900C32A17D0E309932800D49950AB3E`

local_text_path：`local_sources/raw/arxiv_papers/2410.02748/paper.txt`

local_text_sha256：`B6AB859A8896DAF3FD11CCF8B463663184FC7FFC637F64D2A1681EDBD18E673F`

evidence_level：method-results-ablation-read

## 一句话结论

CriSPO 的关键经验是：生成任务不要只给一个总分反馈，应把输出与参考答案的差异拆成多个可编辑 aspect，再把 critique 和 suggestion 一起喂给 optimizer；但这种方法仍依赖自动指标，适合做“多维错误诊断”而不是证明 prompt 已经真实泛化。

## 问题设定

- 任务：文本生成，主实验包括 summarization 和 QA。
- 优化对象：task prompt；扩展 AST 还优化用于多指标权衡的 suffix。
- 目标指标：summarization 主要用 ROUGE；AST 同时考虑 AlignScore 和 ROUGE。
- 约束：不训练模型；使用 LLM 生成多维 critique/suggestion 并做候选搜索。

## 方法摘要

- 候选如何生成：当前 prompt 先在训练样本上生成输出，再由 LLM 比较 prediction/reference，提出多 aspect critique 和 suggestion，optimizer 使用历史 top-K prompt、分数与反馈生成下一批 prompt。
- 反馈如何获得：不是单一错误说明，而是让 LLM 自动发现缺失信息、verbosity、style、faithfulness 等方面的差异。
- 如何选择候选：按任务指标评估候选，并保留历史表现较好的 prompt 进入下一轮。
- 是否使用记忆/archive：使用 top-K 历史 prompt 作为短期搜索上下文，不是长期跨任务 memory。
- 是否优化 optimizer 自身：否；但 AST 把后缀作为另一个可优化文本对象。

## 实验设置

- 数据集：4 个 summarization benchmark 和 5 个 QA benchmark。
- 模型：Claude Instant、Claude 3 Sonnet、Llama 等多种 LLM。
- baselines：manual prompt、0-shot/3-shot、OPRO。
- train/dev/test 切分：论文按任务构造训练与测试流程，结果通常报告多次平均。
- 成本或调用次数：多轮候选生成、critique/suggestion 和评估；AST 会额外引入 suffix 搜索。

## 主要结果

- 论文报告在 summarization 上相对 manual prompt 和 OPRO 有约 3-4 点 ROUGE 改善，并且 Claude 3 Sonnet 这类强模型也能继续受益。
- SAMSum 消融显示完整 CriSPO 的 ROUGE-1 F 为 44.4；去掉 critique-suggestion 降到 42.8，去掉 CoT optimization 降到 43.9，去掉 template 降到 42.2，同时去掉 critique 与 CoT 后接近 OPRO。
- 多 aspect 消融显示 no multi-aspect 版本为 41.1，显著低于 free multi-aspects 的 44.4；pre-defined aspects 与 free multi-aspects 接近，说明“要求多维诊断”比“人工预定义维度”更关键。
- AST 可在保持 ROUGE 基本不退化的情况下优化 AlignScore，用于 faithfulness/reference-similarity 的多目标权衡。

## 失败案例和局限

- 论文承认文本生成评估困难，主证据仍高度依赖 ROUGE/AlignScore 等代理指标。
- predefined aspects 没有明显超过 free multi-aspects，说明人为设计维度未必稳定带来收益。
- 适用范围主要是有 reference 的生成任务；没有证明在 agent/tool-use 或开放偏好任务中同样有效。

## 洞见卡片

```yaml
insight: 生成任务的 prompt 反馈应拆成多个可编辑 aspect，而不是只看总分或笼统 critique。
evidence_type: ablation
paper_evidence:
  section: "4.3 Ablating Key Ingredients"
  table_or_figure: "Table 2"
  quote_or_paraphrase: "no multi-aspect critique 明显低于 free multi-aspects；完整 critique-suggestion + CoT + template 最好。"
mechanism: 多维 critique 把一个低 ROUGE/低 faithfulness 结果拆成长度、覆盖、风格、事实一致性等可操作改写方向。
actionable_rule: 对生成任务做 APO 时，记录每个候选的 aspect-level feedback；不要只保存总分。
counterexample_or_limit: aspect 仍由 LLM 生成，可能受自动指标偏好和 reference 表达方式影响。
minimal_experiment: scalar metric feedback vs single critique vs multi-aspect critique-suggestion。
confidence: medium-high-for-reference-generation
```

## 对本项目的启发

- 如果我们做摘要、抽取或报告生成 prompt 优化，应把 evaluator 输出改成结构化 aspect feedback。
- 对每个候选 prompt 记录 `aspect_name`、`critique`、`suggestion`、`metric_delta`，便于事后判断哪类反馈真正有用。
- AST 提醒我们：优化对象不一定只能是完整 prompt，也可以是后置规则、format contract 或 safety suffix。

## 可复现计划

- 最小复现任务：100-300 条带 reference 的摘要或结构化抽取任务。
- 需要实现的模块：多 aspect evaluator、candidate generator、top-K prompt memory、metric + aspect 日志。
- 预计风险：自动指标和人工偏好不一致；aspect feedback 可能冗长；多目标 suffix 可能牺牲可读性。
