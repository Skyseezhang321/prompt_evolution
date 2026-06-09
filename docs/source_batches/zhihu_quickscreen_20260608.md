# 知乎候选材料快筛与三层分析框架

更新时间：2026-06-09

## 批次信息

- 数据来源：Brave Search 域名限定搜索 `zhihu.com` / `zhuanlan.zhihu.com`
- 原始 artifact：`artifacts/source_search/source_candidates_20260608_132914.jsonl`
- Markdown 预览：`artifacts/source_search/source_candidates_20260608_132914.md`
- 候选数量：99 条
- 本地相关性粗分：high 9，medium 65，low 25
- 当前状态：仅完成搜索候选快筛，尚未抓取全文，尚未进入结构化行业笔记

## 证据边界

知乎材料在本项目中优先作为中文社区传播、工程经验和二手解读线索，不直接作为学术或工程结论证据。进入最终报告前，所有关键主张都要追溯到论文、官方文档、代码仓库、实验记录或可复现案例。

处理规则：

- 不把知乎文章数量当作证据强度。
- 不整篇转载原文；如需留存登录后可见或可能失效内容，只放入 `local_sources/raw/` 并记录 SHA256。
- 只把一手工程实践、带代码复现、明确实验设置或对中文使用场景有补充的文章列为深读候选。
- 对论文解读文章，要记录其指向的原论文和可能误读点。
- 每条保留候选都要尝试写出 `specific_insight_card`：一句话现象、普通用户做法、验证方式、边界。如果只能写成“介绍某方法”，说明它更适合作为索引而不是报告洞见。

## 建议的三层产出

### 第 1 层：简要分析概述

目标是用 1-2 页回答：

- 中文社区当前最关注哪些方向：APO/APE、GEPA、DSPy/MIPRO、上下文工程、Prompt Optimizer 工具。
- 哪些内容只是论文或英文博客转述，哪些可能包含本土工具、中文实践或工程踩坑。
- 哪些关键词反复出现，可以影响后续资料搜集优先级。
- 哪些主张需要立即追溯一手来源。

### 第 2 层：详细内容介绍

对 15-25 篇候选写 source card，每条至少记录：

```yaml
标题:
链接:
类型: 论文解读 | 工具实践 | 经验总结 | 上下文工程 | 泛 prompt 技巧 | 噪声
核心主张:
specific_insight_card:
  一句话现象:
  普通用户做法:
  最小验证:
  边界:
涉及论文或工具:
证据类型: 一手实验 | 官方文档 | 论文转述 | 作者经验 | 二手总结
可采信程度: strong | medium | weak
对本项目价值:
需要追溯的一手来源:
处理建议: 入库 | 深读 | 仅作线索 | 排除
```

### 第 3 层：重点论文详细介绍

按论文/框架追溯，而不是按知乎文章展开。优先级：

1. GEPA / reflective prompt evolution
2. DSPy / MIPROv2
3. APE / APO / OPRO / EvoPrompt
4. PromptBreeder / self-referential prompt evolution
5. PRewrite / RL prompt rewriting
6. Context engineering survey 和 agent context engineering
7. OPIK / Prompt Optimizer / PromptPilot 等工具化实践

每篇重点论文或框架应回到原始论文、官方文档、代码或 demo，再记录知乎文章如何理解、简化或传播该方法。

## 初步分类

| 类别 | 代表候选 | 初步判断 | 下一步 |
| --- | --- | --- | --- |
| APO / APE 综述 | `自动生成prompt：Automatic prompt engineering`、`自动提示工程：APE，APO，EvoPrompt，OPRO，PE2`、`自动优化Prompt：Automatic Prompt Engineering的3种方法` | 适合补中文术语和方法列表，但大概率是二手综述 | 追溯 APE、OPRO、EvoPrompt、PRewrite 原文 |
| GEPA / 反思式进化 | `当提示词优化器学会进化，竟能胜过强化学习`、`DSPy GEPA: 将演化算法引入prompt优化`、`GEPA：自然语言反思优化Prompt，比 RL 更高效的优化方法` | 与当前研究主线高度相关，但必须核验原论文和代码 | 深读原论文，知乎只作为传播与理解差异线索 |
| DSPy / MIPRO | `自动写提示词：DSPy.MIPROv2的介绍与实践（附代码）`、`DSPy的前世今生`、`DSPy使用从0到1快速上手` | 若含代码或实践，可作为实验框架候选说明 | 优先筛带代码或可复现实例的文章 |
| 上下文工程 | 多篇 `Context Engineering` / `上下文工程` / agent context 文章 | 数量多，说明中文圈已把 prompt 问题扩展到 context/workflow | 选 3-5 篇高质量文章对比官方/论文 taxonomy |
| 工具实践 | OPIK、Prompt Optimizer、PromptPilot、Coze、PromptIDE、Auto-Prompt | 可能补充产品化、用户体验和本土工具视角 | 只保留有 eval、对比、失败案例或配置细节的来源 |
| 泛 prompt 技巧 | 黄金法则、万能提示词、提示词写法 | 对 self-evolution 贡献较弱 | 多数仅作背景或排除 |
| Agent 自进化 | Hermes Agent、Manus、agent context 相关文章 | 可能与记忆、技能库、轨迹反思相关 | 需要回到项目、论文、issue 或官方说明核验 |

## 优先深读候选

| 优先级 | 候选标题 | URL | 理由 |
| --- | --- | --- | --- |
| P1 | OPIK：一个开源的自动提示词优化框架 | https://zhuanlan.zhihu.com/p/1998120566998204578 | 工具实践线索，可能连接生产化 prompt optimizer |
| P1 | 当提示词优化器学会进化，竟能胜过强化学习 | https://zhuanlan.zhihu.com/p/1934299196959199541 | GEPA 中文传播线索 |
| P1 | 自动写提示词：DSPy.MIPROv2的介绍与实践（附代码） | https://zhuanlan.zhihu.com/p/18156572393 | DSPy/MIPRO 实践候选 |
| P1 | DSPy GEPA: 将演化算法引入prompt优化 | https://zhuanlan.zhihu.com/p/1933283590302601451 | GEPA 与 DSPy 结合 |
| P1 | LLM agent 专题（4）提示词自动优化：从 APE 到 PRewrite | https://zhuanlan.zhihu.com/p/1993711012239664512 | 覆盖多种 APO 方法，适合做方法索引 |
| P2 | 自动提示工程：APE，APO，EvoPrompt，OPRO，PE2 | https://zhuanlan.zhihu.com/p/16918997361 | 早期方法综述线索 |
| P2 | 通过 LLM 自我优化找到最优提示词的方法: OPRO | https://zhuanlan.zhihu.com/p/661890697 | OPRO 中文解读 |
| P2 | GEPA：自然语言反思优化Prompt，比 RL 更高效的优化方法 | https://zhuanlan.zhihu.com/p/2026228834559697783 | GEPA 复述或补充线索 |
| P2 | Context Engineering，一篇就够了。 | https://zhuanlan.zhihu.com/p/1938967453951571269 | 上下文工程概述线索 |
| P2 | LangChain官方分享LLM的“上下文工程”技巧 | https://zhuanlan.zhihu.com/p/1920981931920693117 | 可追溯到官方博客 |
| P2 | 当 AI 开始自我进化：Hermes Agent 到底改变了什么？ | https://zhuanlan.zhihu.com/p/2032842861587252215 | agent 自进化补充线索 |
| P3 | PromptPilot：提示词优化工程终结者？ | https://zhuanlan.zhihu.com/p/1916783655751250271 | 工具体验，需看是否有 eval |
| P3 | Prompt-Optimizer: AI 提示词优化神器全攻略 | https://zhuanlan.zhihu.com/p/1892351710292332883 | 工具体验，证据等级待定 |
| P3 | 结构化提示词（三）：字节跳动Coze提示词优化器！ | https://zhuanlan.zhihu.com/p/701894071 | 本土工具链线索 |

## 第一层概述草案

从标题和搜索摘要看，知乎候选材料呈现三个明显趋势。

第一，中文社区已从传统 prompt 技巧转向自动化 prompt 优化和上下文工程。高相关候选集中在 GEPA、DSPy/MIPROv2、OPRO、APE/APO、PromptBreeder 以及 Context Engineering，这与项目当前文献地图一致。

第二，知乎材料更适合补“传播路径、工程理解和中文工具生态”，不适合直接支撑方法有效性的结论。多数候选看起来是论文或英文博客的中文转述，真正有价值的是带代码、带工具配置、带 eval 对比或包含失败案例的文章。

第三，上下文工程在知乎候选中占比很高，说明中文实践者已经把 prompt 优化问题扩展到 agent context、memory、workflow 和检索组织。这一部分应与论文中的 context engineering taxonomy、Anthropic/LangChain 等官方实践互相校验。

## 后续任务建议

1. 先从 P1/P2 候选中选 15-20 篇打开核验，标记为 `深读`、`仅作线索` 或 `排除`。
2. 对进入深读的行业材料，按 `docs/industry_notes/template.md` 写结构化笔记。
3. 对涉及论文的文章，先建立“知乎文章 -> 原论文/官方来源”的追溯表。
4. 将稳定线索更新到 `docs/source_inventory.md`，不要直接把全部 99 条导入正式清单。
5. 从知乎材料中抽取中文任务、中文工具和本土 agent 经验，作为英文论文和官方文档之外的补充维度。
