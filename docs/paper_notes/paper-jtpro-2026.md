# Paper Note: JTPRO / Joint Tool-Prompt Reflective Optimization

论文：JTPRO: A Joint Tool-Prompt Reflective Optimization Framework for Language Agents

链接：https://arxiv.org/abs/2604.19821

source_id：paper-jtpro-2026

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：actionable-experiment

阅读日期：2026-06-08

reviewed_by：Codex

local_pdf_path：`local_sources/raw/arxiv_papers/2604.19821/paper.pdf`

local_pdf_sha256：`EB565688A1EF0CC35A67BE24E5656EAEBF357138DC93CB9557FA0EC32CFBF1A5`

local_text_path：`local_sources/raw/arxiv_papers/2604.19821/paper.txt`

local_text_sha256：`2BD9B4B93129937B1884B22E06C456385A03CCB5350A7BD7E4EEB6084D530CB5`

evidence_level：method-results-ablation-read

## 一句话结论

JTPRO 的核心工程洞见是：工具 agent 的失败不只在 global instruction，也常在 per-tool schema 和 slot 描述；真正的优化对象应是“全局策略 + 工具局部描述 + 共享 slot 语义”的联合 context。

## 问题设定

- 任务：大工具集合中的 tool selection 和 argument slot filling。
- 优化对象：global instruction prompt P 和每个工具的 schema/argument descriptions。
- 目标指标：Tool Selection Accuracy (TSA)、Slot Filling Accuracy (SFA)、Overall Success Rate (OSR)。
- 约束：不合并/别名化工具，不训练模型；保持工具本地差异并减少重复 schema 文本。

## 方法摘要

- 候选如何生成：基于 rollout failures 提出 localized edits，更新 global instruction 和相关 tool/slot schema。
- 反馈如何获得：比较 predicted tool-call trace 与 gold trace，诊断 tool confusion、missing slots、value format errors。
- 如何选择候选：GEPA-style Pareto candidate pool；minibatch 改善后再在 validation 上接受。
- 是否使用记忆/archive：维护 candidate context pool 和 validation-best context。
- 是否优化 optimizer 自身：否。

## 实验设置

- 数据集：ETID、ToolACE-300/500/750/1000、SEAL-Tools。
- 模型：GPT-4o mini、o3-mini、GPT-5 等。
- baselines：Base、GEPA、JTPRO；另比较 CoT-style/MIPRO 等。
- train/dev/test 切分：ETID Train-1/2/4 examples per tool，固定 test 404；ToolACE fixed Train/Val/Test；SEAL-Tools Train 600/Val 100/Test 100。
- 成本或调用次数：按 minibatch rollout、Pareto select、validation acceptance 循环。

## 主要结果

- ToolACE 1000 tools 上，o3-mini OSR 从 Base 51.27 到 JTPRO 64.46，提升 13.19；GPT-5 从 62.37 到 73.55。
- ToolACE 中工具数增加主要打击 TSA，JTPRO 通过减少 tool confusion 提升 OSR。
- ETID 中 Base TSA 已高，但 OSR 低，说明瓶颈在 slot/value；JTPRO 在 GPT-4o mini Train-4ex 中 OSR 从 46.53 到 66.83，提升 20.30。
- SEAL-Tools 中，JTPRO 稳定提升 SFA/OSR，例如 GPT-5 OSR 从 28.8 到 33.6。
- 作者强调 joint refinement 优于只优化 global prompt 或只优化 tool specs，因为错误同时来自选择策略和工具局部语义。

## 失败案例和局限

- 当前评估以 call-level correctness 为主，不执行真实后端工具，不能覆盖 runtime side effects。
- 主要处理并行多工具和 schema-rich 工具；对长链依赖工具调用的覆盖有限。
- 需要 labeled tool-call traces，低数据或无标签场景下成本较高。

## 洞见卡片

```yaml
insight: 工具 agent 的 prompt 优化必须把 tool schema 当作可优化 artifact。
evidence_type: method + benchmark-result
paper_evidence:
  section: "6 Results and Analysis"
  table_or_figure: "Table 2, Table 3, Table 4"
  quote_or_paraphrase: "ToolACE 主要是 TSA 瓶颈，ETID 主要是 SFA/slot-value 瓶颈；JTPRO 联合改两者。"
mechanism: global instruction 解决策略选择，per-tool schema 解决歧义和参数格式，shared slot rules 降低重复冲突。
actionable_rule: tool-use eval 日志要分开记录 TSA、SFA、OSR，并允许 optimizer 修改工具描述而不只改 agent prompt。
counterexample_or_limit: 如果工具 schema 来自外部不可修改 API，需要用 wrapper docs 或 retrieval context 承载改写。
minimal_experiment: global-prompt-only vs schema-only vs joint global+schema optimization。
confidence: high-for-tool-agent-settings
```

## 对本项目的启发

- 研究 prompt evolution 时，必须把“prompt artifact”扩展到 tool descriptions、argument docs、format rules。
- 对工具调用任务，主指标不能只看最终 answer，要拆成 selected tool、slots、values。
- JTPRO 的 slot semantics globalization 可转成我们自己的 schema hygiene 检查：重复参数规则应上提到 global rule。

## 可复现计划

- 最小复现任务：20-50 个相似工具的 synthetic tool-selection + slot-filling benchmark。
- 需要实现的模块：tool-call trace evaluator、TSA/SFA/OSR metrics、schema edit generator、global slot rule merger。
- 预计风险：真实工具 schema 不可修改；schema edit 引入冲突；gold traces 构造成本高。
