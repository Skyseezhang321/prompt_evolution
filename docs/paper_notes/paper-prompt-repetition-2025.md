# Paper Note: Prompt Repetition Improves Non-Reasoning LLMs

论文：Prompt Repetition Improves Non-Reasoning LLMs（Yaniv Leviathan, Matan Kalman, Yossi Matias — Google Research；Leviathan/Kalman/Matias 即 speculative decoding 原班作者）

链接：https://arxiv.org/abs/2512.14982 （v1，2025-12-17）

source_id：paper-prompt-repetition-2025

关联 issue：无

线索贡献者：user_provided_example（用户口头线索「Google 写过重复 prompt 大幅提升非思考模型的论文」；2026-06-09 已按摘要级登记进 `source_inventory.md`，2026-06-11 用户要求深读闭环）

新颖性判断：actionable-experiment（零实现成本的固定变换，可直接进入本项目最小 A/B 实验；同时可作为所有 APO 方法的「零智能 baseline 变换」对照）

阅读日期：2026-06-11

reviewed_by：Claude

local_pdf_path：`local_sources/raw/arxiv_papers/2512.14982/paper.pdf`

local_pdf_sha256：`5DD7B024BA18D86A4CA3855620B34BF41DC5905C27A9C6866D971F29AE7E0815`

local_text_path：`local_sources/raw/arxiv_papers/2512.14982/paper.txt`

local_text_sha256：`8CD9BB899D660B42E418A97225EDDF6A6141C639FFEF022A70F896139DD3F40C`

evidence_level：method-and-results-read（正文 4 页 + 附录 A.1–A.4 全文精读；Figure 1/4 经 PDF 渲染核验面板结构与定性方向，正文文字陈述的汇总数字（47/70 胜 0 负、5 胜 1 负 22 平、NameIndex 21.33%→97.33%）与图一致；Figure 1–3 为位图、图内逐格数字未转录，本笔记不引用任何逐格数字）

## 一句话结论

把整个 prompt 原样重复一遍（`<QUERY>` → `<QUERY><QUERY>`），在**关闭推理**时对 7 个主流模型 × 10 个 benchmark 配置取得 47/70 显著提升、0 显著下降（McNemar p<0.1），且**不增加输出长度和端到端时延**（重复只发生在可并行的 prefill 阶段）；机制解释是 causal LM 中靠前的 token 看不到靠后的 token，重复让每个 prompt token 都能注意到完整上下文。代价是输入 token 翻倍（论文未讨论计费成本——our-inference：按 token 计费的输入成本约 ×2）。**开启 step-by-step 推理后收益基本消失**（28 组里 5 胜 1 负 22 平），因为推理模型本来就常自发复述题目。

## 问题设定

- 任务：零样本 prompting 评测（非优化循环）：ARC-Challenge、OpenBookQA、MMLU-Pro（多选题各分 question-first / options-first 两种排列）、GSM8K、MATH，加 2 个自建长上下文索引任务 NameIndex（50 个名字取第 25 个）和 MiddleMatch（N=40、K=10，找两个名字正中间的元素）。
- 优化对象：无优化——一个固定的、任务无关的 prompt 结构变换。
- 目标指标：accuracy；显著性判定用 McNemar 检验 p<0.1。
- 约束：不增加生成 token 数与时延；输出格式不变，可 drop-in 替换现有系统的 prompt。

## 方法摘要

- 候选如何生成：无搜索、无候选——单一确定性变换 `<QUERY><QUERY>`。另测 3 个变体：Verbose（中间加 "Let me repeat that:"）、Repetition ×3、Padding（用句点补到同等长度，作排除「只是变长」的对照）。
- 反馈如何获得：无反馈回路。
- 如何选择候选：不适用。
- 是否使用记忆/archive：否。
- 是否优化 optimizer 自身：否。
- 机制假设（论文陈述）：①causal attention 下 prompt 前段 token 无法注意后段（question-first vs options-first 表现不同即症状），重复后第二遍的每个 token 都能注意完整第一遍，近似给 prompt 内部加了「第二遍全注意」；②RL 训练出的推理模型经常自发复述用户请求，把这一行为前移到可并行的 prefill 阶段即免费获得收益（作者明言与他们的 speculative decoding 动机同源）。

## 实验设置

- 数据集：上述 7 个 benchmark，多选题双排列后共 10 个配置；自建任务模板见附录 A.3。
- 模型：Gemini 2.0 Flash / Flash-Lite、GPT-4o / GPT-4o-mini、Claude 3 Haiku / Claude 3.7 Sonnet、DeepSeek V3，共 7 个；全部走各家官方 API，运行时间 2025 年 2–3 月。
- baselines：原 prompt；Padding 对照。
- train/dev/test 切分：无——纯评测论文，无任何训练或搜索。
- 成本或调用次数：未报告每 benchmark 样本量、总调用次数和 API 费用；输入长度约 ×2（×3 变体约 ×3）。时延实测不增（例外：Claude 两个模型在超长请求上时延上升，作者归因 prefill 变长）。

## 主要结果

- 关闭推理：47/70 显著胜、0 显著负；7 个模型全部受益（论文正文陈述，Figure 1 面板结构经核验为 10 配置 × 7 模型）。
- 多选题中 options-first（问题在选项之后）提升大于 question-first——order 敏感性被修复的直接证据。
- NameIndex 上 Gemini 2.0 Flash-Lite 从 21.33% 提至 97.33%（正文数字；这是用户记忆中「大幅提高」的出处级例子）。
- ×3 变体在 NameIndex/MiddleMatch 上常显著优于 ×2（而 ×2 已显著优于 baseline）；Verbose 与 vanilla 相近。
- Padding 不提升 → 增益来自「重复」本身而非输入变长。
- 开启 step-by-step：28 组里 5 胜 1 负 22 平（Figure 4 经核验）——与显式推理高度重叠、基本不叠加。
- 输出长度（均值与中位数）与时延在所有方法上基本持平（Figure 2/3，趋势级核验）。

## 失败案例和局限

- 推理模式下几乎无收益且出现 1 个显著下降；具体是哪个模型×任务组合论文未指明（未报告）。
- 长 prompt 下重复会推高 prefill 时延，极长 prompt 可能直接不可行（论文脚注 3）。
- 相关工作给出的边界：Shaier 2024 只重复 question 部分无增益（arXiv 2412.07923）——必须重复**整个 prompt**；Xu et al. 2024 的 RE2「请再读一遍题」是让模型自己重读，与本文在输入侧物理重复不同。本文未与这两者做同框架对比实验（未报告）。
- 被测模型均为 2025 年初一代；对此后模型（可能已在训练中内化复述行为）是否仍成立未知（our-inference）。
- 每 benchmark 样本量未报告，无法独立复算 McNemar 显著性。

## 对本项目的启发

> 字段定义与 insight / conclusion / helpful method 的区分口径见 `docs/insight_field_standard.md`。

- insight：causal attention 导致的「信息顺序敏感」是 prompt 性能的一个**结构性**失效来源，与措辞质量无关；一次完整重复可以在完全不动语义的情况下修复它（证据：options-first 配置提升显著大于 question-first，Padding 对照无效）。这把「prompt 结构/顺序」从工程直觉升级为有受控对照的可操作变量，与 [[paper-modular-prompt-optimization-2026]] 的 section-local 编辑方向互证。
- conclusion：在 2025 年初一代主流模型的**非推理模式**下，整 prompt 重复 ×2 是跨模型稳健正向（47/70 胜 0 负）、零输出成本的默认变换；开启推理后增益基本消失（5/28）。值得注意的对照：[[paper-coin-flip-2026]] 显示 APO 优化收益脆弱且 model-specific，而这里一个静态变换跨 7 模型 0 负——「确定性结构变换」可能比「搜索出来的措辞」更可迁移（两者 setting 不同，此对比为 our-inference）。
- helpful method：把 `<QUERY><QUERY>`（或 Verbose 形式）纳入本项目的**廉价 baseline 变换集**——任何 APO 方法在本项目报告的增益，应先回答「是否打得过这个零智能变换」；长上下文索引类任务优先试 ×3。
- anti-pattern / limit：对推理模式叠加它基本无效；超长上下文（如大段 RAG 拼接）盲目翻倍会推高 prefill 成本甚至不可行；只重复局部（如只重复问题）按 Shaier 2024 无增益；按 token 计费时输入成本 ×2。
- 适用场景：非推理、低延迟生产路径（分类、抽取、短 QA、路由判断）；上下文内信息顺序不可控的场景（检索结果拼接、表单转写）。
- 误用风险：把 47/70 解读为「对任意新模型/任务必然有效」；在推理模型上当作免费增益叠加；在按输入计费的大规模场景忽略成本翻倍。

## 最小验证或演示计划

- 要验证的 insight / method：①repetition 在本项目自有任务和 2026 当代模型上是否复现正向、不破坏输出格式；②它作为 APO baseline 时，被测优化方法的净增益还剩多少。
- 最小验证任务：取一个 50–100 样本的小评测集（候选：advisor 知识库问答改造的选择题，或一个分类小任务），三臂对比 baseline / repetition×2 / padding。
- 需要实现的模块：复用 `scripts/llm_clients.py`；新增一个 ~100 行的三臂 A/B 脚本与结果表。
- 观察指标：accuracy、输出长度、输出格式破坏率、失败类型分布；McNemar 检验。
- 预计风险：样本量小导致不显著；2026 代模型可能已内化复述行为使效应衰减（这本身就是有价值的结论）；非推理模式的界定在新 API 上可能与论文不一致。
