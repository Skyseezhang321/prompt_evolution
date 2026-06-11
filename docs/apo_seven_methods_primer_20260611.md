# APO 七法主线详解（APE→ProTeGi→OPRO→DSPy→TextGrad→MIPROv2→GEPA）

生成日期：2026-06-11

reviewed_by：Claude

适用范围：本仓库各报告与笔记反复引用"APE→ProTeGi→OPRO→DSPy→TextGrad→MIPROv2→GEPA"这条基线主干（见 `CHANGELOG.md` 经典锚点补读条目），但此前只有逐篇深读笔记，没有一份把七法串成整体叙事的术语介绍。本文档补上这个入口：每个方法给出定位、机制、代表性结果和被后续方法补上的洞，并指向对应深读笔记。

证据等级：全部内容综合自七篇 `method-and-results-read` 深读笔记（均读过本地 PDF/文本，含 SHA256）；所有数字与笔记同口径，可逐条回溯。属**论文级证据，非本项目复现结论**；跨论文原始分数不可直接横比（任务、模型、年代不同），引用时必须绑定各自实验设置。

> 这条主线不是唯一谱系。进化算法分支（EvoPrompt、PromptBreeder）与受控反例 PROSE 的横向对比见 [classic_optimizer_methods_comparison_20260610.md](classic_optimizer_methods_comparison_20260610.md)；规划搜索分支（PromptAgent）与前史锚点（GrIPS）作为主线外锚点见暗线三与 §1 前史定位；本文档只覆盖被本仓库当作"基线主干"的七法。主线为什么这样选、这样排，见下文「为什么是这条主线」。

## 主线一句话

这条链是自动 prompt 优化（APO）从**盲目搜索 → 利用失败反馈 → 利用优化轨迹 → 优化整个程序 → 通用文本反向传播 → 联合贝叶斯搜索 → 反思式进化**的演进史。驱动演进的三条暗线：**反馈信号越来越丰富**（标量分数 → 失败批评 → 逐模块文本梯度 → 完整执行轨迹），**优化对象越来越大**（单条指令 → 指令+演示 → 多模块程序），**搜索结构越来越聪明**（盲目采样 → beam → MCTS 规划 → Pareto 候选池；规划搜索一站由主线外锚点 PromptAgent 提供，见「三条暗线的含义」第 3 条）。

排序口径提醒：七法按**时间**排序，机制上是**双轨汇合**——critique 线（ProTeGi → TextGrad）与程序线（DSPy → MIPROv2）平行发展，在 GEPA 汇合（轨迹反思 × 多模块程序 × Pareto 池）。MIPROv2 排在 TextGrad 之后是时间序，不代表"反馈密度继续上升"——它属标量信号家族（见主线总结表"信号家族"列的交替），把主线读成单调升级链是误读。

## 为什么是这条主线

主线不是排行榜，也不是某次随口指定的路线；它的形成过程和取舍标准都可回溯：

**形成过程（四步，均有仓库内记录）**

1. **种子**（2026-06-08）：仓库初始化当天的 [literature_map.md](literature_map.md) 与 `research_brief.md` 基于文献检索盘点领域公认经典，这组方法即在其中——是检索结论，不是对话中的即兴指定。
2. **挂成缺口**（2026-06-08）：arXiv top80 扫描建 taxonomy 时，发现经典锚点多数不在 top80 样本内，[arxiv_top80_taxonomy.md](arxiv_top80_taxonomy.md) 显式标注"经典锚点未深读"——此时它们的地位只是待验证假设。
3. **深读闭合**（2026-06-10）：APE / OPRO / DSPy / MIPROv2 / TextGrad 五篇全文证据级深读补齐（连同已有 ProTeGi / GEPA 等笔记），基线主干才正式成形（见 `CHANGELOG.md` 经典锚点补读条目）。
4. **外部校验**（2026-06-10）：用 3 篇独立综述（APO survey 2502.16923、APE survey 2502.11560、Context Engineering survey）做[完整性校验](arxiv_taxonomy_completeness_check_20260610.md)，确认这套盘点在"离散自然语言 prompt 优化"范围内无整块遗漏。2026-06-12 主线结构评审又定向补读 GrIPS 与 PromptAgent，分别检验起点定位与搜索结构缺环（结论已并入本文）。

**取舍标准（为什么是这七个、这个顺序）**

- **基线锚点谱系，不是排行榜**：入选标准是"本项目实验必须对照或参照"——APE/OPRO 是强制下限对照，ProTeGi/TextGrad 是 critique 线对照，MIPROv2 是 instruction+demo 联合优化基线，GEPA 是当前最值得复现的强 baseline。
- **每环留洞、下环补洞**：APE 不用失败信息→ProTeGi 补；OPRO 不知为何失败→DSPy/MIPROv2 换对象、TextGrad/GEPA 换信号；DSPy 不优化 instruction→MIPROv2 补——演进有机制逻辑，不是时间罗列。
- **证据纪律**：七法全部有 `method-and-results-read` 深读笔记（本地 PDF + SHA256），数字逐条可回溯；且三篇独立综述都把这组方法当 canonical 处理。
- **刻意排除项及去处**：进化分支（EvoPrompt/PromptBreeder，标量信号家族）→ [六法横向对比](classic_optimizer_methods_comparison_20260610.md)；规划搜索分支（PromptAgent）→ 暗线三主线外锚点；前史（GrIPS 已读，AutoPrompt/RLPrompt 待读）→ §1 前史定位；PROSE → coin-flip 内部基线，非独立文献。单链呈现是为叙事入口服务，结构实情是上述双轨汇合。
- **终点口径**：主线停在 GEPA 不是更新滞后——[arXiv 2025/2026 前沿深读综合](arxiv_2025_2026_frontier_synthesis_20260612.md)对 25 篇的时间切片显示「新方法起名字的时代（2022–2024）结束」，其中唯一确立主线的命名方法即 GEPA；其后的演进以四个转向形态出现，由「主线之后」一节对接。

## 1. APE（2022）— 生成-筛选范式的起点

**Automatic Prompt Engineer**（Zhou et al., ICLR 2023）把"写指令"形式化为最简两阶段黑盒搜索：**propose-then-select**。

- **前史定位**（2026-06-12 补）：GrIPS（v1 2022-03，早于 APE 八个月）已经在做免梯度的黑盒指令搜索，但其候选来自机械短语编辑（删/换/改写/回加），自承无法引入初始指令之外的新信息；APE 的起点地位在于**首次把候选生成交给 LLM**（LLM-as-generator），而非"第一个黑盒指令搜索"。见 [paper-grips-2022.md](paper_notes/paper-grips-2022.md)；更早的 AutoPrompt（白盒梯度）/ RLPrompt（RL 策略）属另一信号家族，仍待补读。

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
- **留下的洞**：AIME-2025 上仍低于 GRPO（反思进化不是处处替代 RL）；Merge 在 Qwen3 8B 上反而掉分；大部分 rollout 预算花在验证候选而非产生学习信号；优势依赖 feedback function 质量，评价只能给标量时优势收窄。适用条件后被 VISTA 收敛为「反馈含轨迹级诊断 + 真实根因在假设空间内」，反例与数字见下文「主线之后」。
- 深读笔记：[paper-gepa-2026.md](paper_notes/paper-gepa-2026.md)

## 主线总结

| 方法 | 年份 | 反馈信号 | 优化对象 | 信号家族 | 搜索/选择结构 |
| --- | --- | --- | --- | --- | --- |
| APE | 2022 | 小训练集标量分 | 单条 instruction | 标量 | 批量提案（~50）按分选最优，可选 MC 迭代 |
| ProTeGi | 2023 | 失败样本的自然语言批评 | 单条 prompt | critique | beam search + bandit（UCB 系）预算分配 |
| OPRO | 2023 | 历史 (prompt, 分数) 升序轨迹 | 单条 instruction | 标量 | 轨迹 top-20 回填循环，每步 8 条取最高 |
| DSPy | 2023 | metric pass/fail（trace 用于筛 demo） | 多模块程序，主要是 demonstration | 标量（含 trace 筛选） | RandomSearch / Optuna(TPE) 在 dev 选组合 |
| TextGrad | 2024 | 逐节点反传的文本批评 | 任意文本变量 | critique | minibatch TGD + momentum + revert-if-worse 闸门 |
| MIPROv2 | 2024 | metric + 贝叶斯代理模型 | 各模块 instruction × demo 组合 | 标量 | TPE 贝叶斯代理联合搜索 |
| GEPA | 2025 | 完整 execution/evaluation trace 的反思 | 多模块 prompt 池（Pareto） | trace | Pareto 候选池 + 频次采样父代 + merge |

三条暗线的含义：

1. **反馈信息密度决定样本效率**。从标量（APE/OPRO）到批评（ProTeGi/TextGrad）到完整轨迹（GEPA），单位 rollout 被榨取的信息持续上升——这直接对应 GEPA 对 GRPO 的 35 倍 rollout 节省主张。本项目评估方法时按"标量 / critique / trace"三层分类，不把它们混为"LLM 改 prompt"（同 [classic_optimizer_methods_comparison_20260610.md](classic_optimizer_methods_comparison_20260610.md) 结论 2）。
2. **优化对象的升维依赖程序抽象**。从单指令到指令+演示再到多模块系统，DSPy 的 signature/module/编译抽象是承载这种扩展的底座，MIPROv2 与 GEPA 都长在其上；因此任何结果都必须连同程序结构与编译/优化策略一起记录才可复现。
3. **搜索结构是独立于反馈信号的演进维度**（2026-06-12 补，证据级）。盲目采样（APE/OPRO）→ beam（ProTeGi）→ MCTS 规划（PromptAgent，主线外锚点）→ Pareto 候选池（GEPA）。两组单变量消融跨论文互证：PromptAgent 在候选生成与反馈完全固定、同等探索量下 MCTS 0.754 > Greedy 0.698 ≈ Beam 0.697 > 单步 MC 0.635（[paper-promptagent-2023.md](paper_notes/paper-promptagent-2023.md) Table 4）；GEPA 消融显示 Pareto 选择本身是主要贡献（aggregate +12.44 vs 贪心 +6.05、beam +5.11，[paper-gepa-2026.md](paper_notes/paper-gepa-2026.md)）。对本项目的含义：对比 optimizer 时把"探索候选数"作为预算轴单独报告，search structure 与 feedback signal 分开消融，不可把搜索结构带来的收益归功于"反思有效"。

## 主线之后：为什么没有第八法（2025/2026）

主线终点停在 GEPA 不是更新滞后。[arXiv 2025/2026 前沿深读综合](arxiv_2025_2026_frontier_synthesis_20260612.md)对 25 篇的时间切片结论是：**「新方法起名字」的时代（2022–2024）结束了**——25 篇中只有 GEPA 一篇是确立主线的命名方法，其余产出形态是诊断、形式化、对象升维、自进化与卫生。对主线读者，这意味着 GEPA 留下的洞不再由"第八个命名方法"来补，而是由四个转向分头补：

- **反思的适用条件**（转向一·降温与诊断）：VISTA 证明根因不在假设空间时反思越多偏越远——defective seed 上 GEPA 23.81%→13.50%，把假设生成与改写解耦后恢复 87.57%；跨模型迁移 GEPA 优化结果只剩 22.74% vs VISTA 86.05%。"反思有用 vs 有害"由此收敛为两个前置条件：反馈含轨迹级诊断、真实根因在 optimizer 假设空间内。见 [paper-vista-reflection-dark-2026.md](paper_notes/paper-vista-reflection-dark-2026.md)。
- **prompt 膨胀与伪提升**（转向四·卫生与正则）：Prompt Codebooks 把 prompt 拆成按输入路由的可复用单元，HotpotQA 上比 MIPROv2 prompt 短 14.1 倍、性能仍超 GEPA（IFBench 41.33，+2.72）；PrefPO 把长度/重复/hacking 率做进评估（TextGrad hacking 率 86% vs PrefPO 37%）。见 [paper-prompt-codebooks-2026.md](paper_notes/paper-prompt-codebooks-2026.md)、[paper-prefpo-2026.md](paper_notes/paper-prefpo-2026.md)。
- **反馈形态继续升级**（暗线一的延长线）：SPEAR 让 optimizer 自己写 Python 做 confusion matrix / groupby 式错误分析，BBH-7 平均 0.938 vs GEPA 0.628——轨迹之后的下一站可能是"结构化计算分析"。见 [paper-spear-2026.md](paper_notes/paper-spear-2026.md)。
- **optimizer 自身入轨**（转向三·自进化）：SePO 把 optimizer 的 system prompt 纳入演化（71.89→76.38，去 self-improvement 掉回 74.94）、MemAPO 双记忆跨任务复用（70.7% vs TextGrad 63.6%、成本反降 58.6%）——主线七法共同的"optimizer 静态"默认假设开始松动。见 [paper-sepo-2026.md](paper_notes/paper-sepo-2026.md)、[paper-memapo-2026.md](paper_notes/paper-memapo-2026.md)。

完整时间线、两个张力的收敛（反思有用 vs 有害、大增益 vs 抛硬币）与缺口清点（bi-level/thought-driven 整块缺席）见前沿综合本体；本节只做主线视角的对接，不复制其结论，所有数字与该综合及各笔记同口径。

## 对本项目的使用约定

- 这条主线是**基线锚点谱系**，不是排行榜：APE 与 OPRO 是任何 optimizer 实验的强制下限对照；ProTeGi/TextGrad 是 critique 线对照；MIPROv2 是 instruction+demo 联合优化基线；GEPA 是当前最值得复现的强 baseline（见 [literature_map.md](literature_map.md)）。
- 任何主线方法上场前先过 **pre-optimization gate**：zero-shot baseline → headroom / noise floor 估计 → Prompt Repetition 零成本对照（非推理模式 47/70 显著胜 0 负的免费底线）；依据见[前沿综合](arxiv_2025_2026_frontier_synthesis_20260612.md)转向一（Coin Flip：72 次优化运行 49% 低于 zero-shot）。
- 引用各方法的数字时必须绑定其原始实验设置；唯一可公平横比的是把多法放进同一框架的结果（如 coin-flip，见 [classic_optimizer_methods_comparison_20260610.md](classic_optimizer_methods_comparison_20260610.md)）。
- 各方法的最小验证/复现计划已写在对应深读笔记的末节，不在本文档重复。

## 关联文档

- 七篇深读笔记：[APE](paper_notes/paper-ape-2022.md)、[ProTeGi](paper_notes/paper-protegi-2023.md)、[OPRO](paper_notes/paper-opro-2023.md)、[DSPy](paper_notes/paper-dspy-2023.md)、[TextGrad](paper_notes/paper-textgrad-2024.md)、[MIPROv2](paper_notes/paper-miprov2-2024.md)、[GEPA](paper_notes/paper-gepa-2026.md)
- 主线外锚点（2026-06-12 结构评审补读）：[GrIPS（前史：免梯度编辑搜索）](paper_notes/paper-grips-2022.md)、[PromptAgent（规划搜索缺环）](paper_notes/paper-promptagent-2023.md)
- 主线之后的时间切片：[arXiv 2025/2026 前沿深读综合](arxiv_2025_2026_frontier_synthesis_20260612.md)（四个转向 + 两个张力 + 缺口清点）
- 进化算法分支与同框架横比：[classic_optimizer_methods_comparison_20260610.md](classic_optimizer_methods_comparison_20260610.md)
- 文献全景与优先阅读顺序：[literature_map.md](literature_map.md)
- "文本梯度"隐喻的批判：[paper-textual-gradients-flawed-metaphor-2025.md](paper_notes/paper-textual-gradients-flawed-metaphor-2025.md)
- 字段与证据口径：`docs/insight_field_standard.md`
