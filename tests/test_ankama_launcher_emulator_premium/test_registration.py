from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import AsyncMock, MagicMock, patch
from urllib.parse import parse_qs, urlparse

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.bot_storage import (
    BotStorageController,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.mail_account import (
    MailAccountController,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.haapi.urls import build_register_url
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.mail_account import (
    MailAccountEntry,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.mail_providers.manual import (
    extract_confirmation_code,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.pkce import (
    generate_code_challenge,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web.auth import (
    registration as registration_module,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web.auth.models import (
    RegistrationIdentity,
    RegistrationOptions,
    RegistrationResult,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web.auth.oauth_state import (
    build_login_url,
)

from tests.test_ankama_launcher_emulator_premium._fakes import FakeBrowserContext, FakeMailProvider


class TestRegistration(TestCase):
    def test_build_register_url_without_state_keeps_redirect_uri(self) -> None:
        params = parse_qs(urlparse(build_register_url()).query)

        self.assertEqual(
            params["redirect_uri"],
            ["https://auth.ankama.com/login-authorized"],
        )

    def test_build_register_url_with_state_embeds_state_in_redirect_uri(self) -> None:
        params = parse_qs(urlparse(build_register_url("abc123")).query)

        self.assertEqual(
            params["redirect_uri"],
            ["https://auth.ankama.com/login-authorized?state%3abc123"],
        )

    def test_generate_code_challenge_is_pkce_sha256_base64url(self) -> None:
        self.assertEqual(
            generate_code_challenge("abc"),
            "ungWv48Bz-pBQUDeXa4iI7ADYaOWF3qctBD_YfIAFa0",
        )

    def test_build_login_url_uses_launcher_oauth_context(self) -> None:
        params = parse_qs(urlparse(build_login_url("challenge")).query)

        self.assertEqual(params["client_id"], ["102"])
        self.assertEqual(params["redirect_uri"], ["zaap://login"])
        self.assertEqual(params["direct"], ["true"])

    def test_extract_confirmation_code_from_text_or_html(self) -> None:
        self.assertEqual(extract_confirmation_code("Votre code: 123456"), "123456")
        self.assertEqual(
            extract_confirmation_code("<div>Votre code</div><strong>654321</strong>"),
            "654321",
        )

    def test_save_account_writes_generated_account_schema(self) -> None:
        BotStorageController().save_account("new@example.com", "new", schedule_profile="A")
        BotStorageController().save_account("new@example.com", "new", schedule_profile="B")

        accounts = BotStorageController().get_generated_account_records()

        self.assertEqual(len(accounts), 1)
        self.assertEqual(accounts[0].email, "new@example.com")
        self.assertEqual(accounts[0].schedule_profile, "B")

    def test_bad_state_emails_are_loaded_from_json(self) -> None:
        MailAccountController().record_bad_state("bad@example.com")
        self.assertEqual(MailAccountController().load_bad_state_emails(), {"bad@example.com"})

    def test_reassign_schedule_profile_preserves_credentials(self) -> None:
        BotStorageController().save_account("user@example.com", "secret", "C")
        BotStorageController().reassign_schedule_profile("user@example.com", "E")
        account = BotStorageController().get_generated_account_records()[0]

        self.assertEqual(account.password, "secret")
        self.assertEqual(account.schedule_profile, "E")

    def test_peek_next_available_email_excludes_bad_state_and_used(self) -> None:
        mail_controller = MailAccountController()
        mail_controller.record_bad_state("bad@example.com")
        mail_controller.mark_used("used@example.com")
        with mail_controller._acquire_file_lock():
            accounts_file = mail_controller._load()
            accounts_file.accounts.setdefault("good@example.com", MailAccountEntry())
            mail_controller._save(accounts_file)

        self.assertEqual(mail_controller.peek_next_available_email(), "good@example.com")

    def test_record_bad_state_email_deduplicates_and_sorts(self) -> None:
        MailAccountController().record_bad_state("z@example.com")
        MailAccountController().record_bad_state("a@example.com")
        MailAccountController().record_bad_state("z@example.com")
        bad_state_emails = MailAccountController().load_bad_state_emails()

        self.assertEqual(bad_state_emails, {"a@example.com", "z@example.com"})

    def test_finalize_registration_attempt_discards_already_linked_email(self) -> None:
        with MailAccountController()._acquire_file_lock():
            accounts_file = MailAccountController()._load()
            accounts_file.accounts.setdefault("linked@example.com", MailAccountEntry())
            MailAccountController()._save(accounts_file)
        result = RegistrationResult(
            success=False,
            email="linked@example.com",
            password="password",
            final_url="https://auth.ankama.com/register/ankama",
            error=(
                "registration form is still present after submit; visible form errors: "
                '"linked@example.com" est déjà lié à un compte existant. Pour continuer, connectez-vous.'
            ),
        )

        registration_module._finalize_registration_attempt("linked@example.com", result)

        self.assertNotIn("linked@example.com", MailAccountController()._load().accounts)

    def test_finalize_registration_attempt_discards_invalid_email(self) -> None:
        with MailAccountController()._acquire_file_lock():
            accounts_file = MailAccountController()._load()
            accounts_file.accounts.setdefault("retry@example.com", MailAccountEntry())
            MailAccountController()._save(accounts_file)
        result = RegistrationResult(
            success=False,
            email="retry@example.com",
            password="password",
            final_url="https://auth.ankama.com/register/ankama",
            error="registration form is still present after submit; visible form errors: Email invalide",
        )

        registration_module._finalize_registration_attempt("retry@example.com", result)

        self.assertNotIn("retry@example.com", MailAccountController()._load().accounts)


def _registration_options(
    confirmation_timeout_seconds: int = 1200,
) -> RegistrationOptions:
    return RegistrationOptions(
        email="new@example.com",
        password="password",
        identity=RegistrationIdentity(
            firstname="Jane",
            lastname="Doe",
            birthday_day="01",
            birthday_month="02",
            birthday_year="1990",
        ),
        mail_provider=FakeMailProvider(),
        confirmation_timeout_seconds=confirmation_timeout_seconds,
    )


def _ready_registration_form_html(extra_html: str = "") -> str:
    return (
        "<html><body><form>"
        '<input id="ankama-registration-login">'
        '<input id="ankama-registration-password">'
        '<select id="ankama-registration-birthday-day"></select>'
        '<select id="ankama-registration-birthday-month"></select>'
        '<select id="ankama-registration-birthday-year"></select>'
        '<button type="submit"></button>'
        f"{extra_html}"
        "</form></body></html>"
    )


class TestRegisterAccount(IsolatedAsyncioTestCase):
    async def test_saves_account_after_successful_registration(self) -> None:
        page = MagicMock()
        page.url = "https://auth.ankama.com/login-authorized"
        page.goto = AsyncMock()
        page.click = AsyncMock()
        browser_context = FakeBrowserContext(page)

        with (
            patch.object(
                registration_module,
                "launch_browser_context",
                return_value=browser_context,
            ),
            patch.object(
                registration_module,
                "get_registration_state",
                new=AsyncMock(return_value="state"),
            ),
            patch.object(
                registration_module,
                "_wait_for_registration_form_ready",
                new=AsyncMock(),
            ),
            patch.object(
                registration_module,
                "_fill_registration_form",
                new=AsyncMock(),
            ),
            patch.object(
                registration_module,
                "_wait_for_result",
                new=AsyncMock(return_value=registration_module._RegistrationWaitResult(success=True)),
            ),
            patch.object(
                registration_module,
                "human_click_selector",
                new=AsyncMock(),
            ) as human_click_selector,
            patch.object(registration_module, "BotStorageController") as bot_storage_controller,
            patch.object(registration_module.asyncio, "sleep", new=AsyncMock()),
            patch.object(registration_module, "human_wait", new=AsyncMock()),
        ):
            result = await registration_module.register_account(_registration_options())

        self.assertTrue(result.success)
        human_click_selector.assert_awaited_once_with(page, "button[type='submit']")
        bot_storage_controller.return_value.save_account.assert_called_once_with(
            "new@example.com",
            "password",
            schedule_profile=None,
        )

    async def test_returns_failure_when_registration_times_out(self) -> None:
        page = MagicMock()
        page.url = "https://auth.ankama.com/register/ankama"
        page.goto = AsyncMock()
        page.click = AsyncMock()
        page.content = AsyncMock(return_value="<html>registration failed</html>")
        browser_context = FakeBrowserContext(page)
        failure = registration_module._RegistrationWaitResult(
            success=False,
            reason="registration form is still present after submit; visible form errors: Email invalide",
        )

        with (
            patch.object(
                registration_module,
                "launch_browser_context",
                return_value=browser_context,
            ),
            patch.object(
                registration_module,
                "get_registration_state",
                new=AsyncMock(return_value="state"),
            ),
            patch.object(
                registration_module,
                "_wait_for_registration_form_ready",
                new=AsyncMock(),
            ),
            patch.object(
                registration_module,
                "_fill_registration_form",
                new=AsyncMock(),
            ),
            patch.object(
                registration_module,
                "_wait_for_result",
                new=AsyncMock(return_value=failure),
            ),
            patch.object(
                registration_module,
                "human_click_selector",
                new=AsyncMock(),
            ),
            patch.object(registration_module, "BotStorageController") as bot_storage_controller,
            patch.object(registration_module, "MailAccountController") as mail_account_controller,
            patch.object(registration_module, "dump_page_html", new=AsyncMock()),
            patch.object(registration_module.asyncio, "sleep", new=AsyncMock()),
            patch.object(registration_module, "human_wait", new=AsyncMock()),
        ):
            result = await registration_module.register_account(_registration_options())

        self.assertFalse(result.success)
        self.assertEqual(result.error, failure.reason)
        bot_storage_controller.return_value.save_account.assert_not_called()
        mail_account_controller.return_value.remove_email.assert_called_once_with("new@example.com")

    async def test_wait_for_result_reports_visible_form_errors(self) -> None:
        page = MagicMock()
        page.url = "https://auth.ankama.com/register/ankama/form-submit"
        page.content = AsyncMock(return_value="<html><body>form rerendered</body></html>")

        with (
            patch.object(registration_module.asyncio, "sleep", new=AsyncMock()),
            patch.object(
                registration_module,
                "_extract_registration_form_errors",
                new=AsyncMock(return_value=("Adresse email deja utilisee",)),
            ),
        ):
            result = await registration_module._wait_for_result(
                page,
                _registration_options(),
                started_at=registration_module.datetime.now(registration_module.UTC),
            )

        self.assertFalse(result.success)
        self.assertEqual(result.form_errors, ("Adresse email deja utilisee",))
        self.assertIn("Adresse email deja utilisee", result.reason or "")

    async def test_wait_for_registration_form_ready_waits_until_form_markers_present(
        self,
    ) -> None:
        page = MagicMock()
        page.url = "https://auth.ankama.com/register/ankama/form"
        page.content = AsyncMock(
            side_effect=[
                "<html><head></head></html>",
                _ready_registration_form_html(),
            ]
        )

        with patch.object(registration_module.asyncio, "sleep", new=AsyncMock()):
            await registration_module._wait_for_registration_form_ready(
                page,
                _registration_options(confirmation_timeout_seconds=5),
            )

        self.assertEqual(page.content.await_count, 2)

    async def test_wait_for_result_fails_fast_when_form_has_aws_waf(
        self,
    ) -> None:
        page = MagicMock()
        page.url = "https://auth.ankama.com/register/ankama/form-submit"
        page.content = AsyncMock(
            return_value=_ready_registration_form_html(
                '<script src="https://edge.sdk.awswaf.com/challenge.js"></script>'
            )
        )

        with (
            patch.object(registration_module.asyncio, "sleep", new=AsyncMock()),
            patch.object(
                registration_module,
                "_extract_registration_form_errors",
                new=AsyncMock(return_value=()),
            ) as extract_registration_form_errors,
        ):
            result = await registration_module._wait_for_result(
                page,
                _registration_options(confirmation_timeout_seconds=7),
                started_at=registration_module.datetime.now(registration_module.UTC),
            )

        self.assertFalse(result.success)
        self.assertEqual(result.antibot_marker, "aws waf block")
        self.assertIn("registration blocked by antibot marker", result.reason or "")
        extract_registration_form_errors.assert_not_awaited()

    async def test_registration_confirmation_timeout_removes_email(
        self,
    ) -> None:
        page = MagicMock()
        page.url = "https://auth.ankama.com/register/ankama/code"

        with (
            patch.object(
                registration_module,
                "wait_for_code_with_manual_fallback",
                new=AsyncMock(return_value=None),
            ),
            patch.object(registration_module, "MailAccountController") as mail_account_controller,
            self.assertRaises(registration_module.MailboxCodeTimeoutError),
        ):
            await registration_module._handle_confirmation_code(
                page,
                _registration_options(confirmation_timeout_seconds=1),
                started_at=registration_module.datetime.now(registration_module.UTC),
            )

        mail_account_controller.return_value.remove_email.assert_called_once_with("new@example.com")
