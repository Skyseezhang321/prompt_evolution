# Paper Note: APO for Knowledge Graph Construction

论文：Automatic Prompt Optimization for Knowledge Graph Construction: Insights from an Empirical Study

链接：https://arxiv.org/abs/2506.19773

source_id：paper-apo-kg-construction-2025

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：actionable-experiment

阅读日期：2026-06-08

reviewed_by：Codex

local_pdf_path：`local_sources/raw/arxiv_papers/2506.19773/paper.pdf`

local_pdf_sha256：`794F66C9A27688D1CA9C8439049523B398E7688CD0D9ED10C29ECF914605F05D`

local_text_path：`local_sources/raw/arxiv_papers/2506.19773/paper.txt`

local_text_sha256：`555C4DA72C83238A9957275DD491C3FB89CB9748DD8BE6C0D184325CCFAA9655`

evidence_level：method-results-limitation-read

## 一句话结论

这篇论文最有用的经验是：prompt optimization 在简单抽取上可能只是小幅增益，但当 schema 复杂、输入更长、关系类型更多时收益更明显；也就是说 APO 更像是“复杂度放大器下的稳健性工具”，不是所有 KG 抽取场景都必须上。

## 问题设定

- 任务：从文本中抽取 KG triples，包括 entity、relation、triple。
- 优化对象：KG triple extraction prompt，包括 Predict、CoT、Extract-Critique-Refine 等 prompt 结构。
- 目标指标：entity/relation/triple 的 macro precision、recall、F1。
- 约束：使用固定 schema 的 canonical relations；评估 schema complexity、context length、dataset transfer 等因素。

## 方法摘要

- 候选如何生成：比较 DSPy/MIPROv2、APE、TextGrad 三类自动 prompt optimizer。
- 反馈如何获得：按 triple F1 或 precision/recall 等指标评估候选。
- 如何选择候选：由各 optimizer 内部策略选择最佳 prompt。
- 是否使用记忆/archive：DSPy 选择 few-shot candidates 和任务摘要；不是长期跨任务 memory。
- 是否优化 optimizer 自身：否。

## 实验设置

- 数据集：SynthIE、REBEL。
- 模型：Llama3.3-70B、DeepSeek V3、Qwen2.5-72B、Mistral-8x22B、Phi-4、Granite3.2-8B 等。
- baselines：baseline prompt；DSPy、APE、TextGrad 优化 prompt。
- train/dev/test 切分：按 SynthIE/REBEL 做训练、验证、测试；另做跨数据集训练/测试实验。
- 成本或调用次数：与 optimizer、schema size 和输入长度相关；论文重点报告性能而非统一成本。

## 主要结果

- Prompting strategy 实验显示所有策略经 APO 后都有收益；ECR(E-R-T) 的 triple F1 提升最高，达到 +16%。
- Llama3.3-70B 默认 Predict(E-R-T) 在 rel=100 时 triple F1 从 0.62 提升到 0.72；schema relation count 增到 800 时，优化 prompt 相对 baseline 更稳健。
- DSPy、APE、TextGrad 都超过 baseline；Table 7 中 DSPy triple F1 0.72，APE 0.69，TextGrad 0.67，DSPy略优。
- 输入长度从 1x 增到 5x/10x 后 baseline 和 optimized 都下降，但 optimized prompt 仍保持领先。
- 跨数据集 transfer 明显变弱：不同数据集训练的 optimized prompt 在目标数据集上只有约 1% F1 增益，而同数据集训练通常有约 8% 或更多。

## 失败案例和局限

- 推理模型能力比 prompt generation 模型更决定最终性能；大模型生成的 prompt 迁移到小模型可用，但不能弥补执行模型能力不足。
- 跨数据集、跨领域迁移收益显著下降，说明 few-shot 和任务摘要可能过度贴合数据分布。
- KG 抽取的 schema 和输出格式比较明确，结论不能直接外推到开放生成或 agent 任务。

## 洞见卡片

```yaml
insight: APO 的收益会随任务结构复杂度上升而更明显，尤其是 schema 大、输入长、输出格式严格的任务。
evidence_type: empirical-factor-analysis
paper_evidence:
  section: "5 Empirical Analysis; 7 Conclusions"
  table_or_figure: "Table 3, Table 4, Table 7"
  quote_or_paraphrase: "schema complexity 和 context length 增加时，优化 prompt 相对 baseline 更稳健；跨数据集收益下降。"
mechanism: 复杂 schema 下 prompt 需要明确关系选择、实体边界和输出格式；自动优化能补齐这些规则。
actionable_rule: 在跑 APO 前先标注任务复杂度变量：schema size、input length、output schema strictness。
counterexample_or_limit: 如果数据分布变化，优化 prompt 的收益会显著缩水。
minimal_experiment: 低 schema count vs 高 schema count；同域 train/dev vs 跨域 train/dev。
confidence: high-for-schema-extraction
```

## 对本项目的启发

- 选择首个复现实验时，结构化抽取比开放生成更适合，因为指标可解释且 schema complexity 可控。
- 评估报告应把提升按 relation type / label type 展开，避免只看 macro F1。
- 数据分布字段必须记录，否则无法判断 prompt 是否只是学到了训练集 schema 表达习惯。

## 可复现计划

- 最小复现任务：自建 50-100 条结构化抽取样本，设置小 schema 和大 schema 两档。
- 需要实现的模块：schema-aware evaluator、relation-level delta report、cross-domain split。
- 预计风险：LLM 输出解析错误；schema 设计影响过大；跨域样本太少导致结论不稳。
