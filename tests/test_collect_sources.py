import unittest
from unittest.mock import patch

from scripts.collect_sources import (
    CollectionError,
    SourceCandidate,
    collect_brave_web_search,
    collect_x_recent_search,
    deduplicate_candidates,
    get_reddit_bearer_token,
    normalize_url,
    parse_feed,
    parse_xml,
    score_and_keep,
)


class CollectSourcesTests(unittest.TestCase):
    def test_normalize_url_removes_tracking_params_and_fragment(self):
        normalized = normalize_url(
            "https://Example.com/path/?utm_source=x&b=2&ref=hn#comments"
        )

        self.assertEqual(normalized, "https://example.com/path?b=2")

    def test_deduplicate_merges_channels_and_keeps_stronger_candidate(self):
        low = SourceCandidate(
            channel="rss",
            type="blog",
            title="Prompt optimization notes",
            url="https://example.com/post?utm_campaign=x",
            relevance_score=1,
            rank_score=10,
            query="rss",
        )
        high = SourceCandidate(
            channel="hackernews",
            type="post",
            title="Prompt optimization discussion",
            url="https://example.com/post",
            relevance_score=3,
            rank_score=30,
            query="prompt optimization",
        )

        result = deduplicate_candidates([low, high])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "Prompt optimization discussion")
        self.assertEqual(result[0].channels, ["hackernews", "rss"])
        self.assertEqual(result[0].queries, ["prompt optimization", "rss"])
        self.assertTrue(result[0].source_id.startswith("candidate-"))

    def test_collect_brave_web_search_uses_domain_queries(self):
        response = {
            "web": {
                "results": [
                    {
                        "title": "提示词优化实践",
                        "url": "https://zhuanlan.zhihu.com/p/123",
                        "description": "自动提示词优化和 eval-driven rollback。",
                        "profile": {"name": "知乎专栏"},
                        "age": "2026-06-01",
                    }
                ]
            }
        }

        with patch.dict("os.environ", {"BRAVE_SEARCH_API_KEY": "key"}, clear=True):
            with patch("scripts.collect_sources.get_json", return_value=response) as get_json:
                with patch("scripts.collect_sources.time.sleep"):
                    result = collect_brave_web_search(
                        "提示词优化",
                        5,
                        1,
                        "test",
                        domains=("zhihu.com",),
                        channel="zhihu",
                    )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].channel, "zhihu")
        self.assertEqual(result[0].url, "https://zhuanlan.zhihu.com/p/123")
        self.assertEqual(
            get_json.call_args.kwargs["params"]["q"],
            "提示词优化 site:zhihu.com",
        )

    def test_collect_x_recent_search_parses_posts_and_users(self):
        response = {
            "data": [
                {
                    "id": "123",
                    "author_id": "u1",
                    "text": "Prompt optimization with GEPA and eval traces",
                    "created_at": "2026-06-08T00:00:00Z",
                    "public_metrics": {
                        "like_count": 42,
                        "reply_count": 3,
                        "retweet_count": 2,
                        "quote_count": 1,
                    },
                    "lang": "en",
                }
            ],
            "includes": {
                "users": [
                    {"id": "u1", "username": "researcher", "name": "Researcher"}
                ]
            },
        }

        with patch.dict("os.environ", {"X_BEARER_TOKEN": "token"}, clear=True):
            with patch("scripts.collect_sources.get_json", return_value=response):
                result = collect_x_recent_search("prompt optimization", 5, 1, "test")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].channel, "x_api")
        self.assertEqual(result[0].authors_or_org, "researcher")
        self.assertEqual(result[0].url, "https://x.com/researcher/status/123")
        self.assertEqual(result[0].engagement["likes"], 42)

    def test_reddit_requires_oauth_configuration(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(CollectionError):
                get_reddit_bearer_token(1, "test")

    def test_parse_rss_and_score_candidate(self):
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
          <channel>
            <item>
              <title>Prompt optimizer release notes</title>
              <link>https://example.com/prompt-optimizer</link>
              <pubDate>Mon, 08 Jun 2026 00:00:00 GMT</pubDate>
              <description>Eval-driven prompt rollback details.</description>
            </item>
          </channel>
        </rss>
        """
        root = parse_xml(xml, "test rss")

        items = parse_feed(root, "https://example.com/feed.xml")

        self.assertEqual(len(items), 1)
        self.assertTrue(score_and_keep(items[0], min_score=1))
        self.assertEqual(items[0].relevance, "medium")


if __name__ == "__main__":
    unittest.main()
