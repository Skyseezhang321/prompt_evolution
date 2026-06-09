# arXiv 重点论文深读 Batch 2 综合判断

日期：2026-06-08

2026-06-09 补充：新增“可转成普通用户方法的候选”层，用于把论文级判断转写成具体洞见卡片；原有学术结论和证据边界保留。

范围：第二批新增深读 6 篇，累计已深读 11 篇。

第二批新增：

- PromptBreeder：`docs/paper_notes/paper-promptbreeder-2023.md`
- EvoPrompt：`docs/paper_notes/paper-evoprompt-2024.md`
- Scaling Textual Gradients：`docs/paper_notes/paper-scaling-textual-gradients-2025.md`
- Textual Gradients are a Flawed Metaphor：`docs/paper_notes/paper-textual-gradients-flawed-metaphor-2025.md`
- PrefPO：`docs/paper_notes/paper-prefpo-2026.md`
- TextReg：`docs/paper_notes/paper-textreg-2026.md`

结合第一批：

- ProTeGi、Modular Prompt Optimization、GEPA、SePO、SPEAR。

证据边界：以下判断来自本地 PDF 全文的方法、实验、消融、case study 和局限阅读。它们是论文证据级结论，不是本项目复现实验结论。

## 可转成普通用户方法的候选

本节用于把第二批论文的学术判断翻译成更具体的用户可用经验。后文仍保留论文机制、实验变量和边界。

| 具体洞见 | 一句话给普通用户 | 最小可试方法 |
| --- | --- | --- |
| “自然语言梯度”只是比喻。 | 不要以为模型给的 critique 一定像数学梯度那样可靠。 | 把 correct critique、wrong critique、no critique 分组对照。 |
| 第一条改写不要直接采用。 | Prompt 优化像试多个草稿，不是听模型一次建议。 | 每轮生成多个候选，用验证集选择。 |
| 只看准确率会被骗。 | 变长、重复、偏向多数类的 prompt 可能看起来更准。 | 同时记录 balanced accuracy、prompt 长度、重复率、per-class recall。 |
| Prompt 变长可能是过拟合。 | 一直加规则不一定更聪明，可能是在背训练样本。 | 对每条新增规则记录来源样本和可能伤害的反例。 |
| 第一批实验应小而可控。 | 先验证反馈信号和候选选择，不要先复现完整大框架。 | 结构化任务 + train/dev/test/OOD + 多候选 + hygiene selector。 |

## 结论 1：不要把 textual gradient 当作真实梯度，应该当作候选生成信号

ProTeGi、TextGrad 系方法说明自然语言反馈能帮助 prompt 更新，但 `Textual Gradients are a Flawed Metaphor` 给出了重要反例：

- 错误 evaluation labels 通常不显著伤害结果。
- 训练更久没有像梯度下降那样拟合训练集或错误标签。
- gradient-like pipeline 不稳定超过 one-step feedback-driven update。
- 高分 prompt 可能来自 prevalence hacking，例如强行禁止 minority class。

行动结论：后续文档和实验中避免把“textual gradient”写成机制性解释。更稳的术语是 `natural-language feedback`、`critique`、`candidate-generation signal`。

最小实验：correct critique、wrong-label critique、no-label critique、prompt-only improve 四组对照，并报告 per-class recall。

## 结论 2：搜索结构比单次反馈更稳定，传统优化算法仍然有价值

PromptBreeder、EvoPrompt、ProTeGi、GEPA、SePO 的证据都指向同一点：LLM 生成候选方差很高，不能相信第一条改写。

- ProTeGi：beam/bandit 比单次或 uniform selection 更稳。
- EvoPrompt：GA/DE 的 selection、mutation、crossover 可以被 LLM 语义化实现。
- PromptBreeder：mutation prompt、hyper-mutation、lineage、Lamarckian operators 都影响结果。
- GEPA：Pareto candidate selection 明显优于只沿全局 best 搜索。
- SePO：archive-based open-ended evolution 是关键组件。

行动结论：本项目的第一个 optimizer 不应是 one-shot rewrite。至少要支持 candidate pool、parent selection、operator type、rollback/best-seen。

最小实验：one-shot、beam、DE-style diff mutation、Pareto archive 四组。

## 结论 3：优化器本身必须版本化，且要拆成 prompt、工具、搜索策略三个 artifact

第二批进一步强化第一批的判断：

- PromptBreeder：mutation prompt 本身也应进化。
- SePO：prompt agent 的 system prompt 也应作为优化目标。
- SPEAR：optimizer 的工具能力和自主编排会影响结果。
- EvoPrompt：即使 operator prompt 固定，GA/DE search policy 也决定轨迹。

行动结论：每个实验必须记录：

- `task_prompt_version`
- `optimizer_prompt_version`
- `mutation_operator`
- `selection_policy`
- `tool_access`
- `candidate_budget`
- `rollback_policy`

否则无法判断提升来自 prompt 内容、optimizer prompt、工具、搜索算法还是更多采样。

## 结论 4：prompt 质量指标必须超过 task accuracy

PrefPO、TextReg、SPEAR 和 flawed-metaphor 论文共同说明：accuracy 可能被 prompt 变长、样本特化、majority-class shortcut、指标钻空子污染。

必须加入的非功能指标：

- prompt length ratio。
- repetition ratio。
- seed similarity。
- per-class recall / balanced accuracy。
- prompt hacking flag。
- rule specificity / case-patch ratio。
- dev-test 或 ID-OOD gap。

行动结论：一个 prompt 只有在性能提升且 hygiene 不显著恶化时，才算真正改进。

最小实验：performance-only selector vs performance + hygiene selector。

## 结论 5：过拟合不只是 dev-test gap，也包括规则变窄和表示膨胀

TextReg 把这个问题讲得最清楚：优化器会不断追加窄规则和特例说明，训练表现可能提升，但 OOD 任务下降。

结合 PrefPO 和 SPEAR：

- 长 prompt 不一定更好，可能只是重复和补丁堆积。
- 把 evaluator 规则改窄可能提高 benchmark pass rate，但损害真实任务。
- 对结构化 judge，Python 分析可以发现错误模式；但改写后还要检查是否变成 label-distribution shortcut。

行动结论：本项目应尽早加入 OOD 或 stress split。没有 OOD split 的 prompt optimization 很难形成可信结论。

## 结论 6：第一批最小复现实验应该聚焦“结构化任务 + trace + 多候选 + hygiene”

目前不建议直接复现 GEPA/SePO/SPEAR 全系统。更稳的第一实验如下：

1. 任务：多类别分类、judge prompt 或结构化抽取，100-300 条 labeled rows。
2. 数据切分：train/dev/test + 一个 OOD/stress split。
3. 错误信号变量：
   - score-only。
   - natural-language critique。
   - trace/evaluator error。
   - Python dataframe analysis。
4. 搜索变量：
   - one-shot。
   - beam/bandit。
   - DE-style diff mutation。
   - Pareto archive。
5. 保护变量：
   - best-seen rollback。
   - length/repetition penalty。
   - rule specificity check。
6. 指标：
   - accuracy / F1 / kappa。
   - balanced accuracy。
   - OOD performance。
   - prompt length/repetition。
   - prompt hacking flags。
   - token cost。

成功标准：不只是主指标提升，而是 OOD 不下降、minority class 不被牺牲、prompt 不显著膨胀、优化轨迹可解释。

## 截至 Batch 2 仍未深读的 4 篇下载论文

- CriSPO：多维 critique/suggestion，适合补充生成任务。
- MemAPO：self-evolving memory，适合补充跨任务记忆。
- AutoPDL：agent prompt optimization，适合补 agent/workflow。
- MASPO：multi-agent joint prompt optimization，适合补多 agent 协同。

这些论文已在 Batch 3 中补齐深读；参见 `docs/arxiv_deep_reading_batch3_synthesis.md` 和对应论文笔记。
