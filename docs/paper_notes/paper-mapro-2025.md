# Paper Note: MAPRO / Multi-Agent Prompt Optimization as MAP Inference

论文：MAPRO: Recasting Multi-Agent Prompt Optimization as Maximum a Posteriori Inference

链接：https://arxiv.org/abs/2510.07475

source_id：paper-mapro-2025

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：extension

阅读日期：2026-06-08

reviewed_by：Codex

local_pdf_path：`local_sources/raw/arxiv_papers/2510.07475/paper.pdf`

local_pdf_sha256：`8C17CC9E75C00A86C4BB0CE6F600F0F118C3098EB2F97F437E9A460C08A02D98`

local_text_path：`local_sources/raw/arxiv_papers/2510.07475/paper.txt`

local_text_sha256：`39038AFE376C4D94A412DF5B31D7A14AA5FC18B6CC2D0B18961D547DF2571A3C`

evidence_level：method-results-ablation-read

## 一句话结论

MAPRO 把多 agent prompt 优化从“给每个 agent 反思改写”提升为“在固定拓扑上做联合后验推断”：通过语言引导的 max-product belief propagation 和 topology-aware refinement，把 credit 沿 agent/edge 传播，而不是只看单点 prompt 分数。

## 问题设定

- 任务：代码生成、问答、数学推理等多 agent benchmark。
- 优化对象：固定 MAS 拓扑中各 agent 的 prompts / demonstrations。
- 目标指标：各 benchmark accuracy/pass rate。
- 约束：保持 MAS topology 固定；不做模型训练。

## 方法摘要

- 候选如何生成：构建 prompt candidate pool，对节点和边生成/更新候选 prompt。
- 反馈如何获得：统一 reward model 对 node-level、edge-level、global behavior 打分。
- 如何选择候选：把 joint prompt optimization 形式化为 MAP inference，用 language-guided max-product belief propagation 传播局部 belief。
- 是否使用记忆/archive：维护候选池和优化轨迹。
- 是否优化 optimizer 自身：否。

## 实验设置

- 数据集：HumanEval-ET、MBPP-Plus、CodeContest、NewsQA、WebQuestion、MATH、GSM8K 等。
- 模型：Claude Haiku 3.5、Llama 3.3-70B 等。
- baselines：Raw、CoT、ReAct、EvoPrompt、PromptBreeder、Chain MAS、DMAD、ChatEval、Direct、TPE 等。
- train/dev/test 切分：使用任务验证反馈优化，报告多次 mean/std。
- 成本或调用次数：论文强调固定拓扑的 plug-and-play 优化，未把成本作为主表指标。

## 主要结果

- Claude Haiku 3.5 表中，MAPRO 在多个 MAS 设置下达到最好或接近最好结果，例如一组 MAPRO 在 HumanEval-ET 80.21、MBPP-Plus 76.54、GSM8K 93.48。
- Llama 3.3-70B 表中，MAPRO 在 Chain、DMAD、ChatEval 等 MAS 下普遍超过 Direct/TPE。
- 作者总结 MAPRO 在 reasoning-intensive tasks 上收益更明显，例如 WebQuestions、MBPP-Plus；knowledge-heavy task 上收益相对小。
- 去掉 demonstration-guided reward 有明显 drop，例如 HumanEval-ET 从 80.21 降到 76.04，CodeContest 从 31.52 降到 29.70。
- 优化轨迹分析显示 MAPRO 较其他方法更平稳，且 prompt 逐步变得更 task-specific。

## 失败案例和局限

- 只优化固定 topology；作者承认 topology 本身可能带来更大收益，但优化拓扑更复杂。
- MAPRO 的 reward model 设计和 demonstration-guided scoring 对结果关键，外部复现需要严格固定。
- 多 agent benchmark 多、表格复杂，但没有充分隔离“拓扑差异”和“prompt 优化差异”的全部因果关系。

## 洞见卡片

```yaml
insight: 多 agent prompt 优化应沿拓扑传播 credit，而不是把 agent 当彼此独立的 prompt。
evidence_type: method + ablation
paper_evidence:
  section: "4.2 Main Results; 4.4 Reward Model Analysis"
  table_or_figure: "Table 3, Table 4"
  quote_or_paraphrase: "MAPRO 在固定拓扑下普遍超过 Direct/TPE；去掉 demonstration-guided reward 出现 performance drop。"
mechanism: agent 输出会影响下游 agent，node/edge reward 能把局部候选与全局表现连接起来。
actionable_rule: 多 agent prompt 记录应包含 topology edges、node prompt、edge feedback 和 global reward。
counterexample_or_limit: 如果拓扑本身不合适，固定拓扑上的 prompt 优化可能只能局部改善。
minimal_experiment: independent node optimization vs topology-aware reward propagation。
confidence: medium
```

## 对本项目的启发

- 如果研究 agent prompt evolution，必须把 topology 作为实验条件记录，即使本轮不优化拓扑。
- MAPRO 的轨迹可解释性提示我们要保存每轮 prompt diff 和重复出现的改写主题，供人工沉淀规则库。
- demonstration-guided reward 是一个值得单独测试的变量，不能默认并入 evaluator。

## 可复现计划

- 最小复现任务：固定 2-3 节点 MAS，节点间有明确输入输出边。
- 需要实现的模块：node/edge reward schema、candidate pool、belief-propagation-like selector。
- 预计风险：reward model 过拟合 dev；拓扑影响大于 prompt；实现复杂度较高。
