# Changelog

本文件用于持续记录 `prompt_evolution` 仓库中的重要变更，便于回溯 prompt 优化、自进化实验、分析方法与结论的演进过程。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，但在仓库形成稳定版本节奏前，先按日期维护。

## 记录规则

- 将尚未发布或尚未归档的变更写入 `## Unreleased`。
- 每次阶段性整理、实验完成、论文/笔记重构或版本发布时，将 `Unreleased` 内容归档到新的日期小节。
- 只记录对研究追踪有意义的变更，避免记录纯格式化、拼写修正等噪声。
- 每条记录尽量说明“变更内容”和“影响范围”，必要时补充关联实验、数据集、prompt 策略或评估指标。

## 变更类型

- `Added`: 新增研究材料、实验、脚本、数据、prompt 模板或评估方法。
- `Changed`: 调整研究结构、prompt 优化策略、实验流程、分析口径或文档组织。
- `Fixed`: 修正实验代码、数据处理、结论表述或复现实验中的问题。
- `Deprecated`: 标记后续不再推荐使用的 prompt、方法、实验流程或文档。
- `Removed`: 移除过时材料、无效实验、废弃脚本或不再使用的数据。
- `Security`: 与密钥、隐私、数据脱敏或外部服务访问相关的修复。

## Unreleased

<!-- 将下一批重要变更写在这里。 -->

### Added

- 新增 APE、OPRO、DSPy、MIPROv2、TextGrad 五篇经典锚点论文的全文证据级深读笔记（`docs/paper_notes/paper-ape-2022.md`、`paper-opro-2023.md`、`paper-dspy-2023.md`、`paper-miprov2-2024.md`、`paper-textgrad-2024.md`），闭合 `arxiv_top80_taxonomy.md` 自标的"经典锚点未深读"缺口；每篇含本地 PDF/文本 SHA256、方法机制、主结果数字、消融、失败案例、洞见卡片和最小验证计划，并与已有 ProTeGi/EvoPrompt/PromptBreeder/GEPA 等笔记交叉链接，形成 APE→ProTeGi→OPRO→PromptBreeder/EvoPrompt→DSPy→TextGrad→MIPROv2→GEPA 的基线主干。影响范围：`docs/source_inventory.md` 对应 5 行状态由 candidate/skimmed 升为 noted；`docs/arxiv_top80_taxonomy.md` 缺口条目标记闭合；论文级证据，非本项目复现结论。仍待补更早锚点 AutoPrompt/RLPrompt/GrIPS。
- 新增 `docs/insight_field_standard.md` 字段定义规范：把此前散落在 `research_brief.md`、两个深读模板、`insight_method_catalog` 和 `final_report_outline` 里、只有字段名而无统一口径的 insight / conclusion / helpful method / anti-pattern 四类产出，收敛为单一权威——给出区分口径（含 insight↔conclusion↔method 的判别问句）、各类型必填/可选字段、补齐此前缺失的 `conclusion` 独立 schema、统一字段命名映射并标注 catalog 的待收敛点；影响范围：上述四个文档各加一行指向该规范，证据等级仍沿用 `final_report_outline` 的 A/B/C/D，不改动任何已有结论。

- 新增 `docs/insight_handbook_20260609.md` 读者向洞见手册：面向非本领域读者，按学习顺序（要不要优化 → 怎么诊断失败 → 改什么 → 怎么防过拟合和热度误导）把 12 条核心洞见各写成「反直觉点 + 具体示意例子 + 带出处真实数字 + 可照抄步骤 + 边界」，所有 prompt 例子标注示意、数字标注论文出处，并保留与 insight_method_catalog 的对应关系。
- 新增 `docs/analysis_report_v2_20260609.html` 多渠道洞见报告 v2：按洞见而非渠道组织，把 v1 的标签式结论还原为具体 before/after 例子和带出处数字（如 Coin Flip 49% 低于 zero-shot、VISTA 23.81%→13.50%→87.57%、AutoPDL FEVER 6.5%→74.0%、PrefPO 14.7x 长度）；v1 保留作对照与回滚点。
- 新增 MIT 开源协议文件，明确公开仓库的代码和配套文档可复用边界。
- 新增 `CONTRIBUTING.md`、共创工作流文档和 GitHub issue/PR 模板，把外部研究线索、新颖性判断、深读笔记、实验候选和证据沉淀纳入可管理流程。
- 新增项目构建原则文档，并补充 `AGENTS.md` / `CLAUDE.md`，方便 Codex 和 Claude Code 读取仓库工作约束。
- 新增资料搜集计划，明确论文、行业经验、工程框架和失败案例的收集范围、记录字段、覆盖矩阵和 M0 阶段完成标准。
- 新增来源清单，承接资料搜集阶段的候选论文、行业实践、处理状态和待补缺口，并登记第一批联网核验过的种子来源。
- 新增行业经验笔记目录和模板，用于记录知乎、Twitter/X、工程博客、产品文档和事故复盘等重要单一来源。
- 新增本地原文快照留存规范，使用 `local_sources/raw/` 保存不提交的原文，并在笔记中记录路径和 SHA256。
- 新增 Karpathy-inspired Claude Code guidelines 仓库的行业笔记和来源条目，用于后续 coding-agent 行为规则 eval 设计。
- 新增最终报告结构，明确最终交付需要覆盖前沿状态、证据等级、可执行方案、初步实验和风险治理。
- 新增并重构第一版 HTML 多渠道洞见报告页，按 arXiv 论文、GitHub 源码、行业工具、Twitter/X、知乎和其它平台拆解证据贡献，优先呈现有效 insights、可信 conclusions、可复用 helpful methods、反模式和最小验证方式。
- 新增企业微信机器人通知脚本、配置示例、使用文档和单元测试，后续消息通知统一通过该入口发送。
- 新增本地 Git hook 自动通知，commit 后发送提交消息，push 成功后发送远程更新消息。
- 新增 OpenAI / OpenRouter 最小 LLM API 客户端、dry-run/live smoke test、配置示例、使用文档和单元测试，用于后续实验前检查 provider 配置。
- 新增按渠道广搜通用 posts 候选来源的 `scripts/collect_sources.py`、可选环境变量示例和资料搜集计划说明，支持从 Hacker News、DEV、Stack Exchange、RSS、Brave Web Search、X API 和 Reddit OAuth 收集候选元数据，并输出到本地 ignored artifacts 供人工快筛；GitHub 和 arXiv 暂由独立渠道处理。
- 新增 GitHub 仓库发现脚本、使用文档和单元测试，用于通过 GitHub Search API 批量搜集 prompt optimization / prompt self-evolution 相关候选仓库。
- 新增首批 GitHub 仓库候选快筛，解释 raw candidate 噪声来源，并把 85 个候选分为核心深读、周边参考和暂不处理，同时补充创建时间和最近 push 时间分布。
- 新增 GitHub 仓库三层分析文档、结构化 catalog、重点仓库深读和证据矩阵，并将 8 个严格保留仓库登记到来源清单。
- 新增 GitHub 仓库 clone / audit 脚本、单元测试和源码审计流程文档，已对 core4 仓库固定 commit 并生成审计草稿，用于把 GitHub 渠道 insight 提炼从 README 快筛推进到源码证据层。
- 新增 GitHub 仓库候选 insight 证据卡，从 core4 源码审计中提炼 12 条候选方法/经验，并标注证据等级、适用边界和最小实验候选。
- 新增 GitHub 渠道洞见综合文档，按 insight-first 内容整理原则重写 GitHub 渠道 conclusions、helpful methods、反模式、证据边界和最小验证候选。
- 新增 arXiv 候选论文搜索脚本、说明文档和单元测试，用于按渠道广搜 prompt optimization / prompt evolution 相关论文元数据并生成待粗筛清单。
- 新增 arXiv 聚焦筛选脚本和单元测试，用于把广搜候选重排为 100 篇以内的人工快筛优先清单。
- 新增 arXiv top80 论文三层一读分析，包括简要概述、分类 taxonomy / 横向证据矩阵和重点论文详细介绍，用于指导后续深读笔记与最小实验候选选择。
- 新增 arXiv top80 行动手册，把主要论文问题转化为具体工程例子、解决方案、记录字段和 3 个最小实验候选。
- 新增 arXiv top80 洞见与经验总结，把重点论文从方法索引进一步提炼为可复用的现象、机制、经验规则、边界条件和最小验证方式。
- 新增 arXiv 重点论文下载脚本、manifest 和单元测试，把 15 篇优先深读论文的 PDF 与文本抽取结果保存到本地 ignored artifacts，并记录 SHA256、页数和文本长度。
- 新增 arXiv 重点论文全文深读框架，以及 ProTeGi 和 Modular Prompt Optimization 两篇证据化论文笔记，用于把摘要级判断推进到方法、实验、局限和可复现洞见层面。
- 新增 GEPA、SePO 和 SPEAR 三篇重点论文全文深读笔记，并补充首批深读综合判断，把错误信号质量、候选选择、optimizer artifact 管理和最小复现实验变量沉淀为可执行结论。
- 新增 PromptBreeder、EvoPrompt、Scaling Textual Gradients、Textual Gradients are a Flawed Metaphor、PrefPO 和 TextReg 六篇重点论文全文深读笔记，并补充第二批综合判断，用于校正 textual-gradient 机制解释、扩展演化搜索证据、纳入 prompt hygiene / hacking / OOD overfitting 指标。
- 新增 CriSPO、MemAPO、AutoPDL、MASPO、VISTA、Prompt Codebooks、MAPRO、DistillPrompt、JTPRO 等 16 篇 arXiv 重点论文全文深读笔记，并补充第三批综合判断，把 pre-optimization gate、根因假设、exemplar optimization、tool/schema artifact、multi-agent credit assignment、edit-family hygiene 和 memory 过滤沉淀为后续最小实验约束。
- 新增 `insight_method_catalog_20260609.md`，按最新 insight-first 内容整理原则聚合论文、源码和行业材料，形成 12 条核心洞见候选、6 条当前可采信 conclusions、4 个 helpful methods、反模式清单和首批验证优先级，并同步 README 与实验计划入口。
- 新增知乎、Twitter/X 和其它平台候选 posts 的批次快筛与并发分析包，明确 artifact 路径、证据边界、优先候选、追溯字段和后续处理建议，便于多 session 并行分析。
- 新增 Twitter/X 候选 posts 结构化分析，完成 GEPA/DSPy/MIPRO 社媒线索分层、24 条 source card、X 到一手来源追溯表和排除清单，并将 Pydantic GEPA、Promptim、PromptWizard、DSPyground、Promptomatix 等稳定来源回填到来源清单。
- 新增 Twitter/X 社媒线索洞见卡，按 insight-first 原则把 X/Twitter 线索转成 8 条 insight candidates、3 个 helpful method candidates、反模式和最小验证/演示候选。
- 新增其它平台候选来源结构化分析，完成 high/medium 候选证据分层、source cards、工具与工程实践地图，并将 Hugging Face、Arize、LangChain、Langfuse、Humanloop、Weaviate、OPIK 等稳定来源回填到来源清单和行业实践整理。
- 新增其它平台 insight / method cards，把官方文档、cookbook、工具平台和二手博客线索转写为 optimizer intake、prompt version ledger、context-first diagnosis、source triage 等可复用方法、反模式和最小验证候选。
- 新增知乎候选材料三层分析，基于 99 条搜索候选整理快速概述、主题详细分析、重点论文/框架追溯、深读优先级和排除建议。
- 新增知乎候选材料洞见与方法卡片，将知乎批次按最新 insight-first 原则重写为 insight cards、helpful methods、anti-patterns、重点追溯对象和最小验证候选，并明确知乎材料主要作为中文社区理解与误区线索。
- 新增 `pytest.ini`，将项目测试入口限定到 `tests/`，避免本地忽略目录 `local_sources/raw/` 中的第三方源码快照被 pytest 误收集。

### Changed

- 将其它平台（web_search/工具 + 通用社区广搜）渠道对齐到 `docs/insight_field_standard.md` 并补齐覆盖缺口：在 `docs/source_batches/web_search_platform_insight_cards_20260609.md` 把证据等级从自定义 `L1–L4` 收敛到规范 `A/B/C/D`（多源官方工具实践判为 B，仅搜索摘要线索判为 D，并保留 L→A/B/C/D 换算表）；把 WHM-01..04 从散文改写为字段规范的标准 YAML（补齐 `not_recommended_when`、`evaluation_metrics`、`misuse_or_anti_pattern`、`rollback_plan` 等必填具名字段）；新增「结论总览」「反模式」两节做成清晰渠道入口；新增「广搜渠道覆盖与缺口」节，按 artifact 真实清点 web_search(465)/hackernews(~24)/stackexchange(1)/rss(1)/reddit·dev.to(0)/x_api(未跑)，判定通用社区批次以 GEPA 转贴和 Show HN 产品发布为主、净新增有限，并诚实标注真实失败案例/事故复盘覆盖不足（低于覆盖矩阵要求）。同步在 `docs/source_inventory.md` 登记 3 条净新增候选（AWS Bedrock optimizer、Vertex 锁定 prompt 段落 SO 问答、Ask HN「AI evals 半成品」痛点信号），并在 `README.md` 把 insight cards 标为渠道综合入口、analysis 标为证据层。影响范围：仅其它平台渠道相关文档与来源清单，未改动其它渠道证据与结论。
- 将 Twitter/X 渠道三份产出对齐到 `docs/insight_field_standard.md`（该规范晚于这批产出定稿，故此前未对齐）：字段名 `source_trace`→`main_sources`、证据取值 `B-candidate`→规范 `A/B/C/D`（候选状态在证据边界处单独说明，不污染 `evidence_strength`）、反模式表补必填列 `trigger_condition`；新增 5 条 Conclusion Candidates（按 conclusion schema 填 scope/evidence_strength/counterexample，并标注 main_sources 待补与单源不得直接升格）；补齐 `prompt_as_program_spec`、`social_signal_triage`、`vendor_optimizer_evidence_filter` 三张缺失方法卡，将 `tw-insight-02` 的 trace-aware 方法并入 `method-01`、`tw-insight-07` 的 safety 方法标记为 D 级待补；`twitter_web_analysis` 补「候选去向账目」闭合 120 条候选覆盖、补 next_action 核验进度（均 pending）；`twitter_web_parallel_brief` 补 source card `evidence_level`(strong/medium/weak) 与 insight `evidence_strength`(A/B/C/D) 的映射口径。影响范围：仅 Twitter/X 三份文档，未改动其它渠道证据与结论。
- 为 GitHub 渠道补充覆盖边界与跨源互证：在 `docs/github_repo_channel_synthesis_20260609.md` 新增「渠道覆盖与已知偏差」「repo ↔ paper 对照」两节，把"直接 prompt optimizer 效果证据稀缺"结论降级标注为受限召回（无 token、8 查询的冒烟 discovery）+ core4-only 审计造成的选择偏差，并把 3 个 helpful method 归一到统一目录 `insight_method_catalog_20260609.md` 的 HM-* 命名；同步在 `docs/github_repo_insight_cards_20260608.md` 的 GHI-12 补「覆盖边界」。影响范围：仅文档与证据边界标注，不改动既有 insight / conclusion 内容。
- 重排 GitHub 源码审计流程「下一步」：在 `docs/github_repo_source_audit_workflow_20260608.md` 把 `gepa-ai/gepa`、`microsoft/PromptWizard`、`SalesforceAIResearch/promptomatix`、`Eladlev/AutoPrompt` 等正典 optimizer 仓库列为高优先审计对象（高于 strict8 剩余资料型仓库），标注 strict8 剩余项为有意延后，并补充"配 token 重跑完整 discovery"作为校正低召回的步骤。
- 续做 GitHub 渠道文档收敛（跨文档同口径）：在 `docs/insight_method_catalog_20260609.md` 的 C-06 边界补同口径覆盖偏差说明，使统一目录与渠道综合不再各说各话；在 `docs/github_repo_source_audit_workflow_20260608.md` 新增「第二轮待审仓库（正典 prompt optimizer）」表，把 gepa / PromptWizard / promptomatix / AutoPrompt / dspyground 的 source_id、关联论文、优先级和审计重点固化为可执行 backlog；在 `docs/github_repo_analysis_overview_20260608.md` 的初步判断 1 补「"不多"可能是覆盖不足所致」边界。影响范围：仅文档与证据边界标注，不改动既有 insight / conclusion / 方法内容。
- 新增「读者向内容层」并据此更新入口：诊断 v1 报告过度标签化、缺例子、按渠道组织不利于读者理解，改为按读者学习顺序、以具体例子和真实数字为主的洞见手册 + 报告 v2；同步在 README 看板和文档列表前置手册入口，在实验计划中说明手册「首批最小验证」表与 P0–P2 优先级同口径。各渠道文档与论文笔记保持现状作为证据底座，不改动。
- 调整 README 为公开构建首页，将重要分析、分析经过、阶段结果和下一步计划前置展示。
- 明确本轮流程规则变更提交并推送后，后续代码、文档、实验和配置改动必须先在个人/任务分支完成，再通过 PR/合入请求进入 `main`，用于保护 `main` 的可复现基线和 review/回滚边界；并澄清分支粒度为「每个任务/每位贡献者一条」，单条分支可承载多 session、多次批量改动与多次提交，而非每次改动都新建分支。
- 将当前路线从“准备进入最小可复现实验”前移到“M0 资料搜集与综述冻结”，实验计划暂作为后续候选设计。
- 将 M0 资料搜集和实验计划调整为五天交付版，强调前沿状态跟踪、可执行方案产出和 1-2 个关键判断的最小实验验证。
- 将项目主线调整为 insight-first：优先沉淀有效 insights、可信 conclusions、可复用 helpful methods、反模式和风险边界，实验仅作为验证关键洞见、演示方法和校准边界的手段，并同步更新 README、研究框架、资料搜集计划、最终报告结构、实验计划、项目原则、共创工作流和笔记模板。
- 将各渠道总结文档补充为“具体洞见优先”的写作口径，在 arXiv、GitHub、行业实践、Twitter/X、其它平台和知乎分析中新增普通用户可理解的方法卡片、最小验证方式和证据边界，并同步最终报告结构，同时保留原有论文、源码和工具证据层。
- 企业微信命令行和 Git hook 通知默认附带自然语言版 git 主要修改内容，并把涉及文件作为次级明细展示。

## 2026-06-08

### Added

- 新增 changelog 文档，用于跟踪 prompt 优化/自进化研究仓库的重要变化。
- 新增研究总览、文献地图、行业实践、实验计划和论文笔记模板。
