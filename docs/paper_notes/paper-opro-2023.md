# Paper Note: OPRO / Large Language Models as Optimizers

论文：Large Language Models as Optimizers (OPRO)

链接：https://arxiv.org/abs/2309.03409

source_id：paper-opro-2023

关联 issue：无

线索贡献者：internal-arxiv-search（经典锚点补读）

新颖性判断：duplicate-but-foundational-baseline（经典 LLM-as-optimizer 基线，用于校准后续方法的对照锚点）

阅读日期：2026-06-10

reviewed_by：Claude

local_pdf_path：`local_sources/raw/arxiv_papers/2309.03409/paper.pdf`

local_pdf_sha256：`61C8493C964F6D4436F69AE63FF52D3A91540708E9387615F3A8F034BAB081C0`

local_text_path：`local_sources/raw/arxiv_papers/2309.03409/paper.txt`

local_text_sha256：`7BB12BA8540812148D481EA71D9AF9BD856293F15A0D9E8243545F2E8B223BAF`

evidence_level：method-and-results-read（读了方法、主结果、消融、过拟合分析和 EvoPrompt 对比；linear regression/TSP 动机实验和部分附录表格只略读）

版本说明：本地 PDF 为 v3（2024-04-15），结论以该版本为准。

## 一句话结论

OPRO 把"prompt 优化"定义为一个**纯轨迹驱动的黑盒搜索**：每步把"历史 prompt + 其训练分数"按升序塞进一个 meta-prompt，让 optimizer LLM 直接生成 8 条全新指令（不是编辑、也不要求语义保持），评分后回填轨迹。它最有名的产物是"Take a deep breath and work on this problem step-by-step."（GSM8K 80.2，对照"Let's think step by step." 71.8）。它的真正价值不在算法新颖，而在确立了一个**最小、可复现、API-only 的 LLM-as-optimizer 基线**，以及一个后续被反复挑战的论断：prompt 是高度 model-specific / task-specific 的。

## 问题设定

- 任务：自然语言任务（输入输出均为文本）的 instruction 优化，主战场是推理 benchmark（GSM8K、BBH 23 个任务）。
- 优化对象：单段 instruction 文本（不含 few-shot demo 优化），插入位置可选 `Q_begin` / `Q_end` / `A_begin`。
- 目标指标：scorer LLM 在训练子集上的 task accuracy（贪心解码，temperature 0 评估）。
- 约束：只假设 API 访问；只需小训练子集（GSM8K 用 3.5%、BBH 用 20%）；受 optimizer LLM 上下文窗口限制。

## 方法摘要

- 候选如何生成：把 meta-prompt 喂给 optimizer LLM，每步采样 8 次生成 8 条**全新 instruction**。meta-prompt 含两块核心信息——(1) 优化轨迹：历史 instruction + 训练分数，按分数升序排列，只保留分数最高的 20 条；(2) 任务描述：3 条随机训练样例 + meta-instruction（说明优化目标、输出格式，可加"指令应简洁且通用"这类软正则）。
- 反馈如何获得：**只有标量训练分数**。没有自然语言 critique、没有 per-sample trace、没有错误归因。LLM 完全靠"在轨迹里看分数模式"来推断改进方向（in-context pattern recognition 当作隐式梯度）。
- 如何选择候选：无显式选择器/beam/Pareto。轨迹本身充当 archive（截断到 top-20）；最终取训练分数最高的 instruction 作为结果。
- 是否使用记忆/archive：弱 archive——仅 top-20 轨迹截断，无跨任务记忆。
- 是否优化 optimizer 自身：否。meta-prompt 模板和采样策略固定。
- 关键区分：与 ProTeGi（按自然语言反馈编辑单个 prompt）和 APE（要求语义保持的改写）不同，OPRO 利用**整条轨迹**生成可与旧 prompt 语义无关的新候选。

## 实验设置

- 数据集：GSM8K（7,473 train / 1,319 test）、BBH（23 任务，每任务≤250 例，取 20% 优化）；迁移测试 MultiArith、AQuA。
- 模型：optimizer ∈ {PaLM 2-L, PaLM 2-L-IT, text-bison, gpt-3.5-turbo, gpt-4}；scorer ∈ {pre-trained PaLM 2-L, text-bison}。
- baselines：人写 prompt "Let's think step by step."（Kojima 2022）、"Let's work this out in a step by step way..."（Zhou 2022b，即 APE 产物）、空串；以及 EvoPrompt(GA/DE)。
- train/dev/test 切分：**默认不留验证集**（5.4 专门论证为何可以不留）；过拟合分析里临时按 1/3 train、1/3 val、1/3 test 切。
- 成本或调用次数：默认每步 8 候选 × 200 步 ≈ 1600 次候选评估；但论文强调若只为找到"出彩指令"，往往几步即可（GSM8K 第 6 步就得到 78.2 的"Let's do the math!"）。

## 主要结果

论文直接报告：

- GSM8K：optimizer 找到的最佳 instruction 比人写 zero-shot prompt 高**最多 8%**。PaLM 2-L scorer 下 "Take a deep breath and work on this problem step-by-step."（PaLM 2-L-IT 优化）测试 80.2，"Break this down."（PaLM 2-L 优化）79.9，对照 "Let's think step by step." 71.8、空串 34.0（Table 1 / Table 4）。
- BBH：optimizer instruction 在大多数任务上超过 "Let's think step by step." 5% 以上——PaLM 2-L scorer 下 19/23 任务、text-bison scorer 下 15/23 任务；相对空串起点，PaLM 2-L 下 20/23、text-bison 下 15/23 提升超 5%。最高在部分 BBH 任务上提升达 50%（摘要口径）。
- 迁移：GSM8K 上优化的 prompt 迁到同域 MultiArith / AQuA 仍有增益（Table 6，如 "Take a deep breath..." 在 MultiArith 95.3 / AQuA 54.3）。
- 优化曲线整体上升且方差递减：optimizer 随步数生成"分布上更好"的指令，而非单点跳变。

## 失败案例和局限

- **数学/组合优化能力有限（动机实验）**：linear regression 只能在小规模、TSP 在 n=10 时全部命中，n=50 时 optimality gap 比启发式差 up to 20×，明显落后专用 solver。作者明确这只是"LLM 能靠 prompting 做黑盒优化"的演示，不追求 SOTA。
- **过拟合确实存在**：训练准确率常比测试高 5%–20%（5.4，Table 7/10）。作者的辩护是"只要所有候选过拟合程度相近，取最高训练分仍能选到较好测试分"——这是一个**乐观且后续被挑战的假设**（与 TextReg 的 distributional overfitting、Coin Flip 的噪声地板形成对照）。缓解建议：更大训练集 + 早停。
- **轨迹对低质候选敏感**：开局解空间未充分探索时，低分候选会带偏 optimizer 输出，造成不稳定和大方差；靠"每步多采样"缓解。
- **上下文窗口是硬约束**：大规模问题描述塞不进 meta-prompt；轨迹只能截断到 top-20。
- **强 model/task 依赖**：不同 optimizer 产出风格迥异（PaLM/text-bison 简洁、GPT 冗长），最佳 prompt 因模型而异；迁移只验证了同域，未验证跨域/跨模型稳健性。
- **对照 EvoPrompt 的结论有前提**：OPRO 胜出部分因为 EvoPrompt 不用 exemplars、依赖好的初始 prompt；这是 meta-prompt 设计差异而非纯算法优劣。

## 洞见卡片

```yaml
insight: 轨迹驱动（"看历史分数模式生成新候选"）是 LLM-as-optimizer 的一种独立范式，区别于 edit-based(ProTeGi) 和 semantic-preserving(APE)。
evidence_type: direct-method
paper_evidence:
  section: "1, 2.2, 4.2"
  table_or_figure: "Figure 2, Figure 3"
  quote_or_paraphrase: "每步把按分数升序排列的历史 instruction-score 对放进 meta-prompt，让 LLM 生成与旧 prompt 可语义无关的新指令，而非编辑或保持语义改写。"
mechanism: LLM 把 in-context 的"解-分数"序列当作隐式梯度信号，归纳出"哪些表述得高分"。
actionable_rule: 做 optimizer 对照时，至少区分三种信号结构——纯标量轨迹(OPRO)、自然语言 critique(ProTeGi/TextGrad)、轨迹+trace(GEPA)；不要把它们混为"LLM 改 prompt"。
counterexample_or_limit: 纯标量轨迹无法定位错误根因，根因假设不进 hypothesis space 时会原地打转（参见 [[paper-vista-reflection-dark-2026]]）。
minimal_experiment: 同一任务比较 score-only-trajectory rewrite vs critique-guided rewrite，记录样本效率和过拟合 gap。
confidence: high
```

```yaml
insight: "更好的 prompt"常常是 model-specific 的措辞发现，而非更聪明的语义。
evidence_type: direct-result
paper_evidence:
  section: "1, 5.2"
  table_or_figure: "Table 1, Table 4"
  quote_or_paraphrase: "'Take a deep breath...'(80.2) 与 'Break this down.'(79.9) 语义差异大但都高分；不同 optimizer 产出风格迥异，最佳指令含义未必含 step-by-step。"
mechanism: 模型对表层措辞/格式高度敏感，优化器在搜索的是触发某模型某能力的"钥匙短语"。
actionable_rule: 任何 prompt 优化结论都要绑定"在哪个 scorer 模型上"；换模型必须重测，不能默认迁移。
counterexample_or_limit: 这正是脆弱性来源——optimized prompt 跨模型可能失效；OPRO 只验证了同域迁移。
minimal_experiment: 把 A 模型上的最优 prompt 直接搬到 B 模型，测 delta，量化跨模型脆弱性。
confidence: high
```

```yaml
insight: "可以不留验证集"是一个有条件、且后续被挑战的论断。
evidence_type: author-claim + ablation
paper_evidence:
  section: "5.4"
  table_or_figure: "Figure 11, Table 7/10"
  quote_or_paraphrase: "作者论证只要各候选过拟合程度相近，取最高训练分即可；但同时承认训练-测试 gap 常达 5%-20%。"
mechanism: 当 train/val 曲线同涨同跌时，训练分数作为选择信号仍单调有效。
actionable_rule: 本项目相反——默认保留 held-out，并记录 train-test gap 作为安全阀；把 OPRO 的"省验证集"当作可质疑的反面对照而非默认实践。
counterexample_or_limit: 噪声大、小样本或 compound 系统里该假设崩溃（[[paper-coin-flip-2026]]、[[paper-textreg-2026]]）。
minimal_experiment: 复现 OPRO 选择策略，但同时记录 held-out gap 和"按训练分选 vs 按验证分选"的最终测试差。
confidence: medium-high
```

## 对本项目的启发

> 字段定义与 insight / conclusion / helpful method 的区分口径见 `docs/insight_field_standard.md`。

- conclusion：OPRO 是 LLM-as-optimizer 的**基线锚点**而非前沿方法。它证明了"纯标量轨迹 + LLM 生成"就能超人写 prompt，但也暴露了纯标量信号的两大软肋——无法定位根因、强 model/task 依赖。后续 critique/trace 类方法（ProTeGi→GEPA）本质是在补这两个洞。
- helpful method：把 OPRO 的 meta-prompt 结构（升序轨迹 + 截断 archive + 少量 exemplar + 软正则 meta-instruction）作为最简 optimizer 模板，任何更复杂方法都应先打得过它。
- anti-pattern / limit：照搬 OPRO"默认不留验证集"。本项目应把它当反面对照，强制 held-out + train-test gap 记录。
- 适用场景：API-only、有小训练集、有可自动评分的任务（推理/分类/抽取）；想要一个便宜的 optimizer 下限。
- 误用风险：把"Take a deep breath"这类结论当通用 prompt 经验跨模型套用；或把训练分数最高直接当生产 prompt 而不测 OOD。

## 最小验证或演示计划

- 要验证的 insight / method：纯标量轨迹 optimizer 作为下限，对照 critique-guided。
- 最小验证任务：一个结构化抽取或分类任务，100–300 样本，可规则评分。
- 需要实现的模块：(1) OPRO 式 meta-prompt（升序轨迹 top-K + N exemplars）；(2) 每步采样 8 候选、回填轨迹；(3) held-out 评估 + train-test gap 记录；(4) 与 ProTeGi 式 critique rewrite 共用同一评估口径。
- 观察指标：达到目标分所需候选评估数（样本效率）、train-test gap、跨模型迁移 delta、prompt 长度增长。
- 预计风险：小样本下候选差异淹没在噪声里（先做 [[paper-coin-flip-2026]] 式 pre-optimization gate）；optimizer 受低质轨迹带偏。
