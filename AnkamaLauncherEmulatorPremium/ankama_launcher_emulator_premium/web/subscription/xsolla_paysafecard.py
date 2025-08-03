import re
from enum import StrEnum

from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from ankama_launcher_emulator_premium.consts import DEBUG_DUMPS_DIR
from ankama_launcher_emulator_premium.web._client.browser import (
    launch_browser_context,
)
from ankama_launcher_emulator_premium.web.debug_utils import dump_page_html

_PAYSTATION_URL = "https://secure.xsolla.com/paystation4/?token={token}"
_INTERACTION_TIMEOUT_MILLISECONDS = 30_000
_PAYMENT_TIMEOUT_MILLISECONDS = 180_000


class XsollaPaymentOutcome(StrEnum):
    SUCCEEDED = "succeeded"
    REJECTED = "rejected"
    AMBIGUOUS = "ambiguous"


async def pay_with_paysafecard(
    *,
    token: str,
    pin: str,
    login: str,
    proxy_url: str | None,
) -> XsollaPaymentOutcome:
    async with launch_browser_context(
        headless=False,
        proxy_url=proxy_url,
        channel="chrome",
    ) as browser_context:
        page = await browser_context.new_page()
        page.set_default_timeout(_INTERACTION_TIMEOUT_MILLISECONDS)
        await page.goto(_PAYSTATION_URL.format(token=token), wait_until="domcontentloaded")
        try:
            await _select_paysafecard(page)
            await _enter_pin_and_submit(page, pin)
            return await _wait_for_payment_outcome(page)
        except PlaywrightTimeoutError:
            await _dump_ambiguous_payment(page, login)
            return XsollaPaymentOutcome.AMBIGUOUS


async def _select_paysafecard(page: Page) -> None:
    paysafecard_pattern = re.compile(r"paysafe\s*card", re.IGNORECASE)
    payment_method = page.get_by_text(paysafecard_pattern, exact=False).first
    await payment_method.wait_for(state="visible")
    await payment_method.click()


async def _enter_pin_and_submit(page: Page, pin: str) -> None:
    pin_pattern = re.compile(r"(paysafe|pin|code)", re.IGNORECASE)
    pin_input = page.get_by_label(pin_pattern).first
    if await pin_input.count() == 0:
        pin_input = page.get_by_placeholder(pin_pattern).first
    await pin_input.fill(pin)
    submit_pattern = re.compile(
        r"(payer|pay|continuer|continue|confirmer|confirm)",
        re.IGNORECASE,
    )
    await page.get_by_role("button", name=submit_pattern).last.click()


async def _wait_for_payment_outcome(page: Page) -> XsollaPaymentOutcome:
    success_pattern = re.compile(
        r"(paiement réussi|payment successful|merci pour votre achat|thank you)",
        re.IGNORECASE,
    )
    rejected_pattern = re.compile(
        r"(paiement refusé|payment declined|code invalide|invalid pin|solde insuffisant)",
        re.IGNORECASE,
    )
    for _attempt_index in range(_PAYMENT_TIMEOUT_MILLISECONDS // 1_000):
        if await page.get_by_text(success_pattern, exact=False).count() > 0:
            return XsollaPaymentOutcome.SUCCEEDED
        if await page.get_by_text(rejected_pattern, exact=False).count() > 0:
            return XsollaPaymentOutcome.REJECTED
        await page.wait_for_timeout(1_000)
    return XsollaPaymentOutcome.AMBIGUOUS


async def _dump_ambiguous_payment(page: Page, login: str) -> None:
    safe_login = re.sub(r"[^A-Za-z0-9_.-]", "_", login)
    await dump_page_html(f"xsolla_paysafecard_{safe_login}", page)
    DEBUG_DUMPS_DIR.mkdir(parents=True, exist_ok=True)
    await page.screenshot(
        path=str(DEBUG_DUMPS_DIR / f"xsolla_paysafecard_{safe_login}.png"),
        full_page=True,
    )
