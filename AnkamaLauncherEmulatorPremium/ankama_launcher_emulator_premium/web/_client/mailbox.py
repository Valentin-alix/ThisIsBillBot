import asyncio
import email
import imaplib
import logging
import os
import queue
import re
import sys
import threading
import time
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from email.message import Message
from email.utils import parsedate_to_datetime
from html import unescape

from dotenv import load_dotenv

from ankama_launcher_emulator_premium.consts import ENV_PATH

logger = logging.getLogger(__name__)

CONFIRMATION_CODE_PATTERN = re.compile(r"(?<!\d)(\d{6})(?!\d)")
MAILBOX_POLL_INTERVAL_SECONDS = 2.0
MANUAL_CODE_POLL_INTERVAL_SECONDS = 0.2


@dataclass(frozen=True)
class MailboxSettings:
    host: str
    username: str
    password: str
    port: int = 993
    use_ssl: bool = True
    folder: str = "INBOX"
    spam_folder: str = "[Gmail]/Spam"

    @classmethod
    def from_env(cls) -> "MailboxSettings":
        """Build settings from the standard ``IMAP_*`` environment variables."""
        load_dotenv(ENV_PATH)
        return cls(
            host=os.environ["IMAP_HOST"],
            username=os.environ["IMAP_EMAIL"],
            password=os.environ["IMAP_PASSWORD"],
            port=int(os.environ["IMAP_PORT"]),
        )

    @property
    def search_folders(self) -> tuple[str, ...]:
        return (self.folder, self.spam_folder)


class MailboxCodeTimeoutError(TimeoutError):
    pass


def extract_confirmation_code(content: str) -> str | None:
    normalized = re.sub(r"<[^>]+>", " ", unescape(content))
    match = CONFIRMATION_CODE_PATTERN.search(normalized)
    if match is None:
        return None
    return match.group(1)


class ManualCodeInput:
    """Lets the operator type a confirmation code in the terminal.

    stdin can only be consumed by one reader, so a single lazily started thread owns it
    for the whole process and hands the parsed codes to every waiter through a queue.
    The thread is a daemon because a blocking ``readline`` cannot be interrupted: it
    must not keep the interpreter alive at shutdown.
    """

    _instance: "ManualCodeInput | None" = None
    _instance_lock = threading.Lock()

    def __init__(self) -> None:
        self._codes: queue.Queue[str] = queue.Queue()
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._closed = False

    @classmethod
    def start(cls) -> "ManualCodeInput | None":
        """Return the shared reader, or ``None`` when stdin is not a terminal."""
        if not _stdin_is_interactive():
            return None
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = cls()
            instance = cls._instance
        instance._ensure_thread()
        if instance._closed:
            return None
        return instance

    def drain(self) -> None:
        """Drop codes typed before the current wait started."""
        while True:
            try:
                self._codes.get_nowait()
            except queue.Empty:
                return

    def poll(self) -> str | None:
        try:
            return self._codes.get_nowait()
        except queue.Empty:
            return None

    def _ensure_thread(self) -> None:
        with self._lock:
            if self._closed:
                return
            if self._thread is not None and self._thread.is_alive():
                return
            self._thread = threading.Thread(
                target=self._read_loop, name="manual-confirmation-code", daemon=True
            )
            self._thread.start()

    def _read_loop(self) -> None:
        for line in sys.stdin:
            stripped = line.strip()
            if not stripped:
                continue
            code = extract_confirmation_code(stripped)
            if code is None:
                logger.info("[Mailbox] Ignored manual input %r (expected 6 digits).", stripped)
                continue
            self._codes.put(code)
        # stdin reached EOF (piped/closed input): never restart the reader.
        with self._lock:
            self._closed = True


def _stdin_is_interactive() -> bool:
    stream = sys.stdin
    if stream is None:
        return False
    try:
        return stream.isatty()
    except ValueError:
        return False


async def _sleep_until_manual_code(manual: ManualCodeInput | None, seconds: float) -> str | None:
    """Sleep ``seconds``, returning early with a code typed in the terminal."""
    deadline = time.monotonic() + seconds
    while True:
        if manual is not None:
            code = manual.poll()
            if code is not None:
                logger.info("[Mailbox] Confirmation code entered manually.")
                return code
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return None
        await asyncio.sleep(min(MANUAL_CODE_POLL_INTERVAL_SECONDS, remaining))


class ImapMailboxClient:
    def __init__(self, settings: MailboxSettings) -> None:
        self._settings = settings

    async def wait_for_code(
        self, *, since: datetime, timeout_seconds: int, allow_manual: bool = True
    ) -> str | None:
        """Return a recent confirmation code and permanently delete its message.

        The mailbox scan races against the terminal: when the process is attached to a
        console, typing the six digits resolves the wait immediately, which unblocks
        accounts whose code never lands in the watched mailbox.
        """
        deadline = time.monotonic() + timeout_seconds
        manual = ManualCodeInput.start() if allow_manual else None
        if manual is not None:
            manual.drain()
            logger.info(
                "[Mailbox] Waiting for a confirmation code — you can also type it here (6 digits + Enter)."
            )
        while time.monotonic() < deadline:
            code = await asyncio.to_thread(self._find_code, since)
            if code is not None:
                return code
            code = await _sleep_until_manual_code(manual, MAILBOX_POLL_INTERVAL_SECONDS)
            if code is not None:
                return code
        return None

    def _find_code(self, since: datetime) -> str | None:
        with self._connect() as client:
            client.login(self._settings.username, self._settings.password)
            for folder in self._settings.search_folders:
                code = self._find_code_in_folder(client, folder, since)
                if code is not None:
                    return code
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
            # No code in a recent-enough message: log what we saw so an
            # unrecognised Shield-email format is diagnosable from the logs.
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
