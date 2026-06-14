# Prompt Optimization Advisor (Conversational · Grounded LLM + Deterministic Fallback)

**English** | [简体中文](README.md)

A user-facing, **grounded-in-this-repo evidence-graded knowledge base** prompt optimization advice **conversational assistant**. Describe your scenario in chat (task type, whether you have an eval set, single/multi-agent, etc.), and the system selects applicable insights and delivers **layered, concrete, source-traceable** recommendations.

This is the practical landing of the [Cross-Channel Synthesis Report v4](../docs/analysis_report_v4_20260611.html) from "documentation" to "usable" (v3 is frozen; insights 01–12 share the same source and numbering across both versions; 13/14 are new in v4).

## Two Operating Modes (same frontend, same knowledge base)

| Mode | How to run | Intelligence source | Dependencies |
|---|---|---|---|
| **Deterministic core (v1)** | Open `advisor.html` directly | Guided Q&A + rule-based trigger mapping; free-form follow-up uses keyword matching (Chinese bigram) | None (static, free, zero hallucination, 100% traceable) |
| **Grounded LLM Q&A (v2)** | Start the FastAPI backend, open `http://localhost:8000/` in browser | Free-text queries → backend retrieves knowledge base → OpenRouter generates answer, **forced citation of insight numbers + evidence levels, no fabrication** | OpenRouter key in `.env` + `fastapi/uvicorn` |

At startup, the frontend probes `api/health`: **if the backend is up and the key is ready → auto-switches to "LLM mode"**; otherwise falls back to deterministic mode (LLM call failures also auto-fall back to keyword matching). Regardless of mode, every response includes **"traceable knowledge base entries"** at the bottom — traceability does not rely on model self-discipline.

### Single-Entry Three-Panel Console

The page uses a three-panel layout with a single entry point to view all content: **Left** = knowledge base navigation (document/report links + per-channel detailed reports (arXiv/GitHub/other platforms/Twitter/Zhihu, aligned with the main report v4 evidence pyramid) + 14 insights grouped A–G + anti-patterns + initial experiments; click an item → view details on the right); **Center** = conversation; **Right** = detail panel (default: evidence level legend + honesty statement; click a left-panel item to display its full card; after each response, displays "sources cited in this response," with clickable insights to expand). Narrow screens (<1180/<860) collapse left/right panels into drawers, opened by the "📚 Knowledge Base / 📄 Details" buttons in the top bar.

### Integration with Reading Skills (Plan A+B)

The three reading skills (`read-paper` / `github-repo-audit` / `article-deep-read`) are the knowledge base's **content supply chain** — they deep-read papers/repos/articles into notes with evidence levels. The Q&A **retrieves their output rather than running them in real time** (real-time execution would break the "vetted materials only" traceability guarantee):

- **A — Expand retrieval corpus**: In LLM mode, beyond the 14 insights the backend also retrieves `corpus_index.json` (43 notes) as supplementary grounding, and responses can cite entries like `[paper-vista-reflection-dark-2026·A]`, preserving evidence levels and sources.
- **B — Source guidance**: If neither insights nor notes cover a specific source the user asks about, the response (and the deterministic mode's no-match prompt) suggests using the corresponding skill to deep-read it into the knowledge base.

After reading new notes, run `python advisor/build_corpus.py && python advisor/build_vectors.py` to rebuild the corpus and vectors so they become retrievable by the Q&A system.

### Retrieval: Vector-First, Keyword Fallback

In LLM mode the backend defaults to **semantic vector retrieval** (`baai/bge-m3` via OpenRouter): embed the query once → cosine similarity against 57 normalized vectors in `vector_index.json` → take top insights + top notes (notes have a similarity floor `ADVISOR_NOTE_FLOOR`, default 0.30). This captures semantically related items that keyword matching would miss (e.g., "rote memorization, poor generalization" → insight 06 overfitting). **No vector index or runtime embedding failure → automatic fallback to bigram keyword retrieval**; deterministic (`file://`) mode always uses keywords. The `retrieval` field in `/api/health` indicates whether `vector` or `keyword` is currently in use.

> Design trade-offs and target architecture (grounded LLM + deterministic fallback, guided-first then free-form, deterministic core ships first then LLM is layered on) are recorded in the project memory and [CHANGELOG](../CHANGELOG.md).

## Files

| File | Purpose |
|---|---|
| `knowledge_base.json` | **Single source of truth**: 14 insights (with trigger rules, evidence levels, illustrative hands-on examples, real numbers and sources), 9 guided questions, anti-pattern table, and initial experiments. Faithfully extracted from the v4 report (01–12 share the same source as the reader-facing insight handbook; 13/14 are new in v4). |
| `build_advisor.py` | Reads KB → validates → inlines the KB into the self-contained `advisor.html`. |
| `advisor.html` | **Generated artifact** (do not edit manually). Conversational chat page; can be opened by double-clicking (deterministic) or served via the backend (LLM mode). |
| `server.py` | **FastAPI backend** (v2). Reuses `scripts/llm_clients.py` to call OpenRouter; performs retrieval-augmented generation over the knowledge base and constructs a constrained system prompt; co-hosts `advisor.html` and `/api/chat`, `/api/chat/stream` (SSE streaming), `/api/health`. |
| `requirements.txt` | Backend dependencies (`fastapi`, `uvicorn`). |
| `build_corpus.py` | Scans vetted notes produced by reading skills (`docs/paper_notes/` A, `docs/github_repo_audit_notes/` B, `docs/industry_notes/` filtered to evidence-graded entries) → generates `corpus_index.json`. |
| `corpus_index.json` | **Generated artifact** (do not edit manually). Supplementary retrieval corpus for LLM mode: id/type/evidence level/one-sentence summary/source path for each note. |
| `build_vectors.py` | Embeds 14 insights + 43 notes using `baai/bge-m3` (OpenRouter), L2-normalizes → generates `vector_index.json` for semantic vector retrieval. |
| `vector_index.json` | **Generated artifact** (do not edit manually). 57 normalized vectors (1024-dim) + model name; at query time, embeds the question once and ranks by cosine similarity. |
| `test_advisor.py` | KB integrity + source file existence + golden scenario tests for the trigger DSL. |
| `test_server.py` | Backend retrieval / grounded prompt construction / endpoint contract tests (LLM calls are stubbed — no network, no cost). |

## How to Use

```bash
# 1) Edit the knowledge base (the only content you should edit manually) → regenerate the page
python advisor/build_advisor.py
#    After reading new notes → rebuild the supplementary retrieval corpus + vector index for LLM mode (vector step requires an OpenRouter key)
python advisor/build_corpus.py
python advisor/build_vectors.py

# 2) Run tests (required after changing KB / logic / backend)
python -m pytest advisor/ -q

# 3a) Deterministic mode: open advisor/advisor.html directly in a browser

# 3b) Grounded LLM mode: install dependencies and start the backend (key read from repo-root .env)
pip install -r advisor/requirements.txt
python -m uvicorn server:app --app-dir advisor --port 8000
#    Then open http://localhost:8000/ in a browser
```

### Remote Server Deployment

`advisor.html` / `corpus_index.json` / `vector_index.json` are all committed generated artifacts — **no build scripts need to be run on the server**; just pull the code and start:

```bash
git clone https://github.com/Skyseezhang321/prompt_evolution.git && cd prompt_evolution
pip install -r advisor/requirements.txt
# Manually create .env at the repo root (OPENROUTER_API_KEY=...、OPENROUTER_MODEL=...; keys must never be committed)
python -m uvicorn server:app --app-dir advisor --host 0.0.0.0 --port 8784   # port is configurable

# Post-deployment verification
curl http://localhost:8784/api/health
#    Expected: insights=14, corpus=43, retrieval=vector, llm_available=true
#    llm_available=false → .env missing at repo root; service runs but frontend falls back to deterministic mode
```

- **Python version**: ≥3.8 (3.8 compatibility issue fixed on 2026-06-12 — pydantic model annotations cannot use built-in generics `list[dict]`; use `typing.List/Dict` for new model fields). 3.8 is EOL; 3.9+ recommended for the long term.
- **Persistent process**: In production, use systemd / nohup for process management (auto-restart on crash); do not run as a bare foreground process.
- **Public exposure**: `/api/chat` consumes OpenRouter credits; if publicly deployed, be sure to add access control (nginx reverse proxy + authentication) to prevent key abuse.

LLM mode tuning (optional, without changing global `.env` values): `ADVISOR_MAX_TOKENS` (default 1600; reasoning models need a larger output budget). The model is controlled by `OPENROUTER_MODEL` in `.env`.

> **Operations note**: The backend loads the knowledge base / corpus / vector index **at startup** — after changing the KB, backend code, or rebuilding indexes you **must restart the backend**; otherwise the old process will keep serving with the old knowledge base (there was an incident where a residual process ran for a full day with the old 12-insight KB). Verify with: `GET /api/health` — `insights` (currently should be 14) and `corpus` (43). Also, LLM mode only activates when **accessed via the backend** (e.g., `http://localhost:8000/`); opening `advisor.html` by double-clicking (`file://`) is always deterministic mode.

## How to Add or Edit an Insight

Only edit `knowledge_base.json`:

1. Add an entry to `insights[]`; fields follow existing entries (required: `id/group/title/hook/evidence_level/triggers/diagnosis/steps/example/evidence/boundary/sources`).
2. Use the trigger DSL (see below) in `triggers` to bind it to specific answers for guided questions.
3. `evidence[].source` and `sources[]` must point to **actually existing** repo documents (tests will validate this).
4. Always tag numbers with `level` (`A` / `B` / `C` / `D` / `recent-preprint`); do not present paper figures as this project's own conclusions.
5. `example` is an **illustrative hands-on example** (scenario-grounded prompt snippet / field table / before-after, use `\n` for line breaks): the copy must include the word "演示" (tests will validate this); illustrative numbers must not be mixed with evidence numbers; in deterministic mode it renders as card layer ③, in LLM mode it enters the system prompt as rewriting material.
6. `python advisor/build_advisor.py && python -m pytest advisor/test_advisor.py -q`.

### Trigger DSL (same semantics in JS runtime and Python tests)

```jsonc
{ "q": "task_type", "eq": "toolcall" }          // equals
{ "q": "task_type", "in": ["extract","classify"] } // in set
{ "any": [ <cond>, <cond> ] }                    // any true
{ "all": [ <cond>, <cond> ] }                    // all true
```

The `triggers` of an insight is an array of conditions; the insight fires if **any** condition is true. Insights with `spine: true` are "universal disciplines" that always appear in results regardless of scenario.

## How to Evaluate "Advice Quality"

The `GOLDEN` set in `test_advisor.py` is a collection of **scenario → required insight hit** golden cases (e.g., multi-agent must include I08/I11; prompt getting longer must include I06; no eval set must include I01). When adding or adjusting insights or trigger rules, first add cases here to ensure the system **doesn't miss what it should say and doesn't fabricate conclusions absent from the knowledge base** for known scenarios. This is the minimal means of turning "advice quality" into a regressable test.

## Roadmap

- **v1**: Conversational UI + deterministic core. ✅
- **v2**: Grounded LLM Q&A + FastAPI backend. ✅ Validated with live runs using `deepseek/deepseek-v4-pro`: responses cite insight numbers and evidence levels by scenario, honestly declare when knowledge base coverage is lacking, and maintain honest evaluation criteria (paper figures hold under that paper's setup; 12 insights have not yet been reproduced in this project).
- **v2.1 Reading skill integration (A+B)**: ✅ LLM mode retrieval expanded to 42 vetted notes; responses can cite primary paper/repo notes; points to the corresponding skill for ingesting uncovered sources. Validated live (querying VISTA): response simultaneously cited `[I04·recent-preprint]` and `[paper-vista-reflection-dark-2026·A]`.
- **v2.2 Streaming output (SSE)**: ✅ `/api/chat/stream` uses SSE to push `meta` (citations) → `delta` (text chunks) → `done`/`error`; frontend reads the stream with `fetch`, renders incrementally with blinking cursor, appends citation section when done; falls back to keyword matching on failure or non-support. Backend adds `scripts/llm_clients.stream_openrouter_chat` generator (reuses existing config/headers). Live run: single response delivered as 795 chunks / 3,083 characters progressively. Note: reasoning models (deepseek-v4-pro) have a ~10s+ thinking pause before the first chunk, covered by a typing indicator.
- **v2.3 Vector retrieval**: ✅ `baai/bge-m3` (OpenRouter) semantic retrieval replaces keyword matching; offline `build_vectors.py` builds the index; cosine ranking at query time; auto-falls back to keywords if vectors unavailable. Added `scripts/llm_clients.embed_openrouter`.
- **Next candidate steps**: ① Turn "advice quality" evaluation into an offline test set (scenario → whether only vetted materials are cited, whether uncovered-coverage declarations are present) so LLM responses can also be regression-tested; ② Hybrid retrieval (vector + keyword weighting) and retrieval quality evaluation; ③ Multi-turn memory truncation and cost/latency observation; ④ Optional: disable reasoning (faster first token) or switch to a faster model.
