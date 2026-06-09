# GitHub 渠道洞见综合：2026-06-09

本文件按最新内容整理原则重写 GitHub 渠道输出：优先沉淀有效 insights、可信 conclusions、可复用 helpful methods、反模式和最小验证方式。旧的快筛、catalog、源码审计和证据卡继续作为证据层，不在本文件重复展开仓库介绍。

## 结论总览

| conclusion | 当前判断 | 证据等级 | 边界 |
| --- | --- | --- | --- |
| GitHub 渠道最适合提供工程结构和治理方法。 | 公开仓库能展示 prompt/context/eval/versioning 如何组织成代码和流程。 | B/D | 不能直接证明某种 prompt optimizer 稳定涨分。 |
| 直接 prompt optimizer 强证据较少。 | core4 中只有 `linshenkx/prompt-optimizer` 直接属于 prompt optimizer；其价值主要是 compare/evaluation/rewrite 工程结构。 | B | 仍需本项目最小实验验证效果。 |
| 自进化最重要的护栏是冻结 evaluator/data。 | `karpathy/autoresearch` 给出“可变对象”和“固定评估器”隔离的清晰结构，可迁移到 prompt-only optimizer。 | B/D | 它优化的是训练代码，不是 prompt；迁移后仍需验证。 |
| Prompt 优化边界应包含 context packaging。 | `12-factor-agents` 明确把 prompt、RAG、history、tool calls、memory 和输出结构都视为 context 工程对象。 | B/D | 工程原则不是 benchmark 证据。 |
| Memory 不能当作无界历史缓存。 | ECC 的 memory hooks 和 evaluator/RAG prototype 更适合作为 bounded memory、trace、verifier、playbook 的结构参考。 | D | ECC 的方法效果仍需运行核验。 |

证据等级说明：这里的 B 表示来自固定 commit 的开源项目文档/源码审计，D 表示本项目基于源码观察形成的待验证推断。它们不是本项目实验结论。

## 一眼看懂的洞见

| insight | 普通用户一句话 | 可立即尝试的动作 | 主要证据 |
| --- | --- | --- | --- |
| 先比较，再改写。 | 不要直接让模型“优化 prompt”，先让它解释 baseline 为什么失败。 | 让模型先输出失败原因和证据摘要，再让第二步 prompt 根据这些证据改写。 | `prompt-optimizer` 的 structured compare / rewrite-from-evaluation 结构。 |
| 不要让 optimizer 改试卷。 | 自动优化只能改 prompt，不能改 eval cases、grader 或成功标准。 | 把 `candidate_prompt.md` 设为唯一可变文件，其它 eval 文件只读。 | `autoresearch` 的 `program.md` / `prepare.py` 隔离结构。 |
| 验证集要有“会骗过 optimizer 的反例”。 | 只看普通样本会让 prompt 学会局部补丁。 | 加入 schema drift、过拟合触发词、单次好运、边界保守类样本。 | `prompt-optimizer` 的 structured compare calibration。 |
| Prompt 不是唯一优化对象。 | 很多失败来自上下文组织，而不是 system prompt 写得不够漂亮。 | 同时记录 prompt、retrieval context、history compression、tool result format 和 output schema。 | `12-factor-agents` 的 context window 原则。 |
| 每个候选 prompt 都要有账本。 | 没有 diff、分数、成本和拒绝原因，就没有可复用经验。 | 记录 prompt diff、来源、指标、成本、失败样例、保留/丢弃和回滚点。 | `autoresearch` 的 results ledger；ECC 的 trace/verifier artifact。 |
| Memory 要能禁用和过期。 | 记忆不是越多越好，旧经验会污染新任务。 | 每条 memory 记录来源、适用范围、验证状态、过期策略和 opt-out。 | ECC memory-persistence hooks；arXiv memory 类论文可后续互证。 |

## Helpful Methods

### Method 1：Frozen Evaluator Prompt Loop

```yaml
name: Frozen Evaluator Prompt Loop
insight_supported: evaluator / data / harness 必须与可优化 prompt 隔离
problem: 自动优化容易通过修改评分标准、样本或输出解析制造伪提升
recommended_when: 需要验证一个 prompt optimizer 是否真的改善任务表现
not_recommended_when: 任务目标还没定义，或评分器本身还在探索
required_inputs:
  - baseline_prompt.md
  - candidate_prompt.md
  - eval_cases.jsonl
  - frozen_grader.py 或 frozen_judge_prompt.md
  - run_ledger.jsonl
implementation_steps:
  - 固定 eval cases、grader、模型和参数
  - 只允许 optimizer 修改 candidate_prompt.md
  - 每轮记录 prompt diff、score、cost、失败样例和保留/丢弃原因
  - dev set 决策，held-out set 只做最终确认
evaluation_metrics:
  - task_score
  - format_error_rate
  - regression_case_count
  - prompt_length_delta
  - cost_per_candidate
risks:
  - dev set 过拟合
  - judge 偏差
  - prompt 变长但不可维护
rollback_plan: 保留 baseline prompt 和每个 accepted candidate 的 commit/hash
evidence:
  - repo-karpathy-autoresearch@228791fb499a
  - docs/github_repo_insight_cards_20260608.md#GHI-04
next_experiment: 在一个结构化抽取或工具调用小任务上实现 prompt-only loop
```

### Method 2：Compare-First Rewrite

```yaml
name: Compare-First Rewrite
insight_supported: 失败证据比直接改写更可审计
problem: one-shot rewrite 常常只是扩写、迎合 judge 或覆盖局部样本
recommended_when: 已有 baseline 输出和失败样例，需要系统改 prompt
not_recommended_when: 没有可比较输出，或任务没有明确评估标准
required_inputs:
  - baseline prompt
  - baseline outputs
  - target/candidate outputs
  - rubric 或 schema contract
  - rewrite prompt
implementation_steps:
  - 先做 pairwise compare，输出失败类型和证据
  - synthesis 阶段把多条判断压缩为可执行修改建议
  - rewrite 阶段只消费证据摘要，不直接吞全部原始上下文
  - 人工审查 prompt diff，再运行 eval
evaluation_metrics:
  - held_out_score_delta
  - schema_drift_count
  - rewrite_reason_coverage
  - manual_review_time
risks:
  - compare judge 过度自信
  - synthesis 丢失少数失败类型
  - rewrite 过度迎合当前样本
rollback_plan: 保存 compare evidence、rewrite reason 和 prompt diff
evidence:
  - repo-linshenkx-prompt-optimizer@d7cde6c2fc5c
  - docs/github_repo_insight_cards_20260608.md#GHI-01
next_experiment: 对比 direct rewrite 与 compare-first rewrite
```

### Method 3：Bounded Memory And Trace Playbook

```yaml
name: Bounded Memory And Trace Playbook
insight_supported: memory 必须有边界，经验沉淀必须可验证
problem: 无界历史缓存会带来上下文污染、旧错误继承和成本膨胀
recommended_when: 需要让 prompt optimizer 或 agent 从历史失败中复用经验
not_recommended_when: 任务很短、无跨轮复用价值，或隐私边界不清楚
required_inputs:
  - scenario.json
  - trace.jsonl
  - verifier_result.json
  - candidate_playbook.md
  - memory_policy.md
implementation_steps:
  - 每轮保存 scenario、trace、candidate 和 verifier decision
  - 只把通过验证的经验写入 memory
  - 每条 memory 带来源、适用范围、过期时间和 opt-out
  - 定期用反例样本清理或降权 memory
evaluation_metrics:
  - reused_memory_hit_rate
  - stale_memory_error_count
  - token_overhead
  - rollback_count
risks:
  - 把一次性 workaround 写成通用经验
  - 泄露敏感上下文
  - memory 选择器引入隐藏变量
rollback_plan: 支持关闭 memory，并可按 source_id 删除经验条目
evidence:
  - repo-affaan-m-ecc@90dfd9505dc8
  - docs/github_repo_insight_cards_20260608.md#GHI-09
  - docs/github_repo_insight_cards_20260608.md#GHI-10
next_experiment: 比较 no-memory、bounded-summary-memory、raw-history-memory
```

## 反模式

| anti-pattern | 为什么危险 | 替代做法 |
| --- | --- | --- |
| 把 star 数或传播热度当作证据强度。 | 热度不能证明方法有效，也不能说明 eval 严谨。 | 固定 commit，读源码/测试/示例，再标证据等级。 |
| 直接让 LLM 改 prompt。 | 容易扩写、迎合当前样本，无法解释改动原因。 | compare-first rewrite，保留失败证据和 diff。 |
| 让 optimizer 同时改 prompt、数据和 grader。 | 无法判断收益来源，还可能 reward hacking。 | 冻结 evaluator/data，只改目标对象。 |
| 只看平均分提升。 | 可能掩盖 schema drift、少数类回退、安全退化和成本膨胀。 | 记录分组指标、格式错误、失败样例、成本和 prompt hygiene。 |
| 把 memory 当长历史缓存。 | 旧错误、过时策略和无关上下文会污染新任务。 | bounded memory，带来源、范围、过期和禁用开关。 |
| 把“有 tests”写成“方法有效”。 | 测试可能只覆盖安装、格式或配置，不覆盖 optimizer 行为。 | 区分可审计入口、行为测试和效果验证。 |

## 最小验证候选

优先冻结 2 个验证/演示，不建议先做完整 benchmark harness。

| validation | 验证的 insight / method | 最小设置 | 成功标准 |
| --- | --- | --- | --- |
| Frozen Evaluator Prompt Loop | Method 1；GHI-04/GHI-05 | 20-50 条结构化抽取或工具调用样本；固定 grader；只改 prompt | dev 提升不伴随 held-out 回退；格式错误率不恶化；ledger 完整 |
| Direct Rewrite vs Compare-First Rewrite | Method 2；GHI-01/GHI-03 | 同一 baseline prompt、同一失败样本，分别直接 rewrite 和 compare-first rewrite | compare-first 的失败覆盖率、schema 稳定性或人工审查效率更好 |
| Markdown vs JSON Payload Judge | GHI-02 | 同一 judge 任务，分别用 Markdown 拼接和 JSON payload | JSON payload 的解析失败率和 wrapper/schema drift 更低 |
| Bounded Memory Demo | Method 3；GHI-09/GHI-10 | no-memory / bounded summary / raw history 三组 | bounded memory 能降低重复错误，且不明显增加旧经验污染 |

## 证据索引

- [GitHub 仓库候选快筛](github_repo_triage_20260608.md)：解释 85 个 raw candidates 的噪声、筛选和时间分布。
- [GitHub 仓库分析概述](github_repo_analysis_overview_20260608.md)：保留首轮横向结构和仓库类型分布。
- [GitHub 仓库源码审计流程](github_repo_source_audit_workflow_20260608.md)：说明 clone/audit/人工审计流程和证据等级。
- [GitHub 仓库候选 insight 证据卡](github_repo_insight_cards_20260608.md)：保留 GHI-01 到 GHI-12 的详细证据卡。
- [GitHub 仓库证据矩阵](github_repo_evidence_matrix_20260608.md)：保留首轮横向证据矩阵，不再作为最终结论入口。
- `docs/github_repo_audit_notes/`：core4 固定 commit 后的源码审计草稿。

## 最终报告写法建议

GitHub 渠道在最终报告中不宜写成“某仓库证明了 prompt 自进化有效”。更稳妥的写法是：

- 结论：GitHub 源码显示生产形态更关注 eval、版本、trace、context 和 governance，而非单句 prompt 技巧。
- Insight：失败证据、固定 evaluator、候选账本和 context packaging 是 prompt 自进化的工程基础。
- Helpful method：推荐先实现 Frozen Evaluator Prompt Loop 和 Compare-First Rewrite。
- 边界：这些方法来自源码结构观察，需要通过本项目最小验证升级证据等级。
