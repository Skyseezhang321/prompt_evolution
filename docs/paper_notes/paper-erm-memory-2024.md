# Paper Note: ERM / Exemplar-Guided Reflection with Memory

论文：Efficient and Accurate Prompt Optimization: the Benefit of Memory in Exemplar-Guided Reflection

链接：https://arxiv.org/abs/2411.07446

source_id：paper-erm-memory-2024

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：extension

阅读日期：2026-06-08

reviewed_by：Codex

local_pdf_path：`local_sources/raw/arxiv_papers/2411.07446/paper.pdf`

local_pdf_sha256：`F7E332011472799F580234C5028655BEBC062B94772F74FF5608DD2E2F5D6C21`

local_text_path：`local_sources/raw/arxiv_papers/2411.07446/paper.txt`

local_text_sha256：`947F2A750C96C1AD86574DD25C7F6CCE8539ED52C7643EC3F0881A8087D56963`

evidence_level：method-results-ablation-read

## 一句话结论

ERM 的实践结论很直接：不要丢掉历史 feedback 和未选中的错误样例；把它们过滤、检索、选择性遗忘后再用于反思，能同时提高性能并减少达到峰值的优化步数。

## 问题设定

- 任务：true/false、生成、多选等 prompt optimization benchmark。
- 优化对象：人工初始 prompt。
- 目标指标：F1、accuracy、ROUGE-L。
- 约束：使用 LLM optimizer，不训练 target model。

## 方法摘要

- 候选如何生成：对错误样例用 instructive reflective meta-prompt 生成反馈，再改写 prompt；同时构建 exemplar factory。
- 反馈如何获得：当前错误样例 + 历史反馈 + exemplar memory 检索。
- 如何选择候选：沿用 ProTeGi 类 prompt search，同时用 memory 提供更强反馈。
- 是否使用记忆/archive：是，Feedback Memory 和 Exemplar Memory。
- 是否优化 optimizer 自身：否，但通过 memory 改善 optimizer 的输入上下文。

## 实验设置

- 数据集：LIAR、BBH、ETHOS、ArSarcasm、WebNLG、GSM8K、WSC。
- 模型：任务模型 Doubao-Pro；prompt optimizer GPT-4o。
- baselines：APE、ProTeGi、OPRO、PromptBreeder、EvoPrompt、GPO。
- train/dev/test 切分：按各 benchmark 配置；重复 3 次取平均。
- 成本或调用次数：重点报告达到 peak performance 的 optimization steps。

## 主要结果

- zero-shot setting 下，ERM 在 LIAR 为 68.6，ProTeGi 为 58.5，提升 10.1 F1；WebNLG Rouge-L 为 59.6，高于 ProTeGi 55.7。
- few-shot setting 下，ERM 仍在各任务上领先，例如 LIAR 68.6、BBH 86.1、WebNLG 59.6。
- 效率上，LIAR 中 ERM 第 7 步达到 68.6，而 ProTeGi 第 13 步只有 58.5，接近两倍速度。
- 组件消融显示，exemplar-guided reflection 从 58.5 提升到 62.9；加入 feedback memory 到 67.2；完整 ERM 到 68.6。
- Exemplar Factory 中过滤和 selective forgetting 有正贡献；Feedback Memory 中直接存 feedback 不够，过滤和遗忘才有收益。

## 失败案例和局限

- memory 如果不做过滤可能无收益甚至带噪；论文显示直接存 feedback 不如 filtered memory。
- 使用 Doubao-Pro/GPT-4o 的组合，跨模型结论需要复现。
- memory 检索和遗忘策略增加系统复杂度，也带来数据污染和重复使用失败样例的风险。

## 洞见卡片

```yaml
insight: 历史反馈只有经过过滤和选择性遗忘后才是资产，否则可能只是噪声缓存。
evidence_type: ablation + efficiency-result
paper_evidence:
  section: "4.1 Main Results; 4.2 Ablation Study"
  table_or_figure: "Figure 3, Table 4, Table 5, Table 6"
  quote_or_paraphrase: "直接存储 feedback 不提升，过滤和 selective forgetting 才带来额外收益。"
mechanism: 历史错误样例能暴露稳定 failure mode，但坏反馈和冗余样例会误导 optimizer。
actionable_rule: memory schema 必须包含 quality filter、dedup、forgetting policy 和 retrieval reason。
counterexample_or_limit: 对高度非平稳任务，历史 feedback 可能快速过期。
minimal_experiment: no-memory vs raw-memory vs filtered-memory vs filtered+forgetting。
confidence: high-for-memory-ablation
```

## 对本项目的启发

- 记录失败样例时不要只保存文本，要保存是否被选中、为什么被过滤、何时被遗忘。
- memory 的成功标准应包含 peak step 和 token cost，而不仅是最终指标。
- ERM 可作为 ProTeGi 的下一层 baseline：在 critique-guided search 上加 memory。

## 可复现计划

- 最小复现任务：LIAR 风格二分类或结构化判断，100-200 条数据。
- 需要实现的模块：feedback memory、exemplar memory、filtering、selective forgetting、peak-step report。
- 预计风险：memory leakage；重复样例导致 dev overfitting；feedback quality 难自动判断。
