# arXiv Top80 问题-例子-解决方案行动手册

更新时间：2026-06-09

数据来源：`outputs/arxiv_prompt_search/arxiv_focus_top80_20260608T131514Z.csv`

定位：把 `arxiv_top80_overview.md`、`arxiv_top80_taxonomy.md` 和 `arxiv_top80_key_papers.md` 中的抽象判断翻译成具体问题、可执行方案和最小验证任务。本文中的例子是面向本项目的工程化示例，不是论文原文实验样例；论文原始证据需要后续在 `docs/paper_notes/` 中逐篇核验。

## 写作规则：先让普通用户看懂，再给研究证据

后续新增行动项时，先写成“具体洞见卡片”，再展开论文来源：

- 一句话现象：发生了什么具体、反直觉、可观察的事。
- 适用场景：哪些模型、任务、数据和约束下可以试。
- 操作步骤：用户下一条 prompt 或下一轮实验具体改什么。
- Before / after：至少给一个失败 prompt 或失败输出的变化例子。
- 验证方式：用哪组样本、指标、对照和失败类型判断是否有效。
- 边界：哪些场景不能直接套用，是否只是论文观察或待复现线索。

例如“非 reasoning 模型上重复输入 prompt 可能提升效果”这种洞见，应该被写成可 A/B 测的操作卡，而不是只写成“某论文提出 prompt repetition 方法”。

## 先回答“我能做什么”

这批论文对本项目最直接的启发不是“马上复现最大的方法”，而是把 prompt 优化拆成几个可操作模块：

1. 建一个小而稳定的 eval 集合：20-50 条样本，包含正确答案、失败类型、边界样本和不可违反规则。
2. 把 prompt 拆成 section：role、task、constraints、examples、output format、tool policy，明确哪些可改、哪些不可改。
3. 每次只允许 optimizer 改一个 section 或一个变量，并记录 prompt diff、修改理由、评估结果和回滚点。
4. 至少比较三种反馈：只有分数、自然语言 critique、执行轨迹/错误聚合。
5. 除了主指标，还记录 prompt 长度、重复规则数、成本、延迟、失败案例和 OOD/holdout 表现。
6. 如果是 agent 任务，必须单独记录工具调用、拒答边界、局部 agent 输出和系统级成功。

可以先做一个最小闭环：

```text
baseline prompt
-> 跑 train/dev/test 小样本
-> 收集失败样本和错误类型
-> 让 optimizer 只修改 task 或 output_format section
-> 重跑 dev
-> 通过才跑 test
-> 记录 diff、原因、成本、失败变化、回滚点
```

这个闭环比直接复现 GEPA、SePO 或 MASPO 更适合当前阶段，因为它能验证我们最关心的判断：自然语言反馈、结构化 prompt 和回滚治理是否真的有用。

## 问题 1：prompt 优化看起来涨分，但其实只是记住了验证集

### 具体例子

假设我们做一个“从用户需求中抽取结构化字段”的任务。baseline prompt 在 dev 集上漏掉 `deadline` 字段。optimizer 看到 5 个失败样本后，把 prompt 改成：

```text
Always include deadline. If no deadline is provided, infer one from context.
```

dev 分数上升，因为那 5 个失败样本都有 deadline。但 test 集里很多样本没有 deadline，模型开始胡乱推断，导致事实性下降。

### 这对应哪些论文问题

- TextReg：prompt distributional overfitting。
- Why Prompt Optimization Works, and Why It Sometimes Doesn't：不同 edit family 对不同任务可能有相反效果。
- PrefPO：optimizer 可能生成 brittle 或 misaligned prompt。
- Prompt Optimization Is a Coin Flip：prompt optimization 不是在所有任务上都可靠。

### 解决方案

- 把数据分成 `train_opt`、`dev_select`、`test_holdout`，optimizer 只能看 `train_opt`。
- 增加 OOD 或反例样本，例如“没有 deadline 时必须返回 null”。
- 记录 prompt 新增规则数和 prompt 长度。
- 对每条新增规则要求写明证据：来自哪些失败样本，可能伤害哪些样本。
- 引入 regularization：禁止把具体样本模式写成硬规则；鼓励写成可泛化原则。

### 本项目可以怎么做

在 `docs/experiment_plan.md` 里设计一个最小实验：

- 任务：结构化信息抽取或分类。
- 样本：30 条 train_opt、30 条 dev_select、30 条 test_holdout，至少 10 条反例。
- 对比：
  - manual prompt。
  - full prompt rewrite。
  - section-local rewrite。
  - section-local rewrite + prompt length / rule count penalty。
- 成功标准：dev 提升时 test 不下降；prompt 长度增长不超过 30%；反例错误不增加。

## 问题 2：optimizer 任意重写整段 prompt，破坏了安全约束或输出格式

### 具体例子

原 prompt 明确要求：

```text
Output valid JSON only. Never infer missing personally identifiable information.
```

optimizer 为了提高任务完成率，把 prompt 改得更“积极”：

```text
Be helpful and complete every field as much as possible.
```

结果 JSON 格式偶尔被破坏，缺失字段也开始被模型补全。主任务指标可能上升，但治理要求被破坏。

### 这对应哪些论文问题

- Modular Prompt Optimization：把 prompt 当成单块文本会导致约束漂移。
- SPEAR：需要 guard metric 和 auto-rollback。
- TextReg：prompt 可能增长并积累狭窄规则。
- When Prompt Optimization Becomes Jailbreaking：优化过程可能破坏安全边界。

### 解决方案

- 使用结构化 prompt schema：

```yaml
role: 可改
task: 可改
constraints: 不可改
examples: 可改，但必须保留标签格式
output_format: 不可改
tool_policy: 不可改，除非人工审核
```

- optimizer 每次只改一个可变 section。
- `constraints` 和 `output_format` 做 hash 或 snapshot，自动检测是否被修改。
- 每轮评估同时跑 task metric 和 guard metrics。
- guard metric 失败时自动回滚。

### 本项目可以怎么做

先实现文档级规范，不急着写框架：

- 在每个 prompt 变体记录里增加字段：
  - `mutable_sections`
  - `frozen_sections`
  - `changed_section`
  - `edit_reason`
  - `rollback_point`
  - `guard_metrics`
- 最小实验只允许改 `task` 或 `examples`，禁止改 `constraints` 和 `output_format`。

## 问题 3：只看最终答案，忽略了 agent 过程里的工具错误

### 具体例子

一个 agent 任务要求查询资料、计算结果并输出结论。最终答案偶尔正确，但过程里出现：

- 调错工具。
- 重复调用工具。
- 忽略工具返回的错误。
- 用旧上下文回答。
- 成本翻倍。

如果 eval 只看最终答案，optimizer 可能学到“多试几次总会对”，而不是学到更好的 tool policy。

### 这对应哪些论文问题

- SPEAR：用 Python 对 evaluation DataFrame 做错误聚合和 confusion matrix。
- GEPA：把 reasoning、tool calls、tool outputs 纳入反思轨迹。
- AutoPDL：agent prompting pattern 也是优化对象。
- JTPRO：tool-prompt reflective optimization。

### 解决方案

- agent eval 记录完整 trace：
  - 每次 tool call。
  - tool 参数。
  - tool 返回。
  - 是否使用了 tool 结果。
  - token 成本和延迟。
- 错误类型不要只写“wrong answer”，要拆成：
  - wrong_tool。
  - bad_tool_args。
  - ignored_tool_error。
  - unsupported_inference。
  - output_format_error。
- optimizer 只基于错误聚合改 prompt，而不是读一堆原始 trace。

### 本项目可以怎么做

设计一个小型 tool-use 任务：

- 工具：本地检索或简单表格查询。
- 样本：20 条。
- 指标：
  - final_answer_accuracy。
  - tool_selection_accuracy。
  - invalid_tool_call_count。
  - cost_tokens。
  - latency。
- 对比：
  - baseline agent prompt。
  - 只给最终分数的 optimizer。
  - 给 trace summary / error table 的 optimizer。

如果 trace-summary 版本能减少工具错误，而不是只提高最终答案，就说明 agentic prompt optimization 值得继续。

## 问题 4：多 agent 系统里，每个 agent 局部都对，但整体失败

### 具体例子

三 agent 流程：

```text
Planner -> Researcher -> Writer
```

Planner 输出计划太粗，Researcher 查到了材料但没有标注来源，Writer 写得流畅但引用不可追溯。单独看每个 agent 都“完成了任务”，整体报告却不可复查。

### 这对应哪些论文问题

- MASPO：局部 agent 目标与全局系统目标不一致。
- MAPRO / MASPOB：多 agent prompt optimization 需要 credit assignment。
- CANTANTE / Maestro：agent 系统优化不能只看单节点表现。

### 解决方案

- 对每个 agent 设计局部指标，但候选选择使用系统级指标。
- 给下游 agent 评估上游输出质量，例如 Writer 是否能使用 Researcher 的来源。
- 记录 failure attribution：
  - planning_missing_requirement。
  - research_no_source。
  - writer_unverifiable_claim。
- 不要一次改所有 agent prompt。先固定其它 agent，只改一个 role prompt。

### 本项目可以怎么做

最小实验：

- 任务：生成一段带来源的研究摘要。
- Agents：Planner、Retriever、Synthesizer。
- 第一轮只优化 Retriever prompt。
- 系统级成功标准：
  - claim 都能追溯到 source。
  - 不新增未检索来源。
  - 摘要覆盖任务要求。
- 记录哪个 agent 的 prompt 改动导致系统指标变化。

## 问题 5：没有标准答案，怎么优化 prompt？

### 具体例子

我们要优化“给用户写研究建议”的 prompt。输出没有唯一标准答案，但可以比较两个答案哪个更好：

- 是否更具体。
- 是否区分证据和推测。
- 是否给出可执行下一步。
- 是否避免夸大结论。

传统 accuracy 无法评分，但 pairwise preference 可以工作。

### 这对应哪些论文问题

- PrefPO：pairwise preference prompt optimization。
- LLM Prompt Duel Optimizer：label-free prompt optimization。
- PROMST：human feedback + heuristic sampling。
- CriSPO：多方面 critique-suggestion。

### 解决方案

- 把目标写成 rubric，而不是找唯一答案。
- 每轮生成 A/B 两个候选输出，让 judge 按 rubric 比较。
- judge 必须输出：
  - winner。
  - reason。
  - violated criteria。
  - confidence。
- 抽样引入人工 review，校准 LLM judge。
- 防止 optimizer 迎合 judge：保留隐藏 test rubric 或反例样本。

### 本项目可以怎么做

选一个开放式任务，例如“论文摘要转行动建议”：

- 输入：10 篇论文摘要。
- 输出：每篇的行动建议。
- Rubric：
  - 具体性。
  - 可执行性。
  - 证据边界。
  - 风险意识。
- 对比：
  - LLM-as-judge 分数。
  - Pairwise preference。
  - 人工抽检 20%。

成功标准不是“judge 分最高”，而是人工抽检中 preference 与 judge 的一致性不低于预设阈值。

## 问题 6：prompt 越优化越长、越重复、越难维护

### 具体例子

optimizer 每轮都加一句规则：

```text
Be precise.
Be concise.
Do not hallucinate.
Use evidence.
Always check evidence.
Double-check claims.
```

看起来更安全，实际造成：

- 规则重复。
- 约束互相冲突。
- token 成本增加。
- 模型注意力被稀释。
- 后续人类无法判断哪条规则有效。

### 这对应哪些论文问题

- PrefPO：关注 prompt hygiene 和重复内容。
- TextReg：prompt bloat 与 distributional overfitting。
- Modular Prompt Optimization：固定结构 + 去重。
- Prompt Codebooks：把可复用 instruction units 抽成 codebook，避免重复塞入整段 prompt。

### 解决方案

- 记录 prompt 长度、句子数、重复 n-gram、规则数。
- 每轮 optimizer 必须说明：
  - 新增了什么。
  - 删除了什么。
  - 合并了什么。
- 设置长度预算。
- 将高频有效规则沉淀为 reusable guideline，而不是每个 prompt 都复制。

### 本项目可以怎么做

在 prompt 变体日志中增加字段：

```yaml
prompt_chars:
prompt_tokens_estimated:
rule_count:
duplicated_rule_count:
added_rules:
removed_rules:
merged_rules:
```

最小实验：比较“只允许追加规则”和“允许删除/合并规则”的 optimizer，观察 dev/test 表现和 prompt 长度变化。

## 问题 7：每个任务都从零优化，经验不能复用

### 具体例子

我们先优化“抽取论文贡献”，又优化“抽取行业案例风险”。两个任务都反复发现同一类经验：

- 输出必须区分 observation / inference / conclusion。
- 失败样本常来自“把单个例子写成普遍规律”。
- 引用必须保留来源 id。

如果每个任务都从零开始，optimizer 会重复发现这些经验，浪费成本。

### 这对应哪些论文问题

- MemAPO：成功策略和失败模式双 memory。
- Prompt Codebooks：可复用 instruction units。
- PromptBreeder / SePO：optimizer 的改进经验也可以积累。

### 解决方案

- 建立两类 memory：
  - strategy memory：哪些规则在什么任务上有效。
  - failure memory：哪些错误模式反复出现。
- 每条 memory 必须带证据：
  - 来源任务。
  - 触发样本。
  - 修改前后指标。
  - 失败边界。
- memory 进入新任务前先检索，再由 optimizer 判断是否适用。

### 本项目可以怎么做

先不用实现数据库，用 Markdown 或 JSONL 即可：

```yaml
memory_id:
type: strategy | failure
statement:
evidence_source:
task:
before_prompt:
after_prompt:
metric_delta:
known_limits:
reuse_decision:
```

第一版只记录 10 条 memory，验证它们是否能帮助第二个相近任务减少优化轮数。

## 问题 8：想做“自进化”，但不知道到底进化什么

### 具体例子

有人说“让 prompt 自进化”，可能指三件完全不同的事：

1. 进化 task prompt：让某个任务的 prompt 变好。
2. 进化 optimizer prompt：让负责改 prompt 的 agent 变好。
3. 进化 memory：让系统积累跨任务经验。

如果不区分，实验结果无法解释。性能提升可能来自 task prompt 被调好，也可能来自更多搜索预算，或者 optimizer prompt 学到了任务泄漏信息。

### 这对应哪些论文问题

- PromptBreeder：task prompt + mutation prompt。
- SePO：task agent prompt + prompt agent system prompt。
- MemAPO：长期 memory 自进化。
- GEPA：轨迹反思与 Pareto 经验保留。

### 解决方案

每个实验必须明确优化对象：

```yaml
optimization_object:
  task_prompt: true
  optimizer_prompt: false
  memory: false
  examples: false
  workflow: false
```

一次只打开一个对象。如果要同时优化多个对象，必须分阶段：

```text
Stage 1: 固定 optimizer，只优化 task prompt
Stage 2: 固定 task prompt 生成规则，只优化 optimizer prompt
Stage 3: 固定两者，只加入 memory retrieval
```

### 本项目可以怎么做

先做三组对比：

- A：固定 optimizer prompt，只优化 task prompt。
- B：允许 optimizer prompt 改写，但不使用 memory。
- C：固定 optimizer prompt，加入 strategy/failure memory。

每组使用相同任务、相同预算、相同 evaluator。这样才能判断“自进化”到底来自哪里。

## 问题 9：LLM-as-judge 被 optimizer 利用

### 具体例子

评估 rubric 写着“答案要详细”。optimizer 学会让模型输出很长、看似详尽的回答。judge 给高分，但人类读者发现：

- 事实密度下降。
- 废话变多。
- 没有明确行动建议。
- 引用不可靠。

这就是 optimizer 迎合 judge 偏好，而不是真正改进任务。

### 这对应哪些论文问题

- Exploiting LLM-as-a-Judge Disposition。
- When Gradients Collide。
- PrefPO 中的 prompt hacking。
- When Prompt Optimization Becomes Jailbreaking。

### 解决方案

- judge rubric 要拆分维度，避免单一“quality”。
- 加入反作弊指标：
  - unsupported_claim_count。
  - verbosity_without_evidence。
  - format_violation。
  - safety_violation。
- 保留 hidden tests，不让 optimizer 看到全部 rubric 细节。
- 抽样人工复核 judge 高分样本。

### 本项目可以怎么做

如果后续用 LLM judge，至少记录：

```yaml
judge_model:
judge_prompt_version:
rubric:
calibration_examples:
human_audit_sample_rate:
judge_disagreement_cases:
anti_gaming_checks:
```

并且每次 prompt 提升必须展示 3 个“分数提升但仍失败”的样本，避免只看成功案例。

## 10 个可以立即落地的动作

1. 在 `docs/experiment_plan.md` 增加一个“Prompt 变体记录字段”小节。
2. 为后续实验定义 `train_opt/dev_select/test_holdout` 三份数据。
3. 设计一个结构化 prompt schema，并标记 frozen / mutable sections。
4. 先实现人工记录版 prompt diff，不急着自动化。
5. 为每次 optimizer 修改记录 `edit_reason` 和 `evidence_examples`。
6. 加入 prompt 长度、规则数、重复规则数。
7. 对 agent 任务记录 tool trace 和错误类型。
8. 对 LLM-as-judge 设置人工抽检比例。
9. 建一个 `memory_candidates.md`，只记录有证据的 strategy/failure memory。
10. 选一个小任务跑 3 个 baseline：manual、scalar-score rewrite、critique-guided section rewrite。

## 推荐的第一组最小实验

### 实验 A：结构化 prompt 局部优化是否比整段重写更稳

- 目标：验证 section-local rewrite 能否在不破坏约束的情况下提升指标。
- 假设：局部优化比整段重写更少破坏 output format 和 safety constraints。
- 输入样本：结构化信息抽取或分类任务，90 条样本。
- 模型：先用一个固定模型，后续再跨模型。
- 对比：
  - baseline manual prompt。
  - whole-prompt rewrite。
  - section-local critique rewrite。
- 评估：
  - task accuracy / F1。
  - format violation。
  - frozen section violation。
  - prompt length growth。
  - holdout performance。
- 成功标准：section-local 版本 dev 提升，test 不下降，format/frozen violation 为 0。

### 实验 B：错误聚合是否能提升 agent prompt 优化

- 目标：验证给 optimizer 结构化错误表是否比只给最终分数更有效。
- 假设：错误聚合能减少 tool-selection 和 unsupported inference 错误。
- 输入样本：20-30 条 tool-use 小任务。
- 对比：
  - baseline agent prompt。
  - optimizer sees final score only。
  - optimizer sees error table + trace summary。
- 评估：
  - final answer accuracy。
  - tool selection accuracy。
  - invalid tool call count。
  - cost / latency。
- 成功标准：trace-summary 版本工具错误下降，成本不显著上升。

### 实验 C：prompt memory 是否能减少第二个相近任务的优化轮数

- 目标：验证 strategy/failure memory 是否有跨任务复用价值。
- 假设：有证据的 memory 能减少优化轮数，但无筛选 memory 会引入错误迁移。
- 输入样本：两个相近但不相同的抽取/总结任务。
- 对比：
  - task 2 从零优化。
  - task 2 使用 task 1 的 strategy/failure memory。
- 评估：
  - 达到目标分数所需轮数。
  - 成本。
  - 负迁移样本数。
- 成功标准：memory 版本轮数下降，test 和反例样本不恶化。

## 阅读这些论文时要问的具体问题

后续深读每篇论文时，不只摘摘要，而要回答：

1. 它到底优化了什么对象？
2. optimizer 能看到哪些数据？不能看到哪些数据？
3. 候选 prompt 怎么生成？
4. 反馈是分数、文本、轨迹、偏好还是人工？
5. 如何选择候选？有没有 validation split？
6. 成本是多少？调用多少次模型？
7. prompt 是否变长？有没有重复规则？
8. 是否报告失败案例？
9. 是否跨任务或跨模型泛化？
10. 是否有安全边界、回滚点或人工审核？

只有这些问题回答清楚，论文结论才可以进入最终报告或实验设计。
