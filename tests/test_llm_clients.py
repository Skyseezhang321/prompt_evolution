import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.llm_clients import (
    DEFAULT_OPENAI_BASE_URL,
    DEFAULT_OPENROUTER_BASE_URL,
    ENV_OPENAI_API_KEY,
    ENV_OPENAI_BASE_URL,
    ENV_OPENAI_MODEL,
    ENV_OPENROUTER_API_KEY,
    ENV_OPENROUTER_APP_TITLE,
    ENV_OPENROUTER_HTTP_REFERER,
    ENV_OPENROUTER_MODEL,
    LLMConfigError,
    build_chat_messages,
    call_openai_response,
    call_openrouter_chat,
    extract_openai_text,
    extract_openrouter_text,
    load_dotenv,
)


class LLMClientsTests(unittest.TestCase):
    def test_dotenv_loads_llm_settings_without_overwriting_env(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dotenv = Path(tmpdir) / ".env"
            dotenv.write_text(
                f"{ENV_OPENAI_API_KEY}=from-file\n"
                f"{ENV_OPENAI_MODEL}=gpt-test\n",
                encoding="utf-8",
            )

            with patch.dict(
                os.environ,
                {ENV_OPENAI_API_KEY: "from-env"},
                clear=True,
            ):
                load_dotenv(dotenv)

                self.assertEqual(os.environ[ENV_OPENAI_API_KEY], "from-env")
                self.assertEqual(os.environ[ENV_OPENAI_MODEL], "gpt-test")

    def test_openai_dry_run_builds_responses_request(self):
        with patch.dict(
            os.environ,
            {
                ENV_OPENAI_API_KEY: "sk-test",
                ENV_OPENAI_MODEL: "gpt-test",
            },
            clear=True,
        ):
            result = call_openai_response(
                prompt="hello",
                instructions="answer briefly",
                dry_run=True,
            )

        self.assertTrue(result["dry_run"])
        self.assertEqual(result["provider"], "openai")
        self.assertEqual(result["url"], f"{DEFAULT_OPENAI_BASE_URL}/responses")
        self.assertEqual(result["headers"]["Authorization"], "Bearer <redacted>")
        self.assertEqual(result["payload"]["model"], "gpt-test")
        self.assertEqual(result["payload"]["input"], "hello")
        self.assertEqual(result["payload"]["instructions"], "answer briefly")

    def test_openrouter_dry_run_builds_chat_request_with_app_headers(self):
        with patch.dict(
            os.environ,
            {
                ENV_OPENROUTER_API_KEY: "sk-or-test",
                ENV_OPENROUTER_MODEL: "openai/gpt-test",
                ENV_OPENROUTER_HTTP_REFERER: "https://example.com",
                ENV_OPENROUTER_APP_TITLE: "Prompt Evolution",
            },
            clear=True,
        ):
            result = call_openrouter_chat(
                prompt="hello",
                system_prompt="answer briefly",
                dry_run=True,
            )

        self.assertTrue(result["dry_run"])
        self.assertEqual(result["provider"], "openrouter")
        self.assertEqual(
            result["url"],
            f"{DEFAULT_OPENROUTER_BASE_URL}/chat/completions",
        )
        self.assertEqual(result["headers"]["Authorization"], "Bearer <redacted>")
        self.assertEqual(result["headers"]["HTTP-Referer"], "https://example.com")
        self.assertEqual(result["headers"]["X-OpenRouter-Title"], "Prompt Evolution")
        self.assertEqual(result["payload"]["model"], "openai/gpt-test")
        self.assertEqual(result["payload"]["messages"][0]["role"], "system")
        self.assertEqual(result["payload"]["messages"][1]["role"], "user")

    def test_build_chat_messages_requires_non_empty_prompt(self):
        with self.assertRaises(ValueError):
            build_chat_messages("  ")

    def test_live_openai_call_requires_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(LLMConfigError):
                call_openai_response("hello")

    def test_live_openrouter_call_requires_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(LLMConfigError):
                call_openrouter_chat(prompt="hello")

    def test_invalid_base_url_is_rejected(self):
        with patch.dict(
            os.environ,
            {
                ENV_OPENAI_API_KEY: "sk-test",
                ENV_OPENAI_BASE_URL: "not-a-url",
            },
            clear=True,
        ):
            with self.assertRaises(LLMConfigError):
                call_openai_response("hello")

    def test_extracts_openai_response_text(self):
        response = {
            "output": [
                {
                    "content": [
                        {
                            "type": "output_text",
                            "text": "配置正常",
                        }
                    ]
                }
            ]
        }

        self.assertEqual(extract_openai_text(response), "配置正常")

    def test_extracts_openrouter_chat_text(self):
        response = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "配置正常",
                    }
                }
            ]
        }

        self.assertEqual(extract_openrouter_text(response), "配置正常")


if __name__ == "__main__":
    unittest.main()
