# 实验计划

更新时间：2026-06-08

状态：候选验证设计，暂不进入完整 benchmark 实现。先完成 M0 资料搜集、洞见提炼、核心结论和 helpful methods 候选，再选择 1-2 个最小实验验证或演示关键洞见/方法。

## M0：资料搜集与综述冻结

在实现任何完整 benchmark harness 或自动优化脚本前，先按 [资料搜集计划](source_collection_plan.md) 完成论文、行业经验、工程框架和失败案例收集，并形成 insight / conclusion / helpful method 候选。

M0 完成标准：

- 收集 50 个以上候选来源，并记录链接、发布日期、类型、相关性和状态。
- 完成 12-15 篇核心论文或框架的结构化笔记。
- 整理 10-15 个行业实践、工具文档或工程经验来源。
- 形成前沿状态图和方法 taxonomy，覆盖候选生成、候选选择、反馈信号、优化对象、记忆机制和治理机制。
- 输出一份 insight / conclusion / helpful method 候选清单。
- 输出 2-3 个可复用方法或建议。
- 输出 1-2 个最小验证/演示候选，每个候选写清要验证的洞见或方法、目标、假设、输入样本、模型、评估方式、成功标准和主要风险。

未完成 M0 前，不冻结长期任务、数据集或评分器；但可以为报告中的关键洞见或方法设计一次小规模初步验证。

## 初步验证目标

构建一个小型、可复现的初步验证，观察关键 insight、conclusion 或 helpful method 是否有支持迹象，同时记录成本、失败模式和过拟合风险。

初步实验不承担“证明某方法长期有效”的任务，只用于支持、修正或演示最终报告中的洞见与可复用方法。

当前验证候选以 [Insight / Conclusion / Helpful Method 候选清单](insight_method_catalog_20260609.md) 为结构化主入口；面向读者的同口径说明见 [读者向洞见手册](insight_handbook_20260609.md)，其「首批最小验证」表与本文 P0–P2 优先级一致。实验优先服务以下方法卡片，而不是追求完整 benchmark 覆盖：

- HM-01：Pre-Optimization Gate，验证自动优化前是否存在可利用 headroom。
- HM-02：Trace-First Critique Rewrite，验证失败 trace / 根因假设是否优于直接 rewrite。
- HM-03：Exemplar Optimization Baseline，防止把 exemplar selection 的收益误写成 instruction rewrite 收益。
- HM-04：Prompt Artifact Ledger，保证 prompt、examples、tool schema、context 和 evaluator 可追踪、可回滚。

## 实验选择门槛

只有满足以下条件的候选才进入实验计划：

- 明确对应一个 insight、conclusion 或 helpful method。
- 能通过最小任务验证该洞见的一个关键边界。
- 结果无论成功或失败，都能回填到经验总结、反模式或方法 playbook。
- 不需要为了演示而实现完整 benchmark harness。

## 实验纪律

实验设计遵循 [项目构建原则](project_principles.md)。每轮实验默认先写清目标、假设、变量、指标和成功标准，再运行优化。

- 一次实验尽量只改变一个主要变量，例如 prompt 文案、few-shot 示例、模型参数或评分器。
- 如果必须同时改变多个变量，要把该轮标记为多因素实验，结论中不能声称单变量因果。
- 每个结论必须能追溯到运行记录、指标、样例输出或失败案例。
- 每个实验必须记录它验证的 insight/method，以及验证结果如何改变该洞见或方法的可信度。
- 自动改 prompt 的实验必须保留原 prompt、候选 prompt、优化原因、评测结果和回滚点。

## 第一阶段任务选择候选

优先选择评分明确、运行便宜、错误可解释的任务：

| 任务 | 输入 | 输出 | 评分 |
| --- | --- | --- | --- |
| 文本分类 | 用户问题 / 工单 / 评论 | 固定标签 | accuracy / macro-F1 |
| 信息抽取 | 邮件 / 简历 / 商品描述 | JSON schema | exact match / field F1 / JSON validity |
| RAG 问答 | question + retrieved passages | answer + citation | answer correctness / citation precision |
| 工具调用 | 用户请求 + tool schema | function call args | argument exact match / execution success |

当前只保留候选，不做长期冻结。M0 完成后，再根据文献和行业经验选择最能验证关键洞见或 helpful method 的任务，避免过早排除 RAG、agent 或 tool-use 中更有研究价值的最小任务。

## Baselines

1. Manual prompt：人工写的清晰 baseline。
2. Few-shot prompt：manual + 3-5 个示例。
3. APE-style：LLM 生成 N 个候选 instruction，按 dev score 选择。
4. ProTeGi-style：从失败样本生成 textual critique，再编辑 prompt。
5. DSPy/MIPROv2：如果实验栈使用 Python，可作为强 baseline。
6. GEPA-style：记录轨迹并让 optimizer 反思后生成候选，使用 Pareto/validation 选择。
7. Memory APO：维护成功策略和失败模式库，测试跨任务复用。

## 数据切分

- `train`: optimizer 可见，用于生成 critique、候选和少样本示例。
- `dev`: optimizer 可见分数，用于选择候选。
- `validation`: 优化过程只看 aggregate score，用于防止过拟合。
- `test`: 完全保留，最后报告。
- `adversarial`: 格式异常、语言混合、边界条件、诱导越权。

小样本起步配置：

- train 50-100 条
- dev 50 条
- validation 50 条
- test 100 条
- adversarial 30 条

## 优化循环

```text
baseline_prompt
  -> run eval on train/dev
  -> collect failures and traces
  -> optimizer summarizes failure modes
  -> generate K prompt candidates
  -> run candidates on dev
  -> filter by hard constraints
  -> validate top candidates
  -> select winner or keep baseline
  -> write run artifact and prompt diff
```

## 候选过滤规则

- 输出 schema 不能变，除非该轮实验明确允许。
- 安全/拒答/权限规则不能删除或弱化。
- 不允许把测试集答案、具体样本标签、评分器实现泄露进 prompt。
- 候选 prompt 超过长度预算则降级或拒绝。
- 若 validation 下降超过阈值，即使 dev 上升也不采用。

## 指标

质量指标：

- 主任务分数：accuracy、macro-F1、field F1、exact match。
- 格式可靠性：JSON validity、schema compliance。
- 鲁棒性：adversarial set score、跨模型 score。
- 稳定性：多随机种子或多次采样方差。

效率指标：

- optimizer 调用次数。
- target model 调用次数。
- token 成本。
- wall-clock time。
- 单位分数提升成本。

治理指标：

- prompt diff 大小。
- 自动修改原因是否可解释。
- 人工审核通过率。
- 回滚次数。
- 线上失败案例进入 eval 集的比例。

## 运行记录字段

每次优化运行至少记录：

```yaml
run_id:
date:
insight_or_method_validated:
task:
dataset_version:
target_model:
optimizer_model:
prompt_version_before:
prompt_version_after:
parameters:
optimizer_method:
candidate_count:
train_score:
dev_score:
validation_score:
test_score:
adversarial_score:
token_cost:
latency:
accepted:
rejection_reason:
top_failure_modes:
prompt_diff_summary:
source_files:
```

## 里程碑

### M0：资料搜集和综述冻结

- 完成资料搜集计划中的最低覆盖矩阵。
- 更新文献地图、行业实践整理和核心论文笔记。
- 输出前沿状态图、方法 taxonomy、证据强度说明和资料缺口清单。
- 输出 insight / conclusion / helpful method 候选清单。
- 输出 2-3 个可复用方法或建议。

### M1：最小验证冻结

- 从 M0 的实验候选中选择 1-2 个最小验证任务。
- 明确要验证的 insight/method、验证目标、评分器和成功/失败解释口径。
- 准备最小数据集和 baseline prompt，不追求长期 benchmark 完整性。

### M2：初步实验

- 至少实现 manual 与一个改进/优化 baseline。
- 每次运行生成可追踪 artifact。
- 报告指标、成本、失败案例和结论限制。

### M3：最终说明和报告

- 整合前沿状态、行业经验、核心洞见、helpful methods 和初步验证结果。
- 每条关键结论标注证据等级。
- 输出最终报告和后续验证路线。

### M4：反思式进化

- 加入轨迹反思和失败模式总结。
- 引入 candidate archive 和 validation split。
- 和 MIPROv2/GEPA-style baseline 对比。

### M5：记忆与自进化

- 维护成功策略库和失败模式库。
- 测试跨任务迁移。
- 评估长期漂移和回滚机制。

### M6：系统级扩展

- 扩展到 RAG 或 tool-use。
- 优化对象从单 prompt 扩展到 prompt + examples + context + tool policy。
- 输出一份自进化 prompt 系统设计报告。

## 首个可执行实验建议

先做“结构化信息抽取”：

- 输入：短邮件或用户请求。
- 输出：严格 JSON，如 `{intent, entities, urgency}`。
- Baseline：手写 system prompt + JSON schema。
- 优化目标：field F1、JSON validity、成本。
- 失败反思：字段漏抽、错误标签、格式破坏、过度推断。

第一轮只验证最小闭环：

1. 跑 zero-shot / manual baseline / 10-20 个候选，形成 pre-optimization gate。
2. 固定 instruction，比较 no-example、random-example、optimized-example。
3. 在同一失败样本上比较 direct rewrite 和 trace-first critique rewrite。
4. 每个候选写入 prompt artifact ledger，记录 diff、score、cost、失败样本、接受/拒绝理由和 rollback point。

原因：评分清晰、成本低、错误可解释，适合作为 prompt evolution loop 的第一块地基。
