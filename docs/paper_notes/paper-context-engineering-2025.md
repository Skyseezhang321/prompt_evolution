# Paper Note: A Survey of Context Engineering for Large Language Models

论文：A Survey of Context Engineering for Large Language Models（ICT/CAS 等）

链接：https://arxiv.org/abs/2507.13334

source_id：paper-context-engineering-2025

关联 issue：无

线索贡献者：internal-arxiv-search（综述补读，用于范围边界与相邻领域校验）

新颖性判断：survey-boundary-reference（界定 prompt 优化与 context engineering 的边界）

阅读日期：2026-06-10

reviewed_by：Claude

local_pdf_path：`local_sources/raw/arxiv_papers/2507.13334/paper.pdf`

local_pdf_sha256：`AB220955B1FD9FE1D590BFEEF946F52B4E1DDBF317A58BC18FC2863B3CB3D4A5`

local_text_path：`local_sources/raw/arxiv_papers/2507.13334/paper.txt`

local_text_sha256：`6072C86F698C9A4F27834D07048D88EA55D5413F62F1481677496E48784E6225`

evidence_level：taxonomy-read（166 页超大综述，本轮只读目录/taxonomy 结构、定义、组件划分和 future directions；各组件逐论文与基准未深读，后续如需可定向补读特定节）

版本说明：本地 PDF 为 v2（2025-07-21）；配套 `Awesome-Context-Engineering` 仓库。

## 一句话结论

这份综述把 **context engineering 当作 prompt engineering 的超集**：prompt/instruction 只是"Context Retrieval & Generation"下的一个基础组件（§4.1.1），外面还套着检索、动态上下文组装、长上下文处理、记忆层级、上下文压缩，以及 RAG / 工具调用 / 多 agent 等系统实现。对本项目的价值是**确认范围边界**——我们做的是"离散自然语言 prompt 优化"，而非整个 context engineering；同时它点出两个**真正相邻、值得登记为边界的优化目标**：上下文压缩（=约束式 prompt 优化）和智能上下文组装/选择（"放什么进上下文"本身是优化问题）。

## Survey 定位与范围

- 定义：context engineering = 系统化设计、优化进入 LLM 的全部上下文信息（远超单段 prompt）。
- 体量：166 页，组件×系统×评估×future 四大块；定位为 LLM agent / 多 agent 时代的上下文工程地图。

## Taxonomy 结构（目录骨架）

- **Foundational Components §4**：
  - Context Retrieval & Generation §4.1：**Prompt Engineering & Context Generation §4.1.1**（prompt 优化在此）/ External Knowledge Retrieval（RAG 检索）/ Dynamic Context Assembly。
  - Context Processing §4.2：Long Context / Contextual Self-Refinement / Multimodal / Relational-Structured。
  - Context Management §4.3：Fundamental Constraints / **Memory Hierarchies & Storage** / **Context Compression** / Applications。
- **System Implementations §5**：RAG（Modular / Agentic / Graph-Enhanced）/ **Memory Systems**（架构 / memory-enhanced agents / 评估）/ **Tool-Integrated Reasoning**（function calling / agent-environment）/ **Multi-Agent Systems**（通信协议 / 编排 / 协调）。
- **Evaluation §6**：组件级 / 系统级 / 基准 / safety-robustness。
- **Future Directions §7**：理论统一框架 / scaling laws / 多模态 / 下一代架构 / 高级推理规划 / 图问题 / **Intelligent Context Assembly & Optimization §7.2.4** / 领域专化 / 大规模多 agent / 人机协作 / 部署-安全-伦理。

## 对本项目 taxonomy 的边界与完整性信号

- **确认边界（我们刻意不做的相邻系统）**：RAG 架构、检索器优化、长上下文处理、function-calling 机制、多 agent 通信协议——这些是 context engineering 的系统实现，本项目把它们当边界材料而非 APO 核心，综述结构支持这一划分。
- **真正相邻、应在渠道综合登记为"边界但相关"的两点**：
  1. **Context Compression §4.3.3**：与 [[paper-ape-survey-2025]] 的 constrained optimization（∥P∥≤κ）同构——压缩 prompt/上下文以省 token，是约束式 prompt 优化，和我们的 prompt-hygiene/length 主题（[[paper-textreg-2026]]）直接相邻。
  2. **Intelligent Context Assembly & Optimization §4.1.3 / §7.2.4**："放哪些信息进上下文"作为优化问题——是 exemplar/context selection 的放大版（[[paper-teach-better-show-smarter-2024]] 的 exemplar selection 是其子集）。
- **记忆系统**：本项目已通过 [[paper-memapo-2026]]、[[paper-erm-memory-2024]]、[[paper-prompt-codebooks-2026]] 覆盖记忆型自进化；综述把 memory 作为一等系统组件，确认这条线值得继续，但其架构/存储层面属 context engineering 范畴。

## 对本项目的启发

> 字段定义与 insight / conclusion / helpful method 的区分口径见 `docs/insight_field_standard.md`。

- conclusion：本项目聚焦"离散自然语言 prompt/instruction + 少量 exemplar/memory"是合理的窄范围选择；context engineering 是更大盘子。渠道综合应**显式声明**：RAG/检索/长上下文/工具/多 agent 系统实现属边界，本项目只在它们与"可优化 prompt artifact"相交处取材。
- helpful method：把"上下文压缩"与"智能上下文组装"两条作为 backlog 边界条目登记（不展开深读，但在最终报告承认其存在并给指针），避免读者误以为我们漏了。
- anti-pattern / limit：把 context engineering 整体纳入本项目范围会导致范围爆炸（166 页的体量）；应坚持窄边界。
- 适用场景：界定范围、给最终报告写"我们不做什么"一节、登记两条相邻优化目标。
- 误用风险：survey 体量巨大且偏 agent/系统，若当作 APO 证据来源会稀释本项目主线；只用其 taxonomy 做边界参照，不把其逐组件结论当本项目证据。

## 最小验证或演示计划

- 要验证的 insight / method：本项目范围边界声明是否覆盖了 context engineering 的主要相邻组件。
- 最小验证任务：在渠道综合/最终报告加"范围边界"一节，逐条对照 §4–§5 组件标"核心/边界/不做"。
- 观察指标：被误读为"漏掉"的相邻组件数（目标为 0，靠显式声明消除）。
- 预计风险：如后续项目扩到 RAG/agent 实验，需要定向补读本综述的对应章节，而非现在全读。
