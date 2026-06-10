# arXiv Taxonomy 外部完整性校验（对照 3 篇综述）

日期：2026-06-10

目的：用 3 篇独立综述作为外部参照系，校验 `docs/arxiv_top80_taxonomy.md` 的 7 簇方法分类是否漏掉整块子领域，并区分"真缺口 / 刻意边界 / 值得登记的相邻方向"。本文是覆盖核对，不产出新方法结论。

对照来源（均已全文/taxonomy 级深读，证据见对应 paper note）：

- APO Survey（AWS）：`docs/paper_notes/paper-apo-survey-2025.md`（按优化流程 anatomy 的 5 部分框架）。
- APE Survey（Tongji/ECNU）：`docs/paper_notes/paper-ape-survey-2025.md`（优化理论三轴 + 7 个 frontier）。
- Context Engineering Survey（ICT/CAS）：`docs/paper_notes/paper-context-engineering-2025.md`（prompt 优化的超集框架）。

被校验对象：`docs/arxiv_top80_taxonomy.md` 的 7 簇——① 经典 APO/基线锚点 ② textual gradient/反思 ③ 进化/自指/记忆 ④ prompt-as-program/框架 ⑤ agent/system/多 agent/工具 ⑥ 偏好/人类反馈/judge/治理 ⑦ 应用型 APO。

## 一句话结论

**在"离散自然语言 prompt/instruction 优化"这个声明范围内，本项目 7 簇 taxonomy 没有漏掉整块子领域**——3 篇综述的方法大类都能映射到现有簇。校验查出的不是"漏掉的大领域"，而是两类更细的东西：(A) 簇内偏轻的**子机制**（学习型评分、token 级编辑、bandit 筛选、MoE 路由）；(B) 综述共同点名、我们当前未单列的**新兴 frontier**（task-agnostic/online、constrained optimization、bi-level/thought-driven 推理模型、multi-task/negative-transfer）。另有几条是**刻意边界**（soft prompt、multimodal、完整 context-engineering 系统），应在渠道综合里显式声明而非默默缺席。

## 一、覆盖确认：7 簇 ↔ 综述大类映射

| 本项目簇 | APO Survey 对应 | APE Survey 对应 | 结论 |
| --- | --- | --- | --- |
| ① 经典 APO/锚点 | Seed §3 + Numeric eval §4.1 | FM-based meta-prompt | 覆盖；锚点已补深读（APE/OPRO/DSPy/MIPROv2/TextGrad） |
| ② textual gradient/反思 | LLM Feedback §4.2 + Metaprompt §5.3 | discrete token gradient | 覆盖 |
| ③ 进化/自指/记忆 | 遗传算法 §5.1.2 + variable iteration §7 | Evolutionary（genetic/self-referential） | 覆盖 |
| ④ prompt-as-program | Program Synthesis §5.5 | FM-based strategic search | 覆盖 |
| ⑤ agent/system/多 agent | §9.3（点名为 underexplored） | §7 broader applications | 覆盖且为前沿 |
| ⑥ 偏好/judge/治理 | Reward-model §4.1.2 + Human §4.3 | multi-objective/inverse RL §6 | 覆盖 |
| ⑦ 应用型 APO | 散见各 application | domain-specific tasks | 覆盖 |

→ 没有"整块大领域"落在 7 簇之外。

## 二、簇内偏轻的子机制（建议在渠道综合登记为"已知存在、本项目未深入"）

来自 APO Survey 的细粒度 anatomy，本项目按"方法簇"组织时容易略过这些**评分/候选/筛选子机制**：

1. **学习型评分信号**：reward-model score（OIRL 的 XGBoost、DRPO）、entropy-based（CLAPS、GrIPS）、NLL（GPS、PACE）。我们几乎只用 task accuracy / LLM-judge 两类信号。
2. **非 LLM 候选生成**：RL（RLPrompt 已在 inventory 但未深读）、LLM finetuning、GAN 式编辑。
3. **token 级离散编辑**：word/phrase edits、vocabulary pruning（我们聚焦 instruction 级，token 级几乎不碰）。
4. **候选筛选策略**：UCB/bandit 变体、region-based joint search、meta-heuristic ensemble（我们只在 MASPOB 间接触及 bandit）。
5. **MoE / per-cluster 路由**：MOP、GPO 的 cluster-specific prompt、mixture-of-experts（我们有 Prompt Codebooks 的 per-input routing，但 MoE 家族未单列）。

影响判断：这些多属"已被经典方法覆盖、对本项目 5 天交付优先级不高"的子机制，**不必逐一深读**，但渠道综合应一句话承认其存在并给指针，避免被读作疏漏。

## 三、综述共同点名、本项目未单列的新兴 frontier（建议补登记，部分值得定向搜索）

两份 APO/APE 综述的 future-directions **高度重合**，指向我们 taxonomy 没有专门格子的方向：

| Frontier | APO Survey | APE Survey | 本项目现状 | 建议 |
| --- | --- | --- | --- | --- |
| **Task-agnostic / online PO**（无 Dval、用户意图漂移、非平稳） | §9.1 | §7 online | 仅 memory 侧间接触及 | 登记为 frontier；与自进化主线相关，值得 1 次定向搜索 |
| **Constrained optimization**（语义/伦理/资源/可读性约束，Γ(P)≤κ） | — | §7 constraint | 有 hygiene/length 实证（TextReg/edit-level）但无优化理论外壳 | 给现有 hygiene 主题挂"约束优化"表述 |
| **Bi-level / thought-driven（o1/R1）**：prompt 作为推理链高层控制器 | — | §7 bi-level | 完全缺席 | **最值得补**：推理模型时代的新范式，top80 样本可能未覆盖，需定向搜索 |
| **Multi-task / negative transfer** | §9.1 | §7 multi-task | memory 跨任务污染侧触及 | 登记；与 memory 过滤（ERM/MemAPO）合并讨论 |
| **Multi-objective（Pareto/博弈论仲裁）** | — | §7 multi-obj | 有 When Gradients Collide、GEPA Pareto | 已部分覆盖，补博弈论视角即可 |
| **Unclear mechanisms**（evil twins、乱码分隔符、反思错判根因） | §9.2 | — | 已强（VISTA、flawed metaphor） | 已覆盖，可引综述佐证 |

## 四、刻意边界（确认是范围选择，非缺口——但需显式声明）

- **soft / continuous prompt tuning、prefix/layer-spanning embedding**：APE Survey 把它与离散方法并列，本项目 focus 评分的 `NEGATIVE_RULES` 明确惩罚——刻意排除。
- **multimodal（text-to-image/video/audio、VLM）**：两份综述都列为方向，本项目明确不做。
- **完整 context-engineering 系统**：RAG 架构/检索器优化、长上下文处理、function-calling 机制、多 agent 通信协议——属 Context Engineering Survey 的系统实现层，本项目当边界材料。

→ 这些不是"漏了"，是"选了不做"。渠道综合/最终报告应有一节"范围边界：我们不做什么"，逐条声明，把它们从"疑似缺口"变成"明确边界"。

## 五、值得登记为"边界但相邻"的两条优化目标

来自 Context Engineering Survey，与本项目可优化 prompt artifact 直接相交：

1. **上下文压缩（Context Compression §4.3.3）**＝约束式 prompt 优化（∥P∥≤κ），与 hygiene/length 主题同构，应作为 backlog 条目登记。
2. **智能上下文组装/选择（Intelligent Context Assembly §4.1.3/§7.2.4）**＝exemplar/context selection 的放大版，本项目 exemplar 优化（Teach Better or Show Smarter）是其子集。

## 六、对渠道综合（步骤 2）的具体输入

校验完成后，渠道综合应纳入：

1. 增一节**「范围边界」**：显式声明不做 soft prompt / multimodal / 完整 context-engineering 系统。
2. 增一节**「已知 frontier 缺口」**：列 task-agnostic/online、constrained optimization、bi-level/thought-driven、multi-task/negative-transfer，标注"已知存在、当前未覆盖"。
3. 在横向矩阵给每篇论文补**优化流程五维标签**（seed/eval/candidate/filter/iteration，借 APO Survey anatomy），暴露零覆盖子机制。
4. 把 hygiene/length 主题挂到 **constrained-optimization** 表述下。

## 七、最高优先级单项行动

**bi-level / thought-driven（推理模型 o1/R1 时代的 prompt 优化）** 是唯一一个"整块相邻、本项目完全缺席、且很可能不在 2026-06-08 的 top80 样本里"的方向——建议作为下一次定向 arXiv 搜索的主题（关键词：reasoning-model prompt optimization、prompt for o1/R1/DeepSeek-R1、test-time reasoning prompt）。其余子机制与 frontier 以"登记 + 指针"处理即可，不必在本阶段全部深读。
