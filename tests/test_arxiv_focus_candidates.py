import tempfile
import unittest
from pathlib import Path

from scripts.arxiv_focus_candidates import (
    focus_score,
    select_top_papers,
    write_outputs,
)
from scripts.arxiv_prompt_paper_search import ArxivPaper


def make_paper(
    title: str,
    abstract: str,
    method_categories: list[str],
    score: int = 30,
    relevance: str = "high",
    inventory_status: str = "new",
    arxiv_id: str = "2501.00001",
) -> ArxivPaper:
    return ArxivPaper(
        arxiv_id=arxiv_id,
        latest_version_id=f"{arxiv_id}v1",
        title=title,
        authors=["Test Author"],
        published="2025-01-01T00:00:00Z",
        updated="2025-01-01T00:00:00Z",
        abstract=abstract,
        primary_category="cs.CL",
        categories=["cs.CL"],
        abs_url=f"https://arxiv.org/abs/{arxiv_id}",
        pdf_url=f"https://arxiv.org/pdf/{arxiv_id}",
        matched_query_labels=["apo-core"],
        matched_keyword_phrases=["prompt optimization"],
        method_categories=method_categories,
        score=score,
        relevance=relevance,
        inventory_status=inventory_status,
        source_id=f"paper-arxiv-{arxiv_id.replace('.', '-')}",
    )


class ArxivFocusCandidatesTests(unittest.TestCase):
    def test_focus_score_prioritizes_core_apo_over_visual_prompt_noise(self):
        core = make_paper(
            title="Automatic Prompt Optimization with Textual Gradients",
            abstract="We compare baselines on held-out benchmark datasets and report failures.",
            method_categories=["automatic prompt optimization", "textual gradient"],
            arxiv_id="2501.00001",
        )
        visual = make_paper(
            title="Prompt Optimization for Text-to-Image Diffusion Models",
            abstract="We optimize prompts for image generation.",
            method_categories=["automatic prompt optimization"],
            arxiv_id="2501.00002",
        )

        core_score, _ = focus_score(core)
        visual_score, visual_reasons = focus_score(visual)

        self.assertGreater(core_score, visual_score)
        self.assertTrue(any(reason.startswith("penalty:") for reason in visual_reasons))

    def test_select_top_papers_excludes_low_relevance_by_default(self):
        high = make_paper(
            title="Automatic Prompt Optimization",
            abstract="benchmark baseline",
            method_categories=["automatic prompt optimization"],
            relevance="high",
            arxiv_id="2501.00001",
        )
        low = make_paper(
            title="Prompt Optimization",
            abstract="benchmark baseline",
            method_categories=["automatic prompt optimization"],
            relevance="low",
            arxiv_id="2501.00002",
        )

        selected = select_top_papers([low, high], top_n=10)

        self.assertEqual([paper.arxiv_id for paper, _score, _reasons in selected], ["2501.00001"])

    def test_write_outputs_creates_shortlist_files(self):
        paper = make_paper(
            title="Automatic Prompt Optimization",
            abstract="benchmark baseline",
            method_categories=["automatic prompt optimization"],
        )
        ranked = [(paper, 100, ["automatic prompt optimization"])]

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = write_outputs(
                ranked,
                input_path=Path("input.json"),
                output_dir=Path(tmpdir),
                prefix="focus",
            )

            for path in paths.values():
                self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
