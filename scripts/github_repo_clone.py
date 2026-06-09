"""Shallow clone GitHub repositories for source-level audit.

The cloned repositories live under local_sources/raw by default, which is
ignored by git. The script records exact commits and local paths so later notes
can cite what was inspected without committing third-party source code.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Sequence

DEFAULT_OUTPUT_ROOT = Path("local_sources") / "raw" / "github_repo_clones"
DEFAULT_MANIFEST_PREFIX = "github_repo_clone_manifest"


@dataclass(frozen=True)
class RepoTarget:
    source_id: str
    full_name: str
    priority: str
    rationale: str


@dataclass(frozen=True)
class CloneRecord:
    source_id: str
    full_name: str
    priority: str
    rationale: str
    status: str
    clone_url: str
    local_path: str
    commit_sha: str
    current_branch: str
    origin_head: str
    commit_author_date: str
    commit_subject: str
    readme_paths: list[str]
    readme_sha256: list[str]
    license_paths: list[str]
    license_sha256: list[str]
    cloned_at: str
    error: str = ""


DEFAULT_TARGETS: tuple[RepoTarget, ...] = (
    RepoTarget(
        "repo-linshenkx-prompt-optimizer",
        "linshenkx/prompt-optimizer",
        "core",
        "direct prompt optimizer; audit optimizer templates, eval, and prompt asset storage",
    ),
    RepoTarget(
        "repo-karpathy-autoresearch",
        "karpathy/autoresearch",
        "core",
        "self-evolving agent experiment loop; audit program/context and retain-discard mechanics",
    ),
    RepoTarget(
        "repo-humanlayer-12-factor-agents",
        "humanlayer/12-factor-agents",
        "core",
        "agent/context engineering principles; audit prompt/context governance rules",
    ),
    RepoTarget(
        "repo-affaan-m-ecc",
        "affaan-m/ECC",
        "verification",
        "strong README claims about memory, evals, and system prompt slimming; audit evidence",
    ),
    RepoTarget(
        "repo-dair-ai-prompt-engineering-guide",
        "dair-ai/Prompt-Engineering-Guide",
        "reference",
        "taxonomy/resource source for prompt and context engineering",
    ),
    RepoTarget(
        "repo-shanraisshan-claude-code-best-practice",
        "shanraisshan/claude-code-best-practice",
        "reference",
        "coding-agent workflow, memory, skills, and orchestration reference",
    ),
    RepoTarget(
        "repo-f-prompts-chat",
        "f/prompts.chat",
        "data",
        "prompt library / prompt dataset candidate",
    ),
    RepoTarget(
        "repo-pathwaycom-llm-app",
        "pathwaycom/llm-app",
        "peripheral",
        "RAG/context pipeline boundary reference",
    ),
    RepoTarget(
        "repo-google-gemini-gemini-cli",
        "google-gemini/gemini-cli",
        "scenario",
        "agent CLI scenario candidate",
    ),
    RepoTarget(
        "repo-browser-use-browser-use",
        "browser-use/browser-use",
        "scenario",
        "browser-agent tool-use scenario candidate",
    ),
)

PRESETS = {
    "core4": [
        "repo-linshenkx-prompt-optimizer",
        "repo-karpathy-autoresearch",
        "repo-humanlayer-12-factor-agents",
        "repo-affaan-m-ecc",
    ],
    "strict8": [
        "repo-linshenkx-prompt-optimizer",
        "repo-karpathy-autoresearch",
        "repo-dair-ai-prompt-engineering-guide",
        "repo-humanlayer-12-factor-agents",
        "repo-shanraisshan-claude-code-best-practice",
        "repo-affaan-m-ecc",
        "repo-f-prompts-chat",
        "repo-pathwaycom-llm-app",
    ],
    "wide10": [target.source_id for target in DEFAULT_TARGETS],
}


def source_id_for(full_name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", full_name.lower()).strip("-")
    return f"repo-{slug}"


def safe_dir_name(target: RepoTarget) -> str:
    return target.source_id


def clone_url_for(full_name: str) -> str:
    return f"https://github.com/{full_name}.git"


def targets_for(preset: str, extra_repos: Sequence[str]) -> list[RepoTarget]:
    by_id = {target.source_id: target for target in DEFAULT_TARGETS}
    targets = [by_id[source_id] for source_id in PRESETS[preset]]
    for repo in extra_repos:
        full_name = repo.strip().removesuffix(".git")
        if full_name.startswith("https://github.com/"):
            full_name = full_name.removeprefix("https://github.com/").strip("/")
        if not full_name:
            continue
        source_id = source_id_for(full_name)
        if source_id not in {target.source_id for target in targets}:
            targets.append(
                RepoTarget(
                    source_id=source_id,
                    full_name=full_name,
                    priority="extra",
                    rationale="user-supplied repository",
                )
            )
    return targets


def run_git(args: Sequence[str], cwd: Optional[Path] = None) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=str(cwd) if cwd else None,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout.strip()


def clone_or_collect(target: RepoTarget, output_root: Path) -> CloneRecord:
    output_root.mkdir(parents=True, exist_ok=True)
    local_path = output_root / safe_dir_name(target)
    clone_url = clone_url_for(target.full_name)
    cloned_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    try:
        if local_path.exists():
            if not (local_path / ".git").exists():
                raise RuntimeError(f"target path exists but is not a git repo: {local_path}")
            status = "existing"
        else:
            run_git(
                [
                    "clone",
                    "--depth",
                    "1",
                    "--no-tags",
                    clone_url,
                    str(local_path),
                ]
            )
            status = "cloned"

        return collect_clone_record(target, local_path, clone_url, status, cloned_at)
    except (subprocess.CalledProcessError, RuntimeError) as exc:
        return CloneRecord(
            source_id=target.source_id,
            full_name=target.full_name,
            priority=target.priority,
            rationale=target.rationale,
            status="error",
            clone_url=clone_url,
            local_path=str(local_path),
            commit_sha="",
            current_branch="",
            origin_head="",
            commit_author_date="",
            commit_subject="",
            readme_paths=[],
            readme_sha256=[],
            license_paths=[],
            license_sha256=[],
            cloned_at=cloned_at,
            error=str(exc),
        )


def collect_clone_record(
    target: RepoTarget,
    local_path: Path,
    clone_url: str,
    status: str,
    cloned_at: str,
) -> CloneRecord:
    readme_paths = find_root_files(local_path, "README*")
    license_paths = find_root_files(local_path, "LICENSE*")
    return CloneRecord(
        source_id=target.source_id,
        full_name=target.full_name,
        priority=target.priority,
        rationale=target.rationale,
        status=status,
        clone_url=clone_url,
        local_path=str(local_path),
        commit_sha=run_git(["rev-parse", "HEAD"], cwd=local_path),
        current_branch=run_git(["branch", "--show-current"], cwd=local_path),
        origin_head=resolve_origin_head(local_path),
        commit_author_date=run_git(["show", "-s", "--format=%aI", "HEAD"], cwd=local_path),
        commit_subject=run_git(["show", "-s", "--format=%s", "HEAD"], cwd=local_path),
        readme_paths=[str(path.relative_to(local_path)) for path in readme_paths],
        readme_sha256=[sha256_file(path) for path in readme_paths],
        license_paths=[str(path.relative_to(local_path)) for path in license_paths],
        license_sha256=[sha256_file(path) for path in license_paths],
        cloned_at=cloned_at,
    )


def resolve_origin_head(repo_dir: Path) -> str:
    try:
        return run_git(["symbolic-ref", "--short", "refs/remotes/origin/HEAD"], cwd=repo_dir)
    except subprocess.CalledProcessError:
        return ""


def find_root_files(repo_dir: Path, pattern: str) -> list[Path]:
    return sorted(path for path in repo_dir.glob(pattern) if path.is_file())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def write_manifest(
    records: Sequence[CloneRecord],
    output_root: Path,
    prefix: str = DEFAULT_MANIFEST_PREFIX,
) -> dict[str, Path]:
    manifest_dir = output_root / "_manifests"
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


def write_manifest_csv(path: Path, records: Sequence[CloneRecord]) -> None:
    fieldnames = list(asdict(records[0]).keys()) if records else list(CloneRecord.__dataclass_fields__)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            row = asdict(record)
            row["readme_paths"] = ";".join(record.readme_paths)
            row["readme_sha256"] = ";".join(record.readme_sha256)
            row["license_paths"] = ";".join(record.license_paths)
            row["license_sha256"] = ";".join(record.license_sha256)
            writer.writerow(row)


def render_manifest_markdown(records: Sequence[CloneRecord]) -> str:
    ok_count = sum(1 for record in records if record.status in {"cloned", "existing"})
    lines = [
        "# GitHub Repository Clone Manifest",
        "",
        f"Generated at: {datetime.now(timezone.utc).isoformat()}",
        "",
        f"- Targets: {len(records)}",
        f"- Available local repos: {ok_count}",
        f"- Errors: {len(records) - ok_count}",
        "",
        "| status | source_id | repo | commit | branch | readme_sha256 | local_path |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for record in records:
        commit = record.commit_sha[:12] if record.commit_sha else ""
        readme_sha = record.readme_sha256[0][:12] if record.readme_sha256 else ""
        lines.append(
            "| "
            + " | ".join(
                [
                    record.status,
                    record.source_id,
                    f"[{record.full_name}](https://github.com/{record.full_name})",
                    commit,
                    record.current_branch or record.origin_head,
                    readme_sha,
                    record.local_path.replace("\\", "/"),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Shallow clone selected GitHub repositories for local audit."
    )
    parser.add_argument("--preset", choices=sorted(PRESETS), default="core4")
    parser.add_argument("--repo", action="append", default=[], help="extra owner/name repository")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--manifest-prefix", default=DEFAULT_MANIFEST_PREFIX)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    selected_targets = targets_for(args.preset, args.repo)

    if args.dry_run:
        print(
            json.dumps(
                [asdict(target) for target in selected_targets],
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    records = [clone_or_collect(target, args.output_root) for target in selected_targets]
    paths = write_manifest(records, args.output_root, args.manifest_prefix)

    for record in records:
        print(f"{record.status}: {record.full_name} {record.commit_sha[:12]} {record.local_path}")
        if record.error:
            print(f"  error: {record.error}")
    for label, path in paths.items():
        print(f"{label}: {path}")
    return 0 if all(record.status != "error" for record in records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
