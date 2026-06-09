# 知乎候选材料洞见与方法卡片

更新时间：2026-06-09

关联文档：[知乎候选材料三层分析](zhihu_three_layer_analysis_20260608.md)

原始 artifact：

- `artifacts/source_search/source_candidates_20260608_132914.jsonl`
- `artifacts/source_search/source_candidates_20260608_132914.md`

## 文档目标

本文把知乎批次从“来源摘要”重写为更贴近最终报告的材料：insights、conclusions、helpful methods、anti-patterns 和最小验证候选。

知乎批次的主要价值不是证明某个 prompt optimizer 有效，而是观察中文社区如何理解、传播、误解和使用 prompt optimization、GEPA、DSPy、context engineering 与 agent self-evolution。进入最终报告时，知乎材料应优先贡献问题意识、通俗表达、反模式和深读线索；性能、收益和适用边界必须由论文、官方文档、代码或本项目实验补证据。

## 证据边界

本批次基于 Brave Search 返回的标题和摘要。直接访问部分知乎链接时遇到 403，因此当前证据等级偏低。

| 等级 | 含义 | 当前用途 |
| --- | --- | --- |
| ZH-L1 | 仅基于搜索标题、摘要、URL 和主题聚类 | 发现中文社区问题意识、传播口径和候选追溯对象 |
| ZH-L2 | 已读全文，且本地记录快照路径、SHA256 和结构化摘要 | 可写行业经验笔记，但仍不直接证明效果 |
| ZH-L3 | 已追溯到原论文、官方文档、代码或可运行示例 | 可支持方法背景和证据链 |
| ZH-L4 | 与其它渠道或本项目实验互相印证 | 可进入最终报告的核心 conclusion |

当前多数知乎卡片是 ZH-L1。凡涉及“超过 RL”“大幅提升”“自动进化”“生产可用”等主张，都必须升级到 ZH-L3 或 ZH-L4 后才能写成结论。

## 快速结论

1. 知乎候选显示中文社区已经把 prompt optimization 从“提示词技巧”转向“样本、评分器、候选、迭代”的工程问题，但很多文章仍缺少评估字段。
2. GEPA 被频繁传播为“比 RL 更强”。更稳妥的洞见是：在有执行轨迹的任务中，自然语言反思可能比单一标量分数提供更密集的改写信号。
3. DSPy/MIPRO 的关键不是“自动写 prompt”，而是把 instruction、examples、metric 和 optimizer 变成可组合、可评估的程序组件。
4. Context engineering 在知乎材料里非常显眼，说明很多实际失败不是 prompt 文案问题，而是 retrieval、memory、tool output、history compression 或 output schema 问题。
5. 工具体验文章可以帮助发现用户需求和本土工具生态，但只有暴露 dataset、metric、diff、cost、failure 和 rollback 的文章才值得进入证据链。
6. Agent self-evolution 方向的热度高，但必须先明确优化对象：task prompt、system prompt、skill、tool description、memory、workflow policy 不能混为一谈。

## 普通用户一眼看懂版

| 具体洞见 | 普通用户可以怎么做 | 为什么有用 | 证据边界 |
| --- | --- | --- | --- |
| 不要先问 AI“帮我优化 prompt”。 | 先写 10-20 条测试样本和失败例子，再让 AI 根据样本改 prompt。 | 没有样本和评分标准时，优化只是改写口吻。 | 知乎材料暴露痛点，效果需实验验证。 |
| 模型失败时，先定位失败类型。 | 把失败分成理解错任务、缺上下文、格式漂移、工具错误、拒答过度、事实错误。 | 只有知道错在哪里，才知道该改 prompt、context 还是工具。 | 由 context engineering 和 agent 文章共同提示。 |
| GEPA 类方法不要理解成万能替代 RL。 | 对有 trace 的任务，比较 `score-only rewrite` 和 `trace + critique rewrite`。 | 轨迹反思能解释失败原因，可能减少盲目搜索。 | 必须回到 GEPA 论文和本项目验证。 |
| DSPy/MIPRO 不是提示词模板库。 | 把任务写成 signature、examples、metric，再让 optimizer 搜索。 | prompt、示例和评价函数会成为可版本化组件。 | 知乎可作术语入口，证据回到 DSPy/MIPRO。 |
| Agent/RAG 场景先查 context，再改 system prompt。 | 分别记录 retrieval、memory、tool result、history、schema 和 prompt。 | 很多失败来自模型看到的信息不对，而不是指令不够漂亮。 | 需要其它平台和工程源码补强。 |
| 工具文章要看评估字段，不看演示截图。 | 只抽取 dataset、metric、baseline、candidate diff、cost、failure、rollback。 | 这些字段决定工具是否能形成可复盘闭环。 | 无评估字段的文章只作工具线索。 |
| 自进化不是“让系统记住一切”。 | 每条 memory/skill 都记录来源、适用范围、验证结果和禁用方式。 | 无界记忆会污染后续任务，形成不可审计漂移。 | 需要项目源码、issue 或实验支撑。 |
| 泛 prompt 技巧要降权。 | 只有当技巧能映射到样本、指标、失败模式或可验证动作时才保留。 | 避免把“经验口诀”写成研究结论。 | 当前批次的泛技巧文章多数不进核心证据链。 |

## Insight 卡片总览

| id | 候选 insight | 主要来源簇 | 证据等级 | 最小验证优先级 |
| --- | --- | --- | --- | --- |
| ZHI-01 | prompt optimization 已从技巧问题转向 eval-driven iteration。 | APO/APE/OPRO/EvoPrompt/PRewrite 中文解读 | ZH-L1，需要追溯论文 | high |
| ZHI-02 | GEPA 的可迁移洞见是 trace-aware reflection，而不是“全面超过 RL”。 | GEPA / reflective prompt evolution 文章 | ZH-L1，需要 GEPA 论文补证 | high |
| ZHI-03 | DSPy/MIPRO 应被写成 prompt-as-program，而不是自动提示词生成器。 | DSPy / MIPRO / Prompt 编译文章 | ZH-L1，需要官方文档和论文补证 | high |
| ZHI-04 | context engineering 把优化对象从单条 prompt 扩展到模型可见上下文。 | Context Engineering / agent context / RAG context | ZH-L1，需工程资料补证 | high |
| ZHI-05 | 工具类文章的筛选标准是是否支持可复盘评估闭环。 | OPIK / Prompt Optimizer / PromptPilot / Coze | ZH-L1，需官方文档补证 | medium |
| ZHI-06 | agent self-evolution 必须先定义可变对象和冻结对象。 | Hermes / Manus / Skill / Agent 自进化 | ZH-L1，需项目源码补证 | high |
| ZHI-07 | 中文来源适合提炼用户语言和误区，不适合直接承载性能结论。 | 全批次综合 | ZH-L1 | medium |
| ZHI-08 | 泛 prompt 技巧是反模式线索，除非它能接入 eval 和版本管理。 | 泛 prompt engineering 文章 | ZH-L1 | medium |

## 详细 Insight 卡片

### ZHI-01：Prompt optimization 已转向 eval-driven iteration

- insight：知乎材料反复把 APE、APO、OPRO、EvoPrompt、PRewrite、PromptBreeder 等方法放在一起，说明讨论重点正在从“写一个好提示词”转向“生成候选、评估候选、选择候选、再迭代”。
- user_facing_one_liner：不要优化一句话，优化一个带测试样本的流程。
- phenomenon：中文文章大量介绍自动提示工程、提示词搜索、反思改写和进化式候选生成，但经常只讲算法名，少讲 dataset、metric 和 validation split。
- mechanism：prompt 是离散文本程序。没有样本、评分器和候选账本时，优化器无法区分真实提升、风格变化和偶然好运。
- actionable_rule：任何 prompt 优化材料都先抽取 `task`、`baseline prompt`、`test cases`、`metric`、`candidate generation`、`selection rule`、`rollback`。
- helpful_method：Eval-first prompt optimization intake。
- exact_action_to_try：把一个已有 prompt 配上 20 条测试样本，先跑 baseline，再要求模型只基于失败样本给出改写理由和 diff。
- before_after_example：改前是“帮我优化这个客服 prompt”；改后是“在 20 条客服样本上，baseline 有 6 条格式错误、3 条拒答过度，请只改输出格式和拒答边界，并保留回滚版本”。
- counterexample_or_limit：一次性创意写作、语气润色或探索性头脑风暴可能不需要完整 eval 闭环。
- evidence_strength：ZH-L1。该 insight 与 arXiv/GitHub/其它平台资料一致时可升级。
- validation_or_demo：对比 one-shot rewrite 与 eval-first rewrite，看 held-out 样本、格式漂移、人工审查时间和成本。

### ZHI-02：GEPA 的核心不是“替代 RL”，而是 trace-aware reflection

- insight：知乎 GEPA 相关文章常被标题化为“超越 RL”或“比强化学习更强”，但对本项目更有价值的是 trace-aware reflection 这个机制解释。
- user_facing_one_liner：有执行过程的任务，不要只看最后得分，要让模型读失败轨迹再改。
- phenomenon：GEPA 被用于连接 prompt evolution、DSPy、agent 轨迹和自然语言反思，传播热度高，但二手文章容易夸大结论。
- mechanism：标量 reward 只告诉优化器好坏，trace 和 critique 能告诉优化器错在哪里、该改哪个组件、哪些行为不能破坏。
- actionable_rule：报告中避免写“GEPA 全面优于 RL”，应写“在某些有轨迹反馈的任务上，语言反思可能提供更高密度的优化信号”。
- helpful_method：Trace-first agent prompt diagnosis。
- exact_action_to_try：同一批失败任务分别用最终分数和完整 trace 生成 prompt diff，比较改动是否更小、更可审计、对 held-out 更稳定。
- before_after_example：改前是“分数低，重写 prompt”；改后是“第 3 步工具调用参数错、history 压缩丢了用户约束，因此只改 tool instruction 和 history summary rubric”。
- counterexample_or_limit：无清晰 trace、评价极噪声、任务过短或输出只需简单格式修复时，trace 反思未必划算。
- evidence_strength：ZH-L1。需要 GEPA 论文、DSPy cookbook 或本项目实验补证。
- validation_or_demo：构造 `score-only rewrite` vs `trace + critique rewrite` 两组，记录样本效率、改动幅度、成本和失败类型迁移。

### ZHI-03：DSPy/MIPRO 应被解释为 prompt-as-program

- insight：知乎 DSPy/MIPRO 材料适合帮助中文读者理解“prompt 不只是文本，而是 signature、examples、metric、optimizer 的组合”。
- user_facing_one_liner：把 prompt 当程序组件管理，而不是当聊天模板收藏。
- phenomenon：中文材料会把 DSPy/MIPRO 简化成“自动生成提示词”，但高质量材料通常会提到 signature、训练样例、metric、optimizer 和编译过程。
- mechanism：DSPy 把任务接口、示例和评分函数显式化，optimizer 才能搜索 instruction 和 few-shot examples。
- actionable_rule：引用 DSPy/MIPRO 时，必须同时说明被优化对象和评分函数，不能只展示优化后 prompt。
- helpful_method：Prompt-as-program conversion checklist。
- exact_action_to_try：把一个聊天模板改写为 `input fields`、`output schema`、`examples`、`metric`、`optimizer budget` 五个部分。
- before_after_example：改前是“你是一个专业分类器，请分类”；改后是“signature: `text -> label, rationale`；metric: label accuracy + JSON validity；examples: 16 条；optimizer: 只允许改 instruction 和 examples”。
- counterexample_or_limit：如果任务没有稳定指标，或样本少到无法区分候选，DSPy/MIPRO 只能作为组织框架，不能自动保证提升。
- evidence_strength：ZH-L1。需要官方文档、论文和 cookbook 升级。
- validation_or_demo：同一分类任务上比较“手写模板改写”和“signature + metric + optimizer”流程的审查成本、格式错误率和 held-out 表现。

### ZHI-04：Context engineering 是 prompt optimization 的边界扩展

- insight：知乎候选中 context engineering 讨论密集，说明实际工程已经把优化对象从 system prompt 扩展到 retrieval、memory、tool result、history compression 和 schema。
- user_facing_one_liner：模型答错时，先看它看到了什么，再看你怎么命令它。
- phenomenon：很多文章围绕上下文工程、agent context、Manus 经验、RAG 和工具上下文展开，主题不再局限于提示词措辞。
- mechanism：LLM 的输出受可见上下文支配。若检索错、工具返回格式乱、记忆污染或历史摘要丢约束，单纯改 system prompt 只能掩盖问题。
- actionable_rule：RAG/agent 任务的优化记录必须拆分 `prompt`、`retrieval`、`memory`、`tool output`、`history`、`output schema`。
- helpful_method：Trace-first agent prompt diagnosis。
- exact_action_to_try：每次失败记录一张 context fault 表，先标注失败来自哪个上下文组件，再决定是否改 prompt。
- before_after_example：改前是“让模型更严格遵守用户约束”；改后是“检索第 2 条文档过期，history summary 删除了用户地区限制，先修 retrieval filter 和 summary rubric”。
- counterexample_or_limit：纯文本改写、短问答或无外部上下文任务，可能仍主要是 instruction 质量问题。
- evidence_strength：ZH-L1。需和 LangChain、Weaviate、Humanloop、GitHub 源码等其它渠道交叉印证。
- validation_or_demo：对 RAG 任务做 `prompt-only fix` 与 `context-first fix` 对比，评估正确率、归因清晰度和二次退化。

### ZHI-05：工具类文章必须通过评估字段过滤

- insight：知乎工具体验文章能发现产品需求，但不能凭演示截图证明工具有效。只有带 dataset、metric、baseline、trial history、failure 和 rollback 的材料才有研究价值。
- user_facing_one_liner：看工具文章时，别问“效果好不好”，先问“它怎么测出来的”。
- phenomenon：OPIK、Prompt Optimizer、PromptPilot、Coze 等候选说明工具化需求强，但摘要层面常缺少可复现配置。
- mechanism：prompt optimizer 工具如果不记录候选、评分、成本、失败样例和回滚点，用户无法判断优化是否泛化，也无法复盘误用。
- actionable_rule：工具类来源进入清单前，必须至少提供 3 类字段：评估输入、候选改动、运行结果。
- helpful_method：Primary-source promotion gate for posts。
- exact_action_to_try：读工具文章时只做一张抽取表：`dataset`、`metric`、`baseline`、`optimized object`、`diff`、`cost`、`failure`、`rollback`。
- before_after_example：改前是“这个工具能一键优化 prompt”；改后是“该工具使用 50 条 validation data、记录 trial history，但未展示 held-out，因此只能作为 medium evidence”。
- counterexample_or_limit：产品介绍可用于发现生态和用户语言，不一定要完全丢弃，但不能进入效果证据链。
- evidence_strength：ZH-L1。需要官方文档或本地运行记录升级。
- validation_or_demo：抽样 10 篇工具文章，用字段表判定哪些能进入 `source_inventory.md`，哪些只作线索。

### ZHI-06：Agent self-evolution 必须先定义可变对象

- insight：知乎 agent 自进化材料热度高，但“自进化”可能指 task prompt、system prompt、skill、tool description、memory、workflow policy 或 evaluator 的变化。若不拆开，无法形成可验证结论。
- user_facing_one_liner：自进化系统要先声明它能改什么，不能改什么。
- phenomenon：Hermes、Manus、Skill、agent context 等文章常把记忆、反思、工具调用、系统提示词和工作流策略混在一起讲。
- mechanism：不同对象的风险和验证方式不同。改 task prompt 影响局部行为，改 system prompt 影响全局边界，改 memory 可能造成长期污染，改 evaluator 会制造伪提升。
- actionable_rule：自进化实验必须冻结 evaluator、数据和安全边界，只允许一个可变对象进入搜索。
- helpful_method：Mutable-object declaration for self-evolution。
- exact_action_to_try：为每次自进化实验写 `mutable_object`、`frozen_objects`、`promotion_rule`、`rollback_plan`。
- before_after_example：改前是“agent 会从经验中自我改进”；改后是“本轮只允许新增一条 skill instruction，不允许改 grader、tools、system safety policy 和 eval cases”。
- counterexample_or_limit：早期探索可以先宽泛收集失败模式，但进入实验或结论前必须拆分变量。
- evidence_strength：ZH-L1。需要项目源码、issues、运行 trace 或 GitHub 审计补强。
- validation_or_demo：比较“允许多对象同时改”和“只允许改 skill description”两组，看指标归因、回滚难度和安全退化。

### ZHI-07：中文来源更适合作为解释层和误区层

- insight：知乎材料在最终报告中最适合承担“普通用户怎么理解”和“常见误区是什么”的角色，而不是承担强证据角色。
- user_facing_one_liner：中文文章能帮你看懂问题，但证明效果要回到一手证据。
- phenomenon：中文社区对 GEPA、DSPy、上下文工程和 agent 自进化的传播很快，能暴露用户关心的问题和术语接受方式。
- mechanism：二手解读会压缩细节，也容易放大标题主张。它擅长解释，不擅长保留实验设置、负例和适用边界。
- actionable_rule：最终报告可引用知乎作为“传播观察”和“误区提醒”，但核心 conclusion 需要 A/B/C 级证据支撑。
- helpful_method：Primary-source promotion gate for posts。
- exact_action_to_try：每条知乎候选都绑定一个 `primary_source_needed` 字段，未追溯前不得写入核心结论。
- before_after_example：改前是“知乎文章说 GEPA 领先 RL”；改后是“中文社区常这样传播，最终判断回到 GEPA 原论文的任务设置、baseline 和预算”。
- counterexample_or_limit：少数知乎长文可能包含原创工程实践、代码或真实评估，此时可按行业笔记模板升级到 ZH-L2。
- evidence_strength：ZH-L1。
- validation_or_demo：深读 10-15 篇高相关知乎全文，标注哪些是原创实践、哪些是一手材料转述、哪些是泛化标题。

### ZHI-08：泛 prompt 技巧如果脱离 eval，是需要降权的反模式

- insight：泛 prompt 技巧文章可以说明用户痛点，但若不能映射到任务、样本、指标或失败类型，就不应进入核心研究结论。
- user_facing_one_liner：不要收藏万能模板，收藏能被测试的改动。
- phenomenon：候选中仍有少量 prompt engineering 技巧、提示词指南和模板类文章，它们通常缺少自动优化、失败案例和评估流程。
- mechanism：通用技巧在不同任务、模型和上下文里很容易失效；没有版本和指标时，用户会把主观满意度误认为稳定收益。
- actionable_rule：泛技巧只在满足以下任一条件时保留：能作为 baseline、能构成失败类型、能转成 eval case、能解释反模式。
- helpful_method：Prompt-tip downgrade rule。
- exact_action_to_try：把技巧文章中的每条建议改写成可测试断言；改不出来的降权。
- before_after_example：改前是“提示词要具体”；改后是“在信息抽取任务中，输出 schema 必须包含字段缺失处理规则，否则 JSON validity 下降”。
- counterexample_or_limit：教学入门内容可以保留在背景材料里，但不要占用最终报告核心篇幅。
- evidence_strength：ZH-L1。
- validation_or_demo：从泛技巧文章抽取 20 条建议，统计有多少能转成 measurable eval case。

## Helpful Methods 候选

### HM-ZH-01：Eval-first prompt optimization intake

```yaml
name: Eval-first prompt optimization intake
insight_supported: ZHI-01, ZHI-05, ZHI-08
problem: 用户经常直接要求优化 prompt，但没有样本、指标、失败类型和回滚点。
recommended_when: 任务会重复执行，且能收集至少 10-50 条代表样本。
not_recommended_when: 一次性创意写作、探索性 brainstorming、无稳定评价标准的开放表达。
required_inputs: baseline prompt, task definition, eval samples, rubric or metric, current failures, target model, cost budget.
implementation_steps: 1. 写清任务和成功标准；2. 收集样本和失败例；3. 跑 baseline；4. 按失败类型聚类；5. 只针对主要失败类型生成候选 prompt；6. 用 validation set 选择；7. 记录 diff、成本、失败和回滚点。
evaluation_metrics: task score, JSON or schema validity, refusal boundary, held-out score, judge disagreement, cost, latency.
expected_benefit: 把主观改写变成可复盘迭代，减少凭感觉选择 prompt。
cost_and_latency: 需要准备样本和至少一次 baseline eval；短期成本高于 one-shot rewrite。
risks: 样本过小会过拟合，rubric 含糊会诱导 judge 偏差。
misuse_or_anti_pattern: 只在训练样本上挑最高分 prompt，不看 held-out 和失败样例。
rollback_plan: 保留 baseline prompt、候选 diff、接受理由和拒绝理由；发布后可回退到 baseline 或上一稳定版本。
evidence: 知乎批次为 ZH-L1 问题线索；需与 GitHub optimizer ledger、Promptfoo/OPIK/Humanloop 等官方资料交叉验证。
next_experiment: 对比 one-shot rewrite 与 eval-first rewrite 的 held-out 表现、格式错误率和审查时间。
```

### HM-ZH-02：Trace-first agent prompt diagnosis

```yaml
name: Trace-first agent prompt diagnosis
insight_supported: ZHI-02, ZHI-04, ZHI-06
problem: Agent/RAG 失败常被误归因为 prompt 写得不好，实际可能来自上下文、工具、记忆或 history compression。
recommended_when: 任务包含多步推理、工具调用、RAG、memory、长对话或 agent handoff。
not_recommended_when: 单轮短文本任务，或没有可记录执行轨迹的简单分类任务。
required_inputs: failed traces, retrieved context, tool calls and outputs, conversation history, prompt versions, expected output schema, evaluator result.
implementation_steps: 1. 保存失败 trace；2. 标注失败发生步骤；3. 分类为 prompt/context/tool/memory/schema/evaluator 问题；4. 冻结无关组件；5. 只改最可能的对象；6. 用相同 trace 和 held-out case 复测。
evaluation_metrics: task success, step-level failure rate, tool error rate, retrieval relevance, schema validity, prompt diff size, rollback difficulty.
expected_benefit: 降低盲目改 system prompt 的概率，让优化对象和失败根因对齐。
cost_and_latency: 需要 trace logging 和人工或 LLM 辅助归因，初期流程比直接改 prompt 慢。
risks: trace 过长会增加成本；LLM 归因可能把偶然事件解释成稳定原因。
misuse_or_anti_pattern: 一次同时修改 prompt、retrieval、tool schema 和 memory，导致无法归因。
rollback_plan: 每轮只发布一个对象的改动，并保留上一个 prompt/context/tool policy 版本。
evidence: 知乎批次为 ZH-L1；GEPA、LangChain context engineering、GitHub agent harness 资料和本项目实验可补强。
next_experiment: 对比 score-only rewrite 与 trace-first diagnosis 在 RAG/agent 任务上的样本效率和二次退化。
```

### HM-ZH-03：Primary-source promotion gate for posts

```yaml
name: Primary-source promotion gate for posts
insight_supported: ZHI-05, ZHI-07, ZHI-08
problem: 二手 posts 容易把论文、工具或项目主张压缩成标题，导致证据强度被高估。
recommended_when: 处理知乎、Twitter/X、Medium、Substack、博客、工具推广和论坛材料。
not_recommended_when: 已经是原始论文、官方文档、固定 commit 源码或本项目运行记录。
required_inputs: post URL, title, summary, claimed method, claimed result, linked primary source, reproducibility fields.
implementation_steps: 1. 抽取文章主张；2. 标记是否有 dataset、metric、baseline、cost、failure；3. 查找 primary source；4. 未找到则保持线索等级；5. 找到后再写行业笔记或论文笔记；6. 在最终报告中标注证据等级。
evaluation_metrics: promoted source ratio, claims with primary source, claims downgraded, unsupported performance claims removed.
expected_benefit: 防止把传播热度当作方法有效性证据。
cost_and_latency: 需要额外追溯时间，可能降低短期材料数量。
risks: 过度保守可能漏掉原创实践文章。
misuse_or_anti_pattern: 因为文章写得清楚或点赞高，就直接写成 conclusion。
rollback_plan: 对每条结论保留 source_id 和 evidence level；无法补证时从 conclusion 降级为 hypothesis 或 observation。
evidence: 知乎批次直接体现该问题；其它平台和 Twitter/X 批次也存在同类传播噪声。
next_experiment: 抽样 30 条 post，统计经过 promotion gate 后进入核心证据链的比例和被降级原因。
```

## Anti-patterns 与降权规则

| anti-pattern | 为什么危险 | 处理规则 |
| --- | --- | --- |
| “知乎文章很多，所以结论很强” | 数量代表传播热度，不代表实验可复现。 | 只作为问题意识，结论必须追溯一手证据。 |
| “GEPA 全面超过 RL” | 忽略任务、预算、baseline、rollout 和反馈信号差异。 | 改写为待验证机制洞见，不写成普遍结论。 |
| “工具能展示 optimized prompt，所以工具有效” | 演示截图无法证明泛化、稳定性和成本收益。 | 只有评估字段完整时才升级证据。 |
| “Context engineering 就是写更长 prompt” | 误把检索、记忆、工具输出和历史压缩都塞进 instruction。 | 拆分 context 组件并分别记录。 |
| “Self-evolution 就是越记越多” | 无界 memory 会污染后续任务，且难以回滚。 | 每条 memory/skill 必须有来源、适用范围、验证和禁用方式。 |
| “Prompt 技巧可跨任务通用” | 不同模型、任务和上下文会让技巧失效。 | 只有能转成 eval case 的技巧才进入核心材料。 |
| “一次改多个变量更快” | 无法判断提升来自 prompt、context、examples 还是 evaluator。 | 研究实验一次只改一个变量，必要时记录混合变量。 |

## 重点追溯对象

| 对象 | 从知乎得到的线索 | 应追溯到哪里 | 进入最终报告的角色 |
| --- | --- | --- | --- |
| GEPA | 反思式 prompt evolution、trace feedback、与 RL 对比 | GEPA 论文、DSPy/HF cookbook、代码或复现实验 | 核心 insight 和验证候选 |
| DSPy / MIPRO | prompt-as-program、signature、optimizer、metric | DSPy 官方文档、MIPRO 论文、cookbook | helpful method 背景 |
| APO / ProTeGi / OPRO / EvoPrompt | 自动提示工程方法索引 | arXiv 论文和已有 paper notes | 方法 taxonomy |
| Context engineering | prompt 到 context/workflow 的边界扩展 | LangChain、Weaviate、Humanloop、GitHub agent 框架 | 工程结论和反模式 |
| Hermes / Manus / Skill 自进化 | agent 经验沉淀、skill、memory 和自进化 | 原项目、源码、issue、运行 trace | 自进化变量拆分线索 |
| OPIK / Prompt Optimizer / PromptPilot / Coze | 工具化需求、本土生态、产品工作流 | 官方文档、固定版本示例、本项目运行记录 | 行业工具地图 |

## 最小验证候选

| id | 要验证的 insight/method | 最小实验设计 | 主要指标 | 备注 |
| --- | --- | --- | --- | --- |
| V-ZH-01 | ZHI-01 / HM-ZH-01 | 同一任务对比 one-shot rewrite 与 eval-first rewrite。 | held-out score、格式错误率、人工审查时间、成本 | 可优先作为最终报告演示实验。 |
| V-ZH-02 | ZHI-02 / HM-ZH-02 | 同一批 agent/RAG 失败样本对比 score-only rewrite 与 trace-first diagnosis。 | 样本效率、失败类型迁移、二次退化、diff size | 需要先准备 trace logging。 |
| V-ZH-03 | ZHI-04 / HM-ZH-02 | 对 RAG 任务分别做 prompt-only fix 与 context-first fix。 | answer correctness、retrieval relevance、schema validity | 验证 context-first 是否更可归因。 |
| V-ZH-04 | ZHI-05 / HM-ZH-03 | 对 30 条 posts 执行 primary-source promotion gate。 | 升级率、降级原因、缺失字段分布 | 可作为资料整理质量检查。 |
| V-ZH-05 | ZHI-08 | 把 20 条泛 prompt 技巧转成 eval case，统计可转比例。 | 可测试比例、不可测试原因、重复度 | 用于决定泛技巧在最终报告中的占比。 |

## 后续处理建议

1. 深读 10-15 篇高相关知乎全文，若需要登录或原文可能失效，快照放入 `local_sources/raw/`，并记录 SHA256。
2. 对每篇知乎文章补 `primary_source_needed` 字段，优先追溯 GEPA、DSPy/MIPRO、APO/ProTeGi、context engineering 和 Hermes/agent 自进化。
3. 能补齐 dataset、metric、baseline、failure、rollback 的文章，再按 `docs/industry_notes/template.md` 写单篇行业笔记。
4. 最终报告不按“知乎文章列表”呈现，而是把本文件的 ZHI cards 融入全渠道 insight pool。
5. 当前文档中的 ZH-L1 判断不能单独作为结论，只能作为 observation、hypothesis 或 user-facing explanation。
