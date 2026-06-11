"""Download arXiv PDFs and extract local text for deep reading.

PDFs and extracted text are stored under local_sources/raw by default, which is
ignored by git. The script writes a manifest with SHA256 hashes so later notes
can cite exactly which local file was read without committing third-party PDFs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

DEFAULT_INPUT = Path("outputs") / "arxiv_prompt_search" / "arxiv_focus_top80_20260608T131514Z.json"
DEFAULT_OUTPUT_ROOT = Path("local_sources") / "raw" / "arxiv_papers"
DEFAULT_MANIFEST_DIR = Path("outputs") / "arxiv_paper_downloads"
DEFAULT_USER_AGENT = "prompt-evolution-arxiv-paper-downloader/0.1"
DEFAULT_DELAY_SECONDS = 3.0

DEFAULT_KEY_IDS = [
    "2305.03495",  # ProTeGi
    "2309.08532",  # EvoPrompt
    "2309.16797",  # PromptBreeder
    "2507.19457",  # GEPA
    "2606.04465",  # SePO
    "2603.21520",  # MemAPO
    "2601.04055",  # Modular Prompt Optimization
    "2506.00400",  # Scaling Textual Gradients
    "2512.13598",  # Textual Gradients are a Flawed Metaphor
    "2603.19311",  # PrefPO
    "2410.02748",  # CriSPO
    "2605.26275",  # SPEAR
    "2504.04365",  # AutoPDL
    "2605.06623",  # MASPO
    "2605.21318",  # TextReg
]


@dataclass
class PaperRecord:
    arxiv_id: str
    title: str
    abs_url: str
    pdf_url: str
    rank: str = ""
    focus_score: str = ""
    published: str = ""
    updated: str = ""


@dataclass
class DownloadRecord:
    arxiv_id: str
    title: str
    abs_url: str
    pdf_url: str
    status: str
    pdf_path: str
    pdf_sha256: str
    pdf_bytes: int
    text_path: str
    text_sha256: str
    text_chars: int
    page_count: int
    error: str = ""


def normalize_arxiv_id(value: str) -> str:
    text = value.strip()
    if "/abs/" in text:
        text = text.rsplit("/abs/", 1)[1]
    elif "/pdf/" in text:
        text = text.rsplit("/pdf/", 1)[1].removesuffix(".pdf")
    elif text.startswith("http"):
        text = text.rstrip("/").rsplit("/", 1)[-1]
    text = text.split("#", 1)[0].split("?", 1)[0].strip("/")
    return re.sub(r"v\d+$", "", text)


def pdf_url_for(arxiv_id: str) -> str:
    return f"https://arxiv.org/pdf/{arxiv_id}"


def load_papers(path: Path) -> list[PaperRecord]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return load_papers_json(path)
    if suffix == ".csv":
        return load_papers_csv(path)
    raise ValueError("input must be a JSON or CSV file")


def load_papers_json(path: Path) -> list[PaperRecord]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("input JSON must contain a list")
    return [paper_from_mapping(item) for item in raw if isinstance(item, Mapping)]


def load_papers_csv(path: Path) -> list[PaperRecord]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return [paper_from_mapping(row) for row in csv.DictReader(file)]


def paper_from_mapping(item: Mapping[str, Any]) -> PaperRecord:
    arxiv_id = normalize_arxiv_id(str(item.get("arxiv_id", "")))
    abs_url = str(item.get("abs_url", "")).strip() or f"https://arxiv.org/abs/{arxiv_id}"
    pdf_url = str(item.get("pdf_url", "")).strip() or pdf_url_for(arxiv_id)
    return PaperRecord(
        arxiv_id=arxiv_id,
        title=str(item.get("title", "")).strip(),
        abs_url=abs_url,
        pdf_url=pdf_url,
        rank=str(item.get("rank", "")).strip(),
        focus_score=str(item.get("focus_score", "")).strip(),
        published=str(item.get("published", "")).strip(),
        updated=str(item.get("updated", "")).strip(),
    )


def select_papers(
    papers: Sequence[PaperRecord],
    arxiv_ids: Sequence[str],
    top_n: Optional[int],
) -> list[PaperRecord]:
    by_id = {paper.arxiv_id: paper for paper in papers}
    selected: list[PaperRecord] = []

    if arxiv_ids:
        for raw_id in arxiv_ids:
            arxiv_id = normalize_arxiv_id(raw_id)
            paper = by_id.get(arxiv_id)
            if paper is None:
                selected.append(
                    PaperRecord(
                        arxiv_id=arxiv_id,
                        title="",
                        abs_url=f"https://arxiv.org/abs/{arxiv_id}",
                        pdf_url=pdf_url_for(arxiv_id),
                    )
                )
            else:
                selected.append(paper)
        return dedupe_records(selected)

    if top_n is not None:
        return list(papers[:top_n])

    return [paper for paper in papers if paper.arxiv_id in DEFAULT_KEY_IDS]


def dedupe_records(papers: Sequence[PaperRecord]) -> list[PaperRecord]:
    seen: set[str] = set()
    result: list[PaperRecord] = []
    for paper in papers:
        if paper.arxiv_id and paper.arxiv_id not in seen:
            seen.add(paper.arxiv_id)
            result.append(paper)
    return result


def download_and_extract(
    paper: PaperRecord,
    output_root: Path,
    user_agent: str,
    force: bool,
) -> DownloadRecord:
    paper_dir = output_root / safe_arxiv_id(paper.arxiv_id)
    paper_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = paper_dir / "metadata.json"
    pdf_path = paper_dir / "paper.pdf"
    text_path = paper_dir / "paper.txt"

    metadata_path.write_text(
        json.dumps(asdict(paper), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    try:
        if force or not pdf_path.exists():
            download_file(paper.pdf_url, pdf_path, user_agent)

        pdf_sha = sha256_file(pdf_path)
        pdf_bytes = pdf_path.stat().st_size
        text, page_count = extract_pdf_text(pdf_path)
        text_path.write_text(text, encoding="utf-8")
        text_sha = sha256_file(text_path)

        return DownloadRecord(
            arxiv_id=paper.arxiv_id,
            title=paper.title,
            abs_url=paper.abs_url,
            pdf_url=paper.pdf_url,
            status="ok",
            pdf_path=str(pdf_path),
            pdf_sha256=pdf_sha,
            pdf_bytes=pdf_bytes,
            text_path=str(text_path),
            text_sha256=text_sha,
            text_chars=len(text),
            page_count=page_count,
        )
    except Exception as exc:
        return DownloadRecord(
            arxiv_id=paper.arxiv_id,
            title=paper.title,
            abs_url=paper.abs_url,
            pdf_url=paper.pdf_url,
            status="error",
            pdf_path=str(pdf_path) if pdf_path.exists() else "",
            pdf_sha256=sha256_file(pdf_path) if pdf_path.exists() else "",
            pdf_bytes=pdf_path.stat().st_size if pdf_path.exists() else 0,
            text_path=str(text_path) if text_path.exists() else "",
            text_sha256=sha256_file(text_path) if text_path.exists() else "",
            text_chars=text_path.stat().st_size if text_path.exists() else 0,
            page_count=0,
            error=f"{type(exc).__name__}: {exc}",
        )


def download_file(url: str, path: Path, user_agent: str) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = response.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body[:300]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"request failed: {exc}") from exc

    if not data.startswith(b"%PDF"):
        raise RuntimeError(f"downloaded file does not look like a PDF: {url}")
    path.write_bytes(data)


def extract_pdf_text(pdf_path: Path) -> tuple[str, int]:
    try:
        from pypdf import PdfReader
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "pypdf is required for text extraction; run with the bundled Codex Python"
        ) from exc

    reader = PdfReader(str(pdf_path))
    parts: list[str] = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        parts.append(f"\n\n--- PAGE {index} ---\n\n{text.strip()}")
    return "\n".join(parts).strip() + "\n", len(reader.pages)


def write_manifest(
    records: Sequence[DownloadRecord],
    manifest_dir: Path,
    prefix: str,
) -> dict[str, Path]:
    manifest_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = manifest_dir / f"{prefix}_{timestamp}.json"
    csv_path = manifest_dir / f"{prefix}_{timestamp}.csv"
    markdown_path = manifest_dir / f"{prefix}_{timestamp}.md"

    json_path.write_text(
        json.dumps([asdict(record) for record in records], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_manifest_csv(csv_path, records)
    markdown_path.write_text(render_manifest_markdown(records), encoding="utf-8")
    return {"json": json_path, "csv": csv_path, "markdown": markdown_path}


def write_manifest_csv(path: Path, records: Sequence[DownloadRecord]) -> None:
    fieldnames = list(asdict(records[0]).keys()) if records else [
        "arxiv_id",
        "title",
        "abs_url",
        "pdf_url",
        "status",
        "pdf_path",
        "pdf_sha256",
        "pdf_bytes",
        "text_path",
        "text_sha256",
        "text_chars",
        "page_count",
        "error",
    ]
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))


def render_manifest_markdown(records: Sequence[DownloadRecord]) -> str:
    ok_count = sum(1 for record in records if record.status == "ok")
    lines = [
        "# arXiv Paper Download Manifest",
        "",
        f"Generated at: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"- Papers requested: {len(records)}",
        f"- Successful downloads/extractions: {ok_count}",
        f"- Errors: {len(records) - ok_count}",
        "",
        "| status | arxiv_id | pages | text_chars | pdf_sha256 | local_text | title |",
        "| --- | --- | ---: | ---: | --- | --- | --- |",
    ]
    for record in records:
        lines.append(
            "| "
            + " | ".join(
                [
                    record.status,
                    f"[{record.arxiv_id}]({record.abs_url})",
                    str(record.page_count),
                    str(record.text_chars),
                    record.pdf_sha256[:12],
                    record.text_path,
                    md_cell(record.title or record.error),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def safe_arxiv_id(arxiv_id: str) -> str:
    return arxiv_id.replace("/", "_")


def md_cell(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().replace("|", "\\|")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download selected arXiv PDFs and extract local text for reading."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--manifest-dir", type=Path, default=DEFAULT_MANIFEST_DIR)
    parser.add_argument("--prefix", default="arxiv_key_papers")
    parser.add_argument("--arxiv-id", action="append", default=[])
    parser.add_argument("--top-n", type=int, default=None)
    parser.add_argument("--delay-seconds", type=float, default=DEFAULT_DELAY_SECONDS)
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--list-defaults",
        action="store_true",
        help="Print default key paper ids and exit.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    if args.top_n is not None and args.top_n < 1:
        parser.error("--top-n must be >= 1")
    if args.delay_seconds < 0:
        parser.error("--delay-seconds must be >= 0")

    if args.list_defaults:
        for arxiv_id in DEFAULT_KEY_IDS:
            print(arxiv_id)
        return 0

    papers = load_papers(args.input)
    selected = select_papers(papers, args.arxiv_id, args.top_n)
    if not selected:
        raise SystemExit("no papers selected")

    records: list[DownloadRecord] = []
    for index, paper in enumerate(selected, start=1):
        if index > 1 and args.delay_seconds > 0:
            time.sleep(args.delay_seconds)
        print(f"[{index}/{len(selected)}] {paper.arxiv_id} {paper.title}")
        record = download_and_extract(
            paper,
            output_root=args.output_root,
            user_agent=args.user_agent,
            force=args.force,
        )
        records.append(record)
        print(f"  {record.status}: pages={record.page_count} chars={record.text_chars}")
        if record.error:
            print(f"  error: {record.error}")

    paths = write_manifest(records, args.manifest_dir, args.prefix)
    print("")
    print(f"Done: {sum(1 for record in records if record.status == 'ok')}/{len(records)} ok")
    for label, path in paths.items():
        print(f"{label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
