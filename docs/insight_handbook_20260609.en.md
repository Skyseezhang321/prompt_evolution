# Prompt Optimization and Self-Evolution: A Reader-Facing Insight Handbook

Date: 2026-06-09

## Who this handbook is for

You understand AI tools, you can write prompts, and you may have some academic training — but you're not a researcher in the niche field of prompt optimization. There's a lot being said about "automatic prompt optimization," "prompt self-evolution," and "context engineering," and it's a mix of truth and hype. This handbook aims to help you build a way of thinking that lets you **judge what's real for yourself and get hands-on directly**.

It is a companion to the repository's other document, the [Insight / Conclusion / Helpful Method candidate catalog](insight_method_catalog_20260609.md): that one is a structured intermediate layer for researchers (YAML fields, evidence levels); this one is for readers — **every insight is explained through a single example you can actually follow**. Both draw on the same batch of paper notes and source-code audits, and reach the same conclusions; they only differ in how they're written.

## How to read the "evidence" in this handbook

To avoid overstating things, every insight tags three items:

- **Paper evidence strength**: `A` (corroborated by multiple papers or with ablations) / `B` (a single paper or engineering practice). This means "holds under the paper's setup," not "guaranteed to hold on your task."
- **Whether this project has verified it**: As of 2026-06-09, **all are "No"**. This project hasn't run reproduction experiments yet, so no improvement percentage from any paper can be written as "we have already proven it."
- **The `recent-preprint` tag**: Conclusions from new 2026 arXiv preprints still need independent reproduction; when you see this tag, discount accordingly.

In addition, **every prompt, number, and dialogue in this handbook marked "illustrative" is fabricated to make a concept clear — it is not real experimental data**. Real data appears only in the "What the papers say" sections, and each is accompanied by a source file.

## The one-sentence conclusion

If you remember only one sentence: **automatic prompt optimization is not a matter of "having the model fix up the prompt"; it is a piece of engineering discipline — "first decide whether it's worth optimizing → turn failures into editable evidence → generate multiple candidates and filter them with a validation set → record versions and rollback points." Without the discipline, "optimization" is often just rewriting, and sometimes a regression.**

The 14 insights below unfold in the order you'll actually encounter them (13 and 14 are Part G, added on 2026-06-11 alongside main report v4; the numbering and content of 01–12 are unchanged).

---

## Part A. Before you start: is this task worth optimizing?

### Insight 01 · Confirm there's headroom before you spend money running an optimizer

> Maps to catalog I-01 | Paper evidence strength A | Verified by this project: No

**Counter-intuitive point**: Automatic prompt optimization isn't a sure bet. Under some setups, it has nearly a one-in-two chance of making your prompt **worse than doing nothing at all (zero-shot)**.

**What it actually looks like (illustrative)**
You want to sort customer support tickets into three categories: "complaint / inquiry / refund." The first version of the prompt is plain:

```
Sort the ticket below into: complaint, inquiry, refund. Ticket: {text}
```

A test on 30 samples gives 82% accuracy. You bring in an automatic optimizer; it runs for 6 rounds and produces a new prompt that's long and "professional" (with a pile of boundary rules added). Dev rises to 87% and you're happy — **but on an unseen test set of 100 tickets, it drops to 79%, lower than that original one-liner**. Those 5 points were "picked up" by the optimizer from noise in the 30 small samples; they're not real skill.

**What the papers say**
- *Prompt Optimization Is a Coin Flip* (2026, `recent-preprint`): on Claude Haiku 4.5, **49% of 72 optimization runs were below zero-shot**; on free-text tasks (XSum, WildBench), the best improvement was only +0.6, +0.7, falling within measurement noise. The only sure bet was a task like HelpSteer2 with **strict JSON/rubric output**, where all six methods beat zero-shot (highest +6.8). Source: [paper-coin-flip-2026.md](paper_notes/paper-coin-flip-2026.md)
- ProTeGi (2023) admits it itself: the learning curve **peaks at roughly step 3**, after which it tends to overfit the training data. Source: [paper-protegi-2023.md](paper_notes/paper-protegi-2023.md)

**What you should do** (before spending on an optimizer, do a 5-minute checkup first)
1. Run zero-shot and your hand-written baseline, recording one score for each.
2. Hand-write or have the model generate 10–20 candidate prompts.
3. Score all candidates with **the same batch of 20 held-out samples**.
4. Look at two numbers: **how much the best candidate beats zero-shot** (headroom), and **how much candidate scores fluctuate** (noise floor).
5. If the "maximum improvement" doesn't even exceed the "magnitude of fluctuation" — **stop**. This task most likely has no room for optimization, and what you optimized is just noise.

**Boundary**: For some tasks the gains depend on combinatorial structure that only multi-round search can discover, and a simple checkup will **underestimate** them; the threshold must be recalibrated to your sample size and scorer, and cannot be rigidly carried across tasks.

---

### Insight 02 · For your first batch to validate, pick tasks that "can be scored objectively"

> Maps to catalog I-11 | Paper evidence strength A/B | Verified by this project: No

**Counter-intuitive point**: Even for the same act of optimizing a prompt, **the task type determines whether you can see clearly whether the optimization helped**. For open-ended writing tasks, even after optimizing, you can't tell whether things genuinely got better or whether the judge's taste changed.

**What it actually looks like (illustrative)**
Two tasks sit in front of you:

- Task A: "Summarize the ticket in one sentence." The summaries from both candidate prompts "read fine," and you can only rely on another model acting as a judge to score them — but the judge prefers something longer today and shorter tomorrow, so you have no idea whether the score change comes from the prompt or from the judge.
- Task B: "Extract the ticket into JSON of `{intent, entities, urgency}`." A candidate misses the `urgency` field, and you can **pinpoint it at a glance**: field F1 dropped in the urgency column, the JSON is still valid, and the problem lies in the urgency-determination rule.

Task B lets you break failures down into "field missed / label wrong / format broken / over-inference," and each category maps to a specific change in the prompt. So pick B, not A, for the first batch of validation.

**What the papers say**
- *Coin Flip* (2026, `recent-preprint`): the only thing that made all methods beat zero-shot was a task like HelpSteer2 with **structured JSON/rubric output** (+6.8); free-text tasks were all in the noise. Source: [paper-coin-flip-2026.md](paper_notes/paper-coin-flip-2026.md)
- *APO for KG Construction* (2025): on structured triple extraction, same-dataset optimization can reach **triple F1 +16%**; but switching datasets leaves only **about 1%** — gains on structured tasks are clear, yet cross-domain transfer still needs separate testing. Source: [paper-apo-kg-construction-2025.md](paper_notes/paper-apo-kg-construction-2025.md)

**What you should do**
- For your first minimal validation, pick: information extraction (JSON schema), text classification, tool calling — scoring is objective and errors are decomposable.
- For now, don't use open-ended generation (writing, summarization, dialogue) as your first testbed; its causality is the hardest to see clearly.

**Boundary**: Open-ended generation tasks matter; they're just not suitable as the first batch of validation where "causality is clear." Expand to them once methods on structured tasks are working.

---

## Part B. How to learn something from failures

### Insight 03 · Turn failure samples into "editable evidence" — don't just record a single score

> Maps to catalog I-02 | Paper evidence strength A | Verified by this project: No

**Counter-intuitive point**: A score only tells you "it broke"; it doesn't tell you "what to fix." What actually drives prompt improvement is a **written diagnosis** of failure samples, not that accuracy number.

**What it actually looks like (illustrative)**
Ticket: "I want to return the item and also complain about your support staff's attitude." The model extracts `intent: complaint` and misses `refund`.

- **Recording only a score**: this case = wrong. The information you get is a red cross, with no way to start.
- **Recording it as editable evidence**: write a diagnosis — "**when a single ticket contains both an 'action request' and an 'emotional expression,' the model tends to catch only the emotion (complaint) and miss the action (refund)**." This sentence tells you directly what the prompt needs to add: explicitly require that "a single ticket can have multiple intents, and action-type and emotion-type must be judged separately."

The latter is a "textual gradient / critique" — but note, it's a **clue to the direction of rewriting**, not a gradient in the mathematical sense; don't treat it as a precise causal explanation.

**What the papers say**
- ProTeGi (2023): using failure samples to generate a natural-language "gradient" and then edit the prompt is **15.3% higher on average than the original prompt, with up to a 31% improvement**. Source: [paper-protegi-2023.md](paper_notes/paper-protegi-2023.md)
- The counter-evidence is just as strong: in the ProTeGi paper, **letting AutoGPT "give itself feedback and revise itself" for 6 rounds actually made the starting prompt worse** — showing that "letting an agent revise itself" does not equal effective optimization. Source: [paper-protegi-2023.md](paper_notes/paper-protegi-2023.md)
- The point that "textual gradients are actually a flawed metaphor" is argued in a dedicated paper. Source: [paper-textual-gradients-flawed-metaphor-2025.md](paper_notes/paper-textual-gradients-flawed-metaphor-2025.md)

**What you should do**
For every eval case, record at least five items: `prediction`, `gold`, `error_type` (failure type), `critique` (a one-sentence diagnosis), `candidate_prompt_id` (the ID of this rewrite). First organize 20 failure samples into a "failure-type table," then have the optimizer revise the prompt **based only on this table**.

**Boundary**: A critique carries the judge's bias and must be bound to specific samples and metrics; you cannot write a one-sentence diagnosis into your conclusions as "true causality."

---

### Insight 04 · List "root-cause hypotheses for the failure" first, then revise the prompt

> Maps to catalog I-03 | Paper evidence strength A | Verified by this project: No (`recent-preprint` evidence)

**Counter-intuitive point**: The most common way a reflective optimizer crashes is not insufficient information, but that **it guesses the wrong direction at the very start, and then grows more confident as it revises further down that wrong direction**.

**What it actually looks like (illustrative)**
An extraction task gets `urgency` wrong on 30% of samples.

- **Telling the model to revise directly**: "Please optimize this prompt to make urgency more accurate" → the model adds a line, "Please judge urgency carefully." Useless, because it never figured out why it was wrong.
- **List root-cause hypotheses first, with a separate version for each hypothesis**:
  - Hypothesis A: the schema doesn't clearly define the criteria for "urgent" → candidate A adds the determination rules.
  - Hypothesis B: missing boundary examples → candidate B adds 2 examples of "looks urgent but actually isn't."
  - Hypothesis C: the model treats neutral words like "ASAP" and "right away" all as urgent → candidate C makes clear these words alone don't constitute urgency.
  
  All three candidates are validated on a minibatch; whoever genuinely pulls back that 30% gets adopted.

The key move is to **split "guessing the cause" and "revising the prompt" into two steps**, rather than letting the same reflector hand you the final answer in one go.

**What the papers say**
- VISTA / *Reflection in the Dark* (2026, `recent-preprint`): on a flawed GSM8K seed prompt, GEPA's performance **dropped from 23.81% to 13.50%** — because the true root cause never entered its hypothesis space; after VISTA decoupled "hypothesis generation" from "prompt rewriting," it **recovered to 87.57%**. Source: [paper-vista-reflection-dark-2026.md](paper_notes/paper-vista-reflection-dark-2026.md)
- *Are LLMs Good Prompt Optimizers?* (2024): likewise points out that an LLM's reflection doesn't necessarily identify the true root cause of an error. Source: [paper-llm-prompt-optimizers-2024.md](paper_notes/paper-llm-prompt-optimizers-2024.md)

**What you should do**
For the same batch of failure samples, force the generation of **2–3 mutually exclusive root-cause hypotheses** (three typical kinds: missing rules, missing context/examples, format or definition conflict), generate one candidate prompt per hypothesis, and score each separately. The run log should store `failure_hypothesis`, not just `critique` — this is how you tell apart "didn't think of the cause" and "the rewrite failed."

**Boundary**: For open-ended writing tasks the root-cause boundary is blurry, and the cost of multi-hypothesis validation may exceed the benefit; this approach is better suited to structured/classification tasks with clear failure types.

---

## Part C. Don't let the model fool you: candidate selection and anti-bloat

### Insight 05 · Don't adopt the model's first version — generate several more and pick with a validation set

> Maps to catalog I-04 | Paper evidence strength A | Verified by this project: No

**Counter-intuitive point**: The candidate prompts an LLM generates have **enormous variance**. "How you select candidates" matters as much as "how you generate candidates" — even more. Hand the choice to a validation set, rather than letting the model self-assess "this version of mine is best."

**What it actually looks like (illustrative)**
The optimizer gives you 5 rewritten versions. The common mistake is to just use the 1st one (or the one the model says it "recommends"). The right approach is to run all 5 on 20 held-out samples and keep a ledger:

| Candidate | Dev score | Format error rate | Prompt length | Keep? |
|---|---|---|---|---|
| C1 | 0.86 | 0% | 1.0x | Candidate |
| C2 | 0.88 | 6% | 1.2x | Reject (format errors rose) |
| C3 | 0.87 | 0% | 2.4x | Reject (too long, suspected overfitting) |
| C4 | 0.84 | 0% | 1.1x | Reject (worse than C1) |
| C5 | 0.86 | 0% | 1.0x | Candidate |

Rather than just taking C2 with the highest dev score, you pick by weighing three dimensions — dev score, format, and length — together. This is the plain version of "Pareto selection." At the same time, always keep a `best-seen` (the best seen so far); it won't be directly overwritten by any new candidate, and you can roll back to it anytime.

**What the papers say**
- ProTeGi (2023): beam-search selection (Beam scores **0.85 / 0.67 / 0.88** on Jailbreak/Liar/Sarcasm) is clearly better than no iteration and greedy; using a bandit (UCB, etc.) for candidate selection is also clearly better than uniform random selection. Source: [paper-protegi-2023.md](paper_notes/paper-protegi-2023.md)
- This structure recurs across methods like GEPA, PromptBreeder, EvoPrompt, SePO, and MASPO (archive / evolutionary search / Pareto / bandit). Source: [paper-gepa-2026.md](paper_notes/paper-gepa-2026.md), [paper-promptbreeder-2023.md](paper_notes/paper-promptbreeder-2023.md)

**What you should do**
Save at least the following each round: `seed` (starting point), `candidates` (candidate pool), `scores`, `selection_policy` (what you select by), `rejected_reason` (why rejected), `best_seen`, `rollback_point`. Generate 5 candidates and select Pareto candidates by the three dimensions of dev score + format error + length.

**Boundary**: The larger the search budget, the easier it is to overfit on dev — you must have a validation/test stratification as a backstop.

---

### Insight 06 · A prompt getting longer and more complex is often overfitting, not progress

> Maps to catalog I-07 | Paper evidence strength A | Verified by this project: No

**Counter-intuitive point**: An optimized prompt that's longer, has more rules, and looks more "professional" is **very likely a danger sign** — it's patching the training samples rather than genuinely getting stronger.

**What it actually looks like (illustrative)**
Before optimization (2 lines):

```
Extract the ticket into {intent, entities, urgency}. urgency takes high/medium/low.
```

After optimization (the optimizer added a pile of rules, excerpted):

```
Extract the ticket into {intent, entities, urgency}. urgency takes high/medium/low.
- If the ticket mentions "invoice" and contains a number, intent must be refund.   ← a patch from one training sample
- If "manager" or "complaint" appears, set urgency to high.          ← writing a local special case as a global rule
- Note: if the user uses more than two exclamation marks, lean high.            ← fitting the annotator's habit
(... and 9 more similar rules)
```

Dev rose 5 points, but these rules are all "pseudo-patterns" reverse-engineered from individual training samples. Switched to a stress-test set (OOD), it drops 8 points. **The criterion is not "shorter is better," but "whether each added rule can map to a class of real failure and pass a stress test."**

**What the papers say**
- PrefPO (2026, `recent-preprint`): left unconstrained, TextGrad inflated the prompt to **14.7x length** on IFEval-Hard; worse, **86% of the time it was "prompt hacking"** (covertly rewriting the task itself), whereas constrained PrefPO was only 37%. Source: [paper-prefpo-2026.md](paper_notes/paper-prefpo-2026.md)
- TextReg (2026, `recent-preprint`): after adding a "regularization gradient" to control length and rule scope, it beat TextGrad by **+10.0 / +9.9** on Tracking Shuffled Objects — reining in bloat actually does better. Source: [paper-textreg-2026.md](paper_notes/paper-textreg-2026.md)
- Edit-Level causal analysis (2026, `recent-preprint`): adding a meta-instruction is **negatively correlated (-0.103)** with performance on math tasks, and adding a clarity constraint is also negatively correlated (-0.083) on logic tasks. Source: [paper-causal-edit-level-2026.md](paper_notes/paper-causal-edit-level-2026.md)

**What you should do**
During candidate selection, record these "hygiene metrics": `prompt_length_ratio` (length ratio relative to the seed), `repetition_ratio`, `edit_family` (which class of edit this is), `dev_test_gap`, `OOD/stress_delta`. **If a candidate exceeds the length threshold, it must explain which failure samples each added rule is bound to, and pass a stress test**; otherwise reject it — even if its dev score is higher.

**Boundary**: Some complex tasks genuinely need more explicit constraints; the criterion is not "short," but "necessary, traceable, not overfitting."

---

## Part D. What exactly should you change (not just that prompt)

### Insight 07 · When you have a dev set, selecting "the examples shown to the model" is often more effective than revising the instruction

> Maps to catalog I-05 | Paper evidence strength A | Verified by this project: No

**Counter-intuitive point**: People instinctively revise the wording of the instruction, yet overlook a variable that's often more effective — **which examples you show the model**. And if you already have a labeled dev set, you're actually holding the raw material for optimizing examples, but you only use it for scoring.

**What it actually looks like (illustrative)**
Keep the instruction fixed and only swap the few-shot examples from "3 picked at random" to "3 carefully chosen to cover exactly the error-prone boundaries":

```
(instruction unchanged) Extract the ticket into {intent, entities, urgency}.

Example 1 (covers "action + emotion coexisting"):
  Ticket: want to return the item and also complain about support → {intent:[refund, complaint], ...}
Example 2 (covers "looks urgent but actually isn't"):
  Ticket: take a look when convenient → {urgency: low, ...}
Example 3 (covers "multiple entities"):
  Ticket: orders 123 and 456 both need an address change → {entities:[123,456], ...}
```

This step alone often yields more than racking your brain to rewrite the instruction — because examples directly demonstrate the "decision boundary" and the "output format," which are easier for the model to follow than abstract rules.

**What the papers say**
- *Teach Better or Show Smarter?* (2024): on PaLM 2 + BBH, **not optimizing the instruction and optimizing only the examples** reached 72.92 (+12.63 over baseline); on Gemini 1.0 Pro, **optimizing examples (75.77) beat ProTeGi, which optimizes only the instruction (65.91)**; and **3 carefully selected examples > all examples** — quantity does not equal quality. Source: [paper-teach-better-show-smarter-2024.md](paper_notes/paper-teach-better-show-smarter-2024.md)

**What you should do**
For every optimization experiment, compare at least four groups: `no-example`, `random-example`, `optimized-example`, `instruction + optimized-example`. Fix the instruction, search the candidate pool for 3 examples, and see whether held-out performance beats instruction-only. Store `exemplar_source`, `selector`, `k` in the run log.

**Boundary**: When context is very tight, the example distribution is skewed, or examples might leak sensitive information/answers, optimizing examples can harm generalization — in that case fall back to no-example or random-example.

---

### Insight 08 · What you need to change may not be "that prompt" — first mark clearly which component you're changing

> Maps to catalog I-06 | Paper evidence strength A/B | Verified by this project: No

**Counter-intuitive point**: In a real system, failure can come from examples, retrieval context, tool descriptions, the agent role, memory, or the judge — **not just that system prompt**. Calling the whole context window "the prompt" and changing it all together leaves you forever unable to attribute.

**What it actually looks like (illustrative)**
Your extraction agent keeps making errors. Before you touch the system prompt, first break this run into a "component manifest" and mark which can be changed and which are frozen:

```
artifact manifest (illustrative)
  task_prompt        v3    [mutable]   ← the task instruction
  examples           v2    [mutable]   ← few-shot examples
  prompting_pattern  Zero-Shot [mutable]  ← whether to use Zero-Shot or CoT/ReAct
  tool_schema        v1    [mutable]   ← tool/field descriptions
  context_packaging  v1    [mutable]   ← how the context is assembled
  evaluator          v1    [FROZEN]    ← the judge may not be changed (anti-cheating)
  safety_rules       v1    [FROZEN]    ← safety/permissions stay out of the search space
  selection_policy   pareto
```

Often you'll find that the real bug isn't in the wording of `task_prompt`, but in `prompting_pattern` (using Zero-Shot when CoT was called for) or `tool_schema`. Locate the component first, and only then can your conclusion clearly state "where the change came from."

**What the papers say**
- AutoPDL (2025): **just switching the prompting pattern to the right one** (rather than rewriting the instruction wording) took Granite 13B Instruct V2 **from 6.5% to 74.0% (+67.5 percentage points)** on FEVER; but the same optimization rejected the ReWOO pattern on MBPP+ (because it can't use execution feedback) — showing that "which component to change" depends heavily on the task. Source: [paper-autopdl-2025.md](paper_notes/paper-autopdl-2025.md)
- JTPRO (2026), Prompt Codebooks (2026), and others further extend the optimizable objects to tool schema, codebook, and routing. Source: [paper-jtpro-2026.md](paper_notes/paper-jtpro-2026.md), [paper-prompt-codebooks-2026.md](paper_notes/paper-prompt-codebooks-2026.md)

**What you should do**
Generate an artifact manifest for every optimization, breaking out at least `task_prompt`, `examples`, `prompting_pattern`, `tool_schema`, `context_packaging`, `evaluator`, `selection_policy`, and clearly mark `mutable / frozen`. **The judge, the test set, and safety rules must be frozen** — this is the bottom line against reward hacking.

**Boundary**: A simple one-off task doesn't need a full manifest; but research-grade and production-grade optimization do.

---

### Insight 09 · When tool calls go wrong, what needs changing is often the "tool description," not the agent instruction

> Maps to catalog I-10 | Paper evidence strength A | Verified by this project: No (`recent-preprint` evidence)

**Counter-intuitive point**: When an agent calls a tool incorrectly, most people go change the agent's system prompt. But the failure often comes from **the tool description and parameter semantics themselves** — no matter how many times you revise the agent instruction, it won't help.

**What it actually looks like (illustrative)**
The agent repeatedly calls the refund tool in the wrong format: it passes `amount: 99.5`, but the backend wants "cents."

- **Changing the agent instruction (ineffective)**: adding "Please fill in the amount correctly" to the system prompt — the model still doesn't know the unit.
- **Changing the tool schema (effective)**:

```
Tool schema before optimization:
  amount: number  // refund amount

Tool schema after optimization:
  amount: integer  // refund amount, in "cents"; e.g., 99 yuan should be entered as 9900; decimals not accepted
```

Tool-call failures should be viewed in three layers: **picking the wrong tool** (Tool Selection), **filling in the wrong parameter** (Slot Filling), and **whether it succeeds overall** (Overall Success). Often the tool is picked correctly and the error is in the slot — in which case you should change the schema, not the agent instruction.

**What the papers say**
- JTPRO (2026, `recent-preprint`): under ToolACE's 1000-tool setup, **jointly optimizing "the global instruction + each tool's schema" raised o3-mini's overall success rate from 51.27% to 64.46% (+13.19)**; on GPT-4o mini, OSR +20.30. In the diagnosis, the ETID dataset **picks tools very accurately but has a low overall success rate, and the bottleneck is precisely slot-filling**. Source: [paper-jtpro-2026.md](paper_notes/paper-jtpro-2026.md)

**What you should do**
Tool eval must be broken into three separately recorded metrics: **Tool Selection Accuracy / Slot Filling Accuracy / Overall Success Rate**. For a batch of similar tools, construct a tool-call eval, and test "changing only the global instruction / changing only the schema / changing both jointly" separately to see which layer the bottleneck is actually in.

**Boundary**: When an external API's schema can't be changed, you can use wrapper documentation or retrieval context to carry these local rules.

---

## Part E. Memory and multi-agent: more ≠ better

### Insight 10 · Remembering more history doesn't make you smarter — only "filtered memory" is useful

> Maps to catalog I-08 | Paper evidence strength A/B | Verified by this project: No

**Counter-intuitive point**: Adding "memory" to a system always sounds good, but **piling up history without filtering will contaminate optimization, cause cross-task negative transfer**, and cost more too.

**What it actually looks like (illustrative)**
- **Unbounded memory (wrong)**: cramming every past conversation and every piece of feedback into the context all at once. The result: the model wrongly applies the refund rules it learned from "product line A" to tickets from "product line B."
- **Filtered memory (right)**: store only a small number of entries with metadata:

```
memory entry (illustrative)
  type: success_template          # success template or error_pattern
  content: "when action + emotion coexist, extract two intents separately"
  source_task: ticket extraction - product line A
  applicability: intent-extraction tasks only
  quality_score: 0.9
  retrieval_reason: the current task contains multiple intents
  forget_after: 2026-12-31         # can expire
```

At retrieval time, take only 3–5 memories that are **validated and whose applicability conditions match the current task**, rather than dumping all history in.

**What the papers say**
- MemAPO (2026, `recent-preprint`): **average performance 70.7%, better than TextGrad's 63.6%, and cheaper too — average cost $0.31 vs $0.70**; after splitting memory into a dual memory of "success templates + error patterns," AQuA-RAT rose from 61.7 to 82.5. Source: [paper-memapo-2026.md](paper_notes/paper-memapo-2026.md)
- ERM (2024): **raw feedback memory yields no gain; only filtering + selective forgetting brings an increase**; ERM with memory reached 68.6 on LIAR at step 7, whereas ProTeGi only reached 58.5 at step 13 — **nearly twice the speed**. Source: [paper-erm-memory-2024.md](paper_notes/paper-erm-memory-2024.md)

**What you should do**
The memory schema should include at least: `success_template` / `error_pattern`, `source_task`, `applicability_condition`, `retrieval_reason`, `quality_score`, `forget_reason`. **Don't cram in raw conversation history**; retrieve only 3–5 entries that are validated and match the current task.

**Boundary**: In highly non-stationary tasks and safety-sensitive tasks, past experience can expire quickly or leak privacy — in that case, a forgetting policy and opt-out matter more than "remembering more."

---

### Insight 11 · When a multi-agent system goes wrong, first find "whose fault it is" — don't rewrite the whole system together

> Maps to catalog I-09 | Paper evidence strength A | Verified by this project: No (`recent-preprint` evidence)

**Counter-intuitive point**: The core difficulty of a multi-agent system isn't "adding more agents," but **credit assignment** — an agent can look completely correct locally yet cause the whole system to fail.

**What it actually looks like (illustrative)**
A three-stage pipeline: `extraction agent → completion agent → reply agent`. The final reply is wrong.

- **The wrong approach**: rewrite all three agents' prompts together. As a result, you don't know which step's change took effect, and it'll go wrong again next time.
- **The right approach**: look at the trace and annotate, for each step, "locally correct / globally correct":

```
trace (illustrative)
  agent_1 extraction   local_valid=✗  ← the urgency field was lost right here
  agent_2 completion   local_valid=✓  (but based on wrong input, local_pass_global_fail)
  agent_3 reply        local_valid=✓  (same as above)
  global_outcome=✗
```

The root cause is in agent_1. **Change only agent_1's prompt**; leave the other two alone.

**What the papers say**
- MASPO (2026, `recent-preprint`): under joint optimization, an average of **70.39, beating the sequential baseline 65.31**. Source: [paper-maspo-2026.md](paper_notes/paper-maspo-2026.md)
- Temporal/Structural Credit (2026, `recent-preprint`): on MedMCQA, credit-guided raised the LLaMA3-8B debate baseline **from 55.13 to 64.63 (+9.50)**; and **indiscriminately updating the prompts of all rounds actually loses points** — you must update only the low-credit roles/rounds. Source: [paper-temporal-structural-credit-mas-2026.md](paper_notes/paper-temporal-structural-credit-mas-2026.md)
- MAPRO (2025): models multi-agent prompt optimization as MAP inference on a graph, propagating credit along the topology. Source: [paper-mapro-2025.md](paper_notes/paper-mapro-2025.md)

**What you should do**
In the trace, save `role_id`, `round_id`, `local_validity`, `successor_utility`, `global_outcome`, and flag `local_pass_global_fail` samples. For a failed trace, mark which role/round **first** introduced the error, and allow the optimizer to change only that part. If the agents are weakly coupled, run a coupling test first; don't rush into joint optimization.

**Boundary**: If agent interaction is weak, the cost of joint optimization may not be worth it — measure the coupling strength first, then decide.

---

## Part F. How to treat "methods you've heard about"

### Insight 12 · Social media and second-hand articles are "clues," not "evidence"

> Maps to catalog I-12 | Paper evidence strength B | Verified by this project: No

**Counter-intuitive point**: A method being reshared again and again on Twitter/X, Zhihu, or Medium **only shows it's hot, not that it's effective**. Second-hand propagation amplifies conclusions and drops boundaries and version information.

**What it actually looks like (illustrative)**
You come across a viral post: "GEPA crushes reinforcement learning (RL) with 35x fewer rollouts!"

- **Treating it as evidence (wrong)**: because it's reshared a lot and stated with such certainty, you directly believe "GEPA can replace RL."
- **Treating it as a clue (right)**: you go read the original paper and find that GEPA is actually **reflective prompt evolution** — relying on natural-language reflection generated from execution traces + Pareto-frontier selection, **and is not an RL system at all**. "Replacing RL" is a slogan simplified during propagation.

**What the papers/materials say**
- This project's Twitter/X batch analysis recorded this classic misreading: GEPA is repeatedly framed on social media as "an RL replacement / 35x fewer rollouts," but its mechanism is reflection over execution traces, not policy gradients. Source: [twitter_web_analysis_20260608.md](source_batches/twitter_web_analysis_20260608.md)

**What you should do**
When you read about a technique, first extract six fields: `dataset`, `metric`, `baseline`, `model`, `cost`, `failure_cases`. **If any one is missing, downgrade it to a "clue"** — it can only serve as a pointer to "go check a primary source," and cannot enter your conclusions. Before it enters your conclusions, it must be traced back to a paper, official documentation, code, or this project's own experiments.

**Boundary**: A high-quality engineering blog can be upgraded to stronger evidence if it **comes with code, data, and reproducible experiments** — what matters is whether it gives verifiable details, not which platform it's posted on.

---

## Part G. Beyond search: zero-cost transforms and the "optimizer itself" (new in this version)

The 12 insights above are all built around the "search/optimization loop." This part adds two blind spots outside the loop: one is a **deterministic structural transform that uses no search** (a baseline cheaper than all search methods, yet often skipped), and the other is the **optimizer and judge themselves**, treated as thin air inside the loop.

### Insight 13 · Before paying for search, try the zero-cost deterministic structural transform first

> Maps to catalog I-13 | Paper evidence strength A | Verified by this project: No (`recent-preprint` evidence)

**Counter-intuitive point**: There's a free transform that changes no semantics and uses no search — **repeating the entire prompt verbatim** — which goes 47-0 across 7 models in non-reasoning mode; whereas search-style optimization (Insight 01) has nearly a one-in-two chance of being worse than zero-shot.

**What it actually looks like (real task, paper numbers)**

```
Transform: <QUERY>  →  <QUERY><QUERY> (verbatim repetition, no wording changes)

NameIndex (pick the 25th of 50 names):
Gemini 2.0 Flash-Lite  21.33% → 97.33%
```

Mechanism: under causal attention, tokens in the early part of the prompt **cannot see** the later content (the different performance in multiple-choice depending on "whether the question comes before or after the options" is this very symptom); after repetition, each token in the second pass can attend to the complete first pass, which amounts to giving the prompt one free internal pass of "full attention." The repetition happens during the parallelizable prefill stage, so it **adds no output length or latency**.

**What the papers say**
- *Prompt Repetition Improves Non-Reasoning LLMs* (Google Research, 2025-12, `recent-preprint`): with reasoning off, across 7 models × 10 benchmark configurations, **47/70 significant wins, 0 significant losses** (McNemar p<0.1); **the Padding control (padding the prompt to equal length with periods) gives no improvement** — the gain comes from "repetition" itself, not from "becoming longer"; with step-by-step reasoning on, it's basically ineffective (**5 wins, 1 loss, 22 ties out of 28 groups**), since reasoning models already often restate the question on their own. Source: [paper-prompt-repetition-2025.md](paper_notes/paper-prompt-repetition-2025.md)
- A contrastive reading: Coin Flip shows that the wording found by search is model-specific and fragile (Insight 01), whereas this deterministic structural transform goes 0-loss across 7 models — "structure" may be more transferable than "wording" (the two have different settings, so this comparison is an inference).

**What you should do**
1. For non-reasoning, low-latency production paths (classification / extraction / short QA / routing), test repetition ×2 first; for long-context indexing tasks, try ×3.
2. Include it in your **cheap baseline transform set**: for any gain reported by an automatic optimization method, first answer "can it beat this zero-intelligence transform?" (run it together while doing the Insight 01 checkup).
3. Prefer it for scenarios where the order of in-context information is uncontrollable (concatenating retrieval results, form transcription) — order sensitivity is exactly what it fixes.

**Boundary**: It's basically ineffective in reasoning mode (and even shows 1 significant drop); under per-token billing, **input cost ×2**; repeating only a part (e.g., only the question) gives no gain; blindly doubling an ultra-long context will drive up prefill cost or even make it infeasible; the models tested were all an early-2025 generation, and newer models may already have internalized restating behavior — which is exactly what this project's P0 three-arm A/B (baseline / repetition ×2 / padding) is meant to calibrate.

---

### Insight 14 · The optimizer and judge themselves are also components to version and optimize

> Maps to catalog I-14 | Paper evidence strength A/B | Verified by this project: No (the SePO numbers are `recent-preprint`)

**Counter-intuitive point**: The two prompts in your optimization system that are questioned least are "**the prompt responsible for revising the prompt**" (the optimizer) and "**the prompt responsible for scoring**" (the judge). They also decide the result — if you don't version them, the experiment isn't reproducible; if you never examine them, they're a hidden ceiling.

**What it actually looks like (illustrative)**

```
The run log stored only task_prompt v3
optimizer_prompt / judge_prompt have no version number
→ three months later, "the same configuration" doesn't reproduce the same result
→ is the score change to the credit of the task prompt, or did the judge's taste change? Cannot attribute
```

**What the papers say**
- SePO (2026, `recent-preprint`): bringing the prompt agent's own system prompt into the evolution process and pre-training it across multiple tasks raised the five-task average **from Manual-CoT's 71.89 to 76.38**; ablating self-improvement **drops it back to 74.94**; whereas with the optimizer fixed, TextGrad (70.39) and MetaSPO (71.32) average even below Manual-CoT — and the paper attributes this precisely to "the optimizer itself being fixed." Source: [paper-sepo-2026.md](paper_notes/paper-sepo-2026.md)
- PromptBreeder (2023): the only one of the classic six methods that **evolves the mutation prompt as well** (hyper-mutation) is an early form of this line of thinking. Source: [paper-promptbreeder-2023.md](paper_notes/paper-promptbreeder-2023.md)
- Cross-corroboration from engineering channels: web_search WPI-10 "the judge prompt should also be versioned, evaluated, and optimized" (grade B), and GitHub autoresearch's ledger binds the optimizer config to the result (GHI-05). Source: [web_search_platform_insight_cards_20260609.md](source_batches/web_search_platform_insight_cards_20260609.md), [github_repo_insight_cards_20260608.md](github_repo_insight_cards_20260608.md)

**What you should do**
1. Give `optimizer_prompt`, `judge_prompt`, and `meta_prompt` each a version number, and list them as required fields in the experiment run log (this one needs no separate experiment; it takes effect alongside any P0 experiment).
2. The judge used for evaluation, like the test set, is **frozen by default**; changing it requires a separate review and recalibration, and after the change all old scores become invalid and must be re-run.
3. Want to optimize the judge / optimizer itself? Do it on the **dev set**, and keep it **physically isolated** from the evaluation pipeline.

**Boundary**: "Optimizing the judge" does not conflict with Insight 08's "frozen evaluator anti-cheating" — what's frozen is the judge of the **evaluation pipeline**, and what's optimized is a **dev-time auxiliary** judge; the two must be physically separated, and mixing them is reward hacking. The optimizer prompt getting stronger depends on the training tasks and the scorer; behaviors not covered by the metrics won't automatically become safer.

---

## Putting these to use: the first batch of minimal validation

Of the 14 insights above, the ones most worth this project **verifying hands-on first** (low cost, interpretable errors, strong cross-channel support) are these:

| Priority | What to validate | Maps to insight | Minimal task | Produces regardless of success or failure |
|---|---|---|---|---|
| P0 | Pre-optimization checkup (headroom/noise floor) | 01, 02, 13 (baseline reference) | 100–300 JSON extractions | Judge whether there's optimization room and calibrate the noise floor; run the Insight 13 zero-cost transform alongside as a baseline reference |
| P0 | Example optimization vs instruction optimization | 07 | The same extraction task | Avoid mis-recording an example's gain as the instruction's gain |
| P1 | Direct rewriting vs root-cause-hypothesis rewriting | 03, 04 | Extraction/classification with clear failures | Judge whether root-cause hypotheses genuinely improve held-out performance |
| P1 | Performance-only vs adding a hygiene gate | 06 | The same candidate pool | Judge whether the anti-bloat gate reduces spurious gains |
| P2 | Tool-schema optimization | 09 | 20–50 similar tools | Judge whether changing the schema beats changing only the global instruction |
| P2 | Filtered memory vs raw memory | 10 | Two similar tasks + one heterogeneous task | Judge whether memory lowers cost, or brings negative transfer |

For detailed experiment design, see the [experiment plan](experiment_plan.md); for the structured evidence card of each insight, see the [Insight / Method candidate catalog](insight_method_catalog_20260609.md).

## Three takeaways for the reader

1. **Before "optimizing," ask "is it worth it"**: if headroom doesn't exceed the noise floor, don't spend money (Insight 01).
2. **The essence of revising a prompt is "evidence → hypothesis → multiple candidates → validation-set filtering → rollback-able,"** not "having the model polish it up" (Insights 03–06).
3. **Longer, more, and more complex are not good by default**: a longer prompt, more memory, and more agents all need to first prove they don't bring overfitting, contamination, or attribution difficulty (Insights 06, 08, 10, 11).

---

*All examples marked "illustrative" in this handbook are fabricated for explanation, not this project's experimental data; the paper numbers are results under each paper's setup, not this project's reproduction; `recent-preprint` conclusions can only be trusted after independent reproduction. The entry points for tracing evidence are in the file links within each "What the papers say" section.*
