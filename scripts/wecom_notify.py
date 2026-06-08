"""Send repository notifications to a WeCom group robot.

The module intentionally uses only Python's standard library so it can be
called from local scripts, scheduled jobs, or CI without installing packages.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable, Optional

ENV_WEBHOOK = "WECOM_BOT_WEBHOOK"
ENV_ENABLED = "WECOM_NOTIFY_ENABLED"

FALSE_VALUES = {"0", "false", "no", "off", "disabled"}


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
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    load_dotenv(Path(args.dotenv))

    try:
        content = _read_message(args)
        result = send_wecom_notification(
            content=content,
            msgtype=args.msgtype,
            webhook=args.webhook,
            timeout=args.timeout,
            dry_run=args.dry_run,
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
