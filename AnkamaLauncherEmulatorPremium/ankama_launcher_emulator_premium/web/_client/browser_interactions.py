import logging
import random
from asyncio import sleep
from dataclasses import dataclass

from playwright.async_api import Locator, Page
from playwright.async_api import TimeoutError as PlaywrightTimeoutError

COOKIE_ACCEPT_SELECTORS = (
    "button:has-text('Accepter')",
    "button:has-text('Tout accepter')",
    "button:has-text('Accept all')",
    "button:has-text('I accept')",
    "#didomi-notice-agree-button",
    "#onetrust-accept-btn-handler",
)
FORM_ERROR_SELECTORS = (
    ".alert-danger",
    ".ak-alert-danger",
    ".ak-error",
    ".ak-field-error",
    ".form-error",
    ".has-error .help-block",
    ".has-error",
    "[role='alert']",
    "[aria-invalid='true']",
)

ANTIBOT_MARKERS = {
    "captcha": "captcha",
    "cloudflare challenge": "cf-challenge",
    "turnstile": "turnstile",
    "hcaptcha": "hcaptcha",
    "aws waf": "aws-waf",
}


def is_waf_or_cloudfront_block(*, status_code: int | None, content: str) -> bool:
    """Recognize a server-side WAF block without mistaking the WAF SDK for one."""
    lower_content = content.casefold()
    if lower_content.startswith("waf/cloudfront blocked"):
        return True
    return (
        status_code in {None, 403}
        and "request blocked" in lower_content
        and ("cloudfront" in lower_content or "aws waf" in lower_content)
    )


@dataclass(frozen=True)
class AntibotDetection:
    name: str
    marker: str


async def human_wait(*, min_seconds: float, max_seconds: float) -> None:
    await sleep(random.uniform(min_seconds, max_seconds))


async def human_click_locator(locator: Locator) -> None:
    await locator.click()


async def human_click_selector(page: Page, selector: str) -> None:
    await human_click_locator(page.locator(selector).first)


async def human_type_locator(locator: Locator, text: str) -> None:
    await locator.type(text, delay=50)


async def human_type_selector(page: Page, selector: str, text: str) -> None:
    await human_type_locator(page.locator(selector).first, text)


async def accept_cookies_if_present(page: Page) -> bool:
    for selector in COOKIE_ACCEPT_SELECTORS:
        button = page.locator(selector).first
        if await button.count() == 0:
            continue
        try:
            await button.click(timeout=2_000)
        except PlaywrightTimeoutError:
            continue
        return True
    return False


def detect_antibot_marker(html: str) -> AntibotDetection | None:
    lower_html = html.lower()
    for name, marker in ANTIBOT_MARKERS.items():
        if marker in lower_html:
            return AntibotDetection(name=name, marker=marker)
    return None


async def detect_antibot(page: Page) -> AntibotDetection | None:
    return detect_antibot_marker(await page.content())


async def visible_form_error_texts(
    page: Page, selectors: tuple[str, ...] = FORM_ERROR_SELECTORS
) -> tuple[str, ...]:
    errors: list[str] = []
    for selector in selectors:
        texts = await page.locator(selector).all_inner_texts()
        for text in texts:
            compact_text = " ".join(text.split())
            if compact_text and compact_text not in errors:
                errors.append(compact_text)
    return tuple(errors)


async def wait_for_antibot_challenge(
    page: Page,
    *,
    seconds: float,
    logger: logging.Logger,
    log_prefix: str,
) -> AntibotDetection | None:
    detection = await detect_antibot(page)
    if detection is not None:
        logger.info(
            "%s %s detected; solve it in the browser window.",
            log_prefix,
            detection.name,
        )
    await sleep(seconds)
    return detection
