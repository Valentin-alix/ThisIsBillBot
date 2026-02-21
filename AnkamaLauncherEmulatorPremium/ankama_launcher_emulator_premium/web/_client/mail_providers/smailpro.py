import asyncio
import logging
import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import requests
from pydantic import BaseModel

from ankama_launcher_emulator_premium.utils.internet import raise_for_status_with_content
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.consts import (
    SMAILPRO_OUTLOOK_DISABLED_UNTIL_PATH,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.exceptions import HaapiHttpError
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.utils.atomic_file import (
    acquire_file_lock,
    atomic_write_text,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.mail_providers.manual import (
    extract_confirmation_code,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

SMAILPRO_BASE_URL = "https://app.sonjj.com"
SMAILPRO_CODE_TIMEOUT_SECONDS = 2 * 60
SMAILPRO_INITIAL_DELAY_SECONDS = 30.0
SMAILPRO_POLL_INTERVAL_SECONDS = 15.0
SMAILPRO_REQUEST_TIMEOUT_SECONDS = 15.0
SMAILPRO_RECEIPT_GRACE_SECONDS = 10
SMAILPRO_OUTLOOK_DISABLE_DURATION = timedelta(days=1)

RandomMailboxKind = Literal["gmail", "outlook"]
_RANDOM_MAILBOX_PATH: dict[RandomMailboxKind, str] = {"gmail": "temp_gmail", "outlook": "temp_outlook"}


@dataclass(frozen=True)
class SmailProSettings:
    api_key: str
    email: str
    kind: RandomMailboxKind
    timestamp: int
    consumed_message_ids: frozenset[str] = frozenset()
    mark_message_consumed: Callable[[str], None] | None = None


class RandomMailboxResponse(BaseModel):
    email: str
    timestamp: int
    type: Literal["real", "alias"]


class OutlookDisableState(BaseModel):
    disabled_until: datetime


def is_outlook_generation_disabled(*, now: datetime | None = None) -> bool:
    if not SMAILPRO_OUTLOOK_DISABLED_UNTIL_PATH.exists():
        return False
    state = OutlookDisableState.model_validate_json(
        SMAILPRO_OUTLOOK_DISABLED_UNTIL_PATH.read_text(encoding="utf-8")
    )
    return state.disabled_until > (now or datetime.now(UTC))


def disable_outlook_generation() -> datetime:
    disabled_until = datetime.now(UTC) + SMAILPRO_OUTLOOK_DISABLE_DURATION
    with acquire_file_lock(SMAILPRO_OUTLOOK_DISABLED_UNTIL_PATH):
        if SMAILPRO_OUTLOOK_DISABLED_UNTIL_PATH.exists():
            previous_state = OutlookDisableState.model_validate_json(
                SMAILPRO_OUTLOOK_DISABLED_UNTIL_PATH.read_text(encoding="utf-8")
            )
            disabled_until = max(disabled_until, previous_state.disabled_until)
        atomic_write_text(
            SMAILPRO_OUTLOOK_DISABLED_UNTIL_PATH,
            OutlookDisableState(disabled_until=disabled_until).model_dump_json(),
        )
    logger.warning(
        "[SmailPro] Outlook generation disabled until %s after provider token failure.", disabled_until
    )
    return disabled_until


def is_outlook_token_refresh_failure(error: HaapiHttpError) -> bool:
    return (
        error.status_code == 400
        and "Outlook token refresh failed" in str(error)
        and "AADSTS700016" in str(error)
    )


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
    body: dict[str, Any] = raise_for_status_with_content(response)
    mailbox = RandomMailboxResponse.model_validate(body)
    logger.debug("[SmailPro] Minted %s mailbox %s (timestamp=%s)", kind, mailbox.email, mailbox.timestamp)
    return mailbox.email, mailbox.timestamp


def generate_random_mailbox_settings(api_key: str) -> SmailProSettings:
    kind: RandomMailboxKind = (
        "gmail" if is_outlook_generation_disabled() else random.choice(("gmail", "outlook"))
    )
    email, timestamp = generate_random_mailbox(api_key, kind)
    return SmailProSettings(api_key=api_key, email=email, kind=kind, timestamp=timestamp)


class SmailProMailProvider:
    def __init__(self, settings: SmailProSettings) -> None:
        self._settings = settings
        self._session = _session(settings.api_key)
        self._consumed_message_ids = set(settings.consumed_message_ids)

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
        logger.debug("[SmailPro] %d recent message(s) for %s", len(messages), self._settings.email)
        for message in messages:
            mid = message.get("mid")
            if not isinstance(mid, str):
                logger.debug("[SmailPro] Message without mid, skipping.")
                continue
            if mid in self._consumed_message_ids:
                logger.debug("[SmailPro] Skipping consumed Ankama message mid=%s.", mid)
                continue
            if not _is_ankama_message(message):
                logger.debug("[SmailPro] Skipping non-Ankama message mid=%s.", mid)
                continue
            body = self._fetch_message_body(mid)
            if body is None:
                continue
            code = extract_confirmation_code(body)
            if code is None:
                logger.debug("[SmailPro] No confirmation code found in mid=%s body.", mid)
                continue
            self._consumed_message_ids.add(mid)
            if self._settings.mark_message_consumed is not None:
                self._settings.mark_message_consumed(mid)
            logger.info(f"[SmailPro] Confirmation code found. {code}")
            return code
        return None

    def _recent_messages(self, since: datetime) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "email": self._settings.email,
            "timestamp": max(
                self._settings.timestamp, int(since.timestamp()) - SMAILPRO_RECEIPT_GRACE_SECONDS
            ),
        }
        response = self._session.get(
            f"{SMAILPRO_BASE_URL}/v1/{_RANDOM_MAILBOX_PATH[self._settings.kind]}/inbox",
            params=params,
            timeout=SMAILPRO_REQUEST_TIMEOUT_SECONDS,
        )

        try:
            body: dict[str, Any] = raise_for_status_with_content(response)
        except HaapiHttpError as error:
            if self._settings.kind == "outlook" and is_outlook_token_refresh_failure(error):
                disable_outlook_generation()
            raise
        messages: list[dict[str, Any]] = body.get("messages", [])
        logger.debug("[SmailPro] Inbox returned %d message(s) for %s.", len(messages), self._settings.email)
        return messages

    def _fetch_message_body(self, mid: str) -> str | None:
        response = self._session.get(
            f"{SMAILPRO_BASE_URL}/v1/{_RANDOM_MAILBOX_PATH[self._settings.kind]}/message",
            params={"email": self._settings.email, "mid": mid},
            timeout=SMAILPRO_REQUEST_TIMEOUT_SECONDS,
        )
        body: dict[str, Any] = raise_for_status_with_content(response)
        text: str | None = body.get("body") or body.get("html")
        return text


def _is_ankama_message(message: dict[str, Any]) -> bool:
    for field_name in ("textFrom", "textSubject"):
        value = message.get(field_name)
        if isinstance(value, str) and "ankama" in value.casefold():
            return True
    return False
