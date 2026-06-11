# Paper Note: PROSE / PRompt Optimization via Structured Evolution

论文：无独立论文。PROSE 是 *Prompt Optimization Is a Coin Flip*（arXiv 2604.14585）作者**自建的内部方法/消融基线**，完整定义仅见该论文 Appendix C 与 Table 2/4。

链接：https://arxiv.org/abs/2604.14585 （宿主论文；Appendix C "PROSE Method Details"）

source_id：paper-prose-2026（派生自 [[paper-coin-flip-2026]]，非独立来源）

关联 issue：无

线索贡献者：internal-doc-audit（用户发现系统报告反复并列 APE/OPRO/EvoPrompt/PromptBreeder/DSPy-style/PROSE，其中只有 PROSE 无独立笔记，回溯确认它是 coin-flip 自建方法）

新颖性判断：duplicate（结构化 + 进化 + 风险感知选择的组合基线；无独立新贡献，作者引入它正是为了**证伪**"显式 risk-aware selection 有用"这一假设）

阅读日期：2026-06-10

reviewed_by：Claude

local_pdf_path：`local_sources/raw/arxiv_papers/2604.14585/paper.pdf`（与 coin-flip 同一文件）

local_pdf_sha256：`726BF5B639910E69991FE4D9DED654CCA700EBBE40F79D37B10EED71EE6A3638`

local_text_path：`local_sources/raw/arxiv_papers/2604.14585/paper.txt`

local_text_sha256：`8F36F6BF8842C803254632F216983B6E8EFBBB681EE35E93F4277C717F291A43`

evidence_level：method-and-results-read（读全 Appendix C 方法细节、Table 2/4 全部分数、正文脚注 1 对 PROSE 定位的说明；其余实验框架沿用 [[paper-coin-flip-2026]] 已读部分）

来源说明（重要）：**PROSE 没有自己的论文**。它不是 APE/OPRO/EvoPrompt/PromptBreeder/DSPy 那样可独立引用的外部方法，而是 coin-flip 作者为做对照实验自己实现的一个 evolutionary optimizer 变体。本笔记按 paper_note 模板组织只是为了与其余 5 个并列方法同颗粒度、便于横向对比；引用 PROSE 时必须注明出处为 coin-flip Appendix C，不得当作独立文献。

## 一句话结论

PROSE 是 coin-flip 作者自建的一个"加料版"进化式 prompt optimizer：在结构化分解（把 prompt 拆成 role/task/constraints/examples/format 五块）+ 多算子进化搜索之上，叠了一个**显式 risk-aware 选择**——用 `0.70·均分 + 0.15·Sharpe 比率 + 0.15·DRO(最差情况惩罚)` 的风险调整 fitness 选候选。它存在的唯一目的不是刷分，而是当一个**受控反例**：如果"显式针对稳健性/最差情况做选择"真能让优化更可靠，PROSE 应该比 EvoPrompt/PromptBreeder 这些朴素进化方法更稳。结果是它没有任何可测的稳健性优势（Haiku 上和其余方法挤在同一带内，Nova Lite 上同样无优势），从而正向支持 coin-flip 的主结论：**优化收益本身是脆弱且 model-specific 的，靠在选择项里加风险惩罚补不回来**。

## 问题设定

- 任务：compound AI / agent prompt optimization（与 coin-flip 主实验同口径）。
- 优化对象：单段 agent/任务 prompt，但**显式拆成 5 个语义组件**（role、task、constraints、examples、format），允许只改某一块而保留其余。
- 目标指标：LLM-judge 0–100 分；held-out test score（100 test questions）。
- 约束：与其余 5 法**同等算力预算**——每个方法评估约 100 条候选 prompt；20 training questions 提供训练信号。

## 方法摘要

- 候选如何生成：
  - **结构化分解**：每条 prompt 拆成 role/task/constraints/examples/format 五块，算子可针对单块做定向修改，保持其余不变（区别于 OPRO 整条重写、EvoPrompt 整段 crossover）。
  - **种子生成**：用不同温度和多种 prompting 策略（含 "flat-then-decompose"：先平铺再分解）生成 20 个多样候选；按训练分取 top 10 作为初始 population。
  - **六个自适应权重算子**：targeted mutation 25% / LLM crossover 20% / random mutation 20% / exploration 15% / simplification 15% / random generation 5%；权重按"哪类算子的后代得分更高"动态偏移（blend rate 0.3）。
- 反馈如何获得：只有 LLM-judge 标量分（20 train questions）。无自然语言 critique、无 per-sample trace——信号结构与 OPRO/EvoPrompt 同级，仍是纯标量。
- 如何选择候选：**风险调整 fitness**（这是 PROSE 唯一的"新意"所在）——
  `Fitness(p) = 0.70·s̄_p + 0.15·SR(p) + 0.15·DRO(p)`
  其中 `s̄_p` 是平均分，`SR` 是归一化 Sharpe 比率（收益/波动），`DRO` 是 distributionally-robust 项、惩罚最差情况失败。即把"高均分"与"低方差 / 抗最差情况"显式加权进选择信号。
- 是否使用记忆/archive：population size 20、elite 5（精英保留）；4 代无改进则早停（最少 5 代）。弱 archive，无跨任务长期记忆。
- 是否优化 optimizer 自身：否。算子权重会自适应，但 mutation 模板、fitness 公式、超参均固定，非自指。

## 实验设置

- 数据集/任务：Feedback-Bench (FB)、HelpSteer2 (HS2)、WildBench (WB)、XSum（与 coin-flip 主实验四任务一致）。
- 模型：Claude Haiku 4.5、Amazon Nova Lite（被优化/被评分）。
- baselines：zero-shot、manual，以及同框架下的 APE / OPRO / EvoPrompt / PromptBreeder / DSPy-style bootstrap（PROSE 是这组里的第 6 个）。
- train/dev/test 切分：20 train questions / 100 test questions；每格 3 repeats。
- 成本或调用次数：约 100 条候选评估（与其余方法等预算，确保对比公平）。

## 主要结果

论文直接报告（LLM-judge 0–100，3 repeats 均值）：

- **Claude Haiku 4.5（Table 2）**：PROSE = FB **82.1** / HS2 **74.4** / WB **69.6** / XSum **75.9**。
  - 对照同表：Zero-Shot 82.4 / 68.0 / 68.9 / 76.0；EvoPrompt 82.0 / 74.8 / 68.3 / 75.6；PromptBreeder 83.5 / 74.6 / 68.5 / 76.0；DSPy-style 81.9 / 69.8 / 65.1 / 76.2。
  - PROSE 在 WB 上是该任务最高（69.6），但在 FB/XSum 上**低于或持平 zero-shot**；整体落在与其余进化方法**无统计差异**的同一带内。
- **Amazon Nova Lite（Table 4）**：PROSE = FB **80.4** / HS2 **70.0** / WB **64.6** / XSum **72.8**。
  - 其中 FB 80.4、WB 64.6 与 zero-shot（80.4 / 64.6）**完全持平**，XSum 72.8 低于 zero-shot 73.5——同样无稳健性优势。
- **核心结论（Appendix C 收尾句）**：尽管有显式 risk-aware 设计，PROSE 相对更简单的方法**没有任何可测的稳健性优势**，与全文"优化收益脆弱且 model-specific"的主结论一致。

## 失败案例和局限

- **它本身就是一个"负结果"**：PROSE 的价值在于证伪，而非证实。把 Sharpe 比率、DRO 这类金融式风险项塞进选择信号，并没有让优化更稳——说明 compound prompt optimization 的不稳定**不在选择项的设计**，而在更上游（agent 耦合弱、优化 headroom 小、judge 噪声）。
- **多变量同时启用**：结构化分解 + 6 算子 + 风险 fitness + 精英保留 + 早停一次性全开，无法从 PROSE 单独消融出"哪一项有/没用"；它只能证明"这一整套组合不优于朴素进化"，不能定位风险项单独是否有微弱作用。
- **仍是纯标量信号**：和 OPRO/EvoPrompt 一样没有 critique/trace，无法定位错误根因；风险调整只是改了"如何聚合标量分"，没增加信息维度。
- **只在 2 模型 × 4 任务上验证**：负结果的外推同样受限；不能断言"任何风险感知选择都无用"，只能说这一具体实现在该设置下无用。
- **无独立同行评审**：作为论文内部基线，PROSE 的实现细节（如 DRO 具体形式、Sharpe 归一化口径）只在 Appendix C 简述，复现需自行补全。

## 洞见卡片

```yaml
insight: 在"选择项"里显式加风险/最差情况惩罚（Sharpe + DRO），并不能修复 compound prompt optimization 的不稳定。
evidence_type: direct-result（受控反例）
paper_evidence:
  section: "脚注 1, Appendix C, Table 2/4"
  table_or_figure: "Eq.(4) risk-adjusted fitness, Table 2, Table 4"
  quote_or_paraphrase: "PROSE 用 0.70·均分+0.15·Sharpe+0.15·DRO 选候选；'Despite this explicit risk-aware design, PROSE shows no measurable robustness advantage over simpler methods.'"
mechanism: 不稳定来自上游（agent 耦合弱、headroom 小、judge 噪声），选择信号再怎么加风险项也无法凭空造出可被可靠选择的差异。
actionable_rule: 想让优化更稳，先做 coin-flip 式 pre-optimization gate（耦合 + headroom 诊断），而不是先去精修 fitness/选择公式。
counterexample_or_limit: 只在 Haiku/Nova Lite × 4 任务验证；不能外推到"所有风险感知选择都无用"。
minimal_experiment: 同候选池下比较 mean-only 选择 vs risk-adjusted(mean+Sharpe+DRO) 选择，看 held-out 方差与最差任务分是否真的下降。
confidence: medium-high
```

```yaml
insight: 把 prompt 拆成 role/task/constraints/examples/format 五块做定向编辑，是一种合理但本实验未能证明其增益的结构化手段。
evidence_type: method（未隔离消融）
paper_evidence:
  section: "Appendix C (Structured decomposition)"
  table_or_figure: "无单独消融"
  quote_or_paraphrase: "decomposes each prompt into five semantic components ... enabling targeted modification of individual components while preserving others."
mechanism: 结构化分解理论上能减少漂移、保护已验证片段（与 Modular Prompt Optimization 同思路），但 PROSE 把它与风险 fitness 等捆绑，未单独验证。
actionable_rule: 若采用结构化分解，必须单独消融（结构化 vs 整段重写），否则无法归因；可参 [[paper-modular-prompt-optimization-2026]] 的 section-local 做法。
counterexample_or_limit: 本论文未隔离该组件，PROSE 的整体无优势不等于分解本身无用。
minimal_experiment: 固定其余设置，仅切换"五块定向编辑 vs 整段重写"，比较漂移率与 held-out 分。
confidence: medium
```

## 对本项目的启发

> 字段定义与 insight / conclusion / helpful method 的区分口径见 `docs/insight_field_standard.md`。

- conclusion：PROSE 是 coin-flip 的**自建受控反例**，不是可独立引用的方法。它的研究价值是一条负结果——"在选择项里显式加风险/最差情况惩罚，救不回 compound prompt optimization 的脆弱性"——这反过来强化了 coin-flip 的主张：要不要优化、能不能优化，取决于上游的耦合与 headroom，而非下游选择公式的精巧。
- helpful method：把 PROSE 当作"选择信号工程的天花板对照"——本项目若想试 risk-aware / robust 选择，应以 PROSE 的负结果为先验，先证明在自己任务上风险项能降方差再上，否则默认它无增益。其结构化五段分解可作为 prompt ledger 的字段切分参考（role/task/constraints/examples/format），但增益需另行验证。
- anti-pattern / limit：把 PROSE 当成"一个值得复现的强方法"去引用（它是负结果基线）；或一次性叠满结构化+多算子+风险 fitness 而不做单项消融。
- 适用场景：仅当你要论证"选择信号设计的边界"时，PROSE 作为对照有意义；日常优化不必复现它。
- 误用风险：把"PROSE 无优势"误读成"结构化分解无用"或"进化方法无用"——它证明的只是**这一整套组合在该设置下不优于朴素进化**。

## 最小验证或演示计划

- 要验证的 insight / method：risk-adjusted 选择（mean+Sharpe+DRO）相对 mean-only 选择，是否真能降低 held-out 方差和最差任务分。
- 最小验证任务：一个 LLM-judge 评分的主观生成任务（如摘要或回复改写），20 train / 100 test，3 repeats。
- 需要实现的模块：(1) 朴素进化 optimizer（EvoPrompt 式 GA）作底座；(2) 两套选择头——mean-only vs `0.70·mean+0.15·Sharpe+0.15·DRO`；(3) 先跑 [[paper-coin-flip-2026]] 的耦合/headroom gate 作为前置门。
- 观察指标：held-out 均分、跨 repeat 方差、最差任务分（worst-case）、是否能拒绝"两套选择无差异"的 null。
- 预计风险：headroom 太小时两套选择都贴着 zero-shot，差异淹没在 judge 噪声里（先过 gate）；DRO/Sharpe 归一化口径选择会影响结论，需固定并记录。
