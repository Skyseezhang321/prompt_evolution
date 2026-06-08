# Prompt 优化与自进化研究框架

更新时间：2026-06-08

当前阶段：五天交付版 M0 资料搜集、前沿状态总结与方案候选。本文中的研究假设是资料整理的导航线索，不是已经成立的结论；最终报告必须区分证据支持、初步观察和待验证推测。

## 研究问题

Prompt 优化可以被看作一个离散、黑盒、带噪声的程序搜索问题：给定任务、模型、上下文、示例和评价函数，寻找能稳定提升目标指标的指令组合。自进化进一步要求系统从历史成功和失败中积累经验，未来面对新任务或新输入时能自动复用这些经验。

本研究关注三个层次：

- 单 prompt 优化：自动改写 instruction、few-shot examples、输出格式约束。
- 多组件系统优化：同时优化 system prompt、retrieval context、tool policy、agent handoff、judge rubric。
- 自进化闭环：从执行轨迹和失败模式中沉淀可复用策略，让优化器自身也能被改进。

五天交付版额外关注一个工程问题：如何把当前前沿方法转化为短期可执行、可评估、可回滚的方案或建议。

## 关键定义

- Prompt optimization：在固定模型权重下，搜索或生成更优 prompt，使任务指标提升。
- Automatic Prompt Optimization/APO：用 LLM、搜索算法、梯度式文本反馈、贝叶斯优化、进化算法等自动优化 prompt。
- Self-evolving prompt：系统从历史执行结果、反思、记忆或候选 archive 中持续更新 prompt 或 prompt 生成策略。
- Context engineering：把 prompt 扩展为整个上下文窗口的信息工程，包括检索、压缩、示例选择、记忆、工具返回和格式治理。

## 技术分类

| 维度 | 典型方法 | 研究重点 |
| --- | --- | --- |
| 候选生成 | LLM 生成、规则变异、文本梯度、反思改写、示例重采样 | 候选质量、搜索空间、可解释性 |
| 候选选择 | beam search、bandit、Bayesian optimization、Pareto frontier、validation split | 样本效率、过拟合控制 |
| 反馈信号 | exact match、rubric judge、人工偏好、轨迹诊断、工具错误、成本延迟 | 反馈噪声、judge 校准 |
| 优化对象 | instruction、few-shot、system prompt、context、tool policy、agent workflow | 单点改写还是系统级协同 |
| 记忆机制 | 成功策略库、失败模式库、候选 archive、经验检索 | 跨任务泛化、防止污染 |
| 治理机制 | prompt versioning、eval gate、rollback、approval、monitoring | 生产安全、审计、漂移检测 |

## 研究假设

H1：基于执行轨迹的自然语言反思，比只看最终分数的优化更省样本，尤其适合 agent、RAG、tool-use 等多步骤系统。

H2：Prompt 自进化真正有效时，优化对象通常不是单个字符串，而是「prompt + examples + context + tools + evaluator」的组合。

H3：自进化系统需要显式区分可变层和不可变层。业务目标、权限边界、安全策略、合规要求应作为不可自动修改的约束；风格、示例、检索提示、局部策略可以被优化。

H4：成功策略和失败模式的记忆，比每个任务从零开始搜索更有可能降低成本并提升跨任务泛化。

H5：没有强 eval、版本和回滚机制的 prompt 自进化，会快速变成不可审计的行为漂移。

## 研究路线

1. 资料搜集：广泛收集论文、工程框架、官方文档、行业实践和失败案例。
2. 前沿状态总结：从 APE、ProTeGi、OPRO、PromptBreeder、DSPy、TextGrad，到 GEPA、MemAPO、SePO、MASPO 等方向，形成方法地图和证据等级。
3. 工程抽象：把 prompt 当作可版本化的代码资产，把 eval 当作优化目标和发布门禁。
4. 方案化：把资料结论转化为 2-3 个可执行方案或建议，说明适用场景、成本、风险和回滚点。
5. 初步实验：选择 1-2 个关键判断做最小验证，避免为了完整性实现过大的 benchmark harness。
6. 最终报告：整合前沿状态、行业经验、方案建议、初步实验和后续路线。
7. 后续扩展：继续做系统级 RAG/tool-use 实验、记忆型自进化和跨任务迁移验证。

## 风险与控制

- 过拟合 eval：必须保留 validation split 和 hidden test set。
- Judge 偏差：LLM-as-judge 需要人工样本校准，关键指标尽量混合规则评分。
- 成本失控：记录每轮 token、调用次数、候选数量和边际收益。
- Prompt 漂移：每次自动修改都要形成 diff、理由、评测结果和回滚点。
- 安全退化：安全规则和权限边界不纳入自动改写搜索空间。
- 跨模型脆弱性：同一 prompt 至少在目标模型和一个替代模型上做稳健性测试。

## 预期产出

- 一份持续更新的文献地图。
- 一份可追溯的来源清单、方法 taxonomy 和资料缺口清单。
- 一份当前前沿状态总结，覆盖代表论文、工具实践和主要争议。
- 2-3 个可执行方案或建议，包含适用场景、指标、成本、风险和回滚策略。
- 1-2 个初步实验或可复现实验设计，包含失败案例和结论限制。
- 一份最终说明和报告，包含后续可扩展为 benchmark harness 的路线。
