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


def _path_from_status_line(line: str) -> str:
    if len(line) >= 4 and line[2] == " ":
        path = line[3:]
    else:
        parts = line.strip().split(maxsplit=1)
        path = parts[-1] if parts else ""
    if " -> " in path:
        path = path.split(" -> ")[-1]
    return path.strip()


def _path_from_name_status_line(line: str) -> str:
    parts = [part for part in line.split("\t") if part]
    if len(parts) >= 2:
        return parts[-1].strip()
    return _path_from_status_line(line)


def _human_change_bullets(paths: list[str]) -> list[str]:
    normalized = {path.replace("\\", "/") for path in paths if path}
    bullets: list[str] = []

    if any(
        path in {"scripts/wecom_notify.py", "scripts/git_wecom_notify.py"}
        or path.startswith(".githooks/")
        for path in normalized
    ):
        bullets.append("企业微信通知：调整消息组装和发送入口，让 bot 消息先展示可读的改动摘要。")

    if any(path in {"scripts/git_wecom_notify.py"} or path.startswith(".githooks/") for path in normalized):
        bullets.append("Git 自动通知：commit/push hook 会复用同一套仓库通知格式。")

    if any(path.startswith("tests/") for path in normalized):
        bullets.append("测试覆盖：补充通知、Git hook 或接口检查相关单元测试，避免摘要格式回退。")

    if any(
        path in {"README.md", "CHANGELOG.md", "AGENTS.md", "CLAUDE.md"}
        or path.startswith("docs/")
        for path in normalized
    ):
        bullets.append("文档说明：更新 README、变更记录和相关说明文档，保持使用方式可追溯。")

    if any(path.startswith("scripts/llm_") or path == "docs/llm_clients.md" for path in normalized):
        bullets.append("LLM 配置检查：更新 OpenAI/OpenRouter 客户端或 smoke test 支撑后续实验。")

    if any(
        path.startswith("docs/source_")
        or path in {
            "docs/research_brief.md",
            "docs/literature_map.md",
            "docs/industry_practices.md",
            "docs/experiment_plan.md",
        }
        for path in normalized
    ):
        bullets.append("研究资料：补充资料搜集、文献地图、行业实践或实验计划相关内容。")

    if not bullets:
        top_level = sorted({path.split("/", 1)[0] for path in normalized})
        scope = "、".join(top_level[:3]) if top_level else "仓库文件"
        bullets.append(f"仓库更新：共涉及 {len(normalized)} 个文件，主要范围是 {scope}。")

    return [f"- {bullet}" for bullet in bullets[:5]]


def format_git_change_summary(
    status_output: str,
    diff_stat_output: str = "",
    last_commit_output: str = "",
    last_commit_stat_output: str = "",
    last_commit_files_output: str = "",
    max_lines: int = DEFAULT_MAX_GIT_LINES,
) -> str:
    """Format repository changes as concise WeCom markdown."""
    status_lines = [line for line in status_output.splitlines() if line.strip()]
    if status_lines:
        changed_paths = [_path_from_status_line(line) for line in status_lines]
        shown, hidden = _limit_lines(status_lines, max_lines)
        lines = [
            "",
            "### 主要修改内容",
            *_human_change_bullets(changed_paths),
            "",
            "### 涉及文件",
            f"- 工作区变更：{len(status_lines)} 个",
        ]
        lines.extend(f"- `{line}`" for line in shown)
        if hidden:
            lines.append(f"- 其余 {hidden} 个文件未展开")

        return "\n".join(lines)

    if last_commit_output:
        commit_file_lines = [
            line for line in last_commit_files_output.splitlines() if line.strip()
        ]
        changed_paths = [_path_from_name_status_line(line) for line in commit_file_lines]
        lines = [
            "",
            "### 主要修改内容",
            *_human_change_bullets(changed_paths),
            "",
            "### 涉及提交",
            f"- 最近提交：`{last_commit_output}`",
        ]
        if commit_file_lines:
            shown_files, hidden_files = _limit_lines(commit_file_lines, max_lines)
            lines.extend(["", "### 涉及文件"])
            lines.extend(f"- `{line}`" for line in shown_files)
            if hidden_files:
                lines.append(f"- 其余 {hidden_files} 个文件未展开")
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
    last_commit_files_output = ""
    if not status_output:
        last_commit_output = _run_git(root, ["log", "-1", "--pretty=format:%h %s"])
        last_commit_stat_output = _run_git(root, ["show", "--stat", "--format=", "HEAD"])
        last_commit_files_output = _run_git(root, ["show", "--name-status", "--format=", "HEAD"])

    return format_git_change_summary(
        status_output=status_output,
        diff_stat_output=diff_stat_output,
        last_commit_output=last_commit_output,
        last_commit_stat_output=last_commit_stat_output,
        last_commit_files_output=last_commit_files_output,
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
