import asyncio
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any, Literal

import requests
from pydantic import BaseModel

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.mail_providers.manual import (
    extract_confirmation_code,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

SMAILPRO_BASE_URL = "https://app.sonjj.com"
SMAILPRO_CODE_TIMEOUT_SECONDS = 2.5 * 60
SMAILPRO_INITIAL_DELAY_SECONDS = 30.0
SMAILPRO_POLL_INTERVAL_SECONDS = 30.0
SMAILPRO_REQUEST_TIMEOUT_SECONDS = 15.0

RandomMailboxKind = Literal["gmail", "outlook"]
_RANDOM_MAILBOX_PATH: dict[RandomMailboxKind, str] = {"gmail": "temp_gmail", "outlook": "temp_outlook"}
# Each provider's inbox uses its own textDate format: Gmail sends RFC 2822, Outlook sends ISO 8601.
_TEXT_DATE_PARSERS: dict[RandomMailboxKind, Callable[[str], datetime]] = {
    "gmail": parsedate_to_datetime,
    "outlook": datetime.fromisoformat,
}


@dataclass(frozen=True)
class SmailProSettings:
    api_key: str
    email: str
    kind: RandomMailboxKind
    timestamp: int


class RandomMailboxResponse(BaseModel):
    email: str
    timestamp: int
    type: Literal["real", "alias"]


def _session(api_key: str) -> requests.Session:
    session = requests.Session()
    session.headers["X-Api-Key"] = api_key
    return session


def generate_random_mailbox(api_key: str, kind: RandomMailboxKind) -> tuple[str, int]:
    """Mint a fresh real Gmail/Outlook address in a single API call (no domain lookup)."""
    response = _session(api_key).get(
        f"{SMAILPRO_BASE_URL}/v1/{_RANDOM_MAILBOX_PATH[kind]}/random",
        params={"type": "real"},
        timeout=SMAILPRO_REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    body: dict[str, Any] = response.json()
    mailbox = RandomMailboxResponse.model_validate(body)
    logger.info("[SmailPro] Minted %s mailbox %s (timestamp=%s)", kind, mailbox.email, mailbox.timestamp)
    return mailbox.email, mailbox.timestamp


class SmailProMailProvider:
    def __init__(self, settings: SmailProSettings) -> None:
        self._settings = settings
        self._session = _session(settings.api_key)

    async def wait_for_code(self, *, since: datetime, timeout_seconds: int) -> str | None:
        effective_timeout_seconds = min(timeout_seconds, SMAILPRO_CODE_TIMEOUT_SECONDS)
        deadline = time.monotonic() + effective_timeout_seconds
        await asyncio.sleep(min(SMAILPRO_INITIAL_DELAY_SECONDS, effective_timeout_seconds))
        while time.monotonic() < deadline:
            code = await asyncio.to_thread(self._find_code, since)
            if code is not None:
                return code
            remaining_seconds = deadline - time.monotonic()
            await asyncio.sleep(min(SMAILPRO_POLL_INTERVAL_SECONDS, remaining_seconds))
        return None

    def _find_code(self, since: datetime) -> str | None:
        messages = self._recent_messages(since)
        logger.debug(
            "[SmailPro] %d recent message(s) for %s: %r", len(messages), self._settings.email, messages
        )
        for message in messages:
            mid = message.get("mid")
            if mid is None:
                logger.debug("[SmailPro] Message without mid, skipping: %r", message)
                continue
            body = self._fetch_message_body(mid)
            logger.debug("[SmailPro] Body for mid=%s: %r", mid, body)
            if body is None:
                continue
            code = extract_confirmation_code(body)
            if code is None:
                logger.debug("[SmailPro] No confirmation code found in mid=%s body.", mid)
                continue
            logger.info("[SmailPro] Confirmation code found.")
            return code
        return None

    def _recent_messages(self, since: datetime) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"email": self._settings.email, "timestamp": self._settings.timestamp}
        response = self._session.get(
            f"{SMAILPRO_BASE_URL}/v1/{_RANDOM_MAILBOX_PATH[self._settings.kind]}/inbox",
            params=params,
            timeout=SMAILPRO_REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        body: dict[str, Any] = response.json()
        logger.debug("[SmailPro] Inbox response for %s: %r", self._settings.email, body)
        messages: list[dict[str, Any]] = body.get("messages", [])
        return [message for message in messages if _message_date(message, self._settings.kind) >= since]

    def _fetch_message_body(self, mid: str) -> str | None:
        response = self._session.get(
            f"{SMAILPRO_BASE_URL}/v1/{_RANDOM_MAILBOX_PATH[self._settings.kind]}/message",
            params={"email": self._settings.email, "mid": mid},
            timeout=SMAILPRO_REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        body: dict[str, Any] = response.json()
        logger.debug("[SmailPro] Message response for mid=%s: %r", mid, body)
        text: str | None = body.get("body") or body.get("html")
        return text


def _message_date(message: dict[str, Any], kind: RandomMailboxKind) -> datetime:
    date_text = message.get("textDate")
    if not isinstance(date_text, str):
        return datetime.min.replace(tzinfo=UTC)
    parsed = _TEXT_DATE_PARSERS[kind](date_text)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
