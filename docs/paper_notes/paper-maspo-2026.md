# Paper Note: MASPO / Joint Prompt Optimization for LLM-based Multi-Agent Systems

论文：MASPO: Joint Prompt Optimization for LLM-based Multi-Agent Systems

链接：https://arxiv.org/abs/2605.06623

source_id：paper-maspo-2026

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：extension

阅读日期：2026-06-08

reviewed_by：Codex

local_pdf_path：`local_sources/raw/arxiv_papers/2605.06623/paper.pdf`

local_pdf_sha256：`B94DD416006E002FF8A4CF80A6FD875732A1815FAFAC6E27452A2B0A9856520D`

local_text_path：`local_sources/raw/arxiv_papers/2605.06623/paper.txt`

local_text_sha256：`17A05D15B1536E2F530DA83E587130A41666E18A781087C6FC498D8A289C9C44`

evidence_level：method-results-ablation-read

## 一句话结论

MASPO 的核心价值是把多 agent prompt 优化里的“局部看起来对、全局反而错”显式建模，用 local validity、lookahead potential、global alignment 和 misalignment cases 来避免只优化单个 agent 的局部指标。

## 问题设定

- 任务：数学、复杂推理、代码生成等多 agent 协作任务。
- 优化对象：多 agent 系统中各 agent 的 prompt。
- 目标指标：最终任务 accuracy，同时用 joint reward 评估中间 agent prompt。
- 约束：不需要 ground-truth label 直接用于每个中间 agent；通过 joint evaluation 做 credit assignment。

## 方法摘要

- 候选如何生成：按 MAS 拓扑顺序做 coordinate-ascent 风格优化，并用 evolutionary beam search 生成 agent prompt 候选。
- 反馈如何获得：对候选 agent prompt 计算 Local Validity、Lookahead Potential、Global Alignment。
- 如何选择候选：joint reward + beam refresh；额外采样 misalignment cases，即局部有效但全局失败的样本。
- 是否使用记忆/archive：使用 misalignment buffer 和 beam pool。
- 是否优化 optimizer 自身：否。

## 实验设置

- 数据集：MATH-500、AGIEval-MATH、AQuA、GPQA、MBPP、HumanEval-ET。
- 模型：Gemini-2.5-pro 作为 optimizer/evaluator；MAS agent 使用指定 backbone。
- baselines：Vanilla、CoT、SC(CoT)、Self-Refine、AgentDropout、Sequential MAS、Hierarchical MAS、TPE、SPO。
- train/dev/test 切分：sample pool 50，优化阶段固定 budget；最终在 benchmark 上评估。
- 成本或调用次数：beam width 2，每 parent 生成 2 个候选；topological round 和优化 round 都设为 3。

## 主要结果

- Sequential MAS 上，MASPO 平均 70.39，超过 Sequential baseline 65.31、TPE 66.49、SPO 66.56。
- Hierarchical MAS 上，MASPO 平均 71.05，超过 baseline 68.32、TPE 68.47、SPO 69.01。
- 论文报告 MASPO 相比最佳优化 baseline 平均提升 2.90，并且对 Sequential / Hierarchical 两种拓扑都有效。
- 消融中，去掉 Joint Evaluate 平均降到 67.77，去掉 Beam Refresh 降到 68.53；说明 joint reward 和搜索调度都贡献明显。
- lookahead 从 1-step 增到 2/3-step 只带来很小提升，作者因此选择低成本 lookahead。

## 失败案例和局限

- 多 agent 结果对 evaluator/optimizer 的质量敏感；弱 backbone 自优化表现明显降低。
- Misalignment sampling 并非在所有任务上单调提升，Kmis 也需要预算和噪声平衡。
- 论文保持固定 MAS 拓扑，未解决是否应该同时优化拓扑。

## 洞见卡片

```yaml
insight: 多 agent prompt 优化必须专门收集“局部成功、全局失败”的 misalignment cases。
evidence_type: ablation + method-design
paper_evidence:
  section: "3.2 Joint Reward; 4.2 Main Result; Table 2"
  table_or_figure: "Table 1, Table 2"
  quote_or_paraphrase: "w/o Joint Evaluate 明显下降；MASPO 通过 misalignment-aware sampling 处理局部-全局错配。"
mechanism: 单 agent 局部指标可能鼓励对自己角色有利但破坏下游协作的 prompt。
actionable_rule: 多 agent eval 日志要保存每个 agent 的局部输出、下游影响和 final outcome，标记 local-pass/global-fail。
counterexample_or_limit: 如果 agent 之间交互弱，joint optimization 的额外成本可能不划算。
minimal_experiment: independent agent optimization vs joint reward vs joint reward + misalignment sampling。
confidence: medium-high-for-multi-agent
```

## 对本项目的启发

- 多 agent 实验不能只给每个 agent 单独打分；要记录下游 successor utility。
- 建议在我们的 schema 中加入 `local_validity`、`lookahead_delta`、`global_alignment`、`misalignment_case`。
- 对复杂系统先测 agent coupling；如果 coupling 弱，MASPO 这类 joint 方法可能过重。

## 可复现计划

- 最小复现任务：2-3 agent 的顺序推理或抽取-判断 pipeline。
- 需要实现的模块：per-agent trace、joint reward scorer、misalignment buffer、beam refresh。
- 预计风险：evaluator 噪声；中间 credit 不可解释；多 agent budget 快速膨胀。
