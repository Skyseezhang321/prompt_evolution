# Paper Note: GEPA / Reflective Prompt Evolution

论文：GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning

链接：https://arxiv.org/abs/2507.19457

source_id：paper-gepa-2026

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：high-signal-extension

阅读日期：2026-06-08

reviewed_by：Codex

local_pdf_path：`local_sources/raw/arxiv_papers/2507.19457/paper.pdf`

local_pdf_sha256：`AB3A5139BAC83F192AD67529368D77B84B0D807E95A8E4FD0DAA8D45FD046BEC`

local_text_path：`local_sources/raw/arxiv_papers/2507.19457/paper.txt`

local_text_sha256：`469E2EFC0A05B472AC78E1E02C164B50312A7DF237D5F67F9501A5E72BFC504B`

evidence_level：method-and-results-read

## 一句话结论

GEPA 的关键结论是：当系统执行轨迹、工具反馈、编译错误、rubric 失败原因等信息能被序列化成自然语言时，prompt 优化不必只依赖稀疏标量 reward；把这些诊断信号转成反思式 prompt mutation，并用 Pareto frontier 保留“对某些样本特别有效”的候选，可以在远少于 RL rollout 的预算下获得更强结果。

## 问题设定

- 任务：优化一个包含一个或多个 LLM prompt 的 compound AI system。
- 优化对象：系统内各模块的自然语言 prompt；GEPA+Merge 还会在不同模块候选之间做 system-aware crossover。
- 反馈输入：训练样本、执行轨迹、evaluation trace、数值分数和可选的自然语言反馈。
- 目标：在 rollout 预算受限时，提高验证/测试任务表现，尤其是多模块、工具调用、检索、数学和代码类 workflow。
- 对照对象：GRPO、MIPROv2、Trace/OptoPrime、TextGrad，以及贪心候选选择和 beam search 消融。

## 方法摘要

- 候选如何生成：选中当前候选系统的一个模块，在 minibatch 上执行，收集 execution trace 和 evaluation trace，然后用 reflection LM 改写该模块 prompt。
- 反馈如何获得：`feedback function` 不只返回 scalar score，也返回自然语言解释，例如 compiler errors、failed rubrics、人工评分解释或模块级失败信息。
- 如何选择候选：维护 `D_pareto` 上的候选表现矩阵。对每个样本保留取得最高分的候选，去掉被支配候选，再按候选出现在 Pareto frontier 的频次随机采样下一代父候选。
- 是否使用记忆/archive：是。候选池保留多条 lineage，Pareto frontier 起到 diversity archive 的作用。
- 是否优化 optimizer 自身：否。GEPA 优化 task/system prompts，但反思 meta-prompt 和候选选择算法本身是固定的。

## 实验设置

- 任务：HotpotQA、IFBench、HoVer、PUPA、AIME-2025、LiveBench-Math；扩展实验还包括 NPU/CUDA kernel generation 和 adversarial prompt search。
- 模型：Qwen3 8B 和 GPT-4.1 Mini；GRPO 对 Qwen3 8B 做 LoRA/附录含 full finetune 对照。
- baselines：GRPO、MIPROv2、MIPROv2-No-Demos、Trace/OptoPrime、TextGrad。
- 预算：主文对 Qwen3 8B 的 GRPO 使用固定 24,000 rollouts；GEPA 按任务使用约 1,839 到 7,051 rollouts，平均 3,936。
- 成本：GPT-4.1 Mini 表 2 相关实验总成本低于 500 美元；文中报告 GEPA 约 86 美元、GEPA-Merge 约 67 美元、MIPROv2 约 76 美元、Trace/TextGrad 约 172 美元。

## 主要结果

论文直接报告：

- Qwen3 8B 上，GEPA aggregate 从 baseline 45.23 提升到 54.85，超过 GRPO 的 48.91 和 MIPROv2 的 47.84；GEPA 在 6 个任务里 5 个超过 GRPO，但 AIME-2025 低于 GRPO。
- GPT-4.1 Mini 上，GEPA aggregate 为 65.22，GEPA+Merge 为 66.36，超过 TextGrad 59.14、MIPROv2 58.67、Trace 56.30。
- 论文称 GEPA 对 GRPO 平均高约 6%，最高高 20%，并且最高使用 35 倍更少 rollouts；匹配 GRPO 最佳验证分数时，某些任务达到最多 78 倍样本效率。
- GEPA-Qwen-Opt 只用 Qwen3 8B 优化 prompt，再直接迁移到 GPT-4.1 Mini，aggregate improvement 为 +9.00，高于直接在 GPT-4.1 Mini 上优化的 MIPROv2、TextGrad 和 Trace。
- Pareto 候选选择消融中，Qwen3 8B 四任务 aggregate improvement：SelectBestCandidate +6.05、BeamSearch +5.11、GEPA +12.44，说明候选选择策略本身是主要贡献。
- Prompt 长度方面，GEPA/GEPA+Merge 生成的 prompt 最高比 MIPROv2 短 9.2 倍；论文还报告更短 prompt 与更高 aggregate 性能同时出现。

## 失败案例和局限

论文直接或间接暴露：

- GEPA+Merge 在 GPT-4.1 Mini 上有效，但在 Qwen3 8B 上会造成性能下降；作者认为原因是 mutation 和 crossover 的预算分配、merge 调用时机没有自适应。
- Qwen3 8B 的 AIME-2025 上，GEPA/GEPA+Merge 为 32.00，低于 GRPO 的 38.00，说明反思式 prompt evolution 不是所有任务都替代 RL。
- GEPA 的 rollout 预算中大部分花在验证候选上，而不是产生学习信号；作者提出可通过更小验证集或动态验证子集提高样本效率。
- 扩展到 inference-time code search 和 adversarial prompt search 的结果很强，但作者明确称这些是 preliminary findings，需要系统研究。
- 该方法依赖 evaluation trace/feedback function 的质量；当评价过程只能给一个标量分数，优势可能收窄。

## 洞见卡片

```yaml
insight: 可解释的 evaluation trace 比稀疏标量 reward 更适合 prompt 优化。
evidence_type: direct-method + direct-result
paper_evidence:
  section: "3, 4"
  table_or_figure: "Algorithm 1, Table 1, Table 2"
  quote_or_paraphrase: "GEPA 把执行轨迹和评价轨迹交给 reflection LM 生成 prompt 更新；在多任务上用远少于 GRPO 的 rollout 超过 GRPO。"
mechanism: execution/evaluation trace 给出错误发生的位置和原因，reflection LM 可以把它压缩成新规则；scalar reward 只能告诉优化器输赢。
actionable_rule: 设计 prompt eval 时，不只保存 score，还要保存 per-sample trace、失败原因、parser/validator 错误、rubric 命中情况。
counterexample_or_limit: 没有可靠 trace 或反馈质量差时，GEPA 会退化为普通反思式改写；AIME 上也未稳定超过 GRPO。
minimal_experiment: 同一任务比较 score-only rewrite、error-message rewrite、full-trace reflective mutation。
confidence: high-for-trace-rich-workflows; medium-for-pure-classification
```

```yaml
insight: 不要只沿着当前全局最优 prompt 继续优化，要保留对不同样本有效的局部赢家。
evidence_type: ablation
paper_evidence:
  section: "3.1, Observation 3"
  table_or_figure: "Algorithm 2, Table 3, Figure 6"
  quote_or_paraphrase: "Pareto-based selection 的 aggregate improvement 为 +12.44，明显高于 SelectBestCandidate 和 BeamSearch。"
mechanism: 某个候选可能只解决一类样本，但这类策略后续可以扩展；贪心全局最优容易早早锁死在局部模式。
actionable_rule: prompt 优化日志应记录 candidate-by-example score matrix，而不只是 candidate aggregate score。
counterexample_or_limit: Pareto 集过大时会增加验证成本，需要动态子集或支配剪枝。
minimal_experiment: best-average parent selection vs per-example Pareto parent selection。
confidence: high
```

```yaml
insight: 反思式 instruction optimization 正在重新挑战 few-shot demonstration optimization。
evidence_type: direct-result
paper_evidence:
  section: "Observation 2, Observation 4"
  table_or_figure: "Table 2, Figure 17, Figure 18"
  quote_or_paraphrase: "GEPA 在 GPT-4.1 Mini 上超过 MIPROv2，并产生更短的 prompt；作者认为现代 LLM 的 instruction-following/self-reflection 能力改变了 instruction vs demo 的权衡。"
mechanism: 高质量规则能覆盖一组失败模式，而 few-shot demo 增长快、成本高，且可能过拟合示例表面形式。
actionable_rule: 不应默认把 prompt 优化预算先花在 few-shot 选择；先试 instruction-only reflective optimization，再决定是否加 demos。
counterexample_or_limit: 对格式高度依赖或低样本任务，few-shot 仍可能是必要约束。
minimal_experiment: instruction-only GEPA-style rewrite vs demo-only retrieval vs instruction+demo combined。
confidence: medium-high
```

## 对本项目的启发

- 我们的 eval 设计要先升级日志结构：每个失败样本都应保存 `execution_trace`、`evaluation_trace`、`feedback_text`、`module_name`、`candidate_id`。
- 第一批实验不要直接做 RL 对照；更务实的是做 score-only vs trace-aware 的 prompt evolution 对照。
- Candidate archive 必须是矩阵化的，至少能回答“这个 prompt 解决了哪些样本、牺牲了哪些样本”。
- 反思式优化如果要进入生产，需要记录 prompt 长度和 inference 成本；GEPA 把 prompt compactness 作为重要实用结果，这点值得纳入指标。

## 可复现计划

- 最小复现任务：结构化抽取或 judge prompt，100-300 条样本，有 per-row parser/rubric error。
- 需要实现的模块：
  - trace-rich evaluator。
  - reflection mutation prompt。
  - candidate-by-example score table。
  - Pareto parent selector。
  - prompt length / cost tracker。
- 预计风险：
  - validation rollout 成本过高。
  - feedback function 设计不当导致反思方向错误。
  - Pareto frontier 对噪声样本过拟合。
  - merge/crossover 时机不稳定。
