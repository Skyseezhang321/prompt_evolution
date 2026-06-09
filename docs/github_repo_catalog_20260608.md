# GitHub 仓库内容 catalog：2026-06-08

本页是第二层“详细内容介绍”。它按统一字段整理首批严格保留的 8 个 GitHub 仓库，并附 2 个宽松场景候选。此 catalog 的目标不是下最终结论，而是为后续深读、来源清单登记和最小实验设计提供结构化入口。

字段说明：

- 定位：仓库本身解决的问题。
- 关系：与 prompt optimization / prompt self-evolution 的关系。
- 优化对象：prompt text、system prompt、context、agent workflow、memory、RAG pipeline 等。
- 反馈信号：是否看到 eval、test、comparison、benchmark、human feedback、LLM critique 等。
- 可复现性：是否有可运行代码、数据、固定流程或清晰实验入口。
- 本项目价值：对本项目的具体用法。
- 处理建议：深读、引用、候选、暂缓或剔除。

## 严格保留集

### `linshenkx/prompt-optimizer`

- 链接：https://github.com/linshenkx/prompt-optimizer
- 定位：面向用户的 prompt optimization 工具，提供 Web、桌面、浏览器扩展、Docker 等使用方式。
- 关系：首批样本中最直接相关的 prompt optimizer。README 和 topics 都明确指向 prompt optimization、prompt testing、prompt toolkit。
- 优化对象：system prompt、user prompt、prompt templates、可复用 prompt assets。
- 反馈信号：README 声称支持 analysis、single-result evaluation、multi-result compare evaluation；需要深读确认评估器实现、评分标准和是否有固定数据集。
- 可复现性：有产品代码和部署方式；但是否能复现实验结论取决于是否能固定模型、参数、样本和评估器。
- 本项目价值：可作为“工程产品型 prompt optimizer”的代表，拆解 prompt 优化产品应该具备哪些闭环能力。
- 处理建议：进入核心深读和 `source_inventory.md`；重点核验优化流程、评估机制、prompt 版本管理和回滚点。

### `karpathy/autoresearch`

- 链接：https://github.com/karpathy/autoresearch
- 定位：让 AI agent 自动运行小型 LLM 训练研究实验的 repo。
- 关系：不是 prompt optimizer，但高度相关于 prompt/context self-evolution。它用 `program.md` 给 agent 提供研究组织上下文，让 agent 修改训练代码、运行实验、评估结果、保留或丢弃变体。
- 优化对象：研究 agent 的 context/program、实验代码和训练配置，不是单一 prompt 字符串。
- 反馈信号：训练指标和实验结果；README 描述了改动、训练、检查是否改善、重复的闭环。
- 可复现性：有明确 quick start、训练脚本和实验运行方式，但需要 GPU 和固定环境。
- 本项目价值：可把“prompt 自进化”扩展为“agent context/program 自进化”的最小实验参考。
- 处理建议：进入核心深读；提炼闭环结构，用来设计本项目的最小 self-evolving prompt/context 实验。

### `dair-ai/Prompt-Engineering-Guide`

- 链接：https://github.com/dair-ai/Prompt-Engineering-Guide
- 定位：prompt engineering、context engineering、RAG 和 AI agents 的指南、论文、课程和资源库。
- 关系：与 prompt optimization 的关系是 taxonomy / 背景资料，不是优化器或实验框架。
- 优化对象：prompt 技法、prompt elements、LLM settings、RAG、agent patterns 等知识体系。
- 反馈信号：资料汇编本身没有统一 eval；需要回到其引用的论文或教程核验。
- 可复现性：作为指南可读性强，但不是实验 artifact。
- 本项目价值：用于建立术语、方法分类和学习路径，避免本项目只围绕 APO 论文而忽略 prompt engineering 基础。
- 处理建议：作为高质量综述/资源来源登记；不把它的观点直接当作实证结论。

### `humanlayer/12-factor-agents`

- 链接：https://github.com/humanlayer/12-factor-agents
- 定位：构建可靠 LLM agent 应用的工程原则文档。
- 关系：不直接自动优化 prompt，但强调 own your prompts、own your context window、tool calls、execution state、human contact、small focused agents 等 agent/context engineering 原则。
- 优化对象：prompt ownership、context window、tool call interface、agent state、human-in-the-loop workflow。
- 反馈信号：主要是工程经验和原则，不是固定 benchmark；可转化为 eval 维度。
- 可复现性：文档型来源，复现性来自是否能把原则转为具体测试和工作流。
- 本项目价值：帮助定义生产级 prompt/context self-evolution 的治理边界：不是让模型任意改 prompt，而是围绕状态、工具、人审和可恢复性设计。
- 处理建议：进入重点深读；提炼为本项目 agent eval 和治理指标。

### `shanraisshan/claude-code-best-practice`

- 链接：https://github.com/shanraisshan/claude-code-best-practice
- 定位：Claude Code agentic engineering 资料汇编，覆盖 subagents、memory、commands、skills、orchestration workflow 等。
- 关系：偏 coding-agent workflow 和 context engineering，不是 prompt optimizer。
- 优化对象：agent memory、commands、skills、subagent orchestration、project rules。
- 反馈信号：README 主要是链接和实践目录；需要检查具体 best-practice 文档是否有 eval、失败案例或可复现流程。
- 可复现性：较依赖具体 Claude Code 环境和文档质量；当前更像 curated practices。
- 本项目价值：可用于收集 coding-agent prompt/context 管理模式，辅助设计 agent 行为规则 eval。
- 处理建议：二级参考；先不深挖全部内容，优先抽取 memory、subagent、orchestration 的可评估规则。

### `affaan-m/ECC`

- 链接：https://github.com/affaan-m/ECC
- 定位：跨 agent harness 的 operator system，涉及 skills、memory optimization、continuous learning、security scanning、token optimization、evals、system prompt slimming 等。
- 关系：如果 README 描述属实，它与本项目的工程治理和 agent prompt/context 优化高度相关。
- 优化对象：system prompt、memory、skills、agent harness、token budget、verification loops。
- 反馈信号：README 提到 checkpoint/continuous evals、grader types、pass@k 等，但需要核验是否有真实实现和可复现实验。
- 可复现性：未完成核验；star/fork 和 README 中指标叙述需要和 GitHub API、license、核心代码结构交叉检查。
- 本项目价值：可能提供 prompt/context/memory/verification loop 的工程系统案例。
- 处理建议：作为“需核验重点候选”；在核验前不要把它作为强证据。

### `f/prompts.chat`

- 链接：https://github.com/f/prompts.chat
- 定位：大型开源 prompt library / prompt dataset。
- 关系：不是 prompt optimizer；提供 prompt 样本、prompt 分类和 prompt asset 管理参考。
- 优化对象：prompt assets 和 prompt examples，不负责自动改写或 eval。
- 反馈信号：没有统一任务 eval；价值在样本覆盖和真实用户 prompt 形态。
- 可复现性：内容和数据集可抓取，但需要注意版权、任务标签和质量噪声。
- 本项目价值：后续可作为 prompt 样本池，分析常见 prompt 结构或构造最小评测任务。
- 处理建议：暂不深读方法；若进入数据阶段，再固定 commit 或 dataset snapshot。

### `pathwaycom/llm-app`

- 链接：https://github.com/pathwaycom/llm-app
- 定位：RAG、AI pipeline、enterprise search 的可部署模板。
- 关系：与 prompt 优化弱相关，主要代表 context/RAG pipeline 层。
- 优化对象：data sync、retrieval、indexing、RAG templates、token cost / accuracy tradeoff。
- 反馈信号：README 提到不同 pipeline 和 adaptive RAG，但是否有公开 benchmark 需要另查。
- 可复现性：模板和 Docker/API 入口较清晰；但与 prompt 优化实验不是同一变量。
- 本项目价值：提醒在实验设计中区分 prompt 变量、context 变量和 retrieval 变量，避免伪因果结论。
- 处理建议：作为 context/RAG 边界参考，不进入 APO 核心深读。

## 宽松场景候选

### `google-gemini/gemini-cli`

- 链接：https://github.com/google-gemini/gemini-cli
- 定位：Gemini 的开源 CLI agent。
- 关系：不是 prompt optimizer，但可作为 agent prompt/context eval 的运行场景。
- 优化对象：custom context files、MCP、CLI workflow、agent behavior。
- 反馈信号：需要查具体 tests、benchmarks 或 PR review workflow。
- 处理建议：暂不进入核心分析；仅在需要 agent eval 场景时回看。

### `browser-use/browser-use`

- 链接：https://github.com/browser-use/browser-use
- 定位：让 AI agent 操作浏览器的自动化框架。
- 关系：不是 prompt optimizer；可作为 tool-use / browser-agent prompt eval 的任务环境。
- 优化对象：browser agent instruction、tool-use policy、task execution traces。
- 反馈信号：本轮因 GitHub API rate limit 未抓到 README 快照，需要补抓。
- 处理建议：场景候选；不进入当前 prompt optimization 核心结论。

## Catalog 观察

- 直接 prompt optimizer：只有 1 个强相关仓库。
- 可转化为 self-evolution 实验设计的仓库：`karpathy/autoresearch` 最强。
- 工程治理和 context engineering 的仓库数量多于 APO 工具，说明 GitHub 生态更关注 agent workflow 的可靠性，而不是论文式 prompt search。
- 数据/资产型仓库有用，但应与方法型仓库分开，避免把 prompt library 当作优化方法。
