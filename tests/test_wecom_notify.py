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
    compose_repository_message,
    format_git_change_summary,
    load_dotenv,
    notifications_enabled,
    resolve_webhook,
    send_repository_notification,
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

    def test_formats_worktree_change_summary(self):
        summary = format_git_change_summary(
            status_output=" M README.md\n?? scripts/wecom_notify.py\n",
            diff_stat_output=" README.md | 3 +++\n 1 file changed, 3 insertions(+)",
        )

        self.assertIn("### 主要修改内容", summary)
        self.assertIn("企业微信通知", summary)
        self.assertIn("文档说明", summary)
        self.assertIn("工作区变更：2 个", summary)
        self.assertIn("` M README.md`", summary)
        self.assertIn("`?? scripts/wecom_notify.py`", summary)

    def test_formats_clean_repo_last_commit_summary(self):
        summary = format_git_change_summary(
            status_output="",
            last_commit_output="abc1234 update notification",
            last_commit_stat_output=" scripts/wecom_notify.py | 12 ++++++++++++\n",
            last_commit_files_output="M\tscripts/wecom_notify.py\n",
        )

        self.assertIn("### 主要修改内容", summary)
        self.assertIn("企业微信通知", summary)
        self.assertIn("最近提交：`abc1234 update notification`", summary)
        self.assertIn("`M\tscripts/wecom_notify.py`", summary)

    def test_compose_repository_message_can_skip_git_summary(self):
        message = compose_repository_message("hello", include_git_summary=False)

        self.assertEqual(message, "hello")

    def test_repository_dry_run_includes_supplied_git_summary(self):
        result = send_repository_notification(
            "hello",
            webhook="https://example.com/webhook",
            dry_run=True,
            repo=Path.cwd(),
            max_git_lines=1,
        )

        content = result["payload"]["markdown"]["content"]
        self.assertTrue(content.startswith("hello"))
        self.assertIn("### 主要修改内容", content)


if __name__ == "__main__":
    unittest.main()
