# 实验计划

更新时间：2026-06-08

## MVP 目标

构建一个小型、可复现的 prompt optimization loop，验证自动优化是否能在受控任务上稳定超过手写 prompt，同时记录成本、失败模式和过拟合风险。

## 实验纪律

实验设计遵循 [项目构建原则](project_principles.md)。每轮实验默认先写清目标、假设、变量、指标和成功标准，再运行优化。

- 一次实验尽量只改变一个主要变量，例如 prompt 文案、few-shot 示例、模型参数或评分器。
- 如果必须同时改变多个变量，要把该轮标记为多因素实验，结论中不能声称单变量因果。
- 每个结论必须能追溯到运行记录、指标、样例输出或失败案例。
- 自动改 prompt 的实验必须保留原 prompt、候选 prompt、优化原因、评测结果和回滚点。

## 第一阶段任务选择

优先选择评分明确、运行便宜、错误可解释的任务：

| 任务 | 输入 | 输出 | 评分 |
| --- | --- | --- | --- |
| 文本分类 | 用户问题 / 工单 / 评论 | 固定标签 | accuracy / macro-F1 |
| 信息抽取 | 邮件 / 简历 / 商品描述 | JSON schema | exact match / field F1 / JSON validity |
| RAG 问答 | question + retrieved passages | answer + citation | answer correctness / citation precision |
| 工具调用 | 用户请求 + tool schema | function call args | argument exact match / execution success |

第一版建议从“分类 + 信息抽取”开始，避免一开始引入 RAG 和 agent 的复杂噪声。

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

### M1：文献和指标冻结

- 完成 10 篇核心论文笔记。
- 明确第一个任务和评分器。
- 准备最小数据集和 baseline prompt。

### M2：单 prompt 优化 MVP

- 实现 manual、few-shot、APE-style、ProTeGi-style baseline。
- 每次运行生成可追踪 artifact。
- 报告 dev/test 差距和成本。

### M3：反思式进化

- 加入轨迹反思和失败模式总结。
- 引入 candidate archive 和 validation split。
- 和 MIPROv2/GEPA-style baseline 对比。

### M4：记忆与自进化

- 维护成功策略库和失败模式库。
- 测试跨任务迁移。
- 评估长期漂移和回滚机制。

### M5：系统级扩展

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

原因：评分清晰、成本低、错误可解释，适合作为 prompt evolution loop 的第一块地基。
