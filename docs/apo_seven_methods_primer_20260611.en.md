# APO Seven Methods Backbone Primer (APE→ProTeGi→OPRO→DSPy→TextGrad→MIPROv2→GEPA)

Generated: 2026-06-11

reviewed_by: Claude

Scope: The baseline backbone "APE→ProTeGi→OPRO→DSPy→TextGrad→MIPROv2→GEPA" is cited repeatedly across reports and notes in this repository (see the `CHANGELOG.md` classic-anchor catch-up entry), yet previously only individual deep-read notes existed — there was no single document weaving the seven methods into a coherent narrative with terminology introductions. This document fills that gap: each method receives its positioning, mechanism, representative results, and the gap that subsequent methods addressed, along with a pointer to its deep-read note.

Evidence level: All content is synthesized from seven `method-and-results-read` deep-read notes (each based on a locally read PDF/text with SHA256); all figures use consistent definitions with those notes and can be traced item by item. This constitutes **paper-level evidence, not reproduction results from this project**; raw scores across papers cannot be directly compared (tasks, models, and eras differ) — when citing, you must bind each figure to its original experimental setup.

> This backbone is not the only lineage. The evolutionary-algorithm branch (EvoPrompt, PromptBreeder) and the controlled counterexample PROSE are covered in the lateral comparison at [classic_optimizer_methods_comparison_20260610.md](classic_optimizer_methods_comparison_20260610.md); the planning-search branch (PromptAgent) and the historical anchor (GrIPS) serve as off-backbone anchors under Hidden Thread 3 and §1 historical positioning; this document covers only the seven methods treated as the "baseline backbone" by this repository. Why this backbone was selected and ordered this way is explained below under "Why This Backbone."

## The Backbone in One Sentence

This chain is the evolutionary history of automatic prompt optimization (APO) from **blind search → exploiting failure feedback → exploiting optimization trajectories → optimizing an entire program → general-purpose textual backpropagation → joint Bayesian search → reflective evolution**. Three hidden threads drive the evolution: **feedback signals grow richer** (scalar scores → failure critiques → per-node textual gradients → full execution traces); **the optimization target grows larger** (a single instruction → instruction + demonstrations → multi-module programs); **search structures grow smarter** (blind sampling → beam → MCTS planning → Pareto candidate pools; the planning-search station is provided by the off-backbone anchor PromptAgent — see "Meaning of the Three Hidden Threads," item 3).

Ordering note: the seven methods are ordered **chronologically**, and their mechanisms form a **dual-track convergence** — the critique track (ProTeGi → TextGrad) and the program track (DSPy → MIPROv2) develop in parallel and converge in GEPA (reflective traces × multi-module programs × Pareto pool). MIPROv2 appearing after TextGrad is a chronological fact, not an indication that "feedback density keeps rising" — it belongs to the scalar-signal family (see the "Signal Family" column in the summary table below, noting the alternation). Reading the backbone as a monotonically ascending chain is a misreading.

## Why This Backbone

The backbone is not a leaderboard, nor was it specified on a whim; its formation process and selection criteria are fully traceable:

**Formation process (four steps, all documented in the repository)**

1. **Seed** (2026-06-08): [literature_map.md](literature_map.md) and `research_brief.md` on the day the repository was initialized inventoried domain-recognized classics via literature search — this group of methods appeared there. They are a literature-search conclusion, not an improvised designation from conversation.
2. **Flagged as gap** (2026-06-08): When building a taxonomy from an arXiv top-80 scan, most classic anchors were found not in the top-80 sample; [arxiv_top80_taxonomy.md](arxiv_top80_taxonomy.md) explicitly marked "classic anchors not yet deep-read" — at that point their status was only an unverified hypothesis.
3. **Deep-read closure** (2026-06-10): Full-text, evidence-level deep reads of APE / OPRO / DSPy / MIPROv2 / TextGrad were completed (together with existing ProTeGi / GEPA notes, etc.), formally establishing the baseline backbone (see the `CHANGELOG.md` classic-anchor catch-up entry).
4. **External validation** (2026-06-10): Three independent surveys (APO survey 2502.16923, APE survey 2502.11560, Context Engineering survey) were used for a [completeness check](arxiv_taxonomy_completeness_check_20260610.md), confirming no major omissions within the scope of "discrete natural-language prompt optimization." A backbone structural review on 2026-06-12 targeted GrIPS and PromptAgent for supplementary reading, verifying the historical-positioning anchor and the search-structure missing link respectively (conclusions incorporated into this document).

**Selection criteria (why these seven, in this order)**

- **Baseline-anchor lineage, not a leaderboard**: The inclusion criterion is "this project's experiments must compare against or reference it" — APE/OPRO are mandatory lower-bound comparisons, ProTeGi/TextGrad are critique-track comparisons, MIPROv2 is the instruction+demo joint optimization baseline, and GEPA is the strongest baseline most worth reproducing at present.
- **Each link leaves a gap; the next link fills it**: APE doesn't use failure information → ProTeGi fills it; OPRO doesn't know why it fails → DSPy/MIPROv2 change the target, TextGrad/GEPA change the signal; DSPy doesn't optimize instructions → MIPROv2 fills it — the evolution has mechanistic logic, not merely chronological listing.
- **Evidence discipline**: All seven methods have `method-and-results-read` deep-read notes (local PDF + SHA256), with figures traceable item by item; and all three independent surveys treat this group of methods as canonical.
- **Deliberate exclusions and their destinations**: Evolutionary branch (EvoPrompt/PromptBreeder, scalar-signal family) → [six-method lateral comparison](classic_optimizer_methods_comparison_20260610.md); planning-search branch (PromptAgent) → Hidden Thread 3 off-backbone anchor; historical predecessors (GrIPS already read, AutoPrompt/RLPrompt pending) → §1 historical positioning; PROSE → coin-flip internal baseline, not an independent publication. The single-chain presentation serves the narrative entry point; the structural reality is the dual-track convergence described above.
- **Endpoint definition**: The backbone stopping at GEPA is not a matter of lagging updates — the [arXiv 2025/2026 frontier deep-read synthesis](arxiv_2025_2026_frontier_synthesis_20260612.md) time-slice of 25 papers shows "the era of naming new methods (2022–2024) is over"; the only named method establishing a backbone among those 25 is GEPA. Subsequent evolution appears as four shift patterns, bridged by the "After the Backbone" section.

## 1. APE (2022) — Starting Point of the Propose-then-Select Paradigm

**Automatic Prompt Engineer** (Zhou et al., ICLR 2023) formalizes "writing instructions" as a minimal two-phase black-box search: **propose-then-select**.

- **Historical positioning** (added 2026-06-12): GrIPS (v1 2022-03, eight months before APE) was already doing gradient-free black-box instruction search, but its candidates came from mechanical phrase edits (delete/swap/rewrite/add-back) and self-admittedly could not introduce information beyond the initial instruction. APE's claim to the starting position is that it was the **first to delegate candidate generation to an LLM** (LLM-as-generator), not "the first black-box instruction search." See [paper-grips-2022.md](paper_notes/paper-grips-2022.md); the earlier AutoPrompt (white-box gradients) / RLPrompt (RL policy) belong to a different signal family and remain to be read.

- **Mechanism**: Show an LLM a small number of input-output examples, ask it to infer "what instruction would produce this mapping," generate roughly 50 candidate instructions in batch; then use a score function (execution accuracy or log probability) on a small training set to select the highest-scoring one. An optional iterative Monte Carlo search — generating semantic variants of high-scoring instructions for another round of filtering — is included, but the paper self-reports only marginal gains.
- **Representative results**: Reached or exceeded human performance on 24/24 instruction induction tasks (IQM 0.810 vs. 0.749); found the zero-shot CoT prompt "Let's work this out in a step by step way to be sure we have the right answer.", raising MultiArith from 78.7 to 82.0 and GSM8K from 40.7 to 43.0 (relative to the "Let's think step by step." starting point).
- **Gap left**: Pure "generate → score → select" — **does not exploit the information in failure cases**, candidates are independent of each other, and search is nearly blind; it also first exposed the over-fitting caveat that "selection criteria must match the deployment scenario" (an instruction selected under a zero-shot criterion drops in performance in a few-shot scenario).
- Deep-read note: [paper-ape-2022.md](paper_notes/paper-ape-2022.md)

## 2. ProTeGi (2023) — Introducing "Textual Gradients"

**Prompt Optimization with Textual Gradients** (Pryzant et al., EMNLP 2023) — the paper's title is literally "Automatic Prompt Optimization with 'Gradient Descent' and Beam Search."

- **Mechanism**: Analogizes gradient descent to natural-language space — takes the **error examples** from a minibatch run with the current prompt, asks an LLM to summarize the reasons for failure (this critique is the "textual gradient"), then edits the prompt in the "semantic opposite direction"; candidates are expanded via paraphrase and entered into beam search, with a bandit algorithm (UCB family) handling evaluation budget allocation so that not every candidate needs to run on the full validation set.
- **Representative results**: Averaged 3.9% above Monte Carlo search, 8.2% above RL, and 15.3% above the original prompt across four classification benchmarks; the maximum improvement over the initial prompt was 31%. Ablations show that beam search and bandit selection each contribute independently.
- **Gap left**: The first method to make failure cases an optimization signal and the origin of the subsequent critique/trace track (TextGrad, GEPA); however, the learning curve plateaus at about 3 steps, after which it over-fits or stagnates locally, and the critique itself can mislead (qualitative cases of the gradient pulling focus in the wrong direction).
- Deep-read note: [paper-protegi-2023.md](paper_notes/paper-protegi-2023.md)

## 3. OPRO (2023) — LLM as Optimizer

**Optimization by PROmpting** (Yang et al., DeepMind) takes a different angle: instead of failure cases, it uses **optimization trajectories**.

- **Mechanism**: Constructs a meta-prompt containing historical (instruction, training-score) trajectories sorted in **ascending** score order (truncated to top-20), plus a few task examples; at each step the optimizer LLM samples 8 **entirely new** instructions (not edits, no semantic-preservation requirement), evaluates them, and appends the results back to the trajectory to loop. The LLM infers improvement directions from the "solution–score" patterns in context.
- **Representative results**: Found "Take a deep breath and work on this problem step-by-step." (GSM8K test 80.2, vs. "Let's think step by step." 71.8, empty string 34.0); on BBH, exceeded human-written instructions by more than 5% on most tasks.
- **Gap left**: The signal is only a scalar score — **no understanding of why it fails**, unable to locate root causes; the best prompt is highly model-specific (more like searching for "key phrases that trigger a specific model's specific capabilities"); the claim "no validation set required by default" was subsequently challenged repeatedly (train–test gap often 5%–20%). This project uses OPRO as a negative-control comparison and enforces a held-out set.
- Deep-read note: [paper-opro-2023.md](paper_notes/paper-opro-2023.md)

## 4. DSPy (2023) — From "Optimizing One Prompt" to "Compiling a Program"

**DSPy** (Khattab et al., Stanford) is a paradigm shift, not just another algorithm.

- **Mechanism**: Abstracts a multi-step LM pipeline into a **program** — uses signatures (e.g., `question -> answer`) to declare the input/output semantics of each LM call, and modules (Predict / ChainOfThought / ReAct) to instantiate them into a composable computation graph; the specific prompt text is not hand-written but **compiled out by a teleprompter (in-compiler optimizer) targeting a metric**. The core optimizer in this version is BootstrapFewShot: runs the program at high temperature over training inputs, transparently traces multi-stage traces, filters traces where the full pass satisfies the metric, bootstraps the per-module input-output pairs from those traces as demonstration candidates, and then random-searches / uses Optuna to select combinations on a dev set.
- **Representative results**: Compiled GPT-3.5 from ~33% to 88.3 dev / 81.6 test on GSM8K; compilation enabled Llama2-13b-chat to match GPT-3.5; T5-770M with only 200 annotated examples matched the expert-prompted GPT-3.5 solution.
- **Key clarification** (repeatedly emphasized in this repository): **This version optimizes demonstrations, not instructions** — treating DSPy as "a tool that automatically rewrites instructions" is a misreading; systematic automatic instruction optimization comes only in MIPROv2/COPRO. Its paradigm contribution is shifting the evaluation criterion from "model X on task Y" to "model X + program P + compilation strategy S on task Y."
- Deep-read note: [paper-dspy-2023.md](paper_notes/paper-dspy-2023.md)

## 5. TextGrad (2024) — Generalizing Textual Backpropagation

**TextGrad** (Yuksekgonul et al., Stanford) generalizes ProTeGi's "textual gradient" into a general-purpose **textual automatic differentiation framework**.

- **Mechanism**: Models any compound system as a computation graph, where variables are text (prompts, code, molecules, answers, …). After computing a loss in the forward pass (LLM evaluation or rule-based metric), an LLM produces a natural-language critique (textual gradient) for each variable and **backpropagates node by node** through the graph; a text-based gradient descent (TGD) then rewrites the variables. The API is deliberately isomorphic to PyTorch (`Variable` / `loss.backward()` / `optimizer.step()`). Typical cost structure: **a weak model handles forward passes, a strong model serves as the gradient engine**; stability is supported by minibatch + momentum + a **revert-if-worse validation gate** (each round accepts only updates that improve performance on the validation set).
- **Representative results**: Instruction-only (zero demo) prompt optimization on BBH Object Counting: 77.8 → 91.9, surpassing DSPy's 8-demo approach by 7%; matched DSPy on GSM8K (81.1), and adding DSPy-selected demos to the optimized instruction further raised it to 82.1 — **instruction and demonstration are two complementary axes**.
- **Gap left**: "Gradient" is a metaphor the authors themselves acknowledge rather than a true gradient — this repository has a separate critical note [paper-textual-gradients-flawed-metaphor-2025.md](paper_notes/paper-textual-gradients-flawed-metaphor-2025.md); each backpropagation step involves multiple LLM calls at non-trivial cost; reliability degrades when many natural-language constraints are stacked; cross-model transfer has not been validated.
- Deep-read note: [paper-textgrad-2024.md](paper_notes/paper-textgrad-2024.md)

## 6. MIPROv2 (2024) — Joint Bayesian Optimization of Instructions and Demonstrations

**MIPRO** (Opsahl-Ong et al., EMNLP 2024; implemented in the DSPy library as MIPROv2) fills the gap DSPy left on "how to automatically optimize instructions in a multi-stage program," formalizing the problem as two challenges: **proposal** (the prompt space is too large — how to sample a small number of high-quality candidates) and **credit assignment** (only a program-level metric is available with no module-level labels — how to attribute it to individual modules).

- **Mechanism**: Three steps — (1) **bootstrap demonstrations** (reusing DSPy's trace-filtered bootstrapping); (2) **grounded instruction proposal**: feeds the proposer LM a summary of dataset patterns, a summary of the program control flow, bootstrapped demos, and historical scores, asking it to write task-grounded candidate instructions; (3) **Bayesian joint search**: uses Optuna's TPE to build a surrogate model, evaluates "which instruction × which demo set per module" combinations on mini-batches, and updates the prior — proposal and selection are decoupled.
- **Representative results** (7 tasks, 5 runs + significance tests): Joint optimization was best on 5/7 tasks, with a maximum gain of +13%. The most important diagnostic conclusion: **on most tasks, optimizing bootstrapped demonstrations is more effective than optimizing instructions**; instruction optimization is decisive only for tasks with "non-obvious conditional rules that cannot be expressed with a few examples."
- **Gap left**: The optimizer cannot infer hidden rules for complex tasks — a seed prompt still needs to be written by a human; the surrogate model can only select within a fixed candidate set and cannot improve candidates themselves; the demo set itself has high variance.
- Deep-read note: [paper-miprov2-2024.md](paper_notes/paper-miprov2-2024.md)

## 7. GEPA (2025) — Reflective Evolution + Pareto Frontier

**GEPA** (Genetic-Pareto, Agrawal et al.) is the current endpoint of the backbone, positioned as "reflective prompt evolution can surpass RL fine-tuning."

- **Mechanism**: Three core components —
  1. **Reflective mutation**: Selects one module in the system, executes it on a minibatch and collects execution traces + evaluation traces (compilation errors, failed rubrics, module-level failure reasons, and other natural-language feedback), and asks a reflection LM to rewrite that module's prompt accordingly — inheriting ProTeGi/TextGrad's critique approach, but the input is the full rollout trace rather than just a score or single-point critique;
  2. **Pareto candidate pool**: Maintains a candidate × example score matrix, keeps all non-dominated candidates that are best on at least one example, and samples parents according to their frequency of appearance on the Pareto frontier — preventing greedy global-best optimization from locking into a local pattern too early;
  3. **System-aware merge (crossover)**: Combines the winning prompt from each module across different evolution branches into a new candidate (GEPA+Merge).
- **Representative results**: On Qwen3 8B, aggregate score 45.23 → 54.85, surpassing GRPO (RL, fixed 24,000 rollouts) at 48.91 and MIPROv2 at 47.84, while GEPA used on average only ~3,936 rollouts; the paper reports an average of ~6% above GRPO and up to 20% maximum, using up to 35× fewer rollouts. Ablations show **Pareto selection itself is the primary contributor** (aggregate improvement +12.44 vs. greedy +6.05, beam +5.11); the output prompt is up to 9.2× shorter than MIPROv2's.
- **Gap left**: Still below GRPO on AIME-2025 (reflective evolution is not a universal replacement for RL); Merge actually decreases performance on Qwen3 8B; most rollout budget is spent validating candidates rather than generating learning signal; the advantage depends on feedback function quality, and narrows when evaluation can only return a scalar. The applicable conditions were later formalized by VISTA as "feedback contains trace-level diagnosis + the true root cause lies within the hypothesis space" — counterexamples and figures appear in the "After the Backbone" section below.
- Deep-read note: [paper-gepa-2026.md](paper_notes/paper-gepa-2026.md)

## Backbone Summary

| Method | Year | Feedback Signal | Optimization Target | Signal Family | Search / Selection Structure |
| --- | --- | --- | --- | --- | --- |
| APE | 2022 | Small training-set scalar score | Single instruction | Scalar | Batch proposal (~50), select by score, optional MC iteration |
| ProTeGi | 2023 | Natural-language critique of failure examples | Single prompt | Critique | Beam search + bandit (UCB family) budget allocation |
| OPRO | 2023 | Historical (prompt, score) ascending trajectory | Single instruction | Scalar | Trajectory top-20 append loop, 8 candidates per step, keep best |
| DSPy | 2023 | Metric pass/fail (trace used to filter demos) | Multi-module program, primarily demonstrations | Scalar (with trace filtering) | RandomSearch / Optuna (TPE) to select combinations on dev |
| TextGrad | 2024 | Per-node backpropagated textual critique | Any text variable | Critique | Minibatch TGD + momentum + revert-if-worse gate |
| MIPROv2 | 2024 | Metric + Bayesian surrogate model | Per-module instruction × demo combinations | Scalar | TPE Bayesian surrogate joint search |
| GEPA | 2025 | Reflection over full execution/evaluation trace | Multi-module prompt pool (Pareto) | Trace | Pareto candidate pool + frequency-sampled parents + merge |

Meaning of the three hidden threads:

1. **Feedback information density determines sample efficiency.** From scalar (APE/OPRO) to critique (ProTeGi/TextGrad) to full trace (GEPA), the information extracted per rollout continuously increases — this directly corresponds to GEPA's claimed 35× rollout savings over GRPO. This project classifies evaluation methods using the three-tier "scalar / critique / trace" taxonomy and does not conflate them as "LLM rewrites prompt" (consistent with [classic_optimizer_methods_comparison_20260610.md](classic_optimizer_methods_comparison_20260610.md), conclusion 2).
2. **Scaling up the optimization target depends on program abstraction.** From single instructions to instruction+demos to multi-module systems, DSPy's signature/module/compilation abstractions are the foundation that enables this expansion; both MIPROv2 and GEPA are built on top of it. Therefore any result must be recorded together with the program structure and compilation/optimization strategy to be reproducible.
3. **Search structure is an evolution dimension independent of feedback signal** (added 2026-06-12, evidence level). Blind sampling (APE/OPRO) → beam (ProTeGi) → MCTS planning (PromptAgent, off-backbone anchor) → Pareto candidate pool (GEPA). Two single-variable ablations from different papers cross-validate: PromptAgent with candidate generation and feedback fully fixed at equal exploration budget: MCTS 0.754 > Greedy 0.698 ≈ Beam 0.697 > single-step MC 0.635 ([paper-promptagent-2023.md](paper_notes/paper-promptagent-2023.md) Table 4); GEPA ablations show Pareto selection itself is the primary contributor (aggregate +12.44 vs. greedy +6.05, beam +5.11, [paper-gepa-2026.md](paper_notes/paper-gepa-2026.md)). Implication for this project: when comparing optimizers, report "number of candidates explored" as a separate budget axis, ablate search structure and feedback signal independently, and do not attribute gains from search structure to "reflection being effective."

## After the Backbone: Why There Is No Eighth Method (2025/2026)

The backbone stopping at GEPA is not a matter of lagging updates. The time-slice conclusion of the [arXiv 2025/2026 frontier deep-read synthesis](arxiv_2025_2026_frontier_synthesis_20260612.md) across 25 papers is: **"the era of naming new methods" (2022–2024) is over** — among those 25 papers, only GEPA is a named method that establishes a backbone; the rest take the form of diagnosis, formalization, target scaling, self-evolution, and hygiene. For backbone readers, this means the gaps left by GEPA are not filled by an "eighth named method" but rather addressed in four diverging shifts:

- **Applicable conditions for reflection** (Shift 1 · Cooling and Diagnosis): VISTA proves that when the root cause is not within the hypothesis space, more reflection leads further astray — on a defective seed, GEPA 23.81% → 13.50%, and decoupling hypothesis generation from rewriting recovers 87.57%; cross-model transfer of GEPA-optimized results yields only 22.74% vs. VISTA 86.05%. "Reflection useful vs. harmful" thereby converges to two preconditions: feedback must contain trace-level diagnosis, and the true root cause must lie within the optimizer's hypothesis space. See [paper-vista-reflection-dark-2026.md](paper_notes/paper-vista-reflection-dark-2026.md).
- **Prompt bloat and spurious gains** (Shift 4 · Hygiene and Regularization): Prompt Codebooks decompose prompts into reusable units routed by input — on HotpotQA, 14.1× shorter than MIPROv2 prompts while still outperforming GEPA (IFBench 41.33, +2.72); PrefPO incorporates length/repetition/hacking rate into evaluation (TextGrad hacking rate 86% vs. PrefPO 37%). See [paper-prompt-codebooks-2026.md](paper_notes/paper-prompt-codebooks-2026.md), [paper-prefpo-2026.md](paper_notes/paper-prefpo-2026.md).
- **Feedback modality continues to evolve** (extension of Hidden Thread 1): SPEAR lets the optimizer itself write Python for confusion-matrix / groupby-style error analysis — BBH-7 average 0.938 vs. GEPA 0.628 — suggesting "structured computational analysis" as the next station after traces. See [paper-spear-2026.md](paper_notes/paper-spear-2026.md).
- **The optimizer itself enters the loop** (Shift 3 · Self-Evolution): SePO includes the optimizer's own system prompt in evolution (71.89 → 76.38; removing self-improvement drops back to 74.94); MemAPO uses dual memory for cross-task reuse (70.7% vs. TextGrad 63.6%, with cost actually down 58.6%) — the shared default assumption of all seven backbone methods that "the optimizer is static" is beginning to loosen. See [paper-sepo-2026.md](paper_notes/paper-sepo-2026.md), [paper-memapo-2026.md](paper_notes/paper-memapo-2026.md).

For the complete timeline, convergence of the two tensions (reflection useful vs. harmful; large gains vs. coin flip), and gap inventory (bi-level / thought-driven entirely absent), see the frontier synthesis itself; this section only bridges from the backbone perspective and does not duplicate its conclusions — all figures are consistent with that synthesis and the individual notes.

## Usage Conventions for This Project

- This backbone is a **baseline-anchor lineage**, not a leaderboard: APE and OPRO are mandatory lower-bound comparisons for any optimizer experiment; ProTeGi/TextGrad are critique-track comparisons; MIPROv2 is the instruction+demo joint-optimization baseline; GEPA is the strongest baseline most worth reproducing at present (see [literature_map.md](literature_map.md)).
- Before deploying any backbone method, first pass the **pre-optimization gate**: zero-shot baseline → headroom / noise-floor estimate → Prompt Repetition zero-cost comparison (in non-reasoning mode, 47/70 significant wins with 0 losses — a free lower bound); basis in [frontier synthesis](arxiv_2025_2026_frontier_synthesis_20260612.md) Shift 1 (Coin Flip: 49% of 72 optimization runs fell below zero-shot).
- When citing figures from any of these methods, bind them to their original experimental setup; the only fair cross-method comparisons are results from placing multiple methods inside the same framework (e.g., coin-flip; see [classic_optimizer_methods_comparison_20260610.md](classic_optimizer_methods_comparison_20260610.md)).
- The minimal validation/reproduction plan for each method is written in the final section of the corresponding deep-read note and is not repeated here.

## Related Documents

- Seven deep-read notes: [APE](paper_notes/paper-ape-2022.md), [ProTeGi](paper_notes/paper-protegi-2023.md), [OPRO](paper_notes/paper-opro-2023.md), [DSPy](paper_notes/paper-dspy-2023.md), [TextGrad](paper_notes/paper-textgrad-2024.md), [MIPROv2](paper_notes/paper-miprov2-2024.md), [GEPA](paper_notes/paper-gepa-2026.md)
- Off-backbone anchors (added in 2026-06-12 structural review): [GrIPS (historical predecessor: gradient-free edit search)](paper_notes/paper-grips-2022.md), [PromptAgent (planning-search missing link)](paper_notes/paper-promptagent-2023.md)
- Time slice after the backbone: [arXiv 2025/2026 Frontier Deep-Read Synthesis](arxiv_2025_2026_frontier_synthesis_20260612.md) (four shifts + two tensions + gap inventory)
- Evolutionary-algorithm branch and same-framework lateral comparison: [classic_optimizer_methods_comparison_20260610.md](classic_optimizer_methods_comparison_20260610.md)
- Literature panorama and priority reading order: [literature_map.md](literature_map.md)
- Critique of the "textual gradient" metaphor: [paper-textual-gradients-flawed-metaphor-2025.md](paper_notes/paper-textual-gradients-flawed-metaphor-2025.md)
- Field and evidence criteria: `docs/insight_field_standard.md`
