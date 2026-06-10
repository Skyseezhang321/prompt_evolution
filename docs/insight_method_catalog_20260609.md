# Insight / Conclusion / Helpful Method 候选清单

日期：2026-06-09

定位：本文是最终报告前的“内容整理中间层”。它不替代论文笔记、源码审计或行业实践笔记，而是把现有材料按最新 insight-first 原则压缩成可复用的洞见、结论、方法、反模式和验证候选。

证据边界：

- 本文中的 `evidence_strength` 使用 `docs/final_report_outline.md` 的 A/B/C/D 等级。
- A/B 级可作为较强结论或方法候选；C 级来自本项目实验后才能升级；D 级只能写作待验证推测。
- 没有本项目复现实验前，不把任何论文提升比例写成“本项目已证明有效”。

## 使用方式

字段定义与 insight / conclusion / helpful method 的区分口径以 `docs/insight_field_standard.md` 为准；下方精简 schema 缺 `phenomenon` / `mechanism` / `actionable_rule`（正文各条已含），且 `next_validation` 应按规范统一为 `validation_or_demo`。

最终报告应先展示读者能立刻理解的洞见和方法，再展开论文、源码、行业来源证据。每条进入最终报告的判断至少要保留：

```yaml
insight:
user_facing_one_liner:
exact_action_to_try:
helpful_method:
evidence_strength:
counterexample_or_limit:
next_validation:
```

## 核心洞见候选

### I-01：先测是否值得优化，再跑 optimizer

```yaml
insight: prompt optimization 不是默认有收益；很多任务优化后可能低于 zero-shot。
user_facing_one_liner: 先看有没有提升空间，再花钱自动优化。
phenomenon: 小样本 dev 选择和自由文本任务中，候选差异可能不超过噪声，复杂 optimizer 会选到偶然高分 prompt。
mechanism: 当 zero-shot 已接近模型在该任务格式下的能力上限，prompt 搜索主要放大评估噪声。
actionable_rule: 每次 APO 前先跑 zero-shot、人工 baseline 和 10-20 个候选，估计 headroom 与 noise floor。
exact_action_to_try: 用 20 条 held-out 样本测试 10-20 个候选；best gain 小于噪声阈值则停止优化。
helpful_method: pre-optimization gate
evidence_strength: A
main_sources:
  - docs/paper_notes/paper-coin-flip-2026.md
  - docs/arxiv_deep_reading_batch3_synthesis.md
counterexample_or_limit: 需要多轮搜索才能发现组合结构的任务，简单 headroom test 可能低估收益；阈值必须按样本量和评分器重校准。
next_validation: 在一个结构化输出任务和一个自由生成任务上比较 headroom test 对后续优化收益的预测力。
```

### I-02：失败样本要变成可编辑证据，不只是分数

```yaml
insight: 分数告诉你“坏了”，trace 和 critique 才告诉你“该改哪里”。
user_facing_one_liner: 不要只记录 accuracy，要记录失败类型、模型输出和改写理由。
phenomenon: ProTeGi、GEPA、CriSPO、SPEAR、JTPRO 等方法都依赖错误样本、trace、critique 或工具调用诊断生成候选。
mechanism: 自然语言反馈把失败样本压缩成可编辑的 prompt 修改方向，但它不是数学梯度。
actionable_rule: 每个 eval case 至少记录 prediction、gold、error_type、critique、candidate_prompt_id、selector_reason。
exact_action_to_try: 对 20 条失败样本先写失败类型表，再让 optimizer 只基于这张表改 prompt。
helpful_method: trace-first critique loop
evidence_strength: A
main_sources:
  - docs/paper_notes/paper-protegi-2023.md
  - docs/paper_notes/paper-crispo-2024.md
  - docs/paper_notes/paper-textual-gradients-flawed-metaphor-2025.md
  - docs/github_repo_insight_cards_20260608.md
counterexample_or_limit: critique 可能带 judge 偏见，必须绑定样本和指标；不能把 critique 写成真实因果解释。
next_validation: score-only rewrite vs critique-guided rewrite vs trace-guided rewrite。
```

### I-03：先生成根因假设，再改 prompt

```yaml
insight: reflective optimizer 的失败常来自根因假设空间太窄，而不是信息不足。
user_facing_one_liner: 不要直接让模型“改好 prompt”，先列出可能失败原因并逐个验证。
phenomenon: VISTA 中 GEPA 在 defective seed 下没有提出真实根因，表现从 23.81% 降到 13.50%；VISTA 解耦 hypothesis generation 和 rewrite 后恢复到 87.57%。
mechanism: 同一个 reflector 会反复在熟悉解释空间内归因，多假设并行验证能暴露结构性 prompt bug。
actionable_rule: 每个 failure hypothesis 生成一个候选 prompt，用 minibatch 验证，而不是一次性输出最终 prompt。
exact_action_to_try: 对同一批失败样本生成 3 个互斥根因假设：缺规则、缺上下文、格式约束冲突；分别改写并评分。
helpful_method: root-cause hypothesis gate
evidence_strength: A
main_sources:
  - docs/paper_notes/paper-vista-reflection-dark-2026.md
  - docs/paper_notes/paper-llm-prompt-optimizers-2024.md
counterexample_or_limit: 开放写作任务的根因边界模糊，多假设验证成本可能超过收益。
next_validation: one-shot reflection vs K hypotheses + parallel validation。
```

### I-04：候选选择机制和 prompt 改写机制同等重要

```yaml
insight: 不要采用模型给出的第一版优化 prompt；必须保留候选池、选择理由和回滚点。
user_facing_one_liner: 让模型给多个版本，用验证集选，不要让它自评最优。
phenomenon: ProTeGi、GEPA、PromptBreeder、EvoPrompt、SePO、MASPO 都依赖 beam、archive、evolutionary search、Pareto 或 bandit 选择。
mechanism: LLM 候选方差大，搜索和选择结构负责过滤坏改写、防止单次好运和保留 tradeoff。
actionable_rule: 每轮至少保存 seed、candidates、scores、selection_policy、rejected_reason、best_seen、rollback_point。
exact_action_to_try: 生成 5 个候选，按 dev score、format error、prompt length 三个维度选 Pareto 候选。
helpful_method: candidate ledger + Pareto selector
evidence_strength: A
main_sources:
  - docs/paper_notes/paper-protegi-2023.md
  - docs/paper_notes/paper-gepa-2026.md
  - docs/paper_notes/paper-promptbreeder-2023.md
  - docs/paper_notes/paper-maspo-2026.md
  - docs/github_repo_insight_cards_20260608.md
counterexample_or_limit: 搜索预算越大越容易 dev overfitting；必须有 validation/test 分层。
next_validation: one-shot rewrite vs candidate pool + validation selector。
```

### I-05：有 dev set 时，exemplar selection 是一等优化变量

```yaml
insight: 示例选择经常比 instruction rewrite 更能提升或稳定表现。
user_facing_one_liner: 如果你已经有测试样本，就不要只拿它打分，也要试着优化给模型看的例子。
phenomenon: Teach Better or Show Smarter 显示 No IO + optimized exemplars 经常超过 SoTA IO + no/random exemplars；ERM 和 DistillPrompt 也支持样例/反馈复用。
mechanism: exemplar 直接展示决策边界和输出格式，可能比抽象 instruction 更容易被模型执行。
actionable_rule: 每个 APO 实验至少比较 no-example、random-example、optimized-example、instruction+optimized-example。
exact_action_to_try: 固定 instruction，从候选池中搜索 3 个 exemplars，看 held-out 表现是否超过 instruction-only。
helpful_method: exemplar optimization baseline
evidence_strength: A
main_sources:
  - docs/paper_notes/paper-teach-better-show-smarter-2024.md
  - docs/paper_notes/paper-erm-memory-2024.md
  - docs/paper_notes/paper-distillprompt-2025.md
counterexample_or_limit: context 紧张、示例分布偏、样例泄漏时可能伤害泛化。
next_validation: instruction-only vs optimized examples vs combined。
```

### I-06：优化对象已经从 prompt string 扩展为 artifact graph

```yaml
insight: 真实系统里失败可能来自 examples、context、tool schema、agent role、memory 或 evaluator，而不只是一段 system prompt。
user_facing_one_liner: 先标清楚你要改的是哪一个部件，不要把整个上下文窗口都叫 prompt。
phenomenon: AutoPDL 优化 pattern，JTPRO 优化 tool schema，Prompt Codebooks 优化 codebook/routing，多 agent 论文优化 role/round/topology-aware prompt。
mechanism: 不同 artifact 控制不同失败模式；混在一起改会无法归因，也容易绕过安全和格式约束。
actionable_rule: 版本记录至少拆出 task_prompt、examples、context_packaging、tool_schema、agent_role_prompt、evaluator_prompt、selection_policy。
exact_action_to_try: 对一次优化运行生成 artifact manifest，声明 mutable/frozen 字段。
helpful_method: prompt artifact graph
evidence_strength: A/B
main_sources:
  - docs/paper_notes/paper-autopdl-2025.md
  - docs/paper_notes/paper-jtpro-2026.md
  - docs/paper_notes/paper-prompt-codebooks-2026.md
  - docs/industry_practices.md
  - docs/github_repo_insight_cards_20260608.md
counterexample_or_limit: 简单一次性任务不需要完整 artifact graph；但研究和生产场景需要。
next_validation: whole-prompt rewrite vs section-local / artifact-local rewrite。
```

### I-07：prompt 变长、变复杂、加 meta instruction 不一定是进步

```yaml
insight: prompt bloat 可能是过拟合信号，不是能力增强。
user_facing_one_liner: 新 prompt 更长不等于更好；要看它是否只在训练样本上打补丁。
phenomenon: TextReg、PrefPO、Edit-Level Analysis、Flawed Textual Gradients 都显示 prompt hacking、规则膨胀、meta-instruction 和复杂化会制造伪提升。
mechanism: optimizer 可能把局部失败写成全局规则，或利用 label distribution、judge 口味和 dev set 噪声。
actionable_rule: 选择候选时记录 prompt length ratio、repetition ratio、edit family、dev-test gap、OOD/stress delta。
exact_action_to_try: 候选 prompt 若长度增加超过阈值，必须说明新增规则绑定哪些失败样本，并通过 stress split。
helpful_method: prompt hygiene gate
evidence_strength: A
main_sources:
  - docs/paper_notes/paper-textreg-2026.md
  - docs/paper_notes/paper-prefpo-2026.md
  - docs/paper_notes/paper-causal-edit-level-2026.md
  - docs/paper_notes/paper-textual-gradients-flawed-metaphor-2025.md
counterexample_or_limit: 某些复杂任务确实需要更明确约束；判断标准不是短，而是必要、可追溯、不过拟合。
next_validation: performance-only selector vs performance + hygiene selector。
```

### I-08：memory 有用，但只有过滤后的 memory 有用

```yaml
insight: 记住更多历史不等于更聪明；未经筛选的 feedback memory 会污染优化。
user_facing_one_liner: 经验库要有来源、适用范围、质量分和过期策略。
phenomenon: ERM 显示 raw feedback memory 不足，过滤和 selective forgetting 才带来增益；MemAPO 区分成功模板和错误模式。
mechanism: memory 可以降低重复踩坑和候选生成成本，但错误经验会跨任务负迁移。
actionable_rule: memory schema 必须包含 success_template、error_pattern、source_task、applicability_condition、retrieval_reason、quality_score、forget_reason。
exact_action_to_try: 不要直接塞历史对话；只检索经过验证、与当前任务匹配的 3-5 条 memory。
helpful_method: filtered dual memory
evidence_strength: A/B
main_sources:
  - docs/paper_notes/paper-erm-memory-2024.md
  - docs/paper_notes/paper-memapo-2026.md
  - docs/paper_notes/paper-prompt-codebooks-2026.md
  - docs/github_repo_insight_cards_20260608.md
counterexample_or_limit: 高度非平稳任务和安全敏感任务中，历史经验可能快速过期或泄漏隐私。
next_validation: no-memory vs raw-memory vs filtered-memory vs filtered+forgetting。
```

### I-09：多 agent 优化的核心是 credit assignment，不是更多 agent

```yaml
insight: 一个 agent 局部正确也可能让全局失败；需要记录 role、round 和 downstream impact。
user_facing_one_liner: 多 agent 系统先找责任环节，再局部改，不要整个系统一起重写。
phenomenon: MASPO、MAPRO、Temporal/Structural Credit 都围绕局部-全局错配、topology-aware reward 和低 credit 组件更新。
mechanism: agent 输出会影响后继 agent，局部指标不能代表最终任务成功。
actionable_rule: trace 中保存 role_id、round_id、local_validity、successor_utility、global_outcome 和 local_pass_global_fail。
exact_action_to_try: 对失败 trace 标记哪个 role/round 首次引入错误，只允许 optimizer 改该 block。
helpful_method: multi-agent credit ledger
evidence_strength: A
main_sources:
  - docs/paper_notes/paper-maspo-2026.md
  - docs/paper_notes/paper-mapro-2025.md
  - docs/paper_notes/paper-temporal-structural-credit-mas-2026.md
counterexample_or_limit: 如果 agent interaction 很弱，joint optimization 成本可能不划算；先做 coupling test。
next_validation: independent agent optimization vs joint reward vs low-credit block update。
```

### I-10：工具调用任务必须把 tool schema 当作可优化对象

```yaml
insight: tool-use 失败常来自工具描述和参数语义，而不是 agent system prompt。
user_facing_one_liner: 工具调错时，不要只改 agent 指令，也要改工具说明和参数规则。
phenomenon: JTPRO 在 ToolACE、ETID、SEAL-Tools 中通过联合优化 global instruction 和 per-tool schema 改善 TSA/SFA/OSR。
mechanism: global instruction 解决选择策略，tool-local schema 解决工具歧义和 slot/value 格式。
actionable_rule: 工具 eval 必须拆成 Tool Selection Accuracy、Slot Filling Accuracy、Overall Success Rate。
exact_action_to_try: 对 20 个相似工具构造 tool-call eval，分别测试 global-only、schema-only、joint 优化。
helpful_method: tool-schema optimization loop
evidence_strength: A
main_sources:
  - docs/paper_notes/paper-jtpro-2026.md
  - docs/industry_practices.md
counterexample_or_limit: 外部 API schema 不可改时，可用 wrapper docs 或 retrieval context 承载局部规则。
next_validation: global-prompt-only vs schema-only vs joint global+schema optimization。
```

### I-11：结构化任务更适合做第一批验证

```yaml
insight: 严格输出格式、复杂 schema、工具调用和结构化抽取更容易形成可解释的 APO 证据。
user_facing_one_liner: 第一批实验不要选开放作文，先选能客观打分的 JSON 抽取或工具调用。
phenomenon: KG Construction、JTPRO、AutoPDL 和 Coin Flip 的正例都集中在 schema、format、tool 或 latent capability 明确的场景。
mechanism: 结构化任务的失败类型、格式错误、字段 F1 和 tool slot 可以拆解，便于定位 prompt 改动的效果。
actionable_rule: M1 首选结构化抽取或 tool-call benchmark，而不是自由文本生成。
exact_action_to_try: 用 100-300 条 `{intent, entities, urgency}` JSON 抽取样本做最小验证。
helpful_method: structured-task validation demo
evidence_strength: A/B
main_sources:
  - docs/paper_notes/paper-apo-kg-construction-2025.md
  - docs/paper_notes/paper-jtpro-2026.md
  - docs/paper_notes/paper-autopdl-2025.md
  - docs/paper_notes/paper-coin-flip-2026.md
counterexample_or_limit: 开放生成任务仍重要，但不适合作为第一批因果清晰的验证。
next_validation: 结构化抽取上跑 pre-gate、exemplar baseline、critique rewrite 和 hygiene gate。
```

### I-12：社媒和二手文章是线索，不是证据

```yaml
insight: 多个平台重复传播同一方法，只说明热度，不说明方法有效。
user_facing_one_liner: 看到爆款 prompt 技巧，先找原论文、代码、数据和失败案例。
phenomenon: Twitter/X、Medium/Substack 和部分博客大量转述 GEPA/DSPy/MIPRO 等方法，但多数不包含可复现实验。
mechanism: 二手传播会放大结论、丢失边界和版本信息。
actionable_rule: 二手来源只能作为 source pointer；进入结论前必须追溯到论文、官方文档、代码、cookbook 或本项目实验。
exact_action_to_try: 读到一个技巧时，抽取 dataset、metric、baseline、model、cost、failure cases；缺字段则降级为线索。
helpful_method: source evidence triage
evidence_strength: B
main_sources:
  - docs/source_batches/twitter_web_analysis_20260608.md
  - docs/source_batches/web_search_platform_analysis_20260608.md
  - docs/source_collection_plan.md
counterexample_or_limit: 高质量工程博客如果包含代码、数据和复现实验，可升级为 stronger evidence。
next_validation: 对 high-impact social claims 建立 trace-to-primary-source 表。
```

## 当前可采信的核心 conclusions

| id | conclusion | evidence_strength | 主要证据 | 边界 |
| --- | --- | --- | --- | --- |
| C-01 | 自动 prompt 优化必须建立在 dataset、metric、版本和回滚之上；没有 eval 的“优化”只是改写。 | A/B | arXiv 深读、GitHub 源码审计、行业工具文档 | 具体工具效果需本项目任务重跑。 |
| C-02 | textual feedback 有用，但不应被解释为真实梯度。 | A | ProTeGi、Flawed Textual Gradients、Scaling Textual Gradients | 不否定 feedback-driven 方法，只限制解释口径。 |
| C-03 | one-shot rewrite 是弱 baseline，不应作为 self-evolution 的目标形态。 | A/B | ProTeGi、GEPA、PromptBreeder、GitHub compare/rewrite 源码 | 小任务中可能够用，但不能支持强结论。 |
| C-04 | 示例选择、tool schema、context packaging 和 agent role 都可能比 instruction wording 更关键。 | A/B | Teach Better、JTPRO、AutoPDL、12-factor agents、industry docs | 第一批验证需控制变量。 |
| C-05 | prompt bloat、dev overfitting、judge hacking 和 memory pollution 是 prompt self-evolution 的主要风险。 | A/B | TextReg、PrefPO、Coin Flip、ERM、industry eval docs | 风险指标需在实验 runner 中固化。 |
| C-06 | GitHub 渠道更适合提炼工程结构和治理方法，不适合单独证明效果。 | B | core4 源码审计和 insight cards | "不适合证明效果"部分源于受限召回（无 token、8 查询的冒烟 discovery）+ core4-only 审计——正典 optimizer 仓库（gepa / PromptWizard / promptomatix）尚未审计；补审 + 本项目最小实验后可升级，见 `github_repo_channel_synthesis_20260609.md` 的「渠道覆盖与已知偏差」。 |

## Helpful methods 候选

### HM-01：Pre-Optimization Gate

```yaml
name: Pre-Optimization Gate
insight_supported: I-01, I-11
problem: 避免在没有 headroom 的任务上浪费复杂 optimizer 成本。
recommended_when: 准备运行任何自动 prompt optimizer 前。
not_recommended_when: 一次性低风险 prompt 微调，或用户只需要人工改写建议。
required_inputs:
  - 20-50 条 held-out 样本
  - zero-shot prompt
  - manual baseline prompt
  - 10-20 个候选 prompt
implementation_steps:
  - 跑 zero-shot 和 manual baseline。
  - 生成或手写 10-20 个候选。
  - 用同一评分器评估所有候选。
  - 计算 best gain、score spread、format error 和成本。
  - 若 best gain 不超过噪声阈值，停止 APO，回到任务定义或 eval。
evaluation_metrics:
  - main_score
  - best_gain_over_zero_shot
  - score_spread
  - format_error_rate
  - token_cost
expected_benefit: 在无提升空间任务上提前止损。
cost_and_latency: 低，通常小于完整 optimizer 成本。
risks: 小样本可能误判；阈值不可跨任务硬套。
rollback_plan: 保留 zero-shot/manual baseline，不接受自动候选。
evidence: docs/paper_notes/paper-coin-flip-2026.md
next_experiment: 在结构化抽取和开放生成各跑一轮 gate。
```

### HM-02：Trace-First Critique Rewrite

```yaml
name: Trace-First Critique Rewrite
insight_supported: I-02, I-03, I-04
problem: 直接让 LLM 改 prompt 不可审计，且容易误判根因。
recommended_when: 有失败样本、错误类型或 agent/tool trace 的任务。
not_recommended_when: 没有可核验输出或评分器的主观写作任务。
required_inputs:
  - baseline prompt
  - failed examples
  - gold/reference or judge rubric
  - trace or intermediate outputs
implementation_steps:
  - 从失败样本生成 error_type 和 critique。
  - 生成 2-3 个 failure hypotheses。
  - 每个 hypothesis 生成一个候选 prompt。
  - 用 dev/validation 选择候选。
  - 记录 prompt diff、选择理由和回滚点。
evaluation_metrics:
  - main_score
  - failure_type_delta
  - validation_score
  - prompt_length_ratio
  - rejected_reason
expected_benefit: 提高改写可解释性，减少 one-shot rewrite 随机性。
cost_and_latency: 中等，需要额外 critique 和候选评估调用。
risks: critique/judge 偏差；hypothesis 过多导致预算膨胀。
rollback_plan: 保留 best_seen prompt；validation 下降则回滚。
evidence: docs/paper_notes/paper-protegi-2023.md, docs/paper_notes/paper-vista-reflection-dark-2026.md
next_experiment: 对同一结构化抽取任务比较 direct rewrite 和 trace-first rewrite。
```

### HM-03：Exemplar Optimization Baseline

```yaml
name: Exemplar Optimization Baseline
insight_supported: I-05
problem: 防止高估 instruction rewrite 的价值。
recommended_when: 有 labeled dev set，且上下文长度允许放入 3-5 个示例。
not_recommended_when: 上下文非常紧张、示例可能泄漏敏感信息或任务强依赖 zero-shot 表现。
required_inputs:
  - exemplar candidate pool
  - fixed instruction
  - dev split
  - hidden/test split
implementation_steps:
  - 固定 instruction。
  - 比较 no-example、random examples、optimized examples。
  - 再比较 instruction optimization + optimized examples。
  - 只在 hidden/test 上报告最终泛化。
evaluation_metrics:
  - main_score
  - dev_test_gap
  - context_tokens
  - rare_label_score
  - format_error_rate
expected_benefit: 识别收益是否来自示例而非 instruction wording。
cost_and_latency: 中等，取决于 exemplar search budget。
risks: 示例选择过拟合；示例覆盖不均；成本上升。
rollback_plan: 若 test/OOD 下降，回到 no-example 或 random-example baseline。
evidence: docs/paper_notes/paper-teach-better-show-smarter-2024.md
next_experiment: 在结构化抽取任务上比较 instruction-only 和 exemplar-only。
```

### HM-04：Prompt Artifact Ledger

```yaml
name: Prompt Artifact Ledger
insight_supported: I-04, I-06, I-07, I-08, I-10
problem: prompt、examples、tool schema、context 和 evaluator 混在一起改，导致不可归因、不可回滚。
recommended_when: 任何研究级或生产级 prompt 优化。
not_recommended_when: 临时一次性聊天。
required_inputs:
  - artifact manifest
  - prompt diff
  - evaluation run
  - cost report
implementation_steps:
  - 为每个 artifact 建版本号。
  - 标注 mutable/frozen。
  - 每个候选记录分数、失败样本、成本、接受/拒绝理由。
  - 保存 rollback point。
evaluation_metrics:
  - reproducibility
  - rollback_time
  - source_traceability
  - frozen_section_violation
expected_benefit: 让 prompt evolution 可审计、可复现、可回滚。
cost_and_latency: 低到中等，主要是记录成本。
risks: 字段过多会降低执行速度；第一版应保持最小字段。
rollback_plan: 按 ledger 恢复上一版 accepted artifact。
evidence: docs/github_repo_insight_cards_20260608.md, docs/industry_practices.md
next_experiment: 为首个实验 runner 输出 `prompt_runs.jsonl`。
```

## 反模式和风险边界

| anti-pattern | 为什么危险 | 对应防线 | 证据 |
| --- | --- | --- | --- |
| 让模型直接“优化一下 prompt” | 无目标、无评估、无回滚，输出只是润色或随机改写。 | HM-01, HM-02 | ProTeGi, VISTA, industry eval docs |
| 只看平均分 | minority class、格式错误、安全边界可能恶化。 | 分层指标、stress split | TextReg, PrefPO, Coin Flip |
| prompt 越改越长 | 可能是训练样本补丁和规则冲突。 | hygiene gate | TextReg, Edit-Level Analysis |
| 允许 optimizer 改 evaluator 或 test cases | 直接 reward hacking。 | frozen evaluator/data | GitHub autoresearch audit |
| raw memory 无界追加 | 继承坏反馈、隐私泄漏、跨任务污染。 | filtered memory + forgetting | ERM, MemAPO, ECC |
| 用社媒热度当证据 | 热度只说明传播，不说明有效。 | source evidence triage | source_batches |
| 多 agent 一起重写 | 无法判断哪个 role/round 引起变化。 | credit ledger | MASPO, MAPRO |
| 工具调用只改 system prompt | tool schema/slot 错误无法被修复。 | JTPRO-style schema optimization | JTPRO |

## 首批验证优先级

| priority | validation/demo | validates | 最小任务 | 成功/失败都能产出什么 |
| --- | --- | --- | --- | --- |
| P0 | 结构化抽取 pre-gate | I-01, I-11, HM-01 | 100-300 条 JSON 抽取 | 判断是否有优化 headroom，校准 noise floor。 |
| P0 | Exemplar baseline | I-05, HM-03 | 同一抽取任务 | 防止误把示例选择收益写成 instruction rewrite 收益。 |
| P1 | Direct rewrite vs trace-first rewrite | I-02, I-03, HM-02 | 失败样本较清晰的抽取/分类 | 判断 critique/hypothesis 是否改善 held-out。 |
| P1 | Performance-only vs hygiene selector | I-07 | 同一候选池 | 判断 prompt bloat 防线是否减少伪提升。 |
| P2 | Tool schema mini benchmark | I-10 | 20-50 个相似工具 | 判断 schema-only/joint 是否优于 global prompt-only。 |
| P2 | Filtered memory | I-08 | 两个相近任务 + 一个异质任务 | 判断 memory 是否降低成本或带来负迁移。 |

## 进入最终报告前的缺口

- 需要把每条 A/B 级洞见追溯到 2-3 个最强来源，而不是堆满所有引用。
- 至少 1 个 HM 需要本项目最小验证或演示记录，才能获得 C 级本项目证据。
- 需要给 `prompt_runs` / `artifact ledger` 定义最小字段，避免 helpful method 停留在口号。
- 对 2026 年新 arXiv 论文，最终报告中应标注 `recent-preprint`，避免过度采信。
- 行业工具文档需要记录版本和访问日期，尤其是托管 prompt optimizer 产品的迁移/弃用状态。
