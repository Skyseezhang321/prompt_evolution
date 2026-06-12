# Paper Note: GrIPS / Gradient-free, Edit-based Instruction Search for Prompting Large Language Models

论文：GrIPS: Gradient-free, Edit-based Instruction Search for Prompting Large Language Models

链接：https://arxiv.org/abs/2203.07281 （EACL 2023：https://aclanthology.org/2023.eacl-main.277/）

source_id：paper-grips-2022

关联 issue：无

线索贡献者：internal-arxiv-search（经典锚点补读遗留项；2026-06-12 主线结构评审时定向补读，检验"APE 作为主线起点"是否被更早的黑盒指令搜索动摇）

新颖性判断：extension

阅读日期：2026-06-12

reviewed_by：Claude

local_pdf_path：`local_sources/raw/arxiv_papers/2203.07281/paper.pdf`

local_pdf_sha256：`51570662994E142F8AEC131C239AF95D4537A500F1E7D65117D47714792561D5`

local_text_path：`local_sources/raw/arxiv_papers/2203.07281/paper.txt`

local_text_sha256：`E0A9373CC47389EC563BD162F94582493EC63B8B12CFCB78F19BA2D70C2579CD`

evidence_level：method-and-results-read（正文 §1–6 + Limitations 全读，含 Table 1–7 与 Figure 3；附录 A–G 仅按正文指针抽查）

## 一句话结论

GrIPS（v1 2022-03，**早于 APE 八个月**）证明黑盒、免梯度的自然语言指令搜索不需要 LLM 当生成器——纯机械的短语级编辑算子（删/换/改写/回加）+ 小验证集打分就能稳定提分；它和 APE 的真正分界不是时间而是**候选生成方式**（机械编辑 vs LLM 提案），且其"语义不连贯的指令照样涨分"发现比 flawed-metaphor（2025）早三年指向同一结论。

## 问题设定

- 任务：NATURAL-INSTRUCTIONS 中 8 个二分类任务（zero-shot instructional prompt 设定）。
- 优化对象：自然语言 task instruction（显式区别于 few-shot examples 与 prompt template）；也测了 instruction + 4-shot examples 组合模式。
- 目标指标：balanced accuracy（测试集 300 条/任务，消融 100 条/任务）。
- 约束：免梯度、API 可用；明确针对"梯度法对大模型算力不可行、对 API 模型不可得"的痛点。

## 方法摘要

- 候选如何生成：**不用 LLM**。用 CRF 成分句法分析器把指令切成短语级片段，对随机选中的短语施加 4 种编辑算子——del（删除）、swap（两短语互换）、par（用 PEGASUS paraphrase 模型改写）、add（把此前删掉的短语随机加回）。每轮 m=5 个候选 × l=1 个编辑。
- 反馈如何获得：score set S（默认 100 条，可降到 20）上的 balanced accuracy + α·预测熵（α=10；熵项鼓励产出多样标签、打破平分并避开局部极小）。纯标量信号，无 critique、无轨迹。
- 如何选择候选：贪心爬山——最优候选超过当前 base 才替换；n=10 轮、patience P=2 早停。可选 beam search 保留 top-B（B=5，模型调用量约 ×B）。
- 是否使用记忆/archive：被删短语池供 add 算子复用（弱 archive）；无其他记忆。
- 是否优化 optimizer 自身：否（也没有 LLM optimizer 可优化）。

## 实验设置

- 数据集：NATURAL-INSTRUCTIONS 8 个二分类任务；主表测试 300 条/任务，其余分析 100 条/任务。
- 模型：GPT-2 XL（1.5B）、InstructGPT babbage（~1.3B）、curie（~6.7B）；扩展到 OPT 1.3B–30B、BLOOM 1B/3B、GPT-J 6B、GPT-NeoX 20B、FLAN-T5 3B。未测 davinci（成本）。
- baselines：No Search、人工改写（Mishra et al. 2022b 指南，作者自行执行）、example search（同预算同 score set）、直接微调 / Adapters / Prefix-Tuning（仅 GPT-2 XL 可比）。
- train/dev/test 切分：score set 与测试集分离；与梯度法对比时 score set 做 80:20 train/dev。3 个种子（含示例的实验 5 个种子），95% 置信区间 + bootstrap 显著性检验。
- 成本或调用次数：**论文直接报告美元成本**——单次搜索（8 任务）babbage 每种子 $20–25、curie $125–175；全部实验约 $2400；单任务调用量 O(m×n×|S|×B)。

## 主要结果

论文直接报告：

- 主表（Table 1，Instruction-Only）：GPT-2 XL 49.54→58.90（+9.36）、babbage 55.80→60.09（+4.29）、curie 63.71→66.07（+2.36），均 p<0.05；模型越强、提升越小但越稳（置信区间更窄）。
- vs 人工改写（Table 3）：GrIPS 高 5.56 / 2.29 / 1.50 点（三模型）——自动编辑搜索胜过按指南人工重写。
- vs example search（同预算）：InstructGPT 上 GrIPS 高 1.54 / 1.62 点；GPT-2 XL 上反而是 example search 更好（该模型不会跟指令）。
- vs 梯度法（Table 4，GPT-2 XL）：贪心 GrIPS 53.68 低于直接微调 55.88 与 Adapters 55.08，但 beam B=5 达 56.50 超过全部梯度法；恒超 Prefix-Tuning（53.29 / 51.12）。作者推断（引 Li & Liang）Prefix-Tuning 上界 AutoPrompt，故预期 GrIPS 也超 AutoPrompt——**此为作者推断，非直接实验**。
- 消融（Table 2）：去掉 del/swap/par/add 分别 -2.56/-1.01/-1.14/-1.26，去掉熵项 -1.48——四个算子和熵项全都有贡献。
- score set 大小（Figure 3）：|S|=100 提升 4.27 点、|S|=20 仅 +1.0 点——数据越少收益越小，但 20 条仍有正收益。
- 任务无关初始化（Table 5）：从"只有标签列表"的 task-agnostic 指令出发也能提升（最多 +2.42），但不如 task-specific 起点的终点高。
- 开源模型（Table 6）：OPT/BLOOM/GPT-J/NeoX 提升约 6–7 点，FLAN-T5 +3.08。
- 质性（Table 7）：编辑可能让指令**语义不连贯甚至误导人类**（如 Task 195 优化结果为 "In this task, you are given a text from tweets . There."），但准确率照样提升；呼应 Webson & Pavlick 的"误导性指令可以更好"。

## 失败案例和局限

论文直接报告（Limitations 节）：

- 编辑算子**无法引入初始指令之外的新信息**——只能改述、删减、重排已有内容；作者点名"给 add 算子加生成能力"是未来方向（注：这正是 APE/ProTeGi 用 LLM 生成候选补上的洞）。
- 不适合纯生成任务：score function 里没有可替代 accuracy 的好指标。
- 指令理解越强的模型可能越不需要 prompt 优化（curie 提升已收窄到 2.36）。
- GPT-2 XL 上 example search 优于指令搜索——指令搜索的前提是模型会跟指令。

## 洞见卡片

```yaml
insight: 黑盒指令搜索的提分不依赖 LLM 生成器，也不依赖语义连贯——机械编辑 + 小验证集选择就够；"提升"与"指令更易被人理解"可以脱钩。
evidence_type: direct-result + failure-case
paper_evidence:
  section: "5.1, 5.7"
  table_or_figure: "Table 1, Table 7"
  quote_or_paraphrase: "三模型 +2.36~+9.36 显著提升；Task 021/195 的优化产物语义不连贯甚至误导人类但照样涨分。"
mechanism: 验证集上的爬山只对分数负责，不对人类可读性负责；模型对指令的利用方式与人类理解不同构。
actionable_rule: 评估任何 optimizer 的"改进"时，把可读性/语义合理性与分数分开记录；分数上涨不能当作"指令更好地表达了任务"的证据。
counterexample_or_limit: InstructGPT 在 task-specific 起点上整体更高（§5.4），说明语义并非完全无关——是"部分脱钩"不是"完全无关"。
minimal_experiment: 对优化前后 prompt 做人类可读性盲评 vs 分数变化的相关性检验。
confidence: high（与 [[paper-textual-gradients-flawed-metaphor-2025]] 的"提升常来自候选发现而非梯度式学习"跨年代互证）
```

```yaml
insight: 主线起点 APE 的真正贡献边界是"LLM 当候选生成器"，而非"第一个黑盒指令搜索"——GrIPS v1 早于 APE 八个月完成了后者。
evidence_type: direct-method（时间线与方法对照）
paper_evidence:
  section: "1, 3.2; arXiv v1 时间戳 2022-03-14"
  table_or_figure: "Figure 1"
  quote_or_paraphrase: "GrIPS 候选来自句法短语级 del/swap/par/add 机械算子 + PEGASUS 改写，无 LLM 提案；APE（2022-11）才把候选生成交给 LLM 反推。"
mechanism: 两者同属"标量信号 + 黑盒搜索"，差异在候选生成器的表达能力：编辑算子无法引入新信息（GrIPS 自承局限），LLM 提案可以。
actionable_rule: 主线叙事中 APE 的定位应表述为"LLM-as-generator 谱系的起点"，并给 GrIPS（编辑搜索）一行前史定位，避免读者误以为 APE 之前没有黑盒指令优化。
counterexample_or_limit: GrIPS 仅 8 个二分类任务、模型最大 30B；与 APE 的 24 任务 instruction induction 设置不可横比。
minimal_experiment: 同任务同预算下 GrIPS 编辑算子 vs APE 式 LLM 提案的候选质量对比（验证"生成器表达能力"是否是分水岭）。
confidence: high（时间线与机制均为论文直接证据；"分水岭"判断为 our-inference 性质的定位结论）
```

```yaml
insight: 验证集大小直接定价优化收益——|S|=100 提升 4.27 点、|S|=20 只剩 1.0 点。
evidence_type: direct-result
paper_evidence:
  section: "5.6"
  table_or_figure: "Figure 3"
  quote_or_paraphrase: "score set 从 100 缩到 20，babbage 平均提升从 4.27 衰减到 1.0。"
mechanism: score set 即训练集，小样本下选择信号噪声大、泛化差。
actionable_rule: 报告任何 optimizer 增益时必须连同验证集大小一起报告；样本预算 <50 时对宣称的增益打折。
counterexample_or_limit: 单一模型（babbage）上的曲线；不同任务噪声水平不同。
minimal_experiment: 本项目最小实验固定加一条"验证集减半"敏感性检查。
confidence: medium-high
```

## 对本项目的启发

> 字段定义与 insight / conclusion / helpful method 的区分口径见 `docs/insight_field_standard.md`。

- insight：见上方三张洞见卡片。
- conclusion：无（单篇论文不出 conclusion）。
- helpful method：① 分数函数里加预测熵项（α 加权）防候选塌缩到单一标签——廉价、可直接抄进本项目最小实验的 selector；② 论文的成本披露格式（每种子每模型美元数 + 调用量大 O 式）值得作为本项目运行记录的范例。
- anti-pattern / limit：把"分数上涨"解读成"指令语义更好"；在不会跟指令的模型上做指令搜索（GPT-2 XL 上 example search 更优）。
- 适用场景：分类/标签任务、有 50–100 条带标签样本、API 黑盒模型、希望保持指令大体可读时的廉价基线。
- 误用风险：生成任务（无好指标）；期待编辑算子发现初始指令之外的领域知识（它做不到——那是 LLM 提案/critique 线的活）。

## 最小验证或演示计划

- 要验证的 insight / method：熵正则选择项的独立贡献（洞见卡 3 + helpful method ①）。
- 最小验证任务：本项目意图抽取最小任务（与 ProTeGi/APE 复现共用数据）。
- 需要实现的模块：短语切分（可用现成 parser）、4 编辑算子、balanced accuracy + 熵打分器。
- 观察指标：有/无熵项的最终分数与候选标签分布偏斜度；验证集 100 vs 20 的增益衰减。
- 预计风险：中文任务的短语切分质量；8 任务结论是否迁移到抽取任务。
