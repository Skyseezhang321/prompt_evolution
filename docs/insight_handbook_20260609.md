# Prompt 优化与自进化：读者向洞见手册

日期：2026-06-09

## 这本手册是写给谁的

你懂 AI 工具、会写 prompt、可能受过一些学术训练，但不是 prompt 优化这个细分领域的研究者。市面上关于「自动优化 prompt」「prompt 自进化」「context engineering」的说法很多，真假混杂。这本手册想帮你建立一套**能自己判断真假、能直接上手**的认知。

它和仓库里另一份 [Insight / Conclusion / Helpful Method 候选清单](insight_method_catalog_20260609.md) 是配套关系：那份是给研究者用的结构化中间层（YAML 字段、证据等级），这份是给读者用的——**每条洞见都用一个能看懂的例子讲透**。两份引用的是同一批论文笔记和源码审计，结论一致，只是写法不同。

## 怎么读这本手册里的「证据」

为了不把话说满，每条洞见会标三件事：

- **论文证据强度**：`A`（多篇互证或有消融）/ `B`（单篇或工程实践）。这是「论文设置下成立」，不是「在你的任务上一定成立」。
- **本项目是否已验证**：截至 2026-06-09，**全部为「否」**。本项目还没跑复现实验，所以任何论文里的提升比例都不能写成「我们已经证明」。
- **`recent-preprint` 标记**：2026 年的 arXiv 新稿结论还需独立复现，看到这个标记请额外打折。

另外，**手册里所有带「示意」字样的 prompt、数字、对话，都是为了讲清概念虚构的，不是真实实验数据**。真实数据只出现在「论文怎么说」一栏，且都给了出处文件。

## 一句话总结论

如果你只记一句话：**自动优化 prompt 不是「让模型把 prompt 改好」这么一回事，而是一套「先判断值不值得优化 → 把失败变成可编辑证据 → 生成多个候选并用验证集筛选 → 记录版本与回滚」的工程纪律。缺了纪律，「优化」往往只是改写，甚至是退步。**

下面 14 条洞见按你实际会遇到的顺序展开（13、14 为 2026-06-11 随主报告 v4 新增的 Part G，01–12 编号与内容未动）。

---

## Part A. 动手之前：这个任务值不值得优化？

### 洞见 01 · 先确认有没有提升空间，再花钱跑优化器

> 对应清单 I-01｜论文证据强度 A｜本项目已验证：否

**反直觉点**：自动优化 prompt 不是稳赚的。在某些设置下，它有接近一半的概率让你的 prompt **比什么都不做（zero-shot）还差**。

**它具体长什么样（示意）**
你要把客服工单分成「投诉 / 咨询 / 退款」三类。初版 prompt 很朴素：

```
把下面的工单分到：投诉、咨询、退款。工单：{text}
```

30 条样本一测，准确率 82%。你上了个自动优化器，它跑了 6 轮，产出一个又长又「专业」的新 prompt（加了一堆边界规则）。dev 上涨到 87%，你很开心——**但换到没见过的 100 条测试集，掉到 79%，比最初那句话还低**。那 5 个点是优化器在 30 条小样本的噪声里「捡」到的，不是真本事。

**论文怎么说**
- *Prompt Optimization Is a Coin Flip*（2026，`recent-preprint`）：在 Claude Haiku 4.5 上，**72 次优化运行里 49% 低于 zero-shot**；在自由文本任务上（XSum、WildBench）最好的提升只有 +0.6、+0.7，落在测量噪声里。唯一稳赚的是 HelpSteer2 这种**严格 JSON/rubric 输出**任务，六种方法全部超过 zero-shot（最高 +6.8）。来源：[paper-coin-flip-2026.md](paper_notes/paper-coin-flip-2026.md)
- ProTeGi（2023）自己也承认：学习曲线大约 **3 步达峰**，之后往往在训练数据上过拟合。来源：[paper-protegi-2023.md](paper_notes/paper-protegi-2023.md)

**你该怎么做**（花优化器的钱之前，先做 5 分钟体检）
1. 跑 zero-shot 和你手写的 baseline，各记一个分。
2. 手写或让模型生成 10–20 个候选 prompt。
3. 用**同一批 20 条留出样本**给所有候选打分。
4. 看两个数：**最高候选比 zero-shot 高多少**（headroom）、**候选之间分数抖动多大**（noise floor）。
5. 如果「最大提升」还没超过「抖动幅度」——**停**。这个任务大概率没有可优化空间，你优化出来的只是噪声。

**边界**：有些任务的收益要靠多轮搜索才能发现组合结构，简单体检会**低估**它；阈值必须按你的样本量和评分器重新校准，不能跨任务硬套。

---

### 洞见 02 · 第一批要验证的，先选「能客观打分」的任务

> 对应清单 I-11｜论文证据强度 A/B｜本项目已验证：否

**反直觉点**：同样是优化 prompt，**任务类型决定了你能不能看清优化有没有用**。开放写作类任务即使优化了，你也分不清是真变好还是评委口味变了。

**它具体长什么样（示意）**
两个任务摆在你面前：

- 任务甲：「把工单总结成一句话」。两个候选 prompt 产出的总结都「读起来还行」，你只能靠另一个模型当评委打分——而评委今天偏好长一点的，明天偏好短一点的，你根本不知道分数变化来自 prompt 还是评委。
- 任务乙：「把工单抽成 `{intent, entities, urgency}` 的 JSON」。某个候选漏抽了 `urgency` 字段，你**一眼就能定位**：field F1 在 urgency 这一列掉了，JSON 还是合法的，问题就出在紧急度判定规则上。

任务乙能把失败拆成「字段漏抽 / 标签错 / 格式破坏 / 过度推断」，每一类都能对应到 prompt 的具体改动。所以第一批验证选乙，不选甲。

**论文怎么说**
- *Coin Flip*（2026，`recent-preprint`）：唯一让所有方法都超过 zero-shot 的，是 HelpSteer2 这种**结构化 JSON/rubric 输出**任务（+6.8）；自由文本任务全在噪声里。来源：[paper-coin-flip-2026.md](paper_notes/paper-coin-flip-2026.md)
- *APO for KG Construction*（2025）：在结构化三元组抽取上，同数据集优化能拿到 **triple F1 +16%**；但换数据集只剩 **约 1%**——结构化任务收益清楚，可跨域迁移仍要单独测。来源：[paper-apo-kg-construction-2025.md](paper_notes/paper-apo-kg-construction-2025.md)

**你该怎么做**
- 第一批最小验证选：信息抽取（JSON schema）、文本分类、工具调用——评分客观、错误可拆解。
- 暂时别用开放生成（写作、摘要、对话）当第一块试验田，它的因果最难看清。

**边界**：开放生成任务很重要，只是不适合作为「因果清晰」的第一批验证；等结构化任务上的方法跑通了再扩展。

---

## Part B. 怎么从失败里学到东西

### 洞见 03 · 把失败样本变成「可编辑的证据」，不要只记一个分数

> 对应清单 I-02｜论文证据强度 A｜本项目已验证：否

**反直觉点**：分数只告诉你「坏了」，它不告诉你「该改哪里」。真正驱动 prompt 改进的，是对失败样本的**文字诊断**，不是 accuracy 那个数字。

**它具体长什么样（示意）**
工单：「我要退货并且投诉你们客服态度」。模型抽出 `intent: 投诉`，漏了 `退款`。

- **只记分数**：这条 = 错。你拿到的信息是一个红叉，无从下手。
- **记成可编辑证据**：写一句诊断——「**当一条工单同时包含『动作请求』和『情绪表达』时，模型倾向只抓情绪（投诉），漏掉动作（退款）**」。这句话直接告诉你 prompt 该补什么：明确要求「一条工单可以有多个 intent，动作类和情绪类要分别判断」。

后者就是「文本梯度 / critique」——但注意，它是**改写方向的线索**，不是数学意义上的梯度，别把它当成精确的因果解释。

**论文怎么说**
- ProTeGi（2023）：用失败样本生成自然语言「gradient」再编辑 prompt，**比原始 prompt 平均高 15.3%，最高可提升 31%**。来源：[paper-protegi-2023.md](paper_notes/paper-protegi-2023.md)
- 反面证据同样有力：ProTeGi 论文里，**让 AutoGPT「自己反馈、自己改」6 轮，反而把起始 prompt 改差了**——可见「让 agent 自己改」不等于有效优化。来源：[paper-protegi-2023.md](paper_notes/paper-protegi-2023.md)
- 「文本梯度其实是个有缺陷的比喻」这一点，有专门论文论证。来源：[paper-textual-gradients-flawed-metaphor-2025.md](paper_notes/paper-textual-gradients-flawed-metaphor-2025.md)

**你该怎么做**
每个 eval case 至少记五样：`prediction`、`gold`、`error_type`（失败类型）、`critique`（一句话诊断）、`candidate_prompt_id`（这次改写编号）。先把 20 条失败样本整理成一张「失败类型表」，再让优化器**只基于这张表**改 prompt。

**边界**：critique 会带评委偏见，必须绑定到具体样本和指标；不能把一句诊断当成「真实因果」写进结论。

---

### 洞见 04 · 先列「失败根因假设」，再改 prompt

> 对应清单 I-03｜论文证据强度 A｜本项目已验证：否（`recent-preprint` 证据）

**反直觉点**：反思式优化器最常见的翻车，不是信息不够，而是**它一开始就猜错了方向，然后在错误方向上越改越自信**。

**它具体长什么样（示意）**
抽取任务有 30% 的样本 `urgency` 判错。

- **直接让模型改**：「请优化这个 prompt 让 urgency 更准」→ 模型加了一句「请仔细判断紧急度」。没用，因为它根本没搞清为什么错。
- **先列根因假设，每个假设单独改一版**：
  - 假设 A：schema 没定义清楚「紧急」的判定标准 → 候选 A 补上判定规则。
  - 假设 B：缺少边界示例 → 候选 B 加 2 个「看起来急但其实不急」的例子。
  - 假设 C：模型把「尽快」「马上」这类中性词一律当紧急 → 候选 C 明确这些词不单独构成紧急。
  
  三个候选都在 minibatch 上验证，谁真的把那 30% 拉回来了，就采用谁。

关键动作是**把「猜原因」和「改 prompt」拆成两步**，而不是让同一个反思器一口气给出最终答案。

**论文怎么说**
- VISTA / *Reflection in the Dark*（2026，`recent-preprint`）：GEPA 在一个有缺陷的 GSM8K 种子 prompt 上，表现**从 23.81% 掉到 13.50%**——因为真正的根因从没进入它的假设空间；VISTA 把「假设生成」和「prompt 改写」解耦后，**恢复到 87.57%**。来源：[paper-vista-reflection-dark-2026.md](paper_notes/paper-vista-reflection-dark-2026.md)
- *Are LLMs Good Prompt Optimizers?*（2024）：同样指出 LLM 的反思不一定能识别真实错误根因。来源：[paper-llm-prompt-optimizers-2024.md](paper_notes/paper-llm-prompt-optimizers-2024.md)

**你该怎么做**
对同一批失败样本，强制生成 **2–3 个互斥的根因假设**（典型三类：缺规则、缺上下文/示例、格式或定义冲突），每个假设生成一个候选 prompt，分别评分。运行记录里要存 `failure_hypothesis`，而不只是 `critique`——这样你才能区分「没想到原因」和「改写失败」。

**边界**：开放写作任务的根因边界模糊，多假设验证的成本可能超过收益；这套更适合有明确失败类型的结构化/分类任务。

---

## Part C. 别让模型骗你：候选选择与防膨胀

### 洞见 05 · 不要采用模型给的第一版，要多生几个再用验证集选

> 对应清单 I-04｜论文证据强度 A｜本项目已验证：否

**反直觉点**：LLM 生成的 prompt 候选**方差极大**。「怎么选候选」这件事，和「怎么生成候选」一样重要——甚至更重要。把选择权交给一个验证集，而不是让模型自评「我这版最好」。

**它具体长什么样（示意）**
优化器给了你 5 个改写版本。常见错误是直接用第 1 个（或模型说「推荐」的那个）。正确做法是把 5 个都放到 20 条留出样本上跑，记一张账：

| 候选 | dev 分 | 格式错误率 | prompt 长度 | 选不选 |
|---|---|---|---|---|
| C1 | 0.86 | 0% | 1.0x | 候选 |
| C2 | 0.88 | 6% | 1.2x | 弃（格式错误升高）|
| C3 | 0.87 | 0% | 2.4x | 弃（太长，疑似过拟合）|
| C4 | 0.84 | 0% | 1.1x | 弃（不如 C1）|
| C5 | 0.86 | 0% | 1.0x | 候选 |

不是只看 dev 分最高的 C2，而是综合 dev 分、格式、长度三个维度挑——这就是「Pareto 选择」的朴素版。同时永远保留一个 `best-seen`（目前见过最好的），它不会被任何新候选直接覆盖，随时能回滚。

**论文怎么说**
- ProTeGi（2023）：beam search 选择（Beam 在 Jailbreak/Liar/Sarcasm 上 **0.85 / 0.67 / 0.88**）明显优于不迭代和贪心；用 bandit（UCB 等）做候选选择也明显优于均匀随机选。来源：[paper-protegi-2023.md](paper_notes/paper-protegi-2023.md)
- 这一结构在 GEPA、PromptBreeder、EvoPrompt、SePO、MASPO 等方法里反复出现（archive / 进化搜索 / Pareto / bandit）。来源：[paper-gepa-2026.md](paper_notes/paper-gepa-2026.md)、[paper-promptbreeder-2023.md](paper_notes/paper-promptbreeder-2023.md)

**你该怎么做**
每轮至少保存：`seed`（起点）、`candidates`（候选池）、`scores`、`selection_policy`（按什么选）、`rejected_reason`（为什么弃）、`best_seen`、`rollback_point`。生成 5 个候选，按 dev 分 + 格式错误 + 长度三维选 Pareto 候选。

**边界**：搜索预算越大，越容易在 dev 上过拟合——必须有 validation/test 分层兜底。

---

### 洞见 06 · prompt 变长、变复杂，往往是过拟合，不是进步

> 对应清单 I-07｜论文证据强度 A｜本项目已验证：否

**反直觉点**：优化后的 prompt 更长、规则更多、看起来更「专业」，**很可能是危险信号**——它在给训练样本打补丁，而不是真的更强。

**它具体长什么样（示意）**
优化前（2 行）：

```
把工单抽成 {intent, entities, urgency}。urgency 取 high/medium/low。
```

优化后（优化器加了一堆规则，节选）：

```
把工单抽成 {intent, entities, urgency}。urgency 取 high/medium/low。
- 如果工单提到「发票」且包含数字，则 intent 一定是退款。   ← 来自某一条训练样本的补丁
- 如果出现「经理」「投诉」，urgency 一律设为 high。          ← 把局部特例写成全局规则
- 注意：如果用户用了感叹号超过两个，倾向 high。            ← 在拟合标注者的习惯
（……还有 9 条类似规则）
```

dev 涨了 5 分，但这些规则全是从个别训练样本反推出来的「伪规律」。换到压力测试集（OOD），掉 8 分。**判断标准不是「短就好」，而是「每条新增规则能不能对应到一类真实失败，并通过压力测试」。**

**论文怎么说**
- PrefPO（2026，`recent-preprint`）：放任优化时，TextGrad 在 IFEval-Hard 上把 prompt 撑到 **14.7 倍长度**；更严重的是 **86% 的情况下它在「prompt hacking」**（偷偷改写任务本身），而带约束的 PrefPO 只有 37%。来源：[paper-prefpo-2026.md](paper_notes/paper-prefpo-2026.md)
- TextReg（2026，`recent-preprint`）：给优化加上「正则化梯度」控制长度和规则范围后，在 Tracking Shuffled Objects 上比 TextGrad **高 +10.0 / +9.9**——管住膨胀反而更好。来源：[paper-textreg-2026.md](paper_notes/paper-textreg-2026.md)
- Edit-Level 因果分析（2026，`recent-preprint`）：加 meta-instruction 在数学类任务上与性能**负相关（-0.103）**，加 clarity 约束在逻辑任务上也负相关（-0.083）。来源：[paper-causal-edit-level-2026.md](paper_notes/paper-causal-edit-level-2026.md)

**你该怎么做**
候选选择时记录这些「卫生指标」：`prompt_length_ratio`（相对种子的长度比）、`repetition_ratio`、`edit_family`（这次改的是哪类）、`dev_test_gap`、`OOD/stress_delta`。**候选若长度超过阈值，必须说明每条新增规则绑定了哪些失败样本，并通过压力测试**，否则拒绝——哪怕它 dev 分更高。

**边界**：某些复杂任务确实需要更明确的约束；标准不是「短」，而是「必要、可追溯、不过拟合」。

---

## Part D. 到底该改什么（不只是那段 prompt）

### 洞见 07 · 有开发集时，选「给模型看的例子」常比改 instruction 更有效

> 对应清单 I-05｜论文证据强度 A｜本项目已验证：否

**反直觉点**：大家本能地去改 instruction 的措辞，却忽略了一个常常更有效的变量——**给模型看哪几个示例**。而且如果你已经有带标签的开发集，你其实已经握着优化示例的原料了，却只拿它来打分。

**它具体长什么样（示意）**
固定 instruction 不动，只把 few-shot 示例从「随便挑 3 个」换成「精挑 3 个正好覆盖易错边界的」：

```
（instruction 不变）把工单抽成 {intent, entities, urgency}。

示例 1（覆盖「动作+情绪并存」）：
  工单：要退货还要投诉客服 → {intent:[退款,投诉], ...}
示例 2（覆盖「看似紧急其实不急」）：
  工单：方便时帮我看下 → {urgency: low, ...}
示例 3（覆盖「多实体」）：
  工单：订单 123 和 456 都要改地址 → {entities:[123,456], ...}
```

光是这一步，往往就比绞尽脑汁重写 instruction 收益更大——因为示例直接展示了「决策边界」和「输出格式」，比抽象规则更容易被模型照着做。

**论文怎么说**
- *Teach Better or Show Smarter?*（2024）：在 PaLM 2 + BBH 上，**不优化 instruction、只优化示例**就达到 72.92（比基线 +12.63）；在 Gemini 1.0 Pro 上，**优化示例（75.77）超过只优化 instruction 的 ProTeGi（65.91）**；而且**精选 3 个示例 > 全部示例**——数量不等于质量。来源：[paper-teach-better-show-smarter-2024.md](paper_notes/paper-teach-better-show-smarter-2024.md)

**你该怎么做**
每个优化实验至少比较四组：`no-example`、`random-example`、`optimized-example`、`instruction + optimized-example`。固定 instruction，从候选池里搜 3 个示例，看留出表现是否超过 instruction-only。运行记录里存 `exemplar_source`、`selector`、`k`。

**边界**：上下文很紧张、示例分布偏、或示例可能泄漏敏感信息/答案时，优化示例可能伤害泛化——这时要回退到 no-example 或 random-example。

---

### 洞见 08 · 你要改的可能不是「那段 prompt」，先标清楚改的是哪个部件

> 对应清单 I-06｜论文证据强度 A/B｜本项目已验证：否

**反直觉点**：真实系统里，失败可能来自示例、检索上下文、工具描述、agent 角色、记忆或评委——**而不只是那段 system prompt**。把整个上下文窗口都叫「prompt」一起改，会让你永远无法归因。

**它具体长什么样（示意）**
你的抽取 agent 老出错。在动手改 system prompt 之前，先把这次运行拆成一张「部件清单」，并标明哪些能改、哪些冻结：

```
artifact manifest（示意）
  task_prompt        v3    [mutable]   ← 任务指令
  examples           v2    [mutable]   ← few-shot 示例
  prompting_pattern  Zero-Shot [mutable]  ← 用 Zero-Shot 还是 CoT/ReAct
  tool_schema        v1    [mutable]   ← 工具/字段说明
  context_packaging  v1    [mutable]   ← 上下文怎么拼
  evaluator          v1    [FROZEN]    ← 评委不许改（防作弊）
  safety_rules       v1    [FROZEN]    ← 安全/权限不进搜索空间
  selection_policy   pareto
```

很多时候你会发现：真正的 bug 不在 `task_prompt` 的措辞，而在 `prompting_pattern`（该用 CoT 却用了 Zero-Shot）或 `tool_schema`。先定位部件，结论才写得清「变化来自哪里」。

**论文怎么说**
- AutoPDL（2025）：**只是把 prompting pattern 换对**（而非重写指令措辞），FEVER 上 Granite 13B Instruct V2 **从 6.5% 跳到 74.0%（+67.5 个百分点）**；但同样的优化在 MBPP+ 上拒绝了 ReWOO 模式（因为它用不上执行反馈）——可见「改哪个部件」高度依任务而定。来源：[paper-autopdl-2025.md](paper_notes/paper-autopdl-2025.md)
- JTPRO（2026）、Prompt Codebooks（2026）等进一步把可优化对象扩展到 tool schema、codebook、routing。来源：[paper-jtpro-2026.md](paper_notes/paper-jtpro-2026.md)、[paper-prompt-codebooks-2026.md](paper_notes/paper-prompt-codebooks-2026.md)

**你该怎么做**
为每次优化生成一份 artifact manifest，至少拆出 `task_prompt`、`examples`、`prompting_pattern`、`tool_schema`、`context_packaging`、`evaluator`、`selection_policy`，并明确标 `mutable / frozen`。**评委、测试集、安全规则必须 frozen**——这是防 reward hacking 的底线。

**边界**：简单一次性任务不需要完整 manifest；但研究级和生产级优化需要。

---

### 洞见 09 · 工具调用出错时，要改的常是「工具说明」，不是 agent 指令

> 对应清单 I-10｜论文证据强度 A｜本项目已验证：否（`recent-preprint` 证据）

**反直觉点**：agent 把工具调错了，大多数人去改 agent 的 system prompt。但失败常常来自**工具描述和参数语义本身**——你改 agent 指令再多遍也没用。

**它具体长什么样（示意）**
agent 反复用错误格式调退款工具：传了 `amount: 99.5`，但后端要的是「分」。

- **改 agent 指令（无效）**：在 system prompt 里加「请正确填写金额」——模型照样不知道单位。
- **改工具 schema（有效）**：

```
优化前 tool schema:
  amount: number  // 退款金额

优化后 tool schema:
  amount: integer  // 退款金额，单位为「分」，例如 99 元应填 9900，不接受小数
```

工具调用的失败要拆成三层来看：**选错工具**（Tool Selection）、**填错参数**（Slot Filling）、**整体是否成功**（Overall Success）。很多时候工具选对了，错在 slot——那就该改 schema，不该改 agent 指令。

**论文怎么说**
- JTPRO（2026，`recent-preprint`）：在 ToolACE 的 1000 工具设置下，**联合优化「全局指令 + 每个工具的 schema」让 o3-mini 的整体成功率从 51.27% 提到 64.46%（+13.19）**；GPT-4o mini 上 OSR +20.30。诊断里 ETID 数据集**工具选得很准但整体成功率低，瓶颈正是 slot-filling**。来源：[paper-jtpro-2026.md](paper_notes/paper-jtpro-2026.md)

**你该怎么做**
工具 eval 必须拆成 **Tool Selection Accuracy / Slot Filling Accuracy / Overall Success Rate** 三个指标分别记。对一批相似工具构造 tool-call eval，分别测「只改全局指令 / 只改 schema / 两者联合」，看瓶颈到底在哪一层。

**边界**：外部 API 的 schema 不可改时，可以用 wrapper 文档或检索上下文来承载这些局部规则。

---

## Part E. 记忆与多 agent：更多 ≠ 更好

### 洞见 10 · 记住更多历史不等于更聪明——只有「过滤后的记忆」才有用

> 对应清单 I-08｜论文证据强度 A/B｜本项目已验证：否

**反直觉点**：给系统加「记忆」听起来总是好的，但**未经筛选地堆历史，会污染优化、造成跨任务负迁移**，还更贵。

**它具体长什么样（示意）**
- **无界记忆（错）**：把过去所有对话、所有反馈一股脑塞进上下文。结果模型把从「A 产品线」学到的退款规则，错误地套到了「B 产品线」的工单上。
- **过滤记忆（对）**：只存少量带元数据的条目：

```
memory entry（示意）
  type: success_template          # 成功模板 or error_pattern
  content: "动作+情绪并存时分别抽两个 intent"
  source_task: 工单抽取-A产品线
  applicability: 仅 intent 抽取类任务
  quality_score: 0.9
  retrieval_reason: 当前任务含多 intent
  forget_after: 2026-12-31         # 可过期
```

检索时只取 3–5 条**经过验证、且适用条件匹配当前任务**的记忆，而不是把历史全倒进去。

**论文怎么说**
- MemAPO（2026，`recent-preprint`）：**平均表现 70.7%，优于 TextGrad 的 63.6%，而且更便宜——平均成本 $0.31 vs $0.70**；把记忆拆成「成功模板 + 错误模式」双记忆后，AQuA-RAT 从 61.7 提到 82.5。来源：[paper-memapo-2026.md](paper_notes/paper-memapo-2026.md)
- ERM（2024）：**原始反馈记忆没有收益，只有过滤 + 选择性遗忘才带来增益**；带记忆的 ERM 在 LIAR 上第 7 步就到 68.6，而 ProTeGi 第 13 步才 58.5——**接近两倍速度**。来源：[paper-erm-memory-2024.md](paper_notes/paper-erm-memory-2024.md)

**你该怎么做**
记忆 schema 至少包含：`success_template` / `error_pattern`、`source_task`、`applicability_condition`、`retrieval_reason`、`quality_score`、`forget_reason`。**别直接塞历史对话**，只检索经过验证、与当前任务匹配的 3–5 条。

**边界**：高度非平稳的任务、安全敏感任务里，历史经验可能快速过期或泄漏隐私——这时遗忘策略和 opt-out 比「记得多」更重要。

---

### 洞见 11 · 多 agent 系统出错，先找「是谁的责任」，别整个系统一起重写

> 对应清单 I-09｜论文证据强度 A｜本项目已验证：否（`recent-preprint` 证据）

**反直觉点**：多 agent 系统的核心难题不是「加更多 agent」，而是 **credit assignment（责任分配）**——一个 agent 局部看起来完全正确，却可能让整个系统失败。

**它具体长什么样（示意）**
三段流水线：`抽取 agent → 补全 agent → 回复 agent`。最终回复错了。

- **错误做法**：三个 agent 的 prompt 一起重写。结果你不知道是哪一步的改动起了作用，下次还会再错。
- **正确做法**：看 trace，标注每一步的「局部是否正确 / 全局是否正确」：

```
trace（示意）
  agent_1 抽取   local_valid=✗  ← urgency 字段在这里就丢了
  agent_2 补全   local_valid=✓  （但基于错误输入，local_pass_global_fail）
  agent_3 回复   local_valid=✓  （同上）
  global_outcome=✗
```

根因在 agent_1。**只改 agent_1 的 prompt**，别动另外两个。

**论文怎么说**
- MASPO（2026，`recent-preprint`）：联合优化下平均 **70.39，超过顺序 baseline 65.31**。来源：[paper-maspo-2026.md](paper_notes/paper-maspo-2026.md)
- Temporal/Structural Credit（2026，`recent-preprint`）：在 MedMCQA 上，credit-guided 把 LLaMA3-8B 辩论 baseline **从 55.13 提到 64.63（+9.50）**；并且**无差别地更新所有轮次的 prompt 反而会掉分**——必须只更新低 credit 的角色/轮次。来源：[paper-temporal-structural-credit-mas-2026.md](paper_notes/paper-temporal-structural-credit-mas-2026.md)
- MAPRO（2025）：把多 agent prompt 优化建模为图上的 MAP 推断，沿拓扑传播 credit。来源：[paper-mapro-2025.md](paper_notes/paper-mapro-2025.md)

**你该怎么做**
trace 里保存 `role_id`、`round_id`、`local_validity`、`successor_utility`、`global_outcome`，并标出 `local_pass_global_fail` 的样本。对失败 trace 标记哪个 role/round **首次**引入错误，只允许优化器改那一块。如果 agent 之间耦合很弱，先做 coupling test，别急着联合优化。

**边界**：如果 agent 交互很弱，联合优化的成本可能不划算——先测耦合强度再决定。

---

## Part F. 怎么对待「听来的」方法

### 洞见 12 · 社媒和二手文章是「线索」，不是「证据」

> 对应清单 I-12｜论文证据强度 B｜本项目已验证：否

**反直觉点**：一个方法在 Twitter/X、知乎、Medium 上被反复转发，**只能说明它热，不能说明它有效**。二手传播会放大结论、丢掉边界和版本信息。

**它具体长什么样（示意）**
你刷到一条爆款：「GEPA 用少 35 倍的 rollout 吊打强化学习（RL）！」

- **当证据（错）**：因为转发多、说得斩钉截铁，就直接信「GEPA 能替代 RL」。
- **当线索（对）**：去翻原论文，你会发现 GEPA 其实是**反思式 prompt 进化**——靠执行轨迹生成自然语言反思 + Pareto 前沿选择，**根本不是一个 RL 系统**。「替代 RL」是传播过程中被简化出来的口号。

**论文/材料怎么说**
- 本项目的 Twitter/X 批次分析记录了这个典型误读：GEPA 在社媒上被反复框成「RL 替代品 / 35x fewer rollouts」，但其机制是用执行轨迹做反思，不是策略梯度。来源：[twitter_web_analysis_20260608.md](source_batches/twitter_web_analysis_20260608.md)

**你该怎么做**
读到一个技巧时，先抽六个字段：`dataset`、`metric`、`baseline`、`model`、`cost`、`failure_cases`。**任何一个缺失，就把它降级为「线索」**，只能当作「去查一手来源」的指针，不能进结论。进结论前必须追溯到论文、官方文档、代码，或本项目自己的实验。

**边界**：高质量工程博客如果**自带代码、数据和可复现实验**，可以升级为更强的证据——关键看它给不给可核验的细节，不看它发在哪个平台。

---

## Part G. 搜索之外：零成本变换与「优化器自身」（本版新增）

前面 12 条洞见全部围绕「搜索/优化循环」构建。这一部分补两个循环之外的盲区：一个是**不用搜索的确定性结构变换**（比所有搜索方法都便宜、却常被跳过的对照），一个是**循环里被当成空气的 optimizer 与 judge 本身**。

### 洞见 13 · 花钱搜索之前，先试零成本的确定性结构变换

> 对应清单 I-13｜论文证据强度 A｜本项目已验证：否（`recent-preprint` 证据）

**反直觉点**：有一个不改任何语义、不用任何搜索的免费变换——**把整个 prompt 原样重复一遍**——在非推理模式下跨 7 个模型 47 胜 0 负；而搜索式优化（洞见 01）有接近一半的概率比 zero-shot 还差。

**它具体长什么样（真实任务，论文数字）**

```
变换：<QUERY>  →  <QUERY><QUERY>（原样重复，无任何措辞修改）

NameIndex（50 个名字取第 25 个）：
Gemini 2.0 Flash-Lite  21.33% → 97.33%
```

机制：causal attention 下，prompt 前段的 token **看不到**后段的内容（多选题里「问题在前还是选项在前」表现不同，就是这个症状）；重复之后，第二遍的每个 token 都能注意到完整的第一遍，相当于免费给 prompt 内部加了一次「全注意」。重复发生在可并行的 prefill 阶段，所以**不增加输出长度和时延**。

**论文怎么说**
- *Prompt Repetition Improves Non-Reasoning LLMs*（Google Research，2025-12，`recent-preprint`）：关闭推理时，7 模型 × 10 benchmark 配置 **47/70 显著胜、0 显著负**（McNemar p<0.1）；**Padding 对照（把 prompt 用句点补到同等长度）无提升**——增益来自「重复」本身，不是「变长」；开启 step-by-step 推理后基本无效（**28 组里 5 胜 1 负 22 平**，推理模型本就常自发复述题目）。来源：[paper-prompt-repetition-2025.md](paper_notes/paper-prompt-repetition-2025.md)
- 对照读法：Coin Flip 显示搜索出来的措辞 model-specific 且脆弱（洞见 01），而这个确定性结构变换跨 7 模型 0 负——「结构」可能比「措辞」更可迁移（两者 setting 不同，此对比为推断）。

**你该怎么做**
1. 非推理、低延迟生产路径（分类 / 抽取 / 短 QA / 路由）先测重复 ×2；长上下文索引类任务试 ×3。
2. 把它纳入**廉价 baseline 变换集**：任何自动优化方法报告的增益，先回答「打得过这个零智能变换吗」（做洞见 01 体检时顺手一起跑）。
3. 上下文内信息顺序不可控的场景（检索结果拼接、表单转写）优先考虑——order 敏感性正是它修复的对象。

**边界**：推理模式下基本无效（还出现 1 个显著下降）；按 token 计费时**输入成本 ×2**；只重复局部（如只重复问题）无增益；超长上下文盲目翻倍会推高 prefill 成本甚至不可行；被测均为 2025 年初一代模型，新模型可能已内化复述行为——这正是本项目 P0 三臂 A/B（baseline / 重复×2 / padding）要校准的。

---

### 洞见 14 · optimizer 和 judge 本身，也是要版本化、可优化的部件

> 对应清单 I-14｜论文证据强度 A/B｜本项目已验证：否（SePO 数字为 `recent-preprint`）

**反直觉点**：你的优化系统里最不被质疑的两段 prompt，是「**负责改 prompt 的那段 prompt**」（optimizer）和「**负责打分的那段 prompt**」（judge）。它们也在决定结果——不版本化它们，实验不可复现；从不审视它们，它们就是隐藏的天花板。

**它具体长什么样（示意）**

```
运行记录只存了 task_prompt v3
optimizer_prompt / judge_prompt 没有版本号
→ 三个月后「同样配置」跑不出同样结果
→ 分数变化是任务 prompt 的功劳，还是评委口味变了？无法归因
```

**论文怎么说**
- SePO（2026，`recent-preprint`）：把 prompt agent 自己的 system prompt 也纳入演化流程并多任务预训练，五任务平均**从 Manual-CoT 的 71.89 提到 76.38**；消融去掉 self-improvement **掉回 74.94**；而 optimizer 固定的 TextGrad（70.39）、MetaSPO（71.32）平均还不如 Manual-CoT——论文正是归因于「optimizer 本身固定」。来源：[paper-sepo-2026.md](paper_notes/paper-sepo-2026.md)
- PromptBreeder（2023）：经典六法中**唯一连 mutation prompt 一起进化**（hyper-mutation）的方法，是这条思路的早期形态。来源：[paper-promptbreeder-2023.md](paper_notes/paper-promptbreeder-2023.md)
- 工程渠道互证：web_search WPI-10「judge prompt 也应被版本化、评估和优化」（B 级），GitHub autoresearch 的 ledger 把优化器配置与结果绑定（GHI-05）。来源：[web_search_platform_insight_cards_20260609.md](source_batches/web_search_platform_insight_cards_20260609.md)、[github_repo_insight_cards_20260608.md](github_repo_insight_cards_20260608.md)

**你该怎么做**
1. 给 `optimizer_prompt`、`judge_prompt`、`meta_prompt` 各建版本号，列入实验运行记录的必填字段（这条不需要独立实验，随任意 P0 实验一并生效）。
2. 评测用的 judge 与测试集一样**默认 frozen**；要改必须走独立评审与重校准，改后旧分数全部失效重跑。
3. 想优化 judge / optimizer 本身？在**开发集**上做，且与评测链路**物理隔离**。

**边界**：「优化 judge」与洞见 08 的「frozen evaluator 防作弊」不冲突——被冻结的是**评测链路**的 judge，被优化的是**开发期辅助** judge；两者必须物理分开，混用就是 reward hacking。optimizer prompt 变强依赖训练任务与评分器，指标没覆盖的行为不会自动更安全。

---

## 把这些用起来：首批最小验证

上面 14 条洞见里，最值得本项目**先动手验证**的是这几条（成本低、错误可解释、跨渠道支撑强）：

| 优先级 | 验证什么 | 对应洞见 | 最小任务 | 无论成败都能产出 |
|---|---|---|---|---|
| P0 | 优化前体检（headroom/noise floor） | 01、02、13（对照底线） | 100–300 条 JSON 抽取 | 判断有没有优化空间，校准噪声地板；顺手跑洞见 13 零成本变换当对照底线 |
| P0 | 示例优化 vs 指令优化 | 07 | 同一抽取任务 | 防止把示例的收益误记成指令的收益 |
| P1 | 直接改写 vs 根因假设改写 | 03、04 | 失败清晰的抽取/分类 | 判断根因假设是否真的改善留出表现 |
| P1 | 只看性能 vs 加卫生门 | 06 | 同一候选池 | 判断防膨胀门是否减少伪提升 |
| P2 | 工具 schema 优化 | 09 | 20–50 个相似工具 | 判断改 schema 是否优于只改全局指令 |
| P2 | 过滤记忆 vs 原始记忆 | 10 | 两个相近任务 + 一个异质任务 | 判断记忆是否降本，或带来负迁移 |

详细实验设计见 [实验计划](experiment_plan.md)；每条洞见的结构化证据卡见 [Insight / Method 候选清单](insight_method_catalog_20260609.md)。

## 给读者的三条总结

1. **「优化」之前先问「值不值得」**：headroom 没超过 noise floor 就别花钱（洞见 01）。
2. **改 prompt 的本质是「证据 → 假设 → 多候选 → 验证集筛选 → 可回滚」**，不是「让模型润色一下」（洞见 03–06）。
3. **更长、更多、更复杂都不是默认的好**：更长的 prompt、更多的记忆、更多的 agent，都要先证明它没带来过拟合、污染或归因困难（洞见 06、08、10、11）。

---

*本手册所有标「示意」的例子均为讲解虚构，非本项目实验数据；论文数字为各论文设置下的结果，非本项目复现；`recent-preprint` 结论需独立复现后才能采信。证据追溯入口见各条「论文怎么说」中的文件链接。*
