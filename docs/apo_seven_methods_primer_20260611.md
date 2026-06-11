# APO 七法主线详解（APE→ProTeGi→OPRO→DSPy→TextGrad→MIPROv2→GEPA）

生成日期：2026-06-11

reviewed_by：Claude

适用范围：本仓库各报告与笔记反复引用"APE→ProTeGi→OPRO→DSPy→TextGrad→MIPROv2→GEPA"这条基线主干（见 `CHANGELOG.md` 经典锚点补读条目），但此前只有逐篇深读笔记，没有一份把七法串成整体叙事的术语介绍。本文档补上这个入口：每个方法给出定位、机制、代表性结果和被后续方法补上的洞，并指向对应深读笔记。

证据等级：全部内容综合自七篇 `method-and-results-read` 深读笔记（均读过本地 PDF/文本，含 SHA256）；所有数字与笔记同口径，可逐条回溯。属**论文级证据，非本项目复现结论**；跨论文原始分数不可直接横比（任务、模型、年代不同），引用时必须绑定各自实验设置。

> 这条主线不是唯一谱系。进化算法分支（EvoPrompt、PromptBreeder）与受控反例 PROSE 的横向对比见 [classic_optimizer_methods_comparison_20260610.md](classic_optimizer_methods_comparison_20260610.md)；本文档只覆盖被本仓库当作"基线主干"的七法。

## 主线一句话

这条链是自动 prompt 优化（APO）从**盲目搜索 → 利用失败反馈 → 利用优化轨迹 → 优化整个程序 → 通用文本反向传播 → 联合贝叶斯搜索 → 反思式进化**的演进史。驱动演进的两条暗线：**反馈信号越来越丰富**（标量分数 → 失败批评 → 逐模块文本梯度 → 完整执行轨迹），**优化对象越来越大**（单条指令 → 指令+演示 → 多模块程序）。

## 1. APE（2022）— 生成-筛选范式的起点

**Automatic Prompt Engineer**（Zhou et al., ICLR 2023）把"写指令"形式化为最简两阶段黑盒搜索：**propose-then-select**。

- **机制**：给 LLM 看少量 input-output 示例，让它反推"什么指令能产生这种映射"，批量生成约 50 条候选；再用 score function（execution accuracy 或 log probability）在小训练集上选最高分。可选迭代 Monte Carlo 搜索——让 LLM 生成高分指令的语义变体再筛一轮，但论文自报收益仅边际。
- **代表性结果**：24/24 个 instruction induction 任务达到或超过人类（IQM 0.810 vs 0.749）；搜出 zero-shot CoT prompt "Let's work this out in a step by step way to be sure we have the right answer."，把 MultiArith 从 78.7 提到 82.0、GSM8K 从 40.7 提到 43.0（相对 "Let's think step by step." 起点）。
- **留下的洞**：纯"生成→评分→选择"，**不利用失败案例的信息**，候选相互独立，搜索近乎盲目；且最早暴露"选择口径必须等于部署场景"的过拟合戒律（zero-shot 口径选出的指令到 few-shot 场景掉分）。
- 深读笔记：[paper-ape-2022.md](paper_notes/paper-ape-2022.md)

## 2. ProTeGi（2023）— 引入"文本梯度"

**Prompt Optimization with Textual Gradients**（Pryzant et al., EMNLP 2023），论文标题即 "Automatic Prompt Optimization with 'Gradient Descent' and Beam Search"。

- **机制**：把梯度下降类比到自然语言空间——拿当前 prompt 在 minibatch 上的**错误样本**，让 LLM 总结失败原因（这段批评即"文本梯度"），再沿"语义反方向"编辑 prompt；候选经 paraphrase 扩展后进入 beam search，并用 bandit 算法（UCB 系）做评估预算分配，不必每个候选都跑全量验证集。
- **代表性结果**：四个分类 benchmark 上平均比 Monte-Carlo 搜索高 3.9%、比 RL 高 8.2%、比原始 prompt 高 15.3%；最高把初始 prompt 提升 31%。消融显示 beam search 与 bandit 选择各自都有贡献。
- **留下的洞**：第一次让失败案例成为优化信号，是后续 critique/trace 路线（TextGrad、GEPA）的源头；但学习曲线约 3 步即达峰，之后过拟合或局部停滞，且 critique 本身可能误导（梯度把焦点带偏的定性案例）。
- 深读笔记：[paper-protegi-2023.md](paper_notes/paper-protegi-2023.md)

## 3. OPRO（2023）— LLM 即优化器

**Optimization by PROmpting**（Yang et al., DeepMind）换角度：不给失败案例，给**优化轨迹**。

- **机制**：构造 meta-prompt，内含按分数**升序**排列的历史 (instruction, 训练分) 轨迹（截断 top-20）+ 少量任务样例；每步让 optimizer LLM 采样 8 条**全新**指令（不是编辑、不要求语义保持），评分后回填轨迹循环。LLM 靠上下文内的"解-分数"模式归纳改进方向。
- **代表性结果**：搜出 "Take a deep breath and work on this problem step-by-step."（GSM8K 测试 80.2，对照 "Let's think step by step." 71.8、空串 34.0）；BBH 上多数任务超人写指令 5% 以上。
- **留下的洞**：信号只有标量分数，**不知道为什么失败**，无法定位根因；最佳 prompt 高度 model-specific（更像在搜"触发某模型某能力的钥匙短语"）；"默认不留验证集"的论断后续被反复挑战（train-test gap 常达 5%–20%）。本项目把 OPRO 当反面对照，强制 held-out。
- 深读笔记：[paper-opro-2023.md](paper_notes/paper-opro-2023.md)

## 4. DSPy（2023）— 从"优化一个 prompt"到"编译一个程序"

**DSPy**（Khattab et al., Stanford）是范式转变而非又一个算法。

- **机制**：把多步 LM 流水线抽象成**程序**——用 signature（如 `question -> answer`）声明每个 LM 调用的输入输出语义，用 module（Predict / ChainOfThought / ReAct）实例化成可组合计算图；prompt 具体文字不手写，由 **teleprompter（编译器内优化器）针对 metric 编译**出来。本版核心优化器是 BootstrapFewShot：让程序高温多跑训练输入、透明追踪多阶段 trace、用 metric 过滤出整条通过的 trace、把其中各模块的 input-output 对自举为 demonstration 候选，再随机搜索/Optuna 在 dev 上选组合。
- **代表性结果**：GSM8K 上 GPT-3.5 从 ~33% 编译到 88.3 dev / 81.6 test；编译能让 Llama2-13b-chat 追平 GPT-3.5；T5-770M 仅用 200 条标注追平依赖专家 prompt 的 GPT-3.5 方案。
- **关键澄清**（本仓库反复强调）：**这版优化的是 demonstration，不是 instruction**——把 DSPy 当"自动改指令工具"是误读，instruction 层自动优化要到 MIPROv2/COPRO 才系统化。它的范式贡献是把评估口径从"模型 X 在任务 Y"改成"模型 X + 程序 P + 编译策略 S 在任务 Y"。
- 深读笔记：[paper-dspy-2023.md](paper_notes/paper-dspy-2023.md)

## 5. TextGrad（2024）— 文本反向传播的通用化

**TextGrad**（Yuksekgonul et al., Stanford）把 ProTeGi 的"文本梯度"推广成通用**文本自动微分框架**。

- **机制**：把任意 compound 系统建成计算图，变量是文本（prompt、代码、分子、答案……）。前向算出 loss（LLM 评价或规则 metric）后，让 LLM 对每个变量产出自然语言批评（textual gradient）并沿图**逐节点反向传播**，再由文本版梯度下降（TGD）改写变量。API 刻意同构 PyTorch（`Variable` / `loss.backward()` / `optimizer.step()`）。典型成本结构：**弱模型做前向、强模型当 gradient engine**；稳定性靠 minibatch + momentum + **revert-if-worse 验证闸门**（每轮在验证集上只接受变好的更新）支撑。
- **代表性结果**：instruction-only（零 demo）的 prompt 优化在 BBH Object Counting 上 77.8 → 91.9，超 DSPy 8-demo 方案 7%；GSM8K 与 DSPy 持平（81.1），把 DSPy 选的 demo 拼到优化后 instruction 上进一步到 82.1——**instruction 与 demonstration 是互补的两条轴**。
- **留下的洞**："梯度"是作者自认的隐喻而非真梯度，本仓库另有批判性笔记 [paper-textual-gradients-flawed-metaphor-2025.md](paper_notes/paper-textual-gradients-flawed-metaphor-2025.md)；每步反传多次 LLM 调用成本不低；自然语言约束堆多后可靠性下降；跨模型迁移未验证。
- 深读笔记：[paper-textgrad-2024.md](paper_notes/paper-textgrad-2024.md)

## 6. MIPROv2（2024）— 指令与演示的联合贝叶斯优化

**MIPRO**（Opsahl-Ong et al., EMNLP 2024；DSPy 库中实现名 MIPROv2）补上 DSPy 没解决的"多阶段程序里 instruction 怎么自动优化"，并把问题形式化为两个挑战：**proposal**（prompt 空间太大，怎么采到少量高质量候选）与 **credit assignment**（只有程序级 metric、没有模块级标签，怎么归因到各模块）。

- **机制**：三步——(1) **bootstrap demonstration**（沿用 DSPy 的 trace 过滤自举）；(2) **grounded instruction proposal**：给 proposer LM 喂数据集模式摘要、程序控制流摘要、自举 demo 和历史评分，让它写出贴任务的候选指令；(3) **贝叶斯联合搜索**：用 Optuna 的 TPE 建代理模型，在 mini-batch 上评估"各模块选哪条指令 × 哪组 demo"的组合并更新先验，proposal 与 selection 解耦。
- **代表性结果**（7 任务，5 次运行 + 显著性检验）：联合优化在 5/7 任务最优，最高 +13%。最重要的分诊结论：**多数任务上优化 bootstrapped demonstration 比优化 instruction 更管用**；instruction 优化只在"含不显然、又无法靠少量样例表达的条件规则"的任务上才是决定性的。
- **留下的洞**：optimizer 推不出复杂任务的隐藏规则，仍需人写 seed prompt；代理模型只能在固定候选集里选、不能改进候选本身；demo 集本身高方差。
- 深读笔记：[paper-miprov2-2024.md](paper_notes/paper-miprov2-2024.md)

## 7. GEPA（2025）— 反思式进化 + Pareto 前沿

**GEPA**（Genetic-Pareto，Agrawal et al.）是当前主线终点，定位是"反思式 prompt 进化可以超过 RL 微调"。

- **机制**：三个核心组件——
  1. **反思式变异**：选中系统的一个模块，在 minibatch 上执行并收集 execution trace + evaluation trace（编译错误、failed rubrics、模块级失败原因等自然语言反馈），让 reflection LM 据此改写该模块 prompt——继承 ProTeGi/TextGrad 的批评思路，但输入是整条 rollout 轨迹而非只有分数或单点批评；
  2. **Pareto 候选池**：维护 candidate × example 分数矩阵，保留"在至少一个样本上最佳"的所有非支配候选，按出现在 Pareto frontier 的频次采样父代——避免贪心全局最优过早锁死局部模式；
  3. **system-aware merge（crossover）**：把不同进化分支里各模块的优胜 prompt 拼合成新候选（GEPA+Merge）。
- **代表性结果**：Qwen3 8B 上 aggregate 45.23 → 54.85，超过 GRPO（RL，固定 24,000 rollouts）的 48.91 与 MIPROv2 的 47.84，而 GEPA 平均只用约 3,936 rollouts；论文口径为对 GRPO 平均高约 6%、最高 20%，最高省 35 倍 rollouts。消融显示 **Pareto 选择本身是主要贡献**（aggregate improvement +12.44 vs 贪心 +6.05、beam +5.11）；产出 prompt 最高比 MIPROv2 短 9.2 倍。
- **留下的洞**：AIME-2025 上仍低于 GRPO（反思进化不是处处替代 RL）；Merge 在 Qwen3 8B 上反而掉分；大部分 rollout 预算花在验证候选而非产生学习信号；优势依赖 feedback function 质量，评价只能给标量时优势收窄。
- 深读笔记：[paper-gepa-2026.md](paper_notes/paper-gepa-2026.md)

## 主线总结

| 方法 | 年份 | 反馈信号 | 优化对象 | 信号家族 |
| --- | --- | --- | --- | --- |
| APE | 2022 | 小训练集标量分 | 单条 instruction | 标量 |
| ProTeGi | 2023 | 失败样本的自然语言批评 | 单条 prompt | critique |
| OPRO | 2023 | 历史 (prompt, 分数) 升序轨迹 | 单条 instruction | 标量 |
| DSPy | 2023 | metric pass/fail（trace 用于筛 demo） | 多模块程序，主要是 demonstration | 标量（含 trace 筛选） |
| TextGrad | 2024 | 逐节点反传的文本批评 | 任意文本变量 | critique |
| MIPROv2 | 2024 | metric + 贝叶斯代理模型 | 各模块 instruction × demo 组合 | 标量 |
| GEPA | 2025 | 完整 execution/evaluation trace 的反思 | 多模块 prompt 池（Pareto） | trace |

两条暗线的含义：

1. **反馈信息密度决定样本效率**。从标量（APE/OPRO）到批评（ProTeGi/TextGrad）到完整轨迹（GEPA），单位 rollout 被榨取的信息持续上升——这直接对应 GEPA 对 GRPO 的 35 倍 rollout 节省主张。本项目评估方法时按"标量 / critique / trace"三层分类，不把它们混为"LLM 改 prompt"（同 [classic_optimizer_methods_comparison_20260610.md](classic_optimizer_methods_comparison_20260610.md) 结论 2）。
2. **优化对象的升维依赖程序抽象**。从单指令到指令+演示再到多模块系统，DSPy 的 signature/module/编译抽象是承载这种扩展的底座，MIPROv2 与 GEPA 都长在其上；因此任何结果都必须连同程序结构与编译/优化策略一起记录才可复现。

## 对本项目的使用约定

- 这条主线是**基线锚点谱系**，不是排行榜：APE 与 OPRO 是任何 optimizer 实验的强制下限对照；ProTeGi/TextGrad 是 critique 线对照；MIPROv2 是 instruction+demo 联合优化基线；GEPA 是当前最值得复现的强 baseline（见 [literature_map.md](literature_map.md)）。
- 引用各方法的数字时必须绑定其原始实验设置；唯一可公平横比的是把多法放进同一框架的结果（如 coin-flip，见 [classic_optimizer_methods_comparison_20260610.md](classic_optimizer_methods_comparison_20260610.md)）。
- 各方法的最小验证/复现计划已写在对应深读笔记的末节，不在本文档重复。

## 关联文档

- 七篇深读笔记：[APE](paper_notes/paper-ape-2022.md)、[ProTeGi](paper_notes/paper-protegi-2023.md)、[OPRO](paper_notes/paper-opro-2023.md)、[DSPy](paper_notes/paper-dspy-2023.md)、[TextGrad](paper_notes/paper-textgrad-2024.md)、[MIPROv2](paper_notes/paper-miprov2-2024.md)、[GEPA](paper_notes/paper-gepa-2026.md)
- 进化算法分支与同框架横比：[classic_optimizer_methods_comparison_20260610.md](classic_optimizer_methods_comparison_20260610.md)
- 文献全景与优先阅读顺序：[literature_map.md](literature_map.md)
- "文本梯度"隐喻的批判：[paper-textual-gradients-flawed-metaphor-2025.md](paper_notes/paper-textual-gradients-flawed-metaphor-2025.md)
- 字段与证据口径：`docs/insight_field_standard.md`
