import logging

from ankama_launcher_emulator_premium.consts import BOTS_STORAGE_PATH
from ankama_launcher_emulator_premium.interfaces.local_storage import (
    BotRecord,
    GeneratedAccountEntry,
    GeneratedAccountsFile,
)
from ankama_launcher_emulator_premium.utils.bot_storage import BotStorageController

logger = logging.getLogger(__name__)


def load_generated_accounts() -> GeneratedAccountsFile:
    return GeneratedAccountsFile(
        root=[
            GeneratedAccountEntry(
                email=record.email,
                password=record.password,
                available=record.available,
                schedule_profile=record.schedule_profile,
            )
            for record in BotStorageController().get_all_records().values()
            if record.password is not None
        ]
    )


def load_available_generated_accounts() -> list[GeneratedAccountEntry]:
    accounts = load_generated_accounts()
    return [acc for acc in accounts.root if acc.available]


def load_bad_state_emails() -> set[str]:
    return {login for login, record in BotStorageController().get_all_records().items() if record.bad_state}


def record_bad_state_email(email: str) -> None:
    storage = BotStorageController()
    existing_record = storage.get_record(email)
    was_present = existing_record is not None and existing_record.bad_state
    storage.update_record(email, lambda record: setattr(record, "bad_state", True))
    if not was_present:
        logger.warning("[Auth] Recorded bad-state email %s", email)


def mark_account_authenticated(email: str) -> None:
    BotStorageController().update_record(
        email,
        lambda record: setattr(record, "available", False),
    )


def mark_account_available_for_auth_retry(email: str) -> None:
    BotStorageController().update_record(
        email,
        lambda record: setattr(record, "available", True),
    )


def reassign_account_for_auth_retry(email: str, schedule_profile: str) -> None:
    def reassign(record: BotRecord) -> None:
        record.available = True
        record.schedule_profile = schedule_profile

    BotStorageController().update_record(email, reassign)


def remove_generated_account(email: str) -> None:
    # when account is banned for example
    BotStorageController().remove_record(email)


def save_account(
    email: str,
    password: str,
    schedule_profile: str | None = None,
) -> None:
    def save(record: BotRecord) -> None:
        record.password = password
        record.available = True
        record.schedule_profile = schedule_profile

    BotStorageController().update_record(email, save)
    logger.info("[Register] Account saved to %s", BOTS_STORAGE_PATH)


if __name__ == "__main__":
    load_generated_accounts()
