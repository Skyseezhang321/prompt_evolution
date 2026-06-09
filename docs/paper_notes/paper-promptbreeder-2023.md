# Paper Note: PromptBreeder

论文：PromptBreeder: Self-Referential Self-Improvement via Prompt Evolution

链接：https://arxiv.org/abs/2309.16797

source_id：paper-promptbreeder-2023

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：foundational

阅读日期：2026-06-08

reviewed_by：Codex

local_pdf_path：`local_sources/raw/arxiv_papers/2309.16797/paper.pdf`

local_pdf_sha256：`0E5B44B77D345581509BB58B009FA7FEF9928BF8C090B2A056E8916F25D974A0`

local_text_path：`local_sources/raw/arxiv_papers/2309.16797/paper.txt`

local_text_sha256：`A21EE9C153027E59CDD643E398B418874E770F923F2D06BDEFB562AF5B681D1F`

evidence_level：method-and-results-read

## 一句话结论

PromptBreeder 的真正洞见不是“用遗传算法搜索 prompt”，而是把 mutation prompt 也放进演化对象中，让系统同时学习“任务 prompt”和“如何改任务 prompt”；但它也暴露了早期 prompt evolution 的典型风险：搜索空间大、成本高，few-shot context 可能支配结果，task prompt 甚至会漂成无意义文本。

## 问题设定

- 任务：给定一个 domain problem description，自动演化 task prompts，提高 LLM 在该领域的训练/测试表现。
- 优化对象：task prompts、mutation prompts、少量 few-shot contexts，以及某些运行中可变超参。
- 适用任务：算术推理、commonsense reasoning、instruction induction、ETHOS hate speech classification。
- 目标指标：训练 batch fitness 和最终 test accuracy。

## 方法摘要

- 候选如何生成：每个 evolution unit 包含 task prompts、mutation prompt、few-shot contexts。LLM 根据 mutation prompt 改写 task prompt。
- 自指机制：mutation prompt 本身也会被 hyper-mutation prompt 改写，形成 `M' = LLM(H + M)`。
- 搜索机制：binary tournament genetic algorithm。抽两个个体，保留高 fitness 个体，mutate 后覆盖低 fitness 个体。
- 主要 mutation operators：
  - zero-order / first-order prompt generation。
  - EDA population-based mutation。
  - lineage-based mutation。
  - zero-order / first-order hyper-mutation。
  - Lamarckian mutation，从正确 working-out 反推 prompt。
  - prompt crossover 和 context shuffling。
- 多样性维护：BERT embedding similarity filtering、fitness sharing、随机字符前缀、mutation temperature 演化。

## 实验设置

- 模型：PaLM 2-L。
- 主要设置：population size 50；通常 20-30 generations；fitness 用训练集中随机 100 个 Q&A batch 的 accuracy。
- 长跑设置：一般 1-2k fitness evaluations；数据集未自带 split 时按 50/50 train/test 切分。
- 对照：CoT、PoT、Plan-and-Solve、PS+、APE、OPRO、Manual-CoT、Auto-CoT。

## 主要结果

论文直接报告：

- 表 1 中，PromptBreeder 在 PaLM 2-L 上的 zero-shot 结果：MultiArith 99.7、SingleEq 96.4、AddSub 87.8、SVAMP 90.2、SQA 71.8、CSQA 85.4、AQuA-RAT 62.2、GSM8K 83.9，整体高于 PS+、APE、OPRO 等对照。
- few-shot PromptBreeder 在 MultiArith 100.0、SingleEq 98.9、SVAMP 93.7、SQA 80.2、CSQA 85.9、AQuA-RAT 64.6、GSM8K 83.5 等任务上继续保持强表现。
- ETHOS 上，PromptBreeder 演化出的两阶段长 prompt 达到 89%，高于手写 prompt 80%。
- GSM8K 中最有效 mutation prompt 包括“summarise and improve”“simplify into separate sentences”“explain as a good teacher”等；最高成功率 24.13%。
- mutation operator 有效性中，zero-order hyper-mutation 产生改善的比例最高，为 42%，lineage-based mutation 26%，first-order hyper-mutation 23%。
- 消融显示，大多数 self-referential components 被移除后 fitness 下降；ETHOS 欠指定任务中，移除 Lamarckian context-to-prompt mutation 从 81.6% 降到 64.6%。

## 失败案例和局限

- 论文附录显示，few-shot evolution 中 contexts 可能主导 fitness，task prompts 有时漂成 nonsense，例如只剩 “mutant”。
- 早期设置成本高：population 50、1-2k fitness evaluations，并且每次 fitness evaluation 又要跑 100 样本 batch。
- LLM 不一定能理解显式 fitness values；作者在 EDA mutation 中不给 LLM fitness 分数，因为 preliminary experiments 里 LLM 倾向复制高分条目。
- 方法有大量 mutation operators 和启发式，多变量同时变化，因果归因困难。
- 主要基于 PaLM 2-L 和早期基准，和现代 agent/workflow 场景仍需重新验证。

## 洞见卡片

```yaml
insight: 自进化 prompt 的最小闭环不只是优化 task prompt，还要优化 mutation prompt。
evidence_type: method + ablation
paper_evidence:
  section: "3.2, 5, Appendix L"
  table_or_figure: "Table 7, Table 8, Figure 4"
  quote_or_paraphrase: "hyper-mutation operators 直接改 mutation prompts；移除 self-referential operators 在多数数据集上伤害 fitness。"
mechanism: mutation prompt 决定搜索方向；固定 mutation prompt 会把搜索限制在人工预设的改写风格里。
actionable_rule: 记录并版本化 optimizer/mutation prompt，不要只记录最终 task prompt。
counterexample_or_limit: 自指操作数量多，收益可能和 population diversity、context evolution、selection 交织。
minimal_experiment: fixed mutation prompt vs evolved mutation prompt under same candidate budget。
confidence: high-for-evolutionary-prompt-search
```

```yaml
insight: 成功样例可以反向蒸馏成 prompt，但也可能让 context 盖过 prompt 本身。
evidence_type: method + limitation
paper_evidence:
  section: "3.2.4, Appendix J.5, Appendix L"
  table_or_figure: "ETHOS ablation, few-shot examples"
  quote_or_paraphrase: "Lamarckian mutation 从正确 working-out 反推 task prompt；但 few-shot evolution 中 contexts dominate，task prompts 可漂成 nonsense。"
mechanism: successful working-out 包含任务求解过程信息，能诱导规则；但 evaluation 若依赖 few-shot context，prompt 字符串本身可能不再承担主要功能。
actionable_rule: 做 prompt evolution 时要分开评估 instruction-only、context-only、instruction+context。
counterexample_or_limit: 如果 demos 很强，优化器可能只是选择/污染 demos，而不是学到可解释规则。
minimal_experiment: evolved instruction with fixed demos vs evolved demos with fixed instruction。
confidence: medium-high
```

## 对本项目的启发

- “prompt 自进化”需要至少区分 task prompt、mutation prompt、selection policy、context examples。
- 第一批实验不应一次启用九种 mutation operators，否则难以解释提升来源。
- 对所有候选要记录 `operator_type` 和 `parent_id`，否则无法复盘哪类 mutation 真正有效。
- Few-shot context 必须做单独消融，防止把 demo 选择误判成 prompt 规则进化。

## 可复现计划

- 最小复现任务：一个小型分类/抽取任务，100-300 条训练样本。
- 变量：
  - fixed mutation prompt vs evolved mutation prompt。
  - direct mutation vs lineage mutation vs Lamarckian mutation。
  - instruction-only vs instruction+few-shot。
- 指标：test accuracy、prompt length、operator success rate、context-only ablation、每轮成本。
