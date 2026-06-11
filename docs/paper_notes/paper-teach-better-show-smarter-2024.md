# Paper Note: Teach Better or Show Smarter?

论文：Teach Better or Show Smarter? On Instructions and Exemplars in Automatic Prompt Optimization

链接：https://arxiv.org/abs/2406.15708

source_id：paper-teach-better-show-smarter-2024

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：actionable-experiment

阅读日期：2026-06-08

reviewed_by：Codex

local_pdf_path：`local_sources/raw/arxiv_papers/2406.15708/paper.pdf`

local_pdf_sha256：`80B3D570F434686E90398893284A824C1368877A5A160006A4F5300B10580519`

local_text_path：`local_sources/raw/arxiv_papers/2406.15708/paper.txt`

local_text_sha256：`B488D17A0C032813866D16317BE162CA3ADC18BFEEE0CA8AC43DE463957A94AF`

evidence_level：method-results-analysis-read

## 一句话结论

这篇论文给出一个很实用的结论：既然大多数 instruction optimization 已经需要 labeled dev set，那就不该只拿它打分，还应系统优化 exemplars；很多情况下，怎么选例子比怎么改 instruction 更重要。

## 问题设定

- 任务：比较 instruction optimization (IO) 和 exemplar optimization (EO) 的相对作用。
- 优化对象：instruction、self-generated exemplars 或两者组合。
- 目标指标：BBH、MMLU 等任务 accuracy。
- 约束：控制 IO/EO 的 validation evaluation budget，比较组合。

## 方法摘要

- 候选如何生成：IO 包括 No IO、APE、ProTeGi、PromptAgent、OPRO；EO 包括 No EO、Random、Nearest、Diversity、Random Search、Mutation 等。
- 反馈如何获得：validation set 上评估 prompt + exemplar combination。
- 如何选择候选：按 EO/IO 策略选择最优 instruction 或 exemplar set。
- 是否使用记忆/archive：不强调长期 memory。
- 是否优化 optimizer 自身：否。

## 实验设置

- 数据集：BBH、MMLU。
- 模型：PaLM 2、Gemini 1.0 Pro/Ultra、Gemini 1.5 Flash/Pro 等。
- baselines：No IO/No EO 以及各类 IO/EO 组合。
- train/dev/test 切分：dev set 既用于 IO 评估，也用于 EO 选择；test 报告最终泛化。
- 成本或调用次数：主实验 IO/EO 评估预算通常 m=32，k=3 exemplars。

## 主要结果

- PaLM 2 BBH 表中，No IO + No EO 为 60.30；No IO + Mutation EO 达到 72.92，提升 12.63。
- ProTeGi + No EO 为 68.13；ProTeGi + Mutation EO 到 77.29，EO 仍带来 9.16 提升。
- Gemini 1.0 Pro BBH 中，No IO + Mutation 为 75.77，ProTeGi + No EO 只有 65.91；优化 exemplars 单独超过 instruction optimization。
- MMLU 中，No IO + Random Search 为 72.75，ProTeGi + Random Search 为 72.31，说明 EO 可消除甚至反超 zero-shot 下 IO 差距。
- 作者发现 optimized exemplars 的 validation-test generalization gap 通常小于 optimized instructions。

## 失败案例和局限

- EO 需要 labeled dev set 和上下文空间；极长输入或极短 context 场景不一定适用。
- exemplars 是 target model self-generated，质量和任务相关；并非随机越多越好，Table 4 中 all exemplars 不如 3 个优化 exemplars。
- 论文关注 instruction/exemplar，未覆盖 tool schemas、agent topology 等更复杂变量。

## 洞见卡片

```yaml
insight: 如果你已经有 dev set 做 prompt optimization，就应该把 exemplar selection 纳入优化变量。
evidence_type: comprehensive-comparison
paper_evidence:
  section: "Insight 1; Insight 2"
  table_or_figure: "Table 1, Table 2, Table 3, Table 4"
  quote_or_paraphrase: "No IO + optimized exemplars 经常超过 SoTA IO + no/random exemplars。"
mechanism: exemplars 给模型直接展示决策边界和输出模板，且可能比抽象 instruction 更好泛化。
actionable_rule: 每个 APO 实验至少比较 no-example、random-example、optimized-example 三组。
counterexample_or_limit: context 紧张或 exemplar 与 test 分布错配时，EO 可能不划算。
minimal_experiment: instruction-only vs random exemplars vs optimized exemplars vs instruction+optimized exemplars。
confidence: high
```

## 对本项目的启发

- 我们不能把“zero-shot APO”与“用了 dev set 但不放 exemplars”的设置混为一谈。
- prompt 版本记录应增加 `exemplar_source`、`exemplar_selector`、`k`、`selection_budget`。
- 后续最小实验应把 EO 作为强 baseline，否则可能高估 instruction rewrite 的价值。

## 可复现计划

- 最小复现任务：BBH-like 小任务或多分类判断任务，32 次 dev eval budget。
- 需要实现的模块：self-generated exemplar pool、random/nearest/mutation search、IO+EO combination evaluator。
- 预计风险：dev set 太小；exemplar 泄漏；instruction 和 exemplar 同时变化导致归因困难。
