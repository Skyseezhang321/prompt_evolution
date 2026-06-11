# Insight / Conclusion / Helpful Method 字段定义规范

更新时间：2026-06-10

## 这份规范是什么

本文是 `insight`、`conclusion`、`helpful method`、`anti-pattern` 四类核心产出的**唯一字段权威**。目的是消除一个长期存在的问题：这四个概念在 `docs/research_brief.md`、`docs/project_principles.md`、两个深读模板和 `docs/insight_method_catalog_20260609.md` 里反复出现，但此前**只有字段名、没有统一的「定义 + 区分口径 + 必填项」**，导致同一个判断在不同文档里可能被归成不同类型、字段命名也略有出入。

统辖范围（这些文档的字段定义都以本文为准）：

- `docs/paper_notes/template.md`、`docs/industry_notes/template.md` 的「对本项目的启发」段。
- `docs/insight_method_catalog_20260609.md` 的 YAML 字段。
- `docs/final_report_outline.md` 的「Insight 字段」「可执行方案字段」。

与上游文档的关系：本文**承接** `docs/research_brief.md` 第 25-27 行对三类产出的一句话定义，不另起炉灶；在其基础上补齐区分口径、`conclusion` 缺失的字段 schema，并统一字段命名。证据等级沿用 `docs/final_report_outline.md` 的 A/B/C/D，不在本文重复定义。

## 一、四类核心产出的定义与区分

| 类型 | 一句话定义 | 回答的问题 | 判别问句（命中即归此类） |
| --- | --- | --- | --- |
| `insight` 洞见 | 具体、可迁移、可验证的认知：某现象**为什么**发生、机制是什么 | 「发生了什么 / 为什么」 | 它解释了一个机制或反直觉现象吗？换个任务/模型还可能成立吗？ |
| `conclusion` 结论 | 带证据等级、反例和边界的**判断**，可被直接采纳或反驳 | 「所以现在能确定什么」 | 它是一句能被证据支撑或推翻的断言吗？标得出证据等级和适用边界吗？ |
| `helpful method` 方法 | 可直接复用的操作步骤 / playbook，挂靠在某个 insight 下 | 「我具体该怎么做」 | 读者能照着步骤执行吗？有适用场景、指标、回滚吗？ |
| `anti-pattern` 反模式 | 已知会导致错误结论或退化的做法及其触发条件 | 「不要怎么做、为什么」 | 它描述的是一个**应避免**的具体做法及其后果吗？ |

### 容易混的边界（区分口径）

- **insight vs conclusion**：insight 是机制层的「为什么」，允许来自单一来源、可作为待验证认知；conclusion 是判断层的「已确定什么」，**必须**带证据等级和适用边界，**不能**由单篇论文或单次样例直接升格为结论（见 `docs/project_principles.md` 第 4 条）。同一份材料常先沉淀为 insight，积累跨源证据后才升格为 conclusion。
- **insight vs helpful method**：insight 是认知，helpful method 是可照抄的操作。一个 insight 可以暂时不配方法；但**每个 helpful method 必须通过 `insight_supported` 指回它所服务的 insight**，不允许「无洞见支撑的纯操作步骤」。
- **conclusion vs helpful method**：conclusion 是「这件事成立/不成立」，helpful method 是「据此你应该怎么做」。一条 conclusion 可以不产出方法（例如只是划定边界），一个方法则应能追溯到支撑它的 conclusion 或 insight。
- **anti-pattern 的归属**：反模式既可独立成条，也可作为某个 insight/method 的 `counterexample_or_limit` / `misuse_or_anti_pattern` 字段出现；独立成条的标准是它本身具有跨场景的警示价值。

## 二、各类型的字段（必填 / 可选）

字段名以下表为准。标 **必填** 的字段缺失时，该条不得进入最终报告或项目结论。

### Insight

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `insight` | 必填 | 一句话洞见 |
| `user_facing_one_liner` | 必填 | 给非研究者读者的通俗版 |
| `phenomenon` | 必填 | 观察到的现象 |
| `mechanism` | 必填 | 现象背后的机制 |
| `actionable_rule` | 必填 | 可迁移的规则 |
| `evidence_strength` | 必填 | A/B/C/D |
| `main_sources` | 必填 | 支撑来源文件路径，保证可追溯 |
| `counterexample_or_limit` | 必填 | 反例或不成立的情形 |
| `helpful_method` | 可选 | 指向配套方法名（若有） |
| `exact_action_to_try` | 可选 | 读者可立即尝试的最小动作 |
| `before_after_example` | 可选 | 报告展示用的对照例子 |
| `validation_or_demo` | 可选 | 拟用的验证 / 演示方式 |

### Conclusion

此前三处文档均无独立 `conclusion` schema，本规范补齐如下最小集合：

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `conclusion` | 必填 | 一句可被采纳或反驳的判断 |
| `scope` | 必填 | 适用边界：任务类型、模型、样本量等成立条件 |
| `evidence_strength` | 必填 | A/B/C/D |
| `main_sources` | 必填 | 支撑来源 |
| `counterexample_or_limit` | 必填 | 反例、失败案例或不成立的情形 |
| `supersedes_or_conflicts` | 可选 | 与哪条已有判断替代或冲突 |

### Helpful method

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `name` | 必填 | 方法名 |
| `insight_supported` | 必填 | 指回所服务的 insight |
| `problem` | 必填 | 解决什么问题 |
| `recommended_when` | 必填 | 适用场景 |
| `not_recommended_when` | 必填 | 不适用场景（与 `recommended_when` 成对，构成区分口径） |
| `required_inputs` | 必填 | 所需数据 / 前置条件 |
| `implementation_steps` | 必填 | 可照抄的步骤 |
| `evaluation_metrics` | 必填 | 评估指标 |
| `risks` | 必填 | 风险 |
| `misuse_or_anti_pattern` | 必填 | 误用方式 / 对应反模式 |
| `rollback_plan` | 必填 | 回滚策略 |
| `evidence` | 必填 | 证据（来源 / 实验 / 等级） |
| `cost_and_latency` | 可选 | 成本与延迟 |
| `expected_benefit` | 可选 | 预期收益 |
| `next_experiment` | 可选 | 后续验证实验 |

### Anti-pattern

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `anti_pattern` | 必填 | 应避免的具体做法 |
| `why_harmful` | 必填 | 为什么会导致错误结论或退化 |
| `trigger_condition` | 必填 | 在什么条件下会发生 |
| `instead_do` | 必填 | 替代做法（通常指向某个 helpful method） |
| `evidence_or_source` | 可选 | 来源或观察到的案例 |

## 三、字段命名映射（消除现有不一致）

下表对齐三套已有 schema，统一以本规范命名为准；命名不一致或缺失的，应在后续修订中向本规范收敛：

| 本规范统一字段 | paper/industry 模板 | insight_method_catalog | final_report_outline |
| --- | --- | --- | --- |
| `insight` | `insight` | `insight` | `insight` |
| `conclusion` | `conclusion` | （无独立字段，被拆为 `user_facing_one_liner` + `exact_action_to_try`） | （无独立字段） |
| `helpful_method` | `helpful method` | `helpful_method` | 见「可执行方案字段」 |
| `anti_pattern` | `anti-pattern / limit` | `counterexample_or_limit` | `misuse_or_anti_pattern` |
| `validation_or_demo` | 最小验证 / 演示 | `next_validation` | `validation_or_demo` |
| `evidence_strength` | （隐含于证据等级） | `evidence_strength` | `evidence_strength` |

> 已知待收敛点：`insight_method_catalog_20260609.md` 文首「使用方式」列出的精简 schema 缺 `phenomenon` / `mechanism` / `actionable_rule`（正文各条其实已包含），且用 `next_validation` 而非 `validation_or_demo`；其标题含「Conclusion」但无独立 `conclusion` 字段。后续修订该文件时按本规范补齐。

## 四、证据等级

沿用 `docs/final_report_outline.md` 第 39-42 行定义，不在本文重复：A（原始论文/官方文档/开源文档 + 已做结构化笔记）、B（多源重复出现的工程实践）、C（本项目初步实验观察）、D（资料综合推测，须标注待验证）。每条 conclusion、insight、helpful method 的关键判断都必须标注证据等级，且不得把 D 级推测写成确定结论。

## 五、最小合格示例

```yaml
# insight
insight: prompt 优化不是默认有收益，很多任务优化后可能低于 zero-shot。
user_facing_one_liner: 先看有没有提升空间，再花钱自动优化。
phenomenon: 小样本 dev 选择中，候选差异可能不超过噪声。
mechanism: zero-shot 已接近能力上限时，prompt 搜索主要放大评估噪声。
actionable_rule: APO 前先估计 headroom 与 noise floor。
evidence_strength: A
main_sources: [docs/paper_notes/paper-coin-flip-2026.md]
counterexample_or_limit: 需多轮搜索才能发现组合结构的任务可能被低估。

# conclusion
conclusion: 在小样本、自由文本任务上，自动 prompt 优化的期望收益不显著高于 zero-shot。
scope: 小样本 dev（约 20-30 条）、自由生成任务；不含严格 JSON/rubric 输出任务。
evidence_strength: A
main_sources: [docs/paper_notes/paper-coin-flip-2026.md]
counterexample_or_limit: HelpSteer2 等严格 rubric 任务上六种方法均超过 zero-shot。

# helpful_method
name: pre-optimization gate
insight_supported: 「先确认有没有提升空间，再花钱跑优化器」
problem: 避免在没有可优化空间的任务上浪费优化器调用并引入过拟合。
recommended_when: 任务有可客观打分的留出集，且怀疑 headroom 有限。
not_recommended_when: 收益依赖多轮搜索发现组合结构的任务。
required_inputs: 20 条留出样本、10-20 个候选 prompt、zero-shot baseline。
implementation_steps: 跑 baseline → 生成候选 → 同批样本打分 → 比较 headroom 与 noise floor → 低于阈值则停。
evaluation_metrics: best gain over zero-shot、候选间分数方差。
risks: 阈值跨任务硬套会误判。
misuse_or_anti_pattern: 用训练集而非留出集估 headroom。
rollback_plan: gate 判定不可靠时回退到固定预算的常规优化流程。
evidence: docs/paper_notes/paper-coin-flip-2026.md（A）。
```
