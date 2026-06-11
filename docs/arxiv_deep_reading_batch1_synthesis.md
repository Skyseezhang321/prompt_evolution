# arXiv 重点论文深读 Batch 1 综合判断

日期：2026-06-08

2026-06-09 补充：新增“可转成普通用户方法的候选”层，用于把论文级判断转写成具体洞见卡片；原有学术结论和证据边界保留。

范围：已下载 15 篇重点论文中的 5 篇深读笔记。

- ProTeGi：`docs/paper_notes/paper-protegi-2023.md`
- Modular Prompt Optimization：`docs/paper_notes/paper-modular-prompt-optimization-2026.md`
- GEPA：`docs/paper_notes/paper-gepa-2026.md`
- SePO：`docs/paper_notes/paper-sepo-2026.md`
- SPEAR：`docs/paper_notes/paper-spear-2026.md`

证据边界：以下结论来自论文全文的方法、实验、消融和局限阅读，不是只基于 abstract。但还不是本项目复现实验结论；进入最终报告前仍需要最小实验验证。

## 可转成普通用户方法的候选

本节只做“洞见翻译”，不替代后面的论文级判断。最终报告首页可以先展示这些卡片，再展开 ProTeGi、MPO、GEPA、SePO、SPEAR 的学术证据。

| 具体洞见 | 一句话给普通用户 | 最小可试方法 |
| --- | --- | --- |
| 错误信号质量决定优化上限。 | 只知道“答错了”不够，要知道“为什么错”。 | 让评估器输出失败类型和修改建议，再比较 score-only rewrite。 |
| 不要覆盖原 prompt。 | 自动优化要像保存草稿一样保留每个候选。 | 记录 seed、candidate、score、失败样例和 rollback。 |
| 优化器本身也要管理。 | 不是只有任务 prompt 会影响结果，改写 prompt 的 prompt 也会影响结果。 | 分开记录 task prompt、optimizer prompt、工具和搜索策略。 |
| 结构化 prompt 更容易安全修改。 | 把一大段 prompt 拆成角色、任务、约束、输出格式和示例。 | 每次只改一个 section，约束和格式不让自动改。 |
| 先做 trace-rich 小闭环。 | 不要一上来做大而全自进化系统。 | 用 100-300 条结构化任务样本，对比 score、critique、trace 三类反馈。 |

## 结论 1：prompt 优化的上限首先取决于错误信号质量

从弱到强可以分成四层：

1. 只有 scalar score：只能知道输赢，难以知道为什么。
2. 失败样本 + 自然语言 critique：ProTeGi 证明这已经能稳定超过 one-shot / MC / RL phrase-level baselines。
3. execution/evaluation trace：GEPA 把工具输出、编译错误、rubric 失败原因等评价过程信息纳入反思，样本效率显著高于 GRPO。
4. 可计算的结构化错误分析：SPEAR 显示，在 judge/分类/抽取场景，confusion matrix、groupby、per-class metrics 这类代码生成统计能发现长上下文 critique 看不到的规律。

可执行规则：后续任何 prompt evolution 实验，都不应只记录最终分数。最小日志字段应包括 `sample_id`、`prediction`、`gold`、`error_type`、`critique`、`trace`、`analysis_output`、`candidate_prompt_id`。

最小验证：同一任务比较 `score-only rewrite`、`critique rewrite`、`trace-aware rewrite`、`python-analysis rewrite` 四组。

## 结论 2：候选选择和回滚机制不是工程细节，而是方法核心

已读论文给出的证据很一致：

- ProTeGi：beam search 和 bandit selection 明显优于直接采用单次改写。
- GEPA：Pareto candidate selection 明显优于只沿当前 best candidate 继续优化。
- SePO：archive-based open-ended evolution 的消融损失很大。
- SPEAR：auto-rollback 不一定提高平均最优点，但显著提高运行下限，避免最终低于 seed。

可执行规则：不要让 optimizer 直接覆盖原 prompt。所有实验必须保留 seed、候选、选择理由、best-seen、rollback 点和被淘汰原因。

最小验证：`one-shot rewrite` vs `beam/bandit` vs `Pareto archive` vs `rollback-only`。

## 结论 3：optimizer 本身也是需要管理和优化的 artifact

SePO 把这个问题说得最明确：常见方法只优化 task agent prompt，却把 prompt agent 自己的系统 prompt 固定。实验中，去掉 self-improvement 会明显降低 SePO-Generalist 的平均表现。

SPEAR 从另一个方向补充：optimizer 的能力不只来自 prompt，还来自工具和编排策略。相同工具如果固定成 rigid loop，会明显输给 free-form agent。

可执行规则：项目里要把 `task_prompt`、`optimizer_prompt`、`optimizer_tools`、`search_policy` 分开版本化。否则无法判断提升来自 prompt 内容、optimizer 提示词、工具能力还是候选选择策略。

最小验证：固定任务和数据，比较 `fixed optimizer prompt`、`self-improved optimizer prompt`、`same tools rigid loop`、`tool-choice agent`。

## 结论 4：模块化 prompt 比整段 prompt 盲改更容易控制

MPO 的结论和 GEPA 的多模块设置相互支持：

- MPO 把 prompt 固定拆成 System Role、Relevant Context、Task Details、Constraints、Output Format，再做 section-local textual gradients。
- GEPA 在 compound AI system 中按模块更新 prompt，避免每次把整个系统 prompt 一起扰动。

可执行规则：项目中的 prompt 变体最好默认结构化，不要只存一整段字符串。至少区分 `role`、`task`、`constraints`、`output_format`、`examples`、`tools`。

最小验证：整段 rewrite vs section-local rewrite；同时追踪 prompt 长度、格式错误率和跨 split 泛化。

## 结论 5：目前最值得先复现的不是“自进化大系统”，而是 trace-rich 小闭环

已读论文里最稳的共同模式是：小数据、强日志、多候选、可回滚。直接复现 SePO/GEPA/SPEAR 的完整系统成本较高，也很难一次判断因果。

建议第一批最小实验：

1. 任务：多类别 judge 或结构化抽取，100-300 条 labeled rows。
2. baseline：人工 seed prompt + 固定格式输出。
3. 变量 A：错误信号层级，score-only / critique / trace / python analysis。
4. 变量 B：候选选择，single rewrite / beam / Pareto archive。
5. 安全阀：best-seen prompt + auto-rollback。
6. 指标：主指标、格式错误率、prompt 长度、dev-test gap、每轮成本、失败类型变化。

判断标准：不是只看最终分数，而是看哪种错误信号和选择策略能稳定减少同一类失败，并且不过度增加 prompt 长度或 dev-test gap。

## 当前未证事项

- 这些论文结果能否迁移到中文任务，还没有证据。
- Prompt optimizer 自我改进是否会带来安全退化，目前只看到 SePO 的讨论，缺少强实验。
- Python sandbox 型 optimizer 是否值得用于开放生成任务，SPEAR 的证据主要来自 structured judge tasks。
- Pareto archive 的最佳大小、验证集采样方式、噪声处理还没有统一答案。
- Prompt length 是否应该作为优化目标之一，GEPA/SPEAR 都提示重要，但尚未形成统一方法。
