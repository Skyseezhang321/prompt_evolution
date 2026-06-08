# 文献地图

更新时间：2026-06-08

状态：初始种子清单，尚未完成系统性搜集。新增来源应先按 [资料搜集计划](source_collection_plan.md) 登记和分类，再决定是否进入深读笔记。

筛选标准：优先收录直接讨论 automatic prompt optimization、prompt evolution、self-improving/self-evolving prompts、prompt-as-program、context engineering、eval-driven prompt iteration 的论文或框架。

## 快速脉络

1. 早期自动 prompt 生成：把 instruction 当成可搜索的程序。
2. 文本梯度与黑盒搜索：用错误反馈生成自然语言 critique，再编辑 prompt。
3. 进化与自指优化：同时优化 task prompt 和 mutation/optimizer prompt。
4. 程序化 prompt 系统：DSPy 把 LM pipeline 抽象成可编译程序，通过指标优化 prompt 和示例。
5. 反思式进化：GEPA 等方法利用执行轨迹做自然语言诊断和 Pareto 搜索。
6. 记忆与自进化：MemAPO、SePO 把成功经验、失败模式、优化器自身 prompt 纳入长期改进。
7. 上下文工程：研究对象从 prompt 字符串扩展到检索、记忆、工具、agent workflow 的整体上下文。

## 当前前沿关注点

截至 2026-06-08，初步核验后优先跟进这些方向：

- 反思式 prompt evolution：GEPA 等方法把完整执行轨迹作为自然语言反馈，用反思和 Pareto/进化搜索改写 prompt。
- 记忆型自进化：MemAPO 等方法把成功策略和失败模式沉淀为可复用记忆，目标是降低每次从零优化的成本。
- 优化器自进化：SePO 等方法开始把 prompt agent 自身的 system prompt 也纳入优化对象。
- 多 agent / 系统级优化：MASPO、AutoPDL 等方向把优化对象从单 prompt 扩展到 agent 配置或多 agent prompt。
- 模块化 prompt 优化：把 prompt 拆成可局部编辑和约束保护的结构，降低漂移和无边界增长风险。
- context engineering：行业和论文都在把问题从“写好 prompt”推进到“控制模型在每一步看到什么上下文”。

## 核心论文

| 时间 | 论文/项目 | 主要贡献 | 对本研究的价值 |
| --- | --- | --- | --- |
| 2022 | [Large Language Models are Human-Level Prompt Engineers / APE](https://arxiv.org/abs/2211.01910) | 用 LLM 生成 instruction 候选，并用任务分数选择。 | 自动 instruction search 的起点。 |
| 2023 | [Automatic Prompt Optimization with Gradient Descent and Beam Search / ProTeGi](https://arxiv.org/abs/2305.03495) | 用自然语言“梯度”批评当前 prompt，再做语义反向编辑和 beam search。 | 失败反馈如何转成 prompt 编辑方向。 |
| 2023 | [Optimization by PROmpting / OPRO](https://arxiv.org/abs/2309.03409) | 用 LLM 作为优化器，基于历史候选和分数生成更优解。 | LLM-as-optimizer 的通用范式。 |
| 2023 | [PromptBreeder](https://arxiv.org/abs/2309.16797) | 同时进化 task-prompts 和 mutation-prompts，形成自指改进机制。 | 自进化 prompt 的经典起点。 |
| 2023/2024 | [DSPy](https://arxiv.org/abs/2310.03714) | 把 LM 调用写成声明式模块，通过 compile 自动优化 prompt / demonstrations。 | prompt 工程转向可编译 AI program。 |
| 2024 | [TextGrad](https://arxiv.org/abs/2406.07496) | 将文本反馈类比为自动微分中的梯度，优化 prompt、代码等文本对象。 | “textual gradient” 的通用化。 |
| 2024 | [MIPROv2](https://arxiv.org/abs/2406.11695) | 联合优化 instructions 和 few-shot examples，常见于 DSPy pipeline。 | 实验 baseline 候选。 |
| 2025 | [A Systematic Survey of Automatic Prompt Optimization Techniques](https://arxiv.org/abs/2502.16923) | 系统综述 APO 方法。 | 建立分类法和 baseline 清单。 |
| 2025 | [A Survey of Automatic Prompt Engineering: An Optimization Perspective](https://arxiv.org/abs/2502.11560) | 从优化视角统一理解自动 prompt engineering。 | 理论框架参考。 |
| 2025/2026 | [GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning](https://arxiv.org/abs/2507.19457) | 使用轨迹反思、Pareto 选择和 prompt 变异优化复合 AI 系统。 | 当前最值得复现的强 baseline。 |
| 2025 | [Promptomatix](https://arxiv.org/abs/2507.14241) | 从任务描述生成高质量 prompt，包含 meta-prompt optimizer 和 DSPy compiler。 | 低门槛自动优化框架设计参考。 |
| 2025 | [A Survey of Context Engineering for LLMs](https://arxiv.org/abs/2507.13334) | 把上下文检索、生成、处理、管理纳入统一 taxonomy。 | 提醒本项目不要只优化 prompt 字符串。 |
| 2026 | [MemAPO](https://arxiv.org/abs/2603.21520) | 用双记忆机制积累成功策略和失败模式，实现跨任务自进化 APO。 | 本项目“长期记忆 + 经验复用”的核心参考。 |
| 2026 | [Modular Prompt Optimization](https://arxiv.org/abs/2601.04055) | 用 section-local textual gradients 优化结构化 prompt，避免把 prompt 当成单块文本。 | 适合转化为“可变层/不可变层”的工程方案。 |
| 2026 | [promptolution](https://aclanthology.org/2026.eacl-demo.21/) | 统一、模块化、框架无关的 prompt optimization 工具。 | 工具架构与可复现 benchmark 参考。 |
| 2026 | [MASPO](https://arxiv.org/abs/2605.06623) | 面向 LLM 多 agent 系统的联合 prompt 优化。 | 系统级和 agent workflow 优化参考。 |
| 2026 | [SePO](https://arxiv.org/abs/2606.04465) | 同时优化 task agent 和 prompt agent 自身的 system prompt。 | 截至 2026-06-08 检索到的最新直接相关自进化论文。 |

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
