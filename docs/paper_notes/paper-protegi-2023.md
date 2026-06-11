# Paper Note: ProTeGi / Automatic Prompt Optimization with "Gradient Descent" and Beam Search

论文：Automatic Prompt Optimization with "Gradient Descent" and Beam Search

链接：https://arxiv.org/abs/2305.03495

source_id：paper-protegi-2023

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：extension

阅读日期：2026-06-08

reviewed_by：Codex

local_pdf_path：`local_sources/raw/arxiv_papers/2305.03495/paper.pdf`

local_pdf_sha256：`90ED9BD62D8E8C1F5BB810C7749C8272F2DE4CAC037CB75306746C9C9CFCB094`

local_text_path：`local_sources/raw/arxiv_papers/2305.03495/paper.txt`

local_text_sha256：`C08AA4A0B410CE2F80AF10281CC6DCCDC25198E1CEC2C029FED87AFB29D380F3`

evidence_level：method-and-results-read

## 一句话结论

ProTeGi 的核心洞见不是“文本真的有可微梯度”，而是把失败样本压缩成可编辑的自然语言批评，再用多候选搜索和数据选择筛掉坏改写；它是后续 textual critique / prompt evolution 实验必须对照的经典 baseline。

## 问题设定

- 任务：给定初始 prompt 和带标签训练数据，自动改写 prompt，提高黑盒 LLM 在任务上的表现。
- 优化对象：自然语言 task prompt；few-shot examples 在实验中保持固定。
- 目标指标：四个分类任务上的 test binary F1。
- 约束：不训练模型，不访问 LLM 内部状态；通过 LLM API 做 prompt 生成、编辑和评估。

## 方法摘要

- 候选如何生成：对当前 prompt 在 minibatch 上的错误样本生成自然语言“gradient”，再用另一个 LLM prompt 将该 gradient 转成 prompt 编辑；随后对候选做 paraphrase 扩展。
- 反馈如何获得：错误样本 + 当前 prompt 的行为，被 LLM 总结成当前 prompt 的缺陷。
- 如何选择候选：beam search 外循环；候选选择被建模为 best-arm identification，实验比较 UCB、UCB-E、Successive Rejects、Successive Halving 等。
- 是否使用记忆/archive：使用 beam 保留候选，但不是长期 memory。
- 是否优化 optimizer 自身：否。`gradient prompt` 和 `editing prompt` 是静态的。

## 实验设置

- 数据集：
  - Jailbreak：452 个多语言样本，人工标注是否为 jailbreak。
  - Ethos：997 条英文 hate speech comments。
  - Liar：4000 条英文 fake news statements。
  - Sarcasm：10000 条阿拉伯语 sarcasm comments。
- 模型：主实验使用 January 2023 版 `gpt-3.5-turbo`；另比较 GPT-3、InstructGPT、ChatGPT、GPT-4。
- baselines：Monte-Carlo / APE-style search、RL phrase-level operations、AutoGPT feedback、uniform evolutionary selection。
- train/dev/test 切分：每任务随机采样 50 development、150 test；结果为 3 次实验平均。
- 成本或调用次数：主设置 minibatch size 64、beam size 4、6 optimization steps；每步每 4 个错误生成 4 个 gradients，每个 gradient 编辑一次，再生成 2 个 Monte Carlo paraphrases；每个 parent prompt 随机保留 8 个 successors 进入 bandit selection。

## 主要结果

论文直接报告：

- ProTeGi 在四个 benchmark 上均超过对照算法；平均比 MC 高 3.9%，比 RL 高 8.2%，比原始 prompt 高 15.3%，比 AutoGPT 高 15.2%。
- 摘要和引言报告，最高可把初始 prompt 表现提升 31%。
- Beam search ablation 中，Beam(ProTeGi) 在 Jailbreak、Liar、Sarcasm 上分别为 0.85、0.67、0.88，优于 no iteration 和 greedy。
- Bandit selection 中，UCB/UCB-E/SR/SH 均超过 uniform selection；论文发现 UCB-style 实践中优于 successive-rejects-style，与作者原先理论直觉不完全一致。
- 学习曲线显示，所有数据集大约 3 step 达峰，之后可能在训练数据上过拟合或卡入 local minima。

## 失败案例和局限

论文直接报告：

- Qualitative analysis 显示，Jailbreak 的某些 gradient 会把 prompt 焦点错误转到 child grooming 等局部问题；有时 ProTeGi 没有正确利用 gradient，而是用模型内部知识重新定义概念。
- AutoGPT 在 Jailbreak 和 Sarcasm 上 6 轮反馈反而降低起始 prompt 表现，说明“让 agent 自己改”不等于有效优化。
- ProTeGi 实际效率受 LLM API rate limit 限制；即使候选选择相对高效，gradient generation、beam candidates full evaluation 和长 prompt 可能让小预算运行超过 1 小时。
- 只测试了四个 classification benchmark，未覆盖生成、agent、tool-use、多目标或安全治理任务。

## 洞见卡片

```yaml
insight: 失败样本需要转成可编辑语言反馈，而不是只转成分数。
evidence_type: direct-method + direct-result
paper_evidence:
  section: "2.1, 2.2, 3.4"
  table_or_figure: "Figure 3, Table 1, Table 2, Figure 4"
  quote_or_paraphrase: "论文用 minibatch 错误生成 natural language gradients，再编辑 prompt；主结果显示比 MC/RL/AutoGPT 和原始 prompt 更好。"
mechanism: critique 指出当前 prompt 缺陷，beam/bandit 选择避免采纳单次不可靠改写。
actionable_rule: 每轮 prompt 优化至少记录失败样本、critique、候选 prompt、选择指标和淘汰理由。
counterexample_or_limit: critique 可能误导，学习曲线显示约 3 step 后可能过拟合或局部停滞。
minimal_experiment: scalar-score rewrite vs critique-guided rewrite vs critique-guided beam search。
confidence: high-for-classification-baseline; medium-for-general-agent-use
```

```yaml
insight: 候选选择机制和候选生成机制同等重要。
evidence_type: ablation
paper_evidence:
  section: "3.4 Beam Search Ablation; Bandit Algorithms"
  table_or_figure: "Table 1, Table 2"
  quote_or_paraphrase: "Beam search 优于 flat / greedy；bandit best-arm identification 方法优于 uniform selection。"
mechanism: LLM 生成的 prompt 候选方差很高，需要用数据和搜索结构筛选。
actionable_rule: 不直接采用 optimizer 的第一条改写；至少保留多个候选并用 dev set 或 Pareto 指标选择。
counterexample_or_limit: 搜索预算增加也会增加 dev overfitting 风险。
minimal_experiment: one-shot rewrite vs beam width 4 + dev selection。
confidence: high
```

## 对本项目的启发

- ProTeGi 是第一组最小实验的必要 baseline，但不要照搬“gradient”措辞，应称为 natural-language critique 或 textual feedback。
- 评估日志必须记录 `optimization_step`，因为论文显示过多 step 可能过拟合。
- 如果复现，应先用小分类/抽取任务；不要直接推断它适合 agent 或开放生成任务。

## 可复现计划

- 最小复现任务：二分类或结构化抽取任务，90-150 条样本。
- 需要实现的模块：
  - failure minibatch sampler。
  - critique prompt。
  - edit prompt。
  - candidate beam。
  - dev-set selector。
- 预计风险：
  - API 成本和运行时间。
  - critique 误导。
  - dev overfitting。
  - prompt bloat。
