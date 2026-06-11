import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from scripts.arxiv_prompt_paper_search import (
    QuerySpec,
    build_query_url,
    filter_by_min_relevance,
    load_existing_arxiv_ids,
    merge_papers_by_id,
    normalize_arxiv_id,
    parse_atom_feed,
    render_inventory_row,
)


SAMPLE_FEED = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <opensearch:totalResults>1</opensearch:totalResults>
  <entry>
    <id>http://arxiv.org/abs/2305.03495v2</id>
    <updated>2023-05-08T00:00:00Z</updated>
    <published>2023-05-05T00:00:00Z</published>
    <title>Automatic Prompt Optimization with Gradient Descent and Beam Search</title>
    <summary>
      We propose ProTeGi, a textual gradient method for prompt optimization.
    </summary>
    <author><name>Jane Researcher</name></author>
    <author><name>John Engineer</name></author>
    <arxiv:doi>10.0000/example</arxiv:doi>
    <arxiv:comment>Example comment</arxiv:comment>
    <arxiv:journal_ref>Example Journal</arxiv:journal_ref>
    <arxiv:primary_category term="cs.CL" scheme="http://arxiv.org/schemas/atom" />
    <category term="cs.CL" scheme="http://arxiv.org/schemas/atom" />
    <category term="cs.AI" scheme="http://arxiv.org/schemas/atom" />
    <link href="http://arxiv.org/abs/2305.03495v2" rel="alternate" type="text/html" />
    <link title="pdf" href="http://arxiv.org/pdf/2305.03495v2" rel="related" type="application/pdf" />
  </entry>
</feed>
"""


class ArxivPromptPaperSearchTests(unittest.TestCase):
    def test_normalize_arxiv_id_removes_version_from_url(self):
        self.assertEqual(
            normalize_arxiv_id("http://arxiv.org/abs/2305.03495v2"),
            "2305.03495",
        )
        self.assertEqual(
            normalize_arxiv_id("http://arxiv.org/pdf/2305.03495v2.pdf"),
            "2305.03495",
        )
        self.assertEqual(
            normalize_arxiv_id("http://arxiv.org/abs/2305.03495v2", keep_version=True),
            "2305.03495v2",
        )

    def test_build_query_url_preserves_arxiv_query_parameters(self):
        url = build_query_url(
            'all:"prompt optimization"',
            start=10,
            max_results=25,
            sort_by="relevance",
            sort_order="descending",
        )
        query = parse_qs(urlparse(url).query)

        self.assertEqual(query["search_query"], ['all:"prompt optimization"'])
        self.assertEqual(query["start"], ["10"])
        self.assertEqual(query["max_results"], ["25"])
        self.assertEqual(query["sortBy"], ["relevance"])
        self.assertEqual(query["sortOrder"], ["descending"])

    def test_parse_atom_feed_extracts_metadata_and_scores_relevance(self):
        spec = QuerySpec(
            label="apo-core",
            method_category="automatic prompt optimization",
            query='all:"prompt optimization"',
        )
        total_results, papers = parse_atom_feed(SAMPLE_FEED, spec)

        self.assertEqual(total_results, 1)
        self.assertEqual(len(papers), 1)
        paper = papers[0]
        self.assertEqual(paper.arxiv_id, "2305.03495")
        self.assertEqual(paper.latest_version_id, "2305.03495v2")
        self.assertEqual(
            paper.title,
            "Automatic Prompt Optimization with Gradient Descent and Beam Search",
        )
        self.assertEqual(paper.authors, ["Jane Researcher", "John Engineer"])
        self.assertEqual(paper.primary_category, "cs.CL")
        self.assertEqual(paper.categories, ["cs.CL", "cs.AI"])
        self.assertEqual(paper.doi, "10.0000/example")
        self.assertEqual(paper.relevance, "high")
        self.assertIn("prompt optimization", paper.matched_keyword_phrases)
        self.assertIn("textual gradient / beam search", paper.method_categories)

    def test_merge_papers_by_id_combines_query_labels(self):
        spec_one = QuerySpec("apo-core", "automatic prompt optimization", "q1")
        spec_two = QuerySpec("textual-gradient", "textual gradient", "q2")
        first = parse_atom_feed(SAMPLE_FEED, spec_one)[1][0]
        second = parse_atom_feed(SAMPLE_FEED, spec_two)[1][0]

        merged = merge_papers_by_id([first, second])

        self.assertEqual(len(merged), 1)
        self.assertEqual(
            merged[0].matched_query_labels,
            ["apo-core", "textual-gradient"],
        )
        self.assertIn("automatic prompt optimization", merged[0].method_categories)
        self.assertIn("textual gradient", merged[0].method_categories)

    def test_filter_by_min_relevance_keeps_threshold_and_above(self):
        spec = QuerySpec("apo-core", "automatic prompt optimization", "q1")
        paper = parse_atom_feed(SAMPLE_FEED, spec)[1][0]

        self.assertEqual(filter_by_min_relevance([paper], "high"), [paper])
        self.assertEqual(filter_by_min_relevance([paper], "medium"), [paper])

    def test_load_existing_arxiv_ids_reads_inventory_links(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            inventory = Path(tmpdir) / "source_inventory.md"
            inventory.write_text(
                "| url |\n| --- |\n| https://arxiv.org/abs/2305.03495v2 |\n",
                encoding="utf-8",
            )

            self.assertEqual(load_existing_arxiv_ids(inventory), {"2305.03495"})

    def test_render_inventory_row_escapes_markdown_pipes(self):
        spec = QuerySpec("apo-core", "automatic prompt optimization", "q1")
        paper = parse_atom_feed(SAMPLE_FEED, spec)[1][0]
        paper.title = "Prompt Optimization | A Test"

        row = render_inventory_row(paper)

        self.assertIn("Prompt Optimization \\| A Test", row)
        self.assertIn("paper-arxiv-2305-03495", row)


if __name__ == "__main__":
    unittest.main()
