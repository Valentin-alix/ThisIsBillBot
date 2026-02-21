from time import time
from unittest.mock import MagicMock, patch

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.bot_storage import (
    BotStorageController,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.decrypter.crypto_helper import (
    CryptoHelper,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.haapi.haapi import (
    API_KEY_REFRESH_INTERVAL_MS,
    Haapi,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.credentials import (
    DecipheredApiKey,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.local_storage import (
    BotRecord,
)
from tests.fixtures.launcher import IsolatedLauncherStorageTestCase

_LOGIN = "user@example.com"
_FAKE_UUID = "fake-device-uuid"


def _seed_stored_api_key(refresh_date: int) -> DecipheredApiKey:
    api_key = DecipheredApiKey(
        key="api-key",
        provider="ankama",
        refreshToken="old-refresh-token",
        isStayLoggedIn=True,
        accountId=42,
        login=_LOGIN,
        refreshDate=refresh_date,
    )
    encrypted_api_key = CryptoHelper.encrypt(api_key, _FAKE_UUID)
    BotStorageController().upsert_record(
        _LOGIN,
        create=lambda: BotRecord(
            email=_LOGIN,
            password="pwd",
            hardware_id="hw",
            encrypted_api_key=encrypted_api_key,
        ),
        update=lambda record: setattr(record, "encrypted_api_key", encrypted_api_key),
    )
    return api_key


class TestHaapiRefreshApiKey(IsolatedLauncherStorageTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.haapi = Haapi(api_key="api-key", login=_LOGIN)
        self.session = MagicMock()
        self.haapi.zaap_session = self.session
        self._device_uuid_patch = patch(
            "AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.haapi.haapi.Device.getUUID",
            return_value=_FAKE_UUID,
        )
        self._device_uuid_patch.start()
        self.addCleanup(self._device_uuid_patch.stop)

    def test_skips_refresh_while_within_the_launcher_window(self) -> None:
        now_ms = int(time() * 1000)
        _seed_stored_api_key(now_ms - API_KEY_REFRESH_INTERVAL_MS + 60_000)

        self.haapi.refresh_api_key()

        self.session.post.assert_not_called()

    def test_refreshes_and_persists_once_the_window_elapsed(self) -> None:
        now_ms = int(time() * 1000)
        _seed_stored_api_key(now_ms - API_KEY_REFRESH_INTERVAL_MS - 60_000)
        self.session.post.return_value.json.return_value = {
            "key": "rotated-key",
            "account_id": 42,
            "refresh_token": "new-refresh-token",
        }

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
        stored = CryptoHelper.getStoredApiKey(_LOGIN)
        # The launcher only keeps the rotated refresh token, never the new key.
        self.assertEqual(stored.apikey.key, "api-key")
        self.assertEqual(stored.apikey.refreshToken, "new-refresh-token")
        self.assertGreaterEqual(stored.apikey.refreshDate, now_ms)

    def test_second_refresh_after_a_fresh_write_is_a_noop(self) -> None:
        """Guards the read-decide-write atomicity fixed for the TOCTOU race.

        Read, decide, and write now happen inside a single ``update_record`` call
        (one file-lock acquisition), so a refresh that lands right after another one
        just wrote a fresh token must see that fresh ``refreshDate`` and skip instead
        of racing on a stale in-memory read.
        """
        now_ms = int(time() * 1000)
        _seed_stored_api_key(now_ms - API_KEY_REFRESH_INTERVAL_MS - 60_000)
        self.session.post.return_value.json.return_value = {
            "key": "rotated-key",
            "account_id": 42,
            "refresh_token": "new-refresh-token",
        }

        self.haapi.refresh_api_key()
        self.haapi.refresh_api_key()

        self.session.post.assert_called_once()
        stored = CryptoHelper.getStoredApiKey(_LOGIN)
        self.assertEqual(stored.apikey.refreshToken, "new-refresh-token")
