# Paper Note: TextReg

论文：TextReg: Mitigating Prompt Distributional Overfitting via Regularized Text-Space Optimization

链接：https://arxiv.org/abs/2605.21318

source_id：paper-textreg-2026

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：important-extension

阅读日期：2026-06-08

reviewed_by：Codex

local_pdf_path：`local_sources/raw/arxiv_papers/2605.21318/paper.pdf`

local_pdf_sha256：`F5F80698C4DA38BDDCD3068086BD46313A0353F7DA656A2E65A8724062BFEB51`

local_text_path：`local_sources/raw/arxiv_papers/2605.21318/paper.txt`

local_text_sha256：`A415674C70FF00808249E0032C49A03D87020279E84E379CAE1C3330AC82B268`

evidence_level：method-and-results-read

## 一句话结论

TextReg 把 prompt overfitting 解释成 representation control 问题：优化器不断追加长规则和窄规则，训练分数可能提升，但 OOD 泛化下降。它给出一个可操作方向：prompt 优化不只要生成 task gradient，还要生成 regularization gradient，控制 prompt 长度增长和规则适用范围收窄。

## 问题设定

- 任务：缓解 feedback-based prompt optimization 的 distributional overfitting。
- 优化对象：自然语言 prompt。
- 目标：source task 上优化后，在 harder variants、相关数据集和不同 test engines 上保持 OOD generalization。
- 核心概念：representational inefficiency = capacity cost x scope narrowness。

## 方法摘要

- Representational inefficiency：
  - capacity cost：prompt token length 带来的上下文和注意力成本。
  - scope narrowness：prompt 中规则只适用于狭窄样本的程度。
- TextReg 三阶段：
  - Dual-Evidence Gradient Purification：用当前 batch evidence 和 RuleBank recurrence evidence 过滤 raw textual gradients，拒绝 case patches 和 style-only updates。
  - Semantic Edit Regularization：比较前后 prompt edit，检测长度增长和规则收窄，生成 regularization gradient。
  - Regularization-Guided Prompt Update：在 task-faithful candidate 中选择最符合 regularization signal 的改写；若冲突则 task signal 优先。
- RuleBank：保存已接受 generalizable rules，并用 recurrence 作为规则泛化性的代理。

## 实验设置

- Source tasks：Logical Deduction 3 objects、Tracking Shuffled Objects 3 objects、GSM8K。
- OOD evaluation：Logical Deduction 5/7 objects、Tracking Shuffled Objects 5/7 objects、SVAMP、MultiArith。
- Test engines：Qwen2-7B-Instruct、Phi-3.5-Mini-Instruct、Llama-3-8B-Instruct、Llama-3.1-8B-Instruct。
- Optimization backend：Qwen2.5-7B-Instruct forward engine；GPT-4o backward engine；同样配置用于 TextReg 和 baselines。
- Baselines：Zero-shot CoT、TextGrad、REVOLVE。
- 指标：strict string-based exact-match accuracy。

## 主要结果

论文直接报告：

- Table 1 中 TextReg 在几乎所有 test engine/dataset pair 上达到 best 或 second-best，大多数单元格超过 TextGrad 和 REVOLVE。
- 在 Llama-3.1-8B-Instruct 上，Tracking Shuffled Objects 5/7 objects 相比 TextGrad 分别 +10.0 和 +9.9。
- 在 Llama-3-8B-Instruct 上，同一任务分别 +8.4 和 +10.3。
- 在 Phi-3.5-Mini-Instruct 上，Logical Deduction 5obj +11.8、7obj +8.8，Tracking Shuffled Objects 5obj +10.5，SVAMP +7.9，MultiArith +7.9；但 Tracking Shuffled 7obj 相比 TextGrad -0.6。
- Baselines 经常在 OOD 上低于未优化 CoT，例如 Phi-3.5-Mini-Instruct 上 REVOLVE 在 6 个数据集全低于 CoT。
- Ablation：去掉 Gradient Purification、Semantic Edit Regularization 或 Regularization-Guided Update 都会使平均 OOD accuracy 下降，说明三者非冗余。
- Resilience study：把 Gradient、Regularization 或 Optimizer 中一个角色降级为 Qwen2.5-7B-Instruct 后仍保持强性能，说明 regularization signal 有结构性，不完全依赖最强模型。

## 失败案例和局限

- 范围限制明显：论文只覆盖 single-turn reasoning with well-defined behavioral rules；开放生成、多轮 prompt、agent instructions 留作 future work。
- Rule scope 的估计依赖 LLM semantic analyzer 和 RuleBank recurrence，是代理指标，不是真实分布范围。
- 只用 strict exact-match reasoning benchmarks，和 judge/开放生成指标不同。
- Regularization 可能牺牲对少数真实边界情况的专门规则，需要任务侧判断。

## 洞见卡片

```yaml
insight: prompt overfitting 可以表现为“更长 + 更窄”，不是只表现为 dev-test gap。
evidence_type: conceptual + direct-result
paper_evidence:
  section: "1, 3, 5.2"
  table_or_figure: "Figure 1, Table 1"
  quote_or_paraphrase: "TextReg 把 overfitting 归因于 capacity cost 和 scope narrowness 的共同增长，并在 OOD 任务上超过 TextGrad/REVOLVE。"
mechanism: 长 prompt 消耗上下文容量；窄规则只修训练样本，迁移到 harder variants 时失效。
actionable_rule: prompt 优化日志应记录 length_growth 和 rule_scope_change，不只记录分数。
counterexample_or_limit: 某些高风险任务可能需要长而具体的规则，不能单纯惩罚长度。
minimal_experiment: no regularization vs length-only regularization vs scope-aware regularization。
confidence: high-for-structured-reasoning
```

```yaml
insight: 正则化可以在 text space 里实现为“批评批评”和“约束改写”，不需要可微参数。
evidence_type: method + ablation
paper_evidence:
  section: "4, 5.3"
  table_or_figure: "Figure 2, Figure 3"
  quote_or_paraphrase: "三阶段分别过滤 raw gradients、诊断 edit inefficiency、用 regularization signal 指导 prompt update；移除任一组件都会下降。"
mechanism: 先拒绝 case patches，再检查已发生的规则收窄，最后在 task-faithful edits 中选更泛化的版本。
actionable_rule: 在 APO pipeline 中加入 second-order critic，专门判断候选改写是否变长、重复、样本特化。
counterexample_or_limit: 该 critic 本身也可能误判，需要人工抽检和 OOD eval。
minimal_experiment: standard critique update vs critique + regularization critique update。
confidence: medium-high
```

## 对本项目的启发

- 我们的最小实验应加入 OOD split，而不是只做 train/dev/test 同分布。
- Prompt 候选要记录规则级 diff：新增规则、删除规则、泛化规则、case patch。
- 可先实现简化版 RuleBank：把每轮 critique 抽象成 canonical rules，并统计 recurrence。
- Hygiene 和 TextReg 可以合并：长度、重复是 capacity proxy；rule specificity 是 scope proxy。

## 可复现计划

- 最小复现任务：从 3-object 训练到 5/7-object OOD 的 toy reasoning 或结构化任务。
- 变量：
  - TextGrad-style update。
  - length penalty。
  - RuleBank + case-patch filter。
  - full TextReg-like regularized update。
- 指标：in-distribution accuracy、OOD accuracy、length growth、rule specificity、case-patch ratio。
