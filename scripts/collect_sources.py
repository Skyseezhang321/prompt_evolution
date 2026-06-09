"""Collect public source candidates for prompt evolution research.

The script favors public APIs and RSS/Atom feeds over page scraping. It writes
ignored artifacts by default, so broad collection can stay separate from the
curated source inventory until a human skims and accepts candidates.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional, Sequence

DEFAULT_QUERIES = (
    "prompt 优化",
    "提示词优化",
    "自动提示词优化",
    "prompt 自进化",
    "提示词 自进化",
    "上下文工程 LLM",
    "智能体 prompt 优化",
    "automatic prompt optimization",
    "automatic prompt engineering",
    "prompt optimization",
    "prompt optimizer",
    "prompt evolution",
    "reflective prompt evolution",
    "self-evolving prompt",
    "self improving prompt",
    "LLM prompt versioning eval",
    "LLM prompt rollback",
    "context engineering LLM agents",
    "DSPy MIPRO prompt optimization",
    "GEPA prompt optimization",
    "PromptBreeder",
)

DEFAULT_CHANNELS = (
    "hackernews",
    "devto",
    "stackexchange",
    "rss",
)

OPTIONAL_CHANNELS = (
    "reddit",
    "web_search",
    "zhihu",
    "twitter_web",
    "x_api",
)

ALL_CHANNELS = DEFAULT_CHANNELS + OPTIONAL_CHANNELS

DEFAULT_DEVTO_TAGS = (
    "ai",
    "llm",
    "openai",
    "promptengineering",
    "machinelearning",
)

DEFAULT_STACKEXCHANGE_SITES = (
    "genai",
    "ai",
    "stackoverflow",
)

DEFAULT_RSS_FEEDS = (
    "https://aws.amazon.com/blogs/aws/feed/",
    "https://aws.amazon.com/blogs/machine-learning/feed/",
    "https://www.microsoft.com/en-us/research/feed/",
    "https://openai.com/news/rss.xml",
)

DEFAULT_WEB_DOMAINS = (
    "zhuanlan.zhihu.com",
    "zhihu.com",
    "x.com",
    "twitter.com",
    "medium.com",
    "substack.com",
)

BRAVE_DOMAIN_CHANNELS = {
    "zhihu": ("zhuanlan.zhihu.com", "zhihu.com"),
    "twitter_web": ("x.com", "twitter.com"),
}

RELEVANCE_TERMS = (
    "prompt 优化",
    "提示词优化",
    "自动提示词优化",
    "prompt 自进化",
    "提示词 自进化",
    "上下文工程",
    "智能体 prompt",
    "automatic prompt optimization",
    "automatic prompt engineering",
    "prompt optimization",
    "prompt optimizer",
    "prompt evolution",
    "prompt evolver",
    "self-evolving prompt",
    "self evolving prompt",
    "self-improving prompt",
    "reflective prompt evolution",
    "textual gradient",
    "llm-as-judge",
    "eval-driven",
    "prompt versioning",
    "prompt management",
    "prompt rollback",
    "prompt drift",
    "context engineering",
    "dspy",
    "mipro",
    "gepa",
    "promptbreeder",
    "opro",
    "protegi",
    "ape-style",
    "few-shot optimization",
)

TRACKING_PARAMS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "msclkid",
    "ref",
    "ref_src",
    "source",
    "spm",
    "utm_campaign",
    "utm_content",
    "utm_medium",
    "utm_source",
    "utm_term",
}

ENV_BRAVE_SEARCH_API_KEY = "BRAVE_SEARCH_API_KEY"
ENV_X_BEARER_TOKEN = "X_BEARER_TOKEN"
ENV_REDDIT_BEARER_TOKEN = "REDDIT_BEARER_TOKEN"
ENV_REDDIT_CLIENT_ID = "REDDIT_CLIENT_ID"
ENV_REDDIT_CLIENT_SECRET = "REDDIT_CLIENT_SECRET"
ENV_REDDIT_USER_AGENT = "REDDIT_USER_AGENT"
ENV_STACKEXCHANGE_KEY = "STACKEXCHANGE_KEY"
ENV_USER_AGENT = "SOURCE_SEARCH_USER_AGENT"
ENV_TIMEOUT_SECONDS = "SOURCE_SEARCH_TIMEOUT_SECONDS"

DEFAULT_USER_AGENT = "prompt-evolution-source-collector/0.1"
DEFAULT_TIMEOUT_SECONDS = 20.0


@dataclass
class SourceCandidate:
    channel: str
    type: str
    title: str
    url: str
    date: str = ""
    authors_or_org: str = ""
    summary: str = ""
    query: str = ""
    method_category: str = ""
    engagement: dict[str, Any] = field(default_factory=dict)
    matched_terms: list[str] = field(default_factory=list)
    relevance_score: int = 0
    rank_score: float = 0.0
    relevance: str = "low"
    status: str = "candidate"
    novelty_status: str = "unknown"
    decision: str = "needs skim"
    already_in_inventory: bool = False
    channels: list[str] = field(default_factory=list)
    queries: list[str] = field(default_factory=list)
    source_id: str = ""


class CollectionError(RuntimeError):
    """Raised when a channel request or parse step fails."""


def main(argv: Optional[Sequence[str]] = None) -> int:
    load_dotenv(Path.cwd() / ".env")
    args = parse_args(argv)
    queries = load_queries(args)
    channels = resolve_channels(args.channels)
    timeout = read_timeout()
    user_agent = os.getenv(ENV_USER_AGENT, DEFAULT_USER_AGENT).strip()

    if args.dry_run:
        print_dry_run(channels, queries, args)
        return 0

    inventory_urls = load_inventory_urls(Path(args.inventory))
    raw_candidates = collect_all(
        channels=channels,
        queries=queries,
        per_query=args.per_query,
        min_score=args.min_score,
        devto_tags=args.devto_tags,
        stackexchange_sites=args.stackexchange_sites,
        rss_feeds=args.rss_feeds,
        web_domains=args.web_domains,
        timeout=timeout,
        user_agent=user_agent,
        sleep_seconds=args.sleep,
        show_errors=args.show_errors,
    )
    candidates = deduplicate_candidates(raw_candidates)
    mark_existing_inventory(candidates, inventory_urls)
    if args.exclude_existing:
        candidates = [item for item in candidates if not item.already_in_inventory]

    candidates.sort(key=lambda item: item.rank_score, reverse=True)
    if args.max_results:
        candidates = candidates[: args.max_results]

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S")
    jsonl_path = output_dir / f"source_candidates_{stamp}.jsonl"
    md_path = output_dir / f"source_candidates_{stamp}.md"

    write_jsonl(jsonl_path, candidates)
    write_markdown(md_path, candidates, channels, queries)

    print(f"wrote {len(candidates)} candidates")
    print(f"jsonl: {jsonl_path}")
    print(f"markdown: {md_path}")
    print_channel_counts(candidates)
    return 0


def parse_args(argv: Optional[Sequence[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect prompt evolution source candidates by channel.",
    )
    parser.add_argument(
        "--channels",
        default=",".join(DEFAULT_CHANNELS),
        help=(
            "Comma-separated channels. Supported: "
            f"{', '.join(ALL_CHANNELS)}. Use 'all' to include optional API-backed channels."
        ),
    )
    parser.add_argument(
        "--query",
        action="append",
        default=[],
        help="Search query. Can be passed multiple times.",
    )
    parser.add_argument(
        "--queries-file",
        default="",
        help="UTF-8 text file with one query per line.",
    )
    parser.add_argument(
        "--per-query",
        type=int,
        default=10,
        help="Maximum records requested from each query-based channel.",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=0,
        help="Maximum deduplicated candidates to keep. 0 keeps all.",
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=1,
        help="Minimum local relevance score for keeping a candidate.",
    )
    parser.add_argument(
        "--devto-tags",
        nargs="*",
        default=list(DEFAULT_DEVTO_TAGS),
        help="DEV/Forem tags to pull before local keyword filtering.",
    )
    parser.add_argument(
        "--stackexchange-sites",
        nargs="*",
        default=list(DEFAULT_STACKEXCHANGE_SITES),
        help="Stack Exchange site parameters to search.",
    )
    parser.add_argument(
        "--rss-feeds",
        nargs="*",
        default=list(DEFAULT_RSS_FEEDS),
        help="RSS/Atom feed URLs to scan before local keyword filtering.",
    )
    parser.add_argument(
        "--web-domains",
        nargs="*",
        default=list(DEFAULT_WEB_DOMAINS),
        help=(
            "Domains searched by the web_search channel via Brave Search. "
            "The zhihu and twitter_web channels use their own fixed domain lists."
        ),
    )
    parser.add_argument(
        "--inventory",
        default="docs/source_inventory.md",
        help="Existing inventory markdown used to mark duplicate URLs.",
    )
    parser.add_argument(
        "--exclude-existing",
        action="store_true",
        help="Drop candidates whose normalized URL already appears in inventory.",
    )
    parser.add_argument(
        "--output-dir",
        default="artifacts/source_search",
        help="Directory for ignored search artifacts.",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.4,
        help="Delay between requests in seconds.",
    )
    parser.add_argument(
        "--show-errors",
        action="store_true",
        help="Print per-channel request failures to stderr.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned channels and queries without network calls.",
    )
    return parser.parse_args(argv)


def resolve_channels(raw_channels: str) -> list[str]:
    parts = [part.strip() for part in raw_channels.split(",") if part.strip()]
    if not parts:
        return list(DEFAULT_CHANNELS)
    if parts == ["all"]:
        return list(ALL_CHANNELS)

    unknown = sorted(set(parts) - set(ALL_CHANNELS))
    if unknown:
        raise SystemExit(f"unknown channel(s): {', '.join(unknown)}")
    return parts


def load_queries(args: argparse.Namespace) -> list[str]:
    queries: list[str] = []
    if args.queries_file:
        query_path = Path(args.queries_file)
        for line in query_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                queries.append(stripped)
    queries.extend(args.query)
    if not queries:
        queries.extend(DEFAULT_QUERIES)

    seen: set[str] = set()
    unique_queries: list[str] = []
    for query in queries:
        normalized = " ".join(query.split())
        key = normalized.lower()
        if normalized and key not in seen:
            unique_queries.append(normalized)
            seen.add(key)
    return unique_queries


def read_timeout() -> float:
    raw_value = os.getenv(ENV_TIMEOUT_SECONDS, "").strip()
    if not raw_value:
        return DEFAULT_TIMEOUT_SECONDS
    try:
        timeout = float(raw_value)
    except ValueError as exc:
        raise SystemExit(f"{ENV_TIMEOUT_SECONDS} must be a number") from exc
    if timeout <= 0:
        raise SystemExit(f"{ENV_TIMEOUT_SECONDS} must be greater than 0")
    return timeout


def print_dry_run(
    channels: Sequence[str],
    queries: Sequence[str],
    args: argparse.Namespace,
) -> None:
    print("channels:")
    for channel in channels:
        print(f"- {channel}")
    print("queries:")
    for query in queries:
        print(f"- {query}")
    print(f"per_query: {args.per_query}")
    print(f"min_score: {args.min_score}")


def load_dotenv(path: Path) -> None:
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


def collect_all(
    channels: Sequence[str],
    queries: Sequence[str],
    per_query: int,
    min_score: int,
    devto_tags: Sequence[str],
    stackexchange_sites: Sequence[str],
    rss_feeds: Sequence[str],
    web_domains: Sequence[str],
    timeout: float,
    user_agent: str,
    sleep_seconds: float,
    show_errors: bool,
) -> list[SourceCandidate]:
    candidates: list[SourceCandidate] = []

    for channel in channels:
        if channel == "devto":
            candidates.extend(
                collect_feed_like_channel(
                    channel_name=channel,
                    collector=lambda: collect_devto(
                        tags=devto_tags,
                        per_tag=per_query,
                        timeout=timeout,
                        user_agent=user_agent,
                        sleep_seconds=sleep_seconds,
                    ),
                    min_score=min_score,
                    show_errors=show_errors,
                )
            )
            continue

        if channel == "rss":
            candidates.extend(
                collect_feed_like_channel(
                    channel_name=channel,
                    collector=lambda: collect_rss_feeds(
                        feeds=rss_feeds,
                        timeout=timeout,
                        user_agent=user_agent,
                        sleep_seconds=sleep_seconds,
                    ),
                    min_score=min_score,
                    show_errors=show_errors,
                )
            )
            continue

        for query in queries:
            try:
                candidates.extend(
                    collect_query_channel(
                        channel=channel,
                        query=query,
                        per_query=per_query,
                        min_score=min_score,
                        stackexchange_sites=stackexchange_sites,
                        web_domains=web_domains,
                        timeout=timeout,
                        user_agent=user_agent,
                    )
                )
            except CollectionError as exc:
                if show_errors:
                    print(f"[{channel}] {query}: {exc}", file=sys.stderr)
            time.sleep(request_delay(channel, sleep_seconds))

    return candidates


def collect_feed_like_channel(
    channel_name: str,
    collector: Any,
    min_score: int,
    show_errors: bool,
) -> list[SourceCandidate]:
    try:
        return [
            item
            for item in collector()
            if score_and_keep(item, min_score=min_score)
        ]
    except CollectionError as exc:
        if show_errors:
            print(f"[{channel_name}] {exc}", file=sys.stderr)
        return []


def collect_query_channel(
    channel: str,
    query: str,
    per_query: int,
    min_score: int,
    stackexchange_sites: Sequence[str],
    web_domains: Sequence[str],
    timeout: float,
    user_agent: str,
) -> list[SourceCandidate]:
    if channel == "hackernews":
        items = collect_hackernews(query, per_query, timeout, user_agent)
    elif channel == "stackexchange":
        items = collect_stackexchange(
            query,
            per_query,
            stackexchange_sites,
            timeout,
            user_agent,
        )
    elif channel == "reddit":
        items = collect_reddit(query, per_query, timeout, user_agent)
    elif channel in {"web_search", "zhihu", "twitter_web"}:
        domains = BRAVE_DOMAIN_CHANNELS.get(channel, tuple(web_domains))
        items = collect_brave_web_search(
            query,
            per_query,
            timeout,
            user_agent,
            domains=domains,
            channel=channel,
        )
    elif channel == "x_api":
        items = collect_x_recent_search(query, per_query, timeout, user_agent)
    else:
        raise CollectionError(f"unsupported channel: {channel}")

    return [item for item in items if score_and_keep(item, min_score=min_score)]


def collect_hackernews(
    query: str,
    limit: int,
    timeout: float,
    user_agent: str,
) -> list[SourceCandidate]:
    data = get_json(
        "https://hn.algolia.com/api/v1/search_by_date",
        params={
            "query": query,
            "tags": "story",
            "hitsPerPage": clamp_limit(limit, 100),
        },
        timeout=timeout,
        user_agent=user_agent,
    )
    hits = ensure_list(data.get("hits"), "hackernews hits")
    items: list[SourceCandidate] = []
    for hit in hits:
        if not isinstance(hit, Mapping):
            continue
        object_id = string_value(hit.get("objectID"))
        url = string_value(hit.get("url"))
        if not url and object_id:
            url = f"https://news.ycombinator.com/item?id={object_id}"
        items.append(
            SourceCandidate(
                channel="hackernews",
                type="post",
                title=string_value(hit.get("title")),
                url=url,
                date=string_value(hit.get("created_at")),
                authors_or_org=string_value(hit.get("author")),
                summary=string_value(hit.get("story_text")),
                query=query,
                method_category="discussion_search",
                engagement={
                    "points": hit.get("points"),
                    "comments": hit.get("num_comments"),
                    "object_id": object_id,
                    "comments_url": (
                        f"https://news.ycombinator.com/item?id={object_id}"
                        if object_id
                        else ""
                    ),
                },
            )
        )
    return items


def request_delay(channel: str, requested_sleep: float) -> float:
    base_sleep = max(requested_sleep, 0)
    if channel in {"web_search", "zhihu", "twitter_web"}:
        return max(base_sleep, 1.0)
    return base_sleep


def collect_brave_web_search(
    query: str,
    limit: int,
    timeout: float,
    user_agent: str,
    domains: Sequence[str],
    channel: str,
) -> list[SourceCandidate]:
    api_key = os.getenv(ENV_BRAVE_SEARCH_API_KEY, "").strip()
    if not api_key:
        raise CollectionError(f"{channel} requires {ENV_BRAVE_SEARCH_API_KEY}")

    search_queries = build_domain_queries(query, domains)
    candidates: list[SourceCandidate] = []
    for search_query in search_queries:
        data = get_json(
            "https://api.search.brave.com/res/v1/web/search",
            params={
                "q": search_query,
                "count": clamp_limit(limit, 20),
            },
            timeout=timeout,
            user_agent=user_agent,
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": api_key,
            },
        )
        web = data.get("web") if isinstance(data.get("web"), Mapping) else {}
        results = ensure_list(web.get("results", []), "brave web results")
        for result in results:
            if not isinstance(result, Mapping):
                continue
            profile = result.get("profile") if isinstance(result.get("profile"), Mapping) else {}
            url = string_value(result.get("url"))
            candidates.append(
                SourceCandidate(
                    channel=channel,
                    type="post",
                    title=clean_text(string_value(result.get("title"))),
                    url=url,
                    date=string_value(result.get("age")),
                    authors_or_org=string_value(profile.get("name")) or domain_from_url(url),
                    summary=truncate(
                        clean_text(string_value(result.get("description"))),
                        500,
                    ),
                    query=search_query,
                    method_category="web_search",
                    engagement={
                        "domain": domain_from_url(url),
                    },
                )
            )
        time.sleep(1.0)
    return candidates


def build_domain_queries(query: str, domains: Sequence[str]) -> list[str]:
    normalized_domains = [domain.strip() for domain in domains if domain.strip()]
    if not normalized_domains:
        return [query]
    return [f"{query} site:{domain}" for domain in normalized_domains]


def collect_x_recent_search(
    query: str,
    limit: int,
    timeout: float,
    user_agent: str,
) -> list[SourceCandidate]:
    bearer_token = os.getenv(ENV_X_BEARER_TOKEN, "").strip()
    if not bearer_token:
        raise CollectionError(f"x_api requires {ENV_X_BEARER_TOKEN}")

    search_query = query
    if "-is:retweet" not in search_query:
        search_query = f"{search_query} -is:retweet"

    data = get_json(
        "https://api.x.com/2/tweets/search/recent",
        params={
            "query": search_query,
            "max_results": max(10, clamp_limit(limit, 100)),
            "tweet.fields": "created_at,author_id,public_metrics,lang",
            "expansions": "author_id",
            "user.fields": "username,name",
        },
        timeout=timeout,
        user_agent=user_agent,
        headers={
            "Authorization": f"Bearer {bearer_token}",
        },
    )
    tweets = ensure_list(data.get("data", []), "x recent search posts")
    includes = data.get("includes") if isinstance(data.get("includes"), Mapping) else {}
    users = {
        string_value(user.get("id")): user
        for user in includes.get("users", [])
        if isinstance(user, Mapping)
    }
    candidates: list[SourceCandidate] = []
    for tweet in tweets:
        if not isinstance(tweet, Mapping):
            continue
        tweet_id = string_value(tweet.get("id"))
        author_id = string_value(tweet.get("author_id"))
        user = users.get(author_id, {})
        username = string_value(user.get("username"))
        url = (
            f"https://x.com/{username}/status/{tweet_id}"
            if username and tweet_id
            else f"https://x.com/i/web/status/{tweet_id}"
        )
        metrics = tweet.get("public_metrics")
        metrics = metrics if isinstance(metrics, Mapping) else {}
        candidates.append(
            SourceCandidate(
                channel="x_api",
                type="post",
                title=truncate(clean_text(string_value(tweet.get("text"))), 120),
                url=url,
                date=string_value(tweet.get("created_at")),
                authors_or_org=username or author_id,
                summary=clean_text(string_value(tweet.get("text"))),
                query=search_query,
                method_category="social_api_search",
                engagement={
                    "retweets": metrics.get("retweet_count"),
                    "replies": metrics.get("reply_count"),
                    "likes": metrics.get("like_count"),
                    "quotes": metrics.get("quote_count"),
                    "lang": tweet.get("lang"),
                },
            )
        )
    return candidates


def collect_stackexchange(
    query: str,
    limit: int,
    sites: Sequence[str],
    timeout: float,
    user_agent: str,
) -> list[SourceCandidate]:
    candidates: list[SourceCandidate] = []
    for site in sites:
        params: dict[str, Any] = {
            "order": "desc",
            "sort": "relevance",
            "q": query,
            "site": site,
            "pagesize": clamp_limit(limit, 100),
        }
        api_key = os.getenv(ENV_STACKEXCHANGE_KEY, "").strip()
        if api_key:
            params["key"] = api_key
        data = get_json(
            "https://api.stackexchange.com/2.3/search/advanced",
            params=params,
            timeout=timeout,
            user_agent=user_agent,
        )
        items = ensure_list(data.get("items"), f"stackexchange items for {site}")
        for item in items:
            if not isinstance(item, Mapping):
                continue
            owner = item.get("owner") if isinstance(item.get("owner"), Mapping) else {}
            candidates.append(
                SourceCandidate(
                    channel="stackexchange",
                    type="qna",
                    title=html.unescape(string_value(item.get("title"))),
                    url=string_value(item.get("link")),
                    date=timestamp_to_iso(item.get("creation_date")),
                    authors_or_org=string_value(owner.get("display_name")),
                    summary=", ".join(string_value(tag) for tag in item.get("tags", [])),
                    query=query,
                    method_category="qna_search",
                    engagement={
                        "site": site,
                        "score": item.get("score"),
                        "answers": item.get("answer_count"),
                        "is_answered": item.get("is_answered"),
                    },
                )
            )
        time.sleep(0.2)
    return candidates


def collect_reddit(
    query: str,
    limit: int,
    timeout: float,
    user_agent: str,
) -> list[SourceCandidate]:
    reddit_user_agent = os.getenv(ENV_REDDIT_USER_AGENT, "").strip() or user_agent
    bearer_token = get_reddit_bearer_token(timeout, reddit_user_agent)
    data = get_json(
        "https://oauth.reddit.com/search",
        params={
            "q": query,
            "sort": "relevance",
            "limit": clamp_limit(limit, 100),
            "type": "link",
            "raw_json": 1,
        },
        timeout=timeout,
        user_agent=reddit_user_agent,
        headers={
            "Authorization": f"Bearer {bearer_token}",
        },
    )
    root = data.get("data") if isinstance(data.get("data"), Mapping) else {}
    children = ensure_list(root.get("children"), "reddit children")
    candidates: list[SourceCandidate] = []
    for child in children:
        if not isinstance(child, Mapping):
            continue
        post = child.get("data") if isinstance(child.get("data"), Mapping) else {}
        permalink = string_value(post.get("permalink"))
        reddit_url = f"https://www.reddit.com{permalink}" if permalink else ""
        candidates.append(
            SourceCandidate(
                channel="reddit",
                type="post",
                title=string_value(post.get("title")),
                url=reddit_url or string_value(post.get("url")),
                date=timestamp_to_iso(post.get("created_utc")),
                authors_or_org=string_value(post.get("author")),
                summary=truncate(clean_text(string_value(post.get("selftext"))), 500),
                query=query,
                method_category="discussion_search",
                engagement={
                    "subreddit": post.get("subreddit"),
                    "score": post.get("score"),
                    "comments": post.get("num_comments"),
                },
            )
        )
    return candidates


def get_reddit_bearer_token(timeout: float, user_agent: str) -> str:
    bearer_token = os.getenv(ENV_REDDIT_BEARER_TOKEN, "").strip()
    if bearer_token:
        return bearer_token

    client_id = os.getenv(ENV_REDDIT_CLIENT_ID, "").strip()
    client_secret = os.getenv(ENV_REDDIT_CLIENT_SECRET, "").strip()
    if not client_id or not client_secret:
        raise CollectionError(
            "reddit requires REDDIT_BEARER_TOKEN or "
            f"{ENV_REDDIT_CLIENT_ID}/{ENV_REDDIT_CLIENT_SECRET}"
        )

    credentials = f"{client_id}:{client_secret}".encode("utf-8")
    encoded_credentials = base64.b64encode(credentials).decode("ascii")
    data = post_form_json(
        "https://www.reddit.com/api/v1/access_token",
        form={"grant_type": "client_credentials"},
        headers={
            "Authorization": f"Basic {encoded_credentials}",
            "User-Agent": user_agent,
        },
        timeout=timeout,
    )
    token = string_value(data.get("access_token"))
    if not token:
        raise CollectionError("reddit OAuth response did not include access_token")
    return token


def collect_devto(
    tags: Sequence[str],
    per_tag: int,
    timeout: float,
    user_agent: str,
    sleep_seconds: float,
) -> list[SourceCandidate]:
    candidates: list[SourceCandidate] = []
    for tag in tags:
        data = get_json(
            "https://dev.to/api/articles",
            params={
                "tag": tag,
                "top": 365,
                "per_page": clamp_limit(per_tag, 1000),
            },
            timeout=timeout,
            user_agent=user_agent,
        )
        articles = ensure_list(data, f"devto articles for {tag}")
        for article in articles:
            if not isinstance(article, Mapping):
                continue
            user = article.get("user") if isinstance(article.get("user"), Mapping) else {}
            tag_list = article.get("tag_list")
            if isinstance(tag_list, list):
                tags_text = ", ".join(string_value(value) for value in tag_list)
            else:
                tags_text = string_value(article.get("tags"))
            candidates.append(
                SourceCandidate(
                    channel="devto",
                    type="blog",
                    title=string_value(article.get("title")),
                    url=string_value(article.get("canonical_url") or article.get("url")),
                    date=string_value(
                        article.get("published_timestamp") or article.get("published_at")
                    ),
                    authors_or_org=string_value(user.get("username") or user.get("name")),
                    summary=clean_text(
                        " ".join(
                            part
                            for part in (
                                string_value(article.get("description")),
                                tags_text,
                            )
                            if part
                        )
                    ),
                    query=f"tag:{tag}",
                    method_category="blog_feed",
                    engagement={
                        "tag": tag,
                        "comments": article.get("comments_count"),
                        "reactions": article.get("public_reactions_count"),
                    },
                )
            )
        time.sleep(max(sleep_seconds, 0))
    return candidates


def collect_rss_feeds(
    feeds: Sequence[str],
    timeout: float,
    user_agent: str,
    sleep_seconds: float,
) -> list[SourceCandidate]:
    candidates: list[SourceCandidate] = []
    for feed_url in feeds:
        text = get_text(feed_url, timeout=timeout, user_agent=user_agent)
        root = parse_xml(text, f"rss feed {feed_url}")
        candidates.extend(parse_feed(root, feed_url))
        time.sleep(max(sleep_seconds, 0))
    return candidates


def parse_feed(root: ET.Element, feed_url: str) -> list[SourceCandidate]:
    if root.tag.lower().endswith("rss"):
        return parse_rss(root, feed_url)
    if root.tag.endswith("feed"):
        return parse_atom_feed(root, feed_url)
    return []


def parse_rss(root: ET.Element, feed_url: str) -> list[SourceCandidate]:
    items: list[SourceCandidate] = []
    for item in root.findall(".//item"):
        title = clean_text(find_text(item, "title"))
        link = clean_text(find_text(item, "link"))
        date = clean_text(find_text(item, "pubDate"))
        summary = clean_text(
            find_text(item, "description") or find_text(item, "summary")
        )
        items.append(
            SourceCandidate(
                channel="rss",
                type="blog",
                title=title,
                url=link,
                date=date,
                authors_or_org=domain_from_url(feed_url),
                summary=truncate(summary, 500),
                query=feed_url,
                method_category="rss_scan",
            )
        )
    return items


def parse_atom_feed(root: ET.Element, feed_url: str) -> list[SourceCandidate]:
    atom = "{http://www.w3.org/2005/Atom}"
    items: list[SourceCandidate] = []
    for entry in root.findall(f"{atom}entry"):
        links = entry.findall(f"{atom}link")
        link = ""
        for candidate in links:
            rel = candidate.attrib.get("rel", "alternate")
            href = candidate.attrib.get("href", "")
            if href and rel == "alternate":
                link = href
                break
        if not link and links:
            link = links[0].attrib.get("href", "")
        items.append(
            SourceCandidate(
                channel="rss",
                type="blog",
                title=clean_text(find_text(entry, f"{atom}title")),
                url=link,
                date=clean_text(
                    find_text(entry, f"{atom}published")
                    or find_text(entry, f"{atom}updated")
                ),
                authors_or_org=domain_from_url(feed_url),
                summary=truncate(
                    clean_text(
                        find_text(entry, f"{atom}summary")
                        or find_text(entry, f"{atom}content")
                    ),
                    500,
                ),
                query=feed_url,
                method_category="rss_scan",
            )
        )
    return items


def score_and_keep(candidate: SourceCandidate, min_score: int) -> bool:
    score, matched = relevance_score(candidate.title, candidate.summary, candidate.query)
    candidate.relevance_score = score
    candidate.matched_terms = matched
    candidate.relevance = relevance_label(score)
    candidate.rank_score = rank_score(candidate)
    return bool(candidate.url and candidate.title and score >= min_score)


def relevance_score(title: str, summary: str, query: str) -> tuple[int, list[str]]:
    title_text = title.lower()
    summary_text = summary.lower()
    query_text = query.lower()
    matched: set[str] = set()
    score = 0

    for term in RELEVANCE_TERMS:
        lowered = term.lower()
        if lowered in title_text:
            score += 3
            matched.add(term)
        elif lowered in summary_text:
            score += 1
            matched.add(term)

    normalized_query = " ".join(query_text.split())
    if normalized_query and normalized_query.startswith("tag:"):
        normalized_query = ""
    if normalized_query and normalized_query in f"{title_text} {summary_text}":
        score += 2
        matched.add(query)

    return score, sorted(matched)


def relevance_label(score: int) -> str:
    if score >= 6:
        return "high"
    if score >= 2:
        return "medium"
    return "low"


def rank_score(candidate: SourceCandidate) -> float:
    engagement = candidate.engagement
    points = number_value(engagement.get("points") or engagement.get("score"))
    comments = number_value(engagement.get("comments"))
    stars = number_value(engagement.get("stars"))
    reactions = number_value(engagement.get("reactions"))
    answers = number_value(engagement.get("answers"))
    likes = number_value(engagement.get("likes"))
    replies = number_value(engagement.get("replies"))
    retweets = number_value(engagement.get("retweets"))
    return (
        candidate.relevance_score * 10
        + min(points / 5, 15)
        + min(comments / 3, 15)
        + min(stars / 100, 20)
        + min(reactions / 5, 10)
        + min(answers, 5)
        + min(likes / 20, 10)
        + min(replies / 3, 10)
        + min(retweets / 5, 10)
    )


def deduplicate_candidates(candidates: Iterable[SourceCandidate]) -> list[SourceCandidate]:
    merged: dict[str, SourceCandidate] = {}
    for candidate in candidates:
        key = normalize_url(candidate.url) or stable_hash(candidate.title.lower())
        candidate.channels = [candidate.channel]
        candidate.queries = [candidate.query] if candidate.query else []
        existing = merged.get(key)
        if not existing:
            merged[key] = candidate
            continue

        existing.channels = sorted(set(existing.channels + [candidate.channel]))
        if candidate.query:
            existing.queries = sorted(set(existing.queries + [candidate.query]))
        if candidate.rank_score > existing.rank_score:
            candidate.channels = existing.channels
            candidate.queries = existing.queries
            merged[key] = candidate

    deduped = list(merged.values())
    for item in deduped:
        item.channel = item.channels[0] if item.channels else item.channel
        item.source_id = make_source_id(item)
    return deduped


def make_source_id(candidate: SourceCandidate) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", candidate.channel.lower()).strip("-")
    digest = stable_hash(normalize_url(candidate.url) or candidate.title)
    return f"candidate-{slug}-{digest[:10]}"


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def mark_existing_inventory(
    candidates: Sequence[SourceCandidate],
    inventory_urls: set[str],
) -> None:
    for candidate in candidates:
        normalized = normalize_url(candidate.url)
        if normalized in inventory_urls:
            candidate.already_in_inventory = True
            candidate.novelty_status = "duplicate"
            candidate.decision = "already in source_inventory; update only if metadata changed"


def load_inventory_urls(path: Path) -> set[str]:
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8")
    urls = re.findall(r"https?://[^\s)\]|]+", text)
    return {normalize_url(url) for url in urls if normalize_url(url)}


def normalize_url(url: str) -> str:
    raw_url = url.strip()
    if not raw_url:
        return ""

    parsed = urllib.parse.urlparse(raw_url)
    if not parsed.scheme or not parsed.netloc:
        return raw_url.rstrip("/")

    query_pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    filtered_query = [
        (key, value)
        for key, value in query_pairs
        if key.lower() not in TRACKING_PARAMS
    ]
    query = urllib.parse.urlencode(filtered_query, doseq=True)
    path = parsed.path.rstrip("/") or "/"
    normalized = parsed._replace(
        scheme=parsed.scheme.lower(),
        netloc=parsed.netloc.lower(),
        path=path,
        query=query,
        fragment="",
    )
    return urllib.parse.urlunparse(normalized)


def get_json(
    url: str,
    params: Optional[Mapping[str, Any]] = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    user_agent: str = DEFAULT_USER_AGENT,
    headers: Optional[Mapping[str, str]] = None,
) -> Any:
    text = get_text(
        url,
        params=params,
        timeout=timeout,
        user_agent=user_agent,
        headers=headers,
    )
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise CollectionError(f"non-JSON response from {url}: {text[:120]}") from exc


def post_form_json(
    url: str,
    form: Mapping[str, Any],
    headers: Mapping[str, str],
    timeout: float,
) -> Any:
    body = urllib.parse.urlencode(form).encode("utf-8")
    request_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    request_headers.update(headers)
    request = urllib.request.Request(
        url,
        data=body,
        headers=request_headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_body = response.read()
            charset = response.headers.get_content_charset() or "utf-8"
            text = response_body.decode(charset, errors="replace")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:200]
        raise CollectionError(f"HTTP {exc.code} for {url}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise CollectionError(f"request failed for {url}: {exc}") from exc

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise CollectionError(f"non-JSON response from {url}: {text[:120]}") from exc


def get_text(
    url: str,
    params: Optional[Mapping[str, Any]] = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    user_agent: str = DEFAULT_USER_AGENT,
    headers: Optional[Mapping[str, str]] = None,
) -> str:
    full_url = build_url(url, params)
    request_headers = {"User-Agent": user_agent}
    request_headers.update(headers or {})
    request = urllib.request.Request(full_url, headers=request_headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
            charset = response.headers.get_content_charset() or "utf-8"
            return body.decode(charset, errors="replace")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:200]
        raise CollectionError(f"HTTP {exc.code} for {full_url}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise CollectionError(f"request failed for {full_url}: {exc}") from exc


def build_url(url: str, params: Optional[Mapping[str, Any]]) -> str:
    if not params:
        return url
    query = urllib.parse.urlencode(params, doseq=True)
    separator = "&" if urllib.parse.urlparse(url).query else "?"
    return f"{url}{separator}{query}"


def parse_xml(text: str, label: str) -> ET.Element:
    try:
        return ET.fromstring(text)
    except ET.ParseError as exc:
        raise CollectionError(f"invalid XML from {label}") from exc


def ensure_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise CollectionError(f"expected list for {label}")
    return value


def find_text(element: ET.Element, path: str) -> str:
    found = element.find(path)
    return found.text if found is not None and found.text else ""


def clean_text(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", html.unescape(value or ""))
    return " ".join(without_tags.split())


def truncate(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value
    return value[: max_length - 1].rstrip() + "…"


def string_value(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def number_value(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def timestamp_to_iso(value: Any) -> str:
    try:
        timestamp = float(value)
    except (TypeError, ValueError):
        return ""
    return dt.datetime.fromtimestamp(timestamp, tz=dt.timezone.utc).isoformat()


def domain_from_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    return parsed.netloc


def clamp_limit(value: int, maximum: int) -> int:
    return max(1, min(value, maximum))


def write_jsonl(path: Path, candidates: Sequence[SourceCandidate]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for candidate in candidates:
            handle.write(json.dumps(asdict(candidate), ensure_ascii=False) + "\n")


def write_markdown(
    path: Path,
    candidates: Sequence[SourceCandidate],
    channels: Sequence[str],
    queries: Sequence[str],
) -> None:
    lines = [
        "# Source Candidates",
        "",
        f"Generated at: {dt.datetime.now(dt.timezone.utc).isoformat()}",
        f"Channels: {', '.join(channels)}",
        f"Queries: {len(queries)}",
        f"Candidates: {len(candidates)}",
        "",
        "| source_id | channels | relevance | title | date | url | decision |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for candidate in candidates:
        channels_text = ", ".join(candidate.channels or [candidate.channel])
        title = markdown_cell(candidate.title)
        url = candidate.url
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_cell(candidate.source_id),
                    markdown_cell(channels_text),
                    markdown_cell(candidate.relevance),
                    title,
                    markdown_cell(display_date(candidate.date)),
                    f"[link]({url})",
                    markdown_cell(candidate.decision),
                ]
            )
            + " |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def markdown_cell(value: str) -> str:
    return (value or "").replace("|", "\\|").replace("\n", " ")


def display_date(value: str) -> str:
    if not value:
        return ""
    if re.match(r"\d{4}-\d{2}-\d{2}", value):
        return value[:10]
    return value[:24]


def print_channel_counts(candidates: Sequence[SourceCandidate]) -> None:
    counts: dict[str, int] = {}
    for candidate in candidates:
        for channel in candidate.channels or [candidate.channel]:
            counts[channel] = counts.get(channel, 0) + 1
    if not counts:
        return
    print("channels:")
    for channel, count in sorted(counts.items()):
        print(f"- {channel}: {count}")


if __name__ == "__main__":
    raise SystemExit(main())
