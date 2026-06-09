# Paper Note: Prompt Codebooks / Discrete Compositional Prompt Optimization

论文：Prompt Codebooks: Discrete Compositional Optimization for Language Model Instruction Refinement

链接：https://arxiv.org/abs/2605.28360

source_id：paper-prompt-codebooks-2026

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：new-hypothesis

阅读日期：2026-06-08

reviewed_by：Codex

local_pdf_path：`local_sources/raw/arxiv_papers/2605.28360/paper.pdf`

local_pdf_sha256：`22C713EE15AE2DC48F0C3C4D0CD7193BF6FA82533B69471A88F13FD3BDEB729F`

local_text_path：`local_sources/raw/arxiv_papers/2605.28360/paper.txt`

local_text_sha256：`7E2739490DE962DA6FBF846BA1D032EE179722D3C2DBCC6A304772BBCF7993AF`

evidence_level：method-results-efficiency-read

## 一句话结论

Prompt Codebooks 的核心经验是：不要总是把 prompt 当成一整段 monolithic text 优化，可以把它拆成可复用的“instinct”离散代码本，并按输入路由组合；这同时降低 prompt 长度和把失败归因到具体 instruction unit。

## 问题设定

- 任务：multi-hop reasoning、math reasoning、instruction following。
- 优化对象：encoder、prompt generator、codebook 中的自然语言 instincts。
- 目标指标：benchmark accuracy / success，同时报告 prompt token efficiency。
- 约束：使用 8B 本地模型，不使用 proprietary model 主评估。

## 方法摘要

- 候选如何生成：维护 K 个自然语言 instinct，encoder 为每个输入选择 S 个 instinct，generator 把它们压缩成最终 prompt。
- 反馈如何获得：critic 对失败分解为 rendering、instinct content、routing 三类问题。
- 如何选择候选：对 encoder routing、codebook entry、generator rendering 分别更新；使用 epsilon-greedy 维持 codebook 探索。
- 是否使用记忆/archive：codebook 本身就是可复用记忆。
- 是否优化 optimizer 自身：优化 prompt 组件，不训练 base LLM。

## 实验设置

- 数据集：HotpotQA、HoVER、AIME-2025、LiveBench-Math、IFBench、PUPA。
- 模型：Qwen3-8B、LLaMA-3.1-8B。
- baselines：zero-shot、MIPROv2、GRPO、GEPA、GEPA+Merge。
- train/dev/test 切分：遵循 GEPA protocol，test 只最终评估。
- 成本或调用次数：默认 K=16 codebook entries、S=4 active instincts、50 epochs、batch size 15。

## 主要结果

- HotpotQA 上，LLaMA-3.1-8B 相比 zero-shot 提升 +30.36；Qwen3-8B 上超过 GEPA +3.34。
- IFBench 上，PCO 达到 41.33，超过 GEPA +2.72；PUPA 与 GEPA 接近。
- AIME-25 上，PCO 为 35.67，高于 GEPA 的 32.00，仅低于 RL-based GRPO。
- Prompt efficiency 明显：HotpotQA 上相对 MIPROv2 缩短 14.1x；aggregate 相对 MIPROv2 缩短 9.6x，相对 GEPA 系方法平均约 2.0x。
- 论文分析显示无 exploration 时 routing 会塌缩到少数过用 instinct，epsilon-greedy 有助于保持 codebook 多样性。

## 失败案例和局限

- codebook routing 和 generator 都由 LLM 语义判断驱动，可能出现错误 routing 或 instinct 漂移。
- 当前主评估集中在 8B 模型和指定 benchmarks，尚未证明在大模型 API 或生产 agent 中同样高效。
- K、S、epoch 等超参数会影响效率和性能，可能需要任务级调参。

## 洞见卡片

```yaml
insight: prompt 可以被优化成“按输入组合的可复用指令单元”，而不是每个任务一整段长 prompt。
evidence_type: method + efficiency-result
paper_evidence:
  section: "3 Method; 5 Results and Analysis; 5.1 Prompt Efficiency"
  table_or_figure: "Table 1, Figure 2"
  quote_or_paraphrase: "PCO 用 K=16 instincts、每输入选 S=4，并在 HotpotQA 等任务上缩短 prompt 同时保持/提升表现。"
mechanism: 离散 bottleneck 让不同输入调用不同子技能，失败反馈能定位到 instinct 或 routing。
actionable_rule: 对高复用任务，建立 prompt skill/codebook，而不是不断追加规则到单一 prompt。
counterexample_or_limit: 如果输入差异小或任务只需单一策略，codebook 可能过度复杂。
minimal_experiment: monolithic optimized prompt vs 8/16-entry codebook + per-input routing。
confidence: medium
```

## 对本项目的启发

- prompt hygiene 不只是限制长度，还可以通过 codebook 化实现“短上下文 + 高复用”。
- 评估日志应记录 selected instinct IDs，便于分析哪些指令单元真正带来收益。
- 对多任务 prompt evolution，codebook 可能比 memory 更适合作为最终 deploy artifact。

## 可复现计划

- 最小复现任务：多类型问答或结构化抽取，人工定义 8 个初始 instincts。
- 需要实现的模块：instinct registry、router、generator、per-instinct success rate、routing collapse detector。
- 预计风险：router 不稳定；instinct 粒度难定；prompt 压缩损失关键约束。
