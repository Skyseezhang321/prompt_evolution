# 经典 Prompt Optimizer 六法横向对比（APE / OPRO / EvoPrompt / PromptBreeder / DSPy-style / PROSE）

生成日期：2026-06-10

reviewed_by：Claude

适用范围：本表对比 *Prompt Optimization Is a Coin Flip*（[[paper-coin-flip-2026]]）横向比较的 6 个 optimizer。前 5 个是可独立引用的外部方法，各有深读笔记；第 6 个 PROSE 是该论文自建的内部基线（见 [[paper-prose-2026]]，唯一来源为 coin-flip Appendix C）。

证据等级：每个方法的机制与数字直接来自对应深读笔记（多为 `method-and-results-read`，读了本地 PDF）。跨方法的"同口径对比"数字来自 coin-flip 同一实验框架（Haiku/Nova Lite × 4 任务、等算力预算）。

> 注意：各论文**原始论文里的分数不可直接横比**（任务、模型、年代都不同）。唯一可公平横比的是 coin-flip 把 6 法放进同一框架后的分数（见文末"同框架对比"）。本表的"原论文主结果"列仅作各自能力的定性锚点。

## 一句话定位

| 方法 | 年份 | 一句话定位 | 独立笔记 |
| --- | --- | --- | --- |
| **APE** | 2022 | 最简奠基锚点：LLM 提案一批 instruction + 在小训练集上按分选最优（propose-then-select），无梯度无迭代 | [paper-ape-2022.md](paper_notes/paper-ape-2022.md) |
| **OPRO** | 2023 | LLM-as-optimizer 基线：把"历史 prompt+分数"升序塞进 meta-prompt，让 LLM 看分数模式生成全新候选（纯标量轨迹） | [paper-opro-2023.md](paper_notes/paper-opro-2023.md) |
| **EvoPrompt** | 2023/24 | 把经典 GA/DE 翻译成 LLM 能执行的语义算子：EA 管 selection/update，LLM 管 crossover/mutation | [paper-evoprompt-2024.md](paper_notes/paper-evoprompt-2024.md) |
| **PromptBreeder** | 2023 | 自指进化：连 mutation prompt 一起进化（hyper-mutation），同时学"任务 prompt"和"怎么改 prompt" | [paper-promptbreeder-2023.md](paper_notes/paper-promptbreeder-2023.md) |
| **DSPy-style** | 2023 | prompt-as-program：signature 声明 + module 组合 + teleprompter 编译；本版主要**自举 demonstration** 而非 instruction | [paper-dspy-2023.md](paper_notes/paper-dspy-2023.md)（+ [miprov2](paper_notes/paper-miprov2-2024.md) 补 instruction 层） |
| **PROSE** | 2026 | coin-flip 自建受控反例：结构化分解 + 多算子进化 + **风险感知选择**（mean+Sharpe+DRO）；用来证伪"risk-aware 选择有用"，结论是无优势 | [paper-prose-2026.md](paper_notes/paper-prose-2026.md) |

## 五维结构化对比

### 1. 优化对象（改的是什么）

| 方法 | 优化对象 | 结构粒度 |
| --- | --- | --- |
| APE | 单段 instruction | 整条文本 |
| OPRO | 单段 instruction（可选插入位置 Q_begin/Q_end/A_begin） | 整条文本 |
| EvoPrompt | 单段 task instruction | 整段（DE 版只改"差异部分"，保护共识片段） |
| PromptBreeder | task prompt + mutation prompt + few-shot contexts + 部分超参 | 多对象（含 optimizer 自身） |
| DSPy-style | 每个 module 的参数，**主要是 demonstration**，也可含 instruction/field description；以及控制流 | 程序级（signature/module/控制流） |
| PROSE | 单段 prompt，但拆成 role/task/constraints/examples/format 五块定向编辑 | 五段组件 |

### 2. 反馈信号（optimizer 看到什么）

| 方法 | 信号类型 | 有无 critique | 有无 trace |
| --- | --- | --- | --- |
| APE | 标量（execution accuracy 或 log prob） | 无 | 无 |
| OPRO | 纯标量训练分（升序轨迹） | 无 | 无 |
| EvoPrompt | 标量 dev 分（fitness） | 无 | 无 |
| PromptBreeder | 标量 batch fitness | 无 | 无（Lamarckian 用正确 working-out 反推） |
| DSPy-style | metric pass/fail（可程序化） | 无 | **有**（透明追踪多阶段 trace 做 rejection sampling） |
| PROSE | 标量 LLM-judge 分 | 无 | 无 |

> 全组都是**标量信号家族**（无自然语言 critique）。这正是 ProTeGi→TextGrad→GEPA 这条 critique/trace 线要补的洞——本 6 法都不在那条线上。DSPy 的 trace 用途是"筛好 demo"，不是"诊断错误根因"。

### 3. 搜索机制（怎么生成+选候选）

| 方法 | 候选生成 | 选择机制 | archive |
| --- | --- | --- | --- |
| APE | LLM 反推 instruction（forward/reverse/resample），默认 ~50 候选 | 训练集按分选最高；可选迭代 Monte Carlo | 无（迭代版上轮池算弱 archive） |
| OPRO | 每步采 8 条全新 instruction | 取训练分最高；轨迹截断 top-20 当 archive | 弱（top-20 轨迹） |
| EvoPrompt | GA: roulette 选父 → LLM crossover+mutation；DE: 只改差异部分融入 best | population + dev 分，保留 top-N | population |
| PromptBreeder | 9 类 mutation operator（含 hyper-mutation/Lamarckian/crossover） | binary tournament GA；BERT 相似度去重 + fitness sharing | population（含 lineage） |
| DSPy-style | BootstrapFewShot 自举 trace（rejection sampling） | RandomSearch / Optuna(TPE) 在 dev 上交叉验证；可 ensemble top-k | 候选 demo 池 + ensemble |
| PROSE | 20 种子→top10 population；6 自适应权重算子（targeted/crossover/random/exploration/simplification/random-gen） | **风险调整 fitness**：0.70·均分+0.15·Sharpe+0.15·DRO；elite 5，4 代无改进早停 | population(20) + 精英 |

### 4. 是否自指 / 优化 optimizer 自身

| 方法 | 自指 | 说明 |
| --- | --- | --- |
| APE | 否 | 固定提案模板 |
| OPRO | 否 | 固定 meta-prompt 结构 |
| EvoPrompt | 否 | 固定 GA/DE operator prompt |
| **PromptBreeder** | **是** | hyper-mutation 把 mutation prompt 也进化（`M' = LLM(H+M)`）——6 法中唯一显式自指 |
| DSPy-style | 否（可组合） | teleprompter 策略固定，但 teacher 程序可监督 student |
| PROSE | 否 | 算子权重自适应，但 fitness 公式/模板固定 |

### 5. 原论文主结果与关键局限（定性锚点，不可横比）

| 方法 | 原论文代表结果 | 关键局限 |
| --- | --- | --- |
| APE | 24/24 instruction-induction 任务达到/超过人类（IQM 0.810 vs 0.749）；产出 zero-shot CoT prompt | 只优化单 instruction；选择口径≠部署场景会过拟合；迭代搜索收益弱 |
| OPRO | GSM8K 最高 +8% vs 人写 zero-shot（"Take a deep breath…" 80.2 vs 71.8） | 纯标量无法定位根因；强 model/task 依赖；"可不留验证集"被后续挑战 |
| EvoPrompt | BBH 平均 DE +3.5%/GA +2.5%，最高 +25%；超 APE/MI/NI | GPT-3.5 多为单 seed；DE 倾向更长高方差 prompt；只测 canonical GA/DE |
| PromptBreeder | GSM8K 83.5、ETHOS 89% vs 手写 80%；zero-order hyper-mutation 改善率最高 42% | 成本高（pop 50、1–2k 评估）；few-shot context 可能盖过 prompt，task prompt 漂成 nonsense |
| DSPy-style | 编译把 GSM8K 从 ~33%→88%；Llama2-13b 经编译追平 GPT-3.5；T5-770M 仅 200 标注追平 | 本版优化 demo 非 instruction；依赖可判定 metric；bootstrap×2+ensemble 成本放大 |
| PROSE | 见下方同框架表 | **负结果**：风险感知选择无可测稳健性优势 |

## 同框架对比（唯一可公平横比的数字，来自 coin-flip）

LLM-judge 0–100，3 repeats 均值，held-out 100 test questions，等算力预算（每法 ~100 候选）。**粗体 = 该任务最高**。

### Claude Haiku 4.5（coin-flip Table 2）

| 方法 | Feedback-Bench | HelpSteer2 | WildBench | XSum |
| --- | --- | --- | --- | --- |
| Zero-Shot | 82.4 | 68.0 | 68.9 | 76.0 |
| APE | 82.3 | 69.3 | 68.0 | **76.6** |
| OPRO | 81.4 | 73.8 | 69.0 | 74.7 |
| EvoPrompt | 82.0 | **74.8** | 68.3 | 75.6 |
| PromptBreeder | **83.5** | 74.6 | 68.5 | 76.0 |
| DSPy-style | 81.9 | 69.8 | 65.1 | 76.2 |
| PROSE | 82.1 | 74.4 | **69.6** | 75.9 |

> 全表只有 HelpSteer2 上每个 optimizer 都超过 zero-shot；其余三任务平均增益为负或近零。6 法彼此差异在统计上不显著。

### Amazon Nova Lite（coin-flip Table 4，更差）

| 方法 | Feedback-Bench | HelpSteer2 | WildBench | XSum |
| --- | --- | --- | --- | --- |
| Zero-Shot | 80.4 | 70.7 | 64.6 | 73.5 |
| APE | 81.1 | 69.4 | 64.4 | 73.9 |
| OPRO | 81.9 | 70.0 | 64.2 | 73.5 |
| EvoPrompt | 81.0 | 69.7 | 62.9 | 71.8 |
| PromptBreeder | 80.2 | 72.8 | 65.6 | 72.9 |
| DSPy-style | 81.0 | 69.1 | 60.2 | 73.3 |
| PROSE | 80.4 | 70.0 | 64.6 | 72.8 |

> 24 个 method×task 均值中 14 个低于 zero-shot；Haiku 上 HelpSteer2 的 6/6 全胜在 Nova Lite 上崩到 1/6。

## 对本项目的可执行结论

1. **下限基线分层**：做任何 optimizer 实验，下限对照应至少含 APE（propose-then-select）与 OPRO（标量轨迹）。打不过这两个的复杂方法不值得上。
2. **信号结构才是真正的分类轴**：这 6 法都是"标量信号"家族；真正的能力跃迁在 critique/trace 线（ProTeGi→TextGrad→GEPA），评估时不要把"改 prompt"的方法混为一谈，要按"标量 / critique / trace"分层（见 [[paper-opro-2023]] 洞见卡）。
3. **DSPy 优化的是 demo 不是 instruction**：引用"DSPy-style"时必须说清优化层；instruction 自动优化要到 MIPROv2/COPRO。
4. **自指只有 PromptBreeder**：要研究"优化器自进化"，6 法里只有 PromptBreeder 是入口；但它多算子同开、因果难归因，复现要逐项消融。
5. **PROSE 是负结果，别当强方法复现**：先做 coin-flip 的耦合/headroom gate，再谈选择信号工程；"在 fitness 里加风险项"已被证伪无增益。
6. **唯一可信的横比是同框架**：跨论文原始分数不可比。任何"X 比 Y 强"的断言都必须绑定同一模型+任务+预算，否则只是各自 benchmark 的幻觉。

## 关联文档

- 横比来源与诊断框架：[[paper-coin-flip-2026]]（"要不要优化"的刹车）
- critique/trace 线对照：ProTeGi [[paper-protegi-2023]]、TextGrad [[paper-textgrad-2024]]、GEPA [[paper-gepa-2026]]
- instruction+demo 联合优化：[[paper-miprov2-2024]]
- 结构化/模块化 prompt：[[paper-modular-prompt-optimization-2026]]
- 字段与证据口径：`docs/insight_field_standard.md`
