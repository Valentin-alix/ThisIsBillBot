import asyncio
import logging
import random
from dataclasses import dataclass
from datetime import UTC, datetime

from dotenv import load_dotenv
from playwright.async_api import Page

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.consts import ENV_PATH, SONJI_API_KEY
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.bot_storage import (
    BotStorageController,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.mail_account import (
    MailAccountController,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.proxy import ProxyController
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.schedule_profile import (
    ScheduleProfileController,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.haapi.urls import build_register_url
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.utils.proxy import build_http_proxy_url
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.browser import (
    launch_browser_context,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.browser_interactions import (
    detect_antibot_marker,
    human_click_selector,
    human_type_selector,
    human_wait,
    visible_form_error_texts,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.mail_providers.base import (
    MailboxCodeTimeoutError,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.mail_providers.config import (
    resolve_mail_provider,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.mail_providers.manual import (
    wait_for_code_with_manual_fallback,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web.auth.identity import (
    DEFAULT_PASSWORD,
    random_identity,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web.auth.models import (
    RegistrationOptions,
    RegistrationResult,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web.auth.oauth_state import (
    get_registration_state,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web.debug_utils import dump_page_html

logger = logging.getLogger(__name__)

MIN_DELAY_BETWEEN_ACCOUNTS_SEC = 8 * 60
MAX_DELAY_BETWEEN_ACCOUNTS_SEC = 20 * 60
REGISTRATION_FORM_READY_MARKERS = (
    'id="ankama-registration-login"',
    'id="ankama-registration-password"',
    'id="ankama-registration-birthday-day"',
    'id="ankama-registration-birthday-month"',
    'id="ankama-registration-birthday-year"',
    'type="submit"',
)


@dataclass(frozen=True)
class _RegistrationWaitResult:
    success: bool
    reason: str | None = None
    form_errors: tuple[str, ...] = ()
    antibot_marker: str | None = None


def is_aws_waf_marker(marker: str | None) -> bool:
    return marker in {"aws waf", "aws waf block"}


async def register_account(options: RegistrationOptions) -> RegistrationResult:
    logger.info("[Register] Starting Ankama account registration for %s...", options.email)

    async with launch_browser_context(
        headless=options.headless, proxy_url=options.proxy_url, channel="chrome"
    ) as context:
        page = await context.new_page()
        try:
            state = await get_registration_state(page)
            register_url = build_register_url(state)
            await page.goto(
                register_url,
                wait_until="networkidle",
                timeout=20_000,
            )
            await _wait_for_registration_form_ready(page, options)
            await human_wait(min_seconds=3, max_seconds=4)
            wait_result = await _submit_registration_attempt(page, options)

            if wait_result.success:
                logger.info("[Register] Registration completed for %s", options.email)
                BotStorageController().save_account(
                    options.email,
                    options.password,
                    schedule_profile=options.schedule_profile,
                )
                logger.info(f"Successfully saved account {options.email, options.password}")
                return RegistrationResult(True, options.email, options.password, page.url)
            await dump_page_html("register_incomplete", page)
            error = wait_result.reason or "registration did not complete before timeout"
            logger.error(
                "[Register] Registration failed for %s at %s: %s",
                options.email,
                page.url,
                error,
            )
            return RegistrationResult(
                False,
                options.email,
                options.password,
                page.url,
                error,
                wait_result.antibot_marker,
            )
        except Exception as exc:
            logger.exception("[Register] Failure at URL %s", page.url)
            await dump_page_html("register_failure", page)
            return RegistrationResult(False, options.email, options.password, page.url, str(exc))


async def _submit_registration_attempt(page: Page, options: RegistrationOptions) -> _RegistrationWaitResult:
    started_at = datetime.now(UTC)
    await _fill_registration_form(page, options)
    await human_click_selector(page, "button[type='submit']")
    logger.info("[Register] Clicked submit, URL: %s", page.url)
    return await _wait_for_result(page, options, started_at)


async def _fill_registration_form(page: Page, options: RegistrationOptions) -> None:
    identity = options.identity
    await page.wait_for_selector("#ankama-registration-login", timeout=15_000)

    for field_id, value in [
        ("#ankama-registration-login", options.email),
        ("#ankama-registration-password", options.password),
        ("#ankama-registration-lastname", identity.lastname),
        ("#ankama-registration-firstname", identity.firstname),
    ]:
        await human_type_selector(page, field_id, value)
        await human_wait(min_seconds=0.3, max_seconds=0.5)

    for field_id, value in [
        ("#ankama-registration-birthday-day", identity.birthday_day.zfill(2)),
        ("#ankama-registration-birthday-month", identity.birthday_month.zfill(2)),
        ("#ankama-registration-birthday-year", identity.birthday_year),
    ]:
        await human_click_selector(page, field_id)
        await page.select_option(field_id, value)
        await human_wait(min_seconds=0.3, max_seconds=0.5)


async def _wait_for_registration_form_ready(page: Page, options: RegistrationOptions) -> None:
    timeout_seconds = _registration_timeout_seconds(options)
    for second_index in range(timeout_seconds):
        html = await page.content()
        if _is_registration_form_ready(html):
            return

        antibot_detection = detect_antibot_marker(html)
        if antibot_detection is not None and (second_index == 0 or second_index % 15 == 0):
            logger.info(
                "[Register] %s detected before form fill; solve it in the browser window. (%ds elapsed)",
                antibot_detection.name,
                second_index,
            )
        elif second_index > 0 and second_index % 15 == 0:
            logger.info(
                "[Register] Waiting for registration form... (%ds / %ds)",
                second_index,
                timeout_seconds,
            )
        await asyncio.sleep(1)
    raise TimeoutError(f"registration form did not become ready before timeout at {page.url}")


async def _submit_confirmation_code(page: Page, code: str) -> None:
    if await page.locator("#otp").count() > 0:
        await human_type_selector(page, "#otp", code)
    else:
        for index, digit in enumerate(code, start=1):
            selector = f'input[name="n{index}"]'
            if await page.locator(selector).count() > 0:
                await human_type_selector(page, selector, digit)
    async with page.expect_navigation(wait_until="domcontentloaded", timeout=30_000):
        await human_click_selector(page, "button[type='submit']")


async def _handle_confirmation_code(page: Page, options: RegistrationOptions, started_at: datetime) -> bool:
    logger.info("[Register] Email confirmation required.")

    async def via_browser() -> bool:
        while "/register/ankama/code" in page.url:
            await asyncio.sleep(0.3)
        return True

    async def via_mailbox() -> bool:
        code = await wait_for_code_with_manual_fallback(
            options.mail_provider,
            since=started_at,
            timeout_seconds=options.confirmation_timeout_seconds,
        )
        if code is None:
            raise MailboxCodeTimeoutError(
                f"Timed out waiting for registration confirmation code for {options.email}"
            )
        if "/register/ankama/code" not in page.url:
            return False
        await _submit_confirmation_code(page, code)
        return True

    tasks = [
        asyncio.create_task(via_browser()),
        asyncio.create_task(via_mailbox()),
    ]
    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED,
        timeout=options.confirmation_timeout_seconds,
    )
    for task in pending:
        task.cancel()
    if pending:
        await asyncio.gather(*pending, return_exceptions=True)
    for task in done:
        exception = task.exception()
        if isinstance(exception, MailboxCodeTimeoutError):
            MailAccountController().record_bad_state(options.email)
            raise exception
    return any(task.result() for task in done if not task.cancelled())


async def _wait_for_result(
    page: Page, options: RegistrationOptions, started_at: datetime
) -> _RegistrationWaitResult:
    code_handled = False
    timeout_seconds = _registration_timeout_seconds(options)
    for second_index in range(timeout_seconds):
        await asyncio.sleep(0.5)
        current_url = page.url
        html = await page.content()

        if "/register/ankama/code" in current_url and not code_handled:
            code_handled = True
            confirmation_handled = await _handle_confirmation_code(page, options, started_at)
            if confirmation_handled:
                return _RegistrationWaitResult(success=True)
            return _RegistrationWaitResult(
                success=False,
                reason="email confirmation code was not submitted or accepted",
            )

        antibot_detection = detect_antibot_marker(html)
        if antibot_detection is not None:
            reason = f"registration blocked by antibot marker {antibot_detection.name} at {current_url}"
            logger.error("[Register] %s", reason)
            return _RegistrationWaitResult(
                success=False,
                reason=reason,
                antibot_marker=antibot_detection.name,
            )

        form_is_ready = _is_registration_form_ready(html)
        if form_is_ready and second_index > 5:
            form_errors = await _extract_registration_form_errors(page)
            reason = _format_form_failure_reason(
                form_errors=form_errors,
                current_url=current_url,
                antibot_marker=None,
            )
            logger.error("[Register] %s", reason)
            return _RegistrationWaitResult(
                success=False,
                reason=reason,
                form_errors=form_errors,
            )
        if second_index > 0 and second_index % 15 == 0 and antibot_detection is None:
            logger.info(
                "[Register] Still waiting... (%ds / %ds)",
                second_index,
                timeout_seconds,
            )
    return _RegistrationWaitResult(
        success=False,
        reason=f"registration did not complete before timeout at {page.url}",
    )


def _registration_timeout_seconds(options: RegistrationOptions) -> int:
    return min(options.confirmation_timeout_seconds, 1200)


def _is_registration_form_ready(html: str) -> bool:
    return all(marker in html for marker in REGISTRATION_FORM_READY_MARKERS)


async def _extract_registration_form_errors(page: Page) -> tuple[str, ...]:
    return await visible_form_error_texts(page)


def _format_form_failure_reason(
    *,
    form_errors: tuple[str, ...],
    current_url: str,
    antibot_marker: str | None,
) -> str:
    reason = f"registration form is still present after submit at {current_url}"
    details: list[str] = []
    if form_errors:
        details.append(f"visible form errors: {' | '.join(form_errors)}")
    if antibot_marker is not None:
        details.append(f"antibot marker: {antibot_marker}")
    if not details:
        return f"{reason}; no visible form error text found"
    return f"{reason}; {'; '.join(details)}"


async def _register_email(
    email: str,
    schedule_profile: str,
) -> RegistrationResult:
    profile = ScheduleProfileController().get_profile(schedule_profile)
    if profile is None:
        raise ValueError(f"Unknown schedule profile {schedule_profile}")
    return await register_account(
        RegistrationOptions(
            email=email,
            password=DEFAULT_PASSWORD,
            identity=random_identity(),
            mail_provider=resolve_mail_provider(email),
            schedule_profile=schedule_profile,
            proxy_url=build_http_proxy_url(ProxyController().get_proxy(profile.proxy_id)),
        )
    )


def _next_email_to_register() -> str | None:
    email = MailAccountController().peek_next_available_email()
    if email is not None:
        return email
    if SONJI_API_KEY is None:
        return None
    return MailAccountController().provision_smailpro_email(SONJI_API_KEY)


async def register_next_available_email(
    schedule_profile: str,
) -> RegistrationResult | None:
    """Register a single available email, or return ``None`` when none remain.

    Used by the quota-driven scheduler, which only ever wants to consume one slot
    of the shared Ankama rate-limit pool at a time.
    """
    email = _next_email_to_register()
    if email is None:
        return None
    result = await _register_email(email, schedule_profile)
    if result.success:
        MailAccountController().mark_used(email)
    return result


def _first_schedule_profile_id() -> str:
    profiles = ScheduleProfileController().get_all_profiles()
    if not profiles:
        raise ValueError("Did not found any profile")
    return min(profiles)


async def register_available_emails(schedule_profile: str):
    while (email := _next_email_to_register()) is not None:
        result = await _register_email(email, schedule_profile)
        if not result.success:
            if result.antibot_marker is not None:
                logger.warning(
                    "[Register] Stopping batch after antibot marker %s on %s",
                    result.antibot_marker,
                    result.email,
                )
                return
            logger.warning(
                "[Register] Stopping batch after failed registration for %s: %s",
                result.email,
                result.error,
            )
            return
        MailAccountController().mark_used(email)
        await asyncio.sleep(random.randint(MIN_DELAY_BETWEEN_ACCOUNTS_SEC, MAX_DELAY_BETWEEN_ACCOUNTS_SEC))
    logger.warning("No more email available")


if __name__ == "__main__":
    load_dotenv(ENV_PATH)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    asyncio.run(register_available_emails(_first_schedule_profile_id()))
