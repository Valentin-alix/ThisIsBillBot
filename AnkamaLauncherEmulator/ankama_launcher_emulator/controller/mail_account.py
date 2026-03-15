from utils.local_json import read_local_model
import logging
import re
from datetime import datetime, timezone
from threading import RLock

from utils.singleton import Singleton
from filelock import FileLock

from ankama_launcher_emulator.consts import MAIL_ACCOUNTS_STORAGE_PATH
from ankama_launcher_emulator.interfaces.mail_account import (
    ImapAccountConfig,
    MailAccountEntry,
    MailAccountsFile,
    MailAccountConfig,
    ManualAccountConfig,
    SmailProAccountConfig,
)
from ankama_launcher_emulator.quarantine_signals import (
    quarantine_signals,
)
from ankama_launcher_emulator.utils.atomic_file import (
    acquire_file_lock,
    atomic_write_text,
)
from ankama_launcher_emulator.web._client.mail_providers.smailpro import (
    generate_random_mailbox_settings,
    is_outlook_generation_disabled,
)

logger = logging.getLogger(__name__)


class MailAccountController(metaclass=Singleton):
    _LOCK = RLock()
    _FILE_LOCK_TIMEOUT_SECONDS = 20.0

    def _load(self) -> MailAccountsFile:
        with self._LOCK:
            if not MAIL_ACCOUNTS_STORAGE_PATH.exists():
                return MailAccountsFile()
            return read_local_model(MAIL_ACCOUNTS_STORAGE_PATH, MailAccountsFile)

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

    def get_all_entries(self) -> dict[str, MailAccountEntry]:
        with self._acquire_file_lock():
            return self._load().accounts

    def save_config(self, email: str, config: MailAccountConfig, *, create: bool = False) -> None:
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            raise ValueError("Invalid email address.")
        if isinstance(config, ImapAccountConfig):
            if not config.host.strip() or not config.username.strip() or not config.password:
                raise ValueError("IMAP server, username, and password are required.")
            if not 1 <= config.port <= 65535:
                raise ValueError("The IMAP port must be between 1 and 65535.")
        if isinstance(config, SmailProAccountConfig):
            if not config.api_key.strip() or config.email != email or config.timestamp <= 0:
                raise ValueError("A valid SmailPro key, address, and timestamp are required.")
        with self._acquire_file_lock():
            accounts = self._load()
            if create and email in accounts.accounts:
                raise ValueError("This address already exists.")
            if not create and email not in accounts.accounts:
                raise ValueError("This address no longer exists. Refresh the list.")
            entry = accounts.accounts.setdefault(email, MailAccountEntry())
            previous = entry.config
            if isinstance(previous, SmailProAccountConfig) and isinstance(config, SmailProAccountConfig):
                config = config.model_copy(update={"consumed_message_ids": previous.consumed_message_ids})
            entry.config = config
            self._save(accounts)

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
            if (
                isinstance(entry.config, SmailProAccountConfig)
                and entry.config.kind == "outlook"
                and is_outlook_generation_disabled()
            ):
                continue
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
            removed = accounts_file.accounts.pop(email, None)
            if removed is not None:
                self._save(accounts_file)
        if removed is not None:
            quarantine_signals.changed.emit()

    def quarantine(self, email: str, reason: str) -> bool:
        with self._acquire_file_lock():
            accounts_file = self._load()
            entry = accounts_file.accounts.get(email)
            if entry is None:
                logger.warning("[Mailbox] Cannot quarantine unknown mailbox %s", email)
                return False
            entry.bad_state = True
            entry.quarantine_reason = reason
            entry.quarantined_at = datetime.now(timezone.utc)
            self._save(accounts_file)
        logger.warning("[Mailbox] Quarantined %s: %s", email, reason)
        quarantine_signals.changed.emit()
        return True

    def restore_from_quarantine(self, email: str) -> None:
        with self._acquire_file_lock():
            accounts_file = self._load()
            entry = accounts_file.accounts.get(email)
            if entry is None:
                raise LookupError(f"No mailbox stored for {email}")
            entry.bad_state = False
            entry.quarantine_reason = None
            entry.quarantined_at = None
            self._save(accounts_file)
        quarantine_signals.changed.emit()

    def record_smailpro_message_consumed(self, email: str, mid: str) -> None:
        with self._acquire_file_lock():
            accounts_file = self._load()
            entry = accounts_file.accounts.get(email)
            if entry is None or not isinstance(entry.config, SmailProAccountConfig):
                return
            consumed_message_ids = entry.config.consumed_message_ids
            if mid in consumed_message_ids:
                return
            consumed_message_ids.append(mid)
            del consumed_message_ids[:-50]
            self._save(accounts_file)

    def provision_smailpro_email(self, api_key: str) -> str:
        settings = generate_random_mailbox_settings(api_key)
        with self._acquire_file_lock():
            accounts_file = self._load()
            accounts_file.accounts[settings.email] = MailAccountEntry(
                config=SmailProAccountConfig(
                    api_key=settings.api_key,
                    email=settings.email,
                    kind=settings.kind,
                    timestamp=settings.timestamp,
                )
            )
            self._save(accounts_file)
        return settings.email
