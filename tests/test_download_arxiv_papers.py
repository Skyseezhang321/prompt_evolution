import tempfile
import unittest
from pathlib import Path

from scripts.download_arxiv_papers import (
    DownloadRecord,
    PaperRecord,
    normalize_arxiv_id,
    pdf_url_for,
    select_papers,
    write_manifest,
)


class DownloadArxivPapersTests(unittest.TestCase):
    def test_normalize_arxiv_id_removes_url_and_version(self):
        self.assertEqual(
            normalize_arxiv_id("https://arxiv.org/abs/2305.03495v2"),
            "2305.03495",
        )
        self.assertEqual(
            normalize_arxiv_id("https://arxiv.org/pdf/2305.03495v2.pdf"),
            "2305.03495",
        )

    def test_pdf_url_for_uses_arxiv_pdf_endpoint(self):
        self.assertEqual(
            pdf_url_for("2305.03495"),
            "https://arxiv.org/pdf/2305.03495",
        )

    def test_select_papers_by_explicit_ids_preserves_requested_order(self):
        papers = [
            PaperRecord(
                arxiv_id="2305.03495",
                title="ProTeGi",
                abs_url="https://arxiv.org/abs/2305.03495",
                pdf_url="https://arxiv.org/pdf/2305.03495",
            ),
            PaperRecord(
                arxiv_id="2507.19457",
                title="GEPA",
                abs_url="https://arxiv.org/abs/2507.19457",
                pdf_url="https://arxiv.org/pdf/2507.19457",
            ),
        ]

        selected = select_papers(
            papers,
            arxiv_ids=["2507.19457", "2305.03495"],
            top_n=None,
        )

        self.assertEqual([paper.arxiv_id for paper in selected], ["2507.19457", "2305.03495"])

    def test_select_papers_by_top_n(self):
        papers = [
            PaperRecord("a", "A", "https://arxiv.org/abs/a", "https://arxiv.org/pdf/a"),
            PaperRecord("b", "B", "https://arxiv.org/abs/b", "https://arxiv.org/pdf/b"),
        ]

        selected = select_papers(papers, arxiv_ids=[], top_n=1)

        self.assertEqual([paper.arxiv_id for paper in selected], ["a"])

    def test_write_manifest_creates_json_csv_and_markdown(self):
        record = DownloadRecord(
            arxiv_id="2305.03495",
            title="ProTeGi",
            abs_url="https://arxiv.org/abs/2305.03495",
            pdf_url="https://arxiv.org/pdf/2305.03495",
            status="ok",
            pdf_path="local_sources/raw/arxiv_papers/2305.03495/paper.pdf",
            pdf_sha256="ABCDEF",
            pdf_bytes=10,
            text_path="local_sources/raw/arxiv_papers/2305.03495/paper.txt",
            text_sha256="123456",
            text_chars=20,
            page_count=3,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            paths = write_manifest([record], Path(tmpdir), "manifest")

            for path in paths.values():
                self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
