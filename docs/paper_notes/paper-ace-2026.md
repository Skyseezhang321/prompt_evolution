# Paper Note: ACE / Agentic Context Engineering

论文：Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models（Stanford + SambaNova + UC Berkeley，ICLR 2026）

链接：https://arxiv.org/abs/2510.04618

source_id：paper-ace-2026

关联 issue：无

线索贡献者：user-request + web-search（2025/2026 年度代表作选题，用户确认 ACE 优先于 DGM/SEAL/自进化综述）

新颖性判断：actionable-method（兼含对 [[paper-gepa-2026]] "更短 prompt 更好"叙事的 contradiction 信号）

阅读日期：2026-06-12

reviewed_by：Claude

local_pdf_path：`local_sources/raw/arxiv_papers/2510.04618/paper.pdf`

local_pdf_sha256：`51050CED82DF75C143B151262D5AF8763916968CA50374BD8FF778F40552B0AD`

local_text_path：`local_sources/raw/arxiv_papers/2510.04618/paper.txt`

local_text_sha256：`74D846F12098CDE6783A7D0C3088218A93AE1C835E4D8EE33C36994CF357E714`

evidence_level：method-results-ablation-read（正文 §1-§5 与附录 A.1-A.6、B、C 全文精读，附录 F prompt 浏览；Figure 5 leaderboard 为论文内截图，未核验原始 leaderboard 页面；正文百分比与表格数字逐一对算过，含 12.3%/11.9% 与 6.2% 等"GT±均值"口径换算）

版本说明：本地 PDF 为 v3（2026-03-29），ICLR 2026 camera-ready；初版 2025-10-06。官方代码 github.com/ace-agent/ace。

## 一句话结论

ACE 把"上下文"当作**只增不重写的结构化 playbook**来进化：Generator 产生轨迹、Reflector 提炼教训、Curator 输出**增量 delta 条目**并由非 LLM 的确定性逻辑合并，从而同时回避两个失败模式——**简洁偏置（brevity bias，优化器把领域细节压缩掉）**和**上下文坍缩（context collapse，LLM 整体重写在某一步突然把 18,282 token 的积累压成 122 token，准确率跌破不优化基线）**。在 AppWorld 上 offline 比 GEPA 高约 12 个点、adaptation 延迟降 82.3%；但它的边界同样清晰：**反馈信号不可靠时（FiNER online 无标签）ACE 自己也会跌破 base**，说明"自进化"的约束条件是反馈质量，不是优化器形态。

## 问题设定

- 任务：context adaptation——通过修改输入（系统 prompt、agent memory、领域知识）而非权重来提升 LLM/agent 表现；同时覆盖 offline（系统 prompt 优化）与 online（test-time memory 适应）两种场景。
- 优化对象：一个结构化、条目化（itemized bullets）的 context playbook；每个 bullet 含元数据（唯一 ID、helpful/harmful 计数器）和内容（可复用策略、领域概念、常见失败模式）。
- 目标指标：AppWorld 的 TGC/SGC（test-normal 与 test-challenge），FiNER/Formula/DDXPlus 的 accuracy，BIRD-SQL 的 LLM-as-judge 分；同时显式把 adaptation 延迟、rollout 数、token 成本作为一级指标。
- 约束：Generator/Reflector/Curator 三角色用**同一个模型**（DeepSeek-V3.1 非思考模式），排除"强 Reflector 向弱 Generator 蒸馏知识"的混淆，隔离"上下文构建本身"的贡献。
- 立场主张（作者观点）：与人类偏好简洁概括不同，LLM 更适合长而细的上下文、能在推理时自行筛选相关性，所以 context 应当保留领域启发式而非压缩掉。

## 方法摘要

- 候选如何生成：Generator 对新 query 产生推理/执行轨迹，并标注 playbook 中哪些 bullet 有用、哪些误导；Reflector 从成功与失败中提炼具体教训（可迭代精炼，上限 5 轮），并给每个被引用 bullet 打 helpful/harmful/neutral 标签；Curator 把教训合成为**delta 条目**（只产出新增 bullet，不重写全文）。
- 反馈如何获得：有标签时用 ground truth 对比；无标签时利用执行反馈（代码运行成败、单元测试报告、环境信号）。AppWorld 的 Reflector prompt 显式要求从环境反馈中固化 API 输出 schema 这类"硬知识"。
- 如何选择/合并候选：**不做候选间竞争选择**——delta 条目由轻量非 LLM 逻辑确定性合并进 playbook（append 新 ID、原地更新计数器），多个 delta 可并行合并；这是与 GEPA"生成候选→验证集选优"范式的根本差异（附录 C.1）。
- 是否使用记忆/archive：playbook 本身就是记忆。grow-and-refine 机制控制膨胀：语义嵌入去重 + 按需修剪（proactive 每次 delta 后，或 lazy 超窗时）。
- 是否优化 optimizer 自身：否。三角色的 prompt 固定（附录 F），进化的只有 playbook 内容。
- 超参：batch size 1（每样本产出一个 delta），Reflector 精炼与 offline epoch 上限均为 5；online 场景可用 offline warmup 初始化 playbook。

## 实验设置

- 数据集：AppWorld（agent：API 调用、代码生成、环境交互）；FiNER（XBRL 139 类金融实体标注）、Formula（金融数值推理）；附录补 DDXPlus（医疗诊断）、BIRD-SQL（text-to-SQL，各取 1000 训练样本）。
- 模型：默认 DeepSeek-V3.1-671B（非思考模式，三角色同模型）；附录 A.1 换 GPT-OSS-120B、GPT-5.1、Llama-3.3-70B-Instruct 验证可移植性。
- baselines：Base LLM/ReAct（官方实现）、ICL（many-shot，窗口装满为止）、MIPROv2（DSPy 官方实现 auto="heavy"）、GEPA（同上）、Dynamic Cheatsheet（DC-CU，官方实现）。
- train/dev/test 切分：全部沿用各 benchmark 官方切分。offline 在训练集优化、测试集 pass@1 评估；online 在同一打乱顺序的测试集上逐样本"先预测、后更新"。
- 成本或调用次数：论文直接报告（§4.7、附录 A.3）——offline AppWorld：ACE 延迟 9,517s vs GEPA 53,898s（-82.3%），rollouts 357 vs 1,434（-75.1%）；online FiNER：ACE 延迟 5,503s vs DC 65,104s（-91.5%），token 成本 $2.9 vs $17.7（-83.6%）。细粒度对账（1 epoch + 1 精炼轮配置）：adaptation 阶段 ACE 输入 token 39.3M vs GEPA 204.1M（-80.8%），GEPA 大头花在候选验证循环（验证占 139.1M 输入 token）。

## 主要结果

论文直接报告：

- AppWorld（Table 1，DeepSeek-V3.1）：ReAct 基线平均 42.4；offline ACE 有标签 59.4（+17.0），**无标签 57.2（+14.8）**；同期 ICL 46.0、GEPA 46.4。online ACE（无标签 + offline warmup）59.5（+17.1），DC 51.9。正文"超 ICL 12.3%、超 GEPA 11.9%"是 ACE 有/无标签两行均值（58.3）减 baseline 的口径。
- AppWorld leaderboard（2025-09 快照，Figure 5）：ReAct+ACE 平均 59.4 对榜首 IBM CUGA（GPT-4.1 生产级 agent）60.3，基座却是开源 DeepSeek-V3.1；online ACE 在 test-challenge 上 TGC 反超 8.4、SGC 反超 0.7。作者明确声明 CUGA 仅作背景参照、非方法学 baseline。
- 金融（Table 2）：base 平均 69.1；offline ACE 有标签 81.9（+12.8，其中 Formula 67.5→85.5），GEPA 72.5、MIPROv2 70.9；正文"平均超 10.9%"为 ACE 81.9 对三个 baseline 均值的差。online ACE 有标签 76.6。
- **负结果（论文如实报告）**：FiNER online 无标签时 ACE 67.3（-3.4，低于 base 70.7），DC 更差（65.4，-3.7）；作者归因为缺少可靠反馈时 context 被虚假信号污染。
- 消融（Table 3 + Table 18）：去掉 Reflector 与 multi-epoch 后 offline 平均 59.4→55.1；**去掉增量更新（改整体重写）test-normal 平均 70.3→56.9**，相对降幅 TGC -11.7%、SGC -27.8%（附录 C.2 口径），是单项贡献最大的设计。
- 鲁棒性（附录 A.4）：换更弱 Reflector（GPT-OSS-120B）仍 +5.9（vs 默认 +7.6、GPT-5.1 +7.8）；注入对抗性"有害反思"，每 5 步一次仍 +5.4，只有每步注入才跌破 base（66.7 vs 70.7）——退化是渐进的。
- 跨模型（附录 A.1）：四个模型族方向一致。最有信息量的是 Llama-3.3-70B FiNER：**GEPA -3.09、DC -3.5（双双跌破 base），ACE +2.4**——弱模型上反思类优化器更易翻车，ACE 的确定性合并提供了下限保护。GPT-5.1 上 online ACE 也最强（AppWorld test-normal 平均 +11.6）。
- 跨领域（附录 A.2）：DDXPlus 75.2→90.2（+15.0，GEPA 仅 +1.2）；BIRD-SQL 47.8→52.9（+5.1，GEPA 52.2，且 GEPA 在 Moderate/Challenging 子集占优）——结构化代码生成上 ACE 优势收窄。
- 服务成本（§4.7）：评估期 ACE 原始输入 token 比 GEPA 多 117.4%（playbook 长），但 GPT-5.1 prompt caching 实测 91.8% 输入 token 命中缓存，计费输入成本相对原始 token 量降 82.6%——"长 context ≠ 线性贵"。

需要推断（our-inference）：

- Table 19（敏感性，5 轮精炼）test-normal 平均 67.6，与 Table 1 同名配置的 70.3 不一致，提示单次运行方差可能在 2-3 个点量级；论文未报告多 seed 方差，单点对比的小差距（如 BIRD-SQL ACE 52.9 vs GEPA 52.2）不应过度解读。
- Table 12 的 ACE "rollouts 2,075（+42.6%）"与 Table 4(a) 的"357（-75.1%）"口径不同：前者把 Generator/Reflector/Curator 的 LLM 调用都计入且为 1-epoch 配置，后者是环境 rollout。引用 ACE 省 rollout 结论时必须带口径。

## 失败案例和局限

论文直接承认（§5 + 表格）：

- **反馈质量是硬约束**：Reflector 提不出有意义教训时 playbook 会变噪声甚至有害；FiNER online 无标签的 -3.4 是实锤。这与 DC 的依赖结构相同。
- **不是所有任务都需要富上下文**：HotPotQA 这类任务更受益于简短高层指令，Game of 24 只需一条可复用规则，长 playbook 冗余。ACE 的适用域是需要细粒度领域知识、复杂工具使用、环境特定策略的任务。
- 弱模型（Llama-3.3-70B）上绝对收益缩小（+2.4），因为中间反思质量随基座能力下降。
- our-inference：所有 agent 主结果都在 AppWorld 单一环境 + ReAct 单一脚手架上；leaderboard 对照是 2025-09 快照，时效有限。playbook 的可解释性声明（selective unlearning 等）是 Discussion 展望，未做实验。

## 洞见卡片

```yaml
insight: 上下文坍缩是"用 LLM 整体重写记忆"这一操作的结构性风险，与具体方法无关；解法是把更新算子改成"增量 delta + 确定性合并"。
evidence_type: failure-case + ablation
paper_evidence:
  section: "2.2, 3.1, A.5, C.2"
  table_or_figure: "Figure 2, Table 18"
  quote_or_paraphrase: "DC 在 AppWorld 上第 60 步 context 为 18,282 token、准确率 66.7，下一步坍缩到 122 token、57.1，低于不优化的 63.7；ACE 去掉增量更新后 test-normal 平均 70.3→56.9。"
mechanism: 让 LLM 重写越来越长的累积文本时，模型的摘要先验会压缩细节；一次坏重写即不可逆清空积累。增量更新把"保留旧知识"从 LLM 行为约束变成数据结构保证。
actionable_rule: 任何 prompt/memory 自进化循环中，凡是"把全文交给 LLM 重写"的步骤都应换成"LLM 只产出 delta、合并由确定性代码完成"，并保留逐条 ID 与版本。
counterexample_or_limit: 增量结构需要去重/修剪对冲膨胀；论文显示 dedup 阈值 50-90%、修剪触发 10K-100K token 间性能稳定，但这是 FiNER 单任务证据。
minimal_experiment: 同一 memory 循环跑两臂——LLM 全文重写 vs delta+确定性合并，记录每步 context token 数与准确率曲线，观察坍缩事件。
confidence: high
```

```yaml
insight: "更短的 prompt 更好"不是普适规律；简洁是优化目标偏置（brevity bias），在 agent 与知识密集任务上压缩会丢掉决定成败的领域细节。
evidence_type: direct-result + author-claim
paper_evidence:
  section: "1, 2.2, 4.3, 4.4, 5"
  table_or_figure: "Table 1, Table 2, Figure 3"
  quote_or_paraphrase: "GEPA 把 brevity 当优点（见 [[paper-gepa-2026]] 主结果'prompt 比 MIPROv2 短 9.2 倍'），但 ACE 的长 playbook 在 AppWorld 上比 GEPA 高约 13 个点、Formula 高 14 个点；§5 同时承认 HotPotQA/Game-of-24 类任务简短指令更好。"
mechanism: 单条"优化后指令"必须把策略压缩进有限篇幅，与样本无关的领域启发式（API schema、edge case、失败模式）首先被牺牲；条目化 playbook 允许推理时按需取用，把"选什么"推迟到 inference。
actionable_rule: 选优化范式前先判断任务的"知识密度"——失败主要因为缺领域细节/工具规则的任务用累积式 playbook；失败主要因为指令歧义的任务用 GEPA 类短指令进化。两者不是替代关系。
counterexample_or_limit: 与 [[paper-causal-edit-level-2026]]（数学/多跳任务复杂化编辑有害）和 §5 自述边界一致：低知识密度任务上长 context 是纯成本。BIRD-SQL 的 Moderate/Challenging 子集 GEPA 反超，提示结构化生成任务边界更近。
minimal_experiment: 同一任务对照 GEPA 式短指令 vs ACE 式 playbook，按"任务所需领域规则条数"分桶看增益交叉点。
confidence: high-for-agent/knowledge-intensive; medium-for-boundary-position
```

```yaml
insight: 无监督自进化的真实前提是"环境能提供可验证反馈"，不是"方法支持无标签运行"。
evidence_type: direct-result + failure-case
paper_evidence:
  section: "4.3, 4.4, 5"
  table_or_figure: "Table 1, Table 2"
  quote_or_paraphrase: "AppWorld（有代码执行成败信号）无标签 ACE 仍 +14.8；FiNER（无执行信号、只剩自评）无标签 ACE -3.4、DC -3.7，双双跌破 base。"
mechanism: Reflector 的教训质量上限由反馈信号决定；执行反馈是外部世界的 ground truth 替代品，自评反馈则可能把幻觉固化进 playbook 并随积累放大。
actionable_rule: 评估"self-improving"声明时，先问反馈信号来源：执行/测试/环境信号 ≈ 可用；纯 LLM 自评 ≈ 按 [[paper-vista-reflection-dark-2026]] 与 [[paper-llm-prompt-optimizers-2024]] 的反例预设会退化，需要先建反馈通道再上优化器。
counterexample_or_limit: Formula online 无标签仍 +11.0（数值可自校验），说明边界在"任务输出可否机器验证"，不是简单的有无标签二分。
minimal_experiment: 同一任务三臂——GT 标签反馈 / 执行反馈 / 纯自评反馈，跑相同 ACE 循环，看 playbook 污染速度。
confidence: high
```

```yaml
insight: 优化预算的大头未必在"产生学习信号"，候选验证循环本身可能是最大成本项；放弃候选竞争、改用无验证的增量合并，是一种用结构换预算的设计。
evidence_type: direct-result
paper_evidence:
  section: "4.7, A.3, C.1"
  table_or_figure: "Table 4, Table 12"
  quote_or_paraphrase: "GEPA adaptation 期 204.1M 输入 token 中 139.1M 花在候选验证（57 条验证集反复评估）；ACE 无验证循环，输入 token -80.8%、延迟 -82.3%。"
mechanism: 候选选择范式必须为每个候选付验证成本（与 [[paper-gepa-2026]] '大部分 rollout 花在验证'自述互证）；ACE 用"每条 delta 默认进入 + 计数器/去重事后治理"替代事前验证，赌的是单条 bullet 的错误代价低且可被后续反思纠正。
actionable_rule: 设计优化器时把 token 账分三栏记录（信号产生/候选验证/更新执行）；验证占比过高时，考虑降低验证集大小或转向增量合并 + 事后修剪。
counterexample_or_limit: 无验证意味着坏条目会先进 playbook 再被治理，A.4 显示持续对抗注入下会跌破 base；高风险场景仍需最小验证门或 [[paper-spear-2026]] 式 rollback。
minimal_experiment: ACE 式无验证合并 + 周期性修剪 vs 加一道小验证门（每条 delta 在 20 样本上快验），比较净收益与总成本。
confidence: medium-high
```

## 对本项目的启发

> 字段口径见 `docs/insight_field_standard.md`；以下 insight 简引上方卡片。

- insight：①上下文坍缩是 LLM 重写算子的结构性风险（高置信）；②brevity 是偏置不是美德，适用域由任务知识密度决定（高置信）；③无监督自进化的前提是可验证反馈通道（高置信）；④候选验证可能是优化预算大头，增量合并是省预算的结构替代（中高置信）。
- conclusion：在"需要积累领域规则/工具知识"的 agent 类任务上，累积式 playbook 范式（ACE/DC 线）与候选竞争范式（GEPA/MIPROv2 线）已形成正面分野，且 ACE 单篇证据显示前者在该域占优、后者在短指令域占优。scope：AppWorld + 金融/医疗/SQL，DeepSeek-V3.1 为主、三个模型族复验；evidence_strength：A（单篇，多 benchmark + 消融）；反例：HotPotQA/Game-of-24 类任务与 BIRD-SQL 难子集。
- helpful method：**delta-only 上下文更新算子**——LLM 角色只产出带 section 的 ADD 操作（JSON），合并/去重/计数由确定性代码执行（insight_supported：①④；实现细节见附录 F Curator prompt：禁止重写全文、空操作返回空列表、bullet_id 由系统分配）。直接可抄进我们的 advisor/实验脚手架。
- anti-pattern / limit：把"长 context 太贵"当反对累积式范式的理由而不算 KV 缓存账（91.8% 缓存命中、计费 -82.6%）；把"方法支持无标签"读成"无需反馈也能自进化"（FiNER online -3.4 反例）；引用 ACE 省 rollout 时不区分环境 rollout 与 LLM 调用两种口径。
- 适用场景：多轮 agent、领域知识密集（金融/医疗/工具 API）、有执行或可机器验证反馈的任务；offline warmup + online 持续适应组合收益最大（59.5 vs 无 warmup 56.1）。
- 误用风险：低知识密度任务上 playbook 纯增成本；弱基座模型反思质量差，收益缩水（Llama-3.3-70B +2.4）；无去重/修剪的裸增量会膨胀（论文阈值证据仅 FiNER 单任务）。

## 最小验证或演示计划

- 要验证的 insight / method：卡片①（重写 vs delta 的坍缩对照）与卡片③（反馈通道三臂）。
- 最小验证任务：复用本项目既有结构化抽取任务（有 per-row parser/rubric 信号，约 100-300 样本），online 逐样本适应 60-100 步。
- 需要实现的模块：itemized playbook 存储（ID + helpful/harmful 计数）；Reflector prompt（含 bullet 打标）；Curator ADD-only prompt + 确定性合并器；context token 曲线与坍缩事件监测；嵌入去重器。
- 观察指标：每步准确率、context token 数、坍缩事件（单步 token 降幅 >80%）、坏条目存活时长。
- 预计风险：嵌入去重误合语义相近但规则相反的条目；自评反馈臂可能需要提前停止；与 [[paper-memapo-2026]] 的双记忆设计部分重叠，需在实验计划中标明对照关系。
