# Paper Note: APE / Large Language Models Are Human-Level Prompt Engineers

论文：Large Language Models Are Human-Level Prompt Engineers (APE)

链接：https://arxiv.org/abs/2211.01910

source_id：paper-ape-2022

关联 issue：无

线索贡献者：internal-arxiv-search（经典锚点补读）

新颖性判断：duplicate-but-foundational-baseline（automatic instruction generation+selection 的奠基论文；"propose-then-select" 范式与 "Let's work this out..." 基线的来源）

阅读日期：2026-06-10

reviewed_by：Claude

local_pdf_path：`local_sources/raw/arxiv_papers/2211.01910/paper.pdf`

local_pdf_sha256：`B4162F38101DB7511E6292A2577C66514C757824DDD21F8426A6276485355E81`

local_text_path：`local_sources/raw/arxiv_papers/2211.01910/paper.txt`

local_text_sha256：`7B5536FC54C1B1622C35E7F2C05D7DFA710F6446CC3E77151BA5DC1613815B24`

evidence_level：method-and-results-read（读了算法、两种 score function、迭代 Monte Carlo、Instruction Induction / BBII / zero-shot CoT / TruthfulQA 主结果和定量分析；附录任务细节与成本表略读）

版本说明：本地 PDF 为 v2（2023-03-10，ICLR 2023）。

## 一句话结论

APE 把"prompt engineering"形式化为最简的**两阶段黑盒搜索：propose（用一个 LLM 当 inference model 生成一批候选 instruction）+ select（用 score function 在小训练集上选最高分的那条）**。它的奠基意义有三：(1) 确立"instruction 即 program、LLM 既是提案器又是打分器"的范式；(2) 给出第一个"自动生成的 instruction 在 24/24 instruction induction 任务上达到或超过人类"的强证据（IQM 0.810 vs 人类 0.749）；(3) 顺手产出了那条被 OPRO/TextGrad 等后续工作当作强基线的 zero-shot CoT prompt——"Let's work this out in a step by step way to be sure we have the right answer."。它是几乎所有 APO 论文的"最简对照锚点"。

## 问题设定

- 任务：为自然语言任务自动找到一条 zero-shot instruction（明确不含多次 LLM 链式调用、不含外部工具——纯单 instruction 优化）。
- 优化对象：单段 instruction 文本（"program"），不优化 demonstration、不优化系统结构。
- 目标指标：在另一个被控 LLM 上执行该 instruction 的 zero-shot 表现（execution accuracy 或 log probability）。
- 约束：只需少量训练 input-output 对（如 5 对）；API 黑盒；无梯度。

## 方法摘要

- 候选如何生成（propose）：把 LLM 当 inference model，用"填空"式模板让它根据少数 input-output 示例反推出能解释这些示例的 instruction——支持 forward 模式和 reverse 模式（"在中间插入指令"的 infilling）。还有 resampling 模式：让 LLM 生成某条 instruction 的"保持语义的变体"。
- 反馈如何获得（score）：两种 score function——
  1. **Execution accuracy**：0-1 损失，instruction 拼到问题上执行后是否命中答案（可含 order-invariant set matching 等）。
  2. **Log probability**：被控 LLM 在该 instruction 下给出目标答案的对数概率（更软、信息更密）。
  - 为省成本用**自适应过滤**：先在小训练子集上评分，淘汰低分候选，只对高分候选做完整评估。
- 如何选择候选（select）：在训练集（子集）上按 score 选最高分 instruction；可选**迭代 Monte Carlo 搜索**——评估一批后让 LLM 重采样语义相近的新候选，多轮逼近（Algorithm 1）。
- 是否使用记忆/archive：无显式 archive；迭代版的上一轮候选池算弱记忆。
- 是否优化 optimizer 自身：否。
- 默认配置：**非迭代**（迭代只带来边际提升）；默认采样 ~50 条候选。

## 实验设置

- 数据集：24 个 Instruction Induction 任务（Honovich 2022）；自建 BIG-Bench Instruction Induction（BBII，21 任务）；zero-shot CoT 任务套件（MultiArith、GSM8K 等）；TruthfulQA。
- 模型：被控/执行 LLM 为 InstructGPT（text-davinci-002）；提案用 InstructGPT 系列；定量分析涉及 8 个不同规模模型。
- baselines：人写 prompt（Human，金标注）、Honovich 2022 的"Greedy"（无搜索选择的 APE 退化版）。
- train/dev/test 切分：每任务采少量 input-output 对当训练；5 个随机种子重复。
- 成本或调用次数：默认 ~50 候选；TruthfulQA 用 200 候选、取 top-10。

## 主要结果

论文直接报告：

- **Instruction Induction（24 任务）**：APE 在 **24/24** 任务上达到或超过人类，逐任务都超过 Greedy；InstructGPT 下 IQM **0.810 vs 人类 0.749**。
- **BBII（21 任务）**：APE 在 **17/21** 任务上达到或超过默认人写 prompt。
- **Few-shot**：把 APE instruction 前置到 in-context 示例前，在 **21/24** 任务上持平或更好；但反直觉地，在 Rhymes / Large Animal / Second Letters 这 3 个任务上**加 in-context 示例反而掉分**——作者推测是 instruction 过拟合了 zero-shot 场景。
- **Zero-shot CoT**：用 APE 搜 answer-prefix，得到 "Let's work this out in a step by step way to be sure we have the right answer."，把 MultiArith 从 78.7→**82.0**、GSM8K 从 40.7→**43.0**（相对 Kojima "Let's think step by step." 起点）。
- **TruthfulQA**：仅 200 候选即超过人写 "help" prompt；top-10 训练集选择能很好泛化到测试集；可在 truthfulness/informativeness 间权衡。
- **定量分析**：模型越大提案分布越好；**更大更强的模型反而更 cost-effective**（尽管每 token 更贵）；候选采样从 4 增到 128，约 64 后收益饱和，默认取 50；迭代 Monte Carlo 仅边际提升。

## 失败案例和局限

- **过拟合 zero-shot 选择口径**：用 zero-shot execution accuracy 选出的 instruction，到 few-shot 场景可能掉分（3/24 任务）。这是 APO 里最早的"选择口径决定泛化"证据——选择 metric 与部署场景不一致就会过拟合（呼应 [[paper-opro-2023]] 5.4、[[paper-coin-flip-2026]]）。
- **范围窄**：明确不含多步链式/工具/demonstration 优化；只优化单 instruction，不解决 compound 系统（这正是 DSPy/MIPRO/TextGrad 后续要补的）。
- **依赖可判定 score function**：execution accuracy 需要可自动判答；开放生成任务要靠 log prob 或 judge，噪声更大。
- **TruthfulQA 非"true few-shot"**：作者自己声明用了部分 QA 对当训练，结果与原 benchmark 不可直接比——提醒"优化用到的样本不能再算 zero-shot"。
- **迭代搜索收益有限**：迭代 Monte Carlo 相对简单一次性生成只有边际提升，说明这版的 search 能力不强，价值主要在"提案多样性 + 选择"而非"迭代爬坡"。
- **成本随候选数线性增**：虽有自适应过滤，候选数与评估样本仍直接决定成本；无 trace/critique 信号，无法定位错误根因。

## 洞见卡片

```yaml
insight: "propose-then-select"（多样化提案 + 数据驱动选择）是最简也最稳的 APO 骨架。
evidence_type: direct-method + direct-result
paper_evidence:
  section: "3, 4.1"
  table_or_figure: "Algorithm 1, Figure 1, Figure 4"
  quote_or_paraphrase: "用 LLM 反推一批 instruction 候选，再用 execution accuracy 在小训练集上选最优；24/24 任务达到或超过人类（IQM 0.810 vs 0.749）。"
mechanism: 单次 LLM 改写不可靠，但"多候选 + 用数据选"把不可靠性转成可控的搜索，且不需要梯度。
actionable_rule: 任何 optimizer 的下限对照都应包含 APE——多样提案 + held-out 选择；打不过它的复杂方法不值得上。
counterexample_or_limit: 选择口径与部署场景不一致会过拟合（zero-shot 选 → few-shot 掉分）。
minimal_experiment: 同任务比较 APE(propose-select) vs 单次 rewrite vs OPRO 轨迹式，记录样本效率与过拟合 gap。
confidence: high
```

```yaml
insight: 选择 instruction 用的评分口径，必须和最终部署场景一致，否则会过拟合到优化场景。
evidence_type: direct-result
paper_evidence:
  section: "4.1 (Few-shot)"
  table_or_figure: "Figure 8, Figure 14"
  quote_or_paraphrase: "按 zero-shot execution accuracy 选的 instruction 在加 in-context 示例后 3 个任务掉分；改用 few-shot 选择口径可恢复。"
mechanism: optimizer 会精确利用选择信号的形状；选择信号 ≠ 部署信号时，最优解只对选择场景最优。
actionable_rule: 本项目选择 metric 必须等于（或覆盖）部署条件——zero-shot 部署就 zero-shot 选，few-shot 部署就 few-shot 选；并保留 held-out 复核。
counterexample_or_limit: 两种场景表现高度相关时，差异可忽略。
minimal_experiment: 同候选集分别用 zero-shot / few-shot 选择，比较各自在两种部署下的测试分交叉表。
confidence: high
```

```yaml
insight: 更大更强的模型当提案器，单 token 更贵但总成本更低。
evidence_type: direct-result
paper_evidence:
  section: "5 Quantitative Analysis + Appendix D"
  table_or_figure: "Figure 6, 正文成本结论"
  quote_or_paraphrase: "larger and more powerful LMs are more cost-effective for generating the best prompt despite higher per-token cost；提案分布随模型增大变好，候选数约 64 饱和。"
mechanism: 强提案器一次就给出更高质量候选分布，省去为弥补低质提案而做的大量评估。
actionable_rule: 选 proposer/optimizer 模型时按"达到目标分的总成本"算，别只看每 token 单价（与 [[paper-textgrad-2024]] 弱前向+强梯度、[[paper-gepa-2026]] Qwen-opt 迁移互参）。
counterexample_or_limit: 任务简单、提案分布已饱和时，强提案器溢价无收益（候选 >64 后边际递减）。
minimal_experiment: 固定被控模型，比较弱/强 proposer 达到同目标分的总调用成本与候选数。
confidence: medium-high
```

## 对本项目的启发

> 字段定义与 insight / conclusion / helpful method 的区分口径见 `docs/insight_field_standard.md`。

- conclusion：APE 是 APO 的**最简奠基锚点**。它证明"多样提案 + 数据选择"无需梯度即可达到人类级 instruction，并最早暴露"选择口径=部署场景"的过拟合戒律。但它只优化单 instruction、迭代能力弱、无 trace 信号——后续 OPRO（轨迹）、TextGrad（critique）、DSPy/MIPRO（program+demo）、GEPA（trace+Pareto）都是在补它的不足。
- helpful method：把 APE 的 propose-then-select 当作每个 optimizer 实验的**强制下限基线**；并把"选择 metric 必须匹配部署场景"写进评估规范。
- anti-pattern / limit：用与部署不一致的口径选 prompt；只看 proposer 单价而非总成本；指望迭代搜索在弱 search 下爬出大收益。
- 适用场景：单 instruction 优化、有少量带标样本、有可判定 score function、想要便宜可复现的下限。
- 误用风险：把 zero-shot 选出的 prompt 直接用于 few-shot/agent 场景；把"24/24 超人类"当成所有任务通用（任务集是 instruction induction，偏简单）。

## 最小验证或演示计划

- 要验证的 insight / method：propose-then-select 作为下限；选择口径↔部署场景一致性。
- 最小验证任务：一个有可判定 metric 的分类/抽取任务，100–300 样本，分 zero-shot 与 few-shot 两种部署。
- 需要实现的模块：(1) LLM 提案器（forward/reverse 模板，采 ~50 候选）；(2) execution-accuracy 评分 + 自适应过滤；(3) zero-shot 与 few-shot 两套选择口径；(4) 与 OPRO/TextGrad/MIPRO 共用评估集。
- 观察指标：达到目标分的候选数与总成本、zero/few-shot 选择交叉表过拟合 gap、与更复杂 optimizer 的差距、跨模型迁移 delta。
- 预计风险：score function 不可判定时退化；小训练集选择过拟合；候选过少导致提案分布不足。
