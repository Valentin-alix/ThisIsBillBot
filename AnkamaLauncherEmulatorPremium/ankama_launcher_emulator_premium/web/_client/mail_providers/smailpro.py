import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any

import requests

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.mail_providers.manual import (
    extract_confirmation_code,
)

logger = logging.getLogger(__name__)

SMAILPRO_BASE_URL = "https://app.sonjj.com"
SMAILPRO_POLL_INTERVAL_SECONDS = 2.0
SMAILPRO_REQUEST_TIMEOUT_SECONDS = 15.0


@dataclass(frozen=True)
class SmailProSettings:
    api_key: str
    email: str
    expiry_minutes: int = 30


def _session(api_key: str) -> requests.Session:
    session = requests.Session()
    session.headers["X-Api-Key"] = api_key
    return session


def create_smailpro_mailbox(api_key: str, email: str, expiry_minutes: int = 30) -> str:
    """Create (or extend) a temporary SmailPro mailbox and return its address."""
    response = _session(api_key).get(
        f"{SMAILPRO_BASE_URL}/v1/temp_email/create",
        params={"email": email, "expiry_minutes": expiry_minutes},
        timeout=SMAILPRO_REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return email


class SmailProMailProvider:
    def __init__(self, settings: SmailProSettings) -> None:
        self._settings = settings
        self._session = _session(settings.api_key)

    async def wait_for_code(self, *, since: datetime, timeout_seconds: int) -> str | None:
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            code = await asyncio.to_thread(self._find_code, since)
            if code is not None:
                return code
            await asyncio.sleep(SMAILPRO_POLL_INTERVAL_SECONDS)
        return None

    def _find_code(self, since: datetime) -> str | None:
        for message in self._recent_messages(since):
            mid = message.get("mid")
            if mid is None:
                continue
            body = self._fetch_message_body(mid)
            if body is None:
                continue
            code = extract_confirmation_code(body)
            if code is not None:
                logger.info("[SmailPro] Confirmation code found.")
                return code
        return None

    def _recent_messages(self, since: datetime) -> list[dict[str, Any]]:
        response = self._session.get(
            f"{SMAILPRO_BASE_URL}/v1/temp_email/inbox",
            params={"email": self._settings.email},
            timeout=SMAILPRO_REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        body: dict[str, Any] = response.json()
        messages: list[dict[str, Any]] = body.get("messages", [])
        return [message for message in messages if _message_date(message) >= since]

    def _fetch_message_body(self, mid: str) -> str | None:
        response = self._session.get(
            f"{SMAILPRO_BASE_URL}/v1/temp_email/message",
            params={"email": self._settings.email, "mid": mid},
            timeout=SMAILPRO_REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        body: dict[str, Any] = response.json()
        text: str | None = body.get("body") or body.get("html")
        return text


def _message_date(message: dict[str, Any]) -> datetime:
    date_header = message.get("date")
    if not isinstance(date_header, str):
        return datetime.min.replace(tzinfo=UTC)
    parsed = parsedate_to_datetime(date_header)
    if parsed is None:
        return datetime.min.replace(tzinfo=UTC)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)
