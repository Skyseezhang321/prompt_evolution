# Prompt Optimization & Self-Evolving · Cross-Channel Panoramic Mind Map (Mermaid Source)

Date: 2026-06-10 (Updated 2026-06-11 to follow main report v4 structure: added Group G and insight nodes 13/14; Groups A–F unchanged)

This file was originally the **editable text version** of the SVG mind map embedded in [`analysis_report_v3_20260610.html`](./analysis_report_v3_20260610.html), and has since been updated to the 14-insight structure of [`analysis_report_v4_20260611.html`](./analysis_report_v4_20260611.html) (the v3 embedded SVG retains the old 12-insight structure and is frozen together with v3). Mermaid renders directly in GitHub and most Markdown previewers; edit here to rearrange the mind map, then redraw the SVG as needed.

One-line thesis: Automatically optimizing prompts is an **engineering discipline** of "decide if it's worth it → turn failures into editable evidence → multi-candidate + validation-set selection → rollback-ready" — not asking the model to polish a prompt.

---

## 1. Panoramic Mind Map (mindmap)

```mermaid
mindmap
  root((Prompt Optimization<br/>& Self-Evolving<br/>Engineering Discipline))
    Evidence Foundation · 5 Channels
      arXiv · A：Mechanism + Effect Numbers（31+ deep reads）
      GitHub · B：Engineering Structure / Governance（core4）
      Other Platforms · B：Production Tools / Observability Loop
      Twitter/X · B*：Adoption Signals / De-hype（pending verification）
      Zhihu · D：Community Understanding / Misconceptions（leads, not evidence）
    A Is It Worth Optimizing
      Insight01 Checkup first headroom vs noise floor
      Insight02 Start with tasks that can be scored objectively
    B Learn From Failures
      Insight03 Turn failures into editable evidence
      Insight04 List root-cause hypotheses before editing
    C Don't Be Fooled by the Model
      Insight05 Multi-candidate + validation-set selection
      Insight06 Longer & more complex ≈ overfitting
    D Which Component to Edit
      Insight07 Example selection is a first-class variable
      Insight08 Label artifacts clearly（mutable/frozen）
      Insight09 Fix tool call errors by editing the schema
    E Memory & Multi-Agent
      Insight10 Use only filtered memory
      Insight11 Do credit assignment before multi-agent work
    F Secondhand Methods
      Insight12 Social media / secondhand = leads, not evidence
    G Beyond Search · v4 Addition
      Insight13 Try zero-cost structural transforms first（whole-prompt repeat ×2）
      Insight14 Version the optimizer/judge too
    Helpful Methods HM
      HM-01 Pre-Optimization Gate
      HM-02 Trace-First Critique Rewrite
      HM-03 Exemplar Optimization Baseline
      HM-04 Prompt Artifact Ledger
      Source Evidence Triage（I-12）
    Anti-Patterns / Risk Guards
      Only looking at average score / prompt keeps growing longer
      Editing the evaluator or test set（reward hacking）
      Unbounded raw memory append（cross-task contamination）
      Rewriting the whole multi-agent system when one agent fails
      Using social media buzz / vendor % as evidence
      Fixing tool-call issues by editing only the system prompt
    Coverage, Bias & Honesty Boundary
      GitHub limited recall + canonical optimizer pending audit
      Other Platforms insufficient real failure cases / post-mortems
      Twitter candidate traceability chain pending verification（pending）
      2026 new preprints need independent reproduction（recent-preprint）
      This project has no Level-C experimental evidence yet
    First-Round Minimal Validation P0–P2
      P0 Pre-optimization checkup（incl. Insight13 zero-cost transform control） + examples vs instructions
      P1 Direct rewrite vs root-cause hypothesis / hygiene gate
      P2 Tool schema optimization / filtered memory
```

---

## 2. Cross-Channel Evidence Pyramid (How Evidence Stacks Up)

The lower the layer, the closer to first-hand mechanism evidence (strongest, most traceable); the higher the layer, the more it leans toward propagation signals. An insight is more credible when it can be independently supported by multiple layers; upper layers alone are insufficient to support strong conclusions.

```mermaid
flowchart TB
  ZH["Zhihu · D（leads）<br/>Community understanding / misconception clusters / problem framing"]
  TW["Twitter/X · B*（pending verification）<br/>Adoption signals / research→tool mapping / de-hype"]
  WEB["Other Platforms web_search · B<br/>Production tool loops / observability governance"]
  GH["GitHub source · B（partial D）<br/>Engineering structure / frozen evaluator / artifact ledger"]
  ARX["arXiv papers · A（foundation）<br/>Method mechanisms / ablations / effect numbers"]

  ZH --> TW --> WEB --> GH --> ARX
  classDef d fill:#fbe8ed,stroke:#b44a5c,color:#202329;
  classDef b fill:#e9f0fb,stroke:#2d67ad,color:#202329;
  classDef bb fill:#fbf0dc,stroke:#af6b08,color:#202329;
  classDef gg fill:#eaf1e3,stroke:#4f7e33,color:#202329;
  classDef a fill:#e8f3ee,stroke:#257d72,color:#202329;
  class ZH d; class TW b; class WEB bb; class GH gg; class ARX a;
```

---

## 3. Engineering Discipline Loop (Minimal Skeleton for One Prompt Optimization Run)

```mermaid
flowchart LR
  A["① Pre-optimization checkup<br/>headroom vs noise floor<br/>(HM-01)"] -->|Room exists| B["② Turn failures into editable evidence<br/>error_type + critique + trace<br/>(HM-02)"]
  A -->|No room| STOP["Cut losses: return to task definition / eval"]
  B --> C["③ List root-cause hypotheses<br/>2–3 mutually exclusive hypotheses"]
  C --> D["④ Generate multiple candidates<br/>one candidate per hypothesis"]
  D --> E["⑤ Validation-set selection<br/>dev + format errors + length<br/>Pareto + best_seen"]
  E --> F{"⑥ Hygiene gate<br/>Bloat / overfitting / contamination?"}
  F -->|Pass| G["⑦ Record in artifact ledger<br/>mutable/frozen + rollback point<br/>(HM-04)"]
  F -->|Fail| D
  G -->|Rollback| E
  G --> H["⑧ Deploy + observability<br/>regression / critical-failure set"]
```

---

## Maintenance Notes

- The panoramic mind map is organized to match the v4 report (③ workflow insights A–G, 14 total); the evidence pyramid and engineering discipline loop are unchanged from v3/v4.  After any edit, sync the corresponding section of the report.
- Node labels should stay consistent with the I-01..I-14 / HM-01..04 / C-01..06 naming in [`insight_method_catalog_20260609.md`](./insight_method_catalog_20260609.md) to avoid divergence.
- Embedded SVGs are generated by a one-off layout script; to redraw, rearrange nodes following this file's structure.
