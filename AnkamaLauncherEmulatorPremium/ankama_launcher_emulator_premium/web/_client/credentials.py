import logging

from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from ankama_launcher_emulator_premium.exceptions import BannedException
from ankama_launcher_emulator_premium.web._client.browser_interactions import (
    human_click_selector,
    human_type_selector,
    human_wait,
)

logger = logging.getLogger()


async def fill_credentials_and_submit(page: Page, username: str, password: str) -> None:
    await page.wait_for_selector("#ankama-login", timeout=10_000)
    for field_id, value in [
        ("#ankama-login", username),
        ("#ankama-password", password),
    ]:
        await human_type_selector(page, field_id, value)

    await human_wait(min_seconds=0.3, max_seconds=0.6)

    logger.info("[OAuth] Submitting form...")
    await human_click_selector(page, "button[type='submit']")

    await page.wait_for_load_state("domcontentloaded", timeout=15_000)

    alert_ban = page.locator("div:has-text('votre compte est banni')").first
    try:
        await alert_ban.wait_for(state="visible", timeout=2_000)
    except PlaywrightTimeoutError:
        pass
    else:
        raise BannedException(f"Account {username} is banned...")

    await human_wait(min_seconds=0.3, max_seconds=0.6)
