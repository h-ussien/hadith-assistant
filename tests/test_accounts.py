import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import accounts, auth, data


class TestAccounts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.patcher = patch.object(data, "DB", Path(self.temp.name) / "test.db")
        self.patcher.start()
        data.initialize()
        data.initialize_books()
        auth.initialize()
        accounts.initialize()

    def tearDown(self):
        self.patcher.stop()
        self.temp.cleanup()

    def test_first_account_is_admin_and_later_accounts_are_users(self):
        self.assertFalse(accounts.has_admin())
        first = accounts.register("admin1", "a-strong-password", "admin1@example.com")
        second = accounts.register("student1", "another-password", "student1@example.com")
        self.assertTrue(accounts.has_admin())
        self.assertEqual(first["role"], "admin")
        self.assertEqual(second["role"], "user")
        self.assertEqual([u["username"] for u in accounts.list_accounts()], ["admin1", "student1"])

    def test_login_by_username_or_email_and_logout(self):
        accounts.register("admin1", "a-strong-password", "admin1@example.com")
        accounts.register("scholar", "reading-1234", "scholar@example.com")
        token, user = accounts.login("Scholar", "reading-1234")
        self.assertEqual(user["username"], "scholar")
        self.assertFalse(user["admin"])
        self.assertEqual(accounts.identity(token), user)

        token_by_email, by_email = accounts.login("SCHOLAR@EXAMPLE.COM", "reading-1234")
        self.assertEqual(by_email["username"], "scholar")
        self.assertEqual(accounts.identity(token_by_email), by_email)

        accounts.logout("scholar")
        self.assertIsNone(accounts.identity(token))
        self.assertIsNone(accounts.identity(token_by_email))
        self.assertIsNone(accounts.login("scholar", "wrong-password"))

    def test_duplicate_username_email_and_weak_password_rejected(self):
        accounts.register("reader", "long-enough-pass", "reader@example.com")
        with self.assertRaises(ValueError):
            accounts.register("reader", "another-long-password", "other@example.com")
        with self.assertRaises(ValueError):
            accounts.register("second", "another-long-password", "READER@example.com")
        with self.assertRaises(ValueError):
            accounts.register("short", "tiny", "short@example.com")
        with self.assertRaises(ValueError):
            accounts.register("bademail", "long-enough-pass", "not-an-email")

    def test_legacy_admin_password_is_migrated(self):
        auth.setup("the-original-admin-password")
        accounts.initialize()
        token, user = accounts.login("admin", "the-original-admin-password")
        self.assertTrue(user["admin"])
        self.assertEqual(user["username"], "admin")
        self.assertEqual(user["email"], "admin@localhost.local")
        self.assertEqual(accounts.identity(token), user)

    def test_google_account_is_unique_and_not_admin(self):
        token, user = accounts.google_login(
            "Aisha@example.com", "Aisha Salah", "google-sub-123"
        )
        self.assertEqual(user["username"], "aisha")
        self.assertEqual(user["email"], "aisha@example.com")
        self.assertEqual(user["provider"], "google")
        self.assertFalse(user["admin"])
        self.assertEqual(accounts.identity(token), user)

        _, again = accounts.google_login(
            "aisha@example.com", "Aisha Salah", "google-sub-123"
        )
        self.assertEqual(again["username"], "aisha")
        listed = accounts.list_accounts()
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0]["google_sub"], "google-sub-123")

    def test_google_login_cannot_claim_admin_email(self):
        accounts.register("admin1", "a-strong-password", "admin1@example.com")
        with self.assertRaises(ValueError):
            accounts.google_login(
                "admin1@example.com", "Admin Impersonator", "google-sub-999"
            )
        listed = accounts.list_accounts()
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0]["provider"], "local")
        self.assertEqual(listed[0]["role"], "admin")

    def test_search_history_is_per_account(self):
        accounts.register("admin1", "a-strong-password", "admin1@example.com")
        accounts.register("reader", "reading-pass", "reader@example.com")
        accounts.record_history("reader", "الدين النصيحة", "shamela", 3)
        accounts.record_history("admin1", "إنما الأعمال بالنيات", "hadith", 2)
        reader_history = accounts.history("reader")
        self.assertEqual(len(reader_history), 1)
        self.assertEqual(reader_history[0]["query"], "الدين النصيحة")
        accounts.clear_history("reader")
        self.assertEqual(accounts.history("reader"), [])
        self.assertEqual(len(accounts.history("admin1")), 1)


if __name__ == "__main__":
    unittest.main()
