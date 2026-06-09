# Paper Note: SePO / Self-Evolving Prompt Agent

论文：SePO: Self-Evolving Prompt Agent for System Prompt Optimization

链接：https://arxiv.org/abs/2606.04465

source_id：paper-sepo-2026

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：high-signal-extension

阅读日期：2026-06-08

reviewed_by：Codex

local_pdf_path：`local_sources/raw/arxiv_papers/2606.04465/paper.pdf`

local_pdf_sha256：`D8C1F86D90F370388196CC2989FC7AE7D158089E06D250BE4F0F851119941471`

local_text_path：`local_sources/raw/arxiv_papers/2606.04465/paper.txt`

local_text_sha256：`5B127EBA64784E6DB2E3F8FC8866E36D77B5F7F73DA5439217710097641B9D0C`

evidence_level：method-and-results-read

## 一句话结论

SePO 的核心洞见是：prompt 优化系统里最该被质疑的固定 prompt，往往是“负责改 prompt 的 prompt agent 自己的系统 prompt”；把 optimizer prompt 也纳入同一套演化流程，并用多任务预训练摊销成本，能把 prompt optimization 从一次性工具变成可迁移的优化技能。

## 问题设定

- 任务：优化 task agent 的 system prompt，同时优化 prompt agent 自己的 system prompt。
- 优化对象：自然语言 system prompts；不改模型权重。
- 目标：提升 math、ARC、science、code、Sudoku 等任务的测试准确率，并验证 prompt optimization skill 能跨任务迁移。
- 关键对照：Manual-CoT、TextGrad、MetaSPO、去掉 self-improvement、去掉 archive-based open-ended evolution。

## 方法摘要

- 候选如何生成：prompt agent 读取任务、当前候选 archive、评估反馈，生成 child prompt。
- 反馈如何获得：child prompt 在训练样本上被评分；相对 parent 改善则进入 archive。
- 如何选择候选：open-ended evolutionary search，维护 archive；父候选按温度化得分和 child-count 相关规则采样，改善父候选或在噪声容忍范围内的 child 会被接纳。
- 两阶段流程：
  - pre-training：把 prompt agent 自己的 system prompt 当作优化目标，在多任务池上演化。
  - fine-tuning：固定预训练得到的 prompt agent prompt，再优化目标任务的 task agent prompt。
- 是否优化 optimizer 自身：是。这是论文相对 TextGrad/MetaSPO/PromptBreeder 的主要区别。

## 实验设置

- 任务：AIME'25、ARC-AGI-1、GPQA、MBPP、Sudoku。
- 指标：AIME/GPQA/MBPP/Sudoku 使用 pass@1，ARC-AGI-1 使用 pass@3。
- 默认模型：task agent 使用 DeepSeek-V3.2；prompt agent 使用 Gemini 3.1 Pro Preview。
- 模型互换实验：task agent 使用 Gemini 3.1 Flash-Lite Preview；prompt agent 使用 Claude Opus 4.6。
- baselines：Manual-CoT、TextGrad、MetaSPO。
- 预算：TextGrad 和 SePO 共用 10 iterations、每轮 16 examples；SePO 每阶段 `G=5`、`K=2`，即每阶段 10 个 candidate prompts；结果为 5 个随机种子平均。
- 成本：TextGrad 每任务约 14.75-26.52 美元；SePO-Generalist 共享预训练 37.14 美元，摊到五个任务约每任务 7.43 美元，再加各任务 fine-tuning 2.41-15.51 美元。

## 主要结果

论文直接报告：

- 默认模型下，SePO-Generalist 在五个任务全列最佳，平均准确率从 Manual-CoT 的 71.89 提升到 76.38，提升 4.49 点。
- SePO-Specialist 平均为 74.09，也超过 Manual-CoT，但落后 SePO-Generalist 2.29 点，说明多任务预训练比每任务单独预训练更有效。
- TextGrad 平均 70.39、MetaSPO 平均 71.32，均低于 Manual-CoT；论文将其归因于 optimizer 本身固定，以及 MetaSPO 学到的是单一 global prompt 而非可迁移的优化技能。
- 组件消融：去掉 self-improvement 平均降到 74.94；去掉 open-ended evolution 平均降到 72.64。去掉 self-improvement 对 ARC-AGI-1 伤害最大，去掉 archive-based evolution 对 AIME'25 伤害最大。
- 跨任务泛化：即使预训练 mixture 不含相关任务，也能超过 Manual-CoT；Sudoku 从未进入任何预训练 mixture，仍从 96.95 提升到 99.90。
- 模型互换后，SePO-Generalist 仍从 Manual-CoT 67.95 提升到 70.08，五个任务均有增益。

## 失败案例和局限

论文直接报告或可由结果支持：

- 搜索深度超过 `G=5` 后只是 modest gains，不是指数式增长；作者推测 prompt agent prompt 可能接近底层模型能力上限，但未验证。
- 评估只覆盖五个 benchmark；作者明确指出还需要 tool-use agents、multi-turn dialogue、long-horizon planning 等更广任务面，才能声称一般性。
- Archive admission 只依据 held-in score，无法约束指标没有覆盖的行为偏移；安全部署需要额外 safety-aligned eval suite。
- 自进化对象仍然只是自然语言 prompt；工具定义、检索策略、CoT scaffolds 等还没有纳入。
- 多任务 pre-training mixture 使用 greedy heuristic，不是本文重点，可能影响最终 skill 质量。

## 洞见卡片

```yaml
insight: prompt optimizer 的系统 prompt 也是一个需要训练的对象。
evidence_type: direct-method + ablation
paper_evidence:
  section: "3.2, 3.3, 4.2"
  table_or_figure: "Algorithm 1, Table 2"
  quote_or_paraphrase: "SePO 把 prompt agent 当作特殊 task agent；去掉 self-improvement 后平均准确率从 76.38 降到 74.94。"
mechanism: 固定 optimizer prompt 限制了错误分析和改写策略；预训练后的 prompt agent 内化了回归防御、保留有效结构、避免过拟合等优化原则。
actionable_rule: 我们不应只版本化 task prompt，也要版本化 optimizer prompt，并评估 optimizer prompt 的泛化能力。
counterexample_or_limit: optimizer prompt 变强依赖训练任务和评分器，指标没覆盖的行为不会自动更安全。
minimal_experiment: fixed optimizer prompt vs self-improved optimizer prompt on same downstream task set。
confidence: high
```

```yaml
insight: prompt optimization skill 可以被预训练并跨任务摊销，而不只是每个任务临时搜索。
evidence_type: direct-result
paper_evidence:
  section: "4.2 Cross-Task Generalization, Cost"
  table_or_figure: "Table 1, Figure 4, Table 7"
  quote_or_paraphrase: "SePO-Generalist 比 SePO-Specialist 平均高 2.29 点；共享预训练成本为 37.14 美元，可摊到多个任务。"
mechanism: 多任务失败模式迫使 prompt agent 学到通用优化操作，而不是记住单任务 prompt。
actionable_rule: 如果我们要长期研究 prompt evolution，应建立一组 meta-training tasks 来训练 optimizer，而不是只在单一 benchmark 上调 prompt。
counterexample_or_limit: 对高度专业任务，相关预训练任务仍然重要；ARC-AGI-1 的 related-task gap 最大。
minimal_experiment: single-task optimizer pretrain vs multi-task optimizer pretrain vs no pretrain。
confidence: medium-high
```

```yaml
insight: archive/open-ended evolution 和 self-improvement 是两种不同贡献，不能混为一谈。
evidence_type: ablation
paper_evidence:
  section: "4.2 SePO Variants"
  table_or_figure: "Table 2"
  quote_or_paraphrase: "w/o Self-Improvement 平均 74.94；w/o Open-Ended Evolution 平均 72.64；各自最伤的任务不同。"
mechanism: self-improvement 提升生成 child prompt 的能力；archive-based search 则防止线性搜索被当前候选路径锁死。
actionable_rule: 做自进化 prompt 实验时，应单独消融 optimizer prompt 训练和 archive/search policy。
counterexample_or_limit: 如果任务极简单或接近饱和，archive 的增益可能被天花板掩盖。
minimal_experiment: no-archive linear search vs archive search under fixed optimizer prompt; then add optimizer pretraining。
confidence: high
```

## 对本项目的启发

- 后续实验记录里要新增 `optimizer_prompt_version`，并把 optimizer prompt 与 task prompt 分开管理。
- “prompt 自进化”不应只表示 task prompt 自动改写；更严格定义应包含 optimizer artifact 自身进入评估闭环。
- 多任务元训练池需要单独设计，至少覆盖分类、抽取、代码、格式约束、工具调用等不同失败模式。
- 安全指标必须并入 archive admission，否则自进化过程只会朝 capability score 优化。

## 可复现计划

- 最小复现任务：3-5 个小型结构化任务，每个 50-150 条训练样本。
- 需要实现的模块：
  - optimizer prompt seed。
  - task prompt seed。
  - optimizer-prompt pretraining loop。
  - task-prompt fine-tuning loop。
  - archive admission + seed logging。
  - capability + safety dual metrics。
- 预计风险：
  - 多任务池太小导致“伪泛化”。
  - optimizer prompt 过拟合评分器习惯。
  - 成本主要来自 task agent evaluation，不来自 prompt agent。
  - 自进化结果可读但未必符合未测指标。
