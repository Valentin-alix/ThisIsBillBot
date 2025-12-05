import logging
from threading import RLock

from base_python.singleton import Singleton
from filelock import FileLock

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.consts import MAIL_ACCOUNTS_STORAGE_PATH
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.mail_account import (
    ImapAccountConfig,
    MailAccountEntry,
    MailAccountsFile,
    ManualAccountConfig,
    SmailProAccountConfig,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.utils.atomic_file import (
    acquire_file_lock,
    atomic_write_text,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.mail_providers.smailpro import (
    generate_random_mailbox,
)

logger = logging.getLogger(__name__)


class MailAccountController(metaclass=Singleton):
    _LOCK = RLock()
    _FILE_LOCK_TIMEOUT_SECONDS = 20.0

    def _load(self) -> MailAccountsFile:
        with self._LOCK:
            if not MAIL_ACCOUNTS_STORAGE_PATH.exists():
                return MailAccountsFile()
            return MailAccountsFile.model_validate_json(
                MAIL_ACCOUNTS_STORAGE_PATH.read_text(encoding="utf-8")
            )

    def _save(self, accounts_file: MailAccountsFile) -> None:
        atomic_write_text(MAIL_ACCOUNTS_STORAGE_PATH, accounts_file.model_dump_json(indent=2))

    def _acquire_file_lock(self) -> FileLock:
        return acquire_file_lock(MAIL_ACCOUNTS_STORAGE_PATH, timeout_seconds=self._FILE_LOCK_TIMEOUT_SECONDS)

    def _get_entry(self, account_email: str) -> MailAccountEntry | None:
        return self._load().accounts.get(account_email)

    def get_config(
        self, account_email: str
    ) -> ImapAccountConfig | SmailProAccountConfig | ManualAccountConfig | None:
        entry = self._get_entry(account_email)
        return entry.config if entry is not None else None

    def load_bad_state_emails(self) -> set[str]:
        return {email for email, entry in self._load().accounts.items() if entry.bad_state}

    def record_bad_state(self, email: str) -> None:
        with self._acquire_file_lock():
            accounts_file = self._load()
            entry = accounts_file.accounts.setdefault(email, MailAccountEntry())
            was_present = entry.bad_state
            entry.bad_state = True
            self._save(accounts_file)
        if not was_present:
            logger.warning("[Auth] Recorded bad-state email %s", email)

    def peek_next_available_email(self) -> str | None:
        accounts = self._load().accounts
        for email in sorted(accounts):
            entry = accounts[email]
            if not entry.bad_state and not entry.is_used:
                return email
        return None

    def mark_used(self, email: str) -> None:
        with self._acquire_file_lock():
            accounts_file = self._load()
            entry = accounts_file.accounts.setdefault(email, MailAccountEntry())
            entry.is_used = True
            self._save(accounts_file)

    def remove_email(self, email: str) -> None:
        with self._acquire_file_lock():
            accounts_file = self._load()
            if accounts_file.accounts.pop(email, None) is not None:
                self._save(accounts_file)

    def provision_smailpro_email(self, api_key: str) -> str:
        kind = "gmail"
        email, timestamp = generate_random_mailbox(api_key, kind)
        with self._acquire_file_lock():
            accounts_file = self._load()
            accounts_file.accounts[email] = MailAccountEntry(
                config=SmailProAccountConfig(api_key=api_key, email=email, kind=kind, timestamp=timestamp)
            )
            self._save(accounts_file)
        return email
