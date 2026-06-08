import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.wecom_notify import (
    ENV_ENABLED,
    ENV_WEBHOOK,
    NotificationError,
    build_payload,
    load_dotenv,
    notifications_enabled,
    resolve_webhook,
    send_wecom_notification,
)


class WeComNotifyTests(unittest.TestCase):
    def test_builds_markdown_payload(self):
        payload = build_payload("### 标题\n- 内容")

        self.assertEqual(payload["msgtype"], "markdown")
        self.assertEqual(payload["markdown"]["content"], "### 标题\n- 内容")

    def test_builds_text_payload_with_mentions(self):
        payload = build_payload(
            "需要处理",
            msgtype="text",
            mentioned_list=["@all"],
            mentioned_mobile_list=["13800138000"],
        )

        self.assertEqual(payload["msgtype"], "text")
        self.assertEqual(payload["text"]["mentioned_list"], ["@all"])
        self.assertEqual(payload["text"]["mentioned_mobile_list"], ["13800138000"])

    def test_rejects_empty_content(self):
        with self.assertRaises(ValueError):
            build_payload("  ")

    def test_rejects_unknown_message_type(self):
        with self.assertRaises(ValueError):
            build_payload("hello", msgtype="image")

    def test_dotenv_loads_without_overwriting_existing_env(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dotenv = Path(tmpdir) / ".env"
            dotenv.write_text(
                f"{ENV_WEBHOOK}=https://example.com/from-file\n"
                f"{ENV_ENABLED}=false\n",
                encoding="utf-8",
            )

            with patch.dict(
                os.environ,
                {ENV_WEBHOOK: "https://example.com/from-env"},
                clear=True,
            ):
                load_dotenv(dotenv)

                self.assertEqual(os.environ[ENV_WEBHOOK], "https://example.com/from-env")
                self.assertEqual(os.environ[ENV_ENABLED], "false")

    def test_notifications_can_be_disabled(self):
        with patch.dict(os.environ, {ENV_ENABLED: "off"}, clear=True):
            self.assertFalse(notifications_enabled())

    def test_resolve_webhook_requires_url(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(NotificationError):
                resolve_webhook()

    def test_dry_run_does_not_send_network_request(self):
        result = send_wecom_notification(
            "hello",
            webhook="https://example.com/webhook",
            dry_run=True,
        )

        self.assertTrue(result["dry_run"])
        self.assertEqual(result["payload"]["markdown"]["content"], "hello")


if __name__ == "__main__":
    unittest.main()
