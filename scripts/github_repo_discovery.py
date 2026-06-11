"""Discover GitHub repositories for prompt optimization research.

The script uses GitHub's official REST Search API instead of scraping HTML.
Results are deduplicated, lightly scored for research relevance, and exported
as local candidate artifacts. A candidate is not evidence until it is manually
skimmed and entered into the source inventory or a structured note.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional

ENV_GITHUB_TOKEN = "GITHUB_TOKEN"
ENV_GH_TOKEN = "GH_TOKEN"

DEFAULT_OUTPUT_DIR = Path("local_sources/raw/github_repo_discovery")
DEFAULT_PER_PAGE = 50
DEFAULT_MAX_PAGES = 1
DEFAULT_MIN_SCORE = 8.0
DEFAULT_RATE_LIMIT_MAX_WAIT_SECONDS = 90.0
GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"
GITHUB_API_VERSION = "2022-11-28"


@dataclass(frozen=True)
class SearchSpec:
    label: str
    query: str


@dataclass(frozen=True)
class SearchRunConfig:
    per_page: int
    max_pages: int
    sort: str
    order: str
    sleep_seconds: float
    min_score: float
    output_dir: Path
    run_id: str
    rate_limit_max_wait_seconds: float


@dataclass(frozen=True)
class SearchRunResult:
    generated_at: str
    raw_items: int
    unique_repositories: int
    kept_repositories: int
    output_json: Path
    output_csv: Path
    output_markdown: Path
    output_json_sha256: str
    errors: list[dict[str, str]]


class GitHubAPIError(RuntimeError):
    """Raised when the GitHub API request cannot be completed."""


DEFAULT_SEARCH_SPECS: tuple[SearchSpec, ...] = (
    SearchSpec("automatic-prompt-optimization", "automatic prompt optimization in:name,description,readme"),
    SearchSpec("prompt-optimization", "prompt optimization in:name,description,readme"),
    SearchSpec("prompt-optimizer", "prompt optimizer in:name,description,readme"),
    SearchSpec("automatic-prompt-engineering", "automatic prompt engineering in:name,description,readme"),
    SearchSpec("instruction-optimization", "instruction optimization llm in:name,description,readme"),
    SearchSpec("prompt-rewriting", "prompt rewriting llm in:name,description,readme"),
    SearchSpec("system-prompt-optimization", "system prompt optimization in:name,description,readme"),
    SearchSpec("agent-prompt-optimization", "agent prompt optimization in:name,description,readme"),
    SearchSpec("rag-prompt-optimization", "RAG prompt optimization in:name,description,readme"),
    SearchSpec("context-engineering", "context engineering llm in:name,description,readme"),
    SearchSpec("self-evolving-prompt", "self evolving prompt in:name,description,readme"),
    SearchSpec("self-evolving-prompt-hyphen", "self-evolving prompt in:name,description,readme"),
    SearchSpec("prompt-evolution", "prompt evolution llm in:name,description,readme"),
    SearchSpec("reflective-prompt-evolution", "reflective prompt evolution in:name,description,readme"),
    SearchSpec("promptbreeder", "PromptBreeder in:name,description,readme"),
    SearchSpec("evoprompt", "EvoPrompt in:name,description,readme"),
    SearchSpec("opro", "OPRO prompt optimization in:name,description,readme"),
    SearchSpec("protegi", "ProTeGi prompt in:name,description,readme"),
    SearchSpec("textgrad", "TextGrad in:name,description,readme"),
    SearchSpec("dspy", "DSPy optimizer prompt in:name,description,readme"),
    SearchSpec("mipro", "MIPRO DSPy in:name,description,readme"),
    SearchSpec("gepa", "GEPA prompt in:name,description,readme"),
    SearchSpec("rlprompt", "RLPrompt in:name,description,readme"),
    SearchSpec("autoprompt", "AutoPrompt language model in:name,description,readme"),
    SearchSpec("prompt-eval", "prompt eval llm in:name,description,readme"),
    SearchSpec("prompt-benchmark", "prompt benchmark llm in:name,description,readme"),
    SearchSpec("prompt-regression-testing", "prompt regression testing in:name,description,readme"),
    SearchSpec("llm-as-judge-prompt", "LLM as judge prompt eval in:name,description,readme"),
    SearchSpec("prompt-management", "prompt management llm in:name,description,readme"),
    SearchSpec("prompt-versioning", "prompt versioning llm in:name,description,readme"),
    SearchSpec("prompt-observability", "prompt observability in:name,description,readme"),
    SearchSpec("prompt-registry", "prompt registry llm in:name,description,readme"),
    SearchSpec("promptfoo", "promptfoo in:name,description,readme"),
    SearchSpec("langfuse-prompt", "Langfuse prompt in:name,description,readme"),
    SearchSpec("langsmith-prompt", "LangSmith prompt in:name,description,readme"),
    SearchSpec("humanloop-prompt", "Humanloop prompt in:name,description,readme"),
    SearchSpec("phoenix-prompt-optimization", "Phoenix prompt optimization in:name,description,readme"),
    SearchSpec("parea-prompt", "Parea prompt eval in:name,description,readme"),
    SearchSpec("prompt-injection-eval", "prompt injection eval in:name,description,readme"),
    SearchSpec("tool-use-prompt-optimization", "tool use prompt optimization in:name,description,readme"),
)

RELEVANCE_PHRASE_WEIGHTS: tuple[tuple[str, float], ...] = (
    ("automatic prompt optimization", 14.0),
    ("automatic prompt engineering", 13.0),
    ("prompt optimization", 12.0),
    ("prompt optimizer", 12.0),
    ("prompt evolution", 11.0),
    ("self-evolving prompt", 11.0),
    ("self evolving prompt", 11.0),
    ("reflective prompt evolution", 11.0),
    ("system prompt optimization", 10.0),
    ("agent prompt optimization", 10.0),
    ("instruction optimization", 9.0),
    ("prompt rewriting", 8.0),
    ("textual gradient", 8.0),
    ("llm as judge", 7.0),
    ("prompt management", 7.0),
    ("prompt versioning", 7.0),
    ("prompt observability", 7.0),
    ("prompt registry", 7.0),
    ("prompt benchmark", 7.0),
    ("prompt regression", 7.0),
    ("context engineering", 6.0),
    ("rag prompt", 6.0),
    ("tool use prompt", 6.0),
)

KNOWN_METHOD_WEIGHTS: tuple[tuple[str, float], ...] = (
    ("promptbreeder", 12.0),
    ("evoprompt", 10.0),
    ("protegi", 10.0),
    ("textgrad", 10.0),
    ("dspy", 9.0),
    ("mipro", 9.0),
    ("gepa", 9.0),
    ("opro", 8.0),
    ("rlprompt", 8.0),
    ("autoprompt", 6.0),
    ("promptfoo", 7.0),
    ("langfuse", 6.0),
    ("langsmith", 6.0),
    ("humanloop", 6.0),
    ("parea", 5.0),
)


def load_dotenv(path: Path) -> None:
    """Load simple KEY=VALUE pairs from a dotenv file without overwriting env."""
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def resolve_github_token() -> str:
    """Return a GitHub token from supported environment variables, if present."""
    return os.getenv(ENV_GITHUB_TOKEN, "").strip() or os.getenv(ENV_GH_TOKEN, "").strip()


class GitHubSearchClient:
    """Small GitHub Search API client using only the standard library."""

    def __init__(
        self,
        token: str = "",
        sleep_seconds: float = 1.0,
        rate_limit_max_wait_seconds: float = DEFAULT_RATE_LIMIT_MAX_WAIT_SECONDS,
    ) -> None:
        self.token = token
        self.sleep_seconds = sleep_seconds
        self.rate_limit_max_wait_seconds = rate_limit_max_wait_seconds

    def search_repositories(
        self,
        query: str,
        page: int,
        per_page: int,
        sort: str,
        order: str,
    ) -> dict[str, Any]:
        params = {
            "q": query,
            "page": str(page),
            "per_page": str(per_page),
            "sort": sort,
            "order": order,
        }
        url = f"{GITHUB_SEARCH_URL}?{urllib.parse.urlencode(params)}"
        return self._get_json(url)

    def _get_json(self, url: str) -> dict[str, Any]:
        if self.sleep_seconds > 0:
            time.sleep(self.sleep_seconds)

        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "prompt-evolution-repo-discovery",
            "X-GitHub-Api-Version": GITHUB_API_VERSION,
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        request = urllib.request.Request(url, headers=headers, method="GET")
        return self._open_json(request, retry_on_rate_limit=True)

    def _open_json(
        self,
        request: urllib.request.Request,
        retry_on_rate_limit: bool,
    ) -> dict[str, Any]:
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            if retry_on_rate_limit and exc.code in {403, 429}:
                wait_seconds = _rate_limit_wait_seconds(exc.headers)
                if 0 < wait_seconds <= self.rate_limit_max_wait_seconds:
                    time.sleep(wait_seconds)
                    return self._open_json(request, retry_on_rate_limit=False)

            response_text = exc.read().decode("utf-8", errors="replace")
            raise GitHubAPIError(f"GitHub API HTTP {exc.code}: {response_text}") from exc
        except urllib.error.URLError as exc:
            raise GitHubAPIError(f"GitHub API request failed: {exc}") from exc

        try:
            decoded = json.loads(body)
        except json.JSONDecodeError as exc:
            raise GitHubAPIError("GitHub API returned non-JSON response") from exc

        if not isinstance(decoded, dict):
            raise GitHubAPIError("GitHub API returned a non-object JSON response")

        return decoded


def discover_repositories(
    specs: Iterable[SearchSpec],
    client: GitHubSearchClient,
    config: SearchRunConfig,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, str]], dict[str, Any]]:
    """Run all search specs and return kept repositories plus errors and stats."""
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    raw_candidates: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    executed_queries: list[dict[str, Any]] = []

    for spec in specs:
        spec_raw_count = 0
        for page in range(1, config.max_pages + 1):
            try:
                payload = client.search_repositories(
                    query=spec.query,
                    page=page,
                    per_page=config.per_page,
                    sort=config.sort,
                    order=config.order,
                )
            except GitHubAPIError as exc:
                errors.append({"query": spec.query, "page": str(page), "error": str(exc)})
                break

            items = payload.get("items", [])
            if not isinstance(items, list):
                errors.append(
                    {
                        "query": spec.query,
                        "page": str(page),
                        "error": "GitHub response items was not a list",
                    }
                )
                break

            spec_raw_count += len(items)
            for item in items:
                if isinstance(item, Mapping):
                    raw_candidates.append(normalize_repository(item, spec, generated_at))

            if len(items) < config.per_page:
                break

        executed_queries.append(
            {
                "label": spec.label,
                "query": spec.query,
                "raw_items": spec_raw_count,
            }
        )

    unique_repositories = merge_duplicate_repositories(raw_candidates)
    unique_repositories.sort(
        key=lambda repo: (
            repo["relevance_score"],
            repo.get("stargazers_count") or 0,
        ),
        reverse=True,
    )
    kept_repositories = [
        repo for repo in unique_repositories if repo["relevance_score"] >= config.min_score
    ]
    kept_repositories.sort(
        key=lambda repo: (
            repo["relevance_score"],
            repo.get("stargazers_count") or 0,
        ),
        reverse=True,
    )

    stats = {
        "generated_at": generated_at,
        "raw_items": len(raw_candidates),
        "unique_repositories": len(unique_repositories),
        "kept_repositories": len(kept_repositories),
        "min_score": config.min_score,
        "queries": executed_queries,
    }
    return kept_repositories, unique_repositories, errors, stats


def normalize_repository(
    item: Mapping[str, Any],
    spec: SearchSpec,
    generated_at: str,
) -> dict[str, Any]:
    """Normalize a GitHub repository search result into a source candidate."""
    full_name = str(item.get("full_name", "")).strip()
    owner = item.get("owner") if isinstance(item.get("owner"), Mapping) else {}
    topics = sorted(str(topic) for topic in (item.get("topics") or []))
    license_value = item.get("license") if isinstance(item.get("license"), Mapping) else {}

    repo = {
        "source_id": build_source_id(full_name),
        "type": "repo",
        "status": "candidate",
        "novelty_status": "unknown",
        "source_channel": "github",
        "title": full_name,
        "full_name": full_name,
        "owner": str(owner.get("login", "")),
        "name": str(item.get("name", "")),
        "url": str(item.get("html_url", "")),
        "description": str(item.get("description") or ""),
        "language": str(item.get("language") or ""),
        "topics": topics,
        "license_spdx": str(license_value.get("spdx_id") or ""),
        "stargazers_count": int(item.get("stargazers_count") or 0),
        "forks_count": int(item.get("forks_count") or 0),
        "open_issues_count": int(item.get("open_issues_count") or 0),
        "is_fork": bool(item.get("fork")),
        "is_archived": bool(item.get("archived")),
        "created_at": str(item.get("created_at") or ""),
        "updated_at": str(item.get("updated_at") or ""),
        "pushed_at": str(item.get("pushed_at") or ""),
        "default_branch": str(item.get("default_branch") or ""),
        "matched_queries": [spec.label],
        "matched_query_strings": [spec.query],
        "suggested_by": "automated-github-search",
        "linked_issue": "",
        "local_note": "GitHub Search API candidate; requires manual skim before source_inventory inclusion.",
        "decision": "triage",
        "discovered_at": generated_at,
        "raw_snapshot_path": "",
        "raw_snapshot_sha256": "",
    }

    score, keyword_hits = score_repository(repo)
    repo["relevance_score"] = score
    repo["keyword_hits"] = keyword_hits
    repo["relevance"] = relevance_bucket(score)
    repo["method_category"] = classify_method_category(repository_text(repo))
    repo["optimization_object"] = infer_optimization_object(repository_text(repo))
    repo["feedback_signal"] = infer_feedback_signal(repository_text(repo))
    repo["selection_method"] = infer_selection_method(repository_text(repo))
    return repo


def merge_duplicate_repositories(repositories: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplicate repositories by full name while preserving matched queries."""
    merged: dict[str, dict[str, Any]] = {}
    for repo in repositories:
        key = str(repo.get("full_name", "")).lower()
        if not key:
            continue

        if key not in merged:
            merged[key] = dict(repo)
            continue

        existing = merged[key]
        existing["matched_queries"] = sorted(
            set(existing.get("matched_queries", [])) | set(repo.get("matched_queries", []))
        )
        existing["matched_query_strings"] = sorted(
            set(existing.get("matched_query_strings", []))
            | set(repo.get("matched_query_strings", []))
        )
        existing["keyword_hits"] = sorted(
            set(existing.get("keyword_hits", [])) | set(repo.get("keyword_hits", []))
        )
        if repo.get("relevance_score", 0) > existing.get("relevance_score", 0):
            existing["relevance_score"] = repo["relevance_score"]
            existing["relevance"] = repo["relevance"]
            existing["method_category"] = repo["method_category"]
            existing["optimization_object"] = repo["optimization_object"]
            existing["feedback_signal"] = repo["feedback_signal"]
            existing["selection_method"] = repo["selection_method"]

    return list(merged.values())


def score_repository(repo: Mapping[str, Any]) -> tuple[float, list[str]]:
    """Assign a lightweight relevance score based on metadata and keywords."""
    text = repository_text(repo)
    score = 0.0
    keyword_hits: list[str] = []

    for phrase, weight in RELEVANCE_PHRASE_WEIGHTS:
        if phrase in text:
            score += weight
            keyword_hits.append(phrase)

    for method, weight in KNOWN_METHOD_WEIGHTS:
        if method in text:
            score += weight
            keyword_hits.append(method)

    if "prompt" in text and "optim" in text:
        score += 6.0
        keyword_hits.append("prompt+optim")
    if "prompt" in text and any(term in text for term in ("eval", "judge", "benchmark")):
        score += 5.0
        keyword_hits.append("prompt+eval")
    if "prompt" in text and any(term in text for term in ("agent", "rag", "context", "tool")):
        score += 4.0
        keyword_hits.append("prompt+agent-context")
    if "llm" in text and "prompt" in text:
        score += 3.0
        keyword_hits.append("llm+prompt")

    metadata_signal = score
    stars = int(repo.get("stargazers_count") or 0)
    forks = int(repo.get("forks_count") or 0)
    popularity_bonus = min(math.log10(stars + 1) * 2.0, 8.0)
    popularity_bonus += min(math.log10(forks + 1), 3.0)
    if metadata_signal > 0:
        score += popularity_bonus
    else:
        score += min(popularity_bonus, 2.0)

    if bool(repo.get("is_archived")):
        score -= 8.0
        keyword_hits.append("archived-penalty")
    if bool(repo.get("is_fork")):
        score -= 4.0
        keyword_hits.append("fork-penalty")

    return round(max(score, 0.0), 2), sorted(set(keyword_hits))


def repository_text(repo: Mapping[str, Any]) -> str:
    topics = repo.get("topics") or []
    if not isinstance(topics, list):
        topics = []
    parts = [
        str(repo.get("full_name", "")),
        str(repo.get("description", "")),
        str(repo.get("language", "")),
        " ".join(str(topic) for topic in topics),
    ]
    return normalize_text(" ".join(parts))


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("_", " ").replace("-", " ")).strip().lower()


def relevance_bucket(score: float) -> str:
    if score >= 24:
        return "high"
    if score >= 12:
        return "medium"
    return "low"


def classify_method_category(text: str) -> str:
    if any(term in text for term in ("promptbreeder", "evoprompt", "evolution", "self evolving")):
        return "evolutionary-self-evolving"
    if any(term in text for term in ("dspy", "mipro", "teleprompter")):
        return "prompt-as-program"
    if any(term in text for term in ("textgrad", "textual gradient", "critique")):
        return "textual-gradient-critique"
    if any(term in text for term in ("prompt management", "prompt version", "registry", "observability")):
        return "prompt-management-observability"
    if any(term in text for term in ("promptfoo", "eval", "judge", "benchmark", "regression")):
        return "eval-benchmark-governance"
    if any(term in text for term in ("agent", "tool use", "context engineering", "rag")):
        return "agent-context-optimization"
    if any(
        term in text
        for term in (
            "automatic prompt optimization",
            "automatic prompt engineering",
            "prompt optimization",
            "prompt optimizer",
            "instruction optimization",
        )
    ):
        return "automatic-prompt-optimization"
    return "other"


def infer_optimization_object(text: str) -> str:
    if "system prompt" in text:
        return "system_prompt"
    if "agent" in text or "tool use" in text:
        return "agent_prompt_or_tool_policy"
    if "rag" in text or "context engineering" in text:
        return "context_or_rag_prompt"
    if "example" in text or "few shot" in text:
        return "instruction_and_examples"
    if "prompt" in text:
        return "prompt_text"
    return "unknown"


def infer_feedback_signal(text: str) -> str:
    if any(term in text for term in ("human feedback", "preference", "rlhf")):
        return "human_feedback"
    if any(term in text for term in ("judge", "llm as judge", "critique", "textual gradient")):
        return "llm_feedback"
    if any(term in text for term in ("eval", "benchmark", "test", "regression")):
        return "metric_or_test_feedback"
    return "unknown"


def infer_selection_method(text: str) -> str:
    if any(term in text for term in ("beam", "search")):
        return "search"
    if any(term in text for term in ("evolution", "genetic", "promptbreeder", "evoprompt")):
        return "evolutionary"
    if any(term in text for term in ("rl", "reinforcement")):
        return "reinforcement_learning"
    if any(term in text for term in ("optimizer", "optimization", "optim")):
        return "optimizer"
    return "unknown"


def build_source_id(full_name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", full_name.strip().lower()).strip("-")
    return f"repo-{slug}" if slug else "repo-unknown"


def write_outputs(
    repositories: list[dict[str, Any]],
    all_repositories: list[dict[str, Any]],
    errors: list[dict[str, str]],
    stats: Mapping[str, Any],
    config: SearchRunConfig,
    token_present: bool,
) -> SearchRunResult:
    config.output_dir.mkdir(parents=True, exist_ok=True)

    base_path = config.output_dir / config.run_id
    json_path = base_path.with_suffix(".json")
    csv_path = base_path.with_suffix(".csv")
    markdown_path = base_path.with_suffix(".md")

    payload = {
        "metadata": {
            **dict(stats),
            "token_present": token_present,
            "sort": config.sort,
            "order": config.order,
            "per_page": config.per_page,
            "max_pages": config.max_pages,
            "candidate_warning": "Candidates require manual skim before being used as evidence.",
        },
        "errors": errors,
        "repositories": repositories,
        "all_unique_repositories": all_repositories,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    csv_path.write_text(format_csv(all_repositories, min_score=config.min_score), encoding="utf-8")
    markdown_path.write_text(
        format_markdown_report(repositories, errors, stats, config, token_present),
        encoding="utf-8",
    )

    return SearchRunResult(
        generated_at=str(stats["generated_at"]),
        raw_items=int(stats["raw_items"]),
        unique_repositories=int(stats["unique_repositories"]),
        kept_repositories=int(stats["kept_repositories"]),
        output_json=json_path,
        output_csv=csv_path,
        output_markdown=markdown_path,
        output_json_sha256=sha256_file(json_path),
        errors=errors,
    )


def format_csv(repositories: list[dict[str, Any]], min_score: float = DEFAULT_MIN_SCORE) -> str:
    fields = [
        "source_id",
        "kept_by_min_score",
        "relevance_score",
        "relevance",
        "method_category",
        "full_name",
        "url",
        "description",
        "language",
        "stargazers_count",
        "forks_count",
        "updated_at",
        "pushed_at",
        "license_spdx",
        "keyword_hits",
        "matched_queries",
    ]
    rows: list[dict[str, Any]] = []
    for repo in repositories:
        row = {field: repo.get(field, "") for field in fields}
        row["kept_by_min_score"] = repo.get("relevance_score", 0) >= min_score
        row["keyword_hits"] = ";".join(repo.get("keyword_hits", []))
        row["matched_queries"] = ";".join(repo.get("matched_queries", []))
        rows.append(row)

    output_lines: list[str] = []
    writer = csv.DictWriter(_ListWriter(output_lines), fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return "".join(output_lines)


def format_markdown_report(
    repositories: list[dict[str, Any]],
    errors: list[dict[str, str]],
    stats: Mapping[str, Any],
    config: SearchRunConfig,
    token_present: bool,
    top_n: int = 50,
) -> str:
    category_counts: dict[str, int] = {}
    for repo in repositories:
        category = str(repo.get("method_category", "other"))
        category_counts[category] = category_counts.get(category, 0) + 1

    lines = [
        "# GitHub Repository Discovery",
        "",
        f"- Generated at: {stats['generated_at']}",
        f"- Raw items: {stats['raw_items']}",
        f"- Unique repositories: {stats['unique_repositories']}",
        f"- Kept repositories: {stats['kept_repositories']} (min score {config.min_score})",
        f"- Queries executed: {len(stats['queries'])}",
        f"- GitHub token present: {'yes' if token_present else 'no'}",
        "",
        "These are search candidates, not research evidence. Manually skim a repository before adding it to `docs/source_inventory.md`.",
        "",
        "## Coverage",
        "",
        "| method_category | count |",
        "| --- | ---: |",
    ]
    for category, count in sorted(category_counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| {category} | {count} |")

    lines.extend(
        [
            "",
            f"## Top {min(top_n, len(repositories))} Candidates",
            "",
            "| score | repo | stars | updated | category | keyword_hits |",
            "| ---: | --- | ---: | --- | --- | --- |",
        ]
    )
    for repo in repositories[:top_n]:
        hits = ", ".join(repo.get("keyword_hits", [])[:5])
        lines.append(
            "| {score} | [{name}]({url}) | {stars} | {updated} | {category} | {hits} |".format(
                score=repo.get("relevance_score", ""),
                name=repo.get("full_name", ""),
                url=repo.get("url", ""),
                stars=repo.get("stargazers_count", ""),
                updated=str(repo.get("updated_at", ""))[:10],
                category=repo.get("method_category", ""),
                hits=hits.replace("|", "\\|"),
            )
        )

    lines.extend(["", "## Queries", "", "| label | raw_items | query |", "| --- | ---: | --- |"])
    for query in stats["queries"]:
        lines.append(
            f"| {query['label']} | {query['raw_items']} | `{query['query']}` |"
        )

    if errors:
        lines.extend(["", "## Errors", "", "| query | page | error |", "| --- | ---: | --- |"])
        for error in errors:
            message = error["error"].replace("|", "\\|").replace("\n", " ")[:240]
            lines.append(f"| `{error['query']}` | {error['page']} | {message} |")

    lines.append("")
    return "\n".join(lines)


class _ListWriter:
    """Tiny file-like adapter for csv writer."""

    def __init__(self, output_lines: list[str]) -> None:
        self.output_lines = output_lines

    def write(self, value: str) -> int:
        self.output_lines.append(value)
        return len(value)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _rate_limit_wait_seconds(headers: Mapping[str, str]) -> float:
    remaining = headers.get("X-RateLimit-Remaining", "")
    reset = headers.get("X-RateLimit-Reset", "")
    if remaining != "0" or not reset:
        return 0.0

    try:
        reset_at = int(reset)
    except ValueError:
        return 0.0

    return max(float(reset_at - int(time.time()) + 2), 0.0)


def build_search_specs(
    query_limit: Optional[int],
    extra_queries: Optional[list[str]],
) -> list[SearchSpec]:
    specs = list(DEFAULT_SEARCH_SPECS)
    if query_limit is not None:
        specs = specs[:query_limit]

    for index, query in enumerate(extra_queries or [], start=1):
        cleaned_query = query.strip()
        if cleaned_query:
            specs.append(SearchSpec(f"extra-{index}", cleaned_query))

    return specs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Discover GitHub repositories relevant to prompt optimization research."
    )
    parser.add_argument("--dotenv", default=".env", help="dotenv file to load before API calls")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="local output directory")
    parser.add_argument("--run-id", help="output filename stem; defaults to a UTC timestamp")
    parser.add_argument("--query-limit", type=int, help="run only the first N built-in queries")
    parser.add_argument(
        "--extra-query",
        action="append",
        default=[],
        help="extra GitHub repository search query; can be passed multiple times",
    )
    parser.add_argument("--per-page", type=int, default=DEFAULT_PER_PAGE, help="GitHub results per page")
    parser.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES, help="pages per query")
    parser.add_argument("--min-score", type=float, default=DEFAULT_MIN_SCORE, help="minimum relevance score")
    parser.add_argument("--sort", choices=("stars", "forks", "updated"), default="stars")
    parser.add_argument("--order", choices=("desc", "asc"), default="desc")
    parser.add_argument("--sleep-seconds", type=float, default=1.0, help="delay before each request")
    parser.add_argument(
        "--rate-limit-max-wait-seconds",
        type=float,
        default=DEFAULT_RATE_LIMIT_MAX_WAIT_SECONDS,
        help="maximum automatic wait when GitHub rate limit is hit",
    )
    parser.add_argument("--dry-run", action="store_true", help="print the query plan without API calls")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_dotenv(Path(args.dotenv))
    specs = build_search_specs(args.query_limit, args.extra_query)
    run_id = args.run_id or f"github_repo_discovery_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    config = SearchRunConfig(
        per_page=args.per_page,
        max_pages=args.max_pages,
        sort=args.sort,
        order=args.order,
        sleep_seconds=args.sleep_seconds,
        min_score=args.min_score,
        output_dir=Path(args.output_dir),
        run_id=run_id,
        rate_limit_max_wait_seconds=args.rate_limit_max_wait_seconds,
    )

    if config.per_page < 1 or config.per_page > 100:
        print(json.dumps({"ok": False, "error": "--per-page must be between 1 and 100"}))
        return 2
    if config.max_pages < 1:
        print(json.dumps({"ok": False, "error": "--max-pages must be >= 1"}))
        return 2
    if not specs:
        print(json.dumps({"ok": False, "error": "no search queries configured"}))
        return 2

    token = resolve_github_token()
    if args.dry_run:
        print(
            json.dumps(
                {
                    "ok": True,
                    "dry_run": True,
                    "token_present": bool(token),
                    "query_count": len(specs),
                    "queries": [spec.__dict__ for spec in specs],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    client = GitHubSearchClient(
        token=token,
        sleep_seconds=config.sleep_seconds,
        rate_limit_max_wait_seconds=config.rate_limit_max_wait_seconds,
    )
    repositories, all_repositories, errors, stats = discover_repositories(specs, client, config)
    result = write_outputs(
        repositories,
        all_repositories,
        errors,
        stats,
        config,
        token_present=bool(token),
    )
    print(
        json.dumps(
            {
                "ok": True,
                "generated_at": result.generated_at,
                "raw_items": result.raw_items,
                "unique_repositories": result.unique_repositories,
                "kept_repositories": result.kept_repositories,
                "output_json": str(result.output_json),
                "output_csv": str(result.output_csv),
                "output_markdown": str(result.output_markdown),
                "output_json_sha256": result.output_json_sha256,
                "error_count": len(result.errors),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
