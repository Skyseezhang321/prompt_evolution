# Paper Note: TextGrad / Automatic "Differentiation" via Text

论文：TextGrad: Automatic "Differentiation" via Text

链接：https://arxiv.org/abs/2406.07496

source_id：paper-textgrad-2024

关联 issue：无

线索贡献者：internal-arxiv-search（经典锚点补读）

新颖性判断：duplicate-but-foundational-baseline（textual-gradient 范式的命名与框架化源头，后续 GEPA / Modular / Scaling / Flawed-Metaphor 都以它为参照）

阅读日期：2026-06-10

reviewed_by：Claude

local_pdf_path：`local_sources/raw/arxiv_papers/2406.07496/paper.pdf`

local_pdf_sha256：`9CBFD5C78AD69E2A8363E76D6774F3E6B5E68F46B409D8B560E98276A985B428`

local_text_path：`local_sources/raw/arxiv_papers/2406.07496/paper.txt`

local_text_sha256：`1E3A2669F693F91A05AF1D83F584150BCC3BB03A51476190C00DB9B4CF76DE03`

evidence_level：method-and-results-read（读了框架抽象、prompt/instance 优化机制、code/QA/reasoning 三组主结果和 discussion；molecule/radiotherapy 应用与附录 prompt 模板略读）

版本说明：本地 PDF 为 v1（2024-06-11）。

## 一句话结论

TextGrad 把"LLM 给的自然语言反馈"正式抽象成**可经由计算图反向传播的 textual gradient**，并用 PyTorch 同构 API（`Variable` / `TextLoss` / `TGD.step` / `loss.backward()`）封装，使得"优化一个 compound AI 系统的任意变量"（prompt、代码、分子、治疗方案）变成 turn-key 操作。对本项目的核心价值有两层：(1) 它确立了"textual gradient"这个被后续反复使用又反复质疑的术语和工程范式；(2) 它给出一个干净的实证——**instruction-only 的 textual-gradient prompt 优化可以追平甚至超过 DSPy 的 8-shot demo 方案**，且 instruction 与 demo 是互补的。

## 问题设定

- 任务：优化 compound AI 系统中的任意"变量"。两类问题：
  - instance optimization：在测试时直接优化某个具体解（代码片段、某题答案、分子结构），只求改好这一个实例。
  - prompt optimization：优化一个能在整个任务上泛化的 prompt / system instruction。
- 优化对象：被 `requires_grad=True` 标记的文本变量（本项目最关心 system prompt）。
- 目标指标：由一个 `TextLoss`（LLM 评价）或规则 metric（exact match）给出的 loss。
- 约束：只需用户提供目标函数，不需调框架内部组件/prompt；适配闭源 API 模型（不需要参数访问）。

## 方法摘要

- 候选如何生成：把系统建成计算图，前向跑出 prediction 与 loss；反向时让 LLM 对每个变量产出**自然语言批评（textual gradient）**——"这个变量该如何改才能降低下游 loss"。`TGD.step` 用这些 gradient 把变量改写成新版本。链式法则用文本拼接近似：有 successor 的变量收到来自下游的 gradient。
- 反馈如何获得：自然语言 critique，由"gradient engine"LLM 生成。典型设置是**弱模型做前向、强模型做梯度**（gpt-3.5-turbo-0125 跑推理，gpt-4o 产反馈），一次性付优化成本换长期便宜推理。
- 如何选择候选：minibatch SGD（batch size 3、12 iter，共 36 样本，有放回采样）+ **validation loop**：每轮在验证集评估，只有优于上一轮才接受更新（revert-if-worse），这是它的过拟合/稳定性闸门。
- 是否使用记忆/archive：弱——可选 **momentum**（optimizer 改写时能看到该变量的早期版本）；无跨任务记忆。
- 是否优化 optimizer 自身：否（但 discussion 明确把"用 TextGrad 优化 TextGrad 框架自身"列为 future work——这正是后续 metaTextGrad / SePO 的方向）。
- 工程特性：PyTorch 同构抽象、开源、natural language constraints（用自然语言约束 optimizer，但承认"约束太多时可靠性下降"）。

## 实验设置

- 数据集：LeetCode Hard（代码）；Google-proof QA、MMLU-ML、MMLU-College Physics（solution opt）；BBH Object Counting / Word Sorting（50/100/100 train/val/test）、GSM8k（用 DSPy 的 split）（prompt opt）。
- 模型：forward 多为 gpt-4o（code/QA）或 gpt-3.5-turbo-0125（prompt opt）；gradient engine 为 gpt-4o。
- baselines：code 用 Reflexion；prompt opt 用 zero-shot CoT 和 DSPy BootstrapFewShotRandomSearch（10 候选程序、8 demo）。
- train/dev/test 切分：prompt opt 有显式 train/val/test，并用 val 做 revert 闸门（比 OPRO 的"默认不留验证集"更稳健）。
- 成本或调用次数：prompt opt 每任务 12 iter × batch 3 = 36 训练样本；强调"付一次优化成本，换弱模型的便宜推理"。

## 主要结果

论文直接报告：

- 代码（LeetCode Hard，gpt-4o，5 seeds，Table 1）：zero-shot 0.26 → Reflexion(1-demo,5-iter) 0.31 → **TextGrad(0-demo,5-iter) 0.36**。相对最佳已有方法约 20% 相对增益，且 TextGrad 是 zero-shot 无 demo。
- solution opt（Table 2，gpt-4o，zero-shot）：Google-proof QA 51.0(CoT) → 55.0；MMLU-ML 85.7 → 88.4；MMLU-College Physics 91.2 → 95.1。
- prompt opt（Table 3，forward=gpt-3.5-turbo，grad=gpt-4o）：
  - Object Counting：CoT 77.8 → DSPy(8-demo) 84.9 → **TextGrad(instruction-only,0-demo) 91.9**（超 DSPy 7%）。
  - Word Sorting：76.7 → 79.8 → 79.8（与 DSPy 持平）。
  - GSM8k：72.9 → 81.1 → 81.1（与 DSPy 持平）。
  - **互补性**：把 DSPy 选的 demo 直接拼到 TextGrad 优化后的 instruction 上，GSM8k 进一步到 82.1。
- 关键定性观察：DSPy 加 in-context demo、TextGrad 改 system prompt，两者做的是**互补调整**，可叠加。

## 失败案例和局限

- **"梯度"是隐喻而非真梯度**：作者在正文就把 differentiation/gradient 称为 metaphor。后续 [[paper-textual-gradients-flawed-metaphor-2025]] 正是论证这个类比会误导（textual feedback 不具备梯度的局部性/可加性）；本项目引用 TextGrad 结果时必须避免"像在做可微优化"的错觉。
- **constraint 可靠性随数量下降**：自然语言约束多了之后 instruction-following 变差（正文明确）；这与 TextReg / edit-level 分析里"prompt 膨胀=过拟合补丁"的警告一致（[[paper-textreg-2026]]、[[paper-causal-edit-level-2026]]）。
- **稳定性靠工程闸门撑**：minibatch + momentum + revert-if-worse 都是为压方差；discussion 把 variance reduction / adaptive gradient / self-verification 列为未解决方向，说明原始 TextGrad 优化过程并不稳定。
- **扩展性是 future work**：tool-use、RAG 等实用组件当时未纳入计算图；分子/治疗方案只是 in silico proof-of-concept，无实验/临床验证。
- **成本结构**：强模型当 gradient engine、每轮 forward+backward+validation，调用成本不低；论文用"换便宜推理"来正当化，但没给完整 token 成本表（需要时本项目要自行测）。
- **未报告跨模型迁移**：prompt opt 只在 gpt-3.5 上验证，没测优化后的 prompt 搬到别的模型是否仍有效。

## 洞见卡片

```yaml
insight: instruction 优化与 demonstration 优化是互补的两条轴，不该二选一。
evidence_type: direct-result
paper_evidence:
  section: "3.3"
  table_or_figure: "Table 3 + 正文 82.1% 叠加结果"
  quote_or_paraphrase: "TextGrad(instruction-only) 在 Object Counting 超 DSPy(8-demo) 7%，在 GSM8k/Word Sorting 持平；把 DSPy 的 demo 拼到 TextGrad 的 instruction 上 GSM8k 再升到 82.1%。"
mechanism: instruction 改"怎么想/怎么输出"，demo 给"长什么样的范例"，二者覆盖不同失败模式，可叠加。
actionable_rule: APO 实验至少跑 instruction-only / demo-only / instruction+demo 三格，别默认"优化 prompt"只指改 instruction（与 [[paper-teach-better-show-smarter-2024]] 同向）。
counterexample_or_limit: 叠加不总是正收益；demo 会增推理成本，也可能引入分布偏差。
minimal_experiment: 同任务三格对照，记录 accuracy、推理 token 成本、OOD gap。
confidence: high
```

```yaml
insight: 弱模型前向 + 强模型当 gradient engine，是一种可正当化的成本结构。
evidence_type: direct-method + direct-result
paper_evidence:
  section: "3.3"
  table_or_figure: "Table 3 setup"
  quote_or_paraphrase: "forward=gpt-3.5-turbo-0125、feedback=gpt-4o；付一次优化成本换弱模型的便宜推理。"
mechanism: 优化是一次性投入，推理是长期重复成本；把昂贵推理推到优化阶段一次性消化。
actionable_rule: 设计 optimizer 时显式区分 optimizer/gradient 模型与部署/scorer 模型，并分别记成本（与 [[paper-gepa-2026]] 的 Qwen-opt→GPT 迁移同思路）。
counterexample_or_limit: 强模型生成的反馈未必适配弱模型的能力边界，可能优化出弱模型跟不上的 prompt。
minimal_experiment: 固定部署模型，比较"同模型自优化"vs"强模型当 gradient engine"的最终部署分与总成本。
confidence: medium-high
```

```yaml
insight: revert-if-worse 的验证闸门，是 textual 优化里最低成本的过拟合控制。
evidence_type: direct-method
paper_evidence:
  section: "3.3 Methods"
  table_or_figure: "无表，正文描述"
  quote_or_paraphrase: "每轮在 validation set 评估，只有优于上一轮才接受 prompt 更新。"
mechanism: 把"接受更新"从"optimizer 自己说更好"改成"held-out 数据说更好"，挡住自评偏差和单 minibatch 噪声。
actionable_rule: 本项目 optimizer 默认接入 held-out 验证闸门 + 保留 best-seen，而不是无条件接受每次改写（对照 OPRO 的"默认不留验证集"[[paper-opro-2023]]）。
counterexample_or_limit: 验证集太小时闸门本身也会过拟合（[[paper-coin-flip-2026]] 的噪声地板问题）。
minimal_experiment: 有/无 revert 闸门两组，比较测试分波动和 train-test gap。
confidence: high
```

## 对本项目的启发

> 字段定义与 insight / conclusion / helpful method 的区分口径见 `docs/insight_field_standard.md`。

- conclusion：TextGrad 是 textual-gradient 范式的**框架化锚点**。它证明自然语言反馈足以做 turn-key 的 compound 系统优化，且 instruction-only 改写能匹敌 demo 检索；但"梯度"是隐喻，稳定性靠 minibatch/momentum/validation 三件套撑，跨模型迁移未验证。
- helpful method：把 TextGrad 的 prompt-opt 回路（minibatch forward → LLM critique 当 gradient → TGD 改写 → val 闸门 revert）作为 critique-guided optimizer 的标准实现骨架；与 OPRO 的纯标量轨迹形成"反馈信号"对照轴。
- anti-pattern / limit：把 textual gradient 当真梯度推理（叠加性、收敛性）；或无限堆叠 natural language constraint（可靠性下降）。
- 适用场景：compound 系统、可写出明确 loss、愿意用强模型当 gradient engine；尤其 instance optimization（代码/解的 test-time 改进）效果直接。
- 误用风险：在 reasoning 之外把 in-silico 结果（分子/治疗）当已验证结论；忽略 gradient engine 的调用成本。

## 最小验证或演示计划

- 要验证的 insight / method：critique-guided（TextGrad 式）vs 标量轨迹（OPRO 式）vs trace-aware（GEPA 式）三种反馈信号在同一任务上的样本效率与过拟合。
- 最小验证任务：BBH Object Counting 或一个结构化抽取任务（有 exact-match metric，便于复用 TextGrad 口径）。
- 需要实现的模块：(1) Variable/Loss/TGD 最小封装或直接调用现成 textgrad 库；(2) minibatch + revert-if-worse 闸门；(3) 与 OPRO/ProTeGi 共用评估集与 train-test gap 记录；(4) instruction-only / demo-only / 叠加 三格。
- 观察指标：达到目标分的 forward 调用数、gradient engine token 成本、train-test gap、prompt 长度增长、跨模型迁移 delta。
- 预计风险：优化过程方差大（需 momentum/多 seed）；强 gradient engine 成本高；小验证集闸门自身过拟合。
