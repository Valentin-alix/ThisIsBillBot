"""Launcher (Zaap) OAuth login URL helpers for ``auth.ankama.com``."""

from urllib.parse import urlencode

from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from ankama_launcher_emulator_premium.web._client.pkce import (
    generate_code_challenge,
    generate_code_verifier,
)

AUTH_URL = "https://auth.ankama.com/login/ankama"
CLIENT_ID = "102"
LOGIN_REDIRECT_URI = "zaap://login"
ORIGIN_TRACKER = "https://www.ankama-launcher.com/launcher"


def build_login_url(code_challenge: str) -> str:
    params = urlencode(
        {
            "code_challenge": code_challenge,
            "redirect_uri": LOGIN_REDIRECT_URI,
            "client_id": CLIENT_ID,
            "direct": "true",
            "origin_tracker": ORIGIN_TRACKER,
        }
    )
    return f"{AUTH_URL}?{params}"


async def get_registration_state(page: Page) -> str | None:
    verifier = generate_code_verifier()
    await page.goto(
        build_login_url(generate_code_challenge(verifier)),
        wait_until="domcontentloaded",
        timeout=60_000,
    )
    try:
        state = await page.locator('input[name="state"]').first.input_value(timeout=10_000)
    except PlaywrightTimeoutError:
        return None
    return state
