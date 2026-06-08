"""Send repository notifications to a WeCom group robot.

The module intentionally uses only Python's standard library so it can be
called from local scripts, scheduled jobs, or CI without installing packages.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable, Optional

ENV_WEBHOOK = "WECOM_BOT_WEBHOOK"
ENV_ENABLED = "WECOM_NOTIFY_ENABLED"

FALSE_VALUES = {"0", "false", "no", "off", "disabled"}
DEFAULT_MAX_GIT_LINES = 12


class NotificationError(RuntimeError):
    """Raised when a notification cannot be delivered."""


def load_dotenv(path: Optional[Path] = None) -> None:
    """Load simple KEY=VALUE pairs from a .env file without overwriting env vars."""
    dotenv_path = path or Path.cwd() / ".env"
    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")

        if key and key not in os.environ:
            os.environ[key] = value


def notifications_enabled() -> bool:
    """Return whether outbound bot notifications are enabled."""
    return os.getenv(ENV_ENABLED, "true").strip().lower() not in FALSE_VALUES


def _run_git(repo: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def find_git_root(start: Optional[Path] = None) -> Optional[Path]:
    """Return the git repository root for start, if one can be found."""
    base = start or Path.cwd()
    result = subprocess.run(
        ["git", "-C", str(base), "rev-parse", "--show-toplevel"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return None
    root = result.stdout.strip()
    return Path(root) if root else None


def _limit_lines(lines: list[str], max_lines: int) -> tuple[list[str], int]:
    if max_lines <= 0:
        return [], len(lines)
    return lines[:max_lines], max(0, len(lines) - max_lines)


def format_git_change_summary(
    status_output: str,
    diff_stat_output: str = "",
    last_commit_output: str = "",
    last_commit_stat_output: str = "",
    max_lines: int = DEFAULT_MAX_GIT_LINES,
) -> str:
    """Format repository changes as concise WeCom markdown."""
    status_lines = [line for line in status_output.splitlines() if line.strip()]
    if status_lines:
        shown, hidden = _limit_lines(status_lines, max_lines)
        lines = [
            "",
            "### 主要修改内容",
            f"- 工作区变更：{len(status_lines)} 个文件",
        ]
        lines.extend(f"- `{line}`" for line in shown)
        if hidden:
            lines.append(f"- 其余 {hidden} 个文件未展开")

        stat_lines = [line for line in diff_stat_output.splitlines() if line.strip()]
        if stat_lines:
            shown_stat, hidden_stat = _limit_lines(stat_lines, max_lines)
            lines.extend(["", "### 变更统计"])
            lines.extend(f"> {line}" for line in shown_stat)
            if hidden_stat:
                lines.append(f"> 其余 {hidden_stat} 行未展开")

        return "\n".join(lines)

    if last_commit_output:
        lines = [
            "",
            "### 主要修改内容",
            f"- 最近提交：`{last_commit_output}`",
        ]
        stat_lines = [line for line in last_commit_stat_output.splitlines() if line.strip()]
        if stat_lines:
            shown_stat, hidden_stat = _limit_lines(stat_lines, max_lines)
            lines.extend(["", "### 提交统计"])
            lines.extend(f"> {line}" for line in shown_stat)
            if hidden_stat:
                lines.append(f"> 其余 {hidden_stat} 行未展开")
        return "\n".join(lines)

    return "\n### 主要修改内容\n- 未检测到 git 变更"


def collect_git_change_summary(
    repo: Optional[Path] = None,
    max_lines: int = DEFAULT_MAX_GIT_LINES,
) -> str:
    """Collect a concise git summary for notification messages."""
    root = repo or find_git_root()
    if root is None:
        return "\n### 主要修改内容\n- 当前目录不是 git 仓库"

    status_output = _run_git(root, ["status", "--short"])
    diff_stat_parts = [
        _run_git(root, ["diff", "--stat"]),
        _run_git(root, ["diff", "--cached", "--stat"]),
    ]
    diff_stat_output = "\n".join(part for part in diff_stat_parts if part)

    last_commit_output = ""
    last_commit_stat_output = ""
    if not status_output:
        last_commit_output = _run_git(root, ["log", "-1", "--pretty=format:%h %s"])
        last_commit_stat_output = _run_git(root, ["show", "--stat", "--format=", "HEAD"])

    return format_git_change_summary(
        status_output=status_output,
        diff_stat_output=diff_stat_output,
        last_commit_output=last_commit_output,
        last_commit_stat_output=last_commit_stat_output,
        max_lines=max_lines,
    )


def build_payload(
    content: str,
    msgtype: str = "markdown",
    mentioned_list: Optional[Iterable[str]] = None,
    mentioned_mobile_list: Optional[Iterable[str]] = None,
) -> dict[str, Any]:
    """Build a WeCom robot payload for text or markdown messages."""
    if not content or not content.strip():
        raise ValueError("notification content must not be empty")

    if msgtype == "markdown":
        return {
            "msgtype": "markdown",
            "markdown": {"content": content},
        }

    if msgtype == "text":
        text: dict[str, Any] = {"content": content}
        if mentioned_list:
            text["mentioned_list"] = list(mentioned_list)
        if mentioned_mobile_list:
            text["mentioned_mobile_list"] = list(mentioned_mobile_list)
        return {
            "msgtype": "text",
            "text": text,
        }

    raise ValueError("msgtype must be 'markdown' or 'text'")


def resolve_webhook(webhook: Optional[str] = None) -> str:
    """Resolve and validate the target WeCom webhook URL."""
    url = (webhook or os.getenv(ENV_WEBHOOK, "")).strip()
    if not url:
        raise NotificationError(
            f"missing webhook; set {ENV_WEBHOOK} or pass --webhook"
        )

    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise NotificationError("webhook must be an absolute HTTP(S) URL")

    return url


def send_wecom_notification(
    content: str,
    msgtype: str = "markdown",
    webhook: Optional[str] = None,
    timeout: float = 10,
    dry_run: bool = False,
    mentioned_list: Optional[Iterable[str]] = None,
    mentioned_mobile_list: Optional[Iterable[str]] = None,
) -> dict[str, Any]:
    """Send one notification to the configured WeCom robot."""
    payload = build_payload(
        content=content,
        msgtype=msgtype,
        mentioned_list=mentioned_list,
        mentioned_mobile_list=mentioned_mobile_list,
    )

    if not notifications_enabled():
        return {"ok": True, "skipped": True, "reason": "disabled", "payload": payload}

    url = resolve_webhook(webhook)

    if dry_run:
        return {"ok": True, "dry_run": True, "payload": payload}

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        response_text = exc.read().decode("utf-8", errors="replace")
        raise NotificationError(
            f"WeCom webhook HTTP {exc.code}: {response_text}"
        ) from exc
    except urllib.error.URLError as exc:
        raise NotificationError(f"WeCom webhook request failed: {exc}") from exc

    try:
        result = json.loads(response_body)
    except json.JSONDecodeError as exc:
        raise NotificationError(
            f"WeCom webhook returned non-JSON response: {response_body[:200]}"
        ) from exc

    if result.get("errcode") != 0:
        errmsg = result.get("errmsg", "unknown error")
        raise NotificationError(f"WeCom robot rejected message: {errmsg}")

    return result


def compose_repository_message(
    content: str,
    include_git_summary: bool = True,
    repo: Optional[Path] = None,
    max_git_lines: int = DEFAULT_MAX_GIT_LINES,
) -> str:
    """Compose the final notification body for repository events."""
    if not include_git_summary:
        return content
    return f"{content.rstrip()}{collect_git_change_summary(repo=repo, max_lines=max_git_lines)}"


def send_repository_notification(
    content: str,
    msgtype: str = "markdown",
    webhook: Optional[str] = None,
    timeout: float = 10,
    dry_run: bool = False,
    include_git_summary: bool = True,
    repo: Optional[Path] = None,
    max_git_lines: int = DEFAULT_MAX_GIT_LINES,
) -> dict[str, Any]:
    """Send a repository notification with the main git changes attached."""
    final_content = compose_repository_message(
        content=content,
        include_git_summary=include_git_summary,
        repo=repo,
        max_git_lines=max_git_lines,
    )
    return send_wecom_notification(
        content=final_content,
        msgtype=msgtype,
        webhook=webhook,
        timeout=timeout,
        dry_run=dry_run,
    )


def _read_message(args: argparse.Namespace) -> str:
    parts: list[str] = []

    if args.file:
        parts.append(Path(args.file).read_text(encoding="utf-8"))

    if args.message:
        parts.append(" ".join(args.message))

    if not parts and not sys.stdin.isatty():
        parts.append(sys.stdin.read())

    content = "\n".join(part.strip() for part in parts if part.strip())
    if not content:
        raise NotificationError("message content is required")

    return content


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send a notification to the configured WeCom group robot."
    )
    parser.add_argument("message", nargs="*", help="message content")
    parser.add_argument("--file", help="read message content from a UTF-8 file")
    parser.add_argument(
        "--msgtype",
        choices=("markdown", "text"),
        default="markdown",
        help="WeCom robot message type",
    )
    parser.add_argument(
        "--webhook",
        help=f"override {ENV_WEBHOOK}; prefer environment variables for secrets",
    )
    parser.add_argument(
        "--dotenv",
        default=".env",
        help="path to a dotenv file loaded before sending",
    )
    parser.add_argument("--timeout", type=float, default=10, help="request timeout")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print payload without sending the webhook request",
    )
    parser.add_argument(
        "--no-git-summary",
        action="store_true",
        help="do not append the repository's main git changes",
    )
    parser.add_argument(
        "--max-git-lines",
        type=int,
        default=DEFAULT_MAX_GIT_LINES,
        help="maximum git status/stat lines to include per section",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    load_dotenv(Path(args.dotenv))

    try:
        content = _read_message(args)
        result = send_repository_notification(
            content=content,
            msgtype=args.msgtype,
            webhook=args.webhook,
            timeout=args.timeout,
            dry_run=args.dry_run,
            include_git_summary=not args.no_git_summary,
            max_git_lines=args.max_git_lines,
        )
    except (NotificationError, ValueError) as exc:
        print(f"notification failed: {exc}", file=sys.stderr)
        return 1

    if result.get("dry_run"):
        print(json.dumps(result["payload"], ensure_ascii=False, indent=2))
    elif result.get("skipped"):
        print("notification skipped: disabled")
    else:
        print("notification sent")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
