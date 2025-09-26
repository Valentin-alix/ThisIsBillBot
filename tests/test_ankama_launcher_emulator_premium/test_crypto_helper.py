from unittest import TestCase
from unittest.mock import patch

from ankama_launcher_emulator_premium.decrypter import crypto_helper as crypto_module
from ankama_launcher_emulator_premium.decrypter.crypto_helper import CryptoHelper
from ankama_launcher_emulator_premium.interfaces.credentials import DecipheredApiKey
from ankama_launcher_emulator_premium.interfaces.local_storage import BotRecord
from ankama_launcher_emulator_premium.utils import bot_storage


def _api_key(login: str, key: str, account_id: int) -> DecipheredApiKey:
    return DecipheredApiKey(
        key=key,
        provider="ankama",
        refreshToken="refresh-token",
        isStayLoggedIn=True,
        accountId=account_id,
        login=login,
        certificate=None,
        refreshDate=0,
    )


class TestCryptoHelper(TestCase):
    def test_store_then_load_api_key_uses_central_bot_store(self) -> None:
        api_key = _api_key("user@example.com", "secured-key", 42)
        with patch.object(crypto_module.Device, "getUUID", return_value="uuid"):
            CryptoHelper.store_api_key("user@example.com", api_key)
            stored = CryptoHelper.getStoredApiKey("user@example.com")

        self.assertEqual(stored.apikey.key, "secured-key")
        self.assertTrue(bot_storage.BOTS_STORAGE_PATH.exists())

    def test_remove_bot_clears_only_auth_material(self) -> None:
        def seed_bot(record: BotRecord) -> None:
            record.password = "secret"

        with patch.object(crypto_module.Device, "getUUID", return_value="uuid"):
            bot_storage.BotStorageController().update_record(
                "user@example.com",
                seed_bot,
            )
            CryptoHelper.store_api_key(
                "user@example.com",
                _api_key("user@example.com", "secured-key", 42),
            )
            CryptoHelper.remove_bot("user@example.com")
            record = bot_storage.BotStorageController().get_record("user@example.com")

        self.assertIsNotNone(record)
        assert record is not None
        self.assertEqual(record.password, "secret")
        self.assertIsNone(record.encrypted_api_key)
