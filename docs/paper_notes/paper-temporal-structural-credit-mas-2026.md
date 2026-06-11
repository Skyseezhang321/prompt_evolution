# Paper Note: Temporal and Structural Credit Assignment in LLM-based MAS

论文：Unifying Temporal and Structural Credit Assignment in LLM-Based Multi-Agent Prompt Optimization

链接：https://arxiv.org/abs/2605.30227

source_id：paper-temporal-structural-credit-mas-2026

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：new-hypothesis

阅读日期：2026-06-08

reviewed_by：Codex

local_pdf_path：`local_sources/raw/arxiv_papers/2605.30227/paper.pdf`

local_pdf_sha256：`DCF4EB38443536DD1AC324371C19528B3B6E275DC377EBFB8ED0580C631FD85E`

local_text_path：`local_sources/raw/arxiv_papers/2605.30227/paper.txt`

local_text_sha256：`1D233610BD191B8DCB549CBAF21356915C4408B09B8BA6F7968D9896E9285AAD`

evidence_level：method-results-ablation-read

## 一句话结论

这篇论文把多 agent prompt 优化里的“该改谁、该改哪一轮”说得很清楚：用 aggregation state 作为时间 bottleneck，用共享 role prompt 作为结构 bottleneck，然后只更新低 credit 的 role 或 round，而不是每轮粗暴改全系统。

## 问题设定

- 任务：多 agent 多轮 multiple-choice reasoning。
- 优化对象：role-specific prompts 和 round-wise aggregator prompts。
- 目标指标：最终 answer accuracy。
- 约束：固定 base model 和交互协议；只做 prompt-only optimization，不训练模型。

## 方法摘要

- 候选如何生成：verbalized block coordinate descent，在 role prompts 和 aggregation prompts 之间交替更新。
- 反馈如何获得：中间 role utterance、round aggregation output 和最终 score 共同形成 structural / temporal credit。
- 如何选择候选：选择低 credit roles 或低 credit rounds 进行定向更新，高 credit 部分保持不动。
- 是否使用记忆/archive：不强调长期 memory；重点是 credit-guided targeted update。
- 是否优化 optimizer 自身：否。

## 实验设置

- 数据集：AQuA、MedMCQA、GPQA、MMLU。
- 模型：Qwen2.5-7B-Instruct、LLaMA3-8B-Instruct、Gemma-7B-Instruct。
- baselines：unmodified prompts、DSPy/MIPROv2 black-box prompt optimization。
- train/dev/test 切分：每个数据集固定 100 条 optimization set，较大 leave-out test set 最终评估，test 不参与搜索或 credit assignment。
- 成本或调用次数：固定 budget prompt edits；多次 seed 取均值和标准差。

## 主要结果

- MedMCQA 上，LLaMA3-8B Debate baseline 55.13，credit-guided ours 64.63，提升 9.50；DyLAN 下从 54.13 到 61.13，提升 7.00。
- GPQA 上，Qwen2.5-7B Debate 从 32.26 到 35.83，提升 3.57；Gemma Debate 从 12.56 到 18.67，提升 6.11。
- MMLU 上，LLaMA3-8B Debate 从 68.78 到 74.77，提升 6.00。
- 消融结论：role-only 对角色敏感任务贡献更大，aggregator-only 对需要信息整合的任务更有效；组合通常最佳。
- 收敛分析显示 credit-guided optimization 比 black-box baseline 更快、方差更低。

## 失败案例和局限

- 表格中并非每个组合都提升，例如部分 GPQA/AQuA 设置仍低于 baseline，说明 credit signal 不是万能。
- 只声明 dataset-specific prompt search，不声称跨数据集泛化。
- 需要固定解析规则和 multiple-choice 形式；开放生成中 temporal credit 更难稳定定义。

## 洞见卡片

```yaml
insight: 多 agent prompt 优化应先定位低 credit 组件，再做局部更新。
evidence_type: method + ablation
paper_evidence:
  section: "5.2-5.5 Main Results and Ablations"
  table_or_figure: "Table 1, Figure 3, Figure 4"
  quote_or_paraphrase: "structural 与 temporal update 各自有效，组合在 MedMCQA/MMLU 上最强。"
mechanism: aggregation state 让轮次贡献可观察，共享 role prompt 让角色贡献可累计。
actionable_rule: 多 agent trace 必须存 role_id、round_id、aggregation_state、final_outcome，用于 credit 分解。
counterexample_or_limit: 如果中间 state 不可靠或 evaluator 不能评分，credit 会变成噪声。
minimal_experiment: update-all prompts vs update-low-credit-role vs update-low-credit-round vs combined BCD。
confidence: medium
```

## 对本项目的启发

- 对 pipeline/agent prompt 不要直接做整段 diff；先按 role 和 round 分块。
- 我们的日志 schema 应支持 `prompt_block_id`，例如 `agent:planner`、`round:2_aggregator`。
- credit-guided update 是控制变量更清楚的实验设计，符合“一次只改一个变量”的项目原则。

## 可复现计划

- 最小复现任务：planner/solver/critic 三角色、2-3 轮、多选题或结构化判断。
- 需要实现的模块：round aggregator、role scorer、temporal credit、block coordinate prompt editor。
- 预计风险：credit evaluator 偏差；局部更新破坏全局协作；test-set exposure 边界需要严格记录。
