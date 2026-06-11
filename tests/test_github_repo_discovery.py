import unittest

from scripts.github_repo_discovery import (
    SearchSpec,
    build_source_id,
    classify_method_category,
    format_csv,
    format_markdown_report,
    merge_duplicate_repositories,
    normalize_repository,
    relevance_bucket,
    score_repository,
)


class GitHubRepoDiscoveryTests(unittest.TestCase):
    def test_build_source_id_sanitizes_full_name(self):
        self.assertEqual(
            build_source_id("stanfordnlp/dspy"),
            "repo-stanfordnlp-dspy",
        )
        self.assertEqual(
            build_source_id("Owner With Spaces/Repo.Name"),
            "repo-owner-with-spaces-repo-name",
        )

    def test_scores_core_prompt_optimization_repository_as_high(self):
        repo = {
            "full_name": "example/prompt-optimizer",
            "description": "Automatic prompt optimization with LLM as judge evals",
            "language": "Python",
            "topics": ["prompt-optimization", "llm-evaluation"],
            "stargazers_count": 100,
            "forks_count": 10,
        }

        score, hits = score_repository(repo)

        self.assertGreaterEqual(score, 24)
        self.assertEqual(relevance_bucket(score), "high")
        self.assertIn("automatic prompt optimization", hits)
        self.assertIn("prompt+eval", hits)

    def test_high_star_repository_without_metadata_signal_stays_low(self):
        repo = {
            "full_name": "example/popular-unrelated",
            "description": "A popular unrelated developer resource list",
            "language": "Python",
            "topics": [],
            "stargazers_count": 500000,
            "forks_count": 50000,
        }

        score, hits = score_repository(repo)

        self.assertLess(score, 8)
        self.assertEqual(hits, [])

    def test_classifies_known_method_categories(self):
        self.assertEqual(
            classify_method_category("dspy mipro prompt optimizer"),
            "prompt-as-program",
        )
        self.assertEqual(
            classify_method_category("promptbreeder self evolving prompt"),
            "evolutionary-self-evolving",
        )
        self.assertEqual(
            classify_method_category("promptfoo prompt regression eval"),
            "eval-benchmark-governance",
        )

    def test_normalize_repository_adds_research_fields(self):
        item = {
            "full_name": "openai/evals",
            "name": "evals",
            "html_url": "https://github.com/openai/evals",
            "description": "Evals for LLM prompts",
            "language": "Python",
            "topics": ["evals", "llm"],
            "stargazers_count": 1000,
            "forks_count": 100,
            "owner": {"login": "openai"},
            "license": {"spdx_id": "MIT"},
        }

        repo = normalize_repository(
            item,
            SearchSpec("prompt-eval", "prompt eval llm in:name,description,readme"),
            "2026-06-08T00:00:00+00:00",
        )

        self.assertEqual(repo["source_id"], "repo-openai-evals")
        self.assertEqual(repo["status"], "candidate")
        self.assertEqual(repo["source_channel"], "github")
        self.assertEqual(repo["matched_queries"], ["prompt-eval"])
        self.assertEqual(repo["license_spdx"], "MIT")

    def test_merge_duplicate_repositories_unions_query_metadata(self):
        base = {
            "full_name": "example/repo",
            "matched_queries": ["prompt-optimization"],
            "matched_query_strings": ["prompt optimization"],
            "keyword_hits": ["prompt optimization"],
            "relevance_score": 20,
            "relevance": "medium",
            "method_category": "automatic-prompt-optimization",
            "optimization_object": "prompt_text",
            "feedback_signal": "unknown",
            "selection_method": "optimizer",
        }
        duplicate = {
            **base,
            "matched_queries": ["textgrad"],
            "matched_query_strings": ["TextGrad"],
            "keyword_hits": ["textgrad"],
            "relevance_score": 30,
            "relevance": "high",
            "method_category": "textual-gradient-critique",
            "feedback_signal": "llm_feedback",
        }

        merged = merge_duplicate_repositories([base, duplicate])

        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["matched_queries"], ["prompt-optimization", "textgrad"])
        self.assertEqual(merged[0]["relevance"], "high")
        self.assertEqual(merged[0]["method_category"], "textual-gradient-critique")

    def test_markdown_report_marks_candidates_not_evidence(self):
        repositories = [
            {
                "relevance_score": 30,
                "full_name": "example/repo",
                "url": "https://github.com/example/repo",
                "stargazers_count": 42,
                "updated_at": "2026-06-08T00:00:00Z",
                "method_category": "automatic-prompt-optimization",
                "keyword_hits": ["prompt optimization"],
            }
        ]
        stats = {
            "generated_at": "2026-06-08T00:00:00+00:00",
            "raw_items": 1,
            "unique_repositories": 1,
            "kept_repositories": 1,
            "queries": [{"label": "q", "query": "prompt optimization", "raw_items": 1}],
        }
        config = type("Config", (), {"min_score": 8.0})()

        markdown = format_markdown_report(
            repositories,
            errors=[],
            stats=stats,
            config=config,
            token_present=False,
        )

        self.assertIn("search candidates, not research evidence", markdown)
        self.assertIn("[example/repo](https://github.com/example/repo)", markdown)

    def test_csv_marks_repositories_kept_by_min_score(self):
        csv_text = format_csv(
            [
                {
                    "source_id": "repo-high",
                    "relevance_score": 12,
                    "keyword_hits": ["prompt optimization"],
                    "matched_queries": ["prompt-optimization"],
                },
                {
                    "source_id": "repo-low",
                    "relevance_score": 2,
                    "keyword_hits": [],
                    "matched_queries": ["prompt-optimization"],
                },
            ],
            min_score=8,
        )

        self.assertIn("kept_by_min_score", csv_text.splitlines()[0])
        self.assertIn("repo-high,True", csv_text)
        self.assertIn("repo-low,False", csv_text)


if __name__ == "__main__":
    unittest.main()
