# Prompt Evolution Research

本仓库用于调研、总结和必要验证「prompt 优化提升 / prompt 自进化」相关研究。核心产出是有效 insights、可信 conclusion 和可复用 helpful methods；实验主要用于验证关键洞见、演示方法和校准边界。

更新时间：2026-06-08

## 公开构建看板

这是一个公开实时构建中的研究项目。README 优先放置重要分析、研究过程和阶段结果，方便旁观者快速理解当前进展，而不需要先翻完整文档树。

| 项目 | 当前状态 |
| --- | --- |
| 当前阶段 | 五天交付版 insight-first 研究闭环：快速跟进前沿状态，沉淀有效洞见、核心结论和可复用方法。 |
| 当前主线 | 建立从 source -> note -> insight card -> conclusion -> helpful method -> validation/demo -> final report 的可追溯链路。 |
| 第一批实验方向 | 不追求完整 benchmark；只选择 1-2 个能验证洞见或演示方法的最小任务。 |
| 主要风险 | eval 过拟合、LLM-as-judge 偏差、prompt 漂移、成本失控、自动优化破坏安全边界。 |
| 想快速理解结论 | 直接打开 [跨渠道综合论述报告 v4](docs/analysis_report_v4_20260611.html)：四层结构——方法地图（七法演进 / 同框对比 / 选型导引）、工作流洞见（14 条）、工程落地（五件套 / 工具分层 / 发布门）、误区与边界（12 条误读澄清 + frontier 缺口）。旧版 [v3](docs/analysis_report_v3_20260610.html) 已冻结保留作对照；只想读 12 洞见可看 [读者向洞见手册](docs/insight_handbook_20260609.md)。 |
| 想直接拿优化建议 | [Prompt 优化建议助手](advisor/advisor.html)：聊天式描述你的场景，系统按证据分级知识库给出分层、可追溯的建议。两种形态——直接开 `advisor.html`（确定性、免费）；或起 FastAPI 后端（`uvicorn server:app --app-dir advisor`）走**扎根 LLM 问答**（OpenRouter/deepseek，回答强制引用洞见编号与证据等级）。源与构建见 [advisor/](advisor/README.md)。 |
| 阅读路径 | 先读本 README；想快速理解结论读 [读者向洞见手册](docs/insight_handbook_20260609.md)；想参与共创先读 [参与贡献指南](CONTRIBUTING.md) 和 [共创工作流](docs/contribution_workflow.md)；继续研究细节再读 [资料搜集计划](docs/source_collection_plan.md)、[来源清单](docs/source_inventory.md)、[研究框架](docs/research_brief.md)、[实验计划](docs/experiment_plan.md)、[最终报告结构](docs/final_report_outline.md) 和 [变更记录](CHANGELOG.md)。 |

## 五天交付目标

本项目当前目标不是穷尽复现所有 prompt optimization 方法，也不是把实验做成主线，而是在有限时间内完成一个可信、可执行的研究交付：

- 跟上当前前沿：明确 automatic prompt optimization、reflective prompt evolution、self-evolving prompts、context engineering 和 eval-driven prompt iteration 的主要进展。
- 沉淀有效洞见：把论文、源码和行业材料转化为具体、反直觉、可迁移、可验证的 insights，而不是只做摘要。
- 形成经验总结：把行业实践和论文结论整理成可复用原则、方法 playbook、反模式和风险清单。
- 产出 helpful methods：给出 2-3 个有实际复用价值的方法或建议，说明适用场景、前提、成本、风险和误用边界。
- 做最小验证：选择 1-2 个关键洞见或方法做最小实验，提供观察证据、失败案例和后续验证路径。
- 形成最终报告：以 insights、conclusions、helpful methods 为主线，区分“证据支持的结论”“初步验证观察”和“仍待验证的推测”。

## 重要分析和判断

截至 2026-06-08，以下是当前资料搜集和初步核验后最值得跟进的前沿判断：

1. Prompt 优化的主要瓶颈正在从「prompt 文案」转向「eval 质量、失败轨迹、上下文组织和版本治理」。
2. 自然语言反思可能比纯标量 reward 更适合 prompt 级优化，因为 prompt 本身是可读、可编辑、可审计的文本对象。
3. 真正有生产价值的自进化系统必须包含约束搜索、候选隔离、离线评测、人工审核、版本回滚和持续监控。
4. 对 agent 系统而言，优化目标不应只包含最终答案准确率，还要包含工具调用正确性、拒答边界、成本、延迟、稳定性和跨模型迁移。

这些判断还不是最终结论。最终报告必须为每条判断标注证据等级，并通过资料来源、初步实验、失败案例或反例说明支撑强度。

## 当前分析经过

本项目目前按以下路线推进：

1. 先界定研究问题：prompt 不是孤立文本，而是 instruction、examples、context、tool policy、model parameters 和 evaluator 的组合。
2. 再做资料搜集：广泛收集学术论文、工程框架、产品文档、行业案例和反面经验，并记录筛选标准。
3. 然后提炼洞见：从 APE、ProTeGi、OPRO、PromptBreeder、DSPy/MIPROv2 到 GEPA、MemAPO、SePO、MASPO 等方向，抽取能迁移的现象、机制、方法和边界。
4. 再形成方法建议：把论文方法和行业实践转化为 helpful methods、操作 playbook、反模式、评估口径和治理建议。
5. 最后做最小验证：只验证对洞见可信度或方法可用性影响最大的 1-2 个判断，并记录 prompt diff、模型、参数、数据集、评分器、成本、失败模式和回滚点。

## 阶段结果

已经完成：

- 建立研究框架、文献地图、行业实践、实验计划、论文笔记模板和行业经验笔记模板。
- 建立资料搜集计划，用于指导论文、产品文档、工程框架和行业案例的系统化收集。
- 建立最终报告结构，用于约束最终交付必须包含前沿状态、经验总结、方案建议和初步验证。
- 建立项目构建原则，并写入 `AGENTS.md` / `CLAUDE.md`，方便 Codex 和 Claude Code 读取。
- 建立企业微信通知入口，用于后续脚本、实验任务、定时任务和 CI 的统一消息通知。
- 建立 OpenAI / OpenRouter 最小 LLM API 客户端和 dry-run smoke test，用于后续实验前的 provider 配置检查。
- 建立第一批实验候选方向，但尚未冻结具体任务。
- 建立 GitHub 重点仓库 clone / audit 流程，已对 4 个核心仓库固定 commit 并生成源码审计草稿，避免仅凭 README 或热度提炼结论。

尚未完成：

- 尚未完成核心来源的深读笔记、前沿状态图和证据等级标注。
- 尚未冻结第一版稳定 insight / conclusion / helpful method 清单。
- 尚未把资料综述转化为 2-3 个高优先级可复用方法或建议。
- 尚未实现 benchmark harness。
- 尚未冻结第一版数据集和评分器。
- 尚未跑出 manual、few-shot、APE-style、ProTeGi-style 的可比实验结果。
- 尚未形成能支持“自进化有效”的实证结论。

## 下一步

1. 按 [资料搜集计划](docs/source_collection_plan.md) 完成来源快筛、核心来源深读和证据等级标注。
2. 扩充 [文献地图](docs/literature_map.md) 与 [行业实践整理](docs/industry_practices.md)，优先提炼可复用洞见、反模式和方法 playbook。
3. 汇总 2-3 个 helpful methods 或建议，说明适用场景、实现步骤、成本、风险、误用边界和回滚点。
4. 为最重要的 1-2 个洞见或方法设计最小验证，避免为了完整性实现过大的 benchmark harness。
5. 按 [最终报告结构](docs/final_report_outline.md) 输出完整说明和报告。

## 公共共创机制

本项目后续会按 public 项目方式接受外部线索和 PR。共创机制的基本思路是：低门槛接收“我读到一个有价值的点”，高标准沉淀“项目可以采信的研究结论”。

推荐流转：

```text
Research Signal issue -> 项目内新颖性判断 -> 结构化笔记 -> insight/method card -> 必要验证 -> 有证据的结论
```

贡献者可以只提交线索、洞见或有用方法，不必承担完整深读或实验；维护者会把线索标记为 `duplicate`、`extension`、`contradiction`、`new-hypothesis`、`actionable-method` 或 `experiment-candidate`。只有经过来源记录、证据整理和必要验证后，观点才会进入 README、最终报告或项目原则。

参与方式见 [参与贡献指南](CONTRIBUTING.md)，完整管理流程见 [共创工作流](docs/contribution_workflow.md)。

## 研究目标

核心问题不是「怎么写一个更漂亮的 prompt」，而是：

- 如何把 prompt 设计变成可度量、可复现、可回滚的优化问题。
- 如何利用 LLM 的自然语言反思能力，从失败样本、执行轨迹、人工反馈和自动评测中产生更好的指令。
- 如何让 prompt / system prompt / examples / context / tool policy 随经验积累而持续改进，同时控制漂移、过拟合和安全风险。

## 基本原则

本项目采用 [项目构建原则](docs/project_principles.md) 作为后续文档、实验和代码工作的共同约束。简要版本如下：

1. 先定义问题，不先写 prompt。
2. 洞见和方法优先，实验服务验证。
3. 一次只改一个变量。
4. 每个结论必须有证据。
5. 目标驱动执行。
6. 变更可追踪。
7. 精准修改，不做无关重构。

## 当前文档

- [项目构建原则](docs/project_principles.md)：prompt 优化/自进化研究的基本工作原则和代理执行约束。
- [参与贡献指南](CONTRIBUTING.md)：外部贡献者提交线索、笔记、实验和 PR 的入口说明。
- [共创工作流](docs/contribution_workflow.md)：线索查重、新颖性判断、深读、实验和结论沉淀的管理流程。
- [资料搜集计划](docs/source_collection_plan.md)：论文、行业经验、工程框架和反面案例的收集范围、字段和阶段门槛。
- [来源清单](docs/source_inventory.md)：资料搜集阶段的候选论文、行业实践、工具文档和待补缺口。
- [GitHub 仓库发现脚本](docs/github_repo_discovery.md)：通过 GitHub Search API 批量发现 prompt optimization 相关候选仓库。
- [GitHub 仓库候选快筛](docs/github_repo_triage_20260608.md)：对首批 85 个 GitHub raw candidates 做核心/周边/剔除分层。
- [GitHub 仓库分析概述](docs/github_repo_analysis_overview_20260608.md)：对筛选后 GitHub 仓库做三层分析的第一层概览。
- [GitHub 仓库内容 catalog](docs/github_repo_catalog_20260608.md)：用统一字段介绍筛选后仓库的定位、证据和处理建议。
- [GitHub 重点仓库深读](docs/github_repo_deep_dives_20260608.md)：分析 prompt optimizer、自进化 agent 和 agent/context 工程重点仓库。
- [GitHub 仓库证据矩阵](docs/github_repo_evidence_matrix_20260608.md)：横向比较 prompt 优化、自动迭代、eval、回滚和可复现性证据。
- [GitHub 仓库源码审计流程](docs/github_repo_source_audit_workflow_20260608.md)：固定重点仓库 commit，生成 clone/audit manifest 和人工审计笔记，作为 GitHub insight 提炼的证据入口。
- [GitHub 仓库候选 insight 证据卡](docs/github_repo_insight_cards_20260608.md)：从 core4 源码审计提炼 12 条候选方法/经验，并标注证据等级、边界和可转实验。
- [GitHub 渠道洞见综合](docs/github_repo_channel_synthesis_20260609.md)：按最新 insight-first 原则整理 GitHub 渠道的 conclusions、helpful methods、反模式和最小验证候选。
- [研究框架](docs/research_brief.md)：问题定义、研究假设、技术路线和风险。
- [最终报告结构](docs/final_report_outline.md)：最终说明和报告的内容边界、证据等级和验收标准。
- [读者向洞见手册](docs/insight_handbook_20260609.md)：面向非本领域读者，按学习顺序把 12 条核心洞见写成「反直觉点 + 具体例子 + 真实数字 + 可照抄步骤 + 边界」，所有 prompt 例子均标注示意、所有数字标注出处。
- [跨渠道综合论述报告 v4](docs/analysis_report_v4_20260611.html)：当前主报告。把 v3 固化的「12 洞见单层结构」升级为四层知识体系——① 方法地图（七法演进谱系、六法同框对比、选型导引、7 方法簇）；③ 工作流洞见 14 条（01–12 编号与统一目录一致，新增 13 零成本结构变换、14 optimizer/judge 版本化）；④ 工程落地（五件套、工具成熟度分层、研究→工具映射、发布门与账本）；⑥⑨ 误区澄清 12 条与「范围边界 + frontier 缺口」声明，另附 repo↔paper 对照表。旧版 [报告 v3](docs/analysis_report_v3_20260610.html)（已冻结）、[报告 v2](docs/analysis_report_v2_20260609.html)（按洞见组织、arXiv 为主）与 [报告 v1](docs/analysis_report_v1_20260608.html)（按渠道组织）保留作对照与回滚；脑图可编辑源见 [Mermaid 脑图](docs/prompt_evolution_mindmap_20260610.md)（v3 结构，待按 v4 更新）。
- [Insight / Conclusion / Helpful Method 候选清单](docs/insight_method_catalog_20260609.md)：按最新 insight-first 原则，把论文、源码和行业材料聚合成可复用洞见、核心结论、helpful methods、反模式和验证候选（结构化中间层，供研究者和最终报告使用）。
- [文献地图](docs/literature_map.md)：自动 prompt 优化、自进化、上下文工程相关论文脉络。
- [APO 七法主线详解](docs/apo_seven_methods_primer_20260611.md)：把仓库反复引用的基线主干 APE→ProTeGi→OPRO→DSPy→TextGrad→MIPROv2→GEPA 串成整体叙事，逐方法给出定位、机制、代表性结果和局限，数字与各深读笔记同口径。
- [行业实践](docs/industry_practices.md)：OpenAI、Anthropic、Google、DSPy、LangSmith、Promptfoo 等跨来源实践整理。
- [其它平台渠道洞见综合](docs/source_batches/web_search_platform_insight_cards_20260609.md)：其它平台（web_search/工具 + 通用社区广搜）渠道入口，按 A/B/C/D 等级给出结论总览、insight/helpful method 卡片、反模式、广搜渠道覆盖与缺口和验证候选。
- [其它平台候选来源结构化分析](docs/source_batches/web_search_platform_analysis_20260608.md)：证据层，对 Hugging Face、Arize、Promptfoo、Langfuse、Humanloop、LangChain、OPIK、Weaviate 等来源做快筛分层和证据索引。
- [行业经验笔记模板](docs/industry_notes/template.md)：后续深读知乎、Twitter/X、工程博客、事故复盘等行业来源时统一记录。
- [实验计划](docs/experiment_plan.md)：用于验证关键洞见和演示 helpful methods 的最小实验设计、基线、指标、日志字段和里程碑。
- [论文笔记模板](docs/paper_notes/template.md)：后续阅读论文时统一记录。
- [企业微信通知](docs/wecom_notification.md)：统一的企业微信机器人通知入口、配置和调用方式。
- [LLM API 客户端与 smoke test](docs/llm_clients.md)：OpenAI / OpenRouter 的最小调用入口、配置和连通性检查。
- [变更记录](CHANGELOG.md)：记录研究材料、实验和文档结构的重要变化。

## 后续工作流

1. 外部贡献优先通过 `Research Signal` issue 提交线索；维护者按 [共创工作流](docs/contribution_workflow.md) 做项目内新颖性判断。
2. 新来源先按 [资料搜集计划](docs/source_collection_plan.md) 登记分类，再决定是否进入深读。
3. 新论文放到 `docs/paper_notes/`，按模板写 1-2 页摘要。
4. 新行业经验放到 `docs/industry_notes/`，按模板记录来源背景、核心主张、可复用洞见、证据等级和可转化方法。
5. 新实验必须说明要验证哪个 insight、conclusion 或 helpful method，并先更新 [实验计划](docs/experiment_plan.md)，再写代码。
6. 每个 prompt 变体都要记录模型、参数、数据集、评分器、成本和失败案例。
7. 任何「自动改 prompt」的实验都必须保留原 prompt、候选 prompt、优化原因、评测结果和回滚点。

## 消息通知

所有脚本、实验任务、定时任务和 CI 流程的消息通知统一调用 `scripts/wecom_notify.py`，由它发送到企业微信机器人。真实 webhook 放在本地 `.env` 的 `WECOM_BOT_WEBHOOK` 中，不提交到仓库。

命令行和 Git hook 通知默认会附带 git 的“主要修改内容”，先按变更范围生成自然语言摘要，再列出涉及文件；工作区干净时展示最近一次提交摘要。

```bash
python scripts/wecom_notify.py "### Prompt Evolution 通知通道测试"
```

## LLM API smoke test

`.env.example` 中包含 OpenAI 与 OpenRouter 的本地配置模板。默认 smoke test 只输出 dry-run payload，不发送真实请求：

```bash
python scripts/llm_smoke_test.py
```

填好本地 `.env` 后，可用 `--live` 检查 provider 连通性。该检查只验证配置和基础响应解析，不作为 prompt 实验结论。

## License

本项目采用 MIT License。详见 [LICENSE](LICENSE)。
