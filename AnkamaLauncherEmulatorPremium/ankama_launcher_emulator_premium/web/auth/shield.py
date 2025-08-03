"""Resolve Ankama Shield / OTP during the launcher login (HAAPI-based)."""

import logging
from datetime import datetime

from ankama_launcher_emulator_premium.decrypter.crypto_helper import CryptoHelper
from ankama_launcher_emulator_premium.haapi.haapi import (
    Haapi,
    ShieldNotRequiredError,
)
from ankama_launcher_emulator_premium.interfaces.credentials import (
    DecipheredCertif,
)
from ankama_launcher_emulator_premium.interfaces.haapi_api import SignOnResponse
from ankama_launcher_emulator_premium.web._client.mailbox import (
    ImapMailboxClient,
    MailboxCodeTimeoutError,
    MailboxSettings,
)

ZAAP_GAME_ID = 102

logger = logging.getLogger(__name__)


async def _request_and_validate_email_certificate(
    haapi: Haapi,
    mailbox: MailboxSettings,
    since: datetime,
    timeout_seconds: int,
) -> DecipheredCertif:
    """Run the EMAIL Shield flow: request a code, await it, validate, persist.

    Raises ``RuntimeError`` when no code arrives before ``timeout_seconds``.
    """
    domain = haapi.get_security_code("EMAIL")
    logger.info("[OAuth] Shield security code requested (domain=%s)", domain)

    client = ImapMailboxClient(mailbox)
    code = await client.wait_for_code(since=since, timeout_seconds=timeout_seconds)
    if code is None:
        raise MailboxCodeTimeoutError(f"Timed out waiting for Shield/OTP code in mailbox for {haapi.login}")

    certif = haapi.validate_code(code, ZAAP_GAME_ID)
    logger.info("[OAuth] Certificate obtained (id=%s)", certif.id)
    CryptoHelper.store_certificate(certif)
    return certif


async def resolve_shield(
    haapi: Haapi,
    account_info: SignOnResponse | None,
    mailbox: MailboxSettings,
    started_at: datetime,
    *,
    timeout_seconds: int = 300,
) -> DecipheredCertif | None:
    security = account_info.security if account_info is not None else []
    has_shield = "SHIELD" in security
    has_otp = "OTP" in security
    if not (has_shield or has_otp):
        return None

    if has_shield:
        return await _request_and_validate_email_certificate(haapi, mailbox, started_at, timeout_seconds)

    logger.info("[OAuth] OTP required; waiting for code in mailbox...")
    client = ImapMailboxClient(mailbox)
    code = await client.wait_for_code(since=started_at, timeout_seconds=timeout_seconds)
    if code is None:
        raise MailboxCodeTimeoutError(f"Timed out waiting for Shield/OTP code in mailbox for {haapi.login}")

    certif = haapi.validate_otp(code, ZAAP_GAME_ID)
    logger.info("[OAuth] Certificate obtained (id=%s)", certif.id)
    CryptoHelper.store_certificate(certif)
    return certif


async def secure_apikey_via_email(
    haapi: Haapi,
    mailbox: MailboxSettings,
    since: datetime,
    *,
    timeout_seconds: int = 300,
) -> DecipheredCertif | None:
    """Force-secure an apikey that sign-on did not flag as needing a Shield.

    Ankama's ``CreateToken`` (game launch) refuses an apikey that is not bound to a
    device certificate, even when ``SignOnResponse.security`` is empty. This runs the
    EMAIL Shield flow unconditionally so the stored apikey is always certificate-bound.

    Some accounts genuinely do not need securing: HAAPI then answers the security-code
    request with ``401 NONEEDTOBESECURED``. That is benign — return ``None`` so the
    caller proceeds with the unsecured apikey instead of aborting authentication.

    ``since`` is the mailbox watermark; pass the auth start time. The mailbox scan
    returns the *newest* matching code, so an older registration-confirmation email
    cannot win even with a generous watermark.
    """
    logger.info("[OAuth] Securing apikey via forced email Shield flow...")
    try:
        return await _request_and_validate_email_certificate(haapi, mailbox, since, timeout_seconds)
    except ShieldNotRequiredError:
        logger.info(
            "[OAuth] Apikey does not need securing (NONEEDTOBESECURED); proceeding without certificate."
        )
        return None
