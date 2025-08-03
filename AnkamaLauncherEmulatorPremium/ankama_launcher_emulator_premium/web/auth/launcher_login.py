import asyncio
import logging
import re
from datetime import UTC, datetime
from urllib.parse import urlencode

from dotenv import load_dotenv
from playwright.async_api import Page, Response
from pydantic import ValidationError
from requests import HTTPError

from ankama_launcher_emulator_premium.consts import ENV_PATH
from ankama_launcher_emulator_premium.decrypter.crypto_helper import CryptoHelper
from ankama_launcher_emulator_premium.exceptions import (
    BannedException,
    ProxyRejectedError,
)
from ankama_launcher_emulator_premium.haapi.haapi import (
    Haapi,
    refresh_api_key_from_oauth,
)
from ankama_launcher_emulator_premium.interfaces.credentials import (
    DecipheredApiKey,
)
from ankama_launcher_emulator_premium.interfaces.local_storage import (
    GeneratedAccountEntry,
)
from ankama_launcher_emulator_premium.interfaces.oauth_api import TokenResponse
from ankama_launcher_emulator_premium.interfaces.schedule_profile import (
    ProxyController,
    ScheduleProfileController,
)
from ankama_launcher_emulator_premium.utils.proxy import build_http_proxy_url
from ankama_launcher_emulator_premium.web._client.browser import launch_browser_context
from ankama_launcher_emulator_premium.web._client.browser_interactions import (
    human_wait,
    visible_form_error_texts,
)
from ankama_launcher_emulator_premium.web._client.credentials import (
    fill_credentials_and_submit,
)
from ankama_launcher_emulator_premium.web._client.mailbox import (
    MailboxCodeTimeoutError,
    MailboxSettings,
)
from ankama_launcher_emulator_premium.web._client.pkce import (
    generate_code_challenge,
    generate_code_verifier,
)
from ankama_launcher_emulator_premium.web.auth.identity import generate_nickname
from ankama_launcher_emulator_premium.web.auth.models import (
    AuthenticationOptions,
    AuthenticationResult,
)
from ankama_launcher_emulator_premium.web.auth.oauth_state import (
    CLIENT_ID,
    LOGIN_REDIRECT_URI,
    build_login_url,
)
from ankama_launcher_emulator_premium.web.auth.shield import (
    ZAAP_GAME_ID,
    resolve_shield,
    secure_apikey_via_email,
)
from ankama_launcher_emulator_premium.web.auth.storage import (
    load_available_generated_accounts,
    load_bad_state_emails,
    mark_account_authenticated,
    mark_account_available_for_auth_retry,
    record_bad_state_email,
)
from ankama_launcher_emulator_premium.web.debug_utils import try_dump_page_html

TOKEN_URL = "https://auth.ankama.com/token"
PROXY_REJECTED_ERROR_TEXT = "connexion non-autorisée : votre adresse ip est cachée."

logger = logging.getLogger()

MIN_DELAY_BETWEEN_ACCOUNTS_SEC = 30


async def _dump_oauth_failure_page(page: Page) -> None:
    logger.info("[OAuth] Failure at URL %s", page.url)
    await try_dump_page_html("oauth_failure", page, logger, "[OAuth]")


async def _exchange_code_for_token(page: Page, auth_code: str, code_verifier: str) -> TokenResponse | None:
    body = urlencode(
        {
            "grant_type": "authorization_code",
            "code": auth_code,
            "code_verifier": code_verifier,
            "client_id": CLIENT_ID,
            "redirect_uri": LOGIN_REDIRECT_URI,
        }
    )
    result = await page.evaluate(f"""
        (async () => {{
            const response = await fetch('{TOKEN_URL}', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
                body: '{body}'
            }});
            return await response.text();
        }})()
        """)
    try:
        parsed = TokenResponse.model_validate_json(result)
    except ValidationError:
        return None
    return parsed


async def _wait_for_tokens(page: Page, code_verifier: str) -> TokenResponse:
    token_res: TokenResponse | None = None

    async def intercept_response(response: Response) -> None:
        nonlocal token_res
        if "/token" not in response.url or not response.ok:
            return
        try:
            token_res = TokenResponse.model_validate(await response.json())
        except ValidationError:
            token_res = None
            return
        logger.info("[OAuth] Access token intercepted from network!")

    page.on("response", lambda res: asyncio.ensure_future(intercept_response(res)))

    auth_code: str | None = None
    for elapsed_seconds in range(120):
        await asyncio.sleep(1)

        visible_errors = await visible_form_error_texts(page)
        if any(PROXY_REJECTED_ERROR_TEXT in visible_error.casefold() for visible_error in visible_errors):
            raise ProxyRejectedError("Ankama rejected the proxy because its IP address is hidden")

        if auth_code and not token_res:
            logger.info("[OAuth] Exchanging code for token in browser...")
            token_res = await _exchange_code_for_token(page, auth_code, code_verifier)
            if token_res:
                logger.info("[OAuth] Token exchange successful!")
            break

        current_url = page.url
        if current_url.startswith("zaap://login?code="):
            auth_code = current_url.replace("zaap://login?code=", "").split("&")[0]
            logger.info("[OAuth] Auth code found in URL: %s...", auth_code[:20])
            continue

        html = await page.content()
        if "zaap://login?code=" in html:
            match = re.search(r"zaap://login\?code=([^\"'\s&]+)", html)
            if match is not None:
                matched_auth_code = match.group(1)
                auth_code = matched_auth_code
                logger.info("[OAuth] Auth code found in HTML: %s...", matched_auth_code[:20])
                continue

        if elapsed_seconds > 0 and elapsed_seconds % 15 == 0:
            logger.info("[OAuth] Still waiting... (%ds / 120s)", elapsed_seconds)

    if not token_res:
        raise RuntimeError("[OAuth] Failed to get access token or refresh token after 120s")
    return token_res


async def authenticate(options: AuthenticationOptions) -> AuthenticationResult:
    logger.info("[OAuth] Starting Browser OAuth 2.0 + PKCE for %s...", options.email)
    started_at = datetime.now(UTC)

    code_verifier = generate_code_verifier()
    login_url = build_login_url(generate_code_challenge(code_verifier))
    page: Page | None = None

    try:
        async with launch_browser_context(headless=options.headless, proxy_url=options.proxy_url) as context:
            page = await context.new_page()
            logger.info("[OAuth] Navigating to login page...")
            try:
                await page.goto(login_url, wait_until="networkidle", timeout=60_000)
            except Exception as err:
                logger.error(err)
                return AuthenticationResult(success=False, email=options.email, error=str(err))
            logger.info("[OAuth] Waiting for WAF challenge...")
            await human_wait(min_seconds=3, max_seconds=4)
            logger.info("[OAuth] Auto-filling credentials...")
            await fill_credentials_and_submit(page, options.email, options.password)
            logger.info("[OAuth] Credentials submitted, URL: %s", page.url)
            logger.info("[OAuth] Waiting for authorization code (up to 120s)...")
            token_res = await _wait_for_tokens(page, code_verifier)

        logger.info("[OAuth] Access token: %s...", token_res.access_token[:20])
        logger.info("[OAuth] Exchanging OAuth tokens for HAAPI API key...")
        api_key_result = refresh_api_key_from_oauth(
            token_res.access_token,
            token_res.refresh_token,
            proxy_url=options.proxy_url,
        )
        logger.info(
            "[OAuth] HAAPI API key obtained for account_id=%s",
            api_key_result.account_id,
        )

        haapi = Haapi(
            api_key=api_key_result.key,
            login=options.email,
            proxy_url=options.proxy_url,
        )
        account_info = haapi.signOnWithApiKey(ZAAP_GAME_ID)
        certificate = await resolve_shield(
            haapi,
            account_info,
            options.mailbox,
            started_at,
            timeout_seconds=options.shield_timeout_seconds,
        )
        if certificate is None:
            logger.info("Securing api key via email...")
            # Sign-on did not advertise a Shield challenge, but CreateToken still
            # requires a certificate-bound apikey. Force the email Shield flow so we
            # never store an unsecured key that only fails later at game launch.
            certificate = await secure_apikey_via_email(
                haapi,
                options.mailbox,
                started_at,
                timeout_seconds=options.shield_timeout_seconds,
            )
        if certificate is not None:
            logger.info("[OAuth] Securing HAAPI API key with certificate...")
            certificate_hash = CryptoHelper.generateHashFromCertif(certificate)
            api_key_result = refresh_api_key_from_oauth(
                token_res.access_token,
                token_res.refresh_token,
                cert_id=certificate.id,
                cert_hash=certificate_hash,
                proxy_url=options.proxy_url,
            )
            haapi = Haapi(
                api_key=api_key_result.key,
                login=options.email,
                proxy_url=options.proxy_url,
            )
            logger.info(
                "[OAuth] Secured HAAPI API key obtained for account_id=%s",
                api_key_result.account_id,
            )

        if account_info.account is None or not account_info.account.nickname:
            for retry in range(5):
                nickname = generate_nickname()
                logger.info(
                    f"Try : {retry + 1} [OAuth] Creating Ankama account nickname %s...",
                    nickname,
                )
                try:
                    haapi.set_nickname_with_api_key(nickname)
                except HTTPError:
                    continue
                else:
                    break

        api_key_data = DecipheredApiKey(
            key=api_key_result.key,
            provider="ankama",
            refreshToken=api_key_result.refresh_token,
            isStayLoggedIn=True,
            accountId=api_key_result.account_id,
            login=options.email,
            certificate=certificate,
            refreshDate=0,
        )
        CryptoHelper.store_api_key(options.email, api_key_data)
        logger.info("[OAuth] Authentication complete.")
        return AuthenticationResult(
            success=True,
            email=options.email,
            access_token=token_res.access_token,
            account_id=api_key_result.account_id,
        )
    except BannedException as error:
        logger.error("[OAuth] Authentication failed: %s", error)
        raise
    except ProxyRejectedError as error:
        logger.error("[OAuth] Proxy rejected: %s", error)
        if page is not None:
            await _dump_oauth_failure_page(page)
        raise
    except MailboxCodeTimeoutError as exc:
        record_bad_state_email(options.email)
        logger.error(
            "[OAuth] Mailbox code timeout for %s; recorded as bad-state email: %s",
            options.email,
            exc,
        )
        if page is not None:
            await _dump_oauth_failure_page(page)
        return AuthenticationResult(success=False, email=options.email, error=str(exc))
    except Exception as exc:
        logger.exception("[OAuth] Authentication failed: %s", exc)
        if page is not None:
            await _dump_oauth_failure_page(page)
        return AuthenticationResult(success=False, email=options.email, error=str(exc))


async def _authenticate_account(
    account: GeneratedAccountEntry,
    proxy_url: str | None = None,
) -> AuthenticationResult:
    auth_result = await authenticate(
        AuthenticationOptions(
            email=account.email,
            password=account.password,
            mailbox=MailboxSettings.from_env(),
            proxy_url=proxy_url,
        )
    )
    if auth_result.success:
        mark_account_authenticated(account.email)
    else:
        CryptoHelper.remove_bot(account.email)
        mark_account_available_for_auth_retry(account.email)
        if account.email in load_bad_state_emails():
            logger.warning(
                "[OAuth] %s is now in bad-state emails; skipping future scheduler auth",
                account.email,
            )
        else:
            logger.error(auth_result.error)
    return auth_result


async def authenticate_next_available_account(
    email: str | None = None,
    schedule_profile: str | None = None,
) -> AuthenticationResult | None:
    """Authenticate a single available account, or return ``None`` when none remain.

    Used by the quota-driven scheduler, which only ever wants to consume one slot
    of the per-proxy Ankama rate-limit pool at a time.
    """
    available_accounts = load_available_generated_accounts()
    if not available_accounts:
        return None
    account = (
        available_accounts[0]
        if email is None
        else next(
            (account for account in available_accounts if account.email == email),
            None,
        )
    )
    if account is None:
        return None
    profile_id = account.schedule_profile or schedule_profile
    if profile_id is None:
        raise ValueError(f"Generated account {account.email} has no schedule profile")
    profile = ScheduleProfileController().get_profile(profile_id)
    if profile is None:
        raise ValueError(f"Unknown schedule profile {profile_id}")
    proxy = ProxyController().get_proxy(profile.proxy_id)
    if proxy.rejected:
        raise ProxyRejectedError(f"Schedule profile {profile_id} already uses a rejected proxy")
    return await _authenticate_account(account, build_http_proxy_url(proxy))


async def authenticate_available_accounts():
    available_accounts = load_available_generated_accounts()
    for account in available_accounts:
        auth_result = await _authenticate_account(account)
        if not auth_result.success:
            break
        await asyncio.sleep(MIN_DELAY_BETWEEN_ACCOUNTS_SEC)

    logger.info("No more available accounts")


if __name__ == "__main__":
    load_dotenv(ENV_PATH)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    asyncio.run(authenticate_available_accounts())
