"""Smoke tests for configured LLM providers.

By default this script runs in dry-run mode and prints the request shape without
sending network requests. Add --live after filling API keys in .env.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from scripts.llm_clients import (
        LLMConfigError,
        LLMRequestError,
        call_openai_response,
        call_openrouter_chat,
        extract_openai_text,
        extract_openrouter_text,
        load_dotenv,
    )
except ModuleNotFoundError:
    from llm_clients import (
        LLMConfigError,
        LLMRequestError,
        call_openai_response,
        call_openrouter_chat,
        extract_openai_text,
        extract_openrouter_text,
        load_dotenv,
    )

TEST_PROMPT = "请用一句话回复：LLM API 配置正常。"
TEST_SYSTEM_PROMPT = "你是一个用于验证 API 配置的测试助手。回答要简短。"


def smoke_test_openai_response(dry_run: bool = True) -> dict[str, Any]:
    """Test OpenAI official API configuration via the Responses API."""
    response = call_openai_response(
        prompt=TEST_PROMPT,
        instructions=TEST_SYSTEM_PROMPT,
        dry_run=dry_run,
    )
    if dry_run:
        return response

    return {
        "ok": True,
        "provider": "openai",
        "text": extract_openai_text(response),
        "raw": response,
    }


def smoke_test_openrouter_chat(dry_run: bool = True) -> dict[str, Any]:
    """Test OpenRouter configuration via chat completions."""
    response = call_openrouter_chat(
        prompt=TEST_PROMPT,
        system_prompt=TEST_SYSTEM_PROMPT,
        dry_run=dry_run,
    )
    if dry_run:
        return response

    return {
        "ok": True,
        "provider": "openrouter",
        "text": extract_openrouter_text(response),
        "raw": response,
    }


def smoke_test_all(dry_run: bool = True) -> dict[str, Any]:
    """Run both provider smoke tests and collect provider-specific errors."""
    results: dict[str, Any] = {}
    errors: dict[str, str] = {}

    for provider, test_func in (
        ("openai", smoke_test_openai_response),
        ("openrouter", smoke_test_openrouter_chat),
    ):
        try:
            results[provider] = test_func(dry_run=dry_run)
        except (LLMConfigError, LLMRequestError, ValueError) as exc:
            errors[provider] = str(exc)

    return {
        "ok": not errors,
        "dry_run": dry_run,
        "results": results,
        "errors": errors,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run LLM provider smoke tests.")
    parser.add_argument(
        "--provider",
        choices=("all", "openai", "openrouter"),
        default="all",
        help="which provider to test",
    )
    parser.add_argument(
        "--dotenv",
        default=".env",
        help="path to dotenv file loaded before testing",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="send real API requests instead of printing dry-run payloads",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_dotenv(Path(args.dotenv))
    dry_run = not args.live

    try:
        if args.provider == "openai":
            result = smoke_test_openai_response(dry_run=dry_run)
        elif args.provider == "openrouter":
            result = smoke_test_openrouter_chat(dry_run=dry_run)
        else:
            result = smoke_test_all(dry_run=dry_run)
    except (LLMConfigError, LLMRequestError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok", False) else 1


if __name__ == "__main__":
    raise SystemExit(main())
