from collections.abc import Callable

from base_python.singleton import Singleton
from filelock import FileLock

from ankama_launcher_emulator_premium.consts import BOTS_STORAGE_PATH
from ankama_launcher_emulator_premium.interfaces.local_storage import (
    BotRecord,
    BotsFile,
)
from ankama_launcher_emulator_premium.interfaces.zaap_files import UserAccount
from ankama_launcher_emulator_premium.utils.atomic_file import (
    acquire_file_lock,
    atomic_write_text,
)


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
            record = bots_file.bots.get(login, BotRecord(email=login))
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
