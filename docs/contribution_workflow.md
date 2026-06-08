# 共创工作流

更新时间：2026-06-08

本文定义 `prompt_evolution` 作为 public 项目的共创机制。目标是让任何人都能低成本贡献阅读发现，同时让维护者可以管理线索、判断新颖性、组织深读、推动最小实验，并防止没有证据的观点进入项目结论。

## 设计摘要

共创机制采用四层闭环：

```text
research signal -> novelty check -> structured note -> experiment candidate -> evidence-backed conclusion
```

其中：

- `research signal` 是低门槛入口，允许贡献者“提一嘴”。
- `novelty check` 判断这个点对本项目是重复、补充、冲突、新假设，还是可执行实验。
- `structured note` 把单一来源整理成可复查的论文笔记或行业经验笔记。
- `experiment candidate` 把观点转成目标、假设、样本、模型、评分器和成功标准。
- `evidence-backed conclusion` 只接受有来源、实验、失败案例或反例支撑的结论。

## 目标和非目标

目标：

- 降低参与门槛，让读到有价值资料的人可以快速提交线索。
- 把每条线索和来源、判断、笔记、实验、结论关联起来。
- 保持 prompt 优化研究的可度量、可复现和可回滚。
- 让维护者可以用 GitHub issue、label、PR 和文档状态管理协作。

非目标：

- 不把 issue 区变成无证据观点合集。
- 不要求每个贡献者都完成深读和实验。
- 不因为来源看起来权威就直接写入项目结论。
- 不在没有实验计划的情况下实现大型 benchmark 或优化框架。

## 贡献层级

| 层级 | 贡献者要做什么 | 产物 | 管理入口 |
| --- | --- | --- | --- |
| 线索 | 提交来源和有价值的点 | `Research Signal` issue | label: `signal`, `needs-novelty-check` |
| 新颖性判断 | 与现有文档、来源清单和实验计划比对 | issue 评论或状态标签 | label: `duplicate`, `extension`, `contradiction`, `new-hypothesis`, `experiment-candidate` |
| 深读 | 使用模板总结单一来源 | `docs/paper_notes/` 或 `docs/industry_notes/` | PR |
| 综合 | 跨来源整理方法、风险和开放问题 | `docs/literature_map.md`、`docs/industry_practices.md` | PR |
| 实验 | 把假设转成最小实验并记录结果 | `docs/experiment_plan.md`、脚本、运行记录 | issue + PR |
| 结论 | 沉淀证据支持的原则或方案 | README、最终报告、项目原则或 changelog | PR review |

## 状态流转

| 状态 | 进入条件 | 完成条件 | 下一步 |
| --- | --- | --- | --- |
| `submitted` | 有人提交线索 issue | 来源、关键观点和关联问题可读 | `needs-novelty-check` |
| `needs-novelty-check` | 线索需要项目内查重 | 已判定为重复、补充、冲突、新假设或实验候选 | 对应新颖性标签 |
| `duplicate` | 已有同类来源或结论 | 链接到已有文档或 issue | 关闭或合并引用 |
| `extension` | 对已有观点有补充价值 | 指向需要补充的笔记或综述 | `needs-deep-dive` 或 PR |
| `contradiction` | 与已有判断冲突 | 标出冲突点和需要的证据 | `evidence-needed` 或实验候选 |
| `new-hypothesis` | 形成新的可检验假设 | 写清目标、变量和评估方向 | `needs-deep-dive` 或 `experiment-candidate` |
| `needs-deep-dive` | 来源值得系统阅读 | 形成结构化笔记 | PR review |
| `experiment-candidate` | 可以转成最小实验 | 更新 `docs/experiment_plan.md` | 实验实现或暂存 |
| `evidence-backed` | 有来源、指标、失败案例或反例支撑 | 结论进入合适文档并标注证据等级 | changelog 记录 |

## 新颖性审核规则

审核时按以下顺序检查：

1. `docs/source_inventory.md` 是否已有同一来源、同一论文的不同版本或同一产品文档。
2. `docs/paper_notes/` 和 `docs/industry_notes/` 是否已有结构化笔记。
3. `docs/literature_map.md`、`docs/industry_practices.md`、`docs/research_brief.md` 是否已有相同观点。
4. `docs/experiment_plan.md` 是否已有相同或相近实验假设。
5. 这个线索是否能改变当前假设、风险判断、评估方式或实验优先级。

判断口径：

- `duplicate`：已有观点，不新增研究判断；可以补充引用。
- `extension`：已有观点的新边界、新场景、新指标、新失败案例或更强证据。
- `contradiction`：与现有判断相冲突，不能直接改结论，需要保留冲突和证据需求。
- `new-hypothesis`：能形成新的可验证假设，但还不能直接实验。
- `actionable-experiment`：目标、变量、样本、模型和评分方式基本明确，可以进入实验计划。

## 角色分工

| 角色 | 责任 | 不要求 |
| --- | --- | --- |
| Finder | 发现来源并提交研究线索 | 不要求写完整笔记 |
| Triage reviewer | 做项目内新颖性判断，补标签和下一步 | 不要求亲自深读 |
| Synthesizer | 深读单一来源，写结构化笔记 | 不要求跑实验 |
| Experimenter | 把假设转成最小实验并记录结果 | 不要求改项目原则 |
| Maintainer | 决定是否进入 README、最终报告或项目原则 | 不要求接受所有观点 |

一个人可以承担多个角色。PR 中应尽量保留 `suggested_by`、`reviewed_by`、关联 issue 和来源链接，方便后续追踪。

## GitHub 管理方案

建议使用以下 issue 模板：

- `Research Signal`：提交论文、文档、thread、issue、事故复盘等线索。
- `Deep Dive Note`：认领或提交深读笔记。
- `Experiment Proposal`：提出可验证的最小实验。

建议使用以下 labels：

| label | 用途 |
| --- | --- |
| `signal` | 原始研究线索 |
| `needs-novelty-check` | 等待项目内查重和新颖性判断 |
| `needs-deep-dive` | 需要结构化笔记 |
| `experiment-candidate` | 可以进入实验计划 |
| `duplicate` | 已有内容，合并引用即可 |
| `extension` | 补充已有观点 |
| `contradiction` | 与已有判断冲突 |
| `new-hypothesis` | 新假设 |
| `evidence-needed` | 需要来源、实验或失败案例支撑 |
| `ready-for-pr` | 范围清楚，可以实现或写文档 |

## 文档更新矩阵

| 情况 | 必改文档 | 可能需要改 |
| --- | --- | --- |
| 新来源线索 | `docs/source_inventory.md` 或 issue | `docs/contribution_workflow.md` 不需要每次改 |
| 新论文深读 | `docs/paper_notes/<source_id>.md`、`docs/source_inventory.md` | `docs/literature_map.md` |
| 新行业经验深读 | `docs/industry_notes/<source_id>.md`、`docs/source_inventory.md` | `docs/industry_practices.md` |
| 新实验提案 | `docs/experiment_plan.md` | README、最终报告结构 |
| 实验跑完 | 实验记录、`docs/experiment_plan.md` | `docs/industry_practices.md`、最终报告 |
| 项目结论变化 | 对应结论文档、`CHANGELOG.md` | README、`docs/project_principles.md` |

## 质量门槛

线索可以很轻，但进入项目结论前必须满足：

- 有原始来源或可复查 artifact。
- 已完成项目内新颖性判断。
- 已区分作者主张、项目观察、项目推测和项目结论。
- 如果涉及 prompt 或实验，已记录模型、参数、数据集、评分器、成本和失败案例。
- 如果改变项目建议，已说明影响范围、风险和回滚点。

## 最小示例

一个合格的 `Research Signal` issue 可以很短：

```text
来源：<论文或文档链接>
我觉得有价值的点：作者用失败样本生成自然语言 critique，再改写 prompt。
可能关联：本项目关于“自然语言反思是否比标量 reward 更适合 prompt 优化”的判断。
我猜的新颖性：可能是 extension，和 ProTeGi/GEPA 方向有关。
建议下一步：检查是否已在 literature_map 里覆盖；如果没有，加入深读候选。
```

一个不合格的线索通常只有“这篇很强，建议看看”，没有来源、观点或关联问题。这样的线索可以保留，但不能进入后续流程。
