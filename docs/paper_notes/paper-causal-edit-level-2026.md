# Paper Note: Edit-Level Analysis / Why Prompt Optimization Works and Sometimes Doesn't

论文：Why Prompt Optimization Works, and Why It Sometimes Doesn't: A Causal-Inspired Edit-Level Analysis

链接：https://arxiv.org/abs/2605.26655

source_id：paper-causal-edit-level-2026

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：new-hypothesis

阅读日期：2026-06-08

reviewed_by：Codex

local_pdf_path：`local_sources/raw/arxiv_papers/2605.26655/paper.pdf`

local_pdf_sha256：`CB4067269B43794749130F64E9A4E78DDBF27811E33FE0C2D935446523759C9B`

local_text_path：`local_sources/raw/arxiv_papers/2605.26655/paper.txt`

local_text_sha256：`EBB79661922A05A979D5E984C8BC59593E891F603688203DDAAEAF8B8FBCA0C6`

evidence_level：analysis-results-limitation-read

## 一句话结论

这篇论文把一个常见误区讲清楚：prompt optimizer 的编辑不是“越清楚、越复杂、越多 meta instruction 越好”；不同任务类型对 edit family 的反应相反，数学和多跳任务尤其可能被复杂化和 meta-instruction 伤害。

## 问题设定

- 任务：分析 DSPy、TextGrad、GEPA 等优化轨迹中的 prompt edit。
- 优化对象：不是提出新 optimizer，而是评估不同 edit feature / motif 与 performance delta 的关系。
- 目标指标：IPTW-adjusted ACMGD 等关联性估计。
- 约束：作者明确声明是 observational analysis，不主张强因果结论。

## 方法摘要

- 候选如何生成：使用已有 optimizer 产生的 prompt pairs。
- 反馈如何获得：比较 edit 前后 performance delta。
- 如何选择候选：不涉及候选选择；重点是事后估计 edit family 的任务条件化关联。
- 是否使用记忆/archive：分析 2,095 DSPy pairs、17,708 TextGrad/GEPA pairs 等轨迹。
- 是否优化 optimizer 自身：否；提出 edit-conditioned optimizer design 的方向。

## 实验设置

- 数据集/任务组：commonsense、mathematical、logical、sequential、multihop。
- 模型：使用 GPT-4o annotation、surface text features 和 literal text-diff motifs 三种表示。
- baselines：不是 baseline 对比，而是多视角关联估计和 LOO 稳定性检查。
- train/dev/test 切分：分析已有 prompt comparison 数据。
- 成本或调用次数：主要为离线分析。

## 主要结果

- BH-FDR corrected associations 包括：Extraneous_load x sequential 为 -0.060；Metacognition x sequential 为 +0.062。
- Edit motif 层面，meta_instruction x math 为 -0.103，clarity_constraint x logical 为 -0.083，均为显著负关联。
- 表面特征复现多个方向：word_count 对应 extraneous load，step_words 对 logical/sequential 更正向，对 multihop 更负向。
- 83% headline sign patterns 在 leave-one-out exclusion 下保持方向，说明不是完全由单个数据集驱动。
- 作者强调这些是 adjusted associational contrasts，不是因果效应。

## 失败案例和局限

- 观察性研究不能证明某类 edit 导致性能变化；残余混杂来自 optimizer trajectory、backbone、组合编辑等。
- 部分 task group 只有较少数据集，sequential 等结果有 benchmark-sensitive 风险。
- 结果是 optimizer 和 benchmark 条件下的诊断启发，不能直接转成硬规则。

## 洞见卡片

```yaml
insight: prompt edit family 应该按任务类型设先验，尤其要警惕 math/multihop 中的复杂化和 meta-instruction。
evidence_type: observational-analysis
paper_evidence:
  section: "4.3 Heterogeneous Effects; 6 Conclusion"
  table_or_figure: "Table 2, Table 3, Table 4"
  quote_or_paraphrase: "meta_instruction x math 和 clarity_constraint x logical 呈显著负关联；metacognition x sequential 正关联。"
mechanism: 某些任务已经需要清晰算法步骤，额外 meta instruction 可能增加噪声或分散模型执行。
actionable_rule: 选择候选 prompt 时加入 edit-family logging 和 task-conditioned penalties。
counterexample_or_limit: 关联不是因果；需要后续做干预实验验证。
minimal_experiment: math任务上允许/禁止 meta-instruction edits；sequential任务上允许/禁止 metacognitive edits。
confidence: medium
```

## 对本项目的启发

- 每次 prompt diff 应自动标注 edit family：length、CoT、meta-instruction、clarity constraint、demo count 等。
- optimizer 不能只按分数选 prompt，还应检查 prompt 是否通过复杂化、重复和 meta 语言堆砌获得 dev 提升。
- 这篇可直接转成我们的 prompt hygiene / edit prior 实验。

## 可复现计划

- 最小复现任务：一个 math-like、一个 sequential-like、一个 multihop-like 任务。
- 需要实现的模块：prompt diff classifier、edit-family flags、task-conditioned selector、ablation gate。
- 预计风险：edit family 自动标注误差；多个编辑同时出现导致归因困难；样本量不足。
