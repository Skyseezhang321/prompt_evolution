import unittest

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


if __name__ == "__main__":
    unittest.main()
