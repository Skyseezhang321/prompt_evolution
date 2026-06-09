# GitHub 仓库候选 Insight 证据卡：2026-06-08

2026-06-09 补充：新增“普通用户一眼看懂版”，用于把源码审计 insight 转写成具体可试方法；原有 GHI 证据卡保留。

2026-06-09 内容整理补充：面向最终报告的 GitHub 渠道结论、helpful methods、反模式和最小验证候选已整理到 [GitHub 渠道洞见综合](github_repo_channel_synthesis_20260609.md)。本文件继续作为 GHI-01 到 GHI-12 的详细证据卡。

本文件从 core4 源码审计中提炼候选 insight。它不是最终报告结论；每条卡片都保留 source_id、commit、证据路径、证据等级和可转实验方式。

证据等级沿用 [GitHub 仓库源码审计流程](github_repo_source_audit_workflow_20260608.md)：

- L1：固定 commit 后读过 README / docs。
- L2：固定 commit 后定位到源码、配置、测试或示例路径。
- L3：能在本地运行测试、示例或最小复现实验。
- L4：跨仓库、论文或本项目实验互相印证。

当前卡片主要是 L2，不应写成“方法已被证明有效”。它们更适合作为后续实验设计、最终报告假设和经验规则的候选池。

## 快速概述

第一轮源码审计最强的直接启发有 5 条：

1. Prompt 优化不应只生成新 prompt；更稳的闭环是“比较评估 -> 证据压缩 -> 基于评估改写”。
2. evaluator / data / harness 必须和可优化对象隔离，否则 self-evolution 很容易把指标本身改坏。
3. calibration 样本要故意覆盖过拟合、schema 漂移、单次好运、语义不稳定和高风险保守边界。
4. Prompt 和 context 都应作为可测试、可版本化、可回滚的一等工程对象，而不是只存在于框架黑盒或 UI 配置里。
5. Agent harness 的 useful pattern 是 trace、verifier、candidate decision 和 playbook promotion，而不是泛泛声称有 memory / verification loop。

## 普通用户一眼看懂版

GitHub 渠道不擅长直接证明“某个 prompt 技巧一定涨分”，但很擅长给出可落地的工作流。下面这些卡片应作为最终报告和 HTML 页面里的“可操作方法”，详细源码证据仍保留在后续 GHI 卡片中。

| 具体洞见 | 普通用户可以怎么做 | 为什么有用 | 证据边界 |
| --- | --- | --- | --- |
| 不要让模型直接“帮我优化 prompt”，先让它比较两个输出。 | 先给 baseline prompt 和失败输出，让模型判断哪里坏；再把判断摘要交给 rewrite prompt。 | compare 阶段会留下可审计理由，避免优化过程变成黑盒改写。 | 源码结构证据强，效果还需本项目实验验证。 |
| Prompt 里要把任务、输入、输出格式和候选输出分区。 | 用 JSON payload 或清晰 delimiter 包住 `instruction`、`input`、`candidate_output`、`rubric`。 | 减少模型把规则、数据和待评估答案混在一起解释。 | 来自固定 commit 的结构化 compare 实现。 |
| 验证集必须包含“会骗过当前 prompt 的反例”。 | 加入缺字段、格式漂移、同义改写、高风险保守边界、样本触发词等 case。 | 优化器最容易学会局部补丁，反例能暴露过拟合。 | 源码/文档有 calibration 设计，需跑本项目任务确认。 |
| Self-evolution 只能改指定对象，不能改试卷。 | 只允许改 `candidate_prompt.md`；禁止改 `eval_cases`、grader、success criteria。 | 否则系统会把评估规则改松，产生伪提升。 | 来自 autoresearch loop 的工程约束迁移。 |
| 每个 prompt 候选都要有账本。 | 记录 prompt diff、来源、分数、成本、失败样例、接受/拒绝原因和回滚点。 | 没有账本就无法复盘“为什么这个经验值得保留”。 | 工程治理证据强，字段需按本项目实验固化。 |
| Prompt 优化不只改 system prompt。 | 对 agent/RAG 任务，同时记录 context、history compression、tool result format、output schema。 | 很多失败来自模型看到的信息错了，而不是指令写得不够好。 | GitHub 渠道提供边界线索，具体变量优先级需实验。 |

## 卡片总览

| id | 候选 insight | 主要来源 | 证据等级 | 可转实验优先级 |
| --- | --- | --- | --- | --- |
| GHI-01 | 把 prompt 优化拆成 compare / synthesis / rewrite 三段，比直接让模型“改好 prompt”更可审计。 | `repo-linshenkx-prompt-optimizer` | L2 | high |
| GHI-02 | 评估协议应使用结构化 payload 和 JSON contract，减少 Markdown 拼接造成的边界混淆。 | `repo-linshenkx-prompt-optimizer` | L2 | high |
| GHI-03 | calibration 样本要优先攻击过拟合、schema 漂移和稳定性，而不是只验证 happy path。 | `repo-linshenkx-prompt-optimizer` | L2 | high |
| GHI-04 | self-evolving loop 的核心防线是“只允许修改目标对象，不允许修改 evaluator / data”。 | `repo-karpathy-autoresearch` | L2 | high |
| GHI-05 | 每个候选改动都应有 commit、指标、资源、状态和自然语言说明。 | `repo-karpathy-autoresearch` | L2 | high |
| GHI-06 | 接受候选改动时不只看指标，还要记录复杂度收益和失败处理策略。 | `repo-karpathy-autoresearch` | L2 | medium |
| GHI-07 | Prompt 应作为代码资产拥有：可读、可测、可版本化、可替换框架黑盒。 | `repo-humanlayer-12-factor-agents` | L1/L2 | high |
| GHI-08 | Prompt 优化边界应扩展到 context packaging，包括 RAG、history、tool calls、memory 和输出 schema。 | `repo-humanlayer-12-factor-agents` | L1/L2 | high |
| GHI-09 | Memory / context persistence 必须有边界：本地优先、长度上限、profile gating 和 opt-out。 | `repo-affaan-m-ecc` | L2 | medium |
| GHI-10 | Agent 经验沉淀应保存 scenario、trace、verifier result、report 和 candidate playbook。 | `repo-affaan-m-ecc` | L2 | medium |
| GHI-11 | 仓库里“有 tests”只能说明可审计性，不等于方法有效；要把测试入口和效果主张分开。 | core4 综合 | L2 | high |
| GHI-12 | GitHub 渠道的主要价值是工程结构和治理模式，直接证明 prompt optimizer 效果的证据较少。 | core4 综合 | L2 | high |

## 详细卡片

### GHI-01：Compare / Synthesis / Rewrite 三段式比直接改 prompt 更可审计

- source_id：`repo-linshenkx-prompt-optimizer`
- commit：`d7cde6c2fc5c56a579d803d485ad170788a4141e`
- 观察：该仓库不是只有一个“prompt rewrite”入口，而是存在 structured compare pair judge、synthesis 和 rewrite-from-evaluation 的分层实现。比较阶段产生中间判断，综合阶段压缩证据，改写阶段再消费上游结论。
- 证据路径：
  - `local_sources/raw/github_repo_clones/repo-linshenkx-prompt-optimizer/packages/core/src/services/evaluation/structured-compare-prompts.ts`
  - `local_sources/raw/github_repo_clones/repo-linshenkx-prompt-optimizer/packages/core/src/services/template/default-templates/evaluation-structured-compare/`
  - `local_sources/raw/github_repo_clones/repo-linshenkx-prompt-optimizer/packages/core/src/services/evaluation/rewrite-from-evaluation.ts`
- 候选方法：后续实验不要只做“输入 bad prompt -> 输出 better prompt”，而应记录 evaluator 输出、证据摘要、rewrite reason 和 prompt diff。
- 可转实验：同一批失败样本上，对比“直接 rewrite”和“compare -> rewrite”两种流程，看 held-out 成绩、schema drift、拒答边界和人工审查成本。
- 证据等级：L2。源码结构存在；尚未在本项目中复现效果。

### GHI-02：结构化 payload 和 JSON contract 是 prompt 优化闭环的边界控制工具

- source_id：`repo-linshenkx-prompt-optimizer`
- commit：`d7cde6c2fc5c56a579d803d485ad170788a4141e`
- 观察：该仓库的 compare / rewrite 文档显示协议层从 Markdown 拼接迁移到“规则说明 + JSON payload”；源码中也有 compare JSON contract、structured mode 和 compare metadata。
- 证据路径：
  - `local_sources/raw/github_repo_clones/repo-linshenkx-prompt-optimizer/docs/workspace/compare-evaluation-analysis/README.md:28`
  - `local_sources/raw/github_repo_clones/repo-linshenkx-prompt-optimizer/packages/core/src/services/evaluation/types.ts`
  - `local_sources/raw/github_repo_clones/repo-linshenkx-prompt-optimizer/packages/core/src/services/evaluation/service.ts`
- 候选方法：prompt optimizer 的 evaluator prompt 应明确区分 instruction、payload、schema contract、reference output 和 candidate output，避免模型把上下文混成一段可自由解释文本。
- 可转实验：构造同一比较任务的 Markdown 版和 JSON payload 版，测字段改名、wrapper 漂移、JSON-only 边界和 judge 解析失败率。
- 证据等级：L2。协议迁移和结构字段存在；效果仍需本项目验证。

### GHI-03：Calibration 样本要主动测试过拟合、schema 漂移和语义稳定性

- source_id：`repo-linshenkx-prompt-optimizer`
- commit：`d7cde6c2fc5c56a579d803d485ad170788a4141e`
- 观察：structured compare calibration 不只测试功能能跑，而是覆盖高风险过拟合、schema / contract 漂移、同义 flat、replica 语义不稳定、真实边界控制等场景。
- 证据路径：
  - `local_sources/raw/github_repo_clones/repo-linshenkx-prompt-optimizer/docs/workspace/compare-evaluation-analysis/structured-compare-calibration/README.md`
  - `local_sources/raw/github_repo_clones/repo-linshenkx-prompt-optimizer/docs/workspace/compare-evaluation-analysis/real-api-samples/`
- 候选方法：prompt optimizer 的 validation set 应至少包含“能骗过当前样本但伤害通用性”的负例，而不是只看目标样例提升。
- 可转实验：为第一版本项目 benchmark 加入 4 类对抗 calibration case：schema drift、latent trigger overfit、single-run luck、high-risk conservative boundary。
- 证据等级：L2。calibration 设计存在；其泛化效果需要本项目复现。

### GHI-04：Self-evolving loop 必须冻结 evaluator / data / harness

- source_id：`repo-karpathy-autoresearch`
- commit：`228791fb499afffb54b46200aca536f79142f117`
- 观察：`program.md` 明确约束 agent 只能修改 `train.py`，不能修改 `prepare.py`、依赖或 evaluation harness；`prepare.py` 提供固定 metric。
- 证据路径：
  - `local_sources/raw/github_repo_clones/repo-karpathy-autoresearch/program.md:13`
  - `local_sources/raw/github_repo_clones/repo-karpathy-autoresearch/program.md:26`
  - `local_sources/raw/github_repo_clones/repo-karpathy-autoresearch/program.md:31`
  - `local_sources/raw/github_repo_clones/repo-karpathy-autoresearch/prepare.py`
- 候选方法：prompt self-evolution 实验中，可变对象只能是 prompt/context/tool policy 之一；eval data、grader、success criteria 和 logging schema 必须冻结。
- 可转实验：实现一个 prompt-only optimizer，让模型只编辑 `candidate_prompt.md`，不能修改 `eval_cases.jsonl`、grader 或 runner；对比允许改 evaluator 的设置是否出现 reward hacking。
- 证据等级：L2。结构闭环明确；迁移到 prompt 任务仍是本项目实验问题。

### GHI-05：候选改动需要 commit + metric + resource + status + description 的 ledger

- source_id：`repo-karpathy-autoresearch`
- commit：`228791fb499afffb54b46200aca536f79142f117`
- 观察：`program.md` 要求每次实验写入 `results.tsv`，字段覆盖 commit、metric、memory、status 和自然语言说明；失败和 crash 也有记录口径。
- 证据路径：
  - `local_sources/raw/github_repo_clones/repo-karpathy-autoresearch/program.md:64`
  - `local_sources/raw/github_repo_clones/repo-karpathy-autoresearch/program.md:71`
  - `local_sources/raw/github_repo_clones/repo-karpathy-autoresearch/program.md:77`
- 候选方法：prompt optimizer 的每个候选版本都应记录 prompt diff、候选来源、eval score、成本、延迟、status、失败样例和回滚点。
- 可转实验：为本项目第一版 optimizer runner 增加 `prompt_runs.tsv` 或 JSONL ledger，先记录手工 prompt、直接 rewrite、compare rewrite 三类候选。
- 证据等级：L2。ledger 规范存在；prompt 版本字段需本项目定义。

### GHI-06：保留候选改动时应显式考虑复杂度和失败处理

- source_id：`repo-karpathy-autoresearch`
- commit：`228791fb499afffb54b46200aca536f79142f117`
- 观察：`program.md` 不只要求指标变好，还包含 simplicity criterion、超时处理、crash 处理和 discard/revert 规则。
- 证据路径：
  - `local_sources/raw/github_repo_clones/repo-karpathy-autoresearch/program.md:37`
  - `local_sources/raw/github_repo_clones/repo-karpathy-autoresearch/program.md:96`
  - `local_sources/raw/github_repo_clones/repo-karpathy-autoresearch/program.md:103`
  - `local_sources/raw/github_repo_clones/repo-karpathy-autoresearch/program.md:108`
- 候选方法：prompt 优化不能只看分数；如果新 prompt 更长、更脆、更依赖特殊样例或更难审核，就应把复杂度成本记入 decision。
- 可转实验：在 runner 中增加 `prompt_length_delta`、`rule_count_delta`、`manual_review_risk` 和 `rollback_reason` 字段。
- 证据等级：L2。规则存在；复杂度指标如何量化仍需本项目定义。

### GHI-07：Prompt 应作为一等代码资产被拥有，而不是外包给框架黑盒

- source_id：`repo-humanlayer-12-factor-agents`
- commit：`d20c728368bf9c189d6d7aab704744decb6ec0cc`
- 观察：factor 02 明确主张把 prompt 当作 first-class code，以支持控制、测试/eval、迭代和透明度；仓库也包含 create-agent template 和 BAML 示例。
- 证据路径：
  - `local_sources/raw/github_repo_clones/repo-humanlayer-12-factor-agents/content/factor-02-own-your-prompts.md:33`
  - `local_sources/raw/github_repo_clones/repo-humanlayer-12-factor-agents/content/factor-02-own-your-prompts.md:77`
  - `local_sources/raw/github_repo_clones/repo-humanlayer-12-factor-agents/packages/create-12-factor-agent/template/`
- 候选方法：本项目最终方案中，prompt 不应只存 UI 或平台 prompt hub；至少核心 system prompt、evaluation prompt 和 rewrite prompt 要进入版本库或可导出的 artifact。
- 可转实验：比较“prompt 文本不可见/不可 diff”和“prompt 文件 + prompt diff ledger”两种流程在审查成本和回滚速度上的差异。
- 证据等级：L1/L2。主要是工程原则与模板证据，不是效果证明。

### GHI-08：Prompt 优化边界应扩展到 context packaging

- source_id：`repo-humanlayer-12-factor-agents`
- commit：`d20c728368bf9c189d6d7aab704744decb6ec0cc`
- 观察：factor 03 把 context 拆成 prompt/instructions、RAG 文档、past state/tool calls/history、memory 和 structured output instructions，并强调可以自定义 context format。
- 证据路径：
  - `local_sources/raw/github_repo_clones/repo-humanlayer-12-factor-agents/content/factor-03-own-your-context-window.md:14`
  - `local_sources/raw/github_repo_clones/repo-humanlayer-12-factor-agents/content/factor-03-own-your-context-window.md:71`
  - `local_sources/raw/github_repo_clones/repo-humanlayer-12-factor-agents/content/factor-03-own-your-context-window.md:227`
- 候选方法：后续不要把 prompt optimization 狭义定义成“改 system prompt 文案”；对 agent 任务，context selection、history compression、tool result formatting 和 output schema 也应是优化对象。
- 可转实验：同一个 agent task 上，只改 system prompt vs 只改 context packing vs 二者同时改，比较成功率、token、工具误用和可审查性。
- 证据等级：L1/L2。原则明确；需要实验验证哪类 context 改动最有效。

### GHI-09：Memory / context persistence 要有边界和开关

- source_id：`repo-affaan-m-ecc`
- commit：`90dfd9505dc860714cf3cc8216ad7bbb96d93365`
- 观察：ECC 的 memory-persistence 文档把 session start、pre-compact、session end、tool observation 和 activity tracking 作为 lifecycle hooks，并记录本地优先、长度上限、opt-out 和 profile gating。
- 证据路径：
  - `local_sources/raw/github_repo_clones/repo-affaan-m-ecc/hooks/memory-persistence/README.md`
  - `local_sources/raw/github_repo_clones/repo-affaan-m-ecc/scripts/hooks/session-start.js`
  - `local_sources/raw/github_repo_clones/repo-affaan-m-ecc/scripts/hooks/pre-compact.js`
  - `local_sources/raw/github_repo_clones/repo-affaan-m-ecc/tests/hooks/observer-memory.test.js`
- 候选方法：prompt self-evolution 的 memory 不应无界追加；每条 memory 需要来源、作用域、过期策略和禁用开关。
- 可转实验：比较 no-memory、bounded-summary-memory、raw-history-memory 三种设置在 prompt 漂移、token 成本和错误继承上的差异。
- 证据等级：L2。hook 和测试路径存在；实际效果需要运行核验。

### GHI-10：Agent 经验沉淀应保存 scenario、trace、verifier result、report 和 playbook

- source_id：`repo-affaan-m-ecc`
- commit：`90dfd9505dc860714cf3cc8216ad7bbb96d93365`
- 观察：`examples/evaluator-rag-prototype/` 保存了 scenario、trace、verifier-result、report 和 candidate-playbook；verifier 结果区分 accepted / rejected candidate，并只 promotion 一个候选。
- 证据路径：
  - `local_sources/raw/github_repo_clones/repo-affaan-m-ecc/examples/evaluator-rag-prototype/scenario.json`
  - `local_sources/raw/github_repo_clones/repo-affaan-m-ecc/examples/evaluator-rag-prototype/trace.json`
  - `local_sources/raw/github_repo_clones/repo-affaan-m-ecc/examples/evaluator-rag-prototype/verifier-result.json`
  - `local_sources/raw/github_repo_clones/repo-affaan-m-ecc/examples/evaluator-rag-prototype/report.json`
  - `local_sources/raw/github_repo_clones/repo-affaan-m-ecc/examples/evaluator-rag-prototype/candidate-playbook.md`
- 候选方法：prompt 优化后的经验不要只沉淀成“新 prompt”；应保留为什么接受、为什么拒绝、来源证据、验证命令和可复用 playbook。
- 可转实验：为本项目每个 optimizer run 生成 `scenario.json`、`trace.jsonl`、`verifier_result.json` 和 `candidate_prompt.md`。
- 证据等级：L2。示例 artifact 存在；不是通用有效性证明。

### GHI-11：“有 tests”不等于“方法有效”，但它能提高可审计性

- source_id：core4 综合，重点是 `repo-affaan-m-ecc` 与 `repo-linshenkx-prompt-optimizer`
- commits：
  - `repo-affaan-m-ecc`：`90dfd9505dc860714cf3cc8216ad7bbb96d93365`
  - `repo-linshenkx-prompt-optimizer`：`d7cde6c2fc5c56a579d803d485ad170788a4141e`
- 观察：两个仓库都有较大测试/示例面，但这些路径只能说明有可审计入口，不能说明 prompt optimizer 或 agent harness 的方法主张已被验证。
- 证据路径：
  - `local_sources/raw/github_repo_clones/repo-affaan-m-ecc/package.json:348`
  - `local_sources/raw/github_repo_clones/repo-affaan-m-ecc/tests/`
  - `local_sources/raw/github_repo_clones/repo-linshenkx-prompt-optimizer/tests/e2e/`
  - `docs/github_repo_audit_notes/repo-affaan-m-ecc.md`
  - `docs/github_repo_audit_notes/repo-linshenkx-prompt-optimizer.md`
- 候选方法：分析 GitHub 仓库时，应把“测试覆盖工程完整性”和“实验结果证明方法有效”拆开记录。
- 可转实验：对 core4 中可运行的测试入口做 smoke run，标注哪些是 unit/e2e，哪些能真正评估 optimizer behavior。
- 证据等级：L2。测试路径存在；是否通过、是否覆盖关键行为仍需运行。

### GHI-12：GitHub 渠道更适合抽取工程结构，不适合直接得出效果结论

- source_id：core4 综合
- 观察：core4 中只有 `linshenkx/prompt-optimizer` 直接属于 prompt optimizer；`karpathy/autoresearch` 是自进化实验 loop 的结构参考；`humanlayer/12-factor-agents` 是 agent/context 治理原则；`affaan-m/ECC` 是 harness 和 memory / verifier 线索。这些都能贡献方法设计，但都还不能单独证明“prompt 自进化有效”。
- 证据路径：
  - [GitHub 仓库源码审计流程](github_repo_source_audit_workflow_20260608.md)
  - [repo-linshenkx-prompt-optimizer audit note](github_repo_audit_notes/repo-linshenkx-prompt-optimizer.md)
  - [repo-karpathy-autoresearch audit note](github_repo_audit_notes/repo-karpathy-autoresearch.md)
  - [repo-humanlayer-12-factor-agents audit note](github_repo_audit_notes/repo-humanlayer-12-factor-agents.md)
  - [repo-affaan-m-ecc audit note](github_repo_audit_notes/repo-affaan-m-ecc.md)
- 候选方法：最终报告引用 GitHub 渠道时，应优先写“可复用工程方法”和“实验设计约束”，把效果类结论留给论文、官方 benchmark 或本项目实验。
- 可转实验：将 GHI-01、GHI-04、GHI-05、GHI-08 合并成第一版最小 prompt self-evolution harness。
- 证据等级：L2。来自固定源码观察的综合判断；升级到 L4 需要和论文深读、本项目实验互证。

## 第一批实验候选

优先级最高的最小实验可以按下面顺序冻结：

1. **Frozen Evaluator Prompt Loop**：只允许优化 `candidate_prompt.md`，冻结 eval cases、grader、runner 和 ledger schema。验证 GHI-04 / GHI-05。
2. **Direct Rewrite vs Compare Rewrite**：同样失败样本下比较直接改写与 compare/synthesis/rewrite 三段式。验证 GHI-01 / GHI-03。
3. **Markdown vs JSON Payload Judge**：同样 compare prompt 下比较 Markdown 拼接与结构化 payload。验证 GHI-02。
4. **Prompt-only vs Context-packaging**：同一 agent task 上分别改 system prompt 和 context format。验证 GHI-08。

第一批不建议直接复刻 ECC 或完整 UI 工具。更可控的路径是先借鉴 ledger、trace、verifier 和 bounded memory 的结构字段。
