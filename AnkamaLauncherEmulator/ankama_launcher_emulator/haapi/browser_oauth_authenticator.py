import asyncio
import base64
import hashlib
import json
import logging
import random
import re
import secrets
import string
from typing import cast
from urllib.parse import urlencode

from playwright.async_api import Page, async_playwright

from ankama_launcher_emulator.decrypter.crypto_helper import CryptoHelper
from ankama_launcher_emulator.haapi.haapi import (
    Haapi,
    refresh_api_key_from_oauth,
)
from ankama_launcher_emulator.interfaces.deciphered_cert import DecipheredCertifDatas

AUTH_URL = "https://auth.ankama.com/login/ankama"
TOKEN_URL = "https://auth.ankama.com/token"
HAAPI_TOKEN_URL = "https://haapi.ankama.com/json/Ankama/v5/Account/CreateToken"
CLIENT_ID = "102"
REDIRECT_URI = "zaap://login"
ZAAP_GAME_ID = 102

logger = logging.getLogger(__name__)


def _generate_code_verifier() -> str:
    length = random.randint(101, 128)
    return "".join(secrets.choice(string.ascii_letters) for _ in range(length))


def _generate_code_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def _build_login_url(code_challenge: str) -> str:
    params = urlencode(
        {
            "code_challenge": code_challenge,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "direct": "true",
            "origin_tracker": "https://www.ankama-launcher.com/launcher",
        }
    )
    return f"{AUTH_URL}?{params}"


async def _fill_credentials(page: Page, username: str, password: str) -> None:
    await page.wait_for_selector("#ankama-login", timeout=10000)
    for field_id, value in [
        ("#ankama-login", username),
        ("#ankama-password", password),
    ]:
        await page.focus(field_id)
        await page.keyboard.down("Control")
        await page.keyboard.press("a")
        await page.keyboard.up("Control")
        await page.type(field_id, value, delay=50)


async def _exchange_code_for_token(
    page: Page, auth_code: str, code_verifier: str
) -> tuple[str | None, str | None]:
    body = urlencode(
        {
            "grant_type": "authorization_code",
            "code": auth_code,
            "code_verifier": code_verifier,
            "client_id": CLIENT_ID,
            "redirect_uri": REDIRECT_URI,
        }
    )
    result = await page.evaluate(
        f"""
        (async () => {{
            const response = await fetch('{TOKEN_URL}', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
                body: '{body}'
            }});
            return await response.text();
        }})()
        """
    )
    if result:
        data = json.loads(result)
        return data.get("access_token"), data.get("refresh_token")
    return None, None


async def _wait_for_tokens(page: Page, code_verifier: str) -> tuple[str, str]:
    access_token: str | None = None
    oauth_refresh_token: str | None = None

    async def intercept_response(response):
        nonlocal access_token, oauth_refresh_token
        if "/token" in response.url and response.ok:
            body = await response.json()
            token = body.get("access_token")
            if token:
                access_token = token
                oauth_refresh_token = body.get("refresh_token")
                logger.info("[OAuth] Access token intercepted from network!")

    page.on("response", lambda r: asyncio.ensure_future(intercept_response(r)))

    auth_code: str | None = None
    for i in range(120):
        await asyncio.sleep(1)

        if auth_code and not access_token:
            logger.info("[OAuth] Exchanging code for token in browser...")
            access_token, oauth_refresh_token = await _exchange_code_for_token(
                page, auth_code, code_verifier
            )
            if access_token:
                logger.info("[OAuth] Token exchange successful!")
            break

        current_url = page.url
        if current_url.startswith("zaap://login?code="):
            auth_code = current_url.replace("zaap://login?code=", "").split("&")[0]
            logger.info(f"[OAuth] Auth code found in URL: {auth_code[:20]}...")
            continue

        html = await page.content()
        if "zaap://login?code=" in html:
            match = re.search(r"zaap://login\?code=([^\"'\s&]+)", html)
            if match:
                auth_code = cast(str, match.group(1))
                logger.info(f"[OAuth] Auth code found in HTML: {auth_code[:20]}...")
                continue

        if i > 0 and i % 15 == 0:
            logger.info(f"[OAuth] Still waiting... ({i}s / 120s)")

    if not access_token or not oauth_refresh_token:
        raise RuntimeError(
            "[OAuth] Failed to get access token or refresh token after 120s"
        )

    return access_token, oauth_refresh_token


async def _browser_login(
    username: str,
    password: str,
    code_verifier: str,
    login_url: str,
    proxy_url: str | None = None,
) -> tuple[str, str]:
    async with async_playwright() as _client:
        browser = await _client.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            proxy={"server": proxy_url} if proxy_url else None,
        )
        page = await context.new_page()

        logger.info("[OAuth] Navigating to login page...")
        await page.goto(login_url, wait_until="networkidle", timeout=60000)

        logger.info("[OAuth] Waiting for WAF challenge...")
        await asyncio.sleep(3)

        logger.info("[OAuth] Auto-filling credentials...")
        await _fill_credentials(page, username, password)

        logger.info("[OAuth] Submitting form...")
        await page.click("button[type='submit']")

        logger.info("[OAuth] Waiting for authorization code (up to 120s)...")
        access_token, oauth_refresh_token = await _wait_for_tokens(page, code_verifier)

        await browser.close()

    return access_token, oauth_refresh_token


def _handle_security(haapi: Haapi, account_info: dict) -> DecipheredCertifDatas | None:
    security = account_info.get("security", []) or []
    certificate = None

    if "SHIELD" in security:
        logger.info("[OAuth] Shield required, requesting security code via email...")
        domain = haapi.get_security_code("EMAIL")
        logger.info(f"[OAuth] Security code sent to your email ({domain})")
        shield_code = input("[OAuth] Enter Shield code: ").strip()
        certificate = haapi.validate_code(shield_code, ZAAP_GAME_ID)
    elif "OTP" in security:
        logger.info("[OAuth] OTP Shield required, enter your authenticator code...")
        otp_code = input("[OAuth] Enter OTP code: ").strip()
        certificate = haapi.validate_otp(otp_code, ZAAP_GAME_ID)

    if certificate:
        logger.info(f"[OAuth] Certificate obtained (id={certificate['id']})")
        CryptoHelper.store_certificate(certificate)

    return certificate


async def authenticate(
    username: str,
    password: str,
    interface_ip: str | None = None,
    proxy_url: str | None = None,
) -> str:
    """OAuth 2.0 + PKCE via browser (auto-fill). Returns access_token.

    Args:
        interface_ip: bind HAAPI HTTP requests to this network interface IP.
        proxy_url: proxy for both the browser (Playwright) and HAAPI HTTP requests,
                   e.g. ``socks5://user:pass@host:port``.
    """
    logger.info("[OAuth] Starting Browser OAuth 2.0 + PKCE...")

    code_verifier = _generate_code_verifier()
    login_url = _build_login_url(_generate_code_challenge(code_verifier))

    access_token, oauth_refresh_token = await _browser_login(
        username, password, code_verifier, login_url, proxy_url=proxy_url
    )
    logger.info(f"[OAuth] Access token: {access_token[:20]}...")

    logger.info("[OAuth] Exchanging OAuth tokens for HAAPI API key...")
    api_key_result = refresh_api_key_from_oauth(access_token, oauth_refresh_token)
    api_key = api_key_result["key"]
    account_id = api_key_result["account_id"]
    haapi_refresh_token = api_key_result["refresh_token"]
    logger.info(f"[OAuth] HAAPI API key obtained for account_id={account_id}")

    haapi = Haapi(
        api_key=api_key,
        login=username,
        interface_ip=interface_ip,
        proxy_url=proxy_url,
    )
    account_info = haapi.signOnWithApiKey(ZAAP_GAME_ID)
    certificate = _handle_security(haapi, account_info)

    CryptoHelper.store_api_key(
        username,
        {
            "key": api_key,
            "provider": "ankama",
            "refreshToken": haapi_refresh_token,
            "isStayLoggedIn": True,
            "accountId": account_id,
            "login": username,
            "certificate": certificate if certificate else {},
            "refreshDate": 0,
        },
    )
    logger.info("[OAuth] Authentication complete.")

    return access_token


if __name__ == "__main__":
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)
    asyncio.run(authenticate("PcServ_Blibli_2_0@outlook.fr", "blibli44700"))
