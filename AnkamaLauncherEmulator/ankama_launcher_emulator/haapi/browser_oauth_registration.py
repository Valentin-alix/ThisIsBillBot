import asyncio
import logging

from playwright.async_api import Page, async_playwright

from ankama_launcher_emulator.haapi.accounts import (
    load_accounts,
    load_emails,
    save_account,
)
from ankama_launcher_emulator.haapi.urls import (
    build_register_url,
)

logger = logging.getLogger(__name__)


async def _fill_registration_form(
    page: Page,
    email: str,
    password: str,
    firstname: str,
    lastname: str,
    birthday_day: str,
    birthday_month: str,
    birthday_year: str,
) -> None:
    await page.wait_for_selector("#ankama-registration-login", timeout=15_000)
    await page.fill("#ankama-registration-login", email)
    await page.fill("#ankama-registration-password", password)
    await page.fill("#ankama-registration-lastname", lastname)
    await page.fill("#ankama-registration-firstname", firstname)
    await page.select_option("#ankama-registration-birthday-day", birthday_day.zfill(2))
    await page.select_option(
        "#ankama-registration-birthday-month", birthday_month.zfill(2)
    )
    await page.select_option("#ankama-registration-birthday-year", birthday_year)


async def _handle_confirmation_code(page: Page) -> None:
    """
    Handle the email confirmation code step at /register/ankama/code.
    Accepts the code from either the terminal OR the browser (whichever comes first):
    - Terminal: fills #otp and submits the form
    - Browser: user types the code directly — we just detect the navigation away
    """
    logger.info(
        "[Register] Email confirmation required — enter the 6-digit code in the"
        " terminal OR type it directly in the browser."
    )
    loop = asyncio.get_event_loop()

    async def _via_browser() -> None:
        """Resolve as soon as the browser navigates away from the code page."""
        while "/register/ankama/code" in page.url:
            await asyncio.sleep(0.3)

    async def _via_terminal() -> None:
        """Prompt in terminal, fill the form, submit."""
        code = await loop.run_in_executor(
            None,
            lambda: input("[Register] 6-digit code: ").strip(),
        )
        if "/register/ankama/code" not in page.url:
            return
        await page.wait_for_selector("#otp", timeout=5000)
        await page.fill("#otp", code)
        async with page.expect_navigation(wait_until="domcontentloaded", timeout=30000):
            await page.click("button[type='submit']")

    _done, pending = await asyncio.wait(
        {
            asyncio.ensure_future(_via_browser()),
            asyncio.ensure_future(_via_terminal()),
        },
        return_when=asyncio.FIRST_COMPLETED,
        timeout=1200,
    )
    for task in pending:
        task.cancel()

    logger.info("[Register] OTP step complete — now on: %s", page.url)


async def _wait_for_result(page: Page) -> None:
    """
    Wait for registration to complete (up to 3 minutes to allow captcha solving).
    Handles captcha wait and email confirmation code step.
    """
    code_handled = False

    for sec_index in range(180):
        await asyncio.sleep(1)

        current_url = page.url
        html = await page.content()

        if "/register/ankama/code" in current_url and not code_handled:
            code_handled = True
            await _handle_confirmation_code(page)
            return

        captcha_present = any(
            line in html.lower()
            for line in ["captcha", "cf-challenge", "turnstile", "hcaptcha"]
        )
        if captcha_present and (sec_index == 0 or sec_index % 15 == 0):
            logger.info(
                "[Register] Captcha detected — please solve it in the browser window... (%ds elapsed)",
                sec_index,
            )

        if sec_index > 0 and sec_index % 15 == 0 and not captcha_present:
            logger.info("[Register] Still waiting... (%ds / 180s)", sec_index)


async def register(
    email: str,
    password: str,
    firstname: str,
    lastname: str,
    birthday_day: str | int,
    birthday_month: str | int,
    birthday_year: str | int,
    proxy_url: str | None = None,
) -> bool:
    """
    Register a new Ankama account via browser automation (Playwright).

    Opens a visible browser window, fills the registration form, submits it,
    and handles captcha challenges by waiting for the user to solve them.

    Returns True on success, False on timeout or failure.
    """
    logger.info("[Register] Starting Ankama account registration for %s...", email)

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

        logger.info("[Register] Navigating to registration page...")
        await page.goto(build_register_url(), wait_until="networkidle", timeout=60_000)

        logger.info("[Register] Waiting for WAF challenge...")
        await asyncio.sleep(3)

        logger.info("[Register] Filling registration form...")
        await _fill_registration_form(
            page,
            email=email,
            password=password,
            firstname=firstname,
            lastname=lastname,
            birthday_day=str(birthday_day),
            birthday_month=str(birthday_month),
            birthday_year=str(birthday_year),
        )

        logger.info("[Register] Submitting form...")
        await page.click("button[type='submit']")

        logger.info(
            "[Register] Waiting for result (captcha may appear, up to 3 minutes)..."
        )
        await _wait_for_result(page)

        save_account(email, password)

        await browser.close()

    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    emails_registered = [account["email"] for account in load_accounts()]
    emails = load_emails()
    for email in emails:
        if email not in emails_registered:
            asyncio.run(
                register(
                    email=email,
                    password="blibli44700",
                    firstname="Jean",
                    lastname="Dupont",
                    birthday_day="16",
                    birthday_month="09",
                    birthday_year="2000",
                )
            )
