"""Create a focused arXiv reading shortlist from broad candidate metadata.

The broad arXiv search intentionally favors recall. This script is the next
triage step: it reranks metadata for this repository's research question and
writes a top-N candidate list for human skim reading.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.arxiv_prompt_paper_search import (
    ArxivPaper,
    render_inventory_rows,
)

DEFAULT_OUTPUT_DIR = Path("outputs") / "arxiv_prompt_search"
DEFAULT_TOP_N = 100

RELEVANCE_BONUS = {"high": 24, "medium": 8, "low": -18}

METHOD_BONUS = {
    "automatic prompt optimization": 28,
    "automatic prompt engineering": 22,
    "self-evolving prompt optimization": 26,
    "self-referential prompt evolution": 26,
    "evolutionary prompt optimization": 22,
    "evolutionary / self-evolving prompt optimization": 20,
    "reflective prompt evolution": 22,
    "textual gradient": 22,
    "textual gradient / critique-guided optimization": 20,
    "textual gradient / beam search": 18,
    "critique-guided prompt optimization": 18,
    "prompt-as-program": 20,
    "agent prompt optimization": 20,
    "system prompt optimization": 20,
    "multi-agent prompt optimization": 18,
    "agent / system / tool-use prompt optimization": 18,
    "eval / judge / benchmark governance": 16,
    "eval / benchmark governance": 16,
    "human feedback prompt optimization": 16,
    "human feedback": 10,
    "LLM-as-optimizer": 12,
    "instruction optimization": 12,
    "instruction search": 12,
    "instruction search / rewriting": 10,
    "prompt refinement": 10,
    "prompt rewriting": 10,
    "prompt optimization tool": 10,
    "automatic prompt optimization framework": 10,
    "context engineering": 8,
    "context engineering / RAG prompt optimization": 8,
    "RAG prompt optimization": 6,
    "application-specific APO studies": 4,
}

TITLE_BONUS_RULES = [
    (r"\bsurvey\b", 30, "survey"),
    (r"automatic prompt optimization", 34, "automatic prompt optimization in title"),
    (r"automated prompt optimization", 34, "automated prompt optimization in title"),
    (r"automatic prompt engineering", 30, "automatic prompt engineering in title"),
    (r"prompt optimization", 26, "prompt optimization in title"),
    (r"prompt optimizer", 24, "prompt optimizer in title"),
    (r"prompt evolution", 24, "prompt evolution in title"),
    (r"self[- ]evolving prompt", 28, "self-evolving prompt in title"),
    (r"system prompt optimization", 28, "system prompt optimization in title"),
    (r"agentic prompt optimization|agent prompt optimization", 24, "agent prompt optimization in title"),
    (r"multi-agent prompt optimization", 24, "multi-agent prompt optimization in title"),
    (r"textual gradients?", 24, "textual gradient in title"),
    (r"reflective prompt", 20, "reflective prompt in title"),
    (r"prompt overfitting|benchmark overfitting", 22, "overfitting/governance in title"),
    (r"prompt selection", 16, "prompt selection in title"),
    (r"prompt rewriting|prompt refinement", 16, "prompt rewrite/refinement in title"),
    (r"instruction optimization|instruction induction", 16, "instruction optimization in title"),
    (r"context engineering", 14, "context engineering in title"),
]

NAMED_METHOD_BONUS = {
    "autoprompt": 16,
    "rlprompt": 16,
    "grips": 16,
    "protegi": 22,
    "opro": 18,
    "promptbreeder": 24,
    "evoprompt": 20,
    "dspy": 20,
    "mipro": 20,
    "textgrad": 22,
    "gepa": 24,
    "memapo": 24,
    "sepo": 24,
    "maspo": 22,
    "autopdl": 22,
    "promptomatix": 18,
    "promptolution": 18,
    "crispo": 18,
}

ABSTRACT_BONUS_RULES = [
    (r"\bbenchmark|\bdataset|\bvalidation|\btest set|\bheld-out", 6, "reports evaluation data"),
    (r"\bbaseline|\boutperform|\bablation", 6, "reports comparative evaluation"),
    (r"\bcost|\blatency|\befficient|\befficiency", 5, "mentions cost/efficiency"),
    (r"\bfail|\bfailure|\boverfit|\boverfitting|\brobust", 8, "mentions failure/robustness"),
    (r"\bhuman feedback|\bpreference feedback|\bpreference", 6, "uses feedback/preference signal"),
    (r"\bcode:|github\.com", 6, "mentions code availability"),
    (r"\bgeneraliz|\bcross-task|\btransfer", 6, "mentions generalization/transfer"),
]

NEGATIVE_RULES = [
    (r"visual prompt tuning|soft prompt tuning|prefix tuning|prefix-tuning", -60, "soft/visual prompt tuning"),
    (r"text-to-image|text to image|image generation|diffusion model|diffusion models", -42, "image/diffusion prompt domain"),
    (r"text-to-video|text to video|video generation|segmentation", -36, "video/segmentation prompt domain"),
    (r"vision-language|vision language|\bvlm\b|multimodal", -22, "vision/multimodal domain"),
    (r"autonomous driving|robotics|robotic", -18, "robotics/autonomy application"),
    (r"protein|molecule|molecular|quantum|medical image", -18, "distant scientific application"),
]

HARD_TOPIC_RULE = re.compile(
    r"prompt optimization|prompt optimizer|automatic prompt engineering|"
    r"automated prompt engineering|prompt evolution|self[- ]evolving prompt|"
    r"textual gradients?|natural language gradient|semantic gradient|"
    r"system prompt|agentic prompt|agent prompt|multi-agent prompt|"
    r"prompt rewriting|prompt refinement|prompt selection|prompt evaluation|"
    r"prompt overfitting|context engineering|instruction optimization|"
    r"instruction induction|autoprompt|rlprompt|grips|protegi|opro|"
    r"promptbreeder|evoprompt|dspy|mipro|textgrad|gepa|memapo|"
    r"sepo|maspo|autopdl|promptomatix|promptolution|crispo",
    re.IGNORECASE,
)


def load_papers(path: Path) -> list[ArxivPaper]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("input JSON must contain a list of paper objects")

    papers: list[ArxivPaper] = []
    for item in raw:
        if not isinstance(item, Mapping):
            continue
        papers.append(ArxivPaper(**dict(item)))
    return papers


def focus_score(paper: ArxivPaper) -> tuple[int, list[str]]:
    title = _normalize(paper.title)
    abstract = _normalize(paper.abstract)
    body = f"{title} {abstract}"
    score = int(paper.score) + RELEVANCE_BONUS.get(paper.relevance, 0)
    reasons: list[str] = []

    if paper.inventory_status == "existing":
        score += 8
        reasons.append("already in source inventory")

    query_count = len(set(paper.matched_query_labels))
    if query_count >= 3:
        score += min(18, query_count * 3)
        reasons.append(f"matched {query_count} query channels")

    for category in paper.method_categories:
        bonus = METHOD_BONUS.get(category, 0)
        if bonus:
            score += bonus

    if paper.method_categories:
        top_methods = sorted(
            paper.method_categories,
            key=lambda category: -METHOD_BONUS.get(category, 0),
        )[:3]
        reasons.extend(top_methods)

    for pattern, bonus, reason in TITLE_BONUS_RULES:
        if re.search(pattern, title):
            score += bonus
            reasons.append(reason)

    for method_name, bonus in NAMED_METHOD_BONUS.items():
        if method_name in body:
            score += bonus
            reasons.append(f"mentions {method_name}")

    for pattern, bonus, reason in ABSTRACT_BONUS_RULES:
        if re.search(pattern, body):
            score += bonus
            reasons.append(reason)

    for pattern, penalty, reason in NEGATIVE_RULES:
        if re.search(pattern, body):
            score += penalty
            reasons.append(f"penalty: {reason}")

    if not HARD_TOPIC_RULE.search(body):
        score -= 50
        reasons.append("penalty: no direct project topic signal")

    if paper.matched_query_labels == ["broad-llm-prompt-optimization"]:
        score -= 24
        reasons.append("penalty: broad query only")

    return score, _unique(reasons)


def select_top_papers(
    papers: Sequence[ArxivPaper],
    top_n: int,
    min_score: Optional[int] = None,
    include_low: bool = False,
) -> list[tuple[ArxivPaper, int, list[str]]]:
    ranked: list[tuple[ArxivPaper, int, list[str]]] = []
    for paper in papers:
        if not include_low and paper.relevance == "low":
            continue
        score, reasons = focus_score(paper)
        if min_score is not None and score < min_score:
            continue
        ranked.append((paper, score, reasons))

    ranked.sort(
        key=lambda item: (
            -item[1],
            item[0].inventory_status != "existing",
            -int(item[0].score),
            item[0].title.lower(),
        )
    )
    return ranked[:top_n]


def write_outputs(
    ranked: Sequence[tuple[ArxivPaper, int, list[str]]],
    input_path: Path,
    output_dir: Path,
    prefix: str,
) -> Mapping[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = output_dir / f"{prefix}_{timestamp}.json"
    csv_path = output_dir / f"{prefix}_{timestamp}.csv"
    markdown_path = output_dir / f"{prefix}_{timestamp}.md"
    inventory_rows_path = output_dir / f"{prefix}_inventory_rows_{timestamp}.md"

    json_rows = [
        {
            **paper.__dict__,
            "focus_score": score,
            "focus_reasons": reasons,
        }
        for paper, score, reasons in ranked
    ]
    json_path.write_text(
        json.dumps(json_rows, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_csv(csv_path, ranked)
    markdown_path.write_text(
        render_markdown(ranked, input_path),
        encoding="utf-8",
    )
    inventory_rows_path.write_text(
        render_inventory_rows(
            [paper for paper, _score, _reasons in ranked if paper.inventory_status == "new"]
        ),
        encoding="utf-8",
    )

    return {
        "json": json_path,
        "csv": csv_path,
        "markdown": markdown_path,
        "inventory_rows": inventory_rows_path,
    }


def write_csv(
    path: Path,
    ranked: Sequence[tuple[ArxivPaper, int, list[str]]],
) -> None:
    fieldnames = [
        "rank",
        "focus_score",
        "relevance",
        "arxiv_score",
        "inventory_status",
        "arxiv_id",
        "title",
        "published",
        "updated",
        "primary_category",
        "categories",
        "method_categories",
        "matched_query_labels",
        "focus_reasons",
        "abs_url",
        "authors",
        "abstract",
    ]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for rank, (paper, score, reasons) in enumerate(ranked, start=1):
            writer.writerow(
                {
                    "rank": rank,
                    "focus_score": score,
                    "relevance": paper.relevance,
                    "arxiv_score": paper.score,
                    "inventory_status": paper.inventory_status,
                    "arxiv_id": paper.arxiv_id,
                    "title": paper.title,
                    "published": paper.published,
                    "updated": paper.updated,
                    "primary_category": paper.primary_category,
                    "categories": "; ".join(paper.categories),
                    "method_categories": "; ".join(paper.method_categories),
                    "matched_query_labels": "; ".join(paper.matched_query_labels),
                    "focus_reasons": "; ".join(reasons[:8]),
                    "abs_url": paper.abs_url,
                    "authors": "; ".join(paper.authors),
                    "abstract": paper.abstract,
                }
            )


def render_markdown(
    ranked: Sequence[tuple[ArxivPaper, int, list[str]]],
    input_path: Path,
) -> str:
    counts = {
        "existing": sum(1 for paper, _score, _reasons in ranked if paper.inventory_status == "existing"),
        "new": sum(1 for paper, _score, _reasons in ranked if paper.inventory_status == "new"),
        "high": sum(1 for paper, _score, _reasons in ranked if paper.relevance == "high"),
        "medium": sum(1 for paper, _score, _reasons in ranked if paper.relevance == "medium"),
        "low": sum(1 for paper, _score, _reasons in ranked if paper.relevance == "low"),
    }
    lines = [
        "# Focused arXiv Prompt Optimization Shortlist",
        "",
        f"Generated at: {datetime.now(timezone.utc).isoformat()}",
        f"Input: `{input_path}`",
        "",
        "This is a deterministic triage shortlist for human skim reading, not a",
        "research conclusion. The focus score favors direct relevance to prompt",
        "optimization/evolution and penalizes distant visual/diffusion prompt domains.",
        "",
        "## Summary",
        "",
        f"- Papers selected: {len(ranked)}",
        f"- New vs existing source inventory: {counts['new']} new / {counts['existing']} existing",
        f"- Relevance labels: {counts['high']} high / {counts['medium']} medium / {counts['low']} low",
        "",
        "## Shortlist",
        "",
        "| rank | focus_score | arxiv_score | status | arxiv_id | title | year | methods | reasons |",
        "| ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for rank, (paper, score, reasons) in enumerate(ranked, start=1):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(rank),
                    str(score),
                    str(paper.score),
                    paper.inventory_status,
                    f"[{_md_cell(paper.arxiv_id)}]({paper.abs_url})",
                    _md_cell(paper.title),
                    _paper_year(paper),
                    _md_cell("; ".join(paper.method_categories[:5])),
                    _md_cell("; ".join(reasons[:5])),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Rerank broad arXiv candidates into a focused top-N shortlist."
    )
    parser.add_argument("input_json", type=Path, help="JSON output from arxiv_prompt_paper_search.py")
    parser.add_argument("--top-n", type=int, default=DEFAULT_TOP_N)
    parser.add_argument("--min-score", type=int, default=None)
    parser.add_argument("--include-low", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--prefix", default="arxiv_focus_top100")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    if args.top_n < 1:
        parser.error("--top-n must be >= 1")

    papers = load_papers(args.input_json)
    ranked = select_top_papers(
        papers,
        top_n=args.top_n,
        min_score=args.min_score,
        include_low=args.include_low,
    )
    output_paths = write_outputs(
        ranked,
        input_path=args.input_json,
        output_dir=args.output_dir,
        prefix=args.prefix,
    )

    print(
        f"Selected {len(ranked)} papers from {len(papers)} candidates "
        f"({sum(1 for paper, _, _ in ranked if paper.inventory_status == 'new')} new)."
    )
    for label, path in output_paths.items():
        print(f"{label}: {path}")
    return 0


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().lower()


def _unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _paper_year(paper: ArxivPaper) -> str:
    date_text = paper.published or paper.updated
    return date_text[:4] if len(date_text) >= 4 else ""


def _md_cell(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().replace("|", "\\|")


if __name__ == "__main__":
    raise SystemExit(main())
