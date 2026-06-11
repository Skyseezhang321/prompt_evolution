# 文献地图

更新时间：2026-06-12

状态：paper_notes 全目录。下方主表收录全部 39 篇已完成深读笔记（每行链接 arXiv 原文与仓库内笔记），另附「已登记、尚未深读」候选清单。新增来源仍先按 [资料搜集计划](source_collection_plan.md) 登记和分类，再决定是否进入深读笔记；完整处理状态见 [来源清单](source_inventory.md)。

筛选标准：优先收录直接讨论 automatic prompt optimization、prompt evolution、self-improving/self-evolving prompts、prompt-as-program、context engineering、eval-driven prompt iteration 的论文或框架。

收录口径说明：主表按「已写深读笔记」收录，含两类主线之外的特殊条目，均在定位列标注——对照基线类（如 Prompt Repetition，零成本结构变换、非 APO 方法本身，作任何 optimizer 报告增益前的对照底线）与内部基线（PROSE 系 coin-flip 作者自建对照、非独立文献）。

## 快速脉络

> 主线七法（APE→ProTeGi→OPRO→DSPy→TextGrad→MIPROv2→GEPA）的逐方法详细介绍见 [APO 七法主线详解](apo_seven_methods_primer_20260611.md)，所有数字与各深读笔记同口径。

1. 早期自动 prompt 生成：把 instruction 当成可搜索的程序。
2. 文本梯度与黑盒搜索：用错误反馈生成自然语言 critique，再编辑 prompt。
3. 进化与自指优化：同时优化 task prompt 和 mutation/optimizer prompt。
4. 程序化 prompt 系统：DSPy 把 LM pipeline 抽象成可编译程序，通过指标优化 prompt 和示例。
5. 反思式进化：GEPA 等方法利用执行轨迹做自然语言诊断和 Pareto 搜索。
6. 记忆与自进化：MemAPO、SePO 把成功经验、失败模式、优化器自身 prompt 纳入长期改进。
7. 上下文工程：研究对象从 prompt 字符串扩展到检索、记忆、工具、agent workflow 的整体上下文。

## 当前前沿关注点

截至 2026-06-12，优先跟进这些方向：

- 反思式 prompt evolution：GEPA 等方法把完整执行轨迹作为自然语言反馈，用反思和 Pareto/进化搜索改写 prompt。
- 记忆型自进化：MemAPO 等方法把成功策略和失败模式沉淀为可复用记忆，目标是降低每次从零优化的成本。
- 优化器自进化：SePO 等方法开始把 prompt agent 自身的 system prompt 也纳入优化对象。
- 多 agent / 系统级优化：MASPO、AutoPDL 等方向把优化对象从单 prompt 扩展到 agent 配置或多 agent prompt。
- 模块化 prompt 优化：把 prompt 拆成可局部编辑和约束保护的结构，降低漂移和无边界增长风险。
- context engineering：行业和论文都在把问题从“写好 prompt”推进到“控制模型在每一步看到什么上下文”。
- 已确认的覆盖缺口：bi-level / thought-driven（o1/R1 类推理模型时代的 prompt 优化）整块缺席，是最高优先的定向搜索方向；task-agnostic/online 与 constrained optimization 也仅被间接触及。判据与清单见 [taxonomy 外部完整性校验](arxiv_taxonomy_completeness_check_20260610.md)。

## 深读笔记全目录（39 篇）

证据等级均为论文级（方法 + 结果深读，非本项目复现结论）；逐篇含本地 PDF/文本 SHA256、主结果数字、消融、失败案例与最小验证计划。批次归属与综合判断见 [Batch 3 综合](arxiv_deep_reading_batch3_synthesis.md)；其中 2025/2026 年 25 篇的时间切片综合（四个转向 + 两个张力 + 缺口清点）见 [arXiv 2025/2026 前沿深读综合](arxiv_2025_2026_frontier_synthesis_20260612.md)。

| 年份 | 论文 | 一句话定位 | 深读笔记 |
| --- | --- | --- | --- |
| 2022 | [GrIPS](https://arxiv.org/abs/2203.07281) | 前史锚点（v1 早于 APE）：免梯度短语级编辑搜索，无 LLM 生成器；语义不连贯编辑照样涨分。 | [paper-grips-2022](paper_notes/paper-grips-2022.md) |
| 2022 | [APE](https://arxiv.org/abs/2211.01910) | 两阶段黑盒搜索（propose + select）的起点，确立「instruction 即可搜索程序」；LLM-as-generator 谱系自此开始。 | [paper-ape-2022](paper_notes/paper-ape-2022.md) |
| 2023 | [ProTeGi](https://arxiv.org/abs/2305.03495) | 把失败样本压缩成自然语言批评，beam search + 数据选择；textual critique 经典基线。 | [paper-protegi-2023](paper_notes/paper-protegi-2023.md) |
| 2023 | [OPRO](https://arxiv.org/abs/2309.03409) | LLM-as-optimizer：用「历史候选 + 分数」轨迹驱动生成全新指令。 | [paper-opro-2023](paper_notes/paper-opro-2023.md) |
| 2023 | [PromptBreeder](https://arxiv.org/abs/2309.16797) | task-prompt 与 mutation-prompt 同时进化，自指优化的经典起点。 | [paper-promptbreeder-2023](paper_notes/paper-promptbreeder-2023.md) |
| 2023 | [DSPy](https://arxiv.org/abs/2310.03714) | 把 LM pipeline 写成声明式程序再编译，prompt 工程转向可编译 AI program。 | [paper-dspy-2023](paper_notes/paper-dspy-2023.md) |
| 2023 | [PromptAgent](https://arxiv.org/abs/2310.16427) | 把 prompt 优化建模为 MDP + MCTS 规划；同等探索量下树搜索胜 beam/greedy，补上「搜索结构」演进维度。 | [paper-promptagent-2023](paper_notes/paper-promptagent-2023.md) |
| 2024 | [EvoPrompt](https://arxiv.org/abs/2309.08532) | 把 GA/DE 经典进化算法翻译成 LLM 可执行的自然语言算子。 | [paper-evoprompt-2024](paper_notes/paper-evoprompt-2024.md) |
| 2024 | [TextGrad](https://arxiv.org/abs/2406.07496) | 把文本反馈抽象成可经计算图反向传播的「textual gradient」，泛化到任意文本变量。 | [paper-textgrad-2024](paper_notes/paper-textgrad-2024.md) |
| 2024 | [MIPROv2](https://arxiv.org/abs/2406.11695) | 多阶段 LM program 的 instruction + demonstration 联合优化与 credit assignment。 | [paper-miprov2-2024](paper_notes/paper-miprov2-2024.md) |
| 2024 | [CriSPO](https://arxiv.org/abs/2410.02748) | 生成任务的多维 critique-suggestion 反馈，替代单一总分。 | [paper-crispo-2024](paper_notes/paper-crispo-2024.md) |
| 2024 | [ERM](https://arxiv.org/abs/2411.07446) | 历史 feedback 与错误样例经过滤、检索、选择性遗忘后再用于反思。 | [paper-erm-memory-2024](paper_notes/paper-erm-memory-2024.md) |
| 2024 | [Are LLMs Good Prompt Optimizers?](https://arxiv.org/abs/2402.02101) | 反例：LLM 反思未必能识别 target model 的真实错因。 | [paper-llm-prompt-optimizers-2024](paper_notes/paper-llm-prompt-optimizers-2024.md) |
| 2024 | [Teach Better or Show Smarter?](https://arxiv.org/abs/2406.15708) | 有 labeled dev set 时，exemplar 选择经常比 instruction 改写更重要。 | [paper-teach-better-show-smarter-2024](paper_notes/paper-teach-better-show-smarter-2024.md) |
| 2025 | [APO Survey](https://arxiv.org/abs/2502.16923) | 按优化流程 anatomy（5 阶段）组织的系统综述；本项目 taxonomy 的外部参照系。 | [paper-apo-survey-2025](paper_notes/paper-apo-survey-2025.md) |
| 2025 | [APE Survey](https://arxiv.org/abs/2502.11560) | 优化视角统一框架（变量 × 目标 × 方法），点名 underexplored frontier。 | [paper-ape-survey-2025](paper_notes/paper-ape-survey-2025.md) |
| 2025 | [Context Engineering Survey](https://arxiv.org/abs/2507.13334) | 把 context engineering 定位为 prompt engineering 的超集；确认本项目范围边界。 | [paper-context-engineering-2025](paper_notes/paper-context-engineering-2025.md) |
| 2025 | [Scaling Textual Gradients](https://arxiv.org/abs/2506.00400) | full-batch 文本梯度撞 context wall；TSGD-M 用历史高分 prompt 做动量采样。 | [paper-scaling-textual-gradients-2025](paper_notes/paper-scaling-textual-gradients-2025.md) |
| 2025 | [Textual Gradients are a Flawed Metaphor](https://arxiv.org/abs/2512.13598) | 给 textual gradient 叙事降温：提升常来自格式、meta-instruction 与候选发现，而非梯度式学习。 | [paper-textual-gradients-flawed-metaphor-2025](paper_notes/paper-textual-gradients-flawed-metaphor-2025.md) |
| 2025 | [APO for KG Construction](https://arxiv.org/abs/2506.19773) | APO 是「复杂度放大器下的稳健性工具」：schema 越复杂、输入越长，收益越明显。 | [paper-apo-kg-construction-2025](paper_notes/paper-apo-kg-construction-2025.md) |
| 2025 | [AutoPDL](https://arxiv.org/abs/2504.04365) | 把 Zero-Shot/CoT/ReAct/ReWOO 等 prompting pattern 本身当作搜索变量。 | [paper-autopdl-2025](paper_notes/paper-autopdl-2025.md) |
| 2025 | [DistillPrompt](https://arxiv.org/abs/2508.18992) | 先从样例蒸馏任务原则再压缩成 instruction，作 direct few-shot 的对照。 | [paper-distillprompt-2025](paper_notes/paper-distillprompt-2025.md) |
| 2025 | [MAPRO](https://arxiv.org/abs/2510.07475) | 多 agent prompt 优化形式化为 MAP 推断，credit 沿拓扑传播。 | [paper-mapro-2025](paper_notes/paper-mapro-2025.md) |
| 2025 | [Prompt Repetition](https://arxiv.org/abs/2512.14982) | 对照基线（非 APO 方法）：prompt 原样重复一遍，非推理模式 47/70 显著胜 0 负；零成本结构变换的对照底线。 | [paper-prompt-repetition-2025](paper_notes/paper-prompt-repetition-2025.md) |
| 2026 | [GEPA](https://arxiv.org/abs/2507.19457) | 执行轨迹反思 + Pareto 候选保留，少量 rollouts 超过 RL；当前最值得复现的强 baseline。 | [paper-gepa-2026](paper_notes/paper-gepa-2026.md) |
| 2026 | [SePO](https://arxiv.org/abs/2606.04465) | 把 optimizer 自己的 system prompt 也纳入演化；「optimizer/judge 版本化」的直接证据。 | [paper-sepo-2026](paper_notes/paper-sepo-2026.md) |
| 2026 | [SPEAR](https://arxiv.org/abs/2605.26275) | optimizer 自己写 Python 做结构化错误分析（confusion matrix/groupby），auto-rollback 护住下限。 | [paper-spear-2026](paper_notes/paper-spear-2026.md) |
| 2026 | [Modular Prompt Optimization](https://arxiv.org/abs/2601.04055) | 固定 schema 分 section 做局部 textual gradient；最直接的可回滚优化实验方案。 | [paper-modular-prompt-optimization-2026](paper_notes/paper-modular-prompt-optimization-2026.md) |
| 2026 | [PrefPO](https://arxiv.org/abs/2603.19311) | pairwise preference 替代绝对分数；把 prompt hygiene 与 prompt hacking 纳入评估。 | [paper-prefpo-2026](paper_notes/paper-prefpo-2026.md) |
| 2026 | [TextReg](https://arxiv.org/abs/2605.21318) | prompt overfitting 的正则化视角：task gradient 之外还要 regularization gradient。 | [paper-textreg-2026](paper_notes/paper-textreg-2026.md) |
| 2026 | [Edit-Level Causal Analysis](https://arxiv.org/abs/2605.26655) | edit family 因果分析：复杂化与 meta-instruction 在数学/多跳类任务可能有害。 | [paper-causal-edit-level-2026](paper_notes/paper-causal-edit-level-2026.md) |
| 2026 | [JTPRO](https://arxiv.org/abs/2604.19821) | 工具 agent 的优化对象 = 全局策略 + per-tool schema + 共享 slot 语义的联合 context。 | [paper-jtpro-2026](paper_notes/paper-jtpro-2026.md) |
| 2026 | [MASPO](https://arxiv.org/abs/2605.06623) | 显式建模多 agent「局部对、全局错」，用 misalignment cases 驱动联合优化。 | [paper-maspo-2026](paper_notes/paper-maspo-2026.md) |
| 2026 | [MemAPO](https://arxiv.org/abs/2603.21520) | 成功模板与错误模式双记忆、跨任务检索复用；memory 升级为优化器的经验资产。 | [paper-memapo-2026](paper_notes/paper-memapo-2026.md) |
| 2026 | [Prompt Codebooks](https://arxiv.org/abs/2605.28360) | prompt 拆成可复用 instinct codebook，按输入路由组合；降长度、利归因。 | [paper-prompt-codebooks-2026](paper_notes/paper-prompt-codebooks-2026.md) |
| 2026 | [Temporal/Structural Credit in MAS](https://arxiv.org/abs/2605.30227) | 多 agent「该改谁、改哪一轮」：只更新低 credit 的 role 或 round。 | [paper-temporal-structural-credit-mas-2026](paper_notes/paper-temporal-structural-credit-mas-2026.md) |
| 2026 | [VISTA / Reflection in the Dark](https://arxiv.org/abs/2603.18388) | 反例：根因不在 hypothesis space 时反思越多越坏；假设生成与改写要解耦。 | [paper-vista-reflection-dark-2026](paper_notes/paper-vista-reflection-dark-2026.md) |
| 2026 | [Prompt Optimization Is a Coin Flip](https://arxiv.org/abs/2604.14585) | 优化前先做 headroom / noise floor / coupling 诊断；很多 compound AI 设置下优化不如 zero-shot。 | [paper-coin-flip-2026](paper_notes/paper-coin-flip-2026.md) |
| 2026 | [PROSE](https://arxiv.org/abs/2604.14585) | 内部基线（非独立文献）：coin-flip 作者自建的 risk-aware 进化 optimizer，结论为无可测稳健性优势。 | [paper-prose-2026](paper_notes/paper-prose-2026.md) |

## 已登记、尚未深读的重点候选

与主报告 v4 的 repo↔paper 对照表同口径；完整候选池见 [来源清单](source_inventory.md)。

| 论文/项目 | 登记状态 | 备注 |
| --- | --- | --- |
| [PromptWizard](https://arxiv.org/abs/2405.18369) | skimmed（仓库侧） | microsoft/PromptWizard 待审计，先补论文笔记再审码。 |
| [Promptomatix](https://arxiv.org/abs/2507.14241) | skimmed | 低门槛自动优化框架；先深读论文再审仓库。 |
| [Intent-based Prompt Calibration](https://arxiv.org/abs/2402.03099) | candidate | Eladlev/AutoPrompt 对应论文；注意与 LangChain Promptim 区分命名。 |
| [promptolution](https://aclanthology.org/2026.eacl-demo.21/) | candidate | 统一、模块化、框架无关的 prompt optimization 工具（EACL demo）。 |

## 读论文时重点抽取

- 优化对象：instruction、examples、system prompt、workflow、context、tool policy 中哪些被改。
- 搜索算法：候选如何生成、如何选择、是否用 archive、是否用 validation split。
- 反馈来源：分数、人工标签、LLM critique、执行轨迹、工具错误、成本。
- 防过拟合：train/dev/test 怎么分，是否报告跨任务或跨模型泛化。
- 工程成本：调用次数、token、延迟、是否需要强模型当 optimizer。
- 安全治理：是否限制 optimizer 可修改范围，是否保留回滚和人工审核。
- 失败案例：在哪些任务无效，为什么。

## 优先阅读顺序

1. Survey：`2502.16923` 和 `2502.11560`，先建立全局分类。
2. 经典方法：APE、ProTeGi、OPRO、PromptBreeder。
3. 工程框架：DSPy、MIPROv2、promptolution、Promptomatix。
4. 自进化重点：GEPA、MemAPO、SePO。
5. 扩展视角：context engineering survey。

## 开放问题

- 反思式 prompt evolution 的收益来自更好的搜索，还是来自 optimizer 模型的隐含任务知识。
- 成功策略库是否真的能跨任务泛化，还是只是在相近 benchmark 上迁移。
- 如何给 prompt 自进化设置“不可修改宪法”，同时允许局部策略灵活变化。
- LLM-as-judge 评分噪声会不会引导 optimizer 学到迎合 judge 的 prompt。
- 长期运行时，prompt 版本如何和生产数据分布、模型版本、工具版本一起追踪。
