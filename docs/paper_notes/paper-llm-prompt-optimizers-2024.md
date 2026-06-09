# Paper Note: Are LLMs Good Prompt Optimizers?

论文：Are Large Language Models Good Prompt Optimizers?

链接：https://arxiv.org/abs/2402.02101

source_id：paper-llm-prompt-optimizers-2024

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：contradiction

阅读日期：2026-06-08

reviewed_by：Codex

local_pdf_path：`local_sources/raw/arxiv_papers/2402.02101/paper.pdf`

local_pdf_sha256：`07157E71D60F14332D4BF1ACE944F031C97D809D803DA4161DB891633DB93671`

local_text_path：`local_sources/raw/arxiv_papers/2402.02101/paper.txt`

local_text_sha256：`E459360777AF4C484A03A382B7EFD31A80D366DB9D40E30D170CBB17CB3B170C`

evidence_level：method-results-diagnostic-read

## 一句话结论

这篇论文的重要反例是：LLM 可以生成看起来合理的反思，但未必知道 target model 为什么错；更有效的路径可能是直接优化 target model 可执行的行为步骤，并用 instruction-following demonstration 约束它真的照做。

## 问题设定

- 任务：分析 LLM 作为 prompt optimizer 的反思与改写行为。
- 优化对象：prompt；论文另提出 Automatic Behavior Optimization (ABO)。
- 目标指标：object counting、navigate、snarks、question selection 等任务准确率。
- 约束：统一设置下隔离 LLM optimizer 的影响，区分 optimizer 和 target model。

## 方法摘要

- 候选如何生成：传统 APO 让 optimizer 反思错误并改 prompt；ABO 让 optimizer 分解 target model 的行为步骤。
- 反馈如何获得：错误样例、target model 输出和任务分数。
- 如何选择候选：比较多轮 refinement 结果。
- 是否使用记忆/archive：不是重点。
- 是否优化 optimizer 自身：否；改变优化范式，从 prompt text 转向 behavior steps。

## 实验设置

- 数据集：objectcounting、navigate、snarks、questionselection 等。
- 模型：target model 包括 Llama-2-70B-chat、GPT-3.5-Turbo；optimizer 使用 GPT 系模型。
- baselines：Zero-shot-CoT、Few-shot-CoT、APO-All-best、ABO、ABO-Ablation。
- train/dev/test 切分：按任务 benchmark 配置。
- 成本或调用次数：ABO 报告 Step 0/1/2 的迭代表现。

## 主要结果

- 作者观察到 LLM optimizer 的反思会反复给出相似反馈，且往往受自身任务先验影响，不一定识别真实错误原因。
- Llama-2-70B-chat 上，objectcounting 中 Zero-shot-CoT 为 0.425，APO-All-best 为 0.455，ABO Step 1 到 0.860，Step 2 到 0.885。
- navigate 上，Llama-2-70B-chat 的 ABO Step 2 到 0.890，超过 Few-shot-CoT 0.720 和 APO-All-best 0.660。
- GPT-3.5-Turbo 上，ABO Step 2 在 objectcounting/navigate/questionselection 分别为 0.975、0.985、0.905。
- ABO-Ablation 去掉 instruction-following demonstration 后显著下降，例如 Llama objectcounting 0.385，说明“严格遵循”口号不能替代行为示范。

## 失败案例和局限

- ABO 在部分任务上并非单调提升，例如 snarks Step 2 可低于 Step 1。
- 论文侧重诊断和新范式提示，不等价于证明 ABO 普遍优于所有 APO。
- target model 的 instruction-following 能力是核心变量，换模型后要重新验证。

## 洞见卡片

```yaml
insight: LLM optimizer 的自然语言反思可能只是合理猜测，必须用可执行行为示范约束 target model。
evidence_type: diagnostic + intervention-result
paper_evidence:
  section: "5 Findings; 6 Automatic Behavior Optimization"
  table_or_figure: "Table 2, Figure 7"
  quote_or_paraphrase: "ABO-Ablation 去掉 demonstration 后大幅下降，说明行为示范比严格遵循提示更有效。"
mechanism: optimizer 与 target model 存在能力和行为 gap；target model 不一定执行 optimizer 写出的抽象规则。
actionable_rule: 对失败 prompt，不只写新规则，还要生成一条 target model 应如何逐步执行该规则的 demonstration。
counterexample_or_limit: 行为示范会增加上下文长度，且在高能力模型或简单任务上收益可能变小。
minimal_experiment: abstract rule prompt vs rule + instruction-following demonstration vs behavior-step refinement。
confidence: medium-high-for-weak-target-models
```

## 对本项目的启发

- 把 `optimizer_reason` 和 `target_behavior_demo` 分开记录，避免把合理解释当成真实根因。
- 对弱模型或格式/步骤错误，优先尝试 behavior-level decomposition。
- 评估时要检查 target model 是否真的执行新增规则，而不是只看 prompt 是否写了规则。

## 可复现计划

- 最小复现任务：object counting 或结构化步骤任务，故意选择 instruction-following 不稳定的模型。
- 需要实现的模块：behavior step extractor、instruction-following demonstration generator、rule adherence checker。
- 预计风险：示范样例污染 test；长 prompt 成本高；ABO 可能过拟合固定步骤。
