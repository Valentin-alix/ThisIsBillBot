from time import time
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ankama_launcher_emulator_premium.haapi.haapi import (
    API_KEY_REFRESH_INTERVAL_MS,
    Haapi,
)
from ankama_launcher_emulator_premium.interfaces.credentials import (
    DecipheredApiKey,
    StoredApiKey,
)


def _stored_api_key(refresh_date: int) -> StoredApiKey:
    return StoredApiKey(
        apikey=DecipheredApiKey(
            key="api-key",
            provider="ankama",
            refreshToken="old-refresh-token",
            isStayLoggedIn=True,
            accountId=42,
            login="user@example.com",
            refreshDate=refresh_date,
        )
    )


class TestHaapiRefreshApiKey(TestCase):
    def setUp(self) -> None:
        self.haapi = Haapi(api_key="api-key", login="user@example.com")
        self.session = MagicMock()
        self.haapi.zaap_session = self.session

    def test_skips_refresh_while_within_the_launcher_window(self) -> None:
        now_ms = int(time() * 1000)
        stored = _stored_api_key(now_ms - API_KEY_REFRESH_INTERVAL_MS + 60_000)

        with (
            patch(
                "ankama_launcher_emulator_premium.haapi.haapi.CryptoHelper.getStoredApiKey",
                return_value=stored,
            ),
            patch("ankama_launcher_emulator_premium.haapi.haapi.CryptoHelper.store_api_key") as store_mock,
        ):
            self.haapi.refresh_api_key()

        self.session.post.assert_not_called()
        store_mock.assert_not_called()

    def test_refreshes_and_persists_once_the_window_elapsed(self) -> None:
        now_ms = int(time() * 1000)
        stored = _stored_api_key(now_ms - API_KEY_REFRESH_INTERVAL_MS - 60_000)
        self.session.post.return_value.json.return_value = {
            "key": "rotated-key",
            "account_id": 42,
            "refresh_token": "new-refresh-token",
        }

        with (
            patch(
                "ankama_launcher_emulator_premium.haapi.haapi.CryptoHelper.getStoredApiKey",
                return_value=stored,
            ),
            patch("ankama_launcher_emulator_premium.haapi.haapi.CryptoHelper.store_api_key") as store_mock,
        ):
            self.haapi.refresh_api_key()

        _, kwargs = self.session.post.call_args
        self.assertEqual(
            kwargs["data"],
            {
                "refresh_token": "old-refresh-token",
                "long_life_token": "true",
                "shop_key": "ZAAP",
                "payment_mode": "OK",
                "lang": "fr",
            },
        )
        # The launcher only keeps the rotated refresh token, never the new key.
        self.assertEqual(stored.apikey.key, "api-key")
        self.assertEqual(stored.apikey.refreshToken, "new-refresh-token")
        self.assertGreaterEqual(stored.apikey.refreshDate, now_ms)
        store_mock.assert_called_once_with("user@example.com", stored.apikey)
