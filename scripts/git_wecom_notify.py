"""Git hook notifications backed by the repository WeCom notifier."""

from __future__ import annotations

import argparse
import os
import subprocess
import time
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

try:
    from scripts.wecom_notify import NotificationError, load_dotenv, send_repository_notification
except ModuleNotFoundError:
    from wecom_notify import NotificationError, load_dotenv, send_repository_notification

ZERO_SHA = "0" * 40


@dataclass(frozen=True)
class PushUpdate:
    local_ref: str
    local_sha: str
    remote_ref: str
    remote_sha: str

    @property
    def display_ref(self) -> str:
        if self.remote_ref.startswith("refs/heads/"):
            return self.remote_ref.removeprefix("refs/heads/")
        if self.remote_ref.startswith("refs/tags/"):
            return self.remote_ref.removeprefix("refs/tags/")
        return self.remote_ref

    @property
    def is_delete(self) -> bool:
        return self.local_sha == ZERO_SHA


def repo_root() -> Path:
    output = _git("rev-parse", "--show-toplevel")
    return Path(output.strip())


def send_commit_notification(dry_run: bool = False) -> dict:
    root = repo_root()
    load_dotenv(root / ".env")
    branch = _current_branch()
    commit_hash, short_hash, subject, author_name, author_email = _git(
        "show",
        "-s",
        "--format=%H%x00%h%x00%s%x00%an%x00%ae",
        "HEAD",
    ).split("\x00")

    content = "\n".join(
        [
            "### Prompt Evolution commit completed",
            f"- repo: {root.name}",
            f"- branch: {branch}",
            f"- commit: `{short_hash}`",
            f"- subject: {subject}",
            f"- author: {author_name} <{author_email}>",
            f"- full_sha: `{commit_hash}`",
        ]
    )
    return send_repository_notification(content, dry_run=dry_run, repo=root)


def watch_push_and_notify(
    remote: str,
    remote_url: str,
    updates_file: Path,
    timeout_seconds: float = 60,
    interval_seconds: float = 2,
    dry_run: bool = False,
) -> Optional[dict]:
    root = repo_root()
    load_dotenv(root / ".env")
    updates = parse_push_updates(updates_file.read_text(encoding="utf-8").splitlines())
    updates = [update for update in updates if not update.is_delete]
    if not updates:
        return None

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if all(remote_ref_matches(remote, update.remote_ref, update.local_sha) for update in updates):
            content = build_push_notification(root.name, remote, remote_url, updates)
            return send_repository_notification(content, dry_run=dry_run, repo=root)
        time.sleep(interval_seconds)

    return None


def parse_push_updates(lines: Sequence[str]) -> list[PushUpdate]:
    updates: list[PushUpdate] = []
    for raw_line in lines:
        parts = raw_line.strip().split()
        if len(parts) != 4:
            continue
        updates.append(PushUpdate(*parts))
    return updates


def remote_ref_matches(remote: str, remote_ref: str, expected_sha: str) -> bool:
    if not expected_sha or expected_sha == ZERO_SHA:
        return False
    try:
        output = _git("ls-remote", remote, remote_ref, check=False)
    except OSError:
        return False

    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1] == remote_ref and parts[0] == expected_sha:
            return True
    return False


def build_push_notification(
    repo_name: str,
    remote: str,
    remote_url: str,
    updates: Sequence[PushUpdate],
) -> str:
    ref_lines = [
        f"- {update.display_ref}: `{update.local_sha[:12]}`"
        for update in updates
    ]
    return "\n".join(
        [
            "### Prompt Evolution push completed",
            f"- repo: {repo_name}",
            f"- remote: {remote}",
            f"- url: {_redact_url(remote_url)}",
            *ref_lines,
        ]
    )


def _current_branch() -> str:
    branch = _git("branch", "--show-current").strip()
    if branch:
        return branch
    return _git("rev-parse", "--short", "HEAD").strip()


def _redact_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.username or parsed.password:
        netloc = parsed.hostname or ""
        if parsed.port:
            netloc = f"{netloc}:{parsed.port}"
        return urllib.parse.urlunparse(parsed._replace(netloc=netloc))
    return url


def _git(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send WeCom notifications from Git hooks.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    commit_parser = subparsers.add_parser("post-commit")
    commit_parser.add_argument("--dry-run", action="store_true")

    push_parser = subparsers.add_parser("watch-push")
    push_parser.add_argument("--remote", required=True)
    push_parser.add_argument("--url", required=True)
    push_parser.add_argument("--updates-file", required=True)
    push_parser.add_argument("--timeout-seconds", type=float, default=60)
    push_parser.add_argument("--interval-seconds", type=float, default=2)
    push_parser.add_argument("--dry-run", action="store_true")

    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "post-commit":
            send_commit_notification(dry_run=args.dry_run)
        elif args.command == "watch-push":
            watch_push_and_notify(
                remote=args.remote,
                remote_url=args.url,
                updates_file=Path(args.updates_file),
                timeout_seconds=args.timeout_seconds,
                interval_seconds=args.interval_seconds,
                dry_run=args.dry_run,
            )
    except (NotificationError, subprocess.SubprocessError, OSError) as exc:
        print(f"git notification failed: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
