# Don't Let AI Grade Its Own Homework

> The story of a startup team learning to "tame the prompt" — a popular-science story, adapted from [Cross-Channel Synthesis Report v4](./analysis_report_v4_20260611.html).
>
> **A note before you read**: the people, the company, the support tickets, and the dialogue in this story are all **fictional**, used to make the lessons fun to follow; the **paper numbers that appear in the story are real** (drawn from genuine research cited in the report). At the end there's a "story ↔ real evidence" cross-reference table, so sticklers can trace everything back to the original report and the paper notes.

---

## Prologue: One Sentence That Made Old Guo Frown

Yunti Tech had only eleven people, yet it had landed what looked like a respectable gig: building a customer-service AI for a chain home-appliance brand.

The product was called "Xiaomi." When a user vented a complaint on the brand's official account, Xiaomi had to read that ticket within half a second and spit out three things:

- **intent** (what the user wants: complaint / inquiry / refund…)
- **entities** (which orders, which products are involved)
- **urgency** (how urgent it is)

Get them right, and the ticket is auto-routed to the right person. Get them wrong, and a customer who wants to return a product gets dumped into the "inquiry" queue, sits ignored for three days, and then takes it to Weibo.

That morning's standup, the boss, Diana, slapped a chart up on the big screen: two weeks after launch, Xiaomi's accuracy was stuck at 82%, and the client was already getting passive-aggressive.

"This week, get me above 90%."

The room went quiet for two seconds. Then the product manager, Xiaoman, raised her hand—she was really half an engineer, and loved tinkering with new tools.

"That's easy," she said. "Aren't there those tools now that **automatically optimize prompts**? I'll feed ours in, let it run overnight, and by tomorrow morning it'll be fixed. Let the AI fix the AI's homework—how convenient is that."

Sitting in the corner, forty-five years old, ten years of search and recommendation behind him, Old Guo lifted his eyelids from behind his thermos and said, slowly:

"Sure. But first answer me one question—**how will you know it actually got better, instead of just looking better?**"

Xiaoman had no comeback.

That was the beginning of the story. Over the next full quarter, through one wreck after another, they broke that one question down into fourteen smaller ones.

---

## Chapter 1 The Checkup: Is This Job Even Worth Optimizing?

Xiaoman went ahead and ran it her way anyway. She grabbed an open-source optimizer, dropped Xiaomi's prompt in, and set it to "run 6 rounds, score 30 tickets per round, and keep the highest-scoring one."

The next morning, she reported excitedly:

"It worked! The new prompt is long and professional, **dev-set accuracy went 82% → 87%**, up 5 points!"

Old Guo didn't applaud. He did something to spoil the mood: he took that 87% new prompt and ran it on a batch of **100 fresh tickets that had never been part of the optimization**.

The number on the screen was **79%**.

Lower than the plain old 82% they'd started with.

"Those 5 points you gained," Old Guo said, "were scavenged out of the noise of a 30-ticket sample. The optimizer didn't learn the task—it memorized the answers to those 30 questions."

Xiaoman was a little dazed: "Automatic optimization… can actually make things *worse* the more you optimize?"

Old Guo turned his computer around and showed her a 2026 paper (codename Coin Flip). The researchers ran **72** automatic optimizations, and the result was spine-chilling:

> **49%** —— nearly half of the optimization results were *worse* than doing nothing at all (zero-shot). Same odds as flipping a coin.

"So **automatic optimization is not a sure bet**," Old Guo said. "There's roughly a fifty-fifty chance it makes your prompt worse. Last night, you got lucky and landed on the bad half—and thought you'd come out ahead."

He wrote the first rule on the whiteboard:

> **Insight 1: Do a checkup before you do anything.** Don't blow money running an optimizer right out of the gate. First measure two things—
> - **Headroom**: how much higher is the best candidate than zero-shot?
> - **Noise floor**: across a few candidates, how much do the scores jitter on their own?
>
> **If the headroom doesn't exceed the noise floor, stop—don't optimize.** The "gain" you're seeing is probably just jitter.

Xiaoman wasn't convinced: "But surely there's *some* task that can be optimized well?"

"There is," Old Guo said, "but **you have to pick the right task**." He pointed at the three things Xiaomi had to do.

"'Summarize the ticket into one sentence'—open-ended writing like that, how do you even score it? You can only call in another model to be the judge. The judge thinks A is better today, B is better tomorrow; when the score changes you have no idea whether the prompt actually got better or the judge's taste just shifted."

"But 'extract a {intent, entities, urgency} JSON' is different. If urgency gets dropped, that column's score **drops on the spot**, and you can pry the failure apart: was it a missed extraction, a mislabel, broken format, or over-inference? **The cause is clear.**"

That Coin Flip paper backs this up too: of the six optimization methods, the only task where **all of them beat zero-shot** happened to be a structured JSON extraction task (gain +6.8).

> **Insight 2: For your first batch, pick a task you can score objectively.** Information extraction, classification, tool calls—failures can be decomposed and the cause is clear. Open-ended writing matters, but don't make it your first proving ground—you'll be dragged around by the judge's taste.

Xiaoman re-sorted Xiaomi's three jobs: hammer on "extract the JSON" first, push "summarize into one sentence" to later.

This was the first thing they learned: **before you optimize, prove the job is worth optimizing and that you can see the effect clearly.**

---

## Chapter 2 Turn Failures Into Evidence, Not Just a Red X

With the task chosen, Xiaoman got ready to run the optimizer again. Old Guo stopped her: "This time, don't feed it scores. Feed it **evidence** first."

He pulled out a ticket Xiaomi had gotten wrong at random:

> User's words: "I want to return this, AND file a complaint about your support staff's attitude!"
> The intent Xiaomi extracted: **complaint** (it dropped "refund")

"If you only record 'this one is wrong,'" Old Guo said, "what you get is a red X, a bare score. Holding that red X, you have no idea which line of the prompt to fix."

"But if you record it as a **diagnosis**—" he wrote on a sticky note:

> "When a ticket contains both an 'action request' and an 'emotional vent,' the model grabs only the emotion and drops the action."

"—that sentence tells you directly which rule to add. *That's* the fuel for fixing a prompt."

Old Guo called this "turning failures into editable evidence." He dug up a classic paper (ProTeGi) to back it up: using failure samples to generate sentence-by-sentence textual "diagnoses," then rewriting based on them, beat the original prompt by **15.3%** on average, and as much as **+31%** on the toughest task.

But then he pivoted: "There's a trap here, though."

That same paper has a control experiment: letting an AI agent **reflect on its own and revise itself for 6 rounds** actually made the starting prompt worse and worse. "**The textual 'gradient' is just a metaphor, not a real mathematical gradient.** The model is great at writing a reflection that *sounds* perfectly reasonable, and then, following that wrong reflection, it veers off course with ever-growing confidence."

The intern, Azhe, leaned in and asked a "dumb question": "So how do you stop it from guessing the wrong direction in the first place?"

Old Guo said the question wasn't dumb at all—it's exactly what another 2026 paper (VISTA) called "the dark side of reflection." On a set of inherently flawed seeds, a certain popular reflection-style optimizer dropped from 23.81% **to 13.50%**: it locked onto a wrong root cause and then charged bravely forward in the wrong direction. Only after the researchers forcibly split the two steps of "**guessing the root cause**" and "**rewriting**" did the score recover to **87.57%**.

"So," Old Guo wrote the rule on the whiteboard:

> **Insight 3: Record every failure sample as evidence, not just a score.** For each failure, note: what the model answered, the correct answer, the error type, and one concrete diagnosis. First organize 20 failures into a "failure-type table," then let the optimizer revise **based only on that table**.
>
> **Insight 4: List your "failure root-cause hypotheses" first, then revise the prompt.** Don't let the model guess the cause and revise at the same time. For the same batch of failures, force out 2–3 **mutually exclusive** hypotheses, for example:
> - A: missing a decision criterion → Candidate A: add an urgency decision rule
> - B: missing boundary examples → Candidate B: add two "looks urgent but isn't" examples
> - C: neutral words misjudged → Candidate C: declare that "ASAP/right away" alone doesn't count as urgent
>
> Score the three candidates separately on the validation set, and **use whichever one actually pulls the error rate back down.**

Azhe later turned this whole process into a one-liner and stuck it on his desk: **"The score tells you it's broken; the diagnosis tells you where it's broken."**

---

## Chapter 3 Don't Get Fooled by the Model: How to "Select," and How to Prevent "Bloat"

With evidence and hypotheses in hand, the optimizer this time generated five candidate prompts. Xiaoman's instinct was: pick the one with the highest dev-set score.

Old Guo stopped her again: "**Don't look at just one number.**" He had Azhe lay out the five candidates as a ledger:

```
Candidate  Dev score  Format errs  Length   Keep?
C1         0.86       0%           1.0x     ✔ keep
C2         0.88       6%           1.2x     ✗ drop (highest score, but format errors went up)
C3         0.87       0%           2.4x     ✗ drop (too long, looks like overfitting)
C5         0.86       0%           1.0x     ✔ keep
```

"The highest score is C2, but its format-error rate climbed from 0 to 6%—launch a prompt like that and downstream JSON parsing starts throwing errors. **Looking only at the average score hides that cost.**"

In the end they didn't use C2; they picked by combining all three dimensions—"score + format + length." And Old Guo set an iron rule: **the best-seen prompt always gets stored separately and may never be directly overwritten by a new candidate**—in case the new one is a fake gain, you can roll back at any time.

This approach—"generate several, select with the validation set, and don't let the model self-grade 'this is my best version'"—has numbers in the papers too: the classic ProTeGi uses beam search to select candidates and clearly beat "greedily keep only the current best" on several tasks.

"Now let's talk about why C3 got dropped," Old Guo said, pointing at the candidate that was **2.4× as long**. "**When a prompt gets longer and more complex, nine times out of ten it's not progress—it's overfitting.**"

He showed Xiaoman a few rules the optimizer had added itself inside that dropped candidate:

```
- If "invoice" is mentioned and contains a number, intent is definitely refund    ← this is a patch for one specific sample
- If "manager / complaint" appears, urgency is always high                        ← treating a local exception as a global rule
- More than two exclamation marks → lean high                                     ← fitting the annotators' typing habits
```

"Each one *looks* pretty 'professional,' but really they're all patches on the training samples. Dev +5, then −8 on the stress test."

Papers back this up too, and the numbers are scary. A 2026 paper (PrefPO) found: left unchecked, a popular optimizer could balloon a prompt to **14.7× its length**, and **86%** of the changes were actually **quietly tampering with the task itself** (for example, secretly changing "extract strictly" into "extract as much as possible" to game the score). Another (TextReg) added a "don't bloat wildly" regularization constraint, and the result was **shorter and more accurate**—nearly 10 points higher than the unrestrained version.

> **Insight 5: Don't use the first version—generate several and select with the validation set.** How you "select" matters as much as how you "generate." Each round, record: the seed, all candidates, each one's score, why kept / why dropped, the best-seen, and the rollback point. Hand the choice to the validation set, not to the model's gut feeling.
>
> **Insight 6: A prompt that keeps getting longer is usually overfitting, not progress.** If a candidate has grown longer, it must spell out which failure samples each new rule **corresponds to, and that it survives the stress test**—otherwise reject it outright. The standard is "necessary, traceable, not overfitted," not "the shorter the better."

---

## Chapter 4 Which Screw Should You Actually Turn?

The JSON-extraction accuracy climbed to 86%. Past that, it got stuck.

Xiaoman rewrote that instruction over and over, tweaking the wording again and again, and the score didn't budge. She was getting frustrated: "I've polished this instruction into a work of art!"

Old Guo said something that stopped her cold: "**You've been turning the same screw the whole time. But this machine has several screws.**"

On the whiteboard, he broke Xiaomi down into a "parts list":

```
Task instruction   task_prompt        v3   [editable]
Examples           examples           v2   [editable]
Reasoning pattern  prompting_pattern  zero-shot [editable]  ← the real bug often hides here
Tool description   tool_schema        v1   [editable]
Judge              evaluator          v1   [frozen]  ← the judge may not be touched (anti-cheating)
Safety rules       safety_rules       v1   [frozen]  ← safety/permissions stay out of the search space
```

**The first overlooked screw was "examples."** Old Guo had Xiaoman run a controlled test: don't change a single word of the instruction, just carefully swap in three examples—specifically picking the tricky boundary cases:

```
Ex1 (action + emotion together): wants a return and to complain  → intent:[refund, complaint]
Ex2 (looks urgent but isn't): take a look when convenient        → urgency: low
Ex3 (multiple entities): change address on both orders 123 & 456 → entities:[123, 456]
```

The accuracy moved right away. The papers are crystal clear on this: one study (Teach Better) found that **without changing the instruction at all, optimizing only the examples** raised the score by 12.63 points; and on a different model, "optimizing examples" (75.77) clearly beat "optimizing only the instruction" (65.91)—**picking 3 examples carefully even beat stuffing in all of them.**

"Everyone's instinct is to go change the wording of the instruction," Old Guo said, "but they forget the variable that's often more effective—**which examples you show the model.**"

**The second overlooked screw was "reasoning pattern."** A subtask Azhe owned (judging whether a ticket's statements contradict themselves) had absurdly low accuracy. Old Guo took one look: "You're asking it zero-shot, directly. This task needs it to **reason step by step** before answering." He switched the reasoning pattern without changing a word of the wording.

The paper numbers here are the wildest of all—one study (AutoPDL) found that just **switching the reasoning pattern to the right one** (not rewriting the wording) took a task from **6.5% soaring to 74.0%**, a jump of 67.5 percentage points.

**The third overlooked screw was "tool description."** Xiaomi had to call an "initiate refund" tool, and it kept passing the wrong amount. Xiaoman wrote "please fill in the amount correctly" in the agent instructions—wrote it eight hundred times to no avail, and the model still passed `amount: 99.5`.

Old Guo glanced at the tool's definition and changed one line of comment:

```
amount: integer   // unit is "cents"; 99 yuan should be 9900; decimals not accepted
```

The problem vanished. "**The model isn't disobedient—the tool just didn't state the unit clearly.** You can tweak the agent's system prompt until the end of time and it won't help, because the bug isn't on that screw at all." In the paper (JTPRO), optimizing the "global instruction" and "each tool's description" together raised the overall success rate from 51.27% to 64.46%.

> **Insight 7: When you have a dev set, "changing which examples the model sees" is often more effective than "changing the instruction wording."** At minimum, compare: no examples / random examples / curated examples / optimizing the instruction too. Don't rack your brain fixating only on the instruction.
>
> **Insight 8: First label clearly which "part" you're changing.** For each optimization, lay out a parts list and mark which are editable and which are frozen. **The judge, the test set, and the safety rules must be frozen**—that's the bottom line for preventing the model from "cheating to inflate the score."
>
> **Insight 9: When a tool call goes wrong, what needs fixing is usually the "tool description," not the agent instruction.** Split tool evaluation into "was the choice right / were the parameters filled in right / was it successful overall," recorded separately, so you know which layer the bottleneck is in.

What they learned in this chapter is really one thing: **"optimize the prompt" is too vague a phrase. In a real system, failure can come from examples, the reasoning pattern, the tool description, even the judge—first label clearly which screw you're turning, or you can't even say whether you "fixed it."**

---

## Chapter 5 Memory and Clones: More ≠ Better

Xiaomi's accuracy hit 91%, and Diana finally smiled. But the product needed to head toward "smarter the more you use it," and new requirements came in: give Xiaomi a **memory** so it remembers the old tickets it has handled; then split it into **multiple agents** that divide the work and collaborate.

This time Xiaoman had wised up, but she still fell into two new traps.

**Trap one: memory that records everything.** She had Xiaomi cram all the historical conversations into the context, figuring "the more it remembers, the smarter it is." The result: Xiaomi misapplied product line A's refund rules to product line B's tickets—line A had a seven-day no-questions-asked return, line B's custom items were non-returnable, and it mixed them up.

"**Unfiltered memory isn't an asset, it's a source of contamination,**" Old Guo said. "And it's more expensive—every single time you shove a big lump of history in, the tokens burn like crazy."

The right way is to tag every memory: which task it came from, what its applicability conditions are, what quality score it gets, and when it should be forgotten. At retrieval time, **take only 3–5** that have already been validated and whose applicability conditions match the current ticket.

The paper numbers are persuasive: one study (MemAPO) used a "dual-memory" mechanism that was **both more accurate and cheaper**—70.7% vs 63.6%, cost \$0.31 vs \$0.70. Another (ERM) found that **filtered memory converged nearly twice as fast** (reaching 68.6 by step 7, while raw memory ground on to step 13 to reach only 58.5), whereas unfiltered raw memory **brought essentially no benefit**.

**Trap two: rewrite everything when a multi-agent setup errors.** Xiaomi was split into three agents: "extract → complete → reply." Whenever the final reply was wrong, Xiaoman's instinct was to throw out and rewrite all three prompts.

Old Guo had her look at the trace (execution trajectory) first:

```
Extract agent   locally correct?  ✗  ← urgency was already lost at this step
Complete agent  locally correct?  ✓  (but it's completing based on wrong input—locally right, globally wrong)
Reply agent     locally correct?  ✓
```

"The root cause is at the extraction step. The complete and reply agents **didn't do anything wrong themselves**—they just received the wrong input. If you rewrite all three together, you've executed two innocents, and you might introduce new bugs."

In the multi-agent world this has a proper name: **credit assignment**. The paper (Temporal/Structural Credit) measured it: **updating only the step that actually erred** raised the score from 55.13 to 64.63, while **updating all agents indiscriminately actually lost points**.

> **Insight 10: Only "filtered memory" is useful.** Attach metadata to every memory (source task, applicability conditions, quality score, forgetting condition), and retrieve only the 3–5 that are validated and match the current task. Don't shove whole historical conversations in as one lump.
>
> **Insight 11: When a multi-agent setup errors, find "whose fault it is" first—don't rewrite the whole thing.** In the trace, record for each agent / each round "was it locally correct, did it help what came after, was it ultimately successful," find the step that **first introduced the error**, and change only that piece.

The lesson of this chapter is really the same wisdom as Chapter 4: **locate first, then act. Whether you're turning a screw or finding who's responsible, "precision" always beats "start over from scratch."**

---

## Chapter 6 What You Hear Is a Lead, Not Evidence

As the story neared its end, there was a little episode.

One day Xiaoman came across a viral post with tens of thousands of shares:

> **"GEPA crushes reinforcement learning RL with 35× less compute! The age of self-evolution is here!"**

She rushed excitedly into the meeting room: "Guo! Shouldn't we switch our optimizer entirely to GEPA? It can replace RL!"

Old Guo didn't rush to shoot it down. He did something—**he dug up the original paper that had gone viral and read it through.**

After reading, he said: "GEPA is a **reflection-style prompt-evolution method**—it revises prompts by reading execution trajectories and doing Pareto selection. It **isn't an RL system at all**. The claim of 'replacing RL' is a slogan squeezed out by the spread, after deleting all the boundaries and premises to make it more shareable."

"Popularity only shows it's **widely spread**," Old Guo said, writing the last rule on the whiteboard. "**It doesn't show it's effective, and it certainly doesn't show it can replace anything.**"

> **Insight 12: Social media and secondhand articles are "leads," not "evidence."** When you read a trick/conclusion that excites you, first force yourself to extract six fields: **what dataset it used / what metric / which baseline it compared against / what model / how much it cost / what failure cases there were.** Missing any one, and you downgrade it to a "lead"—before it enters your conclusions, **you must go back and trace it to the firsthand paper, official docs, or code.**
>
> Exception: a high-quality engineering blog that comes with its own code, data, and reproducible experiments can be upgraded to stronger evidence—**look at the details, not the platform.**

Xiaoman later developed a habit: every time she saw a headline like "X crushes Y," she'd silently recite those six fields in her head. Nine times out of ten, the headline mentions not one of them.

---

## Chapter 7 The Dumb Trick and the Red Pen: Two Things They Only Figured Out at the Finish Line

After Xiaomi stabilized at 92%, the team thought they could catch their breath. Then, in the wrap-up phase, two more things popped up that turned the twelve items on the whiteboard into fourteen.

**The first thing was one of Azhe's "slip-ups."**

Xiaomi had a long-context subtask: from a long list of order records, precisely pull out the Nth one. This task's accuracy had been consistently dismal, and several rounds of the optimizer hadn't rescued it.

One day, while copying the prompt, Azhe's hand slipped and he **pasted the entire prompt twice, verbatim** before sending it. He was about to undo it—but the answer that came back… was correct. He tried a few more, still correct.

"I didn't change a single word," he ran over to Old Guo, sounding like he'd seen a ghost. "I just **repeated it once.**"

Old Guo didn't laugh—instead he slammed a Google paper onto the desk: this "dumb trick" has a legitimate mechanism. Models like these read prompts **one-directionally**—the words earlier in line "can't see" the words later in line. When the question is up front and the options are at the back, the model has no idea what's coming when it reads the question. Repeat the whole prompt verbatim, and every word in the second pass can "look back and see" the complete first pass.

The paper's numbers are quite scary: in the setting with reasoning mode off, across 7 mainstream models × 10 task configurations, **47 configurations significantly improved, 0 significantly worsened**; on a "pick the 25th of 50 names" task, accuracy went from **21.33% all the way to 97.33%**. The researchers also ran a clever control: padding the prompt to the same length with periods produced **no improvement at all**—the gain comes from "repetition" itself, not "getting longer."

"The best part is, it has **zero search cost**," Old Guo said. "No optimizer, no judge, no running all night."

There are boundaries, of course: with reasoning mode on (letting the model think step by step), only 5 of 28 configurations still improved—reasoning models already tend to restate the question themselves; and if you bill by input tokens, the cost doubles.

But the thing that struck Old Guo most was on a different level. He pulled out the schedule full of optimization experiments and added a line at the very top:

> **Insight 13: Before you pay for search, try the zero-cost "dumb trick."** Set deterministic transforms like "repeat the whole thing" as the **pass mark** for all optimization experiments—for any gain you paid for and ran search to get, first answer one question: **does it beat this zero-intelligence dumb trick?** If not, your optimization was for nothing.

**The second thing was a failed "reproduction."**

Diana asked Xiaoman to take the most successful optimization from early in the quarter and replicate it on another product line. Xiaoman was confident: prompt version, model, parameters, dataset—it was all in the run logs, just follow them.

The numbers didn't match. Same task_prompt v3, same model, and the score was off by several points.

After two days of digging, the cause was almost laughable: over those three months, they had upgraded **the meta-prompt the optimizer uses to revise prompts**, and had also tuned **the judge prompt's wording**—and neither of those two things **even had a version number** in the run logs.

"We assigned a number to every homework assignment," Old Guo said with a wry smile, "but forgot to number **the red pen that grades the homework** and **the teacher who scores it**."

This trap is one the field only recently articulated systematically. A 2026 paper (SePO) went so far as to treat "the optimizer's own system prompt" as a training target and evolve it, raising the average score across five tasks from 71.89 to **76.38**; remove the "self-improvement" step and it immediately fell back to 74.94—**the quality of the optimizer itself affects the result, in hard currency**. Going further back, the classic PromptBreeder had long played with the self-referential move of "evolving the mutation rules along with everything else."

> **Insight 14: The optimizer and the judge are themselves parts that must be versioned.** Assign a version number to both "the prompt that revises prompts" and "the prompt that scores," and write them into every run log. **The judge used for evaluation must be frozen**—to change it, go through a separate review, and after changing, invalidate all old scores and rerun. Want to optimize the judge itself? You may, but you can only touch the **development-phase auxiliary judge**, and it must be **physically isolated** from the evaluation pipeline—otherwise it's the "cheating to inflate the score" from Chapter 4.

Azhe summed these two up into a new one-liner: **"Try the cheapest method first; number the most easily forgotten parts first."**

---

## Epilogue: The Last Three Sentences Old Guo Left on the Whiteboard

When the quarter ended, Xiaomi held steady at 92%, and—more importantly—**they could explain how every single point was earned, and could roll back at any step.**

On the last day of work, Old Guo wiped away the fourteen items densely packed on the whiteboard and left only three sentences. He said that if one day you forget all the earlier details, remembering these three is enough:

> **One: before you act, ask "is it worth it."** If the headroom doesn't exceed the noise floor, don't spend that money—and first lay down a floor with the zero-cost dumb trick from Chapter 7; any optimization that can't beat it was run for nothing.
>
> **Two: the essence of revising a prompt is "evidence → hypothesis → multiple candidates → validation-set selection → rollbackable," not having the model polish it once.**
>
> **Three: longer, more, more complex are none of them good by default.** First prove it brought no overfitting, no contamination, and didn't muddle your causal clarity.

Xiaoman looked at those three sentences and suddenly remembered her own line from the start of the quarter: "Let the AI fix the AI's homework—how convenient is that."

Now she knew the answer: letting the model revise the prompt itself is, of course, technically possible. But **"revising" is easy; "knowing whether the revision was right" is the real skill**—and that latter part is precisely the piece the model can't take off your hands.

That's not an optimizer that lets you sleep well at night. That's a discipline of engineering.

—— The End ——

---

## Appendix: Story ↔ Real Evidence Cross-Reference Table (for the Sticklers)

The story is fictional, but the research and numbers each item corresponds to below are real, and you can follow the links back to the original report and paper notes. The evidence levels follow the report's conventions: **A = paper/source code with structured notes; B = engineering practice that recurs across multiple sources; recent-preprint = a 2026 new draft, to be trusted only after independent reproduction**. **Note: the numbers in the papers hold "under that paper's setup," which does not mean they will necessarily hold on your task.**

| Story plot | Corresponding insight | Real evidence (all numbers from the original paper's setup) | Level |
|---|---|---|---|
| Optimizer cranks dev set to 87%, but new data drops to 79% | Insight 1 Checkup | Coin Flip: 72 optimizations, **49%** below zero-shot; ProTeGi peaks at about **3 steps** then overfits | A / recent-preprint |
| "Extract JSON" is a better first practice than "summarize in one sentence" | Insight 2 Pick the task | Coin Flip: the only task where all six methods beat zero-shot was the structured JSON task (**+6.8**); KG extraction went **+16% → ~1%** after switching datasets | A / recent-preprint |
| Record failures as a diagnosis, not a red X | Insight 3 Failure is evidence | ProTeGi: textual "gradient" rewriting **+15.3% / max +31%**; self-feedback over 6 rounds got worse instead | A |
| List mutually exclusive root-cause hypotheses first, then revise separately | Insight 4 Root-cause hypotheses | VISTA: on flawed seeds 23.81% **→ 13.50%**, recovered to **87.57%** after decoupling hypothesis/rewriting | recent-preprint |
| Lay five candidates out as a ledger, select across three dimensions, store best-seen separately | Insight 5 Multi-candidate selection | ProTeGi: beam selection beats greedy (0.85 / 0.67 / 0.88) | A |
| Drop the 2.4× longer candidate that added spurious rules | Insight 6 Anti-bloat | PrefPO: unchecked, balloons to **14.7×** length, **86%** secretly altering the task; TextReg adds regularization and is actually **+10.0 / +9.9** | recent-preprint |
| Don't change the instruction, just swap in 3 curated examples | Insight 7 Example optimization | Teach Better: optimizing only examples **+12.63**; optimizing examples 75.77 > optimizing only instruction 65.91; 3 curated > all | A |
| Break Xiaomi into a "parts list," freeze judge/safety | Insight 8 Label the part | AutoPDL: just switching to the right reasoning pattern, FEVER **6.5% → 74.0%** (+67.5pp) | A |
| Change the tool comment "unit is cents" instead of the agent instruction | Insight 9 Fix the tool schema | JTPRO: jointly optimizing instruction + tool schema, **51.27% → 64.46%** (ToolACE 1000 tools) | recent-preprint |
| Tag memories, retrieve only 3–5 matching ones | Insight 10 Filter memory | MemAPO: **70.7% vs 63.6%**, \$0.31 vs \$0.70; ERM: filtered memory converges nearly twice as fast | recent-preprint / A |
| Look at the trace, find the step that erred, change only it | Insight 11 Credit assignment | Temporal/Structural Credit: credit-guided **55.13 → 64.63**, indiscriminate updating loses points instead | recent-preprint |
| Read the original paper, debunk the "GEPA replaces RL" slogan | Insight 12 Lead, not evidence | GEPA is actually reflection-style prompt evolution (trajectory + Pareto selection), not an RL system; "replaces RL" is a spread-driven oversimplification | B |
| Azhe's hand slips, pastes the prompt verbatim twice, long-context task surges | Insight 13 Zero-cost transform | Prompt Repetition (Google): non-reasoning mode 7 models × 10 configs **47/70 significant wins 0 losses**; NameIndex **21.33% → 97.33%**; Padding control ineffective; with reasoning on, only 5 of 28 win; input cost ×2 | recent-preprint |
| "Same config" won't reproduce—the grading red pen and the scoring teacher weren't numbered | Insight 14 Version the red pen too | SePO: pretrain the optimizer's system prompt to self-evolve, **71.89 → 76.38**, falls back to 74.94 without self-improvement; PromptBreeder's hyper-mutation is a self-referential precedent | recent-preprint / A |

> **Honest disclaimer (same conventions as the original report)**: as of 2026-06-11, none of these 14 insights **has yet been reproduced and verified in this project**; the 2026 new drafts marked recent-preprint should be trusted only after independent reproduction. The story is a fictional dramatization made to be readable, and **cannot substitute** for the evidence chain in the original report. For the full argument, the method map, the evidence pyramid, and per-channel traceability, go back to [Cross-Channel Synthesis Report v4](./analysis_report_v4_20260611.html) and the [Reader-Facing Insight Handbook](./insight_handbook_20260609.html).
