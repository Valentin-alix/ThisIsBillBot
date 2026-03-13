import logging
import re
from enum import StrEnum

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from ankama_launcher_emulator.haapi.urls import (
    ANKAMA_STORE_DOFUS_UNITY_INGAME_SHOP_KEY,
    ANKAMA_STORE_OVERLAY_AUTH_URL,
)
from ankama_launcher_emulator.interfaces.billing_address import (
    generate_random_billing_address,
)
from ankama_launcher_emulator.web._client.browser import (
    launch_browser_context,
)

logger = logging.getLogger(__name__)

_INTERACTION_TIMEOUT_MILLISECONDS = 30_000
_CONTINUE_PROMPT_TIMEOUT_MILLISECONDS = 5_000
_NEW_TAB_TIMEOUT_MILLISECONDS = 15_000
_PAYMENT_TIMEOUT_MILLISECONDS = 180_000
_ADDRESS_ID_PATTERN = re.compile(r"address-id=(\d+)")
_PAYSAFECARD_PAYMENT_MODE_ID = "OF"


class PaysafecardPurchaseError(Exception):
    pass


class PaysafecardPaymentOutcome(StrEnum):
    SUCCEEDED = "succeeded"
    INVALID_PIN = "invalid_pin"
    INSUFFICIENT_BALANCE = "insufficient_balance"
    REJECTED = "rejected"
    AMBIGUOUS = "ambiguous"


async def _accept_cookies_if_present(page: Page) -> None:
    accept_button = page.locator("#onetrust-accept-btn-handler")
    try:
        await accept_button.wait_for(state="visible", timeout=_CONTINUE_PROMPT_TIMEOUT_MILLISECONDS)
    except PlaywrightTimeoutError:
        return
    await accept_button.click()


async def _accept_connection_prompt_if_present(page: Page) -> None:
    continue_button = page.get_by_role("button", name=re.compile("continuer", re.IGNORECASE))
    try:
        await continue_button.wait_for(state="visible", timeout=_CONTINUE_PROMPT_TIMEOUT_MILLISECONDS)
    except PlaywrightTimeoutError:
        return
    await continue_button.click()


async def _extract_billing_address_id(page: Page) -> str | None:
    match = _ADDRESS_ID_PATTERN.search(await page.content())
    return match.group(1) if match else None


async def _ensure_billing_address(page: Page, login: str) -> None:
    address = generate_random_billing_address(login)
    await page.goto(
        "https://store.ankama.com/fr/direct-cart/billing/address/create",
        wait_until="domcontentloaded",
    )
    await page.fill('input[name="address[name]"]', "domicile")
    await page.fill('input[name="address[firstname]"]', address.firstname)
    await page.fill('input[name="address[lastname]"]', address.lastname)
    await page.fill('input[name="address[address]"]', address.address)
    await page.fill('input[name="address[zipcode]"]', address.zipcode)
    await page.fill('input[name="address[city]"]', address.city)
    await page.get_by_role("button", name="Enregistrer").click()
    await page.wait_for_url("**/direct-cart/payment-choice**")


async def _submit_order(page: Page) -> None:
    await page.check(f'input[name="payment_mode_id"][value="{_PAYSAFECARD_PAYMENT_MODE_ID}"]')
    await page.get_by_role("button", name="Valider et payer").click()
    await page.wait_for_url("**/payment/po/**")


async def _open_alternative_payment_page(page: Page) -> Page:
    try:
        await page.wait_for_load_state("networkidle", timeout=_NEW_TAB_TIMEOUT_MILLISECONDS)
    except PlaywrightTimeoutError:
        pass
    try:
        async with page.context.expect_page(timeout=_NEW_TAB_TIMEOUT_MILLISECONDS) as new_page_info:
            await page.locator("alternative-payment a", has_text="Payer").click()
        payment_page = await new_page_info.value
        await payment_page.wait_for_load_state("domcontentloaded")
        return payment_page
    except PlaywrightTimeoutError:
        return page


async def _enter_pin_and_submit(page: Page, pin: str) -> None:
    await page.fill("#classicPin-addPinField", pin)
    accept_terms = page.locator("#acceptTerms")
    if not await accept_terms.is_checked():
        await page.locator('label[for="acceptTerms"]').click()
    await page.locator("#payBtn").click()


async def _wait_for_payment_outcome(*pages: Page) -> PaysafecardPaymentOutcome:
    success_pattern = re.compile(
        r"(paiement (réussi|accepté)|payment (successful|accepted)|merci pour votre achat|thank you)",
        re.IGNORECASE,
    )
    invalid_pin_pattern = re.compile(r"(code invalide|invalid pin)", re.IGNORECASE)
    insufficient_balance_pattern = re.compile(r"(solde insuffisant|insufficient balance)", re.IGNORECASE)
    rejected_pattern = re.compile(r"(paiement refusé|payment declined)", re.IGNORECASE)
    for _attempt_index in range(_PAYMENT_TIMEOUT_MILLISECONDS // 1_000):
        for page in pages:
            if page.is_closed():
                continue
            if await page.get_by_text(success_pattern, exact=False).count() > 0:
                return PaysafecardPaymentOutcome.SUCCEEDED
            if await page.get_by_text(invalid_pin_pattern, exact=False).count() > 0:
                return PaysafecardPaymentOutcome.INVALID_PIN
            if await page.get_by_text(insufficient_balance_pattern, exact=False).count() > 0:
                return PaysafecardPaymentOutcome.INSUFFICIENT_BALANCE
            if await page.get_by_text(rejected_pattern, exact=False).count() > 0:
                return PaysafecardPaymentOutcome.REJECTED
        await pages[0].wait_for_timeout(1_000)
    return PaysafecardPaymentOutcome.AMBIGUOUS


async def purchase_with_paysafecard(
    *,
    shop_access_token: str,
    cart_id: str,
    pin: str,
    login: str,
    proxy_url: str | None,
) -> PaysafecardPaymentOutcome:
    overlay_url = (
        f"{ANKAMA_STORE_OVERLAY_AUTH_URL}?token={shop_access_token}"
        f"&shopkey={ANKAMA_STORE_DOFUS_UNITY_INGAME_SHOP_KEY}&cart={cart_id}"
    )
    async with launch_browser_context(proxy_url=proxy_url) as browser_context:
        page = await browser_context.new_page()
        page.set_default_timeout(_INTERACTION_TIMEOUT_MILLISECONDS)
        payment_page = page
        try:
            await page.goto(overlay_url, wait_until="domcontentloaded")
            await _accept_connection_prompt_if_present(page)
            await page.wait_for_url("**/direct-cart/payment-choice**")
            if await _extract_billing_address_id(page) is None:
                await _ensure_billing_address(page, login)
            await _submit_order(page)
            payment_page = await _open_alternative_payment_page(page)
            await _accept_cookies_if_present(payment_page)
            await _enter_pin_and_submit(payment_page, pin)
            return await _wait_for_payment_outcome(payment_page, page)
        except (PlaywrightTimeoutError, PlaywrightError) as error:
            raise PaysafecardPurchaseError(
                f"Unable to complete paysafecard purchase for {login}: {error}"
            ) from error
