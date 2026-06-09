# Paper Note: Modular Prompt Optimization

论文：Modular Prompt Optimization: Optimizing Structured Prompts with Section-Local Textual Gradients

链接：https://arxiv.org/abs/2601.04055

source_id：paper-modular-prompt-optimization-2026

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：actionable-experiment

阅读日期：2026-06-08

reviewed_by：Codex

local_pdf_path：`local_sources/raw/arxiv_papers/2601.04055/paper.pdf`

local_pdf_sha256：`A00A2DAECEE4C33D4F400591252E0BFBD1087035FC6793ACF596694516E84E57`

local_text_path：`local_sources/raw/arxiv_papers/2601.04055/paper.txt`

local_text_sha256：`02523F4DEC18CCAEC0F308BD06856D7A0BCBBB77E0D368374D224DBFCEB47A40`

evidence_level：method-and-results-read

## 一句话结论

MPO 把 prompt 结构本身当成优化约束：固定 role/context/task/constraints/output_format 等 schema，只对每个 section 生成局部 textual feedback 并去重合并；这为本项目提供了最直接的“可回滚 prompt 优化”实验方案。

## 问题设定

- 任务：提升小型开源 instruction-tuned LMs 在 reasoning benchmarks 上的表现。
- 优化对象：结构化 prompt 的 semantic sections，而不是整段 prompt。
- 目标指标：ARC-Challenge 和 MMLU accuracy。
- 约束：保持 prompt schema 固定，不改变模型参数，不改变 prompt topology。

## 方法摘要

- 候选如何生成：把初始 prompt 分解成 fixed semantic sections：System Role、Relevant Context、Task Details、Constraints、Output Format；critic model 对每个 section 生成 section-local textual gradient。
- 反馈如何获得：critic 看到当前 section 和周围 prompt context，给出局部自然语言改进建议。
- 如何选择候选：论文文本主要描述 section update、aggregation、de-duplication 和重组；未读到复杂 beam/Pareto 选择机制。
- 是否使用记忆/archive：否。
- 是否优化 optimizer 自身：否。

## 实验设置

- 数据集：
  - ARC-Challenge：1119 training examples，1172 test examples。
  - MMLU：3000 training subset，1400 held-out test examples。
- 模型：LLaMA-3 8B-Instruct，Mistral-7B-Instruct。
- baselines：
  - Untuned structured prompt。
  - TextGrad。
- train/dev/test 切分：论文报告 training subset 和 test / held-out test，但本文未核到 dev selection 细节。
- 成本或调用次数：未读到明确 token/call/runtime 成本。

## 主要结果

论文直接报告：

- ARC-Challenge：
  - LLaMA-3 8B-Instruct：Untuned 75.0，TextGrad 75.67，MPO 79.10。
  - Mistral-7B-Instruct：Untuned 70.73，TextGrad 70.30，MPO 73.04。
- MMLU：
  - LLaMA-3 8B-Instruct：Untuned 57.21，TextGrad 56.40，MPO 61.50。
  - Mistral-7B-Instruct：Untuned 53.79，TextGrad 53.70，MPO 55.50。
- 论文强调 TextGrad 在 MMLU 上相对 untuned prompt 下降，而 MPO 在两个模型和两个任务上都提升。

## 失败案例和局限

论文直接报告 / 未报告：

- 论文 future work 提到需要研究 critic model 选择对优化稳定性和迁移的影响。
- 论文 future work 提到需要研究 structured optimization 是否会放大或缓解 unsafe / jailbreak behaviors。
- 当前实验只覆盖 ARC-Challenge、MMLU 和两个小型开源模型，未覆盖 agent、tool-use、生成任务或生产格式约束。
- 未读到明确成本报告、失败样例、prompt 长度变化曲线、train/dev/test selection 细节或 ablation。

## 洞见卡片

```yaml
insight: 结构化 prompt 比整段 prompt 更适合自动优化，因为它把优化对象和不可变约束分开。
evidence_type: direct-method + direct-result
paper_evidence:
  section: "1 Introduction; 3 Approach; 4 Results"
  table_or_figure: "Figure 1, Table 1, Table 2"
  quote_or_paraphrase: "MPO 固定 System Role、Relevant Context、Task Details、Constraints、Output Format，并对每个 section 做局部 textual gradients；结果在 ARC/MMLU 上超过 TextGrad 和 untuned structured prompt。"
mechanism: section-local feedback 降低 unrelated instructions 之间的干扰，固定 schema 防止自由重写破坏 prompt topology，de-duplication 减少 prompt bloat。
actionable_rule: 本项目的第一个 prompt 优化实验应采用 frozen/mutable section schema，每轮只允许修改一个 section。
counterexample_or_limit: 论文未报告 agent/tool-use、格式约束、安全边界或成本；schema 设计仍需要人工参与。
minimal_experiment: whole-prompt rewrite vs section-local rewrite，观察 task score、format violation、frozen section violation 和 prompt length growth。
confidence: medium-high-for-structured-reasoning-prompts; medium-for-production-agent-prompts
```

```yaml
insight: TextGrad 类全局更新可能不如局部更新稳定，尤其当 prompt 已有明确结构时。
evidence_type: direct-result
paper_evidence:
  section: "4 Results"
  table_or_figure: "Table 1, Table 2"
  quote_or_paraphrase: "TextGrad 在 MMLU 两个模型上低于 untuned structured prompt，而 MPO 在全部设置上提升。"
mechanism: 全局 textual feedback 可能改动无关 section 或引入干扰；局部反馈把错误归因限制在 section 内。
actionable_rule: 如果 prompt 已经包含 role/constraints/output_format，不应默认让 optimizer 重写整段 prompt。
counterexample_or_limit: 论文未给出足够 ablation 证明具体收益来自局部化、去重还是 schema 本身。
minimal_experiment: structured baseline vs TextGrad-style whole prompt vs MPO-style section-local。
confidence: medium
```

## 对本项目的启发

- 这是最适合马上转成 `docs/experiment_plan.md` 的实验方向。
- 本项目的 prompt variant log 应记录：
  - `schema_version`
  - `mutable_sections`
  - `frozen_sections`
  - `changed_section`
  - `section_diff`
  - `deduplication_action`
  - `frozen_section_violation`
- 若后续自动优化系统 prompt 或 tool policy，必须先实现 frozen section 检查。

## 可复现计划

- 最小复现任务：结构化分类或抽取任务，prompt 至少含 role/task/constraints/output_format。
- 需要实现的模块：
  - prompt schema parser。
  - section-local critic。
  - section updater。
  - de-duplication / consolidation。
  - frozen-section guard。
- 预计风险：
  - schema 人工设计偏差。
  - critic 质量影响大。
  - 只在小模型 reasoning 任务上有效，未必迁移到 agent/tool-use。
