# Paper Note: SPEAR / Code-Augmented Agentic Prompt Optimization

论文：SPEAR: Code-Augmented Agentic Prompt Optimization

链接：https://arxiv.org/abs/2605.26275

source_id：paper-spear-2026

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：high-signal-extension

阅读日期：2026-06-08

reviewed_by：Codex

local_pdf_path：`local_sources/raw/arxiv_papers/2605.26275/paper.pdf`

local_pdf_sha256：`03396532204482691E8992E087EEF3F0DC134972CF2E79EA33C333448B47B1B8`

local_text_path：`local_sources/raw/arxiv_papers/2605.26275/paper.txt`

local_text_sha256：`8603C48F33B8BBEDB04988746D55DC189C7FA884F88A670CC65B2C1FE70DF084`

evidence_level：method-and-results-read

## 一句话结论

SPEAR 的核心洞见是：很多 prompt 失败不是“模型没有读懂批评”，而是错误模式隐藏在 eval DataFrame 的结构里；让 optimizer 自己写 Python 做 confusion matrix、groupby、per-class metrics，再用 auto-rollback 护住下限，会比把原始数据塞进长上下文更有效。

## 问题设定

- 任务：自动改写 LLM-as-judge、BBH、GSM8K 等任务的 system prompt，提高 labeled dataset 上的主指标。
- 优化对象：单个 system prompt，不改 task model 权重。
- 核心场景：工业 judge prompts，尤其是多类别、类别不平衡、标签规则细节复杂的评估器。
- 关键问题：现有 APE pipeline 固定了错误分析方式，无法按任务动态发现 confused class pair、label-rule contradiction 或 feature-level error cluster。

## 方法摘要

- 候选如何生成：free-form agent 在循环中选择 `evaluate`、`python`、`set_prompt`、`finish` 四个工具；没有固定 evaluate-analyze-rewrite 顺序。
- 反馈如何获得：`evaluate` 返回 per-row predictions；`python` 在受限 sandbox 中读取 eval DataFrame，用 pandas/numpy 生成自定义错误分析。
- 如何选择候选：full-split evaluate 后若主指标低于 best-seen，auto-rollback 到最佳 prompt；可选 guard metric floor 防止副指标跌破阈值。
- 是否使用记忆/archive：维护 best metric baseline 和 eval history，但不是长期 prompt archive。
- 是否优化 optimizer 自身：否。SPEAR 改变 optimizer 的工具能力和 orchestration autonomy，而不是训练 optimizer prompt。

## 实验设置

- 工业任务：Hiring Assistant 10 个 extraction-judge dimensions、CMA 2 个 tool-selection judges、Facet Suggestion 1 个 filter-relevance judge。
- 公开任务：BBH-7 和 GSM8K。
- 指标：工业任务主要用 Cohen's kappa 或 macro-F1；BBH/GSM8K 用 accuracy。
- 模型：task model 为 GPT-4o；SPEAR 和 GEPA optimizer 使用 GPT-5.4 内部部署；TextGrad 主配置使用 GPT-4o，附录有 GPT-5.4 统一视图。
- 预算：SPEAR `max_eval_calls=15-20`；GEPA `max_metric_calls=400-500`；TextGrad `max_steps=5`。
- 注意：工业 headline 是 best-of-N，且各方法 N 不完全对称；论文用 single-seed unified-optimizer view 和 multi-seed 方差补充约束。

## 主要结果

论文直接报告：

- 工业主表中，SPEAR 在 12 个可比工业任务里赢 11 个；唯一例外是 near-ceiling 的 Hiring Assistant unsound inference，TextGrad 为 0.968，SPEAR 为 0.937。
- 最大增益集中在难任务：Hiring Assistant job location kappa 0.760 vs TextGrad 0.110 / GEPA 0.361；CMA tool-missing 0.976 vs 0.694 / 0.631；Facet macro-F1 0.846 vs 0.751 / 0.734。
- BBH-7 平均准确率 SPEAR 0.938，GEPA 0.628，TextGrad 0.484；但论文指出大部分来自 output-format rewriting，不应被解读成所有 reasoning 任务的结构性胜利。
- GSM8K 上三者几乎都不动：SPEAR 0.965，GEPA 0.960，TextGrad 0.956。
- 消融中，移除 Python tool 是复杂 judge 任务最大损失来源：Hiring Assistant location 降 0.35 kappa，CMA tool-missing 降 0.79 kappa。
- 把完整 train eval DataFrame 作为文本塞给无 Python agent 不能恢复 Python tool：在 CMA tool-missing 上只恢复 A1-to-full gap 的 2%，说明关键不是信息量，而是结构化聚合能力。
- free-form agent 换成同工具 rigid loop，会在 Hiring Assistant location 损失 0.27 kappa，在 BBH logical_deduction_5obj 损失 26 个百分点。
- 78 个 archived SPEAR runs 中，71 个有实质提升，7 个 plateau，没有一个最终低于 seed；论文把这归因于 auto-rollback 抬高下限。

## 失败案例和局限

论文直接报告：

- 优化器模型 GPT-5.4 是内部部署别名，外部无法精确复现具体 point release。
- 三个工业 benchmark 和部分 optimized prompts 不能完整公开，因为涉及内部标注和专有政策内容。
- GPT-4o 在 `T=0` 下也不是 bit-reproducible；小样本 judge 的 kappa 方差很大，单 seed 消融里小于 0.05 的差异只能视为方向性。
- SPEAR 能看到 valid aggregate label distribution，虽不看 valid row content，但相对 GEPA/TextGrad 有 read-side asymmetry。
- 优化后的 prompt 长度约增长 2 倍，生产可能需要后处理压缩或长度惩罚。
- Python sandbox 假设 trusted optimizer LLM 和内部数据；AST whitelist 不是强安全边界，不适合直接面对不可信用户数据。

## 洞见卡片

```yaml
insight: 错误分析能力应该是 optimizer 的工具，而不只是 prompt 里的要求。
evidence_type: direct-method + ablation
paper_evidence:
  section: "3, 4.4, 5"
  table_or_figure: "Figure 1, Table 9, Case studies"
  quote_or_paraphrase: "移除 Python tool 在 CMA tool-missing 上损失约 0.79 kappa；直接把完整 DataFrame 放进上下文只恢复 2% gap。"
mechanism: LLM 长上下文不稳定地抽取多维统计结构；代码可以可靠计算 confusion matrix、groupby、per-class metrics。
actionable_rule: 对 judge/分类/抽取 prompt 优化，优先给 optimizer 提供受控表格分析工具，而不是只给自然语言 critique。
counterexample_or_limit: 对 GSM8K 或 near-saturated tasks，Python tool 几乎没有增益。
minimal_experiment: text-only critique vs full-DF-in-context vs python-analysis tool。
confidence: high-for-structured-eval; low-for-open-ended-generation
```

```yaml
insight: prompt 优化里的“agent 自主编排”本身可产生收益。
evidence_type: ablation
paper_evidence:
  section: "4.4"
  table_or_figure: "Component ablations"
  quote_or_paraphrase: "同样四个工具但固定 rigid loop，在 Hiring Assistant location 损失 0.27 kappa，在 BBH logical_deduction_5obj 损失 26 pp。"
mechanism: 不同任务需要不同分析顺序；有些先写代码聚类，有些先修格式，有些需要多次 eval 后再改 prompt。
actionable_rule: 不要把 optimizer 固定成单一 evaluate -> critique -> rewrite pipeline；至少允许工具调用顺序由策略选择。
counterexample_or_limit: autonomy 依赖强 optimizer model；降到 GPT-4o 时论文报告 near-total failure。
minimal_experiment: fixed-cycle optimizer vs tool-choice optimizer under same tools and budget。
confidence: medium-high
```

```yaml
insight: auto-rollback 更像是提高优化器下限，而不是提高平均最优点。
evidence_type: discussion + ablation
paper_evidence:
  section: "3.2, 4.4, 6"
  table_or_figure: "Algorithm 1, Failure modes"
  quote_or_paraphrase: "A2 在单 seed CI 内，作者不声称显著提高均值；但 78 个 logged runs 中没有低于 seed 结束。"
mechanism: 回滚阻止坏 prompt 留在最终结果，但不一定帮助发现更好 prompt。
actionable_rule: 所有自动 prompt 改写实验都应该默认保留 seed prompt 和 best-seen prompt，并报告是否曾出现 metric regression。
counterexample_or_limit: 如果 dev metric 噪声大，rollback 可能保守地拒绝有泛化潜力的候选。
minimal_experiment: with rollback vs without rollback under noisy dev split。
confidence: high
```

## 对本项目的启发

- 对任何有表格标签的任务，prompt evolution pipeline 应内置 dataframe analysis step，至少生成 confusion matrix、top error clusters、per-label precision/recall。
- 日志字段要保存 optimizer 写出的 analysis code、代码输出、基于该输出的 prompt rewrite rationale。
- 我们不能把“把数据放进上下文”当作结构化分析的替代品；SPEAR 的消融正好说明长上下文无法稳定完成聚合。
- 生产化时必须区分 offline trusted sandbox 和 online untrusted execution；本项目只能先做离线复现实验。

## 可复现计划

- 最小复现任务：多类别 judge 或结构化抽取任务，50-200 行 labeled eval DataFrame。
- 需要实现的模块：
  - evaluate tool 返回 per-row predictions。
  - restricted Python analysis sandbox。
  - set_prompt + auto-rollback。
  - guard metric floor。
  - code/output/rewrite 日志。
- 预计风险：
  - optimizer model 不够强时无法写出有效分析代码。
  - 小样本 kappa 方差导致伪提升。
  - sandbox 安全边界不足。
  - prompt 变长影响部署成本。
