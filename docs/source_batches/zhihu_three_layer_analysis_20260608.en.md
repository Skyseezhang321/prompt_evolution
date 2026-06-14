# Zhihu Candidate Materials Three-Layer Analysis

Updated: 2026-06-09

2026-06-09 content supplement: Following the latest insight-first principle, Zhihu insights, helpful methods, anti-patterns, and minimal-verification candidates oriented toward the final report have been organized into [Zhihu Candidate Materials Insight and Method Cards](zhihu_insight_cards_20260609.md). This file continues to serve as the three-layer source analysis and traceability draft.

2026-06-10 two additional notes: (1) The "evidence level" (weak/medium/unknown) in each thematic table in this file is a rough quick-screen judgment for sorting purposes only; the authoritative evidence_strength follows the canonical A/B/C/D grading converged in the [Insight and Method Cards](zhihu_insight_cards_20260609.md). (2) Channel-level coverage gap: this batch contains only approximately 2 candidates in Safety / Eval / Observability, well below the coverage matrix threshold for eval/governance (8 entries); the Zhihu channel should be assessed as weak coverage in this direction, and the relevant evidence must be supplemented from official tool documentation and other channels — do not artificially inflate numbers within this channel.

## Scope of Analysis

This analysis is based on the titles and Brave Search summaries of the Zhihu batch candidates, not on full-text deep reads. Direct access to some Zhihu links returned 403 errors; this document therefore represents a quick-screen analysis at the source-collection stage and does not constitute final research conclusions.

- Raw candidates: `artifacts/source_search/source_candidates_20260608_132914.jsonl`
- Markdown preview: `artifacts/source_search/source_candidates_20260608_132914.md`
- Candidate count: 99
- Rough relevance scores: high 9, medium 65, low 25
- Processing goal: compress 99 entries into a thematic map, priority deep-read sources, and key paper/framework traceability paths

Evidence boundary:

- Zhihu articles serve primarily as leads for Chinese-community dissemination, tooling ecosystem, and engineering understanding.
- Claims involving method effectiveness, performance gains, cost reduction, or outperforming RL must be traced back to the original papers, official documentation, code repositories, or reproducible experiments.
- Generic prompt-technique and tool-marketing articles: retain only a small number of representative examples; do not include in the core evidence chain.

## Step 0: Quick-Screen Results

Thematic rough groupings overlap; a single article may belong to multiple themes. Based on titles and search summaries, the main distribution of the current batch is:

| Theme | Approximate Count | Assessment |
| --- | ---: | --- |
| Agent / self-evolving / Hermes / Manus / Skill | 26 | Highest volume, but high evidence noise; must return to projects, code, and original articles for verification |
| APO / APE / OPRO / EvoPrompt / PRewrite | 19 | Suitable as a method index; most are paper retellings |
| Context Engineering | 17 | Heavily concentrated in Chinese-community discussion; primary lead for the shift from prompt to context/workflow |
| DSPy / MIPRO / prompt-as-program | 16 | Directly relevant to experimental framework selection; prioritize articles with code and metrics |
| GEPA / reflective prompt evolution | 15 | Highly aligned with the self-evolving main thread; but titles often contain exaggerated language |
| Tool practice / Prompt Optimizer / OPIK / Coze | 12 | Can supplement productization and domestic tooling ecosystem leads; retain only articles with eval or configuration details |
| Generic prompt techniques | 8 | Weak contribution to this project; most are downweighted |
| Safety / Eval / Observability | 2 | Few in number but governance-relevant; should be supplemented from official tool documentation later |

Quick-screen conclusions:

1. The most valuable aspect of Zhihu materials is not providing new methods, but illustrating how the Chinese community connects APO, GEPA, DSPy, and context engineering to agent, self-evolving, and tool practice.
2. High-relevance materials are clearly concentrated in the GEPA, DSPy/MIPROv2, context engineering, and Hermes Agent directions from 2025–2026.
3. There are many tool-related articles, but most resemble experience introductions or promotional pieces; filter using "does it include a dataset, scorer, comparison, failure cases, and version rollback?"

## Insight Translation Layer for General Users

The strength of the Zhihu batch lies in "how users understand, misunderstand, and use these methods," not in proving method effectiveness. When incorporated into the final report, priority should be given to translating findings into problem awareness and accessible examples, with papers, official documentation, code, or project experiments supplying the evidence.

| Problem exposed by the Chinese community | Specific insight it can be translated into | What a general user can do | Evidence boundary |
| --- | --- | --- | --- |
| Many articles are still searching for a "universal prompt." | A good prompt is not a universal template, but is bound to a task, samples, and a scorer. | First write 10–20 of your own test samples, then determine whether a template is useful. | Generic technique articles are mostly downweighted; used only as user pain points. |
| GEPA is commonly spread as "stronger than RL." | The more accurate insight is: natural-language trajectory reflection provides denser information than scalar reward alone on certain tasks. | For tasks with traces, compare `score-only` and `trace+critique` rewriting. | Performance ratios must go back to the GEPA paper and this project's reproductions. |
| DSPy/MIPRO is simplified to "auto-writing prompts." | The more accurate insight is: treating prompt, examples, and metric as program components compiled by an optimizer. | Decompose tasks into signature, examples, and metric rather than only maintaining a chat template. | Chinese articles can help with terminology; evidence goes back to DSPy/MIPRO. |
| Many context engineering articles exist. | Failure does not necessarily come from the prompt; it may come from the context the model sees. | Separately inspect RAG hits, memory, tool output, history compression, and output schema. | This is a boundary lead, not evidence of automatic prompt optimizer effectiveness. |
| Hermes / agent self-evolving is very appealing. | Self-evolving is not "accumulating more and more memory," but distilling evidence-backed failure patterns, skills, and rollback points. | For each memory/skill, record its source, applicable scope, validation results, and a disable switch. | Currently mostly weak; must return to the original project, issues, code, and run logs. |
| Tool experience articles commonly lack eval. | Whether a tool is useful depends on whether it makes testing, versioning, failure cases, and rollback easier. | When reading tool articles, extract only: dataset, metric, diff, cost, failure, rollback. | Articles lacking these fields do not enter the core evidence chain. |

## Layer 1: Brief Overview

This batch of Zhihu candidates shows that the Chinese community has shifted from "prompt techniques" to three more engineering-oriented categories of problems.

The first is automatic prompt optimization. Articles repeatedly mention methods such as APE, APO, OPRO, EvoPrompt, PRewrite, PromptBreeder, GEPA, and DSPy/MIPROv2, indicating that Chinese materials are sufficient to help build a method index and a Chinese terminology glossary. However, most of these articles are second-hand interpretations of papers or English-language materials and cannot directly support performance conclusions.

The second is context engineering. Several high-relevance candidates focus on Context Engineering, agent context, memory, tool context, RAG context, and Manus experience. Together they express a trend: Chinese practitioners have stopped limiting the optimization target to a single prompt and have shifted toward "what context, tools, and memory the model sees at each step." This aligns with the project's research hypothesis of extending the optimization target to `prompt + examples + context + tools + evaluator`.

The third is tooling and agent self-evolving practice. Candidates such as OPIK, Prompt Optimizer, PromptPilot, Coze, and Hermes Agent indicate that the Chinese ecosystem contains many tooling and productization leads. Their value lies in surfacing real-world workflows, user pain points, and domestic tools — not in proving automatic optimization is effective.

The directions most worth continuing to track in this batch are GEPA/DSPy, context engineering, Hermes Agent self-evolving, and eval-driven tool practice. Most in need of downweighting are generic prompt techniques, pure headline-driven tool promotions, and paper summaries lacking primary sources.

## Layer 2: Thematic Detailed Analysis

### 2.1 APO / APE / OPRO / EvoPrompt / PRewrite

Representative candidates:

| Candidate | URL | Value | Evidence Level |
| --- | --- | --- | --- |
| Auto-generating prompts: Automatic prompt engineering (自动生成prompt：Automatic prompt engineering) | https://zhuanlan.zhihu.com/p/672206721 | Mentions iterative generation, evaluation, and selection of prompts; points to ProTeGi/APO | weak |
| Automatic prompt engineering: APE, APO, EvoPrompt, OPRO, PE2 (自动提示工程：APE，APO，EvoPrompt，OPRO，PE2) | https://zhuanlan.zhihu.com/p/16918997361 | Suitable as an early method index | weak |
| LLM agent series (4): Automatic prompt optimization — from APE's "find," OPRO's "realize," to PRewrite's "practice" (LLM agent 专题（4）提示词自动优化：从 APE 的"找"、OPRO 的"悟"到 PRewrite 的"练") | https://zhuanlan.zhihu.com/p/1993711012239664512 | Covers APE, OPRO, PRewrite; can serve as a traceability checklist | medium |
| Finding the optimal prompt via LLM self-optimization: OPRO (通过 LLM 自我优化找到最优提示词的方法: OPRO) | https://zhuanlan.zhihu.com/p/661890697 | Chinese interpretation of OPRO | weak |
| Auto Prompt 2025 latest survey from Amazon (Auto Prompt 2025最新综述from Amazon) | https://zhuanlan.zhihu.com/p/1943346001843815123 | Points to Amazon/APO survey framework; original must be traced | medium |

Analysis:

The shared value of these articles is elevating automatic prompt optimization from "manually tuning prompts" to an optimization problem of "generate candidates, evaluate, select, iterate." They can help organize the method taxonomy, but the search summaries currently show insufficient experimental detail. Before incorporating into the final report, the APE, ProTeGi/APO, OPRO, EvoPrompt, and PRewrite papers should be consulted directly.

Relevance to this project:

- Supplement Chinese explanations for the method taxonomy.
- Help define baselines: manual prompt, APE-style, OPRO-style, ProTeGi-style.
- Flag common risks: sample overfitting, initialization sensitivity, evaluator bias.

### 2.2 GEPA / Reflective Prompt Evolution

Representative candidates:

| Candidate | URL | Value | Evidence Level |
| --- | --- | --- | --- |
| When the prompt optimizer learns to evolve, it can surpass reinforcement learning (当提示词优化器学会进化，竟能胜过强化学习) | https://zhuanlan.zhihu.com/p/1934299196959199541 | Core lead for GEPA dissemination in Chinese | medium |
| DSPy GEPA: Introducing evolutionary algorithms into prompt optimization (DSPy GEPA: 将演化算法引入prompt优化) | https://zhuanlan.zhihu.com/p/1933283590302601451 | Connects GEPA with DSPy | medium |
| GEPA: Optimizing prompts with natural-language reflection — a more efficient optimization method than RL (GEPA：自然语言反思优化Prompt，比 RL 更高效的优化方法) | https://zhuanlan.zhihu.com/p/2026228834559697783 | Emphasizes natural-language reflection signals | weak |
| GEPA: How reflective prompt evolution surpasses reinforcement learning (GRPO, etc.) (GEPA：反思性提示进化如何超越强化学习（GRPO等）) | Item 55 in candidate artifact | Likely a paper retelling | weak |
| GEPA: Reflective prompt evolution can surpass reinforcement learning (GEPA：反思性提示词进化可超越强化学习) | Item 63 in candidate artifact | Likely a paper retelling | weak |

Analysis:

GEPA articles on Zhihu concentrate on three points: natural-language trajectory reflection provides higher information density than scalar reward; evolutionary/Pareto search can more efficiently select candidates; and prompt optimization requires fewer samples than RL in certain settings. These points are directionally consistent with the claims in the GEPA paper, but titles often contain strong statements such as "surpassing reinforcement learning" that must be verified against the paper's experimental setup.

Relevance to this project:

- Serves as a Chinese-community dissemination lead for "why trajectory reflection may be more useful than final score alone."
- Supports a subsequent minimal experiment candidate: compare candidate generation with score-only vs. candidate generation with failure trace.
- Reminds the final report to clearly state GEPA's applicable tasks, baseline, rollout cost, Pareto selection, and limitations.

Should not be taken at face value:

- Numbers such as "35× efficiency improvement" or "20% higher performance" must be traced to paper tables and task settings.
- Generalized conclusions such as "no RL needed" or "replacing RL" should be rewritten as observations under specific experimental conditions.

### 2.3 DSPy / MIPRO / Prompt-as-Program

Representative candidates:

| Candidate | URL | Value | Evidence Level |
| --- | --- | --- | --- |
| Auto-writing prompts: Introduction and practice of DSPy.MIPROv2 (with code) (自动写提示词：DSPy.MIPROv2的介绍与实践（附代码）) | https://zhuanlan.zhihu.com/p/18156572393 | Priority deep-read if code is confirmed | medium |
| The past and present of DSPy (DSPy 的前世今生) | https://zhuanlan.zhihu.com/p/707184607 | Explains DSPy's technical evolution | weak |
| DSPy quick-start from 0 to 1 (DSPy 使用从 0 到 1 快速上手) | https://zhuanlan.zhihu.com/p/707925423 | Engineering onboarding lead | weak |
| DSPy Visualizer: Visualizing the prompt optimization process (DSPy Visualizer：可视化 Prompt 优化过程) | https://zhuanlan.zhihu.com/p/714277212 | Visualization and tracing lead | medium |
| DSPy prompt optimization survey (DsPy优化提示词调研) | https://zhuanlan.zhihu.com/p/1955642727363478849 | Survey lead; content depth needs verification | unknown |

Analysis:

The value of DSPy articles lies in placing prompt optimization in the context of "program compilation," emphasizing the combination of instructions, few-shot examples, metric, and optimizer. MIPROv2 is described as simultaneously optimizing instruction and few-shot examples, which aligns closely with this project's focus on "prompt is not an isolated string."

Relevance to this project:

- DSPy/MIPRO is a strong candidate for the first reproducible experiment harness or baseline.
- These articles may supplement how Chinese developers understand module, signature, metric, teleprompter/optimizer.
- Visualizer-type articles can help design run artifact and prompt diff presentation for subsequent work.

Needs to be traced:

- DSPy original paper and documentation.
- MIPROv2 paper.
- Official implementation and cookbook for GEPA in DSPy.

### 2.4 Context Engineering

Representative candidates:

| Candidate | URL | Value | Evidence Level |
| --- | --- | --- | --- |
| A complete guide to context engineering for large language models (一文搞懂：大语言模型的上下文工程) | https://zhuanlan.zhihu.com/p/1956359769540526470 | Overview of RAG, memory, tool-use, multi-agent | medium |
| On context engineering for AI agents (聊下 AI Agent 的上下文工程) | https://zhuanlan.zhihu.com/p/1932720788206778299 | Connects practitioner definitions | weak |
| LangChain's official share on LLM context engineering techniques (LangChain 官方分享 LLM 的上下文工程技巧) | https://zhuanlan.zhihu.com/p/1920981931920693117 | Traceable to LangChain official source | medium |
| Context Engineering — one article is enough (Context Engineering，一篇就够了) | https://zhuanlan.zhihu.com/p/1938967453951571269 | Spreads definitions and key references | weak |
| From prompt to context: A systematic survey of Context Engineering based on 1400+ papers (从 Prompt 到 Context：基于 1400+ 论文的 Context Engineering 系统综述) | https://zhuanlan.zhihu.com/p/1951318616042631326 | Points to systematic survey and Manus experience | medium |

Analysis:

Context engineering is the densest non-APO theme in the Zhihu batch. Candidate summaries repeatedly mention dynamic systems, the right information and tools, RAG, memory, tool-augmented reasoning, multi-agent, KV cache, and other concepts. This indicates that the Chinese community has already extended the target of prompt optimization to the organization and management of the context window.

Relevance to this project:

- Supports research hypothesis H2: the optimization target is often `prompt + examples + context + tools + evaluator`.
- Provides task design directions for agent/tool-use minimal experiments.
- Helps define immutable layers and variable layers: business objectives/safety boundaries are immutable; context selection, example selection, and tool hints are variable.

Points to note:

- Many context engineering articles may be concept dissemination without experimental evidence.
- Priority should be given to tracing back to Anthropic, LangChain, Manus, and context engineering survey primary sources.

### 2.5 Tool Practice / Prompt Optimizer / OPIK / Coze

Representative candidates:

| Candidate | URL | Value | Evidence Level |
| --- | --- | --- | --- |
| OPIK: An open-source automatic prompt optimization framework (OPIK：一个开源的自动提示词优化框架) | https://zhuanlan.zhihu.com/p/1998120566998204578 | Tool practice lead; summary mentions scoring functions and iterative optimization | medium |
| Don't know how to write AI prompts? Try Prompt Optimizer (AI 提示词不会写？试试 Prompt Optimizer) | https://zhuanlan.zhihu.com/p/28302950149 | Tool experience; should be downweighted | weak |
| Prompt-Optimizer: A complete guide to the AI prompt optimization tool (Prompt-Optimizer: AI 提示词优化神器全攻略) | https://zhuanlan.zhihu.com/p/1892351710292332883 | Open-source tool lead; GitHub should be checked | weak |
| PromptPilot: The end of prompt engineering? (PromptPilot：提示词优化工程终结者？) | https://zhuanlan.zhihu.com/p/1916783655751250271 | Product experience lead | weak |
| Structured prompts (3): ByteDance Coze prompt optimizer (结构化提示词（三）：字节跳动 Coze 提示词优化器) | https://zhuanlan.zhihu.com/p/701894071 | Domestic platform lead | weak |

Analysis:

Tool-related articles can supplement the perspective of "how real users use prompt optimizers," but they are most prone to mixing in marketing and experience pieces. Only articles containing a dataset, scorer, comparison results, cost, failure cases, or version management are worth including in industry notes.

Screening criteria:

- Does it describe the source of input samples?
- Does it describe the evaluator or scoring function?
- Does it record pre- and post-optimization metrics, rather than only displaying subjective output?
- Does it include version management, rollback, or manual review?
- Does it mention safety boundaries and non-rewritable constraints?

### 2.6 Agent Self-Evolving / Hermes / Skill / Manus

Representative candidates:

| Candidate | URL | Value | Evidence Level |
| --- | --- | --- | --- |
| When AI begins to self-evolve: What has Hermes Agent actually changed? (当 AI 开始自我进化：Hermes Agent 到底改变了什么？) | https://zhuanlan.zhihu.com/p/2032842861587252215 | Connects self-evolution with GEPA/DSPy | medium |
| Hermes Agent: The open-source AI agent that "self-evolves" (Hermes Agent：「会自我进化」的开源 AI Agent) | https://zhuanlan.zhihu.com/p/2026106192003437649 | Already has an industry-note lead; needs further verification | medium |
| Open-source AI agents HermesAgent and Openclaw — each with a distinct design philosophy (开源 AI 智能体 HermesAgent 与 Openclaw 各具设计哲学) | https://www.zhihu.com/question/2025650365819810327 | Comparative lead; original project needs verification | weak |
| What is it like to use Hermes Agent? (使用 Hermes Agent 是什么样的体验？) | https://www.zhihu.com/question/2027666092630319823 | User experience lead | weak |
| YC reveals top AI agent prompt engineering (YC 揭秘顶尖 AI 智能体 Prompt 工程) | https://zhuanlan.zhihu.com/p/1912633580997309973 | meta-prompting / agent workflow lead | weak |

Analysis:

Agent self-evolving materials are directly relevant to this project's long-term goals, but the evidence chain is most easily broken. Summaries contain strong claims such as "automatically optimizing skill, system prompt, tool description, and tool implementation code," which must be verified by returning to the Hermes/OpenClaw project, issues, code, and official documentation.

Relevance to this project:

- Provides concrete case leads for "prompt self-evolving goes beyond changing prompt text."
- Helps design the variable layers in subsequent memory/self-evolving schemes: skill, tool description, reflection policy, prompt generator.
- Reminds that self-evolving systems must have versioning, rollback, approval, and safety boundaries.

## Layer 3: Priority Content Traceability

### 3.1 GEPA: Reflective Prompt Evolution

Understanding in Zhihu:

- Summarizes GEPA as using natural-language reflection and evolutionary search to optimize prompts.
- Emphasizes sample efficiency compared to RL / GRPO.
- Connects it with DSPy, agent prompt optimization, and self-evolving systems.

Primary traceability targets:

- GEPA paper: task setup, baseline, rollout count, Pareto selection, failure cases.
- GEPA / DSPy official implementation: optimizer API, artifact, metric requirements.
- Hugging Face cookbook / Arize and similar engineering practices: whether they reproduce or only demonstrate.

Project conversion:

- Minimal experiment candidate: score-only APO vs. trace-reflection APO.
- Fields to record: original prompt, failure trace, reflection, candidate prompt, dev/validation scores, cost, rollback point.

### 3.2 DSPy / MIPROv2: Prompt-as-Program Baseline

Understanding in Zhihu:

- Treats instruction and few-shot examples as optimizable parameters.
- Compares prompt development to shifting from handwritten prompts to compilation.
- Emphasizes the roles of metric and optimizer.

Primary traceability targets:

- DSPy documentation and paper.
- MIPROv2 paper.
- DSPy GEPA cookbook.

Project conversion:

- Strong candidate for the first reproducible experiment harness.
- Use typed signature / module / metric to solidify task boundaries and avoid pure-text prompt drift.

### 3.3 APE / OPRO / EvoPrompt / PRewrite: Early APO Method Taxonomy

Understanding in Zhihu:

- APE: LLM generates candidate instructions; selects by task score.
- APO / ProTeGi: uses failed samples to generate natural-language critiques, then rewrites the prompt.
- OPRO: uses LLM to propose better solutions based on historical candidates and scores.
- PRewrite: trains a prompt rewriter via RL.

Primary traceability targets:

- APE, ProTeGi, OPRO, EvoPrompt, PRewrite original papers.
- Train/dev/test data splits and overfitting controls for each method.

Project conversion:

- Form a baseline sequence: manual → few-shot → APE-style → ProTeGi-style → GEPA-style.
- Use these methods to decompose candidate generation, feedback signal, candidate selection, and optimization target.

### 3.4 Context Engineering: From Prompt to System Context

Understanding in Zhihu:

- Context engineering is a dynamic system that provides LLMs with the information, tools, and format needed to complete tasks.
- Typical implementations include RAG, memory, tool-use, multi-agent, context compression, and KV cache design.
- For agent systems, the prompt is only one part of context management.

Primary traceability targets:

- Context Engineering survey.
- Anthropic / LangChain / Manus related engineering articles.
- Failure cases of context selection and memory in RAG/tool-use/agent workflows.

Project conversion:

- Extend the optimization target beyond instruction alone.
- Establish variable/immutable layers: context selection, examples, and tool hints are variable; safety boundaries, permissions, and business objectives are immutable.

### 3.5 Tool Practice: From "Optimizing Prompts" to Eval-Driven Workflow

Understanding in Zhihu:

- Tools such as OPIK, Prompt Optimizer, PromptPilot, and Coze provide experiences for automatically generating, optimizing, testing, comparing, and managing prompts.
- Some tools only rewrite prompts; others may include dataset, evaluator, and iterative optimization.

Primary traceability targets:

- Official documentation and code for OPIK / Prompt Optimizer / Coze / PromptPilot.
- Whether they include prompt versioning, eval, cost records, rollback, and manual approval.

Project conversion:

- Not to replicate tool UIs, but to extract the governance workflow: dataset → candidate → eval → diff → approval → rollback.
- Establish a tool practice evaluation checklist for use in industry note organization.

## Recommended Retain / Deep-Read / Exclude List

### Priority Retain and Deep-Read

| Theme | Candidates |
| --- | --- |
| GEPA | "When the prompt optimizer learns to evolve, it can surpass reinforcement learning" (当提示词优化器学会进化，竟能胜过强化学习), "DSPy GEPA: Introducing evolutionary algorithms into prompt optimization" (DSPy GEPA: 将演化算法引入prompt优化), "GEPA: Optimizing prompts with natural-language reflection — a more efficient optimization method than RL" (GEPA：自然语言反思优化Prompt，比 RL 更高效的优化方法) |
| DSPy/MIPRO | "Auto-writing prompts: Introduction and practice of DSPy.MIPROv2 (with code)" (自动写提示词：DSPy.MIPROv2的介绍与实践（附代码）), "The past and present of DSPy" (DSPy 的前世今生), "DSPy Visualizer" (DSPy Visualizer) |
| APO taxonomy | "LLM agent series (4): Automatic prompt optimization" (LLM agent 专题（4）提示词自动优化), "Automatic prompt engineering: APE, APO, EvoPrompt, OPRO, PE2" (自动提示工程：APE，APO，EvoPrompt，OPRO，PE2), "Finding the optimal prompt via LLM self-optimization: OPRO" (通过 LLM 自我优化找到最优提示词的方法: OPRO) |
| Context Engineering | "LangChain's official share on LLM context engineering techniques" (LangChain官方分享LLM的上下文工程技巧), "From prompt to context" (从 Prompt 到 Context), "Context Engineering — one article is enough" (Context Engineering，一篇就够了) |
| Agent self-evolving | "Hermes Agent: The open-source AI agent that 'self-evolves'" (Hermes Agent：「会自我进化」的开源 AI Agent), "When AI begins to self-evolve: What has Hermes Agent actually changed?" (当 AI 开始自我进化：Hermes Agent 到底改变了什么？) |
| Tool practice | "OPIK: An open-source automatic prompt optimization framework" (OPIK：一个开源的自动提示词优化框架), "Prompt-Optimizer: A complete guide to the AI prompt optimization tool" (Prompt-Optimizer: AI 提示词优化神器全攻略) |

### Use as Leads Only

- Paper summaries, paper dailies, and hot-topic decoder articles.
- Tool introductions without eval, dataset, code, or failure cases.
- Articles that only propagate GEPA conclusions without additional information.

### Tend to Exclude

- Generic prompt techniques, golden rules, universal prompts.
- Articles whose titles are relevant but whose summaries only cover ordinary prompt engineering.
- Multi-modal or safety paper roundups weakly related to the prompt optimization main thread, unless a dedicated safety/eval extension is planned later.

## Next Steps

1. Select 15–20 P1/P2 candidates for full-text verification; if full text needs to be retained, place it in `local_sources/raw/` and record the SHA256.
2. For each individual source that enters deep-read, use `docs/industry_notes/template.md`.
3. Build a traceability table mapping "Zhihu source → primary paper/official documentation/code."
4. Register the final retained sources in `docs/source_inventory.md`; do not bulk-import all 99 entries.
5. Extract one minimal experiment or engineering plan candidate from each of the three threads: GEPA, DSPy/MIPRO, and Context Engineering.
