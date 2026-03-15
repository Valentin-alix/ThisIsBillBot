from utils.local_json import read_local_model
import logging
from datetime import datetime, timezone
from collections.abc import Callable

from utils.singleton import Singleton
from filelock import FileLock

from ankama_launcher_emulator.consts import BOTS_STORAGE_PATH
from ankama_launcher_emulator.controller.mail_account import (
    MailAccountController,
)
from ankama_launcher_emulator.decrypter.hardware_identity import (
    generate_hardware_id,
)
from ankama_launcher_emulator.interfaces.local_storage import (
    BotRecord,
    BotsFile,
)
from ankama_launcher_emulator.interfaces.zaap_files import UserAccount
from ankama_launcher_emulator.quarantine_signals import (
    quarantine_signals,
)
from ankama_launcher_emulator.utils.atomic_file import (
    acquire_file_lock,
    atomic_write_text,
)

logger = logging.getLogger(__name__)


class BotStorageController(metaclass=Singleton):
    _FILE_LOCK_TIMEOUT_SECONDS = 20.0

    def _load(self) -> BotsFile:
        if not BOTS_STORAGE_PATH.exists():
            return BotsFile()
        return read_local_model(BOTS_STORAGE_PATH, BotsFile)

    def _save(self, bots_file: BotsFile) -> None:
        atomic_write_text(BOTS_STORAGE_PATH, bots_file.model_dump_json(indent=2))

    def _acquire_file_lock(self) -> FileLock:
        return acquire_file_lock(BOTS_STORAGE_PATH, timeout_seconds=self._FILE_LOCK_TIMEOUT_SECONDS)

    def get_record(self, login: str) -> BotRecord | None:
        with self._acquire_file_lock():
            return self._load().bots.get(login)

    def get_all_records(self) -> dict[str, BotRecord]:
        with self._acquire_file_lock():
            return self._load().bots

    def update_record(
        self,
        login: str,
        update: Callable[[BotRecord], None],
    ) -> BotRecord:
        with self._acquire_file_lock():
            bots_file = self._load()
            record = bots_file.bots.get(login)
            if record is None:
                raise LookupError(f"No BotRecord for {login}; register the account first")
            update(record)
            bots_file.bots[login] = record
            self._save(bots_file)
            return record

    def upsert_record(
        self,
        login: str,
        create: Callable[[], BotRecord],
        update: Callable[[BotRecord], None],
    ) -> BotRecord:
        with self._acquire_file_lock():
            bots_file = self._load()
            record = bots_file.bots.get(login)
            if record is None:
                record = create()
            else:
                update(record)
            bots_file.bots[login] = record
            self._save(bots_file)
            return record

    def update_records(
        self,
        update: Callable[[dict[str, BotRecord]], None],
    ) -> None:
        with self._acquire_file_lock():
            bots_file = self._load()
            update(bots_file.bots)
            self._save(bots_file)

    def remove_record(self, login: str) -> None:
        with self._acquire_file_lock():
            bots_file = self._load()
            removed = bots_file.bots.pop(login, None)
            self._save(bots_file)
        if removed is not None:
            quarantine_signals.changed.emit()

    def upsert_account_info(self, login: str, account: UserAccount) -> None:
        self.update_record(
            login,
            lambda record: setattr(record, "account_info", account),
        )

    def get_generated_account_records(self) -> list[BotRecord]:
        return list(self.get_all_records().values())

    def get_accounts_needing_auth(self) -> list[BotRecord]:
        bad_state_emails = MailAccountController().load_bad_state_emails()
        return [
            record
            for record in self.get_all_records().values()
            if record.encrypted_api_key is None
            and record.quarantine_reason is None
            and record.email not in bad_state_emails
        ]

    def quarantine(self, login: str, reason: str) -> BotRecord:
        def mark_quarantined(record: BotRecord) -> None:
            record.quarantine_reason = reason
            record.quarantined_at = datetime.now(timezone.utc)

        record = self.update_record(
            login,
            mark_quarantined,
        )
        quarantine_signals.changed.emit()
        return record

    def restore_from_quarantine(self, login: str) -> BotRecord:
        def restore(record: BotRecord) -> None:
            record.quarantine_reason = None
            record.quarantined_at = None

        record = self.update_record(
            login,
            restore,
        )
        quarantine_signals.changed.emit()
        return record

    def clear_api_key(self, login: str) -> BotRecord:
        return self.update_record(login, lambda record: setattr(record, "encrypted_api_key", None))

    def reassign_schedule_profile(self, login: str, schedule_profile: str) -> None:
        def reassign(record: BotRecord) -> None:
            if record.schedule_profile == schedule_profile:
                return
            record.schedule_profile = schedule_profile
            record.encrypted_api_key = None

        self.update_record(login, reassign)

    def reassign_quarantined_schedule_profile(self, login: str, schedule_profile: str) -> None:
        def reassign(record: BotRecord) -> None:
            if record.schedule_profile == schedule_profile:
                return
            record.quarantined_schedule_profile = record.schedule_profile
            record.schedule_profile = schedule_profile
            record.encrypted_api_key = None

        self.update_record(login, reassign)

    def clear_quarantined_schedule_profile(self, login: str) -> None:
        self.update_record(
            login,
            lambda record: setattr(record, "quarantined_schedule_profile", None),
        )

    def save_account(
        self,
        email: str,
        password: str,
        schedule_profile: str | None = None,
    ) -> None:
        def update(record: BotRecord) -> None:
            record.password = password
            record.schedule_profile = schedule_profile

        self.upsert_record(
            email,
            create=lambda: BotRecord(
                email=email,
                password=password,
                hardware_id=generate_hardware_id(),
                schedule_profile=schedule_profile,
            ),
            update=update,
        )
        logger.info("[Register] Account saved to %s", BOTS_STORAGE_PATH)
