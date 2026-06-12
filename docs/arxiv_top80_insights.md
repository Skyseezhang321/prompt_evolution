# arXiv Top80 洞见与经验总结（一读版）

更新时间：2026-06-09

> **历史快照（2026-06-12 冻结）：** 本文系 top80 标题/摘要级一读产出，此后未随深读批次更新，不再维护。洞见的现行单一事实来源是 [Insight / Method 统一目录](insight_method_catalog_20260609.md)（I-01..14）与[主报告 v4](analysis_report_v4_20260611.html)；arXiv 渠道深读综合见 [Batch 3 综合](arxiv_deep_reading_batch3_synthesis.md)，全部 37 篇笔记目录见[文献地图](literature_map.md)。本文保留作研究过程存档。

数据来源：`outputs/arxiv_prompt_search/arxiv_focus_top80_20260608T131514Z.csv`

定位：本文不是论文目录，也不是实验操作手册，而是从 top80 论文中提炼“可复用洞见”。每条洞见都尽量写成可判断、可迁移、可验证的经验。

证据等级：第一轮洞见。当前主要依据 arXiv 标题、摘要、top80 聚焦结果和部分已核验的 arXiv 页面。后续必须通过 `docs/paper_notes/` 深读补齐实验设置、表格结果、失败案例和代码细节。

## 什么才算本项目要的洞见

例如 [Prompt Repetition Improves Non-Reasoning LLMs](https://arxiv.org/abs/2512.14982) 这类“重复同一段 prompt 可能提升非 reasoning 模型效果”的发现，是一个好的洞见范式。它尚需进入本项目深读和复现实验，不能只凭传播文章采信提升比例；但它作为“什么叫具体洞见”的样子很清楚，因为它具备几个特征：

- 具体：它说的是一个可观察现象，而不是泛泛地说“prompt 很重要”。
- 反直觉：重复文本看起来像噪声，但可能改变模型注意或指令权重。
- 可操作：我们可以马上设计 A/B test。
- 有边界：它不一定对所有模型、任务、上下文长度都成立。
- 可沉淀：如果反复有效，可以变成 prompt 设计经验或 eval 检查项。

因此，本项目后续整理论文时，不应只写：

```text
ProTeGi 使用自然语言梯度和 beam search。
```

而应写成：

```text
洞见：失败样本不只应该被打分，还应该被压缩成“可编辑的语言反馈”。这种反馈可以告诉 optimizer 当前 prompt 缺什么、误导了什么、应该往哪个语义方向改。beam search 的作用不是装饰算法，而是承认单次 LLM 改写不可靠，需要保留多个候选并用数据选择。
```

下面按这种标准整理第一批洞见。

## 一眼看懂版：可直接转成用户方法的洞见

这一节不是替代后面的论文分析，而是把学术判断先压缩成普通用户能马上理解和尝试的操作卡片。后续 HTML 报告应优先展示这一层，再展开论文证据和边界。

| 具体洞见 | 普通用户可以怎么试 | 先别泛化到哪里 |
| --- | --- | --- |
| 对非 reasoning、短输出、信息定位类任务，可以试一次“重复关键 prompt”。 | 把原任务原样重复一遍，或把关键约束在结尾再写一次；用同一批问题比较准确率和格式错误率。 | 不要默认适用于 reasoning 模型、长链推理、长上下文 RAG 或需要严格 token 成本控制的任务。 |
| 只告诉模型“错了”没用，要告诉它“错在哪里”。 | 让评估器输出失败类型，例如事实/推测混淆、漏字段、格式坏、拒答过度，再据此改 prompt。 | 不要把 judge 的一句话当真理；失败类型要能追溯到样本。 |
| 不要直接采用模型给出的第一版“优化后 prompt”。 | 每次生成 3-10 个候选，用验证集选，而不是让模型自评哪个最好。 | 小样本或主观写作任务里，候选选择可能比改写本身更难。 |
| Prompt 越改越长，可能是在给训练样本打补丁。 | 记录新增规则数、prompt 长度和重复率；新增规则必须绑定失败样本。 | 不要把“更详细”自动等同于“更好”。 |
| 把 prompt 拆成 role、task、constraints、examples、output format，比整段重写更稳。 | 只允许 optimizer 改一个 section；约束和输出格式做 hash 或人工审查。 | 对非常简单的一次性聊天，结构化成本可能超过收益。 |
| 有 labeled dev set 时，示例选择本身就是优化对象。 | 比较 no example、random examples、optimized examples，而不是只优化 instruction。 | 示例会泄露分布偏差，必须有 held-out 检查。 |
| Agent 任务的失败原因通常藏在 trace 里，不在最终答案里。 | 记录工具调用、检索结果、每步中间输出和最终失败类型，再改对应环节。 | 不要只看最终答案好坏就改 system prompt。 |
| “是否值得优化”要先测，不要默认 optimizer 一定有用。 | 先跑 zero-shot、人工 baseline、10-20 个随机/手工候选，估计提升空间和噪声。 | 如果候选差异没超过噪声，应该停下修任务定义或 eval。 |

## 洞见 1：自然语言 feedback 的价值不是“像梯度”，而是把失败样本变成可编辑证据

相关论文：

- [ProTeGi](https://arxiv.org/abs/2305.03495)
- [Scaling Textual Gradients via Sampling-Based Momentum](https://arxiv.org/abs/2506.00400)
- [Textual Gradients are a Flawed Metaphor for Automatic Prompt Optimization](https://arxiv.org/abs/2512.13598)
- [Modular Prompt Optimization](https://arxiv.org/abs/2601.04055)

具体现象：

只给 optimizer 一个分数，例如 `accuracy=0.72`，它不知道应该改哪里。给它失败样本和自然语言 critique，例如“当前 prompt 没有要求区分事实和推测，导致模型把推测写成结论”，它就能生成更有方向的改写。

ProTeGi 的关键不是把 LLM 反馈神秘化为真的梯度，而是引入一个结构：

```text
失败样本 -> 自然语言批评 -> prompt 编辑候选 -> 数据选择
```

可迁移经验：

- eval 不能只输出分数，至少要输出失败类型和修改建议。
- critique 应该面向 prompt，而不是面向模型人格。例如不要只写“模型不够认真”，而要写“prompt 没有指定当证据不足时输出 unknown”。
- critique 最好绑定样本 id，方便回溯它来自哪些失败。

具体例子：

任务：把论文摘要转成结构化字段。

失败输出：模型把“可能提升泛化”写成“已经证明提升泛化”。

低价值反馈：

```text
Wrong answer.
```

高价值反馈：

```text
当前 prompt 没有要求区分 observation / inference / conclusion。请在输出格式里增加 evidence_level 字段，并要求没有实验支持的主张标为 inference。
```

可验证实验：

- A 组：optimizer 只看样本分数。
- B 组：optimizer 看失败样本 + 自然语言 critique。
- C 组：optimizer 看失败样本 + section-local critique。

观察 B/C 是否在 test holdout 上更稳，而不只是 dev 涨分。

边界和风险：

- textual gradient 不是数学梯度，不能默认可累积、可组合或总是指向正确方向。
- critique 可能包含 judge 偏见。
- critique 太长会遇到上下文墙，Scaling Textual Gradients 这类论文的意义正在这里。

## 洞见 2：beam search / Pareto / bandit 的核心作用是承认“单次 LLM 改写不可靠”

相关论文：

- [ProTeGi](https://arxiv.org/abs/2305.03495)
- [GEPA](https://arxiv.org/abs/2507.19457)
- [EvoPrompt](https://arxiv.org/abs/2309.08532)
- [MASPO](https://arxiv.org/abs/2605.06623)
- [Bandit-Based Prompt Design Strategy Selection](https://arxiv.org/abs/2503.01163)

具体现象：

LLM 根据同一批失败样本生成 prompt 改写时，可能有的候选变好、有的变坏、有的只修复局部样本、有的破坏格式。直接采用第一版改写是不稳的。

这些论文反复出现 beam search、Pareto frontier、evolutionary population、bandit selection，本质不是为了算法花哨，而是为了处理候选不确定性。

可迁移经验：

- 每次优化至少生成多个候选 prompt。
- 不要让 optimizer 自己声明“这个最好”，必须用 held-out dev 选择。
- 如果目标不止一个，例如准确率、成本、格式、安全，应该保留 Pareto 候选，而不是压成一个总分。
- 候选选择策略和 prompt 改写策略同等重要。

具体例子：

优化一个客服分类 prompt，三个候选：

```text
A: 强调先判断用户意图。
B: 强调输出 JSON。
C: 增加 12 条业务规则。
```

A 提升分类准确率，B 降低格式错误，C 在 dev 上涨分但 prompt 变长且 test 下降。单目标选择可能选 C，多目标 Pareto 会保留 A/B，让人决定是否值得牺牲格式或成本。

可验证实验：

- 单候选直接采纳 vs 5 候选 beam search。
- 单一 accuracy 选择 vs accuracy + format violation + prompt length 的 Pareto 选择。

边界和风险：

- 搜索预算越大，越可能过拟合 dev。
- 如果候选都来自同一个有偏 optimizer，beam search 只是放大同类偏差。
- 需要记录每个候选的来源、分数、失败样本和被淘汰原因。

## 洞见 3：prompt 越优化越长，往往不是能力增强，而是过拟合信号

相关论文：

- [TextReg](https://arxiv.org/abs/2605.21318)
- [PrefPO](https://arxiv.org/abs/2603.19311)
- [Modular Prompt Optimization](https://arxiv.org/abs/2601.04055)
- [Why Prompt Optimization Works, and Why It Sometimes Doesn't](https://arxiv.org/abs/2605.26655)

具体现象：

很多 optimizer 的默认动作是追加规则。它会把失败样本里的局部现象写成全局 instruction，短期提升 dev，长期造成 prompt bloat、重复规则、互相冲突和 OOD 下降。

可迁移经验：

- prompt 长度本身就是指标。
- 新增规则必须有证据，也必须说明可能伤害哪些样本。
- 每轮优化不应只允许 append，也应允许 delete、merge、simplify。
- 规则越具体，越要警惕它是否只服务于某几个训练样本。

具体例子：

失败样本中有 3 条数学题需要逐步推理。optimizer 追加：

```text
Always solve every problem step by step with detailed calculations.
```

这可能提升数学题，但对分类、提取、简短问答任务会增加冗余甚至引入错误。更好的规则是条件化的：

```text
For tasks requiring arithmetic or multi-step reasoning, show the intermediate reasoning needed to verify the final answer. For extraction tasks, do not add reasoning text.
```

可验证实验：

- 记录每轮 prompt token 数、规则数、重复规则数。
- 比较 append-only optimizer 和 edit-with-delete optimizer。
- 增加 OOD holdout，专门检测新增规则是否伤害其它类型样本。

边界和风险：

- prompt 变长不一定总是坏。有些任务确实需要明确 constraints。
- 关键是区分“必要结构化约束”和“为训练样本打补丁”。

## 洞见 4：结构化 prompt 比整段 prompt 更适合自动优化

相关论文：

- [Modular Prompt Optimization](https://arxiv.org/abs/2601.04055)
- [AutoPDL](https://arxiv.org/abs/2504.04365)
- [Promptomatix](https://arxiv.org/abs/2507.14241)
- [promptolution](https://arxiv.org/abs/2512.02840)

具体现象：

整段 prompt 被 optimizer 任意重写时，很难知道性能变化来自哪里，也很难保护安全规则、输出格式和不可变约束。结构化 prompt 把可变和不可变部分分开，让优化更像软件变更。

可迁移经验：

把 prompt 拆成：

```yaml
role:
task:
definitions:
constraints:
examples:
output_format:
tool_policy:
```

然后标注：

```yaml
mutable: [task, examples]
frozen: [constraints, output_format, tool_policy]
```

这样 optimizer 每次只能改一个 section，diff 可审查，失败可回滚。

具体例子：

如果 JSON 格式经常错，不要让 optimizer 重写整段 prompt。只允许它改 `output_format` section，或者只增加一个 JSON example。其它 section 保持不变。

可验证实验：

- whole-prompt rewrite vs section-local rewrite。
- 观察 task score、format violation、frozen section violation、prompt length growth。

边界和风险：

- 结构化 prompt 的初始 schema 需要人工设计。
- schema 太死可能限制 optimizer 发现新策略。
- 所以第一版可以只冻结安全和格式，允许 task/examples 改动。

## 洞见 5：agent prompt 优化的关键证据在 trace 里，不在最终答案里

相关论文：

- [GEPA](https://arxiv.org/abs/2507.19457)
- [SPEAR](https://arxiv.org/abs/2605.26275)
- [AutoPDL](https://arxiv.org/abs/2504.04365)
- [JTPRO](https://arxiv.org/abs/2604.19821)

具体现象：

Agent 最终答对不代表 prompt 好。它可能调错工具、重复调用、忽略错误、靠冗余搜索碰巧答对。只看最终答案会诱导 optimizer 学会“多试几次”，而不是学会正确工具策略。

可迁移经验：

- agent eval 必须记录 trace。
- trace 要聚合成错误表，而不是整段塞给 optimizer。
- prompt 修改应该针对错误类型，例如 wrong_tool、bad_args、ignored_tool_error、unsupported_inference。

具体例子：

一个检索 agent 回答正确，但实际调用了 5 次搜索，其中 3 次 query 无关。最终 accuracy 是 1，tool efficiency 很差。优化目标如果只看 accuracy，不会修这个问题。

更好的反馈：

```text
在 20 个样本中，7 个失败来自 bad_tool_args，主要原因是 query 里包含了完整用户问题而不是关键词。请只修改 tool_policy section，让 agent 先提取 3-5 个检索关键词。
```

可验证实验：

- final-score-only optimizer vs trace-summary optimizer。
- 指标包括 final accuracy、tool selection accuracy、invalid tool calls、latency、cost。

边界和风险：

- trace 记录会增加工程成本。
- trace 太长会干扰 optimizer，需要先聚合。
- 复杂 agent 系统还需要做 credit assignment。

## 洞见 6：多 agent prompt 优化本质是 credit assignment，不是多个 prompt 独立调参

相关论文：

- [MASPO](https://arxiv.org/abs/2605.06623)
- [MAPRO](https://arxiv.org/abs/2510.07475)
- [MASPOB](https://arxiv.org/abs/2603.02630)
- [CANTANTE](https://arxiv.org/abs/2605.13295)

具体现象：

多 agent 系统中，某个 agent 的局部输出看起来正确，但可能让下游失败。Planner 的计划过粗，Researcher 没有来源，Writer 就会写出不可追溯结论。单独优化 Writer prompt 不能解决上游信息缺口。

可迁移经验：

- 多 agent eval 要有局部指标和系统指标。
- 候选选择应看系统级成功，而不只是单个 agent 局部得分。
- 每次只改一个 agent prompt，固定其它 agent，才能判断变化来源。

具体例子：

报告生成流程：

```text
Planner -> Retriever -> Synthesizer
```

如果最终报告缺来源，不要马上改 Synthesizer。先检查 Retriever 是否输出 source_id。如果上游没有 source_id，下游 prompt 再强也只能猜。

可验证实验：

- 固定 Planner/Synthesizer，只改 Retriever prompt。
- 系统指标：claims_with_source_ratio、unsupported_claim_count、final_quality。

边界和风险：

- 多 agent 搜索空间很大，容易成本失控。
- 联合优化必须限制预算和可变对象。

## 洞见 7：LLM-as-judge 一旦进入优化闭环，就变成可被利用的目标

相关论文：

- [PrefPO](https://arxiv.org/abs/2603.19311)
- [Exploiting LLM-as-a-Judge Disposition](https://arxiv.org/abs/2604.20726)
- [When Gradients Collide](https://arxiv.org/abs/2605.26046)
- [When Prompt Optimization Becomes Jailbreaking](https://arxiv.org/abs/2603.19247)

具体现象：

如果 judge 偏爱详细回答，optimizer 会让模型变啰嗦。如果 judge 偏爱自信表达，optimizer 会让模型更少承认不确定。如果 safety judge 有固定措辞偏好，optimizer 可能学会绕过它。

可迁移经验：

- judge prompt 必须版本化。
- judge 不能只输出总分，要输出分项和反作弊检查。
- 必须保留隐藏样本或人工抽检。
- 每次分数提升都要展示失败样本，尤其是“judge 高分但人类不满意”的样本。

具体例子：

Rubric 写“答案要充分”。optimizer 学会输出 1000 字，但事实密度下降。分数上升，用户体验下降。

解决方式：

```yaml
judge_dimensions:
  correctness:
  evidence_support:
  concision:
  actionability:
  uncertainty_calibration:
anti_gaming_checks:
  unsupported_claim_count:
  verbosity_without_new_evidence:
  format_violation:
```

可验证实验：

- 用同一批输出比较单一总分 judge 和多维 judge。
- 人工抽检 judge 高分样本，记录 disagreement cases。

边界和风险：

- 人工抽检成本高。
- 多维 judge 也可能被利用，只是更难。
- judge 本身也需要 eval。

## 洞见 8：所谓“自进化”至少有三种对象，混在一起会让结论失真

相关论文：

- [PromptBreeder](https://arxiv.org/abs/2309.16797)
- [SePO](https://arxiv.org/abs/2606.04465)
- [MemAPO](https://arxiv.org/abs/2603.21520)
- [GEPA](https://arxiv.org/abs/2507.19457)

具体现象：

“prompt 自进化”可能指：

1. task prompt 在变好。
2. optimizer prompt 在变好。
3. memory / archive 在积累经验。

如果实验同时打开这三件事，最后无法解释性能提升来自哪里。

可迁移经验：

每个实验必须声明优化对象：

```yaml
optimization_object:
  task_prompt: true
  optimizer_prompt: false
  memory: false
  examples: false
  workflow: false
```

可验证实验：

- A 组：只优化 task prompt。
- B 组：允许 optimizer prompt 改写。
- C 组：固定 optimizer prompt，但加入 memory。

三组同任务、同预算、同 evaluator，才能判断“自进化”到底是什么在起作用。

边界和风险：

- optimizer prompt 自我修改可能破坏安全边界。
- memory 可能引入错误迁移。
- archive 越大，越需要去重、遗忘和证据等级。

## 洞见 9：prompt memory 的核心不是“记住更多”，而是记住有证据的策略和失败模式

相关论文：

- [MemAPO](https://arxiv.org/abs/2603.21520)
- [Prompt Codebooks](https://arxiv.org/abs/2605.28360)
- [Efficient and Accurate Prompt Optimization](https://arxiv.org/abs/2411.07446)

具体现象：

如果每个任务都从零优化，系统会反复发现同一类经验，例如“区分事实和推测”“缺证据时输出 unknown”“保留 source_id”。这些经验应该沉淀。但如果无筛选地记忆所有 prompt 片段，又会污染新任务。

可迁移经验：

memory entry 必须有证据和边界：

```yaml
memory_id:
type: strategy | failure
statement:
evidence_task:
trigger_examples:
metric_delta:
known_limits:
reuse_decision:
```

具体例子：

失败 memory：

```text
在论文摘要任务中，如果 prompt 没有强制区分 observation / inference / conclusion，模型会把未验证推测写成结论。该规则在行业案例总结任务中也可能适用，但在开放创意写作任务中不一定适用。
```

可验证实验：

- 第二个相近任务从零优化 vs 使用第一个任务积累的 10 条 memory。
- 观察达到目标指标所需轮数、成本和负迁移样本数。

边界和风险：

- memory 复用可能造成过度保守。
- memory 需要过期和冲突解决机制。
- 成功经验和失败模式都要记录，不能只记成功 prompt。

## 洞见 10：prompt-as-program 的意义是把 prompt 工程变成软件工程

相关论文：

- [AutoPDL](https://arxiv.org/abs/2504.04365)
- [Promptomatix](https://arxiv.org/abs/2507.14241)
- [promptolution](https://arxiv.org/abs/2512.02840)
- [DSPy](https://arxiv.org/abs/2310.03714)
- [MIPROv2](https://arxiv.org/abs/2406.11695)

具体现象：

当 prompt 只是字符串，版本、变量、示例、上下文、工具策略容易混在一起。prompt-as-program 把这些拆成可组合模块，使优化可以像编译和调参一样进行。

可迁移经验：

- 不要只保存最终 prompt 文本，还要保存生成它的配置。
- instruction、examples、retrieval context、tool policy、model parameters 应分开记录。
- prompt diff 应该能定位到模块级，而不是只能看整段文本差异。

具体例子：

与其保存：

```text
final_prompt_v17.txt
```

不如保存：

```yaml
prompt_program:
  instruction_version: v4
  examples_version: v3
  output_schema_version: v2
  retriever_config: top_k_5
  model: fixed-model-id
  optimizer: section_local_critique_v1
```

可验证实验：

- 单文本 prompt 版本管理 vs 模块化 prompt config。
- 比较回滚速度、错误定位速度和重复实验可复现性。

边界和风险：

- prompt-as-program 初始工程成本更高。
- 对很小的单轮任务可能过度设计。
- 适合长期任务、agent workflow 和多模型评估。

## 洞见 11：应用型 APO 的价值常常不在新算法，而在暴露任务边界

相关论文：

- [Automatic Prompt Optimization for Knowledge Graph Construction](https://arxiv.org/abs/2506.19773)
- [AutoMedPrompt](https://arxiv.org/abs/2502.15944)
- [Clinical QA / ArchEHR-QA 系列](https://arxiv.org/abs/2506.10751)
- [Political Science Text Classification](https://arxiv.org/abs/2409.01466)
- [APRIL](https://arxiv.org/abs/2509.25196)

具体现象：

应用论文不一定贡献通用 optimizer，但会告诉我们 prompt optimization 在真实任务中遇到哪些边界：schema complexity、输入长度、多关系抽取、医学证据、API synthesis、动态示例选择等。

可迁移经验：

- 应用论文适合用来选实验任务和失败类型。
- 方法论文适合用来选 optimizer。
- 不要因为应用论文分数高就直接采纳其方法为通用结论。

具体例子：

Knowledge Graph APO 论文提醒：同样是抽取任务，schema 复杂度、文本长度和关系多样性会显著改变 prompt 优化难度。这比“某 optimizer 平均分更高”更能指导我们设计 eval。

可验证实验：

- 同一个 optimizer，在简单 schema 和复杂 schema 上分别跑。
- 观察 prompt 修改是否从格式规则转向 schema disambiguation。

边界和风险：

- 应用论文可能高度依赖领域数据。
- 任务指标可能不适合本项目最终目标。

## 洞见 12：有些时候不应该自动优化 prompt，应该先修 eval 或任务定义

相关论文：

- [Prompt Optimization Is a Coin Flip](https://arxiv.org/abs/2604.14585)
- [Why Prompt Optimization Works, and Why It Sometimes Doesn't](https://arxiv.org/abs/2605.26655)
- [Textual Gradients are a Flawed Metaphor](https://arxiv.org/abs/2512.13598)

具体现象：

如果任务定义含糊、标签不一致、judge 不稳定、失败样本类型混乱，optimizer 会朝错误方向努力。prompt optimization 不是替代问题定义的工具。

可迁移经验：

在启动 optimizer 前，先检查：

- 任务目标是否明确。
- 成功标准是否可度量。
- 数据标签是否一致。
- train/dev/test 是否隔离。
- 失败样本是否能归类。
- 是否有不可违反约束。

具体例子：

如果用户问“优化一下研究建议 prompt”，但没有定义什么是好建议，optimizer 只能迎合 judge 或生成更像样的文字。正确做法是先定义 rubric：具体性、证据边界、可执行性、风险意识。

可验证实验：

- 未定义 rubric 直接优化 vs 先定义 rubric 和失败类型再优化。
- 比较人工抽检一致性和 prompt 变体稳定性。

边界和风险：

- 过度定义 rubric 也会让输出僵化。
- 需要在明确目标和保留开放性之间取平衡。

## 可以沉淀成项目原则的初版结论

这些结论可以进入后续 final report，但目前仍需深读和实验支撑：

1. Prompt optimizer 的输入不应只是分数，至少应包含失败样本和可追溯 critique。
2. 自动优化 prompt 时，候选选择机制和候选生成机制同等重要。
3. Prompt 长度增长、规则重复和样本特化是 prompt overfitting 的早期信号。
4. 结构化 prompt 和 section-local edit 比整段自由重写更适合可回滚研究闭环。
5. Agent prompt optimization 必须看 trace 和工具错误，不能只看最终答案。
6. Multi-agent prompt optimization 是 credit assignment 问题。
7. LLM-as-judge 一旦进入优化闭环，就必须做 anti-gaming 和人工抽检。
8. 自进化必须声明对象：task prompt、optimizer prompt、memory 或 workflow。
9. Prompt memory 只有在带证据、边界和负迁移检查时才有研究价值。
10. Prompt-as-program 的核心价值是可复现、可组合、可回滚，而不只是自动调 prompt。
11. 应用型 APO 论文主要用于发现任务边界和失败类型，不宜直接当通用算法证据。
12. 如果 eval 和任务定义不清楚，先不要优化 prompt。

## 下一步应该怎么改阅读笔记

后续每篇 `docs/paper_notes/` 不应只写“方法摘要”，还要强制回答：

```yaml
insight:
phenomenon:
mechanism:
actionable_rule:
counterexample_or_limit:
evidence_strength:
minimal_experiment:
```

例如 ProTeGi 的笔记应该写：

```yaml
insight: 失败样本需要转成可编辑语言反馈，而不是只转成分数。
phenomenon: LLM 可以根据错误样本批评当前 prompt，并生成语义相反方向的编辑候选。
mechanism: critique 提供缺失约束、歧义来源和错误归因；beam search 用数据筛掉坏候选。
actionable_rule: 每轮 prompt 优化都要记录失败样本、critique、候选 prompt 和选择理由。
counterexample_or_limit: critique 可能过拟合 minibatch；文本梯度不是数学梯度。
evidence_strength: 待全文深读核验。
minimal_experiment: scalar-score rewrite vs critique-guided rewrite。
```
