# Paper Note: MIPRO / Optimizing Instructions and Demonstrations for Multi-Stage LM Programs

论文：Optimizing Instructions and Demonstrations for Multi-Stage Language Model Programs（提出 MIPRO；DSPy 实现中称 MIPROv2）

链接：https://arxiv.org/abs/2406.11695

source_id：paper-miprov2-2024

关联 issue：无

线索贡献者：internal-arxiv-search（经典锚点补读）

新颖性判断：duplicate-but-foundational-baseline（DSPy 的 instruction+demo 联合优化器，GEPA/SPEAR 等的主要对照 baseline）

阅读日期：2026-06-10

reviewed_by：Claude

local_pdf_path：`local_sources/raw/arxiv_papers/2406.11695/paper.pdf`

local_pdf_sha256：`F00093AF256C7B3E5168C2E98FBB8C4847232A8838C91BAAD4540CB4F19C91F7`

local_text_path：`local_sources/raw/arxiv_papers/2406.11695/paper.txt`

local_text_sha256：`4B3FF3CB3019D74549885DD405F4F3AAB9200616E3B9AD56ACC441DB025B5D08`

evidence_level：method-and-results-read（读了问题形式化、proposal/credit-assignment 三×三策略、MIPRO 及变体、7 任务 benchmark 主表 Table 2、5 条 lesson 和 limitations；部分附录预算/重要性分数略读）

版本说明：本地 PDF 为 v2（2024-10-06）。论文方法名为 MIPRO，DSPy 库里对应 `MIPROv2`，本项目 inventory 用 `paper-miprov2-2024`。

## 一句话结论

MIPRO 把 [[paper-dspy-2023]] 没解决的"多阶段 LM program 里 **instruction** 怎么自动优化"补上，并把问题干净地形式化为两个挑战：(1) **proposal**——prompt 空间太大，怎么采到少量高质量候选；(2) **credit assignment**——只有 program 级 metric、没有 module 级标签，怎么把功劳/过错分到各 module。它的答案是"bootstrap demonstration + grounded instruction proposal + 贝叶斯(TPE) 在 mini-batch 上联合搜索"。最重要的实证结论对本项目是一记定调：**在多数任务上，优化 bootstrapped demonstration 比优化 instruction 更管用；instruction 优化只在'有不显然、又无法靠少量样例表达的条件规则'的任务上才是决定性的**——而联合优化(MIPRO)在 7 个任务里 5 个最好。

## 问题设定

- 任务：优化任意多阶段 LM program 的 prompt（多跳检索 QA、分类、NLI、claim 验证等）。
- 优化对象：每个 module 的 **free-form instruction + few-shot demonstration**（弱假设：无 module 级标签、无梯度、无 logprob、只有 program 和一个 metric + 训练输入）。
- 目标指标：任意 program 级 metric（EM、accuracy、Recall@21、custom）。
- 约束：proposal 候选要少而精；credit assignment 不能依赖中间标签。

## 方法摘要（3 proposal × 3 credit-assignment）

- 候选如何生成（proposal）：
  1. **Bootstrap demonstrations**：训练输入跑过 program，保留 metric 达标的 trace，把各 module 的 input/output 当候选 demo（DSPy 的 rejection sampling）。
  2. **Grounding**：构造一个 zero-shot program 给 proposer LM 喂"数据集模式摘要 + program 控制流摘要 + bootstrapped demo + 历史 instruction 及其分数"，让它写出 task-grounded instruction。
  3. **Learning to propose**：把 proposal 的超参（温度、是否给 data/program summary、给哪条 tip、给哪组 demo）参数化，用贝叶斯模型跨 trial 学最优 proposal 策略。
- 如何选择候选（credit assignment）：
  1. **Greedy**：一次只改一个 module——能避免错误归因，但低效且"某 module 不先改好别的就看不出收益"；实验里性价比差。
  2. **Surrogate（MIPRO 采用）**：用 Optuna 的 TPE 建贝叶斯代理模型，预测"instruction×demo 组合"的质量，在 **mini-batch** 上评估更新先验；贝叶斯对噪声鲁棒。缺点：只能在固定候选集里选，不能改进候选本身。
  3. **History-based**：让足够强的 proposer LM 从历史评估里同时做 credit assignment 和提新 instruction（OPRO 式，Module-Level / Program-Level）。
- 反馈如何获得：program 级 metric 分数（mini-batch 估计 + 周期性全训练集评估）。
- 是否使用记忆/archive：贝叶斯代理模型的历史 trial 充当隐式 archive；保留最高分参数化。
- 是否优化 optimizer 自身：MIPRO++ 是——它 meta-optimize proposal 策略的超参（把"怎么提 proposal"也纳入贝叶斯搜索）。
- 关键变体：**0-Shot MIPRO**（只优化 instruction）、**Bayesian Bootstrap**（只优化 demo）、**MIPRO++ / 0-Shot MIPRO++**（meta-optimize proposal 超参）。

## 实验设置

- 数据集/程序（7 个，Table 1）：ScoNe(NLI/CoT)、HotPotQA(多跳检索, 2 module/3 调用)、HoVer(4-hop claim 验证, Recall@21)、HotPotQA Conditional(按答案类型改格式的条件规则任务)、Iris(分类/CoT)、Iris-Typo(seed prompt 带拼写错)、Heart Disease(分类/answer ensemble)。
- 切分：500 train / 500 dev / 2k test。
- 模型：proposer LM = GPT-3.5（温度 0.7，写 instruction）；task LM = **Llama-3-8B**（program 内执行）；bootstrap teacher 默认 Llama-3-8B，难任务(ScoNe/HoVer)换 GPT-4o。
- baselines：未优化 program；instruction-only(Module-Level OPRO ±Grounding, 0-Shot MIPRO/++)；demo-only(Bootstrap RS, Bayesian Bootstrap)；joint(MIPRO)。
- 预算/统计：每任务 20–50 trials（mini-batch 实际 trial 更多），每法每任务 5 次运行，Wilcoxon signed-rank 检验显著性。

## 主要结果

论文直接报告（Table 2，test，5 次平均；摘要：5/7 任务超 baseline，最高 +13%）：

- **Lesson 1 — demo 优化通常胜过 instruction 优化**：Bootstrap RS 在除 HotPotQA Conditional 外所有任务都打败"最佳 instruction-only optimizer"（Wilcoxon 显著）。强 demo 传递的是"成功推理行为"，不只是任务格式（不同 demo 集表现方差很大）。
- **Lesson 2 — 联合优化(MIPRO)总体最好**：7 任务里 5 个 MIPRO 最优（如 ScoNe 79.4、HotPotQA 46.4、HoVer 39.0、HotPotQA Cond 28.1、Iris 88.6）。例外 HotPotQA、Heart Disease、Iris-no-typo。
- **Lesson 3 — instruction 优化在"条件规则不显然且无法靠少量样例表达"的任务上是决定性的**：HotPotQA Conditional、Iris-Typo 上，连 0-shot instruction 优化都超过 demo-only；instruction optimizer 甚至能修正 seed prompt 里的拼写错。
- **Lesson 4 — grounding 总体有益但最优策略因任务而异**：grounding 对 HotPotQA/HoVer 是必要的，却伤害 ScoNe；MIPRO++ 能学到任务专属 proposal 策略救回 ScoNe。贝叶斯重要性分数显示：**meta-prompt 里的 bootstrapped demo 选择和那条"tip"重要性最高**，data summary 的重要性因任务大幅波动。
- **Lesson 5 — optimizer 排名依赖预算**：Module-Level OPRO / 0-Shot MIPRO / MIPRO++ 互有胜负；mini-batch 的 0-Shot MIPRO 可能在低预算占优，MIPRO++ 可能在高预算占优。

## 失败案例和局限

- **optimizer 推不出复杂任务规则**：没有手写 seed prompt 时，instruction optimizer 无法从 grounding 里推全条件规则（Heart Disease 用无判据的 seed 就吃亏）。这是本版的硬限制——"自动化"仍依赖人给的规则种子。
- **固定预算、未扫低/高预算**：optimizer 之间的取舍随预算变，本文只在固定预算下比，结论有预算依赖性。
- **固定 proposer + task LM，跨模型未验证**：明确列为 limitation；换模型是否稳定未知。
- **demo 集高方差**：bootstrapped demo 的好坏波动大，选错 demo 集会明显掉分（Appendix G）——"自举不等于稳定"。
- **credit assignment 仍是近似**：greedy 低效、surrogate 只能在固定候选里选、history-based 依赖"足够强的 proposer LM 能从长历史里正确分配 credit"（长历史信息易丢失）。三者都没真正解决 module 级归因。
- **Program-Level OPRO 不如 Module-Level**：把整条多阶段轨迹丢给 LM 让它自己分 credit，复杂且无额外收益——长轨迹里信息丢失。

## 洞见卡片

```yaml
insight: 多数任务上"优化示例"比"优化指令"更管用；指令优化只在特定条件下决定性。
evidence_type: direct-result + ablation
paper_evidence:
  section: "6 (Lessons 1-3)"
  table_or_figure: "Table 2"
  quote_or_paraphrase: "Bootstrap RS 在除 HotPotQA Conditional 外全部任务打败最佳 instruction-only；instruction 优化只在'条件规则不显然且无法靠少量样例表达'时(HotPotQA Cond/Iris-Typo)胜出。"
mechanism: demo 直接示范成功推理行为；instruction 在规则无法被样例覆盖时才提供不可替代的信息。
actionable_rule: 选优化策略前先判任务类型——格式/行为类先试 demo 优化；含隐藏条件规则的先试 instruction 优化；默认跑联合(MIPRO)。与 [[paper-teach-better-show-smarter-2024]]、[[paper-textgrad-2024]] 互补性结论一致。
counterexample_or_limit: HotPotQA 这类最终模块 in-distribution 的简单 QA，instruction 优化收益低。
minimal_experiment: 同任务跑 instruction-only / demo-only / joint 三格，并按"是否含隐藏条件规则"分层看哪格赢。
confidence: high
```

```yaml
insight: 把 credit assignment 与 proposal 解耦，用贝叶斯代理在 mini-batch 上选组合，是对噪声鲁棒的多阶段优化骨架。
evidence_type: direct-method
paper_evidence:
  section: "3.2, 4.3"
  table_or_figure: "Figure 4"
  quote_or_paraphrase: "MIPRO 用 TPE 贝叶斯模型在 mini-batch 上学 instruction×demo 组合的质量，proposer 只管提候选，credit assignment 交给代理模型。"
mechanism: 贝叶斯把不确定性纳入搜索，mini-batch 降单次评估成本，让有限预算探索更多组合。
actionable_rule: 本项目多组件优化默认"proposal 与 selection 分离 + mini-batch 代理评估 + 周期性全集复核"，而不是让一个 LM 一次性既改又选（对照 OPRO 的纯 history-based [[paper-opro-2023]]）。
counterexample_or_limit: 代理只能在固定候选集里选，无法改进候选本身；小验证集下仍会过拟合。
minimal_experiment: 同候选集下比较 greedy / 贝叶斯代理 / history-based 三种选择的样本效率与最终测试分。
confidence: high
```

```yaml
insight: 自动 instruction 优化器仍推不出复杂任务的隐藏规则，需要人写 seed prompt。
evidence_type: direct-result + author-claim
paper_evidence:
  section: "6 (Lesson 3), Limitations"
  table_or_figure: "Table 2 (Heart Disease, HotPotQA Cond)"
  quote_or_paraphrase: "缺判据 seed 的 Heart Disease 上 instruction 优化吃亏；作者明言 optimizer 无法仅靠 grounding 推全任务规则。"
mechanism: grounding 提供数据/程序线索，但不足以外推一套完整条件规则；规则仍需人注入。
actionable_rule: 本项目把"业务规则/约束"当人写不可自动改写层(对齐 H3)，optimizer 只在其上做措辞与示例优化；不要指望 optimizer 凭空补规则。
counterexample_or_limit: 规则可由少量样例表达时，demo 自举即可，无需人写规则。
minimal_experiment: 同任务对比"有判据 seed + 优化"vs"空 seed + 优化"，量化人写规则的边际贡献。
confidence: high
```

## 对本项目的启发

> 字段定义与 insight / conclusion / helpful method 的区分口径见 `docs/insight_field_standard.md`。

- conclusion：MIPRO 是 instruction+demo **联合优化的基线锚点**，并给出本项目可直接采信的分诊规则——多数任务 demo 优化更强，instruction 优化只在隐藏条件规则任务上决定性，联合最稳(5/7)。但 optimizer 推不出规则、跨模型未验证、demo 高方差。
- helpful method：把"bootstrap demo + grounded instruction proposal + 贝叶斯 mini-batch 选择"作为多组件 optimizer 的标准骨架；并把 proposal↔selection 解耦当默认工程结构。
- anti-pattern / limit：默认"优化 prompt = 改 instruction"（多数任务该先优化 demo）；指望 optimizer 凭 grounding 补全业务规则；用单一 dev 全量评估而不 mini-batch（浪费预算）。
- 适用场景：DSPy 式多阶段 program、有 program 级 metric、无 module 级标签、想在有限预算下联合调 instruction+demo。
- 误用风险：忽略 demo 集高方差直接上线；跨模型迁移不重测；小 dev 选择过拟合（[[paper-coin-flip-2026]]）。

## 最小验证或演示计划

- 要验证的 insight / method：分诊规则（按"是否含隐藏条件规则"决定先优化 instruction 还是 demo），以及 proposal↔selection 解耦骨架。
- 最小验证任务：一个"含隐藏条件规则"的结构化任务（仿 HotPotQA Conditional）+ 一个"格式/行为类"任务，各 300–500 样本。
- 需要实现的模块：(1) bootstrap demo（trace 过滤）；(2) grounded instruction proposer；(3) TPE/贝叶斯 mini-batch 选择器；(4) instruction-only / demo-only / joint 三格 + 5 次运行 + 显著性检验。
- 观察指标：各格 test 分与显著性、demo 集方差、达到目标分的 trial 数、跨模型迁移 delta、train-dev-test gap。
- 预计风险：demo 高方差需多 seed；贝叶斯在小 mini-batch 上不稳；缺判据 seed 时 instruction 优化无力（要先注入规则种子）。
