import logging
from collections.abc import Callable

from base_python.singleton import Singleton
from filelock import FileLock

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.consts import BOTS_STORAGE_PATH
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.mail_account import (
    MailAccountController,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.decrypter.hardware_identity import (
    generate_hardware_id,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.local_storage import (
    BotRecord,
    BotsFile,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.zaap_files import UserAccount
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.utils.atomic_file import (
    acquire_file_lock,
    atomic_write_text,
)

logger = logging.getLogger(__name__)


class BotStorageController(metaclass=Singleton):
    _FILE_LOCK_TIMEOUT_SECONDS = 20.0

    def _load(self) -> BotsFile:
        if not BOTS_STORAGE_PATH.exists():
            return BotsFile()
        return BotsFile.model_validate_json(BOTS_STORAGE_PATH.read_text(encoding="utf-8"))

    def _save(self, bots_file: BotsFile) -> None:
        atomic_write_text(BOTS_STORAGE_PATH, bots_file.model_dump_json(indent=2))

    def _acquire_file_lock(self) -> FileLock:
        return acquire_file_lock(BOTS_STORAGE_PATH, timeout_seconds=self._FILE_LOCK_TIMEOUT_SECONDS)

    def get_record(self, login: str) -> BotRecord | None:
        return self._load().bots.get(login)

    def get_all_records(self) -> dict[str, BotRecord]:
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
            bots_file.bots.pop(login, None)
            self._save(bots_file)

    def upsert_account_info(self, account: UserAccount) -> None:
        self.update_record(
            account.login,
            lambda record: setattr(record, "account_info", account),
        )

    def get_generated_account_records(self) -> list[BotRecord]:
        return list(self.get_all_records().values())

    def get_accounts_needing_auth(self) -> list[BotRecord]:
        """Accounts with saved credentials but no live API key yet (excludes bad-state)."""
        bad_state_emails = MailAccountController().load_bad_state_emails()
        return [
            record
            for record in self.get_all_records().values()
            if record.encrypted_api_key is None and record.email not in bad_state_emails
        ]

    def reassign_schedule_profile(self, login: str, schedule_profile: str) -> None:
        self.update_record(
            login,
            lambda record: setattr(record, "schedule_profile", schedule_profile),
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
