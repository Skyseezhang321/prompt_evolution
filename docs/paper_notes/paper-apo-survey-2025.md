# Paper Note: A Systematic Survey of Automatic Prompt Optimization Techniques

论文：A Systematic Survey of Automatic Prompt Optimization Techniques（AWS）

链接：https://arxiv.org/abs/2502.16923

source_id：paper-apo-survey-2025

关联 issue：无

线索贡献者：internal-arxiv-search（综述补读，用于 taxonomy 外部完整性校验）

新颖性判断：survey-taxonomy-reference（不提供新方法，提供领域完整性参照系）

阅读日期：2026-06-10

reviewed_by：Claude

local_pdf_path：`local_sources/raw/arxiv_papers/2502.16923/paper.pdf`

local_pdf_sha256：`54E11E43080055AA6AA8479E13E0899DC560F6157B109CC6F11BC78853C3E0C2`

local_text_path：`local_sources/raw/arxiv_papers/2502.16923/paper.txt`

local_text_sha256：`71FB01282EE3F250CE782A9AE4D43155A86C09D79729A3388125C2AFFED035B0`

evidence_level：method-and-taxonomy-read（读了 5 部分框架、Algorithm 1、各 §3–§7 子类、§9 challenges；附录大表与逐论文归类略读）

版本说明：本地 PDF 为 v2（2025-04-02）。

## 一句话结论

这是按**优化流程 anatomy** 组织的 black-box APO 综述：把任意 APO 系统拆成 5 个可替换阶段（seed → 评估反馈 → 候选生成 → 筛选保留 → 迭代深度），每阶段再细分。它对本项目最大的用处不是结论，而是一个**外部参照系**——用它的细粒度子类去比对 `arxiv_top80_taxonomy.md`，能查出我们按"方法簇"组织时容易漏掉的几类（学习型 reward model、entropy/NLL 评分、token 级编辑、bandit/UCB 筛选、mixture-of-experts 路由）。

## Survey 定位与范围

- 范围：black-box（无需参数访问）的离散自然语言 prompt 优化；明确把 soft/visual prompt tuning 排除在主线之外。
- 形式化：ρopt = argmax_ρ E[f(M_task(ρ⊕x))]（式 1），离散组合空间不可解，故走 Algorithm 1 的近似迭代。

## Taxonomy 结构（5 部分框架，Fig 1）

1. **Seed Prompts §3**：Manual Instructions §3.1 / Instruction-induction via LLMs §3.2（APE、SCULPT 从 README 诱导、UniPrompt 填结构模板、MOP/GPO 诱导 cluster-specific prompt）。
2. **Inference Evaluation & Feedback §4**：
   - Numeric §4.1：Task accuracy / **Reward-model score（学习型，OIRL XGBoost、DRPO）** / **Entropy-based（CLAPS、GrIPS）** / **NLL（APE、GPS、PACE）**。
   - LLM Feedback §4.2（改单候选 / 改多候选）。
   - Human Feedback §4.3。
3. **Candidate Generation §5**：Heuristic edits §5.1（Monte Carlo / **遗传算法** / **word-phrase 编辑** / **vocabulary pruning**）/ Editing with auxiliary trained NN §5.2（**RL** / **LLM finetuning** / **GAN**）/ Metaprompt design §5.3 / Coverage-based §5.4（single-prompt expansion / **mixture-of-experts** / ensemble）/ **Program Synthesis §5.5**。
4. **Filter & Retain §6**：TopK Greedy §6.1 / **UCB & 变体（bandit）§6.2** / **Region-based joint search §6.3** / Meta-heuristic ensemble §6.4。
5. **Iteration depth §7**：Fixed §7.1 / Variable（含 early-convergence）§7.2。

## §9 它点名的 underexplored 方向

- **Task-agnostic / inference-time APO**：现有方法都假设任务已知且有 Dval，生产环境常没有；多未知任务的推理时优化欠研究。
- **Unclear mechanisms**：prompt 的 "evil twins"（不可读却能恢复性能）、乱码分隔符也有效、self-reflection 会错判根因——机制尚不清楚（与 [[paper-textual-gradients-flawed-metaphor-2025]]、[[paper-vista-reflection-dark-2026]] 呼应）。
- **APO for system prompts / agents**：SPRIG 优化 system prompt 需 ~60 小时 vs ProTeGi ~10 分钟/任务；agentic 系统多组件并发优化是开放方向。
- **Multimodal APO**：text-to-image/video/audio——本项目刻意排除的方向。

## 对本项目 taxonomy 的完整性信号

- **确认覆盖**：我们的 textual-gradient、evolutionary、prompt-as-program、agent/multi-agent、preference/governance 簇都能在它的框架里找到对应位置。
- **我们偏轻的子类**（值得在渠道综合里至少登记为"已知存在、本项目未深入"）：learned reward-model 评分、entropy/NLL 评分、RL/GAN/finetune 式候选生成、token 级 word-phrase 编辑与 vocabulary pruning、bandit/UCB 与 region-based 筛选、mixture-of-experts / per-cluster 路由。
- **刻意越界**：soft/visual prompt、multimodal——与我们 focus 评分的 NEGATIVE_RULES 一致，确认是范围边界而非疏漏。

## 对本项目的启发

> 字段定义与 insight / conclusion / helpful method 的区分口径见 `docs/insight_field_standard.md`。

- conclusion：本项目的 7 簇 taxonomy 在"方法语义"上覆盖完整，但在"优化流程的筛选/评分子机制"上比这份 anatomy 粗——尤其 candidate 筛选策略（bandit/UCB/region-based）和非 LLM 评分信号（reward model/entropy/NLL）我们几乎没展开。
- helpful method：把这份 5 阶段 anatomy 当作渠道综合的"检查清单"——每个新方法都标注它落在哪个阶段、用什么评分、什么筛选，避免只按"方法名"归类而漏掉机制差异。
- anti-pattern / limit：把按方法簇组织的 taxonomy 当作穷尽——簇与簇之间的"评分×筛选×迭代"组合空间才是真正的设计空间。
- 适用场景：渠道综合的覆盖核对、新论文归类的统一坐标系。
- 误用风险：survey 自身承认会把多机制论文（如 Tempera 同时含 RL + word-level 编辑）按"最显著特征"归一类，存在粗化；不要把它的单一归类当论文全貌。

## 最小验证或演示计划

- 要验证的 insight / method：用这份 anatomy 把本项目已深读的 30+ 篇逐一打"阶段标签"，统计哪些阶段/评分/筛选子类零覆盖。
- 最小验证任务：对 `arxiv_top80_taxonomy.md` 横向矩阵增列 seed/eval/candidate/filter/iteration 五维标签。
- 观察指标：零覆盖子类数量、与 top80 簇的映射冲突数。
- 预计风险：anatomy 的细粒度子类与我们"方法簇"非一一对应，映射需人工判断。
