import asyncio
import logging
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from urllib.parse import urlparse

from dotenv import load_dotenv
from playwright.async_api import Page, Response

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
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.exceptions import HaapiHttpError
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.haapi.urls import (
    REDIRECT_URI,
    build_register_url,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.utils.proxy import build_http_proxy_url
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.browser import (
    launch_browser_context,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.browser_interactions import (
    detect_antibot_marker,
    human_click_selector,
    human_type_selector,
    human_wait,
    is_waf_or_cloudfront_block,
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
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.mail_providers.smailpro import (
    is_outlook_token_refresh_failure,
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


@dataclass(frozen=True)
class _ConfirmationCodeResult:
    accepted: bool
    rejected: bool = False
    waf_blocked: bool = False
    failure_reason: str | None = None


ReplacementOptionsFactory = Callable[[RegistrationOptions], Awaitable[RegistrationOptions | None]]


def is_aws_waf_marker(marker: str | None) -> bool:
    return marker in {"aws waf", "aws waf block"}


async def register_account(
    options: RegistrationOptions,
    *,
    replacement_options_factory: ReplacementOptionsFactory | None = None,
) -> RegistrationResult:
    logger.debug("[Register] Starting Ankama account registration for %s...", options.email)
    current_options = options
    rejected_mailbox_count = 0

    async with launch_browser_context(proxy_url=options.proxy_url) as context:
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
            discarded_email: str | None = None
            wait_result = await _submit_registration_attempt(page, current_options)

            while _is_duplicate_email_error(wait_result.form_errors):
                logger.debug(
                    "[Register] %s is already linked to an Ankama account; requesting a replacement.",
                    current_options.email,
                )
                MailAccountController().quarantine(
                    current_options.email, "Adresse déjà liée à un compte Ankama"
                )
                discarded_email = current_options.email
                rejected_mailbox_count += 1
                if replacement_options_factory is None:
                    break
                replacement_options = await replacement_options_factory(current_options)
                if replacement_options is None:
                    break
                current_options = replacement_options
                wait_result = await _submit_replacement_email_attempt(page, current_options)

            if wait_result.success:
                if current_options.persist_account:
                    BotStorageController().save_account(
                        current_options.email,
                        current_options.password,
                        schedule_profile=current_options.schedule_profile,
                    )
                    persistence_status = "account saved"
                else:
                    persistence_status = "persistence disabled"
                logger.info(
                    "[Register] Ankama accepted %s after %d rejected mailbox(es); %s.",
                    current_options.email,
                    rejected_mailbox_count,
                    persistence_status,
                )
                return RegistrationResult(True, current_options.email, current_options.password, page.url)
            error = wait_result.reason or "registration did not complete before timeout"
            result = RegistrationResult(
                False,
                current_options.email,
                current_options.password,
                page.url,
                error,
                wait_result.antibot_marker,
            )
            mailbox_discarded = _is_discardable_email_error(result) and current_options.email != discarded_email
            if mailbox_discarded:
                MailAccountController().quarantine(current_options.email, "Inscription refusée par Ankama")
            logger.error(
                "[Register] Registration failed for %s after %d rejected mailbox(es)%s: %s",
                current_options.email,
                rejected_mailbox_count,
                "; mailbox discarded" if mailbox_discarded else "",
                error,
            )
            return result
        except HaapiHttpError as exc:
            logger.error("[Register] Registration failed for %s: %s", current_options.email, exc)
            logger.debug("[Register] Failure at URL %s", page.url, exc_info=True)
            return RegistrationResult(
                False,
                current_options.email,
                current_options.password,
                page.url,
                str(exc),
                outlook_generation_disabled=is_outlook_token_refresh_failure(exc),
            )
        except Exception as exc:
            if is_waf_or_cloudfront_block(status_code=None, content=str(exc)):
                MailAccountController().quarantine(current_options.email, "Blocage WAF/CloudFront confirmé")
                logger.error(
                    "[Register] WAF/CloudFront blocked %s after %d rejected mailbox(es); mailbox discarded.",
                    current_options.email,
                    rejected_mailbox_count,
                )
                return RegistrationResult(
                    False,
                    current_options.email,
                    current_options.password,
                    page.url,
                    str(exc),
                )
            logger.error("[Register] Registration failed for %s: %s", current_options.email, exc)
            logger.debug("[Register] Failure at URL %s", page.url, exc_info=True)
            return RegistrationResult(False, current_options.email, current_options.password, page.url, str(exc))


async def _submit_registration_attempt(page: Page, options: RegistrationOptions) -> _RegistrationWaitResult:
    await _fill_registration_form(page, options)
    started_at = datetime.now(UTC)
    await human_click_selector(page, "button[type='submit']")
    logger.debug("[Register] Clicked submit, URL: %s", page.url)
    return await _wait_for_result(page, options, started_at)


async def _submit_replacement_email_attempt(
    page: Page, options: RegistrationOptions
) -> _RegistrationWaitResult:
    await page.locator("#ankama-registration-login").first.fill("")
    await human_type_selector(page, "#ankama-registration-login", options.email)
    await human_wait(min_seconds=0.3, max_seconds=0.5)
    started_at = datetime.now(UTC)
    await human_click_selector(page, "button[type='submit']")
    logger.debug("[Register] Retried submit with replacement email %s, URL: %s", options.email, page.url)
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

        if is_waf_or_cloudfront_block(status_code=None, content=html):
            raise RuntimeError("WAF/CloudFront blocked registration page")

        antibot_detection = detect_antibot_marker(html)
        if antibot_detection is not None and (second_index == 0 or second_index % 15 == 0):
            logger.info(
                "[Register] %s detected before form fill; solve it in the browser window. (%ds elapsed)",
                antibot_detection.name,
                second_index,
            )
        elif second_index > 0 and second_index % 15 == 0:
            logger.debug(
                "[Register] Waiting for registration form... (%ds / %ds)",
                second_index,
                timeout_seconds,
            )
        await asyncio.sleep(1)
    raise TimeoutError(f"registration form did not become ready before timeout at {page.url}")


async def _submit_confirmation_code(page: Page, code: str) -> _ConfirmationCodeResult:
    logger.debug("[Register] Submitting email confirmation code from %s.", urlparse(page.url).path)
    if await page.locator("#otp").count() > 0:
        await human_type_selector(page, "#otp", code)
    else:
        for index, digit in enumerate(code, start=1):
            selector = f'input[name="n{index}"]'
            if await page.locator(selector).count() > 0:
                await human_type_selector(page, selector, digit)
    async with page.expect_navigation(wait_until="domcontentloaded", timeout=30_000) as navigation:
        await human_click_selector(page, "button[type='submit']")
    response: Response | None = await navigation.value
    response_body = await response.text() if response is not None and response.status == 403 else ""
    waf_blocked = response is not None and is_waf_or_cloudfront_block(
        status_code=response.status,
        content=response_body,
    )
    accepted = page.url.startswith(REDIRECT_URI)
    rejected = response is not None and response.status == 403 and not waf_blocked
    form_errors = (
        await visible_form_error_texts(page)
        if not accepted and not rejected and not waf_blocked
        else ()
    )
    response_path = urlparse(response.url).path if response is not None else None
    page_path = urlparse(page.url).path
    failure_reason = None
    if not accepted and not rejected and not waf_blocked:
        details = [
            f"response status={response.status if response is not None else None}",
            f"response path={response_path}",
            f"page path={page_path}",
        ]
        if form_errors:
            details.append(f"visible form errors: {' | '.join(form_errors)}")
        failure_reason = "confirmation code submission did not reach the expected redirect; " + "; ".join(
            details
        )
    result = _ConfirmationCodeResult(
        accepted=accepted,
        rejected=rejected,
        waf_blocked=waf_blocked,
        failure_reason=failure_reason,
    )
    logger.debug(
        "[Register] Confirmation code submission result: response_present=%s status=%s ok=%s "
        "response_path=%s page_path=%s accepted=%s rejected=%s waf_blocked=%s "
        "visible_form_errors=%s failure_reason=%s",
        response is not None,
        response.status if response is not None else None,
        response.ok if response is not None else None,
        response_path,
        page_path,
        result.accepted,
        result.rejected,
        result.waf_blocked,
        form_errors,
        result.failure_reason,
    )
    return result


async def _handle_confirmation_code(
    page: Page, options: RegistrationOptions, started_at: datetime
) -> _ConfirmationCodeResult:
    logger.debug("[Register] Email confirmation required at %s.", urlparse(page.url).path)

    async def via_browser() -> _ConfirmationCodeResult:
        while "/register/ankama/code" in page.url:
            await asyncio.sleep(0.3)
        result = _ConfirmationCodeResult(accepted=page.url.startswith(REDIRECT_URI))
        logger.debug(
            "[Register] Browser left confirmation page: page_path=%s accepted=%s.",
            urlparse(page.url).path,
            result.accepted,
        )
        return result

    async def via_mailbox() -> _ConfirmationCodeResult:
        code = await wait_for_code_with_manual_fallback(
            options.mail_provider,
            since=started_at,
            timeout_seconds=options.confirmation_timeout_seconds,
        )
        if code is None:
            logger.debug("[Register] Mailbox did not provide a confirmation code before its deadline.")
            raise MailboxCodeTimeoutError(
                f"Timed out waiting for registration confirmation code for {options.email}"
            )
        logger.debug("[Register] Mailbox provided a confirmation code.")
        if "/register/ankama/code" not in page.url:
            logger.debug(
                "[Register] Confirmation page was left before mailbox code submission: page_path=%s.",
                urlparse(page.url).path,
            )
            return _ConfirmationCodeResult(accepted=False)
        return await _submit_confirmation_code(page, code)

    tasks = {
        "browser": asyncio.create_task(via_browser()),
        "mailbox": asyncio.create_task(via_mailbox()),
    }
    done, pending = await asyncio.wait(
        tasks.values(),
        return_when=asyncio.FIRST_COMPLETED,
        timeout=options.confirmation_timeout_seconds,
    )
    for source, task in tasks.items():
        if task in pending:
            logger.debug("[Register] Cancelling pending %s confirmation task.", source)
            task.cancel()
    if pending:
        await asyncio.gather(*pending, return_exceptions=True)
    for source, task in tasks.items():
        if task not in done:
            continue
        exception = task.exception()
        if exception is None:
            result = task.result()
            logger.debug(
                "[Register] %s confirmation task completed: accepted=%s rejected=%s waf_blocked=%s.",
                source,
                result.accepted,
                result.rejected,
                result.waf_blocked,
            )
        if isinstance(exception, MailboxCodeTimeoutError):
            MailAccountController().quarantine(options.email, "Délai dépassé pour le code de confirmation")
            raise exception
    results = [task.result() for task in done if not task.cancelled()]
    return next((result for result in results if result.accepted), _ConfirmationCodeResult(accepted=False))


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
            confirmation_result = await _handle_confirmation_code(page, options, started_at)
            if confirmation_result.accepted:
                return _RegistrationWaitResult(success=True)
            reason = confirmation_result.failure_reason or "email confirmation code was not submitted or accepted"
            if confirmation_result.waf_blocked:
                reason = "WAF/CloudFront blocked confirmation code submission"
            elif confirmation_result.rejected:
                reason = "Ankama rejected confirmation code"
            return _RegistrationWaitResult(
                success=False,
                reason=reason,
            )

        form_errors = ()
        if second_index > 5:
            form_errors = await _extract_registration_form_errors(page)

        form_is_ready = _is_registration_form_ready(html)
        if is_waf_or_cloudfront_block(status_code=None, content=html):
            reason = "WAF/CloudFront blocked registration page"
            logger.debug("[Register] %s", reason)
            return _RegistrationWaitResult(success=False, reason=reason)
        antibot_detection = detect_antibot_marker(html)
        if form_errors:
            reason = _format_form_failure_reason(
                form_errors=form_errors,
                current_url=current_url,
                antibot_marker=None,
            )
            logger.debug("[Register] %s", reason)
            return _RegistrationWaitResult(
                success=False,
                reason=reason,
                form_errors=form_errors,
            )

        if antibot_detection is not None:
            reason = f"registration blocked by antibot marker {antibot_detection.name} at {current_url}"
            logger.debug("[Register] %s", reason)
            return _RegistrationWaitResult(
                success=False,
                reason=reason,
                antibot_marker=antibot_detection.name,
            )

        if form_is_ready and second_index > 5:
            reason = _format_form_failure_reason(
                form_errors=(),
                current_url=current_url,
                antibot_marker=None,
            )
            logger.debug("[Register] %s", reason)
            return _RegistrationWaitResult(
                success=False,
                reason=reason,
            )
        if second_index > 0 and second_index % 15 == 0 and antibot_detection is None:
            logger.debug(
                "[Register] Still waiting... (%ds / %ds)",
                second_index,
                timeout_seconds,
            )
    return _RegistrationWaitResult(
        success=False,
        reason=f"registration did not complete before timeout at {page.url}",
    )


def _registration_timeout_seconds(options: RegistrationOptions) -> int:
    return min(options.confirmation_timeout_seconds, 60)


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
    options = RegistrationOptions(
        email=email,
        password=DEFAULT_PASSWORD,
        identity=random_identity(),
        mail_provider=resolve_mail_provider(email),
        schedule_profile=schedule_profile,
        proxy_url=build_http_proxy_url(ProxyController().get_proxy(profile.proxy_id)),
    )

    async def replacement_options_factory(
        current_options: RegistrationOptions,
    ) -> RegistrationOptions | None:
        replacement_email = _next_email_to_register()
        if replacement_email is None:
            return None
        return replace(
            current_options,
            email=replacement_email,
            mail_provider=resolve_mail_provider(replacement_email),
        )

    return await register_account(options, replacement_options_factory=replacement_options_factory)


_DISCARDABLE_EMAIL_ERROR_MARKERS = (
    "n'est pas valide",
    "compte existant",
    "ankama rejected confirmation code",
    "waf/cloudfront blocked",
)


def _is_duplicate_email_error(form_errors: tuple[str, ...]) -> bool:
    return any("compte existant" in error.casefold() for error in form_errors)


def _is_discardable_email_error(result: RegistrationResult) -> bool:
    return result.error is not None and any(
        marker in result.error.casefold() for marker in _DISCARDABLE_EMAIL_ERROR_MARKERS
    )


def _finalize_registration_attempt(email: str, result: RegistrationResult) -> None:
    if result.success:
        MailAccountController().mark_used(email)


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
    _finalize_registration_attempt(result.email, result)
    return result


def _first_schedule_profile_id() -> str:
    profiles = ScheduleProfileController().get_all_profiles()
    if not profiles:
        raise ValueError("Did not found any profile")
    return min(profiles)


async def register_available_emails(schedule_profile: str):
    while (email := _next_email_to_register()) is not None:
        result = await _register_email(email, schedule_profile)
        _finalize_registration_attempt(result.email, result)
        if result.success:
            await asyncio.sleep(
                random.randint(MIN_DELAY_BETWEEN_ACCOUNTS_SEC, MAX_DELAY_BETWEEN_ACCOUNTS_SEC)
            )
            continue
        if _is_discardable_email_error(result):
            continue
        if result.outlook_generation_disabled:
            logger.warning("[Register] Outlook is unavailable; continuing batch with Gmail.")
            continue
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
    logger.warning("No more email available")


if __name__ == "__main__":
    load_dotenv(ENV_PATH)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    asyncio.run(register_available_emails(_first_schedule_profile_id()))
