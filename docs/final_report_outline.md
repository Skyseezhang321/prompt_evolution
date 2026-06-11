# 最终报告结构

更新时间：2026-06-09

## 报告目标

最终报告要回答三个问题：

1. 截至 2026-06-08，prompt 优化与 prompt 自进化领域的前沿状态是什么。
2. 已有资料中最有价值的 insights、conclusions 和反模式是什么，证据强度和边界分别是什么。
3. 在工程实践中，哪些 helpful methods 或建议值得实际执行，前提、成本、风险和验证方式分别是什么。

报告不追求穷尽所有论文，也不声称初步实验能证明长期稳定收益。报告的价值来自可追溯证据、清晰判断、可复用洞见、可执行方法和诚实的风险边界。实验结果只用于验证、演示或修正洞见与方法，不应喧宾夺主。

## 核心问题

- 当前前沿方法如何分类：自动 instruction 搜索、文本梯度、反思式进化、prompt-as-program、记忆型自进化、agent/context 优化。
- 行业实践正在收敛到什么：eval-driven development、prompt versioning、observability、人工审核、rollback、context engineering。
- 哪些结论已有较强证据，哪些只是初步趋势。
- 哪些洞见具体、可迁移、可验证，值得进入最终报告。
- 哪些 helpful methods 适合作为短期落地方案，哪些更适合作为中长期研究方向。
- 初步实验能验证哪些关键洞见或方法，不能验证哪些判断。

## 建议结构

1. 执行摘要：用一页说明主要 conclusions、最高价值 insights、推荐 helpful methods 和风险。
2. 一眼看懂的具体洞见卡片：先展示普通用户能立刻理解和尝试的发现，例如“非 reasoning 模型可测试 prompt repetition”“先写失败根因假设再改 prompt”“示例选择本身是一等优化变量”。
3. 研究范围与方法：说明来源筛选、证据等级、验证边界和不覆盖内容。
4. Key insights：逐条写清洞见、现象、机制、可迁移规则、反例和证据等级。
5. Helpful methods：给出 2-3 个可复用方法或建议，每个包含适用场景、实施步骤、所需数据、评估指标、成本、误用风险和回滚策略。
6. 前沿状态地图：按方法类别总结学术论文和工程框架，为洞见和方法提供背景。
7. 行业经验总结：总结官方文档、工具实践和生产治理经验，优先提炼可复用规则而不是产品罗列。
8. 初步验证/演示：描述验证目标、要验证的 insight/method、数据、prompt 版本、模型、指标、结果、失败案例和限制。
9. 风险与治理：覆盖 eval 过拟合、judge 偏差、prompt 漂移、安全退化、成本失控和跨模型脆弱性。
10. 后续路线：说明如果继续投入，应优先补哪些来源、洞见、方法、验证和工程能力。

## 证据等级

- A：原始论文、官方文档或开源项目文档，并已完成结构化笔记。
- B：多个独立来源重复出现的行业实践或工程经验，已记录来源和适用条件。
- C：本项目初步实验观察，有运行记录、样例输出和失败案例。
- D：基于资料综合形成的推测，尚未有充分证据，必须标注为待验证。

最终报告中的每个关键判断都必须标注证据等级。不能把 D 级推测写成确定结论。

## 可执行方案字段

> 本节及下方「Insight 字段」的字段定义与各类型必填项以 `docs/insight_field_standard.md` 为准；该文同时给出本仓库尚缺的 `conclusion` 独立字段 schema。

每个 helpful method 或方案至少写清：

```yaml
name:
insight_supported:
problem:
recommended_when:
not_recommended_when:
required_inputs:
implementation_steps:
evaluation_metrics:
expected_benefit:
cost_and_latency:
risks:
misuse_or_anti_pattern:
rollback_plan:
evidence:
next_experiment:
```

## Insight 字段

每条核心洞见至少写清：

```yaml
insight:
user_facing_one_liner:
phenomenon:
mechanism:
actionable_rule:
helpful_method:
exact_action_to_try:
before_after_example:
counterexample_or_limit:
evidence_strength:
validation_or_demo:
```

## 验收标准

最终报告完成时应满足：

- 能说明当前前沿的主要方向和代表方法。
- 能把论文和行业实践转化为 insights、conclusions、helpful methods 和反模式，而不是只做摘要。
- 至少包含 8 条核心 insights 或 conclusions。
- 至少包含 2 个可复用 helpful methods 或建议。
- 至少包含 1 个用于验证/演示关键洞见或方法的初步实验设计。
- 每个关键结论都能追溯到来源、实验或明确标注为待验证。
- 明确列出不确定性、反例和后续验证路径。
