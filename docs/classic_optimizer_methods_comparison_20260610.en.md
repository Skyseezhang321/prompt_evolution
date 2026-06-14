# Classic Prompt Optimizer Methods Side-by-Side Comparison: Six Approaches (APE / OPRO / EvoPrompt / PromptBreeder / DSPy-style / PROSE)

Generated: 2026-06-10

reviewed_by: Claude

Scope: This table compares the 6 optimizers benchmarked in *Prompt Optimization Is a Coin Flip* ([[paper-coin-flip-2026]]). The first 5 are independently citable external methods, each with its own deep-read note; the 6th, PROSE, is an internal baseline built by that paper (see [[paper-prose-2026]]—its sole source is coin-flip Appendix C).

Evidence level: The mechanism and numbers for each method come directly from the corresponding deep-read notes (mostly `method-and-results-read`, read from local PDFs). The "same-framework comparison" numbers across methods come from coin-flip's unified experimental setup (Haiku / Nova Lite × 4 tasks, equal compute budget).

> Note: Scores reported in each method's **original paper are not directly comparable** (different tasks, models, and eras). The only fair cross-method comparison is the score coin-flip produces by placing all 6 methods inside the same framework (see "Same-Framework Comparison" at the end). The "Original paper representative results" column below serves only as a qualitative anchor for each method's own capabilities.

## One-Line Positioning

| Method | Year | One-Line Positioning | Standalone Note |
| --- | --- | --- | --- |
| **APE** | 2022 | Simplest foundational anchor: LLM proposes a batch of instructions + selects the best by score on a small training set (propose-then-select); no gradients, no iteration | [paper-ape-2022.md](paper_notes/paper-ape-2022.md) |
| **OPRO** | 2023 | LLM-as-optimizer baseline: packs "history of prompts + scores" in ascending order into a meta-prompt, letting the LLM infer patterns from the score trajectory to generate entirely new candidates (pure scalar trajectory) | [paper-opro-2023.md](paper_notes/paper-opro-2023.md) |
| **EvoPrompt** | 2023/24 | Translates classical GA/DE into semantic operators the LLM can execute: EA handles selection/update, LLM handles crossover/mutation | [paper-evoprompt-2024.md](paper_notes/paper-evoprompt-2024.md) |
| **PromptBreeder** | 2023 | Self-referential evolution: evolves mutation prompts alongside task prompts (hyper-mutation), learning both "the task prompt" and "how to change the prompt" | [paper-promptbreeder-2023.md](paper_notes/paper-promptbreeder-2023.md) |
| **DSPy-style** | 2023 | Prompt-as-program: signature declaration + module composition + teleprompter compilation; this version primarily **bootstraps demonstrations** rather than instructions | [paper-dspy-2023.md](paper_notes/paper-dspy-2023.md) (+ [miprov2](paper_notes/paper-miprov2-2024.md) for the instruction layer) |
| **PROSE** | 2026 | coin-flip's own controlled negative-result baseline: structured decomposition + multi-operator evolution + **risk-aware selection** (mean + Sharpe + DRO); used to falsify "risk-aware selection helps"—conclusion: no advantage | [paper-prose-2026.md](paper_notes/paper-prose-2026.md) |

## Five-Dimension Structured Comparison

### 1. Optimization Target (What Is Being Changed)

| Method | Optimization Target | Structural Granularity |
| --- | --- | --- |
| APE | Single instruction segment | Entire text |
| OPRO | Single instruction segment (with optional insertion position Q_begin / Q_end / A_begin) | Entire text |
| EvoPrompt | Single task instruction segment | Entire segment (DE version edits only the "differing parts," protecting consensus segments) |
| PromptBreeder | Task prompt + mutation prompt + few-shot contexts + some hyperparameters | Multi-object (including the optimizer itself) |
| DSPy-style | Parameters of each module—**primarily demonstrations**, optionally instruction / field description—plus control flow | Program level (signature / module / control flow) |
| PROSE | Single prompt segment, decomposed into five targeted-edit blocks: role / task / constraints / examples / format | Five-component segments |

### 2. Feedback Signal (What the Optimizer Sees)

| Method | Signal Type | Critique? | Trace? |
| --- | --- | --- | --- |
| APE | Scalar (execution accuracy or log prob) | No | No |
| OPRO | Pure scalar training score (ascending trajectory) | No | No |
| EvoPrompt | Scalar dev score (fitness) | No | No |
| PromptBreeder | Scalar batch fitness | No | No (Lamarckian variant back-infers from correct working-out) |
| DSPy-style | Metric pass / fail (programmable) | No | **Yes** (transparent multi-stage trace used for rejection sampling) |
| PROSE | Scalar LLM-judge score | No | No |

> All six are members of the **scalar-signal family** (no natural-language critique). This is precisely the gap that the ProTeGi → TextGrad → GEPA critique/trace lineage is designed to fill—none of these 6 methods belongs to that lineage. DSPy's trace is used to "filter good demos," not to "diagnose the root cause of errors."

### 3. Search Mechanism (How Candidates Are Generated and Selected)

| Method | Candidate Generation | Selection Mechanism | Archive |
| --- | --- | --- | --- |
| APE | LLM infers instructions (forward / reverse / resample), default ~50 candidates | Pick highest score on training set; optional iterative Monte Carlo | None (iterative version's previous pool is a weak archive) |
| OPRO | 8 entirely new instructions sampled each step | Pick highest training score; trajectory truncated to top-20 as archive | Weak (top-20 trajectory) |
| EvoPrompt | GA: roulette-select parents → LLM crossover + mutation; DE: only differing parts merged with best | Population + dev score, retain top-N | Population |
| PromptBreeder | 9 mutation operator types (including hyper-mutation / Lamarckian / crossover) | Binary-tournament GA; BERT-similarity deduplication + fitness sharing | Population (with lineage) |
| DSPy-style | BootstrapFewShot bootstraps trace (rejection sampling) | RandomSearch / Optuna (TPE) cross-validates on dev; can ensemble top-k | Candidate demo pool + ensemble |
| PROSE | 20 seeds → top-10 population; 6 adaptive-weight operators (targeted / crossover / random / exploration / simplification / random-gen) | **Risk-adjusted fitness**: 0.70·mean + 0.15·Sharpe + 0.15·DRO; elite 5, early stop after 4 generations without improvement | Population (20) + elite |

### 4. Self-Reference / Does the Optimizer Optimize Itself?

| Method | Self-Referential | Notes |
| --- | --- | --- |
| APE | No | Fixed proposal template |
| OPRO | No | Fixed meta-prompt structure |
| EvoPrompt | No | Fixed GA/DE operator prompt |
| **PromptBreeder** | **Yes** | Hyper-mutation also evolves the mutation prompt (`M' = LLM(H+M)`)—the only method among the 6 with explicit self-reference |
| DSPy-style | No (composable) | Teleprompter strategy is fixed, but a teacher program can supervise a student |
| PROSE | No | Operator weights are adaptive, but the fitness formula / templates are fixed |

### 5. Original Paper Representative Results and Key Limitations (Qualitative Anchors — Not Cross-Comparable)

| Method | Original Paper Representative Results | Key Limitations |
| --- | --- | --- |
| APE | Matches or exceeds human performance on 24/24 instruction-induction tasks (IQM 0.810 vs. 0.749); produces zero-shot CoT prompt | Optimizes only a single instruction; mismatch between selection criteria and deployment scenario leads to overfitting; iterative search yields weak gains |
| OPRO | GSM8K up to +8% vs. hand-written zero-shot ("Take a deep breath…" 80.2 vs. 71.8) | Pure scalar provides no way to localize root cause; strong model/task dependency; "validation set not required" claim challenged by follow-up work |
| EvoPrompt | BBH average DE +3.5% / GA +2.5%, up to +25%; outperforms APE / MI / NI | GPT-3.5 mostly single-seed; DE tends toward longer, higher-variance prompts; only canonical GA/DE tested |
| PromptBreeder | GSM8K 83.5, ETHOS 89% vs. hand-written 80%; zero-order hyper-mutation achieves up to 42% improvement rate | High cost (population 50, 1–2k evaluations); few-shot context may overshadow prompt; task prompt can drift into nonsense |
| DSPy-style | Compilation takes GSM8K from ~33% → 88%; Llama2-13b compiled to match GPT-3.5; T5-770M with only 200 labels matches larger models | This version optimizes demos, not instructions; requires a decidable metric; bootstrap×2 + ensemble amplifies cost |
| PROSE | See same-framework table below | **Negative result**: risk-aware selection shows no measurable robustness advantage |

## Same-Framework Comparison (The Only Fair Cross-Method Numbers, from coin-flip)

LLM-judge 0–100, mean of 3 repeats, held-out 100 test questions, equal compute budget (~100 candidates per method). **Bold = highest score for that task.**

### Claude Haiku 4.5 (coin-flip Table 2)

| Method | Feedback-Bench | HelpSteer2 | WildBench | XSum |
| --- | --- | --- | --- | --- |
| Zero-Shot | 82.4 | 68.0 | 68.9 | 76.0 |
| APE | 82.3 | 69.3 | 68.0 | **76.6** |
| OPRO | 81.4 | 73.8 | 69.0 | 74.7 |
| EvoPrompt | 82.0 | **74.8** | 68.3 | 75.6 |
| PromptBreeder | **83.5** | 74.6 | 68.5 | 76.0 |
| DSPy-style | 81.9 | 69.8 | 65.1 | 76.2 |
| PROSE | 82.1 | 74.4 | **69.6** | 75.9 |

> Across the entire table, only HelpSteer2 sees every optimizer beat zero-shot; the average gain on the other three tasks is negative or near zero. Differences among the 6 methods are not statistically significant.

### Amazon Nova Lite (coin-flip Table 4, worse overall)

| Method | Feedback-Bench | HelpSteer2 | WildBench | XSum |
| --- | --- | --- | --- | --- |
| Zero-Shot | 80.4 | 70.7 | 64.6 | 73.5 |
| APE | 81.1 | 69.4 | 64.4 | 73.9 |
| OPRO | 81.9 | 70.0 | 64.2 | 73.5 |
| EvoPrompt | 81.0 | 69.7 | 62.9 | 71.8 |
| PromptBreeder | 80.2 | 72.8 | 65.6 | 72.9 |
| DSPy-style | 81.0 | 69.1 | 60.2 | 73.3 |
| PROSE | 80.4 | 70.0 | 64.6 | 72.8 |

> 14 of 24 method × task cells fall below zero-shot; the 6/6 sweep that HelpSteer2 showed on Haiku collapses to 1/6 on Nova Lite.

## Actionable Conclusions for This Project

1. **Lower-bound baseline stratification**: Any optimizer experiment should include at minimum APE (propose-then-select) and OPRO (scalar trajectory) as lower-bound controls. A more complex method that cannot beat these two is not worth pursuing.
2. **Signal structure is the true classification axis**: All 6 methods belong to the "scalar signal" family; the genuine capability leap lies in the critique/trace lineage (ProTeGi → TextGrad → GEPA). When evaluating, do not lump "prompt-editing" methods together—stratify by "scalar / critique / trace" (see insight card in [[paper-opro-2023]]).
3. **DSPy optimizes demos, not instructions**: When citing "DSPy-style," always specify the optimization layer; automatic instruction optimization requires MIPROv2 / COPRO.
4. **Self-reference only in PromptBreeder**: For research on "optimizer self-evolution," PromptBreeder is the only entry point among the 6—but it runs multiple operators simultaneously, making causal attribution difficult; reproduction requires ablating each component individually.
5. **PROSE is a negative result—do not treat it as a strong method to reproduce**: First run coin-flip's coupling/headroom gate; then discuss selection signal engineering. "Adding a risk term to the fitness function" has already been falsified as yielding no gain.
6. **The only trustworthy cross-method comparison is the same-framework one**: Raw scores from different original papers are not comparable. Any claim that "X is stronger than Y" must be bound to the same model + task + budget; otherwise it is merely an illusion created by each method's own benchmark.

## Related Documents

- Full method-by-method coverage of the seven baseline methods (APE → ProTeGi → OPRO → DSPy → TextGrad → MIPROv2 → GEPA): [apo_seven_methods_primer_20260611.md](apo_seven_methods_primer_20260611.md)
- Side-by-side source and diagnostic framework: [[paper-coin-flip-2026]] ("the brake on whether to optimize at all")
- Critique/trace lineage reference: ProTeGi [[paper-protegi-2023]], TextGrad [[paper-textgrad-2024]], GEPA [[paper-gepa-2026]]
- Joint instruction + demo optimization: [[paper-miprov2-2024]]
- Structured / modular prompt: [[paper-modular-prompt-optimization-2026]]
- Field and evidence criteria: `docs/insight_field_standard.md`
