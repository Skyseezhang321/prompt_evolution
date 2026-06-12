# Paper Note: GEPA / Reflective Prompt Evolution

论文：GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning

链接：https://arxiv.org/abs/2507.19457 （快照为 v2，2026-02-14 更新；ICLR 2026 Oral）

source_id：paper-gepa-2026

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：actionable-method（初读标 high-signal-extension，2026-06-12 按模板枚举归一；定位为本项目最值得复现的强 baseline）

阅读日期：2026-06-08（初读）；2026-06-12（深读复核）

reviewed_by：Codex（初读，method-and-results-read）；Claude（2026-06-12 复核全部主结果数字，补读附录 C–N）

local_pdf_path：`local_sources/raw/arxiv_papers/2507.19457/paper.pdf`

local_pdf_sha256：`AB3A5139BAC83F192AD67529368D77B84B0D807E95A8E4FD0DAA8D45FD046BEC`

local_text_path：`local_sources/raw/arxiv_papers/2507.19457/paper.txt`

local_text_sha256：`469E2EFC0A05B472AC78E1E02C164B50312A7DF237D5F67F9501A5E72BFC504B`

evidence_level：method-results-ablation-read（2026-06-12 第二轮：正文全读；附录 C meta-prompt、D merge 算法、E 实验配置、F–I 结果分析、N 反思调用计数逐项核验；Table 1/2/3/4 数字与正文声明逐一对过；附录 K/L 的完整 prompt 文本仅抽样阅读）

## 一句话结论

GEPA 的关键结论是：当系统执行轨迹、工具反馈、编译错误、rubric 失败原因等信息能被序列化成自然语言时，prompt 优化不必只依赖稀疏标量 reward；把这些诊断信号转成反思式 prompt mutation，并用 Pareto frontier 保留“对某些样本特别有效”的候选，可以在远少于 RL rollout 的预算下获得更强结果。

## 问题设定

- 任务：优化一个包含一个或多个 LLM prompt 的 compound AI system。
- 形式化：系统 Φ=(M, C, X, Y)，模块 M_i=(π_i, θ_i, X_i, Y_i)；可学习参数为 ⟨Π, Θ⟩，GEPA 只进化 prompt 集合 Π，权重 Θ 冻结；目标是 rollout 预算约束下最大化期望 metric（式 2，#rollouts ≤ B）。
- 优化对象：系统内各模块的自然语言 prompt；GEPA+Merge 还会在不同模块候选之间做 system-aware crossover。
- 反馈输入：训练样本、执行轨迹（execution trace：模块推理、工具调用）、评价轨迹（evaluation trace：评分器在折算成标量前产生的文本，如编译错误）、数值分数和可选的自然语言反馈（含人工评分解释）。
- 目标：在 rollout 预算受限时，提高验证/测试任务表现，尤其是多模块、工具调用、检索、数学和代码类 workflow。
- 对照对象：GRPO、MIPROv2（含 No-Demos 变体）、Trace/OptoPrime、TextGrad，以及贪心候选选择和 beam search 消融。

## 方法摘要

- 候选如何生成：选中当前候选系统的一个模块（轮询 round-robin），在 minibatch（实验中 b=3）上执行，收集 execution trace 和 evaluation trace，然后用 reflection LM 改写该模块 prompt。反思 meta-prompt（附录 C）是单一通用模板：给出当前指令、minibatch 的输入/输出/反馈，要求“识别所有 niche 与领域特定的事实信息写进新指令（因为这些信息以后不一定可得）”，并把模型用过的可泛化策略也固化进指令。
- 接受门槛：新候选先在同一 minibatch 上复评，分数提升才被加入候选池，并在 D_pareto 全量评估、记录祖先关系（Algorithm 1）。
- 反馈如何获得：`feedback function µ_f` 不只返回 scalar score，也返回自然语言 feedback_text，例如 compiler errors、failed rubrics、人工评分解释或模块级失败信息（多跳系统可逐 hop 给反馈）。
- 数据划分：D_train 拆成 D_feedback（产生反思信号）与 D_pareto（候选选择用）；实验中训练集作 D_feedback、验证集作 D_pareto（论文协议：优化器可跟踪验证分数，但不可见验证样本内容）。
- 如何选择候选：维护 D_pareto 上的候选×样本得分矩阵。对每个样本保留取得最高分的候选构成 Pareto frontier，剪掉被支配候选，再按候选出现在 frontier 的频次加权随机采样下一代父候选（Algorithm 2）。
- Merge / crossover（附录 D.1，Algorithm 3/4）：仅当两候选共享祖先、各自进化了互不相交的模块集合、且都优于该祖先时才触发；逐模块取“进化过的那一方”，双方都改过同一模块则取总分高者；同一 (i, j, ancestor) 组合不重复尝试；实验中 merge 最多调用 5 次。条件严格，触发稀疏。
- 是否使用记忆/archive：是。候选池保留多条 lineage，Pareto frontier 起到 diversity archive 的作用（作者引 MAP-Elites 式 illumination）。
- 是否优化 optimizer 自身：否。GEPA 优化 task/system prompts，但反思 meta-prompt 和候选选择算法本身是固定的。

## 实验设置

- 任务与切分（附录 E.1）：
  - HotpotQA：150/300/300（train/val/test），HoVer 多跳程序改最后一跳为答题；反馈=每个 stage 已检回/仍缺的 gold 文档集合（模块级）。
  - IFBench：train/val 用 IF-RLVR-Train（150/300），test 用 IFBench 294 条（58 个全新 OOD 约束）；2 段式系统（先答题再按约束改写）；反馈=满足与未满足的约束描述。
  - AIME-2025：2022–2024 共 90 题对半分 train/val，AIME-2025 30 题每题重复 5 次作 test；单步 CoT 系统。
  - LiveBench-Math：368 题（2025-07-30 截取），seed 0 打乱三等分；单步 CoT 系统。
  - HoVer：150/300/300；最多 3-hop、2 个 query writer + 2 个 summarizer；反馈同 HotpotQA。全参微调对照（Figure 11）用简化 2-hop 程序。
  - PUPA：111/111/221；PAPILLON 2 模块系统；反馈=质量分与 PII 泄漏分的分解。
- 模型与推理参数（E.2）：Qwen3 8B（temp 0.6 / top-p 0.95 / top-k 20）和 GPT-4.1 Mini（temp 1.0）；context 上限 16384。
- 预算对齐协议（E.4）：先跑 MIPROv2（auto=heavy：18 个 instruction 候选 + 18 套 few-shot），记录其每个 benchmark 实际消耗的 rollouts（2,270–6,926），再把 GEPA 的预算 cap 到同一数值（偏差 ≤10.15%）。主文对 Qwen3 8B 的 GRPO 固定 24,000 rollouts；GEPA 按任务 1,839–7,051，平均 3,936。
- GRPO 配置：compound 系统用 Ziems et al. 2025 的多模块 GRPO 实现；LoRA r=16、α=64、dropout 0.05，500 步 × group 12 × 每步 4 个训练实例 = 24,000 rollouts，每 20 步验证做 early stopping；作者手动探索过 LR/β/clipping。另有 2-hop HoVer 全参微调对照（FSDP2、group 16，Figure 11），相对差距与 LoRA 版相当。
- Trace/TextGrad 公平性：同一程序架构、同一数据切分、同一 metric 与反馈函数、与 MIPROv2/GEPA 同等 rollout 预算；Trace 框架不支持模块级反馈，按其官方 BigBench-Hard 教程格式给反馈。
- 反思调用次数（附录 N，Table 4）：整个优化过程 reflection LM 仅被调用 17–92 次（按任务/模型不同）。
- 成本（E.3）：GPT-4.1 Mini 上 Table 2 全部实验总成本低于 500 美元；GEPA 约 86 美元、GEPA+Merge 约 67 美元、MIPROv2 约 76 美元、Trace 与 TextGrad 合计约 172 美元。

## 主要结果

论文直接报告（2026-06-12 与 Table 1/2/3 逐项核对一致）：

- Qwen3 8B（Table 1）：GEPA aggregate 从 baseline 45.23 提升到 54.85，超过 GRPO 的 48.91 和 MIPROv2 的 47.84；GEPA 在 6 个任务里 5 个超过 GRPO（+19.0/+2.73/+13.66/+5.19/+0.7），但 AIME-2025 为 32.00，低于 GRPO 的 38.00。
- 口径提醒：摘要写对 GRPO “up to 20%”，Observation 1 正文写 “up to 19%”（按 Table 1 HotpotQA 62.33−43.33=+19.0）；GEPA+Merge 对 GRPO 最大差距 +21（64.33−43.33）。引用时建议直接用表格数字。
- GPT-4.1 Mini（Table 2）：GEPA aggregate 65.22、GEPA+Merge 66.36，超过 TextGrad 59.14、MIPROv2 58.67、MIPROv2-No-Demos 57.14、Trace 56.30（baseline 53.03）。
- 样本效率：GEPA 匹配 GRPO 最佳验证分数只需 243–1,179 rollouts（最多 78 倍效率）；若只计训练集 rollout（验证不算），达到最优只需 79–737 次，追平 GRPO 最佳验证分四个任务分别只要 102/32/6/179 次训练 rollout——学习信号的产生本身极便宜，预算大头是候选验证。IFBench 上 678 个 rollouts 即找到最优 prompt（38.61，对 GRPO 24,000 rollouts 的 35.88）。
- 跨模型迁移：GEPA-Qwen-Opt 只用 Qwen3 8B 优化 prompt，原样迁移到 GPT-4.1 Mini，aggregate improvement +9.00（HotpotQA 最高 +27.67），高于直接在 GPT-4.1 Mini 上优化的 MIPROv2（+5.64）、TextGrad（+6.11）、Trace（+3.27）。
- 候选选择消融（Table 3，Qwen3 8B 四任务）：aggregate improvement——SelectBestCandidate（TextGrad 式贪心）+6.05、BeamSearch（N=4，APO/ProTeGi 式）+5.11、GEPA Pareto +12.44；单任务上 Pareto 比 beam 最多高 11.33、比贪心最多高 8.17。Figure 6 显示贪心在第一个子节点后即陷入局部最优。
- 泛化差距（Figure 16，对 Wan et al. 2024 结论的更新）：GEPA 的 val→test 回落不劣于 MIPROv2，如 HotpotQA GPT-4.1 Mini 上 GEPA +0.67%（测试反超验证）vs MIPROv2 −4.33%——在现代模型上，反思进化出的 instruction 不再比 few-shot demo 更易过拟合。
- Prompt 长度（Figure 17/18）：aggregate 上 GEPA 的 prompt 约为 MIPROv2 的 1/4.3–1/4.9，单任务最高短 9.2 倍（PUPA, Qwen3 8B）；更高分的 optimizer 总体产出更短 prompt。注意：附录 I 正文写 “33% shorter”，Figure 17 caption 写 “less than 33% of the size”，二者矛盾，按 Figure 18 数字应取后者口径（约为其 1/3 以下）。
- 单次反思更新即可大幅提分（Figure 5，PUPA 轨迹）：82.26 → 90.99 仅一步；最优候选 97.6。
- 扩展实验（论文自标 preliminary）：
  - NPUEval（GPT-4o，inference-time search 用法，trainset=待解任务全集、刻意过拟合）：Sequential10 4.25% → +RAG 16.33% → +RAG+MIPROv2 19.03% → GEPA 单 prompt 26.85%（无需运行时 RAG）/ Pareto 30.52%，个别 kernel 向量利用率 70%。µ_f 按编译错误检索技术手册片段注入反馈。
  - KernelBench（35 题代表子集，GPT-4o + Sequential5）：fast_1 从接近 0% 提到 20% 以上。
  - 对抗 prompt 搜索（GPT-5 Mini）：反转 reward 后进化出“通用 trivia 干扰 + 严格格式指令”的前缀，使 AIME-2025 pass@1 从 76% 降到 10%；失败模式是模型大量输出字面占位符 `### <final answer>`。

## 失败案例和局限

论文直接或间接暴露：

- GEPA+Merge 在 GPT-4.1 Mini 上有效，但在 Qwen3 8B 上整体劣化，IFBench 上 28.23 甚至跌破 baseline 36.90（负优化，不只是不如 GEPA）；作者归因于 mutation/crossover 预算分配与 merge 触发时机用了与 GPT-4.1 Mini 相同的固定超参，提出自适应调度作为 future work。
- Qwen3 8B 的 AIME-2025 上，GEPA/GEPA+Merge 为 32.00，低于 GRPO 的 38.00，说明反思式 prompt evolution 不是所有任务都替代 RL。同表中 MIPROv2 在该任务为 20.00、低于 baseline 27.33——few-shot demo 优化在小模型数学题上同样可能负优化。
- GEPA 的 rollout 预算大部分花在验证候选上（产生学习信号的训练 rollout 仅 79–737）；作者提出更小验证集或动态验证子集两个方向，均未实验验证。
- 扩展到 inference-time code search 和 adversarial prompt search 的结果很强，但作者明确称这些是 preliminary findings；且该用法是对任务集的刻意过拟合，不能与主实验的泛化设定混读。
- 该方法依赖 evaluation trace/feedback function 的质量；当评价过程只能给一个标量分数，优势可能收窄。
- our-inference（论文未直接讨论）：Pareto 选择按 per-instance 验证分数运作，对验证集信号的使用粒度远重于常规 early stopping，理论上有验证集过拟合风险。Figure 16 的泛化差距分析显示实测回落不大，部分缓解该担忧；但 D_pareto≈300 条的设置缩小后结论是否保持，论文未报告。
- 对抗实验既是方法能力展示，也是 instruction-following 脆弱性的证据：无害 trivia + 严格格式指令的组合即可让前沿模型崩到 10%，提示我们自己的优化 prompt 也应做这类扰动回归测试。

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
  table_or_figure: "Table 2, Figure 16, Figure 17, Figure 18"
  quote_or_paraphrase: "GEPA 在 GPT-4.1 Mini 上超过 MIPROv2，并产生更短的 prompt；泛化差距分析显示反思进化的 instruction 回落不劣于 demo；作者认为现代 LLM 的 instruction-following/self-reflection 能力改变了 instruction vs demo 的权衡。"
mechanism: 高质量规则能覆盖一组失败模式，而 few-shot demo 增长快、成本高，且可能过拟合示例表面形式。
actionable_rule: 不应默认把 prompt 优化预算先花在 few-shot 选择；先试 instruction-only reflective optimization，再决定是否加 demos。
counterexample_or_limit: 对格式高度依赖或低样本任务，few-shot 仍可能是必要约束。
minimal_experiment: instruction-only GEPA-style rewrite vs demo-only retrieval vs instruction+demo combined。
confidence: medium-high
```

```yaml
insight: 反思式优化的成本结构是“学习信号便宜、验证昂贵”，优化预算应优先花在验证策略设计上。
evidence_type: direct-result
paper_evidence:
  section: "Observation 1, Appendix N"
  table_or_figure: "Table 4（reflection 调用 17–92 次）；Observation 1（train-only rollouts 79–737；追平 GRPO 只需 102/32/6/179 次训练 rollout）"
  quote_or_paraphrase: "GEPA 的 rollout 预算大部分花在验证候选上，分数只用于候选选择、不产生学习信号；整个优化过程反思 LM 只被调用几十次。"
mechanism: 反思式更新每次只消耗一个 minibatch（b=3）的 trace 加一次反思调用；而每个被接受的候选都要在全量 D_pareto 上评估，验证成本随接受候选数线性增长。
actionable_rule: 复现时把训练信号 rollout、验证 rollout、反思调用三类成本分开记账；缩小或动态化验证集的边际收益可能大于改进反思质量。
counterexample_or_limit: 动态验证子集是论文自提的 future work，未做实验；验证集太小会让 Pareto frontier 对噪声样本过拟合。
minimal_experiment: 固定反思流程，比较 D_pareto=300 / 100 / 动态子集三种设置的最终测试分与总 rollout 数。
confidence: high（成本结构为直接报告）；medium（改进方向未经验证）
```

```yaml
insight: feedback function 可以是注入领域知识的运行时通道，而不只是评分器。
evidence_type: direct-result（作者自标 preliminary）
paper_evidence:
  section: "5.1"
  table_or_figure: "Figure 7（NPUEval 4.25%→30.52%）, Figure 27"
  quote_or_paraphrase: "µ_f 根据 rollout 失败（如编译错误）定向检索技术手册章节并随反馈返回；GEPA 进化出的单一 prompt 让同一 agent 无需运行时 RAG 达到 26.85%。"
mechanism: 错误信息驱动的定向检索把外部文档变成反思素材，进化把检索到的知识固化进 prompt——相当于把 RAG 的运行时成本一次性摊销到优化期。
actionable_rule: 设计 µ_f 时考虑三层：分数、失败解释、按失败检索的领域材料；领域手册/规范文档可以经 µ_f 进入优化循环。
counterexample_or_limit: 该用法属 inference-time search（trainset=待解任务全集、刻意过拟合），不能直接推广到泛化设定；作者明确称需系统研究。
minimal_experiment: 同一代码生成任务，比较 µ_f=score-only vs +error text vs +error-driven doc retrieval 三种反馈的进化曲线。
confidence: medium
```

## 对本项目的启发

> 类型标注按 `docs/insight_field_standard.md`。

- （helpful method）我们的 eval 设计要先升级日志结构：每个失败样本都应保存 `execution_trace`、`evaluation_trace`、`feedback_text`、`module_name`、`candidate_id`。
- （helpful method）GEPA 的预算对齐协议可直接抄作我们对照实验的公平性模板：先跑基线 optimizer 记录其实际 rollouts，再把新方法 cap 到同一预算（论文做到偏差 ≤10.15%）。
- （conclusion，证据 A，scope=trace 丰富的多模块任务）第一批实验不要直接做 RL 对照；更务实的是做 score-only vs trace-aware 的 prompt evolution 对照。
- （helpful method）candidate archive 必须是矩阵化的，至少能回答“这个 prompt 解决了哪些样本、牺牲了哪些样本”。
- （helpful method）成本记账分三类：训练信号 rollout、验证 rollout、反思调用——GEPA 的数据说明三者量级差异巨大（79–737 vs 数千 vs 17–92）。
- （conclusion，证据 A）反思式优化如果要进入生产，需要记录 prompt 长度和 inference 成本；GEPA 把 prompt compactness 作为重要实用结果，这点值得纳入指标。
- （anti-pattern）固定 merge/crossover 超参跨模型硬套：GPT-4.1 Mini 上 +1.14 aggregate 的同一配置在 Qwen3 8B IFBench 上跌破 baseline。
- （anti-pattern）把 GEPA 的 inference-time search 结果（NPUEval/KernelBench）当泛化能力证据引用——那是对任务集的刻意过拟合用法。
- （待验证 hypothesis，our-inference）per-instance 验证分数驱动的 Pareto 选择存在验证集过拟合风险，验证集缩小时尤甚；我们复现时应同时记录 val/test 差距随 D_pareto 大小的变化。

## 可复现计划

- 最小复现任务：结构化抽取或 judge prompt，100-300 条样本，有 per-row parser/rubric error。
- 关键超参（按论文实验配置）：minibatch b=3；接受门槛=minibatch 提升才进池+全量 D_pareto 评估；module 选择轮询；merge 默认关闭（论文中其收益模型相关且可能负优化）。
- 需要实现的模块：
  - trace-rich evaluator（三层反馈：分数 / 失败解释 / 可选领域材料）。
  - reflection mutation prompt（可先抄附录 C 通用模板）。
  - candidate-by-example score table。
  - Pareto parent selector（按 frontier 出现频次加权采样）。
  - prompt length / cost tracker（三类成本分账）。
- 预计风险：
  - validation rollout 成本过高（GEPA 预算大头即在此）。
  - feedback function 设计不当导致反思方向错误。
  - Pareto frontier 对噪声样本过拟合（验证集小时尤甚）。
  - merge/crossover 时机不稳定（论文已实证跨模型不可硬套）。
