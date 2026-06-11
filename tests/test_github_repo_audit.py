import tempfile
import unittest
from pathlib import Path

from scripts.github_repo_audit import (
    FileSignal,
    RepoAudit,
    escape_md,
    excerpt_matching_lines,
    render_audit_note,
    sha256_file,
    tags_for_content,
    tags_for_path,
)


class GitHubRepoAuditTests(unittest.TestCase):
    def test_tags_for_path_detects_prompt_eval_agent_memory(self):
        self.assertIn("prompt", tags_for_path("src/prompts/system_prompt.md"))
        self.assertIn("eval", tags_for_path("evals/grader.yaml"))
        self.assertIn("agent", tags_for_path("agents/reviewer.md"))
        self.assertIn("memory_context", tags_for_path("docs/context-window.md"))

    def test_tags_for_content_detects_core_evidence_terms(self):
        text = (
            "Prompt optimization uses compare evaluation with a judge. "
            "The agent repeats candidates and keeps the best checkpoint."
        )

        tags = tags_for_content(text)

        self.assertIn("prompt_optimization", tags)
        self.assertIn("evaluation", tags)
        self.assertIn("iteration_loop", tags)
        self.assertIn("agent_workflow", tags)

    def test_excerpt_matching_lines_adds_line_numbers(self):
        excerpts = excerpt_matching_lines("hello\ncompare evaluation with judge\n")

        self.assertEqual(excerpts, ["L2: compare evaluation with judge"])

    def test_sha256_file_hashes_bytes_uppercase(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "file.txt"
            path.write_text("hello", encoding="utf-8")

            self.assertEqual(
                sha256_file(path),
                "2CF24DBA5FB0A30E26E83B2AC5B9E29E1B161E5C1FA7425E73043362938B9824",
            )

    def test_render_audit_note_keeps_human_review_boundary(self):
        audit = RepoAudit(
            source_id="repo-example-repo",
            full_name="example/repo",
            local_path="local_sources/raw/github_repo_clones/repo-example-repo",
            commit_sha="abcdef123456",
            current_branch="main",
            generated_at="2026-06-08T00:00:00+00:00",
            total_files_seen=1,
            text_files_scanned=1,
            readme_files=["README.md"],
            license_files=["LICENSE"],
            package_files=["package.json"],
            path_tag_counts={"prompt": 1},
            content_tag_counts={"evaluation": 1},
            file_signals=[
                FileSignal(
                    path="README.md",
                    size_bytes=10,
                    sha256="A" * 64,
                    path_tags=[],
                    content_tags=["evaluation"],
                    excerpts=["L1: compare evaluation"],
                )
            ],
            audit_json_path="local_sources/raw/github_repo_audits/repo-example-repo/audit.json",
            audit_json_sha256="B" * 64,
        )

        markdown = render_audit_note(audit)

        self.assertIn("源码审计草稿，不是最终 insight", markdown)
        self.assertIn("Claims To Verify Manually", markdown)
        self.assertIn("README.md", markdown)

    def test_escape_md_escapes_table_pipes(self):
        self.assertEqual(escape_md("a | b"), "a \\| b")


if __name__ == "__main__":
    unittest.main()
