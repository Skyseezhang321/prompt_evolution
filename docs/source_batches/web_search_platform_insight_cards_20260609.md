# 其它平台 Insight / Method Cards：2026-06-09

本文件承接 [其它平台候选来源结构化分析](web_search_platform_analysis_20260608.md)，按最新 insight-first 原则，把 Hugging Face、Arize/Phoenix、Promptfoo、Langfuse、Humanloop、LangChain/LangSmith、OPIK、Weaviate、Medium/Substack/LessWrong 等来源转写成可复用洞见、helpful methods、反模式和验证候选。

本文件不是最终结论。它保留 source_id、主要证据、证据等级和可转验证方式，供最终报告和后续实验选择使用。详细 source cards 仍在 [其它平台候选来源结构化分析](web_search_platform_analysis_20260608.md) 中。

## 证据等级

本文件统一采用 `docs/insight_field_standard.md` 规定的 **A/B/C/D** 等级，不再使用早期的 `L1–L4` 自定义阶梯：

- A：原始论文、官方文档或开源项目文档，且已完成结构化笔记。
- B：多个独立来源重复出现的工程实践，已记录来源和适用条件。
- C：本项目初步实验观察，有运行记录、样例输出和失败案例。
- D：基于资料综合形成的推测，尚未有充分证据，必须标注为待验证。

旧等级换算（仅供对照早期版本）：

| 旧 L 级 | 含义 | 收敛到 | 升级条件 |
| --- | --- | --- | --- |
| L1 | 仅搜索 artifact 标题/摘要/域名线索 | D | 追溯到一手来源后升 B |
| L2 | 已追溯官方文档/blog/cookbook/论文页并登记 | B | 完成结构化行业笔记后升 A |
| L3 | 已有结构化笔记/可复现 notebook/本地源码证据 | A（或 B→A 过渡） | — |
| L4 | 已被论文、代码、官方文档和本项目实验交叉验证 | A + 本项目 C 级证据 | — |

当前其它平台卡片多数是 **B**：来自多个官方工具文档的重复工程实践，但尚未完成结构化行业笔记（升 A），也未经本项目实验验证（升 C）。它们适合进入最终报告的候选洞见和方法章节，但效果类主张仍需本项目最小实验验证。关联的 [其它平台候选来源结构化分析](web_search_platform_analysis_20260608.md) 仍在来源层使用 `strong/medium/weak` 作为快筛状态标签，对应关系：`strong≈B（含可入 A 的官方来源）`、`medium≈B/D`、`weak≈D`。

## 快速概述

其它平台批次最有价值的不是“又找到一批文章”，而是把工具生态反复强调的工程闭环抽象出来：

1. Prompt optimizer 的输入不应只是 prompt，而是 `prompt + dataset + metric + trace + constraints`。
2. Prompt management、trace、versioning 和 rollback 是自动优化的基础设施，不是事后补充。
3. Cookbook、official docs 和 notebook 比 Medium/Substack 摘要更接近可复现证据。
4. 优化过程中的 rejected candidates、trial history、cost 和失败原因，和 best prompt 一样重要。
5. RAG/agent 场景必须先区分 prompt problem 与 context problem，否则实验变量不可归因。

## 结论总览

| conclusion | 当前判断 | 证据等级 | 边界 |
| --- | --- | --- | --- |
| 其它平台渠道最适合提供工具生态的工程闭环，而非效果证明。 | 官方工具文档反复要求 dataset、metric、trace、versioning、rollback。 | B | 不能单独证明某个 optimizer 稳定涨分，需本项目实验。 |
| Optimizer 的输入是 `prompt + dataset + metric + trace + constraints`，不是单条 prompt。 | Promptfoo、Promptim、OPIK、Arize、Vertex、HF cookbook 均以此为闭环。 | B | 主观写作任务需先定义 rubric，否则 metric 不稳。 |
| Prompt management/observability 是治理层，不是效果证据。 | Langfuse、Humanloop、LangSmith、Arize 提供版本/trace/experiment。 | B | 带可复现 notebook 的工具文章可作方法线索，仍需重跑。 |
| Context engineering 与 prompt optimization 必须分变量。 | Weaviate、LangChain、12-factor agents 把 context 拆成多组件。 | B | 纯分类/抽取无外部 context 时可先做 prompt-only。 |
| 厂商提升比例不可直接采信，可采信的是流程字段。 | Arize、OPIK、Vertex、OpenAI 文档给流程，营销标题强调百分比。 | B | 开源 notebook + 固定数据集可作复现起点。 |
| 二手 posts 与社区热度是线索，不是效果证据。 | GEPA/DSPy 在 Medium/Substack/社区大量重复同一来源。 | D | 含代码/数据/失败分析的工程复盘可升 B。 |

## 普通用户一眼看懂版

| 具体洞见 | 普通用户可以怎么做 | 为什么有用 | 证据边界 |
| --- | --- | --- | --- |
| 不要把 prompt 丢给优化器就结束。 | 先准备 20-50 条样本和评分规则，再运行优化器。 | 没有 dataset 和 metric，自动优化只是自动改写。 | Promptfoo、Promptim、OPIK、Arize、HF cookbook 都支持这一闭环；效果需本项目验证。 |
| 每个 prompt 版本都要能解释“为什么改”。 | 保存 diff、来源、失败样例、分数、成本、接受/拒绝原因和回滚点。 | 线上退化时能快速回滚，也能积累可复用经验。 | LangSmith、Langfuse、Humanloop、Arize、OPIK 提供治理线索。 |
| 看工具文章时，不要先看涨幅百分比。 | 先找 dataset、metric、baseline、模型、成本、失败样例、validation split。 | 厂商或博客的提升比例很难迁移，但流程字段可以迁移。 | Arize/OPIK 等 benchmark 只作 workflow evidence。 |
| RAG/agent 失败不一定该改 prompt。 | 分开检查 retrieval、memory、tool output、message history、output schema。 | 很多失败来自上下文组织，而不是 instruction 写得不够好。 | Weaviate、LangChain context engineering、12-factor agents 提供边界证据。 |
| 保留失败和被拒候选。 | 不只存 best prompt，还存 trial history 和 rejected reason。 | 被拒候选能暴露 overfit、格式漂移和安全退化。 | OPIK OptimizationResult、Arize experiments、LangSmith commits 支持该做法。 |
| 社区热度不是证据。 | Medium/Substack 只作为发现原始论文、代码、cookbook 的入口。 | 多篇转述同一论文不能提高方法可信度。 | 其它平台 artifact 中 GEPA 二手解读重复度高。 |

## 卡片总览

| id | 候选 insight / method | 主要来源 | 证据等级 | 可转验证优先级 |
| --- | --- | --- | --- | --- |
| WPI-01 | Optimizer intake 必须先检查 dataset、metric、baseline 和约束。 | Promptfoo、Promptim、OPIK、Arize、HF cookbook | B | high |
| WPI-02 | Prompt version 的最小账本应绑定 trace、eval、成本和回滚点。 | LangSmith、Langfuse、Humanloop、Arize、OPIK | B | high |
| WPI-03 | Trial history 和 rejected candidates 是 optimizer 的学习资料。 | OPIK、Arize、LangSmith、Promptfoo | B | high |
| WPI-04 | Cookbook-first triage 比读二手摘要更适合作为研究入口。 | Hugging Face cookbook/blog、Arize/Phoenix cookbooks | B | medium |
| WPI-05 | Prompt management/observability 是治理层，不是自动优化效果证据。 | Langfuse、Humanloop、LangSmith、Arize | B | high |
| WPI-06 | Context engineering 与 prompt optimization 要分变量验证。 | Weaviate、LangChain docs、12-factor agents | B | high |
| WPI-07 | Vendor benchmark 可采流程，不直接采信提升比例。 | Arize、OPIK、Vertex、OpenAI docs | B | high |
| WPI-08 | Secondary posts 的主要价值是传播地图和原始来源发现。 | Medium/Substack/LessWrong/HF forum | D | medium |
| WPI-09 | 工具选择应按阶段匹配，不要一开始引入重平台。 | Promptfoo、Promptim、Langfuse、Humanloop、Arize、OPIK | B | medium |
| WPI-10 | Judge prompt 也应被版本化、评估和优化。 | Arize LLM-as-a-Judge、OPIK G-Eval、OpenAI graders | B | high |

## Helpful Methods

字段口径以 `docs/insight_field_standard.md` 的 helpful method schema 为准（必填：`name`、`insight_supported`、`problem`、`recommended_when`、`not_recommended_when`、`required_inputs`、`implementation_steps`、`evaluation_metrics`、`risks`、`misuse_or_anti_pattern`、`rollback_plan`、`evidence`）。

### WHM-01：Optimizer Intake Checklist

```yaml
name: Optimizer Intake Checklist
insight_supported: WPI-01
problem: 用户常把 prompt 直接丢给优化器，没有 dataset、metric、baseline 和约束，结果只是自动改写。
recommended_when: 准备使用 Promptfoo、Promptim、OPIK、Arize、Vertex、OpenAI Prompt Optimizer、DSPy/GEPA 等工具优化会重复使用的 prompt。
not_recommended_when: 一次性创意写作、无评分器、无失败样本，或任务目标/约束尚未定义。
required_inputs:
  - 任务定义与不可自动改写的约束
  - 最小 dataset：正常样本、边界样本、历史失败样本
  - baseline prompt、模型、参数、输出 schema
  - metric 或 rubric，并记录评分器版本
  - train/dev/test 切分
implementation_steps:
  - 写清任务和不可自动改写的约束
  - 准备并切分 dataset，优化器只能看 train
  - 固定 baseline prompt、模型、参数和输出 schema
  - 定义 metric 或 rubric，记录评分器版本
  - 运行优化后记录 best prompt、所有候选、分数、成本、失败样例和拒绝原因
evaluation_metrics:
  - dev/test score（dev 提升且 test 不掉分）
  - format_error_rate、safety_failure_rate
  - cost_delta、latency_delta
  - 人工可解释采用理由的比例
risks:
  - 只给 3-5 条 happy path 导致局部补丁
  - 只看平均分掩盖边界失败
  - 同时改 prompt/examples/schema/evaluator 失去归因能力
misuse_or_anti_pattern: 没有 eval 时直接让模型“优化一下 prompt”。
rollback_plan: 保留 baseline prompt 与每个 accepted/rejected 候选；test 掉分则回退到 baseline。
evidence: practice-promptfoo-optimization、practice-langchain-promptim、practice-opik-optimizer-overview、practice-arize-phoenix-prompt-optimization-techniques、practice-hf-dspy-gepa-cookbook（B）。
next_experiment: 用 100-300 条结构化抽取或分类样本，对比手工 prompt、直接 rewrite、checklist-gated optimizer 三种流程。
```

### WHM-02：Prompt Version Ledger

```yaml
name: Prompt Version Ledger
insight_supported: WPI-02, WPI-03
problem: 只存 prompt 文本无法复现线上行为，被拒候选丢失后也无法积累可复用经验。
recommended_when: 任何需要多人协作、长期维护或上线的 prompt。
not_recommended_when: 一次性探索型 prompt 草稿（但一旦进入 eval 或报告结论必须补齐账本）。
required_inputs:
  - prompt_id、version、owner、model、parameters、tools、output_schema
  - prompt diff 和修改原因
  - eval run、dataset split、trace sample、成本、失败样例
implementation_steps:
  - 为每个 prompt 版本记录 prompt_id/version/owner/model/parameters/tools/output_schema
  - 记录 prompt diff 和修改原因
  - 绑定 eval run、dataset split、trace sample、成本和失败样例
  - 记录 adoption decision：accepted/rejected/rolled_back/needs_more_data
  - 保留 rollback target 和触发回滚的指标
evaluation_metrics:
  - 线上回归可追到具体 prompt/model/schema 改动的比例
  - rejected 候选可复查率
  - rollback 定位时间
risks:
  - 只存文本不存模型/参数/tools/schema 仍无法复现
  - 只依赖平台 UI 不导出本地 artifact，影响长期可追踪性
misuse_or_anti_pattern: 把 prompt 当临时文本直接覆盖线上版本。
rollback_plan: 每个 production prompt 保留 parent 和上一稳定版本，按 ledger 恢复。
evidence: practice-langsmith-prompts、practice-langfuse-prompt-management、practice-langfuse-prompt-tracing、practice-humanloop-prompts、practice-arize-ax-prompt-learning、practice-opik-optimizer-overview（B）。
next_experiment: 为后续 optimizer runner 增加 prompt_runs.jsonl，每条候选记录 diff、score、cost、failures、decision 和 rollback target。
```

### WHM-03：Context First Diagnosis

```yaml
name: Context First Diagnosis
insight_supported: WPI-06
problem: RAG/agent/tool-use 失败常被误归因为 prompt 写得不好，实际可能来自 retrieval、memory、tool output 或 history compression。
recommended_when: RAG、agent、tool-use、长上下文任务中 prompt 改写效果不稳定或失败类型混杂。
not_recommended_when: 单轮纯文本分类且上下文固定、无外部 context 的任务。
required_inputs:
  - 失败样例与 trace（检索命中、工具输入输出、中间判断、最终输出、judge 理由）
  - 当前 prompt、retrieval、memory、tool output、history、output schema 记录
implementation_steps:
  - 先把失败归因字段拆开：instruction/retrieval/memory/tool output/history compression/output schema/judge rubric
  - 每次只改一个组件
  - 对每个失败样例记录完整 trace
  - 若错误来自 context，不写成 prompt optimizer 的收益或失败
evaluation_metrics:
  - failure owner 分布（能否定位失败组件）
  - prompt-only fix 与 context fix 的效果可分离度
  - 归因清晰度、token、工具误用率
risks:
  - 同一次实验同时改 prompt/retriever/memory/tool schema 导致不可归因
  - 把“上下文变好”误记为“prompt optimizer 更有效”
misuse_or_anti_pattern: 看到失败就改 system prompt。
rollback_plan: 每层改动独立 commit 或独立 prompt/context version，可逐层回退。
evidence: practice-weaviate-context-engineering、practice-langchain-agent-context-engineering、practice-langchain-deepagents-context-engineering、repo-humanlayer-12-factor-agents（B）。
next_experiment: 同一 RAG/agent 小任务上对比 prompt-only、context-only、prompt+context 三组，检查成功率、token、工具误用和归因清晰度。
```

### WHM-04：Source Triage Rule for Blogs and Tools

```yaml
name: Source Triage Rule for Blogs and Tools
insight_supported: WPI-04, WPI-07, WPI-08
problem: 二手博客和工具营销文章容易把论文/工具主张压缩成标题，导致证据强度被高估。
recommended_when: 阅读 Medium/Substack、产品博客、工具榜单、社媒推荐时。
not_recommended_when: 已经是原始论文、官方文档、固定 commit 源码或本项目运行记录。
required_inputs:
  - 来源 URL、标题、摘要、声称的方法与结果
  - 可复现字段核查：dataset、metric、code、notebook、失败案例、成本、version/rollback
implementation_steps:
  - 判断来源类型：official docs/cookbook/paper page/forum/practitioner blog/paper digest/marketing
  - 对非官方来源只抽取可复现字段，缺失则降级为线索
  - 有实验配置的文章进入候选，只复述论文摘要的降级为 weak
  - 工具榜单只用于发现官方 docs，不直接引用排名或推荐语
evaluation_metrics:
  - 最终报告引用一手来源/可复现流程的比例
  - 被追溯到一手来源的二手主张比例
  - 因缺字段被降级的条目数
risks:
  - 把 GEPA/DSPy 的重复解读当成独立证据
  - 把工具营销文章里的性能提升当成稳定结论
misuse_or_anti_pattern: 因为文章写得清楚或热度高就直接写成 conclusion。
rollback_plan: 对每条结论保留 source_id 和 evidence level；无法补证时从 conclusion 降级为 hypothesis 或 observation。
evidence: candidate-web-search-* GEPA duplicates group、Microsoft APO Medium group、tool-list Medium group、Hugging Face/Arize/OPIK 官方来源（D，传播观察）。
next_experiment: 抽样 10 篇 Medium/Substack，把主张追溯到论文或 docs，统计能保留为 method evidence 的比例。
```

## 详细 Insight Cards

### WPI-01：Optimizer intake 必须先检查 dataset、metric、baseline 和约束

- insight：自动优化前先定义评价问题，而不是先生成候选 prompt。
- user_facing_one_liner：没有测试集和评分规则，就不要启动 prompt optimizer。
- phenomenon：官方优化工具几乎都要求 dataset、metric/evaluator、baseline prompt 或现有 eval config。
- mechanism：optimizer 需要反馈信号选择候选；没有反馈信号时，候选只是风格不同的改写。
- actionable_rule：任何 optimizer run 都必须先通过 WHM-01 checklist。
- counterexample_or_limit：开放写作和品牌语气任务可先做人工 pairwise rubric，但仍要固定评价口径。
- evidence_strength：B。
- main_sources：Promptfoo optimization、LangChain Promptim、OPIK optimizer overview、Arize Phoenix cookbook、HF DSPy GEPA cookbook。
- validation_or_demo：结构化抽取或分类任务上，对比 no-eval rewrite 与 eval-gated optimizer。

### WPI-02：Prompt version 的最小账本应绑定 trace、eval、成本和回滚点

- insight：prompt 不是文本片段，而是一个带上下文的可追踪变更对象。
- user_facing_one_liner：每个 prompt 版本都要像代码 commit 一样可解释、可回滚。
- phenomenon：LangSmith、Langfuse、Humanloop、Arize 和 OPIK 都强调 prompt version、trace、dataset/evaluator 或 experiment 关联。
- mechanism：prompt 效果依赖模型、参数、tools、schema 和输入分布；只存文本无法复现线上行为。
- actionable_rule：采用 WHM-02 ledger 字段作为后续实验和报告的最小记录标准。
- counterexample_or_limit：一次性探索型 prompt 草稿可简化，但一旦进入 eval 或报告结论，必须补齐账本。
- evidence_strength：B。
- main_sources：LangSmith manage prompts、Langfuse prompt tracing、Humanloop prompts/evaluators、Arize AX prompt learning、OPIK OptimizationResult。
- validation_or_demo：在同一 prompt 变体上模拟一次回滚，验证是否能定位触发指标和目标版本。

### WPI-03：Trial history 和 rejected candidates 是 optimizer 的学习资料

- insight：只保存 best prompt 会丢失最有价值的失败证据。
- user_facing_one_liner：被拒绝的 prompt 也要保存，因为它告诉你优化器容易犯什么错。
- phenomenon：OPIK、Arize、LangSmith/Promptim 等都把 experiments、trials、history、scores 或 commits 当作流程对象。
- mechanism：失败候选可暴露 overfit、schema drift、成本膨胀、安全退化和 judge gaming。
- actionable_rule：每次 optimizer run 至少保留 top candidates、rejected candidates、score deltas、failure tags 和 rejection reason。
- counterexample_or_limit：超大规模搜索可先抽样保留，但必须保留决策摘要和代表失败。
- evidence_strength：B。
- main_sources：OPIK optimizer overview、Arize experiments、Promptim/LangSmith tracking、Promptfoo baseline/candidate eval。
- validation_or_demo：人工审查 best-only ledger 与 full-trial ledger，比较能否解释 test 掉分。

### WPI-04：Cookbook-first triage 比读二手摘要更适合作为研究入口

- insight：可运行 cookbook 和 official blog 更接近实验入口，二手摘要更适合传播观察。
- user_facing_one_liner：先找 notebook 和官方 docs，再读解读文章。
- phenomenon：Hugging Face GEPA cookbook 和 cross-encoder blog 包含任务、数据、metric 和 optimizer 配置；大量 Medium/Substack 只复述 GEPA 论文结论。
- mechanism：cookbook 暴露可复现变量，二手摘要通常省略失败案例、成本和评估边界。
- actionable_rule：来源快筛时优先保留 official docs/cookbook；secondary posts 必须追溯原文。
- counterexample_or_limit：高质量 practitioner blog 若含代码、成本、失败和生产流程，可保留为 medium source。
- evidence_strength：B。
- main_sources：HF DSPy GEPA cookbook、HF DSPy + cross-encoders blog、GEPA duplicate group。
- validation_or_demo：同一主题下比较 cookbook 与 5 篇二手解读能提供多少记录字段。

### WPI-05：Prompt management/observability 是治理层，不是自动优化效果证据

- insight：工具平台能提高可审计性，但不能单独证明 optimizer 有效。
- user_facing_one_liner：平台让你管好 prompt，不等于它证明 prompt 变好了。
- phenomenon：Langfuse、Humanloop、LangSmith、Arize 提供 versioning、trace、dataset、experiment、monitoring；这些是流程证据，不是跨任务效果证据。
- mechanism：治理工具降低回滚和审计成本，但性能收益仍取决于任务、数据和 evaluator。
- actionable_rule：最终报告引用工具文档时写“治理闭环”，不写“效果已证明”。
- counterexample_or_limit：带明确 benchmark 和可复现 notebook 的工具文章可以作为方法线索，但仍需本项目重跑。
- evidence_strength：B。
- main_sources：Langfuse docs、Humanloop docs、LangSmith docs、Arize docs。
- validation_or_demo：同一 prompt 优化流程在有/无 ledger 与 trace 的情况下比较审查成本和回滚速度。

### WPI-06：Context engineering 与 prompt optimization 要分变量验证

- insight：agent/RAG 失败经常来自上下文组织，不一定来自 instruction。
- user_facing_one_liner：先查模型看到了什么，再决定要不要改 prompt。
- phenomenon：Weaviate 和 LangChain 文档把 context 拆成 retrieval、memory、tools、messages、state、response format 等组件。
- mechanism：当错误来自检索缺失或 tool output 格式混乱时，改 prompt 可能只是掩盖问题。
- actionable_rule：RAG/agent 实验必须记录 context variable，并至少比较 prompt-only 与 context-only。
- counterexample_or_limit：纯分类/抽取任务如果没有外部 context，可以先做 prompt-only optimizer。
- evidence_strength：B。
- main_sources：Weaviate context engineering、LangChain context engineering docs、12-factor agents。
- validation_or_demo：同一 RAG 任务分别改 prompt、retrieval prompt、tool result schema，比较失败归因。

### WPI-07：Vendor benchmark 可采流程，不直接采信提升比例

- insight：厂商材料的最大价值是暴露工作流字段，而不是证明提升幅度会迁移。
- user_facing_one_liner：看到“提升 184%”先问用的是什么数据和评分器。
- phenomenon：Arize、OPIK、Vertex、OpenAI 等产品文档提供流程；营销或 benchmark 标题常强调提升比例。
- mechanism：任务、模型、数据分布、evaluator 和成本预算不同，提升比例不可直接迁移。
- actionable_rule：从厂商材料抽取 required_inputs、implementation_steps、evaluation_metrics、rollback_plan，而不是抽取结论百分比。
- counterexample_or_limit：开源 notebook、固定数据集和完整配置可作为复现实验起点。
- evidence_strength：B。
- main_sources：Arize GEPA vs Prompt Learning、OPIK optimizer docs、Vertex/OpenAI prompt optimizer docs、Medium OPIK article group。
- validation_or_demo：选一条厂商流程，用本项目任务复跑，只比较流程可用性和边界。

### WPI-08：Secondary posts 的主要价值是传播地图和原始来源发现

- insight：二手博客不应直接进入证据链，但可以帮助发现用户误解和传播重点。
- user_facing_one_liner：社区文章告诉你大家怎么理解，不告诉你方法是否一定有效。
- phenomenon：GEPA、DSPy、MIPRO、Microsoft APO 在 Medium/Substack 中大量重复出现。
- mechanism：传播材料会简化术语、夸大收益、漏掉实验边界，但能暴露哪些概念最容易误用。
- actionable_rule：将 secondary posts 标为 weak/social signal，除非它包含代码、dataset、metric、cost 或失败案例。
- counterexample_or_limit：工程师个人复盘若有真实生产数据和失败分析，可升为 medium。
- evidence_strength：D。
- main_sources：GEPA Medium/Substack duplicate group、Microsoft APO group、HF forum/practitioner blog candidates。
- validation_or_demo：对 secondary posts 做误解标签，例如“GEPA=RL 替代品”“DSPy=自动写 prompt”，并回到一手来源校正。

### WPI-09：工具选择应按阶段匹配，不要一开始引入重平台

- insight：不同工具解决的是不同成熟度的问题。
- user_facing_one_liner：小项目先用简单 eval gate，别一开始上完整平台。
- phenomenon：Promptfoo 偏轻量 CLI eval/optimization；Promptim 偏 prompt optimization library；Langfuse/Humanloop/LangSmith 偏治理和追踪；Arize/OPIK 覆盖 experiment/optimizer dashboard。
- mechanism：早期最缺的是小数据和评分器；后期才需要多人协作、prompt hub、observability 和 rollback。
- actionable_rule：先满足 eval gate，再引入 prompt management，再考虑 optimizer SDK 和 observability 平台。
- counterexample_or_limit：已有线上流量和多人 prompt 协作的团队可以更早引入治理平台。
- evidence_strength：B。
- main_sources：Promptfoo、Promptim、Langfuse、Humanloop、LangSmith、Arize、OPIK docs。
- validation_or_demo：把第一版实验拆成 three-tier tool path：config-only、library optimizer、platform-integrated。

### WPI-10：Judge prompt 也应被版本化、评估和优化

- insight：评分器本身是 prompt 优化闭环中最危险的可变对象之一。
- user_facing_one_liner：评委 prompt 也会偏，也要测试和版本管理。
- phenomenon：Arize LLM-as-a-Judge prompt optimization、OPIK G-Eval、OpenAI graders 都把 judge/rubric 作为明确对象。
- mechanism：如果 judge prompt 漂移或被优化器过拟合，prompt 改写的分数提升会变成伪提升。
- actionable_rule：业务 prompt 和 judge prompt 分开版本化；优化业务 prompt 时冻结 judge；优化 judge 时使用人工校准样本。
- counterexample_or_limit：规则评分或 exact match 任务风险较低，但仍需记录 scorer 版本。
- evidence_strength：B。
- main_sources：Arize Phoenix LLM-as-a-Judge prompt optimization、OPIK G-Eval、OpenAI graders、Promptfoo assertions。
- validation_or_demo：构造固定业务 prompt，分别改业务 prompt 和 judge prompt，观察分数变化是否代表真实质量变化。

## 反模式

| anti_pattern | 为什么危险 | 替代做法 |
| --- | --- | --- |
| 把 prompt 丢给优化器就结束。 | 没有 dataset 和 metric 时，自动优化只是风格化改写。 | 先过 WHM-01 Optimizer Intake Checklist。 |
| 采信厂商“提升 X%”的标题。 | 任务、模型、数据分布和 evaluator 不同，提升比例不可迁移。 | 只抽取 required_inputs/steps/metrics/rollback 流程字段（WPI-07）。 |
| 把工具平台能力当作 optimizer 效果证据。 | versioning/trace/dashboard 是治理，不证明 prompt 变好。 | 引用时写“治理闭环”，效果回到本项目实验（WPI-05）。 |
| 把社区/二手转述当独立证据。 | 多篇转述同一来源只代表热度，不提高可信度。 | 标为 source pointer，追溯一手来源（WHM-04）。 |
| 在 RAG/agent 里一上来就改 system prompt。 | 失败可能来自检索/记忆/工具输出，改 prompt 只是掩盖。 | 先做 WHM-03 Context First Diagnosis 拆变量。 |
| 优化业务 prompt 时让 judge prompt 一起漂移。 | judge 被优化器过拟合会制造伪提升。 | 业务 prompt 与 judge prompt 分开版本化、冻结其一（WPI-10）。 |

## 广搜渠道覆盖与缺口

「其它平台」批次由两类渠道组成：web_search（Brave 域名定向）和通用社区广搜（Hacker News / Stack Exchange / RSS / Reddit / dev.to）。前者是本文件主体；后者本轮净新增信号有限，但**不应静默丢弃**，故在此登记覆盖与缺口（满足 `docs/source_collection_plan.md` 的缺口分析要求）。

| 渠道 | 采集量 | 处理深度 | 说明 |
| --- | --- | --- | --- |
| web_search | 465 | 深读+卡片 | 压缩为 30-50 条 source cards，见 [结构化分析](web_search_platform_analysis_20260608.md)。 |
| hackernews | ~24 | 快筛未深读 | 见 `artifacts/source_search/source_candidates_20260608_083113.*`。 |
| stackexchange | 1 | 快筛 | 同上。 |
| rss | 1 | 快筛 | 同上。 |
| reddit / dev.to | 0 | 命中为空 | 本轮查询未返回相关结果。 |
| x_api | 未跑 | — | 需 `X_BEARER_TOKEN`；Twitter/X 信号已由独立 `twitter_web` 渠道覆盖。 |

通用社区批次（26 条）的信号判断：

- **高重复**：约一半是 GEPA 转贴（substack/HN/observablehq/podcast/HF cookbook/optimize_anything），均指向已覆盖的 GEPA 论文或 cookbook，按 WHM-04 降级为 pointer。
- **已入库或已覆盖**：Promptbreeder、Promptomatix（已在 `source_inventory.md`）；Weaviate context engineering、OPIK agent optimizer（已在 web_search 批次）。
- **低信号产品发布**：Promptify 插件、SimplAI、UltraContext、InsForge、EvoAgents、Openlayer 等 Show HN，缺评估字段，不入证据链。
- **净新增（值得登记）**：
  - `Amazon Bedrock advanced prompt optimization and migration tool`（RSS / AWS blog）——一个尚未覆盖的厂商 optimizer，补充 WPI-07/09 工具地图。
  - `Vertex AI Prompt Optimizer: lock sections via placeholder_to_content`（Stack Overflow）——对应「冻结/可变段落」边界，呼应 frozen-evaluator / mutable-object 约束。
  - `Ask HN: What tools are you using for AI evals? Everything feels half-baked`——社区痛点信号，佐证 WPI-01/WPI-05「eval 基础设施不成熟、需自建闭环」。

**缺口（诚实标注）**：

1. 真实失败案例 / 事故复盘来自社区渠道的覆盖不足。`source_collection_plan.md` 覆盖矩阵要求「失败案例/反面经验 ≥5 个来源」，目前其它平台渠道贡献的多是工具流程，缺 production 踩坑一手叙述。
2. Reddit、dev.to 本轮零命中，x_api 未跑——社区讨论维度（尤其英文实践者的失败故事）尚未真正采集。
3. 上述 3 条净新增仅完成登记，未深读核验；进入结论前需追溯一手来源并补字段。

**后续建议**：若优先补失败案例，针对性查 Reddit（r/LocalLLaMA、r/MachineLearning）、HN 评论区和 Ask HN eval/optimizer 线程，而非再泛搜一轮工具榜单。

## 进入最终报告的建议

- WPI-01、WPI-02、WPI-06、WPI-10 可作为核心 insights。
- WHM-01、WHM-02、WHM-03 可作为 helpful methods。
- WPI-05、WPI-07、WPI-08 可作为证据边界和 anti-patterns。
- WPI-03、WPI-09 可作为后续实验 runner 和工具选型约束。

## 后续动作

1. 将 WHM-01 和 WHM-02 合并进第一版最小实验设计，形成 optimizer intake + prompt ledger。
2. 对 HF DSPy GEPA cookbook、Promptfoo optimization、Arize Phoenix prompt optimization、OPIK optimizer overview、Langfuse prompt experiments 写 3-5 篇行业笔记。
3. 在最终报告中不要单列工具清单作为主内容；先展示 WPI/WHM 卡片，再把工具作为证据索引。
4. 选择 1 个结构化任务做验证：比较 no-eval rewrite、eval-gated rewrite、ledger+trace rewrite 三种流程。
