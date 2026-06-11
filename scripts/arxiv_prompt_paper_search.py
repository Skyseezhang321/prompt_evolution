"""Find arXiv papers related to prompt optimization and prompt evolution.

This script intentionally collects metadata only. It uses the official arXiv
Atom API, deduplicates by arXiv id, assigns a lightweight relevance label, and
exports review-ready candidate files for the M0 source collection phase.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping, Optional, Sequence

API_BASE_URL = "https://export.arxiv.org/api/query"
DEFAULT_OUTPUT_DIR = Path("outputs") / "arxiv_prompt_search"
DEFAULT_MAX_RESULTS_PER_QUERY = 100
DEFAULT_PAGE_SIZE = 100
DEFAULT_DELAY_SECONDS = 3.0
DEFAULT_USER_AGENT = "prompt-evolution-arxiv-search/0.1"
DEFAULT_INVENTORY_PATH = Path("docs") / "source_inventory.md"

ATOM_NS = "http://www.w3.org/2005/Atom"
OPENSEARCH_NS = "http://a9.com/-/spec/opensearch/1.1/"
ARXIV_NS = "http://arxiv.org/schemas/atom"
XML_NS = {
    "atom": ATOM_NS,
    "opensearch": OPENSEARCH_NS,
    "arxiv": ARXIV_NS,
}

DOMAIN_FILTER = "(cat:cs.CL OR cat:cs.AI OR cat:cs.LG OR cat:cs.IR OR stat.ML)"
RELEVANCE_ORDER = {"low": 0, "medium": 1, "high": 2}


@dataclass(frozen=True)
class QuerySpec:
    label: str
    method_category: str
    query: str


@dataclass(frozen=True)
class KeywordRule:
    phrase: str
    weight: int
    method_category: str
    title_bonus: int = 0


@dataclass
class ArxivPaper:
    arxiv_id: str
    latest_version_id: str
    title: str
    authors: list[str]
    published: str
    updated: str
    abstract: str
    primary_category: str
    categories: list[str]
    abs_url: str
    pdf_url: str
    doi: str = ""
    journal_ref: str = ""
    comment: str = ""
    matched_query_labels: list[str] = field(default_factory=list)
    matched_keyword_phrases: list[str] = field(default_factory=list)
    method_categories: list[str] = field(default_factory=list)
    score: int = 0
    relevance: str = "low"
    inventory_status: str = "new"
    source_id: str = ""


@dataclass
class QueryResult:
    spec: QuerySpec
    total_results: int
    returned_results: int
    papers: list[ArxivPaper]


class ArxivSearchError(RuntimeError):
    """Raised when arXiv search or parsing fails."""


KEYWORD_RULES = [
    KeywordRule("automatic prompt optimization", 12, "automatic prompt optimization", 8),
    KeywordRule("automated prompt optimization", 12, "automatic prompt optimization", 8),
    KeywordRule("automatic prompt engineering", 11, "automatic prompt engineering", 8),
    KeywordRule("automated prompt engineering", 11, "automatic prompt engineering", 8),
    KeywordRule("prompt optimization", 10, "automatic prompt optimization", 7),
    KeywordRule("prompt optimizer", 10, "automatic prompt optimization", 7),
    KeywordRule("prompt optimizers", 10, "automatic prompt optimization", 7),
    KeywordRule("prompt evolution", 11, "evolutionary prompt optimization", 8),
    KeywordRule("evolutionary prompt", 10, "evolutionary prompt optimization", 7),
    KeywordRule("evolve prompts", 8, "evolutionary prompt optimization", 5),
    KeywordRule("self-evolving prompt", 12, "self-evolving prompt optimization", 8),
    KeywordRule("self evolving prompt", 12, "self-evolving prompt optimization", 8),
    KeywordRule("self-improving prompt", 10, "self-evolving prompt optimization", 7),
    KeywordRule("self improving prompt", 10, "self-evolving prompt optimization", 7),
    KeywordRule("system prompt optimization", 12, "system prompt optimization", 8),
    KeywordRule("agent prompt optimization", 10, "agent prompt optimization", 7),
    KeywordRule("multi-agent prompt optimization", 12, "multi-agent prompt optimization", 8),
    KeywordRule("tool-use prompt optimization", 10, "tool-use prompt optimization", 6),
    KeywordRule("tool use prompt optimization", 10, "tool-use prompt optimization", 6),
    KeywordRule("textual gradient", 10, "textual gradient", 7),
    KeywordRule("textual gradients", 10, "textual gradient", 7),
    KeywordRule("natural language gradient", 9, "textual gradient", 6),
    KeywordRule("semantic gradient", 7, "textual gradient", 5),
    KeywordRule("gradient descent and beam search", 9, "textual gradient / beam search", 6),
    KeywordRule("critique-suggestion", 8, "critique-guided prompt optimization", 5),
    KeywordRule("critique suggestion", 8, "critique-guided prompt optimization", 5),
    KeywordRule("reflective prompt", 9, "reflective prompt evolution", 6),
    KeywordRule("reflection", 2, "reflective prompt evolution", 0),
    KeywordRule("llm-as-optimizer", 9, "LLM-as-optimizer", 6),
    KeywordRule("language model as optimizer", 8, "LLM-as-optimizer", 5),
    KeywordRule("optimization by prompting", 10, "LLM-as-optimizer", 7),
    KeywordRule("instruction induction", 7, "instruction induction", 5),
    KeywordRule("instruction optimization", 8, "instruction optimization", 6),
    KeywordRule("instruction search", 7, "instruction search", 5),
    KeywordRule("discrete prompt optimization", 9, "discrete prompt optimization", 6),
    KeywordRule("prompt rewriting", 7, "prompt rewriting", 5),
    KeywordRule("prompt refinement", 7, "prompt refinement", 5),
    KeywordRule("human feedback", 4, "human feedback", 0),
    KeywordRule("preference feedback", 4, "human feedback", 0),
    KeywordRule("dueling bandit", 5, "human feedback / bandits", 3),
    KeywordRule("context engineering", 8, "context engineering", 6),
    KeywordRule("rag prompt optimization", 8, "RAG prompt optimization", 6),
    KeywordRule("retrieval prompt optimization", 8, "RAG prompt optimization", 6),
    KeywordRule("llm-as-a-judge", 4, "eval / judge", 2),
    KeywordRule("llm as a judge", 4, "eval / judge", 2),
    KeywordRule("prompt overfitting", 6, "eval / benchmark governance", 4),
    KeywordRule("benchmark overfitting", 5, "eval / benchmark governance", 3),
    KeywordRule("prompt selection", 5, "prompt selection", 3),
    KeywordRule("autoprompt", 8, "gradient-guided prompt search", 6),
    KeywordRule("rlprompt", 8, "reinforcement learning prompt search", 6),
    KeywordRule("grips", 8, "gradient-free instruction search", 6),
    KeywordRule("protegi", 12, "textual gradient / beam search", 8),
    KeywordRule("opro", 9, "LLM-as-optimizer", 6),
    KeywordRule("promptbreeder", 12, "self-referential prompt evolution", 8),
    KeywordRule("evoprompt", 12, "evolutionary prompt optimization", 8),
    KeywordRule("dspy", 10, "prompt-as-program", 7),
    KeywordRule("mipro", 10, "prompt-as-program", 7),
    KeywordRule("textgrad", 12, "textual gradient", 8),
    KeywordRule("gepa", 12, "reflective prompt evolution", 8),
    KeywordRule("memapo", 12, "memory-based APO", 8),
    KeywordRule("sepo", 12, "self-evolving prompt optimization", 8),
    KeywordRule("maspo", 12, "multi-agent prompt optimization", 8),
    KeywordRule("autopdl", 12, "agent prompt optimization", 8),
    KeywordRule("promptomatix", 10, "automatic prompt optimization framework", 7),
    KeywordRule("promptolution", 10, "prompt optimization tool", 7),
    KeywordRule("crispo", 9, "critique-guided prompt optimization", 6),
]

NEGATIVE_RULES = [
    KeywordRule("visual prompt tuning", -8, "visual prompt tuning"),
    KeywordRule("soft prompt tuning", -6, "soft prompt tuning"),
    KeywordRule("prefix tuning", -4, "soft prompt tuning"),
    KeywordRule("prefix-tuning", -4, "soft prompt tuning"),
    KeywordRule("image prompt", -4, "image prompt"),
    KeywordRule("stable diffusion prompt", -6, "image prompt"),
]


def _phrase(field: str, value: str) -> str:
    escaped = value.replace('"', '\\"')
    return f'{field}:"{escaped}"'


def _term(field: str, value: str) -> str:
    return f"{field}:{value}"


def _any_phrase(field: str, phrases: Sequence[str]) -> str:
    return "(" + " OR ".join(_phrase(field, phrase) for phrase in phrases) + ")"


def _any_term(field: str, terms: Sequence[str]) -> str:
    return "(" + " OR ".join(_term(field, term) for term in terms) + ")"


def _with_domain(query: str) -> str:
    return f"({query}) AND {DOMAIN_FILTER}"


def default_query_specs() -> list[QuerySpec]:
    """Return high-recall arXiv query specs for this research phase."""
    return [
        QuerySpec(
            "apo-core",
            "automatic prompt optimization",
            _with_domain(
                _any_phrase(
                    "all",
                    [
                        "automatic prompt optimization",
                        "automated prompt optimization",
                        "automatic prompt engineering",
                        "automated prompt engineering",
                        "prompt optimization",
                        "prompt optimizer",
                    ],
                )
            ),
        ),
        QuerySpec(
            "prompt-evolution",
            "evolutionary / self-evolving prompt optimization",
            _with_domain(
                _any_phrase(
                    "all",
                    [
                        "prompt evolution",
                        "evolutionary prompt",
                        "evolve prompts",
                        "self-evolving prompt",
                        "self evolving prompt",
                        "self-improving prompt",
                        "genetic prompt",
                    ],
                )
            ),
        ),
        QuerySpec(
            "textual-gradient-critique",
            "textual gradient / critique-guided optimization",
            _with_domain(
                _any_phrase(
                    "all",
                    [
                        "textual gradient",
                        "natural language gradient",
                        "semantic gradient",
                        "gradient descent and beam search",
                        "critique-suggestion",
                        "critique suggestion",
                        "reflective prompt",
                    ],
                )
            ),
        ),
        QuerySpec(
            "llm-optimizer",
            "LLM-as-optimizer",
            _with_domain(
                _any_phrase(
                    "all",
                    [
                        "optimization by prompting",
                        "LLM-as-optimizer",
                        "language model as optimizer",
                        "large language model as optimizer",
                        "prompting optimization",
                    ],
                )
            ),
        ),
        QuerySpec(
            "instruction-search",
            "instruction search / rewriting",
            _with_domain(
                _any_phrase(
                    "all",
                    [
                        "instruction induction",
                        "instruction optimization",
                        "instruction search",
                        "discrete prompt optimization",
                        "prompt rewriting",
                        "prompt refinement",
                    ],
                )
            ),
        ),
        QuerySpec(
            "named-methods-classic",
            "named classic methods",
            _with_domain(
                _any_term(
                    "all",
                    [
                        "AutoPrompt",
                        "RLPrompt",
                        "GrIPS",
                        "ProTeGi",
                        "OPRO",
                        "PromptBreeder",
                        "EvoPrompt",
                    ],
                )
            ),
        ),
        QuerySpec(
            "named-methods-recent",
            "named recent methods",
            _with_domain(
                _any_term(
                    "all",
                    [
                        "DSPy",
                        "MIPRO",
                        "TextGrad",
                        "GEPA",
                        "MemAPO",
                        "SePO",
                        "MASPO",
                        "AutoPDL",
                        "Promptomatix",
                        "promptolution",
                        "CriSPO",
                    ],
                )
            ),
        ),
        QuerySpec(
            "agent-system-tool",
            "agent / system / tool-use prompt optimization",
            _with_domain(
                _any_phrase(
                    "all",
                    [
                        "system prompt optimization",
                        "agent prompt optimization",
                        "multi-agent prompt optimization",
                        "LLM agents prompt optimization",
                        "tool-use prompt optimization",
                        "tool use prompt optimization",
                    ],
                )
            ),
        ),
        QuerySpec(
            "context-rag",
            "context engineering / RAG prompt optimization",
            _with_domain(
                _any_phrase(
                    "all",
                    [
                        "context engineering",
                        "RAG prompt optimization",
                        "retrieval prompt optimization",
                        "prompt optimization retrieval augmented generation",
                        "context optimization large language models",
                    ],
                )
            ),
        ),
        QuerySpec(
            "eval-judge-governance",
            "eval / judge / benchmark governance",
            _with_domain(
                _any_phrase(
                    "all",
                    [
                        "eval driven prompt",
                        "evaluation driven prompt",
                        "prompt evaluation",
                        "LLM-as-a-judge prompt optimization",
                        "prompt overfitting",
                        "benchmark overfitting prompt",
                        "prompt selection",
                    ],
                )
            ),
        ),
        QuerySpec(
            "human-feedback",
            "human feedback prompt optimization",
            _with_domain(
                _any_phrase(
                    "all",
                    [
                        "prompt optimization with human feedback",
                        "human feedback prompt optimization",
                        "preference feedback prompt optimization",
                        "dueling bandit prompt",
                    ],
                )
            ),
        ),
        QuerySpec(
            "application-studies",
            "application-specific APO studies",
            _with_domain(
                _any_phrase(
                    "all",
                    [
                        "automatic prompt optimization for",
                        "prompt optimization for knowledge graph",
                        "prompt optimization for text generation",
                        "prompt optimization for information extraction",
                        "prompt optimization for code generation",
                    ],
                )
            ),
        ),
        QuerySpec(
            "broad-llm-prompt-optimization",
            "broad LLM prompt optimization",
            _with_domain(
                "(all:prompt AND all:optimization AND (all:LLM OR "
                + _phrase("all", "large language model")
                + " OR "
                + _phrase("all", "large language models")
                + "))"
            ),
        ),
    ]


def build_query_url(
    query: str,
    start: int,
    max_results: int,
    sort_by: str,
    sort_order: str,
) -> str:
    params = {
        "search_query": query,
        "start": str(start),
        "max_results": str(max_results),
        "sortBy": sort_by,
        "sortOrder": sort_order,
    }
    return f"{API_BASE_URL}?{urllib.parse.urlencode(params)}"


def fetch_query(
    spec: QuerySpec,
    max_results_per_query: int,
    page_size: int,
    sort_by: str,
    sort_order: str,
    user_agent: str,
    delay_seconds: float,
) -> QueryResult:
    papers: list[ArxivPaper] = []
    total_results = 0
    start = 0
    requested_any_page = False

    while start < max_results_per_query:
        current_page_size = min(page_size, max_results_per_query - start)
        url = build_query_url(
            spec.query,
            start=start,
            max_results=current_page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        if requested_any_page and delay_seconds > 0:
            time.sleep(delay_seconds)

        feed = fetch_url(url, user_agent=user_agent)
        parsed_total, page_papers = parse_atom_feed(feed, spec)
        requested_any_page = True
        total_results = parsed_total
        papers.extend(page_papers)

        if len(page_papers) < current_page_size:
            break

        start += current_page_size
        if start >= total_results:
            break

    return QueryResult(
        spec=spec,
        total_results=total_results,
        returned_results=len(papers),
        papers=papers,
    )


def fetch_url(url: str, user_agent: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise ArxivSearchError(f"arXiv API HTTP {exc.code}: {body[:500]}") from exc
    except urllib.error.URLError as exc:
        raise ArxivSearchError(f"arXiv API request failed: {exc}") from exc


def parse_atom_feed(feed: bytes, spec: QuerySpec) -> tuple[int, list[ArxivPaper]]:
    try:
        root = ET.fromstring(feed)
    except ET.ParseError as exc:
        raise ArxivSearchError("arXiv API returned invalid Atom XML") from exc

    total_results_text = root.findtext("opensearch:totalResults", namespaces=XML_NS)
    try:
        total_results = int(total_results_text or "0")
    except ValueError:
        total_results = 0

    papers = [parse_entry(entry, spec) for entry in root.findall("atom:entry", XML_NS)]
    return total_results, papers


def parse_entry(entry: ET.Element, spec: QuerySpec) -> ArxivPaper:
    entry_id = _text(entry, "atom:id")
    latest_version_id = normalize_arxiv_id(entry_id, keep_version=True)
    arxiv_id = normalize_arxiv_id(entry_id)

    title = _collapse_ws(_text(entry, "atom:title"))
    abstract = _collapse_ws(_text(entry, "atom:summary"))
    authors = [
        _collapse_ws(author.findtext("atom:name", default="", namespaces=XML_NS))
        for author in entry.findall("atom:author", XML_NS)
    ]
    authors = [author for author in authors if author]

    primary_category_element = entry.find("arxiv:primary_category", XML_NS)
    primary_category = ""
    if primary_category_element is not None:
        primary_category = primary_category_element.attrib.get("term", "")

    categories = [
        category.attrib.get("term", "")
        for category in entry.findall("atom:category", XML_NS)
        if category.attrib.get("term")
    ]

    abs_url = ""
    pdf_url = ""
    for link in entry.findall("atom:link", XML_NS):
        href = link.attrib.get("href", "")
        if link.attrib.get("rel") == "alternate":
            abs_url = href
        if link.attrib.get("title") == "pdf" or link.attrib.get("type") == "application/pdf":
            pdf_url = href

    paper = ArxivPaper(
        arxiv_id=arxiv_id,
        latest_version_id=latest_version_id,
        title=title,
        authors=authors,
        published=_text(entry, "atom:published"),
        updated=_text(entry, "atom:updated"),
        abstract=abstract,
        primary_category=primary_category,
        categories=categories,
        abs_url=abs_url or f"https://arxiv.org/abs/{arxiv_id}",
        pdf_url=pdf_url,
        doi=_text(entry, "arxiv:doi"),
        journal_ref=_text(entry, "arxiv:journal_ref"),
        comment=_text(entry, "arxiv:comment"),
        matched_query_labels=[spec.label],
        method_categories=[spec.method_category],
    )
    apply_scoring(paper)
    return paper


def normalize_arxiv_id(value: str, keep_version: bool = False) -> str:
    """Extract an arXiv id from a URL or raw id, optionally keeping version."""
    text = value.strip()
    if "/abs/" in text:
        text = text.rsplit("/abs/", 1)[1]
    elif "/pdf/" in text:
        text = text.rsplit("/pdf/", 1)[1].removesuffix(".pdf")
    elif text.startswith("http"):
        text = text.rstrip("/").rsplit("/", 1)[-1]

    text = text.split("#", 1)[0].split("?", 1)[0].strip("/")
    if keep_version:
        return text

    return re.sub(r"v\d+$", "", text)


def apply_scoring(paper: ArxivPaper) -> None:
    title = _normalize_text(paper.title)
    body = _normalize_text(f"{paper.title} {paper.abstract}")
    score = 0
    phrase_hits: list[str] = []
    category_scores: dict[str, int] = {}

    for rule in KEYWORD_RULES:
        if rule.phrase in body:
            hit_score = rule.weight
            if rule.phrase in title:
                hit_score += rule.title_bonus
            score += hit_score
            phrase_hits.append(rule.phrase)
            category_scores[rule.method_category] = (
                category_scores.get(rule.method_category, 0) + hit_score
            )

    strong_positive = score >= 10
    for rule in NEGATIVE_RULES:
        if rule.phrase in body:
            score += rule.weight
            if not strong_positive:
                category_scores[rule.method_category] = (
                    category_scores.get(rule.method_category, 0) + rule.weight
                )

    score += min(len(set(paper.matched_query_labels)), 5)

    categories = [
        category
        for category, _score in sorted(
            category_scores.items(),
            key=lambda item: (-item[1], item[0]),
        )
        if _score > 0
    ]
    paper.matched_keyword_phrases = sorted(set(phrase_hits))
    paper.method_categories = sorted(
        set(categories + paper.method_categories),
        key=lambda value: value.lower(),
    )
    paper.score = score
    paper.relevance = relevance_from_score(score, paper.title)
    paper.source_id = source_id_for_paper(paper)


def relevance_from_score(score: int, title: str) -> str:
    title_normalized = _normalize_text(title)
    direct_title_signals = (
        "prompt optimization",
        "automatic prompt engineering",
        "prompt evolution",
        "system prompt optimization",
        "promptbreeder",
        "evoprompt",
        "protegi",
        "textgrad",
        "gepa",
        "memapo",
        "sepo",
        "maspo",
        "autopdl",
    )
    if score >= 18 or any(signal in title_normalized for signal in direct_title_signals):
        return "high"
    if score >= 8:
        return "medium"
    return "low"


def merge_papers_by_id(papers: Iterable[ArxivPaper]) -> list[ArxivPaper]:
    merged: dict[str, ArxivPaper] = {}
    for paper in papers:
        existing = merged.get(paper.arxiv_id)
        if existing is None:
            merged[paper.arxiv_id] = paper
            continue

        existing.matched_query_labels = sorted(
            set(existing.matched_query_labels + paper.matched_query_labels)
        )
        existing.method_categories = sorted(
            set(existing.method_categories + paper.method_categories),
            key=lambda value: value.lower(),
        )
        existing.matched_keyword_phrases = sorted(
            set(existing.matched_keyword_phrases + paper.matched_keyword_phrases)
        )
        apply_scoring(existing)

    return sorted(
        merged.values(),
        key=lambda paper: (
            -RELEVANCE_ORDER[paper.relevance],
            -paper.score,
            paper.published,
            paper.title.lower(),
        ),
    )


def mark_existing_inventory(papers: Sequence[ArxivPaper], inventory_path: Path) -> None:
    existing_ids = load_existing_arxiv_ids(inventory_path)
    for paper in papers:
        if paper.arxiv_id in existing_ids:
            paper.inventory_status = "existing"


def load_existing_arxiv_ids(inventory_path: Path) -> set[str]:
    if not inventory_path.exists():
        return set()

    text = inventory_path.read_text(encoding="utf-8")
    ids: set[str] = set()
    for match in re.finditer(r"arxiv\.org/(?:abs|pdf)/([A-Za-z0-9.\-/]+)", text):
        ids.add(normalize_arxiv_id(match.group(1)))
    return ids


def filter_by_min_relevance(
    papers: Sequence[ArxivPaper],
    min_relevance: str,
) -> list[ArxivPaper]:
    threshold = RELEVANCE_ORDER[min_relevance]
    return [
        paper
        for paper in papers
        if RELEVANCE_ORDER[paper.relevance] >= threshold
    ]


def write_outputs(
    papers: Sequence[ArxivPaper],
    query_results: Sequence[QueryResult],
    output_dir: Path,
    inventory_min_relevance: str,
) -> Mapping[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    json_path = output_dir / f"arxiv_prompt_papers_{timestamp}.json"
    csv_path = output_dir / f"arxiv_prompt_papers_{timestamp}.csv"
    markdown_path = output_dir / f"arxiv_prompt_papers_{timestamp}.md"
    inventory_path = output_dir / f"arxiv_inventory_rows_{timestamp}.md"
    summary_path = output_dir / f"arxiv_search_summary_{timestamp}.json"

    json_path.write_text(
        json.dumps([paper_to_dict(paper) for paper in papers], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_csv(csv_path, papers)
    markdown_path.write_text(render_markdown_report(papers, query_results), encoding="utf-8")
    inventory_path.write_text(
        render_inventory_rows(
            [
                paper
                for paper in filter_by_min_relevance(papers, inventory_min_relevance)
                if paper.inventory_status == "new"
            ]
        ),
        encoding="utf-8",
    )
    summary_path.write_text(
        json.dumps(build_summary(papers, query_results), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return {
        "json": json_path,
        "csv": csv_path,
        "markdown": markdown_path,
        "inventory_rows": inventory_path,
        "summary": summary_path,
    }


def paper_to_dict(paper: ArxivPaper) -> dict[str, object]:
    data = asdict(paper)
    data["authors"] = paper.authors
    return data


def write_csv(path: Path, papers: Sequence[ArxivPaper]) -> None:
    fieldnames = [
        "arxiv_id",
        "latest_version_id",
        "title",
        "authors",
        "published",
        "updated",
        "relevance",
        "score",
        "inventory_status",
        "primary_category",
        "categories",
        "method_categories",
        "matched_query_labels",
        "matched_keyword_phrases",
        "abs_url",
        "pdf_url",
        "doi",
        "journal_ref",
        "comment",
        "abstract",
    ]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for paper in papers:
            writer.writerow(
                {
                    "arxiv_id": paper.arxiv_id,
                    "latest_version_id": paper.latest_version_id,
                    "title": paper.title,
                    "authors": "; ".join(paper.authors),
                    "published": paper.published,
                    "updated": paper.updated,
                    "relevance": paper.relevance,
                    "score": paper.score,
                    "inventory_status": paper.inventory_status,
                    "primary_category": paper.primary_category,
                    "categories": "; ".join(paper.categories),
                    "method_categories": "; ".join(paper.method_categories),
                    "matched_query_labels": "; ".join(paper.matched_query_labels),
                    "matched_keyword_phrases": "; ".join(paper.matched_keyword_phrases),
                    "abs_url": paper.abs_url,
                    "pdf_url": paper.pdf_url,
                    "doi": paper.doi,
                    "journal_ref": paper.journal_ref,
                    "comment": paper.comment,
                    "abstract": paper.abstract,
                }
            )


def build_summary(
    papers: Sequence[ArxivPaper],
    query_results: Sequence[QueryResult],
) -> dict[str, object]:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_query_hits": sum(result.returned_results for result in query_results),
        "unique_papers": len(papers),
        "new_papers": sum(1 for paper in papers if paper.inventory_status == "new"),
        "existing_papers": sum(
            1 for paper in papers if paper.inventory_status == "existing"
        ),
        "by_relevance": _count_by(papers, lambda paper: paper.relevance),
        "by_primary_category": _count_by(papers, lambda paper: paper.primary_category),
        "by_method_category": _count_many(papers, lambda paper: paper.method_categories),
        "queries": [
            {
                "label": result.spec.label,
                "method_category": result.spec.method_category,
                "returned_results": result.returned_results,
                "total_results": result.total_results,
                "query": result.spec.query,
            }
            for result in query_results
        ],
    }


def render_markdown_report(
    papers: Sequence[ArxivPaper],
    query_results: Sequence[QueryResult],
) -> str:
    summary = build_summary(papers, query_results)
    lines = [
        "# arXiv Prompt Optimization Candidate Papers",
        "",
        f"Generated at: {summary['generated_at']}",
        "",
        "This is an automatically generated candidate list. Treat relevance as a",
        "triage signal, not as a research conclusion.",
        "",
        "## Summary",
        "",
        f"- Total query hits before dedupe: {summary['total_query_hits']}",
        f"- Unique papers after dedupe: {summary['unique_papers']}",
        f"- New vs existing inventory: {summary['new_papers']} new / {summary['existing_papers']} existing",
        f"- Relevance counts: {json.dumps(summary['by_relevance'], ensure_ascii=False)}",
        "",
        "## Query Coverage",
        "",
        "| query_label | returned | total_reported | method_category |",
        "| --- | ---: | ---: | --- |",
    ]
    for result in query_results:
        lines.append(
            "| "
            + " | ".join(
                [
                    _md_cell(result.spec.label),
                    str(result.returned_results),
                    str(result.total_results),
                    _md_cell(result.spec.method_category),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Candidate Papers",
            "",
            "| relevance | score | status | arxiv_id | title | year | categories | matched_queries | method_categories |",
            "| --- | ---: | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for paper in papers:
        lines.append(
            "| "
            + " | ".join(
                [
                    paper.relevance,
                    str(paper.score),
                    paper.inventory_status,
                    f"[{_md_cell(paper.arxiv_id)}]({paper.abs_url})",
                    _md_cell(paper.title),
                    _paper_year(paper),
                    _md_cell("; ".join(paper.categories)),
                    _md_cell("; ".join(paper.matched_query_labels)),
                    _md_cell("; ".join(paper.method_categories)),
                ]
            )
            + " |"
        )

    return "\n".join(lines) + "\n"


def render_inventory_rows(papers: Sequence[ArxivPaper]) -> str:
    lines = [
        "| source_id | status | relevance | title | date | url | method_category | local_note | decision |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for paper in papers:
        lines.append(render_inventory_row(paper))
    return "\n".join(lines) + "\n"


def render_inventory_row(paper: ArxivPaper) -> str:
    local_note = (
        "arXiv automated search candidate; "
        f"score={paper.score}; "
        f"queries={', '.join(paper.matched_query_labels)}; "
        f"keywords={', '.join(paper.matched_keyword_phrases[:8])}"
    )
    return (
        "| "
        + " | ".join(
            [
                _md_cell(paper.source_id),
                "candidate",
                paper.relevance,
                _md_cell(paper.title),
                _paper_year(paper),
                paper.abs_url,
                _md_cell("; ".join(paper.method_categories)),
                _md_cell(local_note),
                "needs skim",
            ]
        )
        + " |"
    )


def source_id_for_paper(paper: ArxivPaper) -> str:
    safe_id = paper.arxiv_id.lower().replace(".", "-").replace("/", "-")
    return f"paper-arxiv-{safe_id}"


def run_search(args: argparse.Namespace) -> tuple[list[ArxivPaper], list[QueryResult]]:
    specs = default_query_specs()
    if args.query_label:
        requested = set(args.query_label)
        specs = [spec for spec in specs if spec.label in requested]
        missing = requested - {spec.label for spec in specs}
        if missing:
            raise SystemExit(f"unknown query label(s): {', '.join(sorted(missing))}")

    query_results: list[QueryResult] = []
    all_papers: list[ArxivPaper] = []
    for index, spec in enumerate(specs):
        if index > 0 and args.delay_seconds > 0:
            time.sleep(args.delay_seconds)
        print(f"[{index + 1}/{len(specs)}] {spec.label}")
        result = fetch_query(
            spec,
            max_results_per_query=args.max_results_per_query,
            page_size=args.page_size,
            sort_by=args.sort_by,
            sort_order=args.sort_order,
            user_agent=args.user_agent,
            delay_seconds=args.delay_seconds,
        )
        query_results.append(result)
        all_papers.extend(result.papers)
        print(
            f"  returned {result.returned_results}; "
            f"arXiv total reported {result.total_results}"
        )

    papers = merge_papers_by_id(all_papers)
    mark_existing_inventory(papers, args.inventory_path)
    papers = filter_by_min_relevance(papers, args.min_relevance)
    return papers, query_results


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Search arXiv for prompt optimization/evolution candidate papers."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for JSON/CSV/Markdown candidate outputs.",
    )
    parser.add_argument(
        "--inventory-path",
        type=Path,
        default=DEFAULT_INVENTORY_PATH,
        help="Existing source inventory used to mark already registered arXiv ids.",
    )
    parser.add_argument(
        "--max-results-per-query",
        type=int,
        default=DEFAULT_MAX_RESULTS_PER_QUERY,
        help="Maximum arXiv results to retrieve for each query label.",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=DEFAULT_PAGE_SIZE,
        help="Results per arXiv request. Keep moderate to reduce server load.",
    )
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=DEFAULT_DELAY_SECONDS,
        help="Delay between arXiv requests. arXiv asks API clients to use >=3s.",
    )
    parser.add_argument(
        "--sort-by",
        choices=["relevance", "lastUpdatedDate", "submittedDate"],
        default="relevance",
        help="arXiv API sortBy parameter.",
    )
    parser.add_argument(
        "--sort-order",
        choices=["ascending", "descending"],
        default="descending",
        help="arXiv API sortOrder parameter.",
    )
    parser.add_argument(
        "--min-relevance",
        choices=["low", "medium", "high"],
        default="low",
        help="Minimum relevance label to keep in output files.",
    )
    parser.add_argument(
        "--inventory-min-relevance",
        choices=["medium", "high"],
        default="medium",
        help="Minimum relevance for generated source_inventory rows.",
    )
    parser.add_argument(
        "--query-label",
        action="append",
        help="Restrict to one query label. Repeat to include multiple labels.",
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help="User-Agent header for arXiv API requests.",
    )
    parser.add_argument(
        "--list-queries",
        action="store_true",
        help="Print query labels and query strings without calling arXiv.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.max_results_per_query < 1:
        parser.error("--max-results-per-query must be >= 1")
    if args.page_size < 1 or args.page_size > 2000:
        parser.error("--page-size must be between 1 and 2000")
    if args.delay_seconds < 0:
        parser.error("--delay-seconds must be >= 0")

    if args.list_queries:
        for spec in default_query_specs():
            print(f"{spec.label}\t{spec.method_category}\t{spec.query}")
        return 0

    papers, query_results = run_search(args)
    output_paths = write_outputs(
        papers,
        query_results,
        output_dir=args.output_dir,
        inventory_min_relevance=args.inventory_min_relevance,
    )

    summary = build_summary(papers, query_results)
    print("")
    print(
        "Done: "
        f"{summary['unique_papers']} unique papers "
        f"({summary['new_papers']} new, {summary['existing_papers']} existing)."
    )
    for label, path in output_paths.items():
        print(f"{label}: {path}")
    return 0


def _text(entry: ET.Element, path: str) -> str:
    return entry.findtext(path, default="", namespaces=XML_NS).strip()


def _collapse_ws(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _normalize_text(text: str) -> str:
    return _collapse_ws(text).lower()


def _paper_year(paper: ArxivPaper) -> str:
    date_text = paper.published or paper.updated
    return date_text[:4] if len(date_text) >= 4 else ""


def _md_cell(value: str) -> str:
    return _collapse_ws(value).replace("|", "\\|")


def _count_by(
    papers: Sequence[ArxivPaper],
    key_fn,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for paper in papers:
        key = key_fn(paper) or "unknown"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def _count_many(
    papers: Sequence[ArxivPaper],
    key_fn,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for paper in papers:
        values = list(key_fn(paper)) or ["unknown"]
        for value in values:
            counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


if __name__ == "__main__":
    raise SystemExit(main())
