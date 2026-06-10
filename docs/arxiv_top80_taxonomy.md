# arXiv Top80 分类综述与横向矩阵

更新时间：2026-06-08

数据来源：`outputs/arxiv_prompt_search/arxiv_focus_top80_20260608T131514Z.csv`

证据等级：标题 + arXiv 摘要 + 自动分类的一读矩阵。本文用于粗筛和深读排期，不作为最终结论。

## 分析框架

本批论文统一按以下维度分析：

| 维度 | 关注问题 |
| --- | --- |
| 优化对象 | 改 instruction、few-shot examples、system prompt、结构化 prompt section、workflow、agent role、tool policy、memory，还是 optimizer 自身。 |
| 反馈信号 | 使用任务分数、自然语言 critique、textual gradient、pairwise preference、human feedback、judge score、执行轨迹、工具错误、失败样本还是 memory。 |
| 候选生成 | 使用 LLM rewrite、beam search、evolutionary operators、bandit/Bayesian、program compiler、agentic tool loop、code analysis 或 synthetic data。 |
| 候选选择 | 用 dev set 分数、Pareto frontier、successive halving、pairwise preference、joint agent outcome、guard metric、cost-aware objective 还是 archive。 |
| 评估可信度 | 是否报告数据集、模型、baseline、train/dev/test 隔离、成本、失败案例、泛化和代码。 |
| 对项目价值 | 能否作为 baseline、taxonomy source、风险证据、工程设计参考或最小实验候选。 |

## 方法簇 1：经典 APO 与基线锚点

代表论文：

- [ProTeGi](https://arxiv.org/abs/2305.03495)：用自然语言“梯度”批评 prompt，再做 beam search。
- [AutoHint](https://arxiv.org/abs/2307.07415)：通过 hint generation 做自动 prompt 优化。
- [EvoPrompt](https://arxiv.org/abs/2309.08532)：连接 LLM 与进化算法做离散 prompt 搜索。
- [PromptBreeder](https://arxiv.org/abs/2309.16797)：同时进化 task prompts 和 mutation prompts。
- [Are Large Language Models Good Prompt Optimizers?](https://arxiv.org/abs/2402.02101)：直接评估 LLM 作为 prompt optimizer 的能力边界。

粗读判断：

这些论文构成历史基线，价值不只在性能，而在问题形式化：prompt 可以作为自然语言离散对象被生成、评价、选择和回滚。后续实验若要建立 baseline，至少需要覆盖 manual prompt、APE/LLM rewrite、ProTeGi-style textual feedback、evolutionary search 中的 2-3 类。

## 方法簇 2：Textual Gradient 与反思式优化

代表论文：

- [Scaling Textual Gradients via Sampling-Based Momentum](https://arxiv.org/abs/2506.00400)：讨论 textual gradient 扩展到更多训练数据时的上下文墙和稳定性问题。
- [CriSPO](https://arxiv.org/abs/2410.02748)：面向生成任务，用多方面 critique-suggestion 指导 prompt 修改。
- [Modular Prompt Optimization](https://arxiv.org/abs/2601.04055)：把结构化 prompt 拆成 section，用局部 textual gradient 优化。
- [Reflection in the Dark](https://arxiv.org/abs/2603.18388)：指出 reflective APO 的黑箱轨迹和失败模式，并用多 agent 分离 hypothesis 与 rewriting。
- [TextReg](https://arxiv.org/abs/2605.21318)：把 prompt distributional overfitting 作为 text-space optimization 的正则化问题处理。
- [Textual Gradients are a Flawed Metaphor](https://arxiv.org/abs/2512.13598)：挑战 textual gradient 类比本身，提醒不要把自然语言反馈误当可微梯度。

粗读判断：

Textual gradient 的真正价值可能不是“梯度类比”，而是把失败样本转成可读、可审计、可局部应用的修改建议。该方向最值得转化为本项目实验的是：同一任务上比较 scalar score、free-form critique、section-local critique 三种反馈信号，并记录 prompt 增长、泛化和失败模式。

## 方法簇 3：进化、自指和记忆型自进化

代表论文：

- [EvoPrompt](https://arxiv.org/abs/2309.08532)：population + evolutionary operators。
- [PromptBreeder](https://arxiv.org/abs/2309.16797)：自指地优化 mutation prompt。
- [GEPA](https://arxiv.org/abs/2507.19457)：结合轨迹反思、Pareto frontier 和 prompt evolution。
- [MemAPO](https://arxiv.org/abs/2603.21520)：把成功策略和失败模式沉淀为双 memory。
- [SePO](https://arxiv.org/abs/2606.04465)：把 prompt agent 自身的 system prompt 也纳入优化对象。
- [Prompt Codebooks](https://arxiv.org/abs/2605.28360)：把可复用 instruction units 组织为 codebook，并按实例路由。
- [C-MOP](https://arxiv.org/abs/2602.10874)：把 momentum 和 clustering 用于 prompt evolution。

粗读判断：

本批论文里的自进化有三种不同对象：task prompt、optimizer prompt、经验 memory。后续文档和实验必须分开记录，否则无法判断收益来自更好的 prompt、更多搜索预算，还是来自 optimizer 本身的经验迁移。

## 方法簇 4：Prompt-as-Program、结构化 prompt 与框架化工具

代表论文：

- [Promptomatix](https://arxiv.org/abs/2507.14241)：从任务描述生成 prompt，结合 meta-prompt optimizer 和 DSPy compiler。
- [AutoPDL](https://arxiv.org/abs/2504.04365)：把 agent prompting pattern 与 demonstrations 搜索写成可执行 PDL program。
- [promptolution](https://arxiv.org/abs/2512.02840)：统一、模块化的 prompt optimization 框架。
- [Is It Time To Treat Prompts As Code?](https://arxiv.org/abs/2507.03620)：用 DSPy 做多用例 prompt optimization case study。
- [A Comparative Study of DSPy Teleprompter Algorithms](https://arxiv.org/abs/2412.15298)：比较 DSPy teleprompter 与人类评估对齐。
- [Composing Policy Gradients and Prompt Optimization for Language Model Programs](https://arxiv.org/abs/2508.04660)：把 prompt optimization 放到 language model programs 中讨论。

粗读判断：

这类论文把 prompt 从文本片段提升为可编译、可组合、可执行、可复用的程序组件。对本项目来说，prompt-as-program 的工程价值高于单次分数提升，因为它天然支持版本追踪、局部回滚和实验隔离。

## 方法簇 5：Agent、系统 prompt、多 agent 和工具链优化

代表论文：

- [SPEAR](https://arxiv.org/abs/2605.26275)：agentic optimizer 使用 evaluate/python/set_prompt/finish 工具，并提供 auto-rollback 和 guard metric。
- [AutoPDL](https://arxiv.org/abs/2504.04365)：搜索 agentic/non-agentic prompting patterns。
- [System Prompt Optimization with Meta-Learning](https://arxiv.org/abs/2505.09666)：专门优化 system prompt。
- [MASPO](https://arxiv.org/abs/2605.06623)：联合优化多 agent 系统中的 role prompts。
- [MAPRO](https://arxiv.org/abs/2510.07475)：把 multi-agent prompt optimization 重写为 MAP inference。
- [MASPOB](https://arxiv.org/abs/2603.02630)：bandit-based multi-agent prompt optimization。
- [JTPRO](https://arxiv.org/abs/2604.19821)：联合 tool-prompt reflective optimization。

粗读判断：

Agent 场景里，优化对象不再是“回答 prompt”，而是 role、tool policy、workflow、局部 agent 输出和全局成功之间的 credit assignment。该方向很适合本项目后续做最小实验，因为可以选择一个小型 tool-use 任务，比较 manual prompt、局部 role prompt 改写和带 guard metric 的 agentic optimizer。

## 方法簇 6：偏好、人类反馈、judge 与治理

代表论文：

- [PrefPO](https://arxiv.org/abs/2603.19311)：用 pairwise preference 和 LLM discriminator 支持无标签优化。
- [PROMST](https://arxiv.org/abs/2402.08702)：在 multi-step tasks 中结合 human feedback 和 heuristic sampling。
- [LLM Prompt Duel Optimizer](https://arxiv.org/abs/2510.13907)：用 label-free duel / preference 做 prompt optimization。
- [When Prompt Optimization Becomes Jailbreaking](https://arxiv.org/abs/2603.19247)：把 prompt optimization 与 adaptive red-teaming 联系起来。
- [When Gradients Collide](https://arxiv.org/abs/2605.26046)：分析 LLM judges 的多目标 prompt optimization failure modes。
- [Exploiting LLM-as-a-Judge Disposition](https://arxiv.org/abs/2604.20726)：提示 optimizer 可能利用 judge 倾向。

粗读判断：

这一簇是后续风险章节的核心证据来源。只要 optimizer 面向 judge 或偏好信号优化，就必须防 prompt hacking、judge gaming、过拟合到 rubrics、牺牲安全边界和 prompt 变长。

## 方法簇 7：应用型 APO 与经验研究

代表论文：

- [APO for Knowledge Graph Construction](https://arxiv.org/abs/2506.19773)：比较 DSPy、APE、TextGrad 在 triple extraction 上的效果。
- [AutoMedPrompt](https://arxiv.org/abs/2502.15944)：医疗 prompt 优化。
- [Clinical QA / ArchEHR-QA 系列](https://arxiv.org/abs/2506.10751)：医疗 evidence-grounded QA 的 agentic prompt optimization。
- [Knowledge Restoration-driven Prompt Optimization](https://arxiv.org/abs/2601.15037)：面向 open-domain relation triplet extraction。
- [Political Science Text Classification](https://arxiv.org/abs/2409.01466)：文本分类和 dynamic exemplar selection。
- [APRIL](https://arxiv.org/abs/2509.25196)：API synthesis 中的 APO + RL。

粗读判断：

应用论文的价值不在提出通用算法，而在提供任务边界、指标选择、跨模型表现和失败案例。它们适合作为后续实验场景参考，但不应优先作为方法 taxonomy 的核心证据。

## 横向证据矩阵：优先深读候选

| 论文 | 优化对象 | 反馈信号 | 搜索/选择方式 | 本项目价值 |
| --- | --- | --- | --- | --- |
| ProTeGi | task prompt | textual critique / task score | semantic edit + beam search | 经典 textual-gradient baseline |
| EvoPrompt | task prompt population | dev score | evolutionary operators | 经典进化 baseline |
| PromptBreeder | task prompt + mutation prompt | fitness on train set | self-referential evolution | 自指优化起点 |
| GEPA | prompts in AI system | trajectory reflection | Pareto / evolutionary search | 当前强 baseline 与实验候选 |
| SePO | task agent prompt + prompt agent system prompt | task benchmark score / self-evolution archive | open-ended evolutionary search | optimizer 自身可优化的核心证据 |
| MemAPO | prompt + reusable memory | success strategies + failure patterns | memory retrieval/editing | 长期经验积累机制 |
| Modular Prompt Optimization | structured prompt sections | section-local textual gradients | schema-preserving local edits | 可回滚结构化 prompt 方案参考 |
| Scaling Textual Gradients | prompt updates | minibatch textual gradients | momentum sampling / Gumbel-Top-k | textual gradient 扩展性证据 |
| Textual Gradients are a Flawed Metaphor | textual-gradient methods | behavioral experiments | critique / case study | 反证与术语风险 |
| PrefPO | prompt | pairwise preference | LLM discriminator + optimizer loop | 无标签优化与 prompt hacking 风险 |
| CriSPO | generation task prompt | multi-aspect critique-suggestion | optimizer + suffix tuning | 多指标生成任务 APO |
| SPEAR | prompt + optimizer workflow | eval dataframe / code analysis | agentic tool loop + rollback | 工程化 agent optimizer 参考 |
| AutoPDL | agent configuration / PDL prompt program | task score | successive halving over prompt programs | prompt-as-program baseline |
| MASPO | multi-agent role prompts | joint downstream outcome | evolutionary beam search | 多 agent credit assignment |
| TextReg | prompt edits | regularized textual gradients | OOD-aware regularized update | prompt overfitting 治理 |
| Why Prompt Optimization Works... | prompt edit families | cross-task observational analysis | causal-inspired analysis | 解释失败和迁移边界 |
| Prompt Codebooks | reusable instruction units | structured critic verdict | codebook + router + generator | 可复用经验单元 |
| Reflection in the Dark | reflective APO trajectory | labeled hypotheses / minibatch verification | multi-agent explore-exploit | reflective optimizer 可解释性 |
| Prompt Optimization Is a Coin Flip | compound AI prompts | task outcomes / failure diagnosis | diagnostic analysis | 何时不该自动优化 |
| When Prompt Optimization Becomes Jailbreaking | adversarial prompts | safety eval / red-team signal | adaptive optimization | 安全边界证据 |

## 初步深读优先级

### P0：直接影响方案选择

- ProTeGi、GEPA、SePO、MemAPO、Modular Prompt Optimization、SPEAR、AutoPDL、MASPO、TextReg、PrefPO。

### P1：影响 taxonomy 和风险章节

- Textual Gradients are a Flawed Metaphor、Why Prompt Optimization Works、Reflection in the Dark、Prompt Optimization Is a Coin Flip、When Prompt Optimization Becomes Jailbreaking、When Gradients Collide。

### P2：应用和场景参考

- Knowledge Graph APO、AutoMedPrompt、ArchEHR-QA 系列、Political Science Text Classification、APRIL、Knowledge Restoration-driven Prompt Optimization。

## 当前缺口

- ~~需要补读不一定在 top80 中的经典锚点：APE、OPRO、DSPy、MIPROv2、TextGrad 原始论文。~~（2026-06-10 已闭合：5 篇均完成全文证据级深读，笔记见 `docs/paper_notes/paper-ape-2022.md`、`paper-opro-2023.md`、`paper-dspy-2023.md`、`paper-miprov2-2024.md`、`paper-textgrad-2024.md`；连同已有的 ProTeGi/EvoPrompt/PromptBreeder 形成 APE→ProTeGi→OPRO→PromptBreeder/EvoPrompt→DSPy→TextGrad→MIPROv2→GEPA 的基线主干。仍待补的更早锚点：AutoPrompt、RLPrompt、GrIPS。）
- 2026-06-10 完成对照 3 篇综述（APO survey 2502.16923、APE survey 2502.11560、Context Engineering survey 2507.13334）的**外部完整性校验**，结论见 `docs/arxiv_taxonomy_completeness_check_20260610.md`：本 7 簇在"离散自然语言 prompt 优化"范围内无整块遗漏；查出的是簇内偏轻子机制（学习型评分/token 级编辑/bandit 筛选/MoE 路由）、需登记的 frontier（task-agnostic/online、constrained optimization、bi-level/thought-driven 推理模型、multi-task）、以及需显式声明的刻意边界（soft prompt、multimodal、完整 context-engineering 系统）。最高优先级单项补读：bi-level/thought-driven（o1/R1 推理模型）prompt 优化。
- 当前矩阵尚未核验每篇论文的 train/dev/test 切分、成本和代码可用性。
- 需要将 P0 论文逐篇转成 `docs/paper_notes/` 模板笔记，再决定最小实验候选。
- 如果要从论文分类进入洞见和经验总结，先读 `docs/arxiv_top80_insights.md`，其中把主要论文条目提炼成了可验证的 insight cards。
- 如果要从 taxonomy 进入可执行工作流，先读 `docs/arxiv_top80_action_playbook.md`，其中把主要问题拆成了具体症状、解决方案和最小实验。
