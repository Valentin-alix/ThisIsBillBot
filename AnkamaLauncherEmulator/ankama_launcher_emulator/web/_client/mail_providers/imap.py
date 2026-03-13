import asyncio
import email
import imaplib
import logging
import re
import time
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from email.message import Message
from email.utils import parsedate_to_datetime
from html import unescape

from ankama_launcher_emulator.web._client.mail_providers.manual import (
    extract_confirmation_code,
)

logger = logging.getLogger(__name__)

IMAP_POLL_INTERVAL_SECONDS = 2.0


@dataclass(frozen=True)
class MailboxSettings:
    host: str
    username: str
    password: str
    port: int = 993
    use_ssl: bool = True
    folder: str = "INBOX"
    spam_folder: str = "[Gmail]/Spam"

    @property
    def search_folders(self) -> tuple[str, ...]:
        return (self.folder, self.spam_folder)


class ImapMailProvider:
    def __init__(self, settings: MailboxSettings) -> None:
        self._settings = settings

    async def wait_for_code(self, *, since: datetime, timeout_seconds: int) -> str | None:
        """Return a recent confirmation code and permanently delete its message."""
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            code = await asyncio.to_thread(self._find_code, since)
            if code is not None:
                return code
            await asyncio.sleep(IMAP_POLL_INTERVAL_SECONDS)
        return None

    def _find_code(self, since: datetime) -> str | None:
        try:
            with self._connect() as client:
                client.login(self._settings.username, self._settings.password)
                for folder in self._settings.search_folders:
                    code = self._find_code_in_folder(client, folder, since)
                    if code is not None:
                        return code
        except (imaplib.IMAP4.error, OSError):
            logger.exception("[Mailbox] IMAP connection or login failed; will retry")
            return None
        return None

    def _find_code_in_folder(self, client: imaplib.IMAP4, folder: str, since: datetime) -> str | None:
        try:
            select_status, _ = client.select(folder, readonly=False)
        except imaplib.IMAP4.error:
            logger.exception(f"error while selecting folder {folder}")
            return None
        if select_status != "OK":
            return None
        status, data = client.search(None, "UNSEEN", "SINCE", since.strftime("%d-%b-%Y"))
        if status != "OK" or not data:
            return None
        ids = data[0].split()
        for message_id in reversed(ids[-20:]):
            code = self._code_from_message(client, message_id, since)
            if code is not None:
                return code
        return None

    def _connect(self) -> imaplib.IMAP4:
        if self._settings.use_ssl:
            return imaplib.IMAP4_SSL(self._settings.host, self._settings.port)
        return imaplib.IMAP4(self._settings.host, self._settings.port)

    def _code_from_message(self, client: imaplib.IMAP4, message_id: bytes, since: datetime) -> str | None:
        status, data = client.fetch(message_id.decode("ascii"), "(BODY.PEEK[])")
        if status != "OK" or not data:
            return None
        for item in data:
            if not isinstance(item, tuple):
                continue
            raw_message = item[1]
            if not isinstance(raw_message, bytes):
                continue
            message = email.message_from_bytes(raw_message)
            if _message_datetime(message) < since:
                continue
            for part in _message_text_parts(message):
                code = extract_confirmation_code(part)
                if code is not None:
                    self._delete_message(client, message_id)
                    logger.info("[Mailbox] Confirmation code found and deleted.")
                    return code
            logger.info(
                "[Mailbox] No code in message subject=%r snippet=%r",
                message.get("Subject", ""),
                _first_text_snippet(message),
            )
        return None

    def _delete_message(self, client: imaplib.IMAP4, message_id: bytes) -> None:
        message_number = message_id.decode("ascii")
        store_status, _ = client.store(message_number, "+FLAGS", r"(\Deleted)")
        if store_status != "OK":
            raise RuntimeError(f"Failed to mark mailbox message {message_number} for deletion")
        expunge_status, _ = client.expunge()
        if expunge_status != "OK":
            raise RuntimeError(f"Failed to expunge mailbox message {message_number}")


def _message_datetime(message: Message) -> datetime:
    date_header = message.get("Date")
    if date_header is None:
        return datetime.min.replace(tzinfo=UTC)
    parsed = parsedate_to_datetime(date_header)
    if parsed is None:
        return datetime.min.replace(tzinfo=UTC)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _first_text_snippet(message: Message, limit: int = 200) -> str:
    for part in _message_text_parts(message):
        collapsed = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", unescape(part))).strip()
        if collapsed:
            return collapsed[:limit]
    return ""


def _message_text_parts(message: Message) -> Iterable[str]:
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get_content_type() not in {"text/plain", "text/html"}:
                continue
            payload = part.get_payload(decode=True)
            if not isinstance(payload, bytes):
                continue
            charset = part.get_content_charset() or "utf-8"
            yield payload.decode(charset, errors="replace")
        return
    payload = message.get_payload(decode=True)
    if isinstance(payload, bytes):
        charset = message.get_content_charset() or "utf-8"
        yield payload.decode(charset, errors="replace")
