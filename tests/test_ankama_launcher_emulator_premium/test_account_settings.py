from unittest import TestCase

from ankama_launcher_emulator_premium.utils import account_settings


class TestAccountSettings(TestCase):
    def test_load_account_settings_returns_none_when_bot_missing(self) -> None:
        settings = account_settings.load_account_settings("missing@example.com")

        self.assertIsNone(settings.proxy_url)

    def test_save_then_load_account_settings_round_trip(self) -> None:
        account_settings.save_account_settings(
            "user@example.com",
            "socks5://user:pass@127.0.0.1:1080",
        )
        settings = account_settings.load_account_settings("user@example.com")

        self.assertEqual(
            settings.proxy_url,
            "socks5://user:pass@127.0.0.1:1080",
        )
