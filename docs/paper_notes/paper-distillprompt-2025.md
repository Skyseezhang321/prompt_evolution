# Paper Note: DistillPrompt / Automatic Prompt Optimization with Prompt Distillation

论文：Automatic Prompt Optimization with Prompt Distillation

链接：https://arxiv.org/abs/2508.18992

source_id：paper-distillprompt-2025

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：extension

阅读日期：2026-06-08

reviewed_by：Codex

local_pdf_path：`local_sources/raw/arxiv_papers/2508.18992/paper.pdf`

local_pdf_sha256：`11E1AD995E7C5FD8DC5B8CB122C70AF8A97250CEA401B1AF45450FB702C45374`

local_text_path：`local_sources/raw/arxiv_papers/2508.18992/paper.txt`

local_text_sha256：`754EFBAC3C201522D93D5EB8F23A4A396C2E055FCA0E4F537DB37C16AF56B208`

evidence_level：method-results-read

## 一句话结论

DistillPrompt 提供了一个简单但实用的经验：先让多个候选从样例中抽取任务原则，再压缩、聚合成 distilled prompt，可以把 few-shot 的信息转成更泛化的 instruction，减少直接塞样例导致的过拟合。

## 问题设定

- 任务：分类、问答、文本生成。
- 优化对象：自然语言 prompt。
- 目标指标：分类用 macro F1；生成用 METEOR。
- 约束：non-gradient autoprompting；当前实现候选数 N=4、样例数 K=5。

## 方法摘要

- 候选如何生成：每轮从当前最佳 prompt 生成多个 variation。
- 反馈如何获得：候选在训练任务上评估，最高分进入下一轮。
- 如何选择候选：每 epoch 选择最高目标指标候选。
- 是否使用记忆/archive：不使用长期 memory。
- 是否优化 optimizer 自身：否。

## 实验设置

- 数据集：SST-2、MedQA、GSM8K、MNLI、MR、TREC、SAMSum、BBH。
- 模型：t-lite-instruct-0.1。
- baselines：baseline prompt、3-shot prompt、Grips、ProTeGi。
- train/dev/test 切分：训练样例用于 prompt distillation，表格报告任务指标。
- 成本或调用次数：每 epoch 5 个阶段：variation generation、example embedding、compression、aggregation、final variation/evaluation。

## 主要结果

- 分类任务中，DistillPrompt 在 SST-2 0.9484、MNLI 0.7606、MR 0.9392、BBH 0.4045 等指标上超过或接近最强 baseline。
- 生成任务中，DistillPrompt 在 GSM8K、SAMSum、BBH METEOR 上分别为 0.0347、0.4579、0.2961，超过 Grips 的 0.02643、0.45516、0.1491。
- 作者报告相对 Grips 全数据集平均提升 20.12%；分类平均 F1 相对 baseline 提升 36.18%，相对 Grips 提升 15.09%；生成平均 METEOR 相对 Grips 提升 25.05%。

## 失败案例和局限

- 论文较短，实验模型单一，缺少更充分的消融来证明 compression/aggregation 各自贡献。
- 用训练集最高分选择候选，仍有 dev/train overfitting 风险。
- 对 prompt distillation 的定义较宽，需要在复现时严格区分“直接示例插入”和“原则抽取+压缩”。

## 洞见卡片

```yaml
insight: few-shot 样例不一定要直接放进 prompt，也可以先蒸馏成任务原则再压缩聚合。
evidence_type: method + benchmark-result
paper_evidence:
  section: "2 DistillPrompt; 3.2 Results"
  table_or_figure: "Table 1, Table 2"
  quote_or_paraphrase: "作者发现直接插入样例不如让 LLM 从样例抽取 task-solving principles 后压缩。"
mechanism: 原则抽取保留可泛化信息，压缩减少样例标签细节导致的过拟合。
actionable_rule: 有 labeled examples 时，比较 direct few-shot、principle distillation、distilled+examples 三种输入组织。
counterexample_or_limit: 如果任务依赖具体格式示例，过度压缩可能丢掉关键 schema。
minimal_experiment: few-shot insertion vs example-principle distillation vs compressed aggregation。
confidence: medium-low-due-limited-ablation
```

## 对本项目的启发

- 在我们的 prompt 变体中可加入 `example_distillation` 变量，避免把所有样例策略都称为 few-shot。
- 适合做低成本 baseline：实现简单，能测试“压缩后的经验总结是否优于直接示例”。
- 需要强制记录压缩前后的 prompt length 和样例覆盖，以防信息丢失。

## 可复现计划

- 最小复现任务：分类任务 + 小生成任务，各 50 条 train、100 条 test。
- 需要实现的模块：sample principle extractor、instruction compressor、candidate aggregator、length/coverage audit。
- 预计风险：压缩引入幻觉原则；train 过拟合；METEOR 与真实质量不一致。
