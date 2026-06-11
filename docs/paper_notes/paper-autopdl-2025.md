# Paper Note: AutoPDL / Automatic Prompt Optimization for LLM Agents

论文：AutoPDL: Automatic Prompt Optimization for LLM Agents

链接：https://arxiv.org/abs/2504.04365

source_id：paper-autopdl-2025

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：actionable-experiment

阅读日期：2026-06-08

reviewed_by：Codex

local_pdf_path：`local_sources/raw/arxiv_papers/2504.04365/paper.pdf`

local_pdf_sha256：`C6589A3B53B7908F9D160078895A56C47151424FED0F618FC5D7747B9778B3AD`

local_text_path：`local_sources/raw/arxiv_papers/2504.04365/paper.txt`

local_text_sha256：`1E81E89935B6FA9C8E34BD048DF9AE671F584FF7A77EC326C6AE186FF336357B`

evidence_level：method-results-read

## 一句话结论

AutoPDL 说明 agent prompt 优化不应只改 instruction 文本，还要把 Zero-Shot、CoT、ReAct、ReWOO 等高层 prompting pattern 当作搜索变量；不同任务和模型的最佳 pattern 差异很大，不存在通用最优套路。

## 问题设定

- 任务：FEVER、GSM8K、GSM-Hard、MBPP+。
- 优化对象：prompting pattern、instruction、few-shot demonstrations，输出为可执行 PDL 程序。
- 目标指标：任务 accuracy。
- 约束：离散搜索空间；用 successive halving 控制评估预算。

## 方法摘要

- 候选如何生成：从 pattern library 中组合 Zero-Shot、CoT、ReWOO、ReAct，并配置 demonstrations / instructions。
- 反馈如何获得：候选 PDL 程序在 validation 数据上执行并计分。
- 如何选择候选：successive halving，先粗评很多候选，再逐步给更好候选更多数据预算。
- 是否使用记忆/archive：保留候选评估轨迹，不是长期 memory。
- 是否优化 optimizer 自身：否。

## 实验设置

- 数据集：FEVER、GSM8K、GSM-Hard、MBPP+。
- 模型：Granite 系列、LLaMA 3.1/3.2/3.3、GPT-4o-mini 迁移评估。
- baselines：zero-shot baseline；不同 pattern 与 few-shot 组合。
- train/dev/test 切分：用 train 构建候选/示例，validation 选择，test 最终评估。
- 成本或调用次数：每个完整优化运行耗时约数分钟到二十多分钟，随任务和模型变化。

## 主要结果

- FEVER 上 Granite 13B Instruct V2 从 6.5% 提升到 74.0%，增幅 67.5pp，最佳 pattern 是 3-shot ReWOO。
- GSM8K 上 LLaMA 3.3 70B 从 85.5% 到 95.4%，增幅 9.9pp，最佳 pattern 是 3-shot CoT；部分 Granite code 模型没有找到超过 zero-shot 的配置。
- MBPP+ 上 Granite 34B Code 从 48.7% 到 61.3%，增幅 12.6pp，最佳 pattern 是 3-shot ReAct；部分模型最佳仍是 zero-shot。
- GPT-4o-mini 交叉实验显示，开源模型上优化出的 PDL 程序迁移到 GPT-4o-mini 后在 FEVER/GSM-Hard/GSM8K 分别有 4.0pp、9.3pp、13.1pp 提升，但 MBPP+ 没提升。

## 失败案例和局限

- 并非所有模型/任务都有 headroom；多处结果显示最佳仍是 zero-shot。
- ReAct/ReWOO 的适用性受任务和工具反馈影响，例如 MBPP+ 不实现 ReWOO，因为它不能利用执行反馈。
- PDL 增强了可执行性和可读性，但也要求用户接受 prompt-as-program 的工程表示。

## 洞见卡片

```yaml
insight: 对 agent 来说，prompting pattern 是比局部措辞更大的优化变量。
evidence_type: direct-result
paper_evidence:
  section: "5 Results; 7 Conclusion"
  table_or_figure: "Table 1, Table 2, Table 3"
  quote_or_paraphrase: "不同模型/任务的最佳 pattern 在 CoT、ReAct、ReWOO、Zero-Shot 间切换。"
mechanism: pattern 决定模型是否能调用工具、显式推理、复用 demonstrations；instruction 只是在既定 pattern 内微调。
actionable_rule: 设计 agent APO 时，先搜索 pattern/workflow，再优化每个节点的 instruction。
counterexample_or_limit: 如果任务 zero-shot 已接近饱和，pattern search 可能没有收益。
minimal_experiment: zero-shot vs CoT vs ReAct vs ReWOO 的 successive-halving 小搜索。
confidence: high-for-agent-pattern-search
```

## 对本项目的启发

- prompt evolution 的实验记录应增加 `prompting_pattern` 字段，不能只记录 prompt text。
- 对工具或代码任务，先判断是否需要 ReAct 这类执行反馈 pattern，再谈 instruction 优化。
- PDL/YAML 程序化表示值得参考，因为它让 prompt diff、回滚和复现实验更明确。

## 可复现计划

- 最小复现任务：一个 QA、一个数学、一个工具/代码任务，各 50-100 条 dev 样本。
- 需要实现的模块：pattern library、candidate builder、successive halving evaluator、PDL-like manifest。
- 预计风险：搜索空间膨胀；pattern 与 few-shot 同时变化会导致因果归因困难。
