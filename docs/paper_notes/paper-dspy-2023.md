# Paper Note: DSPy / Compiling Declarative LM Calls into Self-Improving Pipelines

论文：DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines

链接：https://arxiv.org/abs/2310.03714

source_id：paper-dspy-2023

关联 issue：无

线索贡献者：internal-arxiv-search（经典锚点补读）

新颖性判断：duplicate-but-foundational-baseline（prompt-as-program 范式源头；MIPROv2、GEPA、Promptomatix、大量行业工具均建立其上）

阅读日期：2026-06-10

reviewed_by：Claude

local_pdf_path：`local_sources/raw/arxiv_papers/2310.03714/paper.pdf`

local_pdf_sha256：`5309836325C3A580B6C176242F49F21CA40E413B0ACD514E74B67E16BB1B56BC`

local_text_path：`local_sources/raw/arxiv_papers/2310.03714/paper.txt`

local_text_sha256：`927F5577E048E9FA3084FB5D68664C972AE0F7AD39CEF0930BB3E706761149E7`

evidence_level：method-and-results-read（读了编程模型三要素、compiler 三阶段、GSM8K/HotPotQA 两个 case study 主表和评估假设；附录 teleprompter 伪代码略读）

版本说明：本地 PDF 为 v1（2023-10-05）。注意：本版 teleprompter 主要优化 **demonstrations**，instruction 的自动优化是后续 [[paper-miprov2-2024]] 才系统化的；引用 DSPy 时要区分"这版优化什么"。

## 一句话结论

DSPy 把"写 prompt"重构成"写程序再编译"：用 natural-language **signature**（如 `question -> answer`）声明每个 LM 调用的输入输出，用 **module**（Predict / ChainOfThought / ReAct…）把 signature 实例化成可组合的 define-by-run 计算图，再用 **teleprompter**（编译器内的优化器）自动为每个 module 生成高质量 demonstration / instruction。它的范式贡献不是某个算法，而是把 prompt 从"手搓字符串"升级为**可版本化、可编译、可迁移、可复现**的程序组件——并附带一个对本项目极重要的方法论转向：评估对象应从"模型 X 在 GSM8K"变成"模型 X + 程序 P + 编译策略 S 在 GSM8K"。

## 问题设定

- 任务：构建并优化多阶段 LM pipeline（数学推理、多跳检索 QA、RAG、agent loop）。
- 优化对象：pipeline 中每个 Predict module 的参数——**主要是 demonstrations**，也可含 instruction / field description；以及（higher-order）控制流本身（如 ensemble）。
- 目标指标：任意 metric——EM / F1，甚至"另一个 DSPy 程序"（如检查 grounding 的判别程序）。
- 约束：训练集可极小且只需最终输出标签（中间步骤标签由 bootstrap 自动补）；适配 promptable 大模型与 finetunable 小模型。

## 方法摘要

- 候选如何生成（Stage 1 Candidate Generation）：编译器递归找出所有 Predict module，对每个 module 用 **BootstrapFewShot**——让 teacher 程序（或 zero-shot 自身）在训练输入上高温多次运行，**透明追踪多阶段 trace**，用 metric 过滤出"整条 pipeline 通过"的 trace，把其中各 module 的好 input-output 对当作候选 demonstration（rejection-sampling 式自举）。
- 反馈如何获得：metric pass/fail（可以是程序化 metric）。本版**不做自然语言 critique**，靠"哪些 trace 通过 metric"的筛选信号。
- 如何选择候选（Stage 2 Parameter Optimization）：把每个参数的候选集交给超参搜索——`BootstrapFewShotWithRandomSearch`、`BootstrapFewShotWithOptuna`（TPE），在 dev/val 上交叉验证选最优；或 `BootstrapFinetune` 把 demonstration 蒸馏进小模型权重。
- 是否使用记忆/archive：弱——候选 demonstration 池 + ensemble（Stage 3）保留 top-k 程序做多数投票；无跨任务长期记忆。
- 是否优化 optimizer 自身：否。teleprompter 策略固定，但可**组合**（teacher 程序监督 student 程序：大模型 pipeline 监督小模型/finetune）。
- 关键定位：与 OPRO（改 instruction 文本）、TextGrad（改任意变量的 textual gradient）不同，DSPy 这版的核心优化对象是 **demonstration 自举 + pipeline 编译**，instruction 退居其次。

## 实验设置

- 数据集：GSM8K（数学应用题）；HotPotQA（多跳检索 QA，用 ColBERTv2 检索器）。
- 模型：GPT-3.5、Llama2-13b-chat；finetune 目标 Flan-T5-Large（770M）。
- baselines：vanilla few-shot、few-shot + human CoT（专家写的 reasoning chain）、专家 ReAct prompt。
- train/dev/test 切分：在 dev 上做候选比较以避免 test 过拟合；HotPotQA 的 T5 编译只用 200 labeled + 800 unlabeled。
- 成本或调用次数：强调"编译只需几分钟到几十分钟"；小训练集即可。

## 主要结果

论文直接报告：

- **GSM8K（Table 1，dev/test）**：编译把简单程序从 4–20% 拉到 49–88%。
  - GPT-3.5：vanilla 极低（摘要口径 ~33%）→ CoT+ensemble **88.3 dev / 81.6 test** → reflection+ensemble 86.7 dev。
  - Llama2-13b-chat：从 ~9% → reflection+ensemble **49.0 dev / 46.9 test**。
  - bootstrap×2（自举套自举）明显优于单次 bootstrap（GPT-3.5 vanilla 44.0→64.7 dev）。
- **HotPotQA（Table 2，answer EM / passage acc）**：
  - GPT-3.5 vanilla few-shot 34.3 EM → CoT-RAG bootstrap 42.3/36.0 → multihop 程序最佳。摘要口径 32%→46%。
  - Llama2 22%→41%；编译能让 **Llama2-13b-chat 追平 GPT-3.5**。
  - **T5-Large（770M）** 经 BootstrapFinetune 后 dev 上 39.3% answer EM / 46.0% passage acc，仅用 200 labeled + 800 unlabeled——小模型经编译可与依赖专家 prompt 的 GPT-3.5 方案竞争。
- 定性：bootstrap 的 demonstration 常胜过专家手写 CoT / ReAct prompt；模块化让多种 pipeline（reflection、multihop）便宜地探索。

## 失败案例和局限

- **本版主要优化 demonstration，不是 instruction**：把 DSPy 当"自动改 instruction 工具"是误读；instruction-level 优化要到 MIPROv2/COPRO。引用时必须说清楚优化的是哪一层。
- **依赖可自动判定的 metric**：bootstrap 的 rejection sampling 要求 metric 能过滤好 trace；自由生成/主观任务里 metric 难定义时，自举信号失效。
- **检索召回受限**：CoT-RAG 完全依赖 ColBERTv2 从原问题直接检索，passage recall 受限；要靠 multihop 生成查询补救——说明 pipeline 结构本身是性能瓶颈，不是 prompt 单点能解决。
- **小训练集 + dev 选择仍有过拟合风险**：论文用 dev 比较来"避免 test 过拟合"，但候选选择本身建立在小 dev 上，与 OPRO/TextGrad 同样面临验证集噪声问题（[[paper-coin-flip-2026]]）。
- **LM 不可靠是前提假设**：作者明说 LM 高度不可靠，但"对多阶段设计搜索解空间还算高效"；这是经验性赌注，非保证。
- **成本未细表**：bootstrap×2 + ensemble(top-7) 会成倍放大调用；论文给"几分钟编译"但无完整 token 成本/推理成本对照。

## 洞见卡片

```yaml
insight: prompt 优化的对象应是"程序（signature+module+控制流）"，不是"一段字符串"。
evidence_type: direct-method + direct-result
paper_evidence:
  section: "3, 4, 6, 7"
  table_or_figure: "Table 1, Table 2"
  quote_or_paraphrase: "把 prompting 技术翻译成带 signature 的声明式 module，用 teleprompter 编译；GPT-3.5 GSM8K 从~33%到88%，小模型经编译追平 GPT-3.5。"
mechanism: 把"措辞"与"程序结构/参数"解耦后，优化器能在结构固定下系统搜索参数，换模型只需重编译。
actionable_rule: 本项目 prompt versioning 应保存 program artifact（signature/module/控制流/编译策略），而非单段文本（与 [[paper-autopdl-2025]]、batch3 的 artifact graph 结论一致）。
counterexample_or_limit: 一次性简单聊天里，程序化抽象的成本可能超过收益。
minimal_experiment: 同任务比较"手搓 prompt 字符串"vs"DSPy 程序+bootstrap 编译"的可复现性与换模型迁移成本。
confidence: high
```

```yaml
insight: 在有可判定 metric 时，自举 demonstration 常胜过专家手写 instruction/示例。
evidence_type: direct-result
paper_evidence:
  section: "6, 7"
  table_or_figure: "Table 1 (bootstrap vs +humanCoT), Table 2 (bootstrap vs expert ReAct)"
  quote_or_paraphrase: "bootstrap 的 demonstration 超过 few-shot+humanCoT 与专家 ReAct prompt；Llama2 经编译追平 GPT-3.5。"
mechanism: 模型自己生成、被 metric 过滤过的 trace，比人写示例更贴合该模型该 pipeline 的分布。
actionable_rule: 有 labeled dev 时，把 demonstration 自举当一等优化变量，与 instruction 改写并列对照（呼应 [[paper-teach-better-show-smarter-2024]]、[[paper-textgrad-2024]] 的互补性）。
counterexample_or_limit: metric 不可自动判定、或小 dev 噪声大时自举失效。
minimal_experiment: instruction-only / bootstrapped-demo / 二者叠加 三格，记录 EM 与推理成本。
confidence: high
```

```yaml
insight: 评估口径应绑定"程序 P + 编译策略 S"，而非裸模型分。
evidence_type: author-claim
paper_evidence:
  section: "5 Goals of Evaluation"
  table_or_figure: "无"
  quote_or_paraphrase: "从'不同 LM 在 GSM8K 怎么比'转向'它们在程序 P、编译策略 S 下怎么比'，才是可复现的 run。"
mechanism: 同一模型在不同 program/编译下分数差异巨大，脱离 program 谈模型分无法复现。
actionable_rule: 本项目所有 APO 结果必须连同 program 结构、teleprompter/optimizer、编译预算一起记录，否则不可复现（直接喂入渠道综合的 provenance 字段）。
counterexample_or_limit: 增加记录负担；对单点 prompt 实验略重。
minimal_experiment: 固定模型、变 program/编译策略，量化分数离散度，证明"裸模型分"不可比。
confidence: high
```

## 对本项目的启发

> 字段定义与 insight / conclusion / helpful method 的区分口径见 `docs/insight_field_standard.md`。

- conclusion：DSPy 是 prompt-as-program 的**奠基锚点**。它的实证支持本项目三条主张——(1) 优化对象是 artifact graph 不是字符串；(2) 有 metric 时自举 demonstration 极强；(3) 评估必须绑定 program+编译策略才可复现。但本版优化的是 demonstration，不是 instruction。
- helpful method：把 DSPy 的"signature 声明 → module 组合 → teleprompter 编译（bootstrap trace + 候选搜索 + ensemble）"作为 pipeline 级优化的参考骨架；本项目的 prompt ledger 字段应对齐 signature/module/编译策略。
- anti-pattern / limit：把 DSPy 当"自动改 instruction"工具（误读优化层）；或脱离 program 谈模型分。
- 适用场景：多阶段 pipeline / RAG / agent、有可自动判定 metric、想让小模型替代大模型省成本。
- 误用风险：在 metric 不可判定的主观任务上硬套自举；忽略 bootstrap×2+ensemble 的成本放大。

## 最小验证或演示计划

- 要验证的 insight / method：program+编译可复现性，以及"自举 demo vs instruction 改写 vs 叠加"。
- 最小验证任务：一个两阶段 RAG 或结构化抽取任务，有 EM/F1 metric，100–300 样本。
- 需要实现的模块：(1) 用现成 dspy 库声明最小 program（Predict/ChainOfThought）；(2) BootstrapFewShot(+RandomSearch) 编译；(3) 与 instruction-only optimizer（OPRO/TextGrad 式）共用同一评估集；(4) 换模型重编译测迁移。
- 观察指标：编译前后 EM、达到目标分的标注样本数（标签效率）、换模型迁移 delta、编译总调用成本、train-dev-test gap。
- 预计风险：小 dev 选择过拟合；metric 设计不当导致自举筛错 trace；ensemble 成本放大。
