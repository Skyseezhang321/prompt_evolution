import unittest
from pathlib import Path
from unittest import mock

import scripts.git_wecom_notify as git_wecom_notify
from scripts.git_wecom_notify import (
    ZERO_SHA,
    build_push_notification,
    parse_push_updates,
)


class GitWeComNotifyTests(unittest.TestCase):
    def test_parse_push_updates_ignores_invalid_lines(self):
        updates = parse_push_updates(
            [
                "refs/heads/main abc123 refs/heads/main def456",
                "invalid",
            ]
        )

        self.assertEqual(len(updates), 1)
        self.assertEqual(updates[0].local_ref, "refs/heads/main")
        self.assertEqual(updates[0].local_sha, "abc123")
        self.assertEqual(updates[0].remote_ref, "refs/heads/main")

    def test_push_update_detects_delete(self):
        updates = parse_push_updates(
            [f"refs/heads/main {ZERO_SHA} refs/heads/main abc123"]
        )

        self.assertTrue(updates[0].is_delete)

    def test_build_push_notification_redacts_credentials(self):
        updates = parse_push_updates(
            [
                "refs/heads/main "
                "0123456789abcdef0123456789abcdef01234567 "
                "refs/heads/main "
                "abcdefabcdefabcdefabcdefabcdefabcdefabcd"
            ]
        )

        content = build_push_notification(
            repo_name="prompt_evolution",
            remote="origin",
            remote_url="https://user:token@example.com/repo.git",
            updates=updates,
        )

        self.assertIn("Prompt Evolution push completed", content)
        self.assertIn("main: `0123456789ab`", content)
        self.assertIn("https://example.com/repo.git", content)
        self.assertNotIn("token", content)

    def test_git_decodes_output_as_utf8(self):
        with mock.patch.object(git_wecom_notify.subprocess, "run") as run:
            run.return_value = mock.Mock(stdout="中文提交\n")
            output = git_wecom_notify._git("show", "-s")

        self.assertEqual(output, "中文提交\n")
        self.assertEqual(run.call_args.kwargs["encoding"], "utf-8")
        self.assertEqual(run.call_args.kwargs["errors"], "replace")

    def test_git_returns_empty_string_when_stdout_is_none(self):
        with mock.patch.object(git_wecom_notify.subprocess, "run") as run:
            run.return_value = mock.Mock(stdout=None)
            output = git_wecom_notify._git("show", "-s")

        self.assertEqual(output, "")

    def test_send_commit_notification_degrades_when_commit_info_unreadable(self):
        with (
            mock.patch.object(git_wecom_notify, "repo_root", return_value=Path("repo")),
            mock.patch.object(git_wecom_notify, "load_dotenv"),
            mock.patch.object(git_wecom_notify, "_current_branch", return_value="main"),
            mock.patch.object(git_wecom_notify, "_git", return_value=""),
            mock.patch.object(
                git_wecom_notify, "send_repository_notification", return_value={"ok": True}
            ) as send,
        ):
            result = git_wecom_notify.send_commit_notification(dry_run=True)

        self.assertEqual(result, {"ok": True})
        content = send.call_args.args[0]
        self.assertIn("已降级为简化通知", content)
        self.assertIn("- branch: main", content)


if __name__ == "__main__":
    unittest.main()
