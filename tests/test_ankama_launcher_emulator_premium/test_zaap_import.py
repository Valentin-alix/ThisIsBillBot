import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller import bot_storage, zaap_import
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.decrypter import crypto_helper as crypto_module
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.decrypter.crypto_helper import CryptoHelper
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.credentials import DecipheredApiKey

_UUID = "uuid"


def _write_zaap_files(zaap_path: Path, login: str, account_id: int) -> None:
    settings: dict[str, list[dict[str, Any]]] = {
        "USER_ACCOUNTS": [
            {
                "login": login,
                "nickname": "nick",
                "id": account_id,
                "type": "ANKAMA",
                "firstname": "f",
                "lastname": "l",
                "tag": "0001",
                "security": [],
                "locked": "0",
                "gameList": [],
            }
        ]
    }
    zaap_path.mkdir()
    (zaap_path / "Settings").write_text(json.dumps(settings), encoding="utf-8")

    keydata_dir = zaap_path / "keydata"
    keydata_dir.mkdir()
    api_key = DecipheredApiKey(
        key="secured-key",
        provider="ankama",
        refreshToken="refresh-token",
        isStayLoggedIn=True,
        accountId=account_id,
        login=login,
        certificate=None,
        refreshDate=0,
    )
    encrypted = CryptoHelper.encrypt(api_key, _UUID)
    (keydata_dir / f".keydata{account_id}").write_text(encrypted, encoding="utf-8")


def test_imports_account_with_matching_user_account_and_api_key(tmp_path: Path) -> None:
    zaap_path = tmp_path / "zaap"
    with patch.object(crypto_module.Device, "getUUID", return_value=_UUID):
        _write_zaap_files(zaap_path, "user@example.com", 42)
        with patch.object(zaap_import, "ZAAP_PATH", zaap_path):
            zaap_import.import_zaap_accounts()

        record = bot_storage.BotStorageController().get_record("user@example.com")

    assert record is not None
    assert record.password is None
    assert record.account_info is not None
    assert record.account_info.nickname == "nick"
    assert record.encrypted_api_key is not None
    decrypted = CryptoHelper.decrypt(record.encrypted_api_key, _UUID)
    assert DecipheredApiKey.model_validate_json(decrypted).login == "user@example.com"


def test_skips_keydata_without_matching_user_account(tmp_path: Path) -> None:
    zaap_path = tmp_path / "zaap"
    with patch.object(crypto_module.Device, "getUUID", return_value=_UUID):
        _write_zaap_files(zaap_path, "user@example.com", 42)
        (zaap_path / "Settings").write_text(json.dumps({"USER_ACCOUNTS": []}), encoding="utf-8")
        with patch.object(zaap_import, "ZAAP_PATH", zaap_path):
            zaap_import.import_zaap_accounts()

        record = bot_storage.BotStorageController().get_record("user@example.com")

    assert record is None


def test_missing_zaap_directory_is_a_noop(tmp_path: Path) -> None:
    with patch.object(zaap_import, "ZAAP_PATH", tmp_path / "does-not-exist"):
        zaap_import.import_zaap_accounts()
