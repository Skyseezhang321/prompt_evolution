# Paper Note: EvoPrompt

论文：EvoPrompt: Connecting LLMs with Evolutionary Algorithms Yields Powerful Prompt Optimizers

链接：https://arxiv.org/abs/2309.08532

source_id：paper-evoprompt-2024

关联 issue：无

线索贡献者：internal-arxiv-search

新颖性判断：foundational

阅读日期：2026-06-08

reviewed_by：Codex

local_pdf_path：`local_sources/raw/arxiv_papers/2309.08532/paper.pdf`

local_pdf_sha256：`776A3F4AC1F2A321761EAE0332320773D08BA7A260939296D8A979F67D82A627`

local_text_path：`local_sources/raw/arxiv_papers/2309.08532/paper.txt`

local_text_sha256：`2B3450ABFB2C8CB150A60E3C2CAD85FF3A9CADE4C9AA65DE4F5AA611485EDFD3`

evidence_level：method-and-results-read

## 一句话结论

EvoPrompt 的核心贡献是把 GA/DE 这类经典 evolutionary algorithms 翻译成 LLM 能执行的自然语言操作。它说明 prompt evolution 不必完全重造搜索算法，传统优化算法里的 selection、crossover、mutation、population update 仍然有用，但必须用 LLM 保持 prompt 的语义连贯性。

## 问题设定

- 任务：离散 prompt optimization，用黑盒 LLM 优化自然语言 prompt。
- 优化对象：单段 task instruction。
- 适用模型：Alpaca-7B 和 GPT-3.5。
- 适用任务：language understanding、summarization、simplification、BBH。
- 对照：manual instructions、PromptSource、Natural Instructions、APE、APO。

## 方法摘要

- 总框架：从 prompt population 出发，按 fitness 选择父代，用 LLM 执行 evolutionary operator，生成候选 prompt，再按 dev set 分数更新 population。
- GA 版本：
  - roulette wheel selection 选择两个 parent prompts。
  - LLM 先 crossover，再 mutation。
  - 每轮生成 N 个新 prompt，和旧 population 合并后保留 top N。
- DE 版本：
  - LLM 识别两个 prompt 的不同部分，模拟 `b-c`。
  - 只 mutation 不同部分，保护共享高价值结构。
  - 将 mutated difference 融入当前 best prompt，再和 basic prompt crossover。
  - 每个 basic prompt 只在新候选更好时被替换。
- 是否自指：否。它使用固定 GA/DE operator prompt，不优化 operator prompt 自身。

## 实验设置

- 操作者模型：GPT-3.5 负责执行 evolutionary operators。
- 被优化模型：Alpaca-7B、GPT-3.5。
- 数据：7 个 language understanding datasets、SAMSum、ASSET、23 个 BBH tasks。
- Alpaca 结果平均 3 random seeds；GPT-3.5 因预算限制报告 1 seed。
- BBH 设置：从 test set 抽一部分作为 development set，报告相对 “Let's think step by step” + 3-shot CoT 的 normalized score。

## 主要结果

论文直接报告：

- Alpaca language understanding 表 1：EvoPrompt-GA 平均 76.25，EvoPrompt-DE 平均 77.05，超过 APE 73.80、MI 71.07、NI 68.21。
- SAMSum 表 2：EvoPrompt-DE 在 Alpaca 上 ROUGE-1/2/L 为 39.46/13.93/35.49，在 GPT-3.5 上为 46.49/19.49/41.96，均高于 MI 和 APE。
- ASSET 表 3：EvoPrompt 在 Alpaca/GPT-3.5 上 SARI 均高于 MI 和 APE。
- BBH：EvoPrompt 在 22 个任务上都得到更好 prompt；DE 最高提升 25%、平均 3.5%，GA 最高提升 15%、平均 2.5%。附录表 12 报告 BBH 平均 accuracy：baseline 71.49、APE 71.85、GA 74.18、DE 75.03。
- GA 设计消融：roulette wheel selection 平均 48.17，高于 tournament 48.00 和 random 47.50。
- DE 设计消融：只 mutation 不同部分加 best prompt 组合效果最好。Subj 上 Diff+best 为 75.55，而 All+best 为 69.87，Diff+random 为 69.82，Diff+eliminate 为 69.07。
- 初始化消融：精心选择初始 prompts 不是必需；random prompts 接近 top prompts。当初始 prompts 差时，DE 比 GA 更强。

## 失败案例和局限

- GPT-3.5 结果多为单 seed，预算限制影响统计稳健性。
- BBH 从 test set 采样作为 dev set，和严格 held-out protocol 有差异。
- DE 倾向生成更长、方差更大的 prompts，探索更强但成本和可维护性风险更大。
- 只测试 canonical GA/DE，作者也承认更高级 DE variants、PSO、ACO、QD 等仍是 future work。
- 目标主要是 task performance，没有系统考察 prompt hygiene、hacking、OOD generalization。

## 洞见卡片

```yaml
insight: LLM 适合做语义保持的 evolutionary operator，而不是 token-level 随机编辑器。
evidence_type: method + result
paper_evidence:
  section: "3, 4"
  table_or_figure: "Algorithm 1, Figure 1, Figure 2, Table 1-3"
  quote_or_paraphrase: "LLM 执行 crossover/mutation，EA 负责 selection/update；31 datasets 上超过 manual prompts 和 APE/APO。"
mechanism: 传统 EA 提供 exploration/exploitation 框架，LLM 负责保持自然语言 prompt 的连贯性和可读性。
actionable_rule: 设计 prompt mutation 时，不要做字符/词级随机扰动；让 LLM 显式说明继承、变异和保留的语义部分。
counterexample_or_limit: 操作 prompt 固定，不能自适应学习更好的 mutation style。
minimal_experiment: LLM-GA mutation vs random paraphrase mutation under same population budget。
confidence: high
```

```yaml
insight: Differential Evolution 的“只改差异、保留共识”很适合 prompt 搜索。
evidence_type: ablation
paper_evidence:
  section: "5.2"
  table_or_figure: "Table 5"
  quote_or_paraphrase: "DE 中 Diff+best 明显优于 All+best、Diff+random 和去掉 Prompt 3。"
mechanism: 多个高分 prompt 的共同部分可能是稳定有效规则，差异部分才是值得探索的区域。
actionable_rule: 候选 prompt 合并时先抽取共同规则和冲突规则，再只在冲突区域做变异。
counterexample_or_limit: 如果初始 population 都很差，共同部分也可能是共同错误。
minimal_experiment: whole-prompt rewrite vs common/different-part rewrite。
confidence: high
```

## 对本项目的启发

- 对 PromptBreeder/GEPA 的 archive，我们可以增加 “common rule / divergent rule” 分析，而不是只保留候选列表。
- 如果初始 prompt 质量不确定，DE-style mutation 可能比 GA 更稳。
- Prompt evolution 的日志要保存 parent prompts 和新 prompt 中哪些片段来自哪个 parent。

## 可复现计划

- 最小复现任务：分类或抽取任务，10 个初始 prompt。
- 变量：
  - GA-style crossover+mutation。
  - DE-style diff-only mutation。
  - whole-prompt rewrite。
- 指标：dev/test accuracy、prompt length、共同规则保留率、每轮 token 成本。
