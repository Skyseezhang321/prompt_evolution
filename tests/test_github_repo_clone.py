import tempfile
import unittest
from pathlib import Path

from scripts.github_repo_clone import (
    CloneRecord,
    clone_url_for,
    render_manifest_markdown,
    source_id_for,
    targets_for,
    write_manifest,
)


class GitHubRepoCloneTests(unittest.TestCase):
    def test_source_id_for_normalizes_repo_name(self):
        self.assertEqual(
            source_id_for("linshenkx/prompt-optimizer"),
            "repo-linshenkx-prompt-optimizer",
        )

    def test_clone_url_for_uses_https_github_url(self):
        self.assertEqual(
            clone_url_for("karpathy/autoresearch"),
            "https://github.com/karpathy/autoresearch.git",
        )

    def test_targets_for_core4_preserves_expected_order(self):
        targets = targets_for("core4", [])

        self.assertEqual(
            [target.full_name for target in targets],
            [
                "linshenkx/prompt-optimizer",
                "karpathy/autoresearch",
                "humanlayer/12-factor-agents",
                "affaan-m/ECC",
            ],
        )

    def test_targets_for_adds_extra_repo(self):
        targets = targets_for("core4", ["https://github.com/example/repo"])

        self.assertEqual(targets[-1].source_id, "repo-example-repo")
        self.assertEqual(targets[-1].priority, "extra")

    def test_write_manifest_creates_json_csv_markdown(self):
        record = CloneRecord(
            source_id="repo-example-repo",
            full_name="example/repo",
            priority="core",
            rationale="test",
            status="cloned",
            clone_url="https://github.com/example/repo.git",
            local_path="local_sources/raw/github_repo_clones/repo-example-repo",
            commit_sha="abcdef123456",
            current_branch="main",
            origin_head="origin/main",
            commit_author_date="2026-06-08T00:00:00+00:00",
            commit_subject="initial",
            readme_paths=["README.md"],
            readme_sha256=["A" * 64],
            license_paths=["LICENSE"],
            license_sha256=["B" * 64],
            cloned_at="2026-06-08T00:00:00+00:00",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = write_manifest([record], Path(tmpdir), prefix="test_manifest")

            self.assertTrue(paths["json"].exists())
            self.assertTrue(paths["csv"].exists())
            self.assertTrue(paths["markdown"].exists())

    def test_manifest_markdown_links_repository(self):
        record = CloneRecord(
            source_id="repo-example-repo",
            full_name="example/repo",
            priority="core",
            rationale="test",
            status="cloned",
            clone_url="https://github.com/example/repo.git",
            local_path="local_sources/raw/github_repo_clones/repo-example-repo",
            commit_sha="abcdef123456",
            current_branch="main",
            origin_head="origin/main",
            commit_author_date="2026-06-08T00:00:00+00:00",
            commit_subject="initial",
            readme_paths=[],
            readme_sha256=[],
            license_paths=[],
            license_sha256=[],
            cloned_at="2026-06-08T00:00:00+00:00",
        )

        markdown = render_manifest_markdown([record])

        self.assertIn("[example/repo](https://github.com/example/repo)", markdown)


if __name__ == "__main__":
    unittest.main()
