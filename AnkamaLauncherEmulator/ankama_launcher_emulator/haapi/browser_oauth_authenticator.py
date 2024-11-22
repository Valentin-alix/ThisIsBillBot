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

import requests
from playwright.async_api import async_playwright

AUTH_URL = "https://auth.ankama.com/login/ankama"
TOKEN_URL = "https://auth.ankama.com/token"
HAAPI_TOKEN_URL = "https://haapi.ankama.com/json/Ankama/v5/Account/CreateToken"
CLIENT_ID = "102"
REDIRECT_URI = "zaap://login"

logger = logging.getLogger(__name__)


def _generate_code_verifier() -> str:
    chars = string.ascii_letters
    length = random.randint(101, 128)
    return "".join(secrets.choice(chars) for _ in range(length))


def _generate_code_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


async def authenticate(username: str, password: str) -> tuple[str, str]:
    """OAuth 2.0 + PKCE via browser (auto-fill). Returns (access_token, game_token)."""
    logger.info("[OAuth] Starting Browser OAuth 2.0 + PKCE...")

    code_verifier = _generate_code_verifier()
    code_challenge = _generate_code_challenge(code_verifier)

    params = urlencode(
        {
            "code_challenge": code_challenge,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "direct": "true",
            "origin_tracker": "https://www.ankama-launcher.com/launcher",
        }
    )
    login_url = f"{AUTH_URL}?{params}"

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
        )
        page = await context.new_page()

        access_token: str | None = None

        async def intercept_response(response):
            nonlocal access_token
            if "/token" in response.url and response.ok:
                body = await response.json()
                token = body.get("access_token")
                if token:
                    access_token = token
                    logger.info("[OAuth] Access token intercepted from network!")

        page.on("response", lambda r: asyncio.ensure_future(intercept_response(r)))

        logger.info("[OAuth] Navigating to login page...")
        await page.goto(login_url, wait_until="networkidle", timeout=60000)

        logger.info("[OAuth] Waiting for WAF challenge...")
        await asyncio.sleep(3)

        logger.info("[OAuth] Auto-filling credentials...")
        await page.wait_for_selector("#ankama-login", timeout=10000)

        await page.focus("#ankama-login")
        await page.keyboard.down("Control")
        await page.keyboard.press("a")
        await page.keyboard.up("Control")
        await page.type("#ankama-login", username, delay=50)

        await page.focus("#ankama-password")
        await page.keyboard.down("Control")
        await page.keyboard.press("a")
        await page.keyboard.up("Control")
        await page.type("#ankama-password", password, delay=50)

        logger.info("[OAuth] Submitting form...")
        await page.click("button[type='submit']")

        logger.info("[OAuth] Waiting for authorization code (up to 120s)...")

        auth_code: str | None = None
        for i in range(120):
            await asyncio.sleep(1)

            if auth_code and not access_token:
                logger.info("[OAuth] Exchanging code for token in browser...")
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
                    token = data.get("access_token")
                    if token:
                        access_token = token
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

        await browser.close()

    if not access_token:
        raise RuntimeError("[OAuth] Failed to get access token after 120s")

    logger.info(f"[OAuth] Access token: {access_token[:20]}...")

    logger.info("[OAuth] Creating game token...")

    response = requests.get(
        HAAPI_TOKEN_URL,
        params={"game": 1},
        headers={"apikey": access_token, "User-Agent": "Zaap 3.13.18"},
    )
    response.raise_for_status()
    game_token = response.json().get("token")

    if not game_token:
        raise RuntimeError("[OAuth] Failed to create game token")

    logger.info(f"[OAuth] Game token: {game_token[:20]}...")
    return access_token, game_token


if __name__ == "__main__":
    asyncio.run(authenticate("test", "testpassword"))
