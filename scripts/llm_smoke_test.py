"""Smoke tests for configured LLM model matrices.

By default this script runs in dry-run mode and prints request shapes without
sending network requests. Add --live after filling API keys in .env.
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import replace
from pathlib import Path
from typing import Any, Callable, Optional

try:
    from scripts.llm_clients import (
        LLMConfigError,
        LLMRequestError,
        call_openai_response,
        call_openrouter_chat,
        extract_openai_text,
        extract_openrouter_text,
        load_dotenv,
        resolve_openai_config,
        resolve_openai_models,
        resolve_openrouter_config,
        resolve_openrouter_models,
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
        resolve_openai_config,
        resolve_openai_models,
        resolve_openrouter_config,
        resolve_openrouter_models,
    )

TEST_PROMPT = "Reply with exactly: ok"
TEST_SYSTEM_PROMPT = "You are a smoke test. Keep the answer minimal."

SMOKE_OPENAI_MAX_OUTPUT_TOKENS = 96
SMOKE_OPENROUTER_MAX_TOKENS = 128
SMOKE_TIMEOUT_SECONDS = 120.0


def smoke_test_openai_model(model: str, dry_run: bool = True) -> dict[str, Any]:
    """Test one OpenAI model via the Responses API."""
    config = resolve_openai_config(require_api_key=not dry_run)
    config = replace(
        config,
        model=model,
        max_output_tokens=SMOKE_OPENAI_MAX_OUTPUT_TOKENS,
        reasoning_effort=_openai_reasoning_effort_for_model(model),
        timeout=SMOKE_TIMEOUT_SECONDS,
    )

    started = time.perf_counter()
    response = call_openai_response(
        prompt=TEST_PROMPT,
        instructions=TEST_SYSTEM_PROMPT,
        dry_run=dry_run,
        config=config,
    )
    if dry_run:
        return response

    text = extract_openai_text(response)
    return {
        "ok": bool(text),
        "provider": "openai",
        "model": model,
        "elapsed_seconds": round(time.perf_counter() - started, 2),
        "status": response.get("status"),
        "text": text[:120],
    }


def smoke_test_openrouter_model(model: str, dry_run: bool = True) -> dict[str, Any]:
    """Test one OpenRouter model via chat completions."""
    config = resolve_openrouter_config(require_api_key=not dry_run)
    config = replace(
        config,
        model=model,
        max_tokens=SMOKE_OPENROUTER_MAX_TOKENS,
        temperature=0.0,
        timeout=SMOKE_TIMEOUT_SECONDS,
    )

    started = time.perf_counter()
    response = call_openrouter_chat(
        prompt=TEST_PROMPT,
        system_prompt=TEST_SYSTEM_PROMPT,
        dry_run=dry_run,
        config=config,
    )
    if dry_run:
        return response

    text = extract_openrouter_text(response)
    choice = (response.get("choices") or [{}])[0]
    return {
        "ok": bool(text),
        "provider": "openrouter",
        "model": model,
        "elapsed_seconds": round(time.perf_counter() - started, 2),
        "finish_reason": choice.get("finish_reason"),
        "text": text[:120],
    }


def smoke_test_openai_models(
    dry_run: bool = True,
    models: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Run smoke tests for the configured OpenAI model matrix."""
    return _run_model_matrix(
        provider="openai",
        models=models or resolve_openai_models(),
        dry_run=dry_run,
        test_func=smoke_test_openai_model,
    )


def smoke_test_openrouter_models(
    dry_run: bool = True,
    models: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Run smoke tests for the configured OpenRouter model matrix."""
    return _run_model_matrix(
        provider="openrouter",
        models=models or resolve_openrouter_models(),
        dry_run=dry_run,
        test_func=smoke_test_openrouter_model,
    )


def smoke_test_all(dry_run: bool = True) -> dict[str, Any]:
    """Run all configured provider model matrices."""
    results = {
        "openai": smoke_test_openai_models(dry_run=dry_run),
        "openrouter": smoke_test_openrouter_models(dry_run=dry_run),
    }
    return {
        "ok": all(result["ok"] for result in results.values()),
        "dry_run": dry_run,
        "results": results,
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
        "--models",
        help="comma-separated model ids; only valid with --provider openai/openrouter",
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
    models = _parse_models_arg(args.models)

    if args.provider == "all" and models:
        print(
            json.dumps(
                {"ok": False, "error": "--models is only valid for one provider"},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    try:
        if args.provider == "openai":
            result = smoke_test_openai_models(dry_run=dry_run, models=models)
        elif args.provider == "openrouter":
            result = smoke_test_openrouter_models(dry_run=dry_run, models=models)
        else:
            result = smoke_test_all(dry_run=dry_run)
    except (LLMConfigError, LLMRequestError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok", False) else 1


def _run_model_matrix(
    provider: str,
    models: list[str],
    dry_run: bool,
    test_func: Callable[[str, bool], dict[str, Any]],
) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for model in models:
        try:
            results[model] = test_func(model, dry_run)
        except (LLMConfigError, LLMRequestError, ValueError) as exc:
            results[model] = {"ok": False, "provider": provider, "model": model, "error": str(exc)}

    return {
        "ok": all(result.get("ok") for result in results.values()),
        "provider": provider,
        "dry_run": dry_run,
        "models": results,
    }


def _openai_reasoning_effort_for_model(model: str) -> str:
    # Pro models reject "none"; keep smoke tests valid while using a tiny output cap.
    return "medium" if "-pro" in model else "none"


def _parse_models_arg(raw_models: Optional[str]) -> Optional[list[str]]:
    if not raw_models:
        return None

    models = [part.strip() for part in raw_models.split(",") if part.strip()]
    if not models:
        raise ValueError("--models must contain at least one model id")

    return models


if __name__ == "__main__":
    raise SystemExit(main())
