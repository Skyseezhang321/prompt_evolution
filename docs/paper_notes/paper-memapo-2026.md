# Paper Note: MemAPO / Generalizable Self-Evolving Memory for Automatic Prompt Optimization

论文：Generalizable Self-Evolving Memory for Automatic Prompt Optimization

链接：https://arxiv.org/abs/2603.21520

source_id：paper-memapo-2026

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：new-hypothesis

阅读日期：2026-06-08

reviewed_by：Codex

local_pdf_path：`local_sources/raw/arxiv_papers/2603.21520/paper.pdf`

local_pdf_sha256：`29144EB3D8668D1D4AE41A294B3593B85DB2BD7B4720894FB0CC293F3868AD5F`

local_text_path：`local_sources/raw/arxiv_papers/2603.21520/paper.txt`

local_text_sha256：`2B977FBE5C3AABECBE8BDD541D0D4CF2913E55B0A741F9AEB94F7432ACC77B4B`

evidence_level：method-results-ablation-read

## 一句话结论

MemAPO 的核心洞见是：prompt 优化不要每个任务从零开始反思，应该把“有效策略模板”和“错误模式”分开记忆并检索复用；它把 memory 从样例缓存提升为优化器的经验资产。

## 问题设定

- 任务：跨逻辑推理、数学计算、知识密集任务的 prompt optimization。
- 优化对象：任务 prompt，并通过跨任务记忆改善候选生成。
- 目标指标：各任务 accuracy / performance，另报告优化成本。
- 约束：不训练模型；通过可编辑 memory 累积经验。

## 方法摘要

- 候选如何生成：先根据当前任务检索 memory，再用 memory-augmented prompt optimizer 生成候选 prompt。
- 反馈如何获得：评估候选后，把成功经验和失败模式转成 memory update。
- 如何选择候选：按任务表现评估，并把高价值策略写回 memory。
- 是否使用记忆/archive：是，核心是 dual memory。
- 是否优化 optimizer 自身：部分优化；optimizer 的跨任务经验通过 memory 自我演化，而不是改模型参数。

## 实验设置

- 数据集：GeoShape、AQuA-RAT、Gaokao MathQA、Gaokao Geography、Gaokao History 等跨域任务。
- 模型：Qwen3-8B、GPT-4o-mini；另比较使用更强 optimizer 的情况。
- baselines：IO、CoT、Step-Back、RaR、ProTeGi、OPRO、TextGrad、PromptBreeder、SPO。
- train/dev/test 切分：同域任务合并优化、分任务评估；另有跨域混合实验。
- 成本或调用次数：报告平均优化成本，MemAPO 通过经验复用降低成本。

## 主要结果

- GPT-4o-mini 上，MemAPO 平均表现 70.7%，强于 TextGrad 的 63.6%，且平均成本 0.31 美元，低于 TextGrad 的 0.70 美元。
- Qwen3-8B 上，MemAPO 平均表现 70.6%，在多数任务上为最佳。
- 成本分析报告 MemAPO 相比 TextGrad 在两个 backbone 上分别降低约 58.6% 和 55.7% 优化成本。
- 跨域 Gaokao MathQA + History 实验中，MemAPO 同时保持两类任务提升，优于大多数容易跨域退化的 baseline。
- 双 memory 消融显示 CTM 与 EPM 都有明显贡献；AQuA-RAT 从 61.7 提升到 80.5/77.9，双 memory 到 82.5。

## 失败案例和局限

- memory 的质量控制是关键风险；错误模板如果被检索复用，会系统性放大坏经验。
- 当前证据主要来自作者设定的任务组合，不等价于证明跨所有 prompt 优化任务都能泛化。
- self-evolving memory 仍依赖 LLM 对错误模式和策略模板的抽象质量。

## 洞见卡片

```yaml
insight: prompt optimizer 应该显式区分“可复用成功模板”和“应避免错误模式”。
evidence_type: ablation + cost-result
paper_evidence:
  section: "4.2 Main Results; 4.3 Ablation Study"
  table_or_figure: "Table 1, Table 3, Figure 2"
  quote_or_paraphrase: "CTM/EPM 单独有效，组合最佳；相比 TextGrad 显著降成本。"
mechanism: 成功模板提高候选质量，错误模式减少重复踩坑，二者让优化不必每轮从失败样本重新归纳。
actionable_rule: 本项目的 optimizer 日志应拆出 success_template_memory 和 error_pattern_memory 两张表。
counterexample_or_limit: memory 会引入跨任务迁移风险，需要检索相似度、有效期和回滚机制。
minimal_experiment: no-memory vs success-memory vs error-memory vs dual-memory。
confidence: medium
```

## 对本项目的启发

- 不要把历史 prompt 只当 archive；应提炼为“何时有效”的策略和“何时失败”的反例。
- memory 记录字段至少包含 task type、input pattern、failure type、successful edit、negative transfer flag。
- 成本指标应成为 prompt evolution 的一等指标，因为 memory 的价值不只是更高分，也包括更少迭代。

## 可复现计划

- 最小复现任务：两个相近任务加一个异质任务，例如数学 QA + 事实判断。
- 需要实现的模块：memory schema、retriever、memory update、negative-transfer audit。
- 预计风险：memory 抽象过粗；跨域检索误匹配；短期 dev 提升掩盖长期污染。
