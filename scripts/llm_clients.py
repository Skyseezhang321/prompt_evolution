"""Small LLM API clients for OpenAI and OpenRouter.

The module uses only Python's standard library so early experiments can run
without dependency setup. OpenAI uses the Responses API, while OpenRouter uses
its OpenAI-compatible chat completions endpoint.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterator, Mapping, Optional, Sequence

ENV_OPENAI_API_KEY = "OPENAI_API_KEY"
ENV_OPENAI_BASE_URL = "OPENAI_BASE_URL"
ENV_OPENAI_MODEL = "OPENAI_MODEL"
ENV_OPENAI_MODELS = "OPENAI_MODELS"
ENV_OPENAI_TIMEOUT_SECONDS = "OPENAI_TIMEOUT_SECONDS"
ENV_OPENAI_MAX_OUTPUT_TOKENS = "OPENAI_MAX_OUTPUT_TOKENS"
ENV_OPENAI_REASONING_EFFORT = "OPENAI_REASONING_EFFORT"
ENV_OPENAI_TEXT_VERBOSITY = "OPENAI_TEXT_VERBOSITY"

ENV_OPENROUTER_API_KEY = "OPENROUTER_API_KEY"
ENV_OPENROUTER_BASE_URL = "OPENROUTER_BASE_URL"
ENV_OPENROUTER_MODEL = "OPENROUTER_MODEL"
ENV_OPENROUTER_MODELS = "OPENROUTER_MODELS"
ENV_OPENROUTER_TIMEOUT_SECONDS = "OPENROUTER_TIMEOUT_SECONDS"
ENV_OPENROUTER_MAX_TOKENS = "OPENROUTER_MAX_TOKENS"
ENV_OPENROUTER_TEMPERATURE = "OPENROUTER_TEMPERATURE"
ENV_OPENROUTER_HTTP_REFERER = "OPENROUTER_HTTP_REFERER"
ENV_OPENROUTER_APP_TITLE = "OPENROUTER_APP_TITLE"
ENV_OPENROUTER_EMBED_MODEL = "OPENROUTER_EMBED_MODEL"
DEFAULT_OPENROUTER_EMBED_MODEL = "baai/bge-m3"
OPENROUTER_EMBEDDINGS_PATH = "/embeddings"

DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"
DEFAULT_OPENAI_MODEL = "gpt-5.5"
DEFAULT_OPENAI_MODELS = (
    "gpt-5.5",
    "gpt-5.5-pro",
    "gpt-5.4",
    "gpt-5.4-pro",
    "gpt-5.4-mini",
    "gpt-5.4-nano",
)
DEFAULT_OPENAI_TIMEOUT_SECONDS = 60.0
DEFAULT_OPENAI_MAX_OUTPUT_TOKENS = 512
DEFAULT_OPENAI_REASONING_EFFORT = "none"
DEFAULT_OPENAI_TEXT_VERBOSITY = "low"

DEFAULT_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_OPENROUTER_MODEL = "deepseek/deepseek-v4-pro"
DEFAULT_OPENROUTER_MODELS = (
    "deepseek/deepseek-v4-pro",
    "qwen/qwen3.7-max",
    "z-ai/glm-5.1",
    "minimax/minimax-m3",
    "moonshotai/kimi-k2.6",
)
DEFAULT_OPENROUTER_TIMEOUT_SECONDS = 60.0
DEFAULT_OPENROUTER_MAX_TOKENS = 512
DEFAULT_OPENROUTER_TEMPERATURE = 0.2

OPENAI_RESPONSES_PATH = "/responses"
OPENROUTER_CHAT_COMPLETIONS_PATH = "/chat/completions"


class LLMConfigError(RuntimeError):
    """Raised when LLM API configuration is missing or invalid."""


class LLMRequestError(RuntimeError):
    """Raised when an LLM API request fails."""


@dataclass(frozen=True)
class OpenAIConfig:
    api_key: str
    base_url: str
    model: str
    timeout: float
    max_output_tokens: int
    reasoning_effort: str
    text_verbosity: str


@dataclass(frozen=True)
class OpenRouterConfig:
    api_key: str
    base_url: str
    model: str
    timeout: float
    max_tokens: int
    temperature: float
    http_referer: str
    app_title: str


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


def resolve_openai_config(require_api_key: bool = True) -> OpenAIConfig:
    """Read OpenAI settings from environment variables."""
    api_key = os.getenv(ENV_OPENAI_API_KEY, "").strip()
    if require_api_key and not api_key:
        raise LLMConfigError(f"missing API key; set {ENV_OPENAI_API_KEY}")

    base_url = _resolve_base_url(
        ENV_OPENAI_BASE_URL,
        DEFAULT_OPENAI_BASE_URL,
    )
    return OpenAIConfig(
        api_key=api_key,
        base_url=base_url,
        model=_read_str_env(ENV_OPENAI_MODEL, DEFAULT_OPENAI_MODEL),
        timeout=_read_float_env(
            ENV_OPENAI_TIMEOUT_SECONDS,
            DEFAULT_OPENAI_TIMEOUT_SECONDS,
            minimum=0.1,
        ),
        max_output_tokens=_read_int_env(
            ENV_OPENAI_MAX_OUTPUT_TOKENS,
            DEFAULT_OPENAI_MAX_OUTPUT_TOKENS,
            minimum=1,
        ),
        reasoning_effort=_read_str_env(
            ENV_OPENAI_REASONING_EFFORT,
            DEFAULT_OPENAI_REASONING_EFFORT,
        ),
        text_verbosity=_read_str_env(
            ENV_OPENAI_TEXT_VERBOSITY,
            DEFAULT_OPENAI_TEXT_VERBOSITY,
        ),
    )


def resolve_openai_models() -> list[str]:
    """Read the OpenAI model matrix from OPENAI_MODELS."""
    return _read_csv_env(ENV_OPENAI_MODELS, DEFAULT_OPENAI_MODELS)


def resolve_openrouter_config(require_api_key: bool = True) -> OpenRouterConfig:
    """Read OpenRouter settings from environment variables."""
    api_key = os.getenv(ENV_OPENROUTER_API_KEY, "").strip()
    if require_api_key and not api_key:
        raise LLMConfigError(f"missing API key; set {ENV_OPENROUTER_API_KEY}")

    base_url = _resolve_base_url(
        ENV_OPENROUTER_BASE_URL,
        DEFAULT_OPENROUTER_BASE_URL,
    )
    return OpenRouterConfig(
        api_key=api_key,
        base_url=base_url,
        model=_read_str_env(ENV_OPENROUTER_MODEL, DEFAULT_OPENROUTER_MODEL),
        timeout=_read_float_env(
            ENV_OPENROUTER_TIMEOUT_SECONDS,
            DEFAULT_OPENROUTER_TIMEOUT_SECONDS,
            minimum=0.1,
        ),
        max_tokens=_read_int_env(
            ENV_OPENROUTER_MAX_TOKENS,
            DEFAULT_OPENROUTER_MAX_TOKENS,
            minimum=1,
        ),
        temperature=_read_float_env(
            ENV_OPENROUTER_TEMPERATURE,
            DEFAULT_OPENROUTER_TEMPERATURE,
            minimum=0,
        ),
        http_referer=os.getenv(ENV_OPENROUTER_HTTP_REFERER, "").strip(),
        app_title=os.getenv(ENV_OPENROUTER_APP_TITLE, "").strip(),
    )


def resolve_openrouter_models() -> list[str]:
    """Read the OpenRouter model matrix from OPENROUTER_MODELS."""
    return _read_csv_env(ENV_OPENROUTER_MODELS, DEFAULT_OPENROUTER_MODELS)


def build_openai_response_payload(
    prompt: str,
    config: Optional[OpenAIConfig] = None,
    instructions: Optional[str] = None,
) -> dict[str, Any]:
    """Build a Responses API payload for a single text prompt."""
    if not prompt or not prompt.strip():
        raise ValueError("prompt must not be empty")

    resolved_config = config or resolve_openai_config(require_api_key=False)
    payload: dict[str, Any] = {
        "model": resolved_config.model,
        "input": prompt,
        "max_output_tokens": resolved_config.max_output_tokens,
    }

    if instructions and instructions.strip():
        payload["instructions"] = instructions
    if resolved_config.reasoning_effort:
        payload["reasoning"] = {"effort": resolved_config.reasoning_effort}
    if resolved_config.text_verbosity:
        payload["text"] = {"verbosity": resolved_config.text_verbosity}

    return payload


def call_openai_response(
    prompt: str,
    instructions: Optional[str] = None,
    dry_run: bool = False,
    config: Optional[OpenAIConfig] = None,
    model: Optional[str] = None,
) -> dict[str, Any]:
    """Call OpenAI's Responses API, or return request details in dry-run mode."""
    resolved_config = config or resolve_openai_config(require_api_key=not dry_run)
    if model:
        resolved_config = replace(resolved_config, model=model)
    payload = build_openai_response_payload(
        prompt=prompt,
        config=resolved_config,
        instructions=instructions,
    )
    url = _join_url(resolved_config.base_url, OPENAI_RESPONSES_PATH)
    headers = _build_headers(resolved_config.api_key)

    if dry_run:
        return _dry_run_result("openai", url, headers, payload)

    return _post_json(url, headers, payload, resolved_config.timeout)


def build_chat_messages(
    prompt: str,
    system_prompt: Optional[str] = None,
) -> list[dict[str, str]]:
    """Build a minimal chat message list from a user prompt."""
    if not prompt or not prompt.strip():
        raise ValueError("prompt must not be empty")

    messages: list[dict[str, str]] = []
    if system_prompt and system_prompt.strip():
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    return messages


def build_openrouter_chat_payload(
    messages: Sequence[Mapping[str, str]],
    config: Optional[OpenRouterConfig] = None,
) -> dict[str, Any]:
    """Build an OpenRouter chat completions payload."""
    normalized_messages = _normalize_messages(messages)
    resolved_config = config or resolve_openrouter_config(require_api_key=False)

    return {
        "model": resolved_config.model,
        "messages": normalized_messages,
        "max_tokens": resolved_config.max_tokens,
        "temperature": resolved_config.temperature,
    }


def call_openrouter_chat(
    prompt: Optional[str] = None,
    messages: Optional[Sequence[Mapping[str, str]]] = None,
    system_prompt: Optional[str] = None,
    dry_run: bool = False,
    config: Optional[OpenRouterConfig] = None,
    model: Optional[str] = None,
) -> dict[str, Any]:
    """Call OpenRouter chat completions, or return request details in dry-run mode."""
    if messages is not None and prompt is not None:
        raise ValueError("pass either messages or prompt, not both")
    if messages is None:
        if prompt is None:
            raise ValueError("prompt or messages is required")
        messages = build_chat_messages(prompt, system_prompt=system_prompt)

    resolved_config = config or resolve_openrouter_config(require_api_key=not dry_run)
    if model:
        resolved_config = replace(resolved_config, model=model)
    payload = build_openrouter_chat_payload(messages, config=resolved_config)
    url = _join_url(resolved_config.base_url, OPENROUTER_CHAT_COMPLETIONS_PATH)
    headers = _build_headers(
        resolved_config.api_key,
        {
            "HTTP-Referer": resolved_config.http_referer,
            "X-OpenRouter-Title": resolved_config.app_title,
        },
    )

    if dry_run:
        return _dry_run_result("openrouter", url, headers, payload)

    return _post_json(url, headers, payload, resolved_config.timeout)


def stream_openrouter_chat(
    messages: Sequence[Mapping[str, str]],
    config: Optional[OpenRouterConfig] = None,
    model: Optional[str] = None,
) -> Iterator[str]:
    """Stream OpenRouter chat completions, yielding visible content text deltas.

    Parses the SSE response (``data: {...}`` lines, terminated by ``data: [DONE]``)
    and yields each ``choices[0].delta.content`` chunk. Reasoning-only deltas are
    skipped. Raises LLMRequestError on transport/HTTP errors.
    """
    resolved_config = config or resolve_openrouter_config()
    if model:
        resolved_config = replace(resolved_config, model=model)
    payload = build_openrouter_chat_payload(messages, config=resolved_config)
    payload["stream"] = True
    url = _join_url(resolved_config.base_url, OPENROUTER_CHAT_COMPLETIONS_PATH)
    headers = _build_headers(
        resolved_config.api_key,
        {
            "HTTP-Referer": resolved_config.http_referer,
            "X-OpenRouter-Title": resolved_config.app_title,
        },
    )
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=dict(headers), method="POST")

    try:
        response = urllib.request.urlopen(request, timeout=resolved_config.timeout)
    except urllib.error.HTTPError as exc:
        response_text = exc.read().decode("utf-8", errors="replace")
        raise LLMRequestError(f"LLM API HTTP {exc.code}: {response_text}") from exc
    except urllib.error.URLError as exc:
        raise LLMRequestError(f"LLM API request failed: {exc}") from exc

    with response:
        for raw_line in response:
            line = raw_line.decode("utf-8", errors="replace").strip()
            if not line or not line.startswith("data:"):
                continue
            data = line[len("data:"):].strip()
            if data == "[DONE]":
                break
            try:
                obj = json.loads(data)
            except json.JSONDecodeError:
                continue
            choices = obj.get("choices") or []
            if not choices or not isinstance(choices[0], Mapping):
                continue
            delta = choices[0].get("delta") or {}
            chunk = delta.get("content")
            if chunk:
                yield chunk


def embed_openrouter(
    texts: "str | Sequence[str]",
    model: Optional[str] = None,
    config: Optional[OpenRouterConfig] = None,
) -> list[list[float]]:
    """Return embedding vectors for ``texts`` via OpenRouter's /embeddings endpoint.

    OpenRouter exposes an OpenAI-compatible embeddings API; default model is
    ``baai/bge-m3`` (1024-dim, multilingual). Reuses OpenRouter config/headers.
    Raises LLMRequestError on transport/HTTP errors.
    """
    if isinstance(texts, str):
        texts = [texts]
    texts = list(texts)
    if not texts:
        return []

    resolved_config = config or resolve_openrouter_config()
    embed_model = model or _read_str_env(ENV_OPENROUTER_EMBED_MODEL, DEFAULT_OPENROUTER_EMBED_MODEL)
    url = _join_url(resolved_config.base_url, OPENROUTER_EMBEDDINGS_PATH)
    headers = _build_headers(
        resolved_config.api_key,
        {
            "HTTP-Referer": resolved_config.http_referer,
            "X-OpenRouter-Title": resolved_config.app_title,
        },
    )
    payload = {"model": embed_model, "input": texts}
    response = _post_json(url, headers, payload, resolved_config.timeout)

    data = response.get("data")
    if not isinstance(data, list) or len(data) != len(texts):
        raise LLMRequestError("embeddings response missing or mismatched data[]")
    ordered = sorted(data, key=lambda d: d.get("index", 0) if isinstance(d, Mapping) else 0)
    return [list(item.get("embedding", [])) for item in ordered]


def extract_openai_text(response: Mapping[str, Any]) -> str:
    """Extract text content from a raw OpenAI Responses API response."""
    output_text = response.get("output_text")
    if isinstance(output_text, str):
        return output_text

    parts: list[str] = []
    for output_item in response.get("output", []):
        if not isinstance(output_item, Mapping):
            continue
        for content_item in output_item.get("content", []):
            if not isinstance(content_item, Mapping):
                continue
            text = content_item.get("text")
            if isinstance(text, str):
                parts.append(text)

    return "\n".join(part for part in parts if part)


def extract_openrouter_text(response: Mapping[str, Any]) -> str:
    """Extract text content from a raw OpenRouter chat completion response."""
    choices = response.get("choices", [])
    if not isinstance(choices, Sequence) or not choices:
        return ""

    first_choice = choices[0]
    if not isinstance(first_choice, Mapping):
        return ""

    message = first_choice.get("message", {})
    if not isinstance(message, Mapping):
        return ""

    content = message.get("content", "")
    return content if isinstance(content, str) else ""


def _post_json(
    url: str,
    headers: Mapping[str, str],
    payload: Mapping[str, Any],
    timeout: float,
) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers=dict(headers),
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        response_text = exc.read().decode("utf-8", errors="replace")
        raise LLMRequestError(f"LLM API HTTP {exc.code}: {response_text}") from exc
    except urllib.error.URLError as exc:
        raise LLMRequestError(f"LLM API request failed: {exc}") from exc

    try:
        decoded = json.loads(response_body)
    except json.JSONDecodeError as exc:
        raise LLMRequestError(
            f"LLM API returned non-JSON response: {response_body[:200]}"
        ) from exc

    if not isinstance(decoded, dict):
        raise LLMRequestError("LLM API returned a non-object JSON response")

    return decoded


def _build_headers(
    api_key: str,
    extra_headers: Optional[Mapping[str, str]] = None,
) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {api_key or '<missing>'}",
        "Content-Type": "application/json",
    }

    for key, value in (extra_headers or {}).items():
        if value:
            headers[key] = value

    return headers


def _dry_run_result(
    provider: str,
    url: str,
    headers: Mapping[str, str],
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "ok": True,
        "dry_run": True,
        "provider": provider,
        "url": url,
        "headers": _redact_headers(headers),
        "payload": dict(payload),
    }


def _redact_headers(headers: Mapping[str, str]) -> dict[str, str]:
    redacted = dict(headers)
    if "Authorization" in redacted:
        redacted["Authorization"] = "Bearer <redacted>"
    return redacted


def _normalize_messages(
    messages: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    if not messages:
        raise ValueError("messages must not be empty")

    normalized: list[dict[str, str]] = []
    for message in messages:
        role = str(message.get("role", "")).strip()
        content = str(message.get("content", "")).strip()
        if not role or not content:
            raise ValueError("each message requires role and content")
        normalized.append({"role": role, "content": content})

    return normalized


def _resolve_base_url(env_name: str, default: str) -> str:
    base_url = _read_str_env(env_name, default).rstrip("/")
    parsed = urllib.parse.urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise LLMConfigError(f"{env_name} must be an absolute HTTP(S) URL")
    return base_url


def _join_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def _read_str_env(env_name: str, default: str) -> str:
    return os.getenv(env_name, "").strip() or default


def _read_csv_env(env_name: str, default: Sequence[str]) -> list[str]:
    raw_value = os.getenv(env_name, "").strip()
    if not raw_value:
        return list(default)

    values = [part.strip() for part in raw_value.split(",") if part.strip()]
    if not values:
        raise LLMConfigError(f"{env_name} must contain at least one model id")

    return values


def _read_int_env(env_name: str, default: int, minimum: int) -> int:
    raw_value = os.getenv(env_name, "").strip()
    if not raw_value:
        return default

    try:
        value = int(raw_value)
    except ValueError as exc:
        raise LLMConfigError(f"{env_name} must be an integer") from exc

    if value < minimum:
        raise LLMConfigError(f"{env_name} must be >= {minimum}")

    return value


def _read_float_env(env_name: str, default: float, minimum: float) -> float:
    raw_value = os.getenv(env_name, "").strip()
    if not raw_value:
        return default

    try:
        value = float(raw_value)
    except ValueError as exc:
        raise LLMConfigError(f"{env_name} must be a number") from exc

    if value < minimum:
        raise LLMConfigError(f"{env_name} must be >= {minimum}")

    return value
