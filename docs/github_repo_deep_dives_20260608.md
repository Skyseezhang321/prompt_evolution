# GitHub 重点仓库深读：2026-06-08

本页是第三层“重点仓库详细介绍”。第一轮重点覆盖 4 个核心仓库，并附 1 个需核验重点候选。

重点选择原则：

- 能直接改变本项目的方法判断。
- 能转化为最小可复现实验或 eval 维度。
- 能帮助区分 prompt text optimization、context engineering、agent workflow 和 self-evolution。

## 1. `linshenkx/prompt-optimizer`

链接：https://github.com/linshenkx/prompt-optimizer

### 为什么重点看

这是首批 GitHub 样本里最直接的 prompt optimization 工具。它不是论文方法，而是产品化工具，因此适合回答一个工程问题：如果要把 prompt 优化做成可用工具，闭环里至少要包含哪些模块。

### 内容概要

仓库定位是帮助用户改写 prompt、测试 prompt、比较结果并保存可复用 prompt assets。README 显示它支持 Web、桌面、浏览器扩展和 Docker 部署，面向实际使用场景而非单一 benchmark。

它的核心对象包括：

- system prompt
- user prompt
- prompt template
- imported prompt / prompt garden
- reusable prompt asset

从 README 看，它至少覆盖三个环节：

1. 生成或改写候选 prompt。
2. 对 prompt 结果做分析、单次评估或多结果比较。
3. 保存优化后的 prompt，形成可复用资产。

### 对本项目的启发

这个仓库说明，工程型 prompt optimizer 不只是“把一句 prompt 写得更好”，而应至少记录：

- 原始 prompt
- 优化后 prompt
- 优化原因或优化模式
- 测试输入
- 输出比较
- 评估方式
- 保存版本
- 使用场景

这与本项目 AGENTS.md 中“每个 prompt 变体都要记录模型、参数、数据集、评分器、成本和失败案例”的要求一致。

### 证据强度

当前证据强度：中。

理由：

- README 和 topics 强相关。
- 有可运行产品形态。
- 但尚未核验内部优化 prompt、eval prompt、数据结构、版本存储和测试样本。
- 尚未确认是否有固定 benchmark 或失败案例记录。

### 深读问题

- 优化器使用哪些内置 meta-prompt 或模板？
- 是否区分 system prompt 和 user prompt 的优化目标？
- multi-result compare evaluation 如何实现，是人工比较、LLM judge，还是规则评分？
- 是否记录模型、参数、成本、版本和回滚点？
- 是否能导出 prompt diff 和评估结果？

### 可转化实验

最小实验候选：

- 选 10 个短 prompt，固定模型和任务输入。
- 用该工具产生优化版本。
- 用人工规则 + LLM judge 双评估比较 baseline 和 optimized。
- 记录哪些改写提升清晰度，哪些只是扩写或过拟合 judge。

## 2. `karpathy/autoresearch`

链接：https://github.com/karpathy/autoresearch

### 为什么重点看

它不是 prompt optimizer，却是本批 GitHub 仓库中最接近“自进化闭环”的案例。README 描述的核心流程是：agent 修改实验代码，运行训练，检查是否改善，保留或丢弃，然后重复。

### 内容概要

仓库围绕一个小型 LLM 训练设置组织 agent 自动研究。关键对象包括：

- `program.md`：给 agent 的研究组织上下文和行为说明。
- `train.py`：agent 可以修改的训练代码。
- `prepare.py`：固定数据准备和评估工具。
- 实验运行结果：用于判断改动是否保留。

这个设计的关键点是把“可编辑对象”和“固定对象”分开：

- 固定：数据准备、基本评估工具、运行环境。
- 可变：agent context / program、训练代码、模型超参或实现。
- 选择：基于实验结果保留或丢弃。

### 对本项目的启发

prompt 自进化可以借鉴这个结构，而不是让模型自由改系统 prompt：

```text
固定任务和评估器
-> 读取当前 prompt/context
-> 生成候选修改
-> 在隔离样本上运行
-> 根据指标和失败案例选择
-> 保留候选或回滚
-> 记录下一轮经验
```

它还提醒我们，真正的 self-evolution 不应只保存“更好的 prompt”，还要保存：

- 为什么生成候选
- 哪些实验支持保留
- 哪些失败导致丢弃
- 当前 context/program 的职责边界
- 哪些文件或规则不可自动修改

### 证据强度

当前证据强度：中偏高。

理由：

- README 给出清晰运行闭环。
- 有代码和 quick start。
- 但优化对象不是 prompt，需要转译到本项目场景。
- 需要实际运行后才能评价闭环稳定性。

### 深读问题

- `program.md` 如何定义 agent 行为和实验边界？
- agent 如何记录实验日志和选择理由？
- 是否存在自动回滚或人工审核点？
- 是否容易出现 overfitting 到短训练 run？
- 这个闭环如何映射到 prompt optimization，而不引入代码变更变量？

### 可转化实验

最小实验候选：

- 用 `program.md` 形式定义一个 prompt optimizer agent。
- 固定一个小任务集和评分器。
- 只允许修改 prompt 文件，不允许改评估器和数据。
- 每轮生成一个候选 prompt，运行 dev set，记录保留/丢弃。
- 对 held-out set 验证是否真实提升。

## 3. `humanlayer/12-factor-agents`

链接：https://github.com/humanlayer/12-factor-agents

### 为什么重点看

它提供的不是优化算法，而是生产 agent 的工程原则。对本项目来说，这类原则可以转化为 prompt/context self-evolution 的护栏和 eval 维度。

### 内容概要

README 把可靠 LLM agent 应用拆成多个 factor，包括 prompt ownership、context window、tool calls、execution state、human contact、small focused agents 等。

其中与本项目最相关的是：

- Own your prompts：prompt 应该是可管理、可审查、可版本化的工程对象。
- Own your context window：context 不是随意堆叠文本，而是需要组织、裁剪和治理。
- Tools are structured outputs：tool policy 与 prompt 共同决定 agent 行为。
- Launch/Pause/Resume：agent workflow 需要可暂停、恢复和审查。
- Small focused agents：降低单个 agent 的职责复杂度。

### 对本项目的启发

自动优化 prompt 时，不能只优化最终答案准确率，还要监控：

- tool call 是否正确
- context 是否被污染或过载
- 是否越权调用工具
- 是否能暂停和人工接管
- 是否能回滚 prompt/context 版本
- 是否能解释为什么改动被保留

这意味着本项目的 eval 不应只有 answer score，还要包括 workflow score 和 governance score。

### 证据强度

当前证据强度：中。

理由：

- 来源是工程原则文档，结构清晰。
- 但不是实验论文，没有固定 benchmark。
- 价值在于转化为评估维度，而不是作为方法有效性的证据。

### 深读问题

- 哪些 factor 可以直接变成测试用例？
- 哪些 factor 与 prompt optimization 冲突，例如自动改 prompt 可能破坏 human-in-the-loop？
- 是否有具体失败案例或生产事故支撑这些原则？
- 如何把 context window ownership 量化？

### 可转化实验

最小实验候选：

- 给同一个 coding-agent 任务设计两个 prompt：只追求完成任务 vs 加入 workflow/governance 约束。
- 比较 final answer score、工具调用正确性、越界修改、成本和可回滚性。
- 检查治理约束是否降低任务成功率或反而减少失败。

## 4. `dair-ai/Prompt-Engineering-Guide`

链接：https://github.com/dair-ai/Prompt-Engineering-Guide

### 为什么重点看

它是 prompt engineering 领域的高覆盖资料入口，适合作为 taxonomy 和术语参考。它不是实证方法，但能帮助我们避免把 prompt optimization 的范围定义得过窄。

### 内容概要

仓库覆盖 prompt engineering、context engineering、RAG、AI agents、LLM settings、prompt elements、prompting techniques、论文和课程资源。

对本项目有用的部分主要是：

- prompt elements 和 basic prompting：定义 prompt 结构。
- LLM settings：提醒模型参数是变量，不能和 prompt 改动混在一起。
- RAG 和 context engineering：提醒 prompt 和外部 context 的边界。
- methods / papers：作为追踪 APO、APE、CoT、self-consistency 等方法的索引。

### 对本项目的启发

本项目的“prompt”定义应包含多个层次：

- instruction
- examples
- context
- tool policy
- output schema
- model settings
- evaluator prompt

但实验时必须一次只改一个变量。这个指南适合作为边界定义的背景，不适合作为效果结论。

### 证据强度

当前证据强度：中偏低，作为结论证据；高，作为资料入口。

理由：

- 它是资料库，不是统一实验。
- 可以指向原始论文和教程。
- 引用时应回到原始来源，不直接把指南内容当作实证。

### 深读问题

- 哪些 prompt engineering 方法与 automatic prompt optimization 最相关？
- 哪些章节可以帮助构造初始 prompt 变体？
- 它的 RAG/context engineering 分类是否能与本项目 taxonomy 对齐？

## 5. `affaan-m/ECC` 需核验重点候选

链接：https://github.com/affaan-m/ECC

### 为什么暂列重点

README 覆盖 system prompt slimming、memory persistence、verification loops、grader types、pass@k、security scanning、skills 等关键词，和本项目的工程闭环高度相关。

### 当前谨慎点

它的 README 叙述很强，star/fork 很高，且声称覆盖大量 agents、skills 和 workflows。此类仓库必须先核验：

- GitHub API 元数据是否与 README 声称一致。
- 是否有清晰 license。
- 是否有实际 eval 文件、grader 配置或 benchmark 结果。
- skills/rules 是否可复用，还是主要是目录聚合。
- 是否有失败案例、回滚机制和版本历史。

### 对本项目的潜在价值

如果核验通过，它可以作为“agent harness 层 prompt/context/memory 治理”的工程案例，尤其适合补充：

- system prompt slimming
- token budget optimization
- memory persistence
- verification loop
- security boundary
- skill-based agent behavior control

### 处理建议

先做证据核验，再决定是否进入正式深读。当前只能作为中等证据候选，不能作为强结论来源。
