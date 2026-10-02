import json
import logging
from typing import Any

from pydantic import ValidationError

from ankama_launcher_emulator.consts import ZAAP_PATH
from ankama_launcher_emulator.controller.bot_storage import (
    BotStorageController,
)
from ankama_launcher_emulator.decrypter.crypto_helper import (
    CryptoHelper,
)
from ankama_launcher_emulator.decrypter.device import Device
from ankama_launcher_emulator.decrypter.hardware_identity import (
    generate_hardware_id,
)
from ankama_launcher_emulator.interfaces.credentials import (
    DecipheredApiKey,
)
from ankama_launcher_emulator.interfaces.local_storage import BotRecord
from ankama_launcher_emulator.interfaces.zaap_files import UserAccount

logger = logging.getLogger(__name__)


def _load_user_accounts() -> dict[int, UserAccount]:
    settings_path = ZAAP_PATH / "Settings"
    if not settings_path.exists():
        return {}
    settings: dict[str, Any] = json.loads(settings_path.read_text(encoding="utf-8"))
    accounts: dict[int, UserAccount] = {}
    for entry in settings.get("USER_ACCOUNTS", []):
        try:
            account = UserAccount.model_validate(entry)
        except ValidationError:
            logger.warning("Skipping unparsable zaap USER_ACCOUNTS entry", exc_info=True)
            continue
        accounts[account.id] = account
    return accounts


def import_zaap_accounts() -> None:
    keydata_dir = ZAAP_PATH / "keydata"
    if not keydata_dir.exists():
        return

    user_accounts_by_id = _load_user_accounts()
    uuid = Device.getUUID()
    storage = BotStorageController()

    for keydata_file in keydata_dir.iterdir():
        if not keydata_file.name.startswith(".key"):
            continue
        raw = keydata_file.read_text(encoding="utf-8")
        try:
            deciphered = DecipheredApiKey.model_validate_json(CryptoHelper.decrypt(raw, uuid))
        except (ValueError, IndexError):
            logger.warning("Failed to decrypt zaap keydata file %s", keydata_file.name, exc_info=True)
            continue

        user_account = user_accounts_by_id.get(deciphered.accountId)
        if user_account is None:
            logger.warning(
                "No matching USER_ACCOUNTS entry for zaap account id %s (login %s)",
                deciphered.accountId,
                deciphered.login,
            )
            continue

        def update(record: BotRecord, raw=raw, user_account=user_account) -> None:
            record.encrypted_api_key = raw
            record.account_info = user_account

        storage.upsert_record(
            deciphered.login,
            create=lambda raw=raw, user_account=user_account, login=deciphered.login: BotRecord(
                email=login,
                hardware_id=generate_hardware_id(),
                encrypted_api_key=raw,
                account_info=user_account,
            ),
            update=update,
        )
        logger.info("Imported zaap account %s", deciphered.login)
