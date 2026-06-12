# Paper Note: PromptAgent / Strategic Planning with Language Models Enables Expert-level Prompt Optimization

论文：PromptAgent: Strategic Planning with Language Models Enables Expert-level Prompt Optimization

链接：https://arxiv.org/abs/2310.16427

source_id：paper-promptagent-2023

关联 issue：无

线索贡献者：主线结构评审（2026-06-12 检验"APO 七法主线是否缺失规划搜索分支"时定向补读；此前全仓库仅在 [[paper-teach-better-show-smarter-2024]] 的对比方法列表中出现过一次，未登记）

新颖性判断：extension

阅读日期：2026-06-12

reviewed_by：Claude

local_pdf_path：`local_sources/raw/arxiv_papers/2310.16427/paper.pdf`

local_pdf_sha256：`0E386889C321A4498A92D7B074FB8A9888A4606B8434CE3307568392CF9297AD`

local_text_path：`local_sources/raw/arxiv_papers/2310.16427/paper.txt`

local_text_sha256：`C212B27B7D2CB714441018B5EA3A0ACC5062FEB8B245F52CBA4D60C01FCAB014`

evidence_level：method-and-results-read（精读正文方法、全部主结果表 Table 1–4、Figure 4–5 与附录 A 实现细节/数据切分/meta-prompt；附录 C 收敛图与附录 D 各任务 prompt 样例仅略读）

## 一句话结论

PromptAgent 把 prompt 优化重构成 MDP + MCTS 策略规划问题（状态=prompt 版本、动作=从 base model 错误生成的自然语言反馈），在 12 任务上平均超 APE 7%–11%，且搜索消融显示**同等探索量下 MCTS 显著优于 beam/greedy/MC**——这证明"搜索结构"是独立于"反馈信号形式"的第二个演进维度，是 ProTeGi（beam）与 GEPA（Pareto 候选池）之间被本仓库主线漏掉的一环。

## 问题设定

- 任务：12 个任务跨三域——6 个 BBH（Penguins、Geometric Shapes、Epistemic、Object Counting、Temporal、Causal Judgement）、3 个生物医学（NCBI 疾病 NER、Biosses 句子相似度、MedQA）、3 个通用 NLU（Subj、TREC、CB）。
- 优化对象：zero-shot 自然语言 task prompt（论文显式声明 prompt 不含训练样例）；目标是自动产出含领域知识、解题指引、例外处理的"专家级"长 prompt。
- 目标指标：accuracy（NCBI 为 F1）。
- 约束：黑盒 API；不访问梯度或内部状态。

## 方法摘要

- 候选如何生成：把优化过程建模为 MDP (S, A, T, r)。每步两段式：(1) 采训练 minibatch（batch size 5）收集 base model 错误样本，用 meta-prompt 1 让 optimizer 总结失败原因，生成 error feedback（即动作）；(2) meta-prompt 2 接收当前 prompt + 错误样本 + error feedback + **当前路径上的 prompt 轨迹**，生成新 prompt（即新状态）。
- 反馈如何获得：失败样本 + LLM 对失败的自然语言反思——属 critique 信号家族（不是完整执行轨迹；单步任务也没有多模块 trace 可收）。
- 如何选择候选：MCTS 四操作——UCT 选择（exploration weight c=2.5）、扩展（expand_width=3 批 × num_samples=1–2 个新 prompt）、模拟（迭代贪心扩展至终态，代替随机 playout）、回传（Q = 该节点起全部未来轨迹累计奖励的平均，公式 2）。共 12 次 MCTS 迭代；奖励 = 训练集内分出的 held-out 子集（默认 150 条，按训练集大小在 60–200 浮动）上的任务表现。深度 >2 后早停：节点奖励低于父节点与根节点均值、或高于当前全局最大值即停。最终输出 = 平均奖励最高路径中奖励最高的节点。
- 是否使用记忆/archive：搜索树本身保留全部状态-动作-奖励（树即 archive，支持回溯）；无跨任务记忆。
- 是否优化 optimizer 自身：否，两个 meta-prompt 静态。

## 实验设置

- 数据集：12 任务，切分见论文 Table 6（如 NCBI 2000 train / 940 test、Epistemic 500/500、CB 125/56）。
- 模型：base = GPT-3.5（temperature 0），optimizer = GPT-4（temperature 1.0）；迁移实验把优化好的 prompt 直接搬到 GPT-4 与 PaLM 2（chat-bison-001）。
- baselines：Human ZS/FS、CoT（ZS = "Let's think step by step"；few-shot 用 Suzgun et al. 原版）、GPT Agent（ChatGPT 插件 AI Agents + GPT-4，类似迭代次数）、APE（initial 100 候选 + iterative 50 候选）。
- train/dev/test 切分：有官方测试集用官方（>1000 抽 1000）；无则对半分；reward 用训练集内 held-out 子集，测试集只做最终报告。
- 成本或调用次数：未报告 token / 美元成本与运行时间；探索效率以"探索过的 prompt 节点数"度量——PromptAgent 数十个节点 vs Greedy-S 34、Greedy-L 72、APE 150。

## 主要结果

论文直接报告：

- BBH 6 任务平均：PromptAgent 0.802 vs APE 0.690、CoT(few-shot) 0.707、Human ZS 0.513（相对提升 11.2% / 9.5% / 28.9%）；5/6 任务最高，Object Counting 输给 few-shot CoT（0.860 vs 0.960）。
- 生物医学 3 任务平均 0.655 vs APE 0.582（+7.3%）；通用 NLU 平均 0.868 vs APE 0.778（+9%）、vs CoT +16.9%。
- 跨模型迁移（Table 3）：GPT-3.5 上优化的 prompt 迁到 GPT-4 后 11/12 任务持平或胜过 Human/APE（平均 0.839 vs 0.759/0.762）；迁到 PaLM 2 全任务大幅掉分，但仍 7/12 任务胜 baseline（平均 0.441 vs 0.392/0.381），领域任务（NCBI 0.177 vs 0.016/0.025）收益最明显。
- 搜索结构消融（Table 4，5 任务，控制同等探索量）：MCTS 0.754 > Greedy 0.698 ≈ Beam 0.697 > 单步 MC 0.635；MCTS 相对最佳对照 +5.6%。**候选生成与反馈完全相同，只换搜索算法**——这是干净的单变量消融。
- 探索效率（Figure 4a）：PromptAgent 以更少探索节点取得更高准确率（图上聚于左上角）；Greedy 从 34 节点加到 72 节点有提升但仍不及 MCTS。
- 收敛（Figure 4b，Epistemic）：train 与 test 路径曲线都在深度 3 左右趋稳且彼此接近。
- 质性（Figure 5，NCBI）：最优路径 0.521 → 0.622 → 0.609 → 0.645，逐步注入"排除基因/蛋白/位点""locus 是基因组位置不是疾病名"等领域规则；产出 prompt 显著长于 human/APE 版本。

## 失败案例和局限

论文直接报告：

- 迁移到弱模型 PaLM 2 时全任务表现大幅下降——作者明确说弱模型"可能无法领会专家级 prompt 的微妙之处"。专家级长 prompt 高度依赖 base model 理解力。
- Object Counting 上输给 few-shot CoT（该任务最受益于逐步推理格式）。
- 作者承认专家 prompt 更长更复杂，提及未来可能需要 prompt 压缩（引 LLMLingua）。

论文未报告（不替它补）：

- token / 美元成本、运行时长。
- 多模块程序、agent、开放生成任务上的表现——全部 12 任务是单步分类/抽取/QA。
- optimizer 用弱模型（非 GPT-4）时是否仍有效。

## 洞见卡片

```yaml
insight: 搜索结构是独立于反馈信号形式的演进维度；同等探索量下"能前瞻+回溯"的树搜索显著优于只向前的 beam/greedy。
evidence_type: ablation
paper_evidence:
  section: "4.2 Ablation on search strategies"
  table_or_figure: "Table 4, Figure 4a"
  quote_or_paraphrase: "相同的动作生成与状态转移，只换搜索算法：MCTS 0.754 vs Greedy 0.698 / Beam 0.697 / MC 0.635；同时 MCTS 用更少探索节点。"
mechanism: prompt 空间的单步改写收益高方差，前瞻模拟+Q 值回传允许放弃看似好的局部路径、回到早期节点重新分支；beam/greedy 无法回溯。
actionable_rule: 评价或设计 optimizer 时，把"探索候选数"作为预算轴单独报告；对比实验应将 search structure 与 feedback signal 分开消融，不可混称"LLM 反思有效"。
counterexample_or_limit: 消融仅 5 个单步任务；MCTS 在多模块程序上未验证；GEPA 后来在程序级场景用 Pareto 池而非 MCTS。
minimal_experiment: 固定候选生成与反馈（critique 式），等预算比较 MC / beam / MCTS 三种搜索结构。
confidence: high（单 prompt 分类/抽取任务范围内）
```

```yaml
insight: 错误反馈榨出的"专家级长 prompt"是 model-specific 资产，向弱模型迁移会大幅掉价。
evidence_type: direct-result
paper_evidence:
  section: "4.2 Prompt generalization"
  table_or_figure: "Table 3"
  quote_or_paraphrase: "GPT-3.5 优化的 prompt 迁到 GPT-4 进一步提升（11/12 胜），迁到 PaLM 2 全任务大幅下降（仍 7/12 胜 baseline）。"
mechanism: 专家级 prompt 依赖 base model 对细密指令的解析能力；弱模型读不懂长指令反而被干扰。
actionable_rule: prompt 资产迁移到任何新模型前必须重新评测；与 [[paper-opro-2023]] 的"最佳 prompt 是 model-specific 钥匙短语"互证。
counterexample_or_limit: 向更强模型迁移基本无损甚至增益——掉价主要发生在向下迁移。
minimal_experiment: 同一优化 prompt 在强/弱两档目标模型上对比 baseline 差值。
confidence: high
```

```yaml
insight: （our-inference）critique 线的搜索结构存在 beam→MCTS→Pareto 池的独立演进，本仓库主线 ProTeGi→GEPA 之间缺这一环。
evidence_type: our-inference
paper_evidence:
  section: "2 Related Works; 4.2 Ablation"
  table_or_figure: "Table 4（本文）+ GEPA 论文消融（Pareto +12.44 vs greedy +6.05 / beam +5.11，见 [[paper-gepa-2026]]）"
  quote_or_paraphrase: "本文自称'首次把策略规划引入 prompt 优化'；其 Table 4 与 GEPA 消融形成跨论文互证：选择/搜索结构的贡献可以不小于反馈信号形式。"
mechanism: 两篇论文各自的单变量消融都指向同一结论——候选怎么选（树/池结构）独立贡献大幅收益。
actionable_rule: 主线叙事在"两条暗线"（反馈密度、对象升维）之外应补第三条：搜索结构（盲采样→beam→MCTS 规划→Pareto 池）。
counterexample_or_limit: 这是跨论文综合推断，两文任务设置不同，不可横比数字本身。
minimal_experiment: 同任务同反馈下 beam vs MCTS vs Pareto 池三臂对比（即把本文 Table 4 延伸一臂）。
confidence: medium
```

## 对本项目的启发

> 字段定义与 insight / conclusion / helpful method 的区分口径见 `docs/insight_field_standard.md`。

- insight：见上方三张洞见卡片；核心是"搜索结构是独立演进维度"。
- conclusion：无（单篇论文不出 conclusion）。
- helpful method：MCTS 预算口径可直接借用——12 次迭代、UCT c=2.5、depth 8/6/4 三档、expand_width 3；以及"深度 >2 后，奖励低于父/根均值即早停"的剪枝规则（廉价、无需额外调用）。
- anti-pattern / limit：把"探索更多候选"当提升手段——APE 探索 150 个候选不及 MCTS 的数十个（Figure 4a）；与 [[paper-gepa-2026]] "大部分 rollout 花在验证而非学习信号"互证。
- 适用场景：有领域知识缺口的单 prompt 任务（生物医学 NER 这类需要术语澄清/例外处理规则的任务收益最大）。
- 误用风险：把专家级长 prompt 直接搬到弱模型；把单步分类任务结论外推到多模块程序/agent；把"MCTS 赢了"误读为反馈信号不重要（本文反馈与 ProTeGi 同族，赢在搜索）。

## 最小验证或演示计划

- 要验证的 insight / method：搜索结构独立贡献（洞见卡 1/3）。
- 最小验证任务：本项目意图抽取最小任务（与 ProTeGi 复现共用数据）。
- 需要实现的模块：搜索树 + UCT 选择 + 早停剪枝（候选生成与 critique 模块复用 ProTeGi 复现件）。
- 观察指标：held-out 准确率、train-test gap、探索节点数（预算轴）。
- 预计风险：单任务结论不稳定；MCTS 实现复杂度高于 beam；GPT-4 级 optimizer 成本。
