# Paper Note: A Survey of Automatic Prompt Engineering: An Optimization Perspective

论文：A Survey of Automatic Prompt Engineering: An Optimization Perspective（Tongji / ECNU）

链接：https://arxiv.org/abs/2502.11560

source_id：paper-ape-survey-2025

关联 issue：无

线索贡献者：internal-arxiv-search（综述补读，用于 taxonomy 外部完整性校验）

新颖性判断：survey-taxonomy-reference（优化理论视角的领域参照系）

阅读日期：2026-06-10

reviewed_by：Claude

local_pdf_path：`local_sources/raw/arxiv_papers/2502.11560/paper.pdf`

local_pdf_sha256：`B85F03302E50963A258716CEC6ACB6DCDE2582850F2BC3E94BB85A6D1181E81D`

local_text_path：`local_sources/raw/arxiv_papers/2502.11560/paper.txt`

local_text_sha256：`D12E443436D261EA610CF7494BA2B5CE35B73FA6A263C8D30EB7243E4CEF0998`

evidence_level：method-and-taxonomy-read（读了优化框架 Fig 1、优化空间/目标/方法三轴、constrained objectives §5.2、§7 future directions；逐论文细节略读）

版本说明：本地 PDF 为 v1（2025-02-17）。

## 一句话结论

这份综述用**优化理论的统一框架**组织自动 prompt engineering：把问题写成在"离散/连续/混合 prompt 空间"上最大化期望指标，再按 **优化变量 × 目标函数（含约束）× 优化方法** 三个轴归类。对本项目最有价值的是它的 §7：明确点名 7 个 underexplored frontier，其中 **constrained optimization、multi-task、online（task-agnostic）、multi-objective、bi-level/thought-driven（o1/R1）、multi-agent** 几个直接指出我们 taxonomy 里偏弱或缺席的格子。

## Survey 定位与范围

- 视角：applied-optimization；跨 text / vision / multimodal（比我们的范围宽）。
- 形式化：max_{P∈P} E[g(f(P(x)), y)]，P 可为离散、连续(soft)、或混合空间。

## Taxonomy 结构（Fig 1，三轴）

1. **优化空间 §4**：Discrete（hard instructions/exemplars）/ **Continuous（soft prompt：prefix-based、layer-spanning embedding）** / **Mixed（hybrid，instruction+exemplar 或 +soft）**。
2. **目标函数 §5**：Downstream tasks（instruction induction、分类、math、commonsense、multi-hop、domain-specific、multimodal）；指标（exact/set match、F1、BERTScore、perplexity）；**Constrained objectives §5.2**：Prompt Editing（受限编辑预算）/ **Prompt Compression（∥P∥≤κ 长度预算）**——形式化为 Γ(P)≤κ。
3. **优化方法 §6**：FM-based（heuristic / automatic meta-prompt、strategic search & replanning、prompt editing、compression）/ Evolutionary（genetic operators、self-referential）/ Gradient-based（discrete token gradient、soft prompt tuning）/ Reinforcement Learning（PRewrite/PACE/StablePrompt/Evoke；multi-objective & inverse RL：Prompt-OIRL、MORL-Prompt、MAPO）。

## §7 它点名的 underexplored frontier（7 个）

1. **Constraint optimization**：在离散 prompt 搜索里纳入语义/伦理约束、human-value、资源界、可读性，并形式化为可解约束。
2. **Multi-task PO**：跨任务共享结构、negative transfer、缺"prompt similarity"形式定义。
3. **Online PO**：非平稳、用户意图漂移、bounded dynamic regret（= APO survey 的 task-agnostic/inference-time）。
4. **Multi-objective PO**：Pareto / 多准则 / 博弈论仲裁竞争目标（与 [[paper-textreg-2026]]、When Gradients Collide 呼应）。
5. **Heterogeneous modality**：vision/多模态——本项目刻意排除。
6. **Bi-level PO（thought-driven，o1/R1）**：prompt 作为推理链的高层控制器，微小改动剧烈改变 reasoning trajectory，平衡点是否存在/唯一是开放问题。
7. **Broader applications**：multi-turn agent 的序贯决策、multi-agent 博弈均衡、垂域大模型约束。

## 对本项目 taxonomy 的完整性信号

- **确认覆盖**：FM-based / evolutionary / RL / 我们的 textual-gradient（≈discrete token gradient）都对得上；instruction↔exemplar 联合优化它也强调。
- **刻意越界但应明确登记为边界**：continuous(soft) prompt、multimodal、gradient-based soft tuning——本项目排除，但综述把它们与离散方法放进同一框架，提醒我们在渠道综合里写清"我们只做离散自然语言 prompt"。
- **真正值得补的格子**：
  - **Constrained optimization** 的形式化（Γ(P)≤κ）——给我们的 prompt-hygiene/length 主题（[[paper-textreg-2026]]、[[paper-causal-edit-level-2026]]）一个优化理论外壳。
  - **Bi-level / thought-driven（o1/R1）**——推理模型时代"prompt 作为推理控制器"的视角，我们 taxonomy 完全没有。
  - **Online / task-agnostic** 与 **multi-task / negative transfer**——两份综述都点名，我们只在 memory（[[paper-memapo-2026]]、[[paper-erm-memory-2024]]）侧间接触及。

## 对本项目的启发

> 字段定义与 insight / conclusion / helpful method 的区分口径见 `docs/insight_field_standard.md`。

- conclusion：本项目"离散自然语言 prompt 优化"的范围是清晰且合理的选择，但应在渠道综合里**显式声明边界**（不含 soft prompt / multimodal），并把 constrained optimization、bi-level（推理模型）、online/multi-task 三个 frontier 列为"已知存在、当前未覆盖"，避免被读作疏漏。
- helpful method：用"优化空间×目标(含约束)×方法"三轴给本项目的方法卡补一行坐标，尤其把 hygiene/length 主题挂到 constrained-optimization 轴。
- anti-pattern / limit：把 prompt 优化只当无约束的指标最大化——综述明确无约束化会牺牲可读性、资源界和价值对齐。
- 适用场景：界定本项目范围边界、补 frontier 缺口清单、给 governance 主题一个优化理论表述。
- 误用风险：该综述跨模态、含 soft prompt，直接照搬其 taxonomy 会把本项目刻意排除的方向重新拉进来。

## 最小验证或演示计划

- 要验证的 insight / method：把 §7 的 7 个 frontier 与本项目 taxonomy 逐格比对，标"已覆盖/边界外/待补"。
- 最小验证任务：在渠道综合里加一节"范围边界与已知 frontier 缺口"。
- 观察指标：待补 frontier 数、与现有论文笔记的挂接数。
- 预计风险：bi-level / 推理模型方向新论文可能不在 top80 样本里，需另起一次定向搜索。
