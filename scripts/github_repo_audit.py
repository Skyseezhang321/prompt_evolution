"""Generate source-audit drafts from locally cloned GitHub repositories.

This script scans repository structure and selected text files for evidence of
prompt optimization, evaluation loops, versioning, rollback, memory, context,
and agent workflow mechanics. It intentionally produces audit notes, not final
insights: human review is required before drawing conclusions.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional, Sequence

DEFAULT_CLONE_ROOT = Path("local_sources") / "raw" / "github_repo_clones"
DEFAULT_AUDIT_ROOT = Path("local_sources") / "raw" / "github_repo_audits"
DEFAULT_NOTES_DIR = Path("docs") / "github_repo_audit_notes"
MAX_TEXT_BYTES = 250_000
MAX_EXCERPTS_PER_REPO = 24
MAX_MATCHING_FILES = 80

SKIP_DIRS = {
    ".git",
    ".next",
    ".nuxt",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
}

TEXT_SUFFIXES = {
    ".cfg",
    ".conf",
    ".css",
    ".env",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".mdx",
    ".mjs",
    ".py",
    ".rs",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}

PATH_PATTERNS = {
    "prompt": re.compile(r"prompt|instruction|system[-_ ]?prompt|template", re.I),
    "eval": re.compile(r"eval|benchmark|grader|judge|score|test", re.I),
    "agent": re.compile(r"agent|subagent|skill|tool|workflow|orchestrat", re.I),
    "memory_context": re.compile(r"memory|context|rag|retriev", re.I),
    "versioning": re.compile(r"version|history|rollback|checkpoint|diff", re.I),
}

CONTENT_PATTERNS = {
    "prompt_optimization": re.compile(
        r"prompt optimization|optimi[sz]e(?:s|d|r)? prompt|prompt optimizer|system prompt slimming|prompt tuning",
        re.I,
    ),
    "evaluation": re.compile(
        r"eval(?:uation)?|benchmark|grader|judge|score|compare|pass@k|test set|held[- ]out",
        re.I,
    ),
    "iteration_loop": re.compile(
        r"iterate|iteration|loop|repeat|candidate|keep|discard|retain|rollback|checkpoint",
        re.I,
    ),
    "memory_context": re.compile(r"memory|context window|context engineering|rag|retrieval", re.I),
    "agent_workflow": re.compile(r"agent|subagent|tool call|workflow|orchestration|handoff", re.I),
    "risk_failure": re.compile(
        r"failure|risk|security|attack|sandbox|leak|drift|overfit|regression",
        re.I,
    ),
}


@dataclass(frozen=True)
class FileSignal:
    path: str
    size_bytes: int
    sha256: str
    path_tags: list[str]
    content_tags: list[str]
    excerpts: list[str]


@dataclass(frozen=True)
class RepoAudit:
    source_id: str
    full_name: str
    local_path: str
    commit_sha: str
    current_branch: str
    generated_at: str
    total_files_seen: int
    text_files_scanned: int
    readme_files: list[str]
    license_files: list[str]
    package_files: list[str]
    path_tag_counts: dict[str, int]
    content_tag_counts: dict[str, int]
    file_signals: list[FileSignal]
    audit_json_path: str
    audit_json_sha256: str = ""


def source_id_from_repo_dir(repo_dir: Path) -> str:
    return repo_dir.name


def infer_full_name(repo_dir: Path) -> str:
    try:
        url = run_git(["config", "--get", "remote.origin.url"], cwd=repo_dir)
    except subprocess.CalledProcessError:
        return repo_dir.name

    text = url.removesuffix(".git").rstrip("/")
    if text.startswith("https://github.com/"):
        return text.removeprefix("https://github.com/")
    if text.startswith("git@github.com:"):
        return text.removeprefix("git@github.com:")
    return text


def run_git(args: Sequence[str], cwd: Path) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout.strip()


def iter_repo_files(repo_dir: Path) -> Iterable[Path]:
    for path in repo_dir.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(repo_dir).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        yield path


def audit_repo(repo_dir: Path, audit_root: Path) -> RepoAudit:
    source_id = source_id_from_repo_dir(repo_dir)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    full_name = infer_full_name(repo_dir)
    commit_sha = git_or_empty(["rev-parse", "HEAD"], repo_dir)
    current_branch = git_or_empty(["branch", "--show-current"], repo_dir)

    all_files = list(iter_repo_files(repo_dir))
    total_files_seen = len(all_files)
    readme_files = rel_paths(repo_dir, [path for path in all_files if path.name.lower().startswith("readme")])
    license_files = rel_paths(repo_dir, [path for path in all_files if path.name.lower().startswith("license")])
    package_files = rel_paths(
        repo_dir,
        [
            path
            for path in all_files
            if path.name
            in {
                "package.json",
                "pyproject.toml",
                "requirements.txt",
                "Cargo.toml",
                "pnpm-lock.yaml",
                "uv.lock",
            }
        ],
    )

    signals: list[FileSignal] = []
    path_tag_counts: dict[str, int] = {key: 0 for key in PATH_PATTERNS}
    content_tag_counts: dict[str, int] = {key: 0 for key in CONTENT_PATTERNS}
    text_files_scanned = 0

    candidate_files = prioritize_files(repo_dir, all_files)
    for path in candidate_files:
        rel_path = path.relative_to(repo_dir).as_posix()
        path_tags = tags_for_path(rel_path)
        for tag in path_tags:
            path_tag_counts[tag] += 1

        if not is_text_file(path):
            if path_tags:
                signals.append(
                    FileSignal(
                        path=rel_path,
                        size_bytes=path.stat().st_size,
                        sha256=sha256_file(path),
                        path_tags=path_tags,
                        content_tags=[],
                        excerpts=[],
                    )
                )
            continue

        text_files_scanned += 1
        text = read_limited_text(path)
        content_tags = tags_for_content(text)
        excerpts = excerpt_matching_lines(text)
        for tag in content_tags:
            content_tag_counts[tag] += 1
        if path_tags or content_tags or excerpts:
            signals.append(
                FileSignal(
                    path=rel_path,
                    size_bytes=path.stat().st_size,
                    sha256=sha256_file(path),
                    path_tags=path_tags,
                    content_tags=content_tags,
                    excerpts=excerpts,
                )
            )
        if len(signals) >= MAX_MATCHING_FILES:
            break

    audit_dir = audit_root / source_id
    audit_dir.mkdir(parents=True, exist_ok=True)
    audit_json_path = audit_dir / "audit.json"
    audit = RepoAudit(
        source_id=source_id,
        full_name=full_name,
        local_path=str(repo_dir),
        commit_sha=commit_sha,
        current_branch=current_branch,
        generated_at=generated_at,
        total_files_seen=total_files_seen,
        text_files_scanned=text_files_scanned,
        readme_files=readme_files,
        license_files=license_files,
        package_files=package_files,
        path_tag_counts={key: value for key, value in path_tag_counts.items() if value},
        content_tag_counts={key: value for key, value in content_tag_counts.items() if value},
        file_signals=signals,
        audit_json_path=str(audit_json_path),
    )
    audit_json_path.write_text(
        json.dumps(asdict(audit), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return replace(audit, audit_json_sha256=sha256_file(audit_json_path))


def git_or_empty(args: Sequence[str], repo_dir: Path) -> str:
    try:
        return run_git(args, cwd=repo_dir)
    except subprocess.CalledProcessError:
        return ""


def rel_paths(repo_dir: Path, paths: Sequence[Path]) -> list[str]:
    return sorted(path.relative_to(repo_dir).as_posix() for path in paths)


def prioritize_files(repo_dir: Path, files: Sequence[Path]) -> list[Path]:
    def key(path: Path) -> tuple[int, str]:
        rel_path = path.relative_to(repo_dir).as_posix()
        rel_parts = path.relative_to(repo_dir).parts
        path_tags = tags_for_path(rel_path)
        root_priority = 0 if len(path.relative_to(repo_dir).parts) <= 2 else 1
        tag_priority = 0 if path_tags else 1
        readme_priority = 0 if path.name.lower().startswith("readme") else 1
        archive_priority = 1 if any(part in {"archive", "archives"} for part in rel_parts) else 0
        source_priority = 0 if any(part in {"src", "packages", "docs", "examples", "evals", "tests"} for part in rel_parts) else 1
        return (
            tag_priority,
            archive_priority,
            readme_priority,
            root_priority,
            source_priority,
            rel_path.lower(),
        )

    return sorted(files, key=key)


def tags_for_path(rel_path: str) -> list[str]:
    return [tag for tag, pattern in PATH_PATTERNS.items() if pattern.search(rel_path)]


def tags_for_content(text: str) -> list[str]:
    return [tag for tag, pattern in CONTENT_PATTERNS.items() if pattern.search(text)]


def is_text_file(path: Path) -> bool:
    if path.suffix.lower() in TEXT_SUFFIXES:
        return True
    if path.name.lower() in {"dockerfile", "makefile"}:
        return True
    return False


def read_limited_text(path: Path) -> str:
    data = path.read_bytes()[:MAX_TEXT_BYTES]
    return data.decode("utf-8", errors="replace")


def excerpt_matching_lines(text: str) -> list[str]:
    excerpts: list[str] = []
    for index, line in enumerate(text.splitlines(), start=1):
        compact = re.sub(r"\s+", " ", line).strip()
        if not compact:
            continue
        if any(pattern.search(compact) for pattern in CONTENT_PATTERNS.values()):
            excerpts.append(f"L{index}: {compact[:180]}")
        if len(excerpts) >= MAX_EXCERPTS_PER_REPO:
            break
    return excerpts


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def write_audit_note(audit: RepoAudit, notes_dir: Path, force: bool = False) -> Path:
    notes_dir.mkdir(parents=True, exist_ok=True)
    note_path = notes_dir / f"{audit.source_id}.md"
    if note_path.exists() and not force:
        return note_path
    note_path.write_text(render_audit_note(audit), encoding="utf-8")
    return note_path


def render_audit_note(audit: RepoAudit) -> str:
    top_signals = audit.file_signals[:20]
    lines = [
        f"# Source Audit: {audit.full_name}",
        "",
        "本笔记是源码审计草稿，不是最终 insight。只能用于记录可追溯观察和后续核验问题。",
        "",
        "## Source Fixation",
        "",
        f"- source_id: `{audit.source_id}`",
        f"- repository: https://github.com/{audit.full_name}",
        f"- local_path: `{audit.local_path}`",
        f"- commit_sha: `{audit.commit_sha}`",
        f"- branch: `{audit.current_branch}`",
        f"- generated_at: `{audit.generated_at}`",
        f"- audit_json: `{audit.audit_json_path}`",
        f"- audit_json_sha256: `{audit.audit_json_sha256}`",
        "",
        "## Structure Signals",
        "",
        f"- total_files_seen: {audit.total_files_seen}",
        f"- text_files_scanned: {audit.text_files_scanned}",
        f"- readme_files: {', '.join(audit.readme_files) or 'none'}",
        f"- license_files: {', '.join(audit.license_files) or 'none'}",
        f"- package_files: {', '.join(audit.package_files) or 'none'}",
        f"- path_tag_counts: `{json.dumps(audit.path_tag_counts, ensure_ascii=False)}`",
        f"- content_tag_counts: `{json.dumps(audit.content_tag_counts, ensure_ascii=False)}`",
        "",
        "## Evidence File Signals",
        "",
    ]
    if not top_signals:
        lines.append("- No matching files found by the first-pass scanner.")
    for signal in top_signals:
        tags = sorted(set(signal.path_tags + signal.content_tags))
        lines.extend(
            [
                f"### `{signal.path}`",
                "",
                f"- sha256: `{signal.sha256}`",
                f"- tags: {', '.join(tags) or 'none'}",
            ]
        )
        if signal.excerpts:
            lines.append("- excerpts:")
            for excerpt in signal.excerpts[:8]:
                lines.append(f"  - {escape_md(excerpt)}")
        lines.append("")

    lines.extend(
        [
            "## Claims To Verify Manually",
            "",
            "- README 中关于 optimization / eval / memory / agent loop 的说法是否有代码或配置支撑？",
            "- 是否存在固定样本、测试集、benchmark、grader 或人工评审流程？",
            "- 是否能定位核心 prompt、optimizer prompt、evaluator prompt、template 或 agent context 文件？",
            "- 是否记录版本、diff、失败案例、回滚点、成本或模型参数？",
            "- 哪些观察可以转成可测假设，哪些只是产品或 README 叙述？",
            "",
            "## Human Notes",
            "",
            "- TODO: 人工阅读核心文件后补充观察。",
            "- TODO: 标注可迁移方法、机制解释、反例和最小实验候选。",
        ]
    )
    return "\n".join(lines) + "\n"


def escape_md(text: str) -> str:
    return text.replace("|", "\\|")


def write_summary(
    audits: Sequence[RepoAudit],
    audit_root: Path,
    notes: Sequence[Path],
    prefix: str = "github_repo_audit_manifest",
) -> dict[str, Path]:
    audit_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = audit_root / f"{prefix}_{timestamp}.json"
    csv_path = audit_root / f"{prefix}_{timestamp}.csv"
    markdown_path = audit_root / f"{prefix}_{timestamp}.md"

    json_path.write_text(
        json.dumps([asdict(audit) for audit in audits], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    with csv_path.open("w", encoding="utf-8", newline="") as file:
        fieldnames = [
            "source_id",
            "full_name",
            "commit_sha",
            "total_files_seen",
            "text_files_scanned",
            "audit_json_path",
            "audit_json_sha256",
            "note_path",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for audit, note in zip(audits, notes):
            writer.writerow(
                {
                    "source_id": audit.source_id,
                    "full_name": audit.full_name,
                    "commit_sha": audit.commit_sha,
                    "total_files_seen": audit.total_files_seen,
                    "text_files_scanned": audit.text_files_scanned,
                    "audit_json_path": audit.audit_json_path,
                    "audit_json_sha256": audit.audit_json_sha256,
                    "note_path": str(note),
                }
            )
    markdown_path.write_text(render_summary_markdown(audits, notes), encoding="utf-8")
    return {"json": json_path, "csv": csv_path, "markdown": markdown_path}


def render_summary_markdown(audits: Sequence[RepoAudit], notes: Sequence[Path]) -> str:
    lines = [
        "# GitHub Repository Audit Manifest",
        "",
        f"Generated at: {datetime.now(timezone.utc).isoformat()}",
        "",
        "| repo | commit | files | text_scanned | audit_json_sha256 | note |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ]
    for audit, note in zip(audits, notes):
        lines.append(
            "| "
            + " | ".join(
                [
                    f"[{audit.full_name}](https://github.com/{audit.full_name})",
                    audit.commit_sha[:12],
                    str(audit.total_files_seen),
                    str(audit.text_files_scanned),
                    audit.audit_json_sha256[:12],
                    str(note).replace("\\", "/"),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def find_repo_dirs(clone_root: Path, source_ids: Sequence[str]) -> list[Path]:
    if source_ids:
        return [clone_root / source_id for source_id in source_ids]
    return sorted(path for path in clone_root.iterdir() if (path / ".git").exists())


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scan cloned GitHub repositories and generate source-audit drafts."
    )
    parser.add_argument("--clone-root", type=Path, default=DEFAULT_CLONE_ROOT)
    parser.add_argument("--audit-root", type=Path, default=DEFAULT_AUDIT_ROOT)
    parser.add_argument("--notes-dir", type=Path, default=DEFAULT_NOTES_DIR)
    parser.add_argument("--source-id", action="append", default=[])
    parser.add_argument("--force-notes", action="store_true")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    if not args.clone_root.exists():
        parser.error(f"clone root does not exist: {args.clone_root}")

    repo_dirs = find_repo_dirs(args.clone_root, args.source_id)
    missing = [path for path in repo_dirs if not (path / ".git").exists()]
    if missing:
        parser.error("missing cloned repos: " + ", ".join(str(path) for path in missing))

    audits = [audit_repo(repo_dir, args.audit_root) for repo_dir in repo_dirs]
    notes = [
        write_audit_note(audit, args.notes_dir, force=args.force_notes)
        for audit in audits
    ]
    summary_paths = write_summary(audits, args.audit_root, notes)

    for audit, note in zip(audits, notes):
        print(f"audited: {audit.full_name} {audit.commit_sha[:12]} -> {note}")
    for label, path in summary_paths.items():
        print(f"{label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
