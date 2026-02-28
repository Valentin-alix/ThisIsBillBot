from typing import cast
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

import requests
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.exceptions import ProxyRejectedError
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.haapi import haapi as haapi_module
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.credentials import DecipheredCertif
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.local_storage import BotRecord
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.oauth_api import TokenResponse
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.mail_providers.base import (
    MailboxCodeTimeoutError,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web.auth import (
    launcher_login as launcher_login_module,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web.auth.models import (
    AuthenticationOptions,
    AuthenticationResult,
)
from playwright._impl._errors import TargetClosedError

from tests.fixtures.launcher import (
    FakeBrowserContext,
    FakeMailProvider,
)


def _make_haapi(certif: DecipheredCertif | None = None) -> MagicMock:
    haapi = MagicMock()
    haapi.get_security_code.return_value = "test.com"
    payload = certif or DecipheredCertif(id=7, encodedCertificate="AB", login="x@y.z")
    haapi.validate_code.return_value = payload
    haapi.validate_otp.return_value = payload
    return haapi


class _FakeRefreshApiKeySession:
    def __init__(self, response: requests.Response) -> None:
        self.proxies: dict[str, str] = {}
        self.response = response
        self.last_url: str | None = None
        self.last_data: object | None = None

    def post(
        self,
        url: str,
        *,
        data: object,
        headers: dict[str, str],
        verify: bool,
    ) -> requests.Response:
        self.last_url = url
        self.last_data = data
        return self.response


def _json_response(status_code: int, body: bytes) -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    setattr(response, "_content", body)
    response.url = "https://haapi.ankama.com/json/Ankama/v5/Api/RefreshApiKey"
    return response


class TestRefreshApiKeyFromOauth(IsolatedAsyncioTestCase):
    def test_uses_proxy_for_refresh_api_key_request(self) -> None:
        response = _json_response(200, b'{"key":"api-key","account_id":123,"refresh_token":"next"}')
        session = _FakeRefreshApiKeySession(response)

        with patch.object(haapi_module.requests, "Session", return_value=session):
            result = haapi_module.refresh_api_key_from_oauth(
                "access",
                "refresh",
                proxy_url="http://127.0.0.1:9000",
            )

        self.assertEqual(result.account_id, 123)
        self.assertEqual(
            session.proxies,
            {"http": "http://127.0.0.1:9000", "https": "http://127.0.0.1:9000"},
        )

    def test_refresh_api_key_http_error_includes_response_body(self) -> None:
        response = _json_response(403, b'{"error":"FORBIDDEN"}')
        session = _FakeRefreshApiKeySession(response)

        with (
            patch.object(haapi_module.requests, "Session", return_value=session),
            self.assertRaises(requests.exceptions.HTTPError) as context,
        ):
            haapi_module.refresh_api_key_from_oauth("access", "refresh")

        self.assertIn("FORBIDDEN", str(context.exception))


class TestOAuthAuthenticate(IsolatedAsyncioTestCase):
    async def test_wait_for_tokens_raises_when_ankama_rejects_proxy(self) -> None:
        page = MagicMock()
        page.on = MagicMock()

        with (
            patch.object(
                launcher_login_module,
                "visible_form_error_texts",
                new=AsyncMock(
                    return_value=(
                        "Connexion non-autorisée : votre adresse IP est cachée. "
                        "Veuillez consulter notre FAQ pour plus d'informations",
                    )
                ),
            ),
            patch.object(launcher_login_module.asyncio, "sleep", new=AsyncMock()),
            self.assertRaises(ProxyRejectedError),
        ):
            await launcher_login_module._wait_for_tokens(page, "verifier")

    async def test_authenticate_propagates_proxy_rejection(
        self,
    ) -> None:
        page = MagicMock()
        page.url = "https://account.ankama.com/login"
        page.goto = AsyncMock()
        browser_context = FakeBrowserContext(page)
        with (
            patch.object(
                launcher_login_module,
                "launch_browser_context",
                return_value=browser_context,
            ),
            patch.object(
                launcher_login_module,
                "human_wait",
                new=AsyncMock(),
            ),
            patch.object(
                launcher_login_module,
                "fill_credentials_and_submit",
                new=AsyncMock(),
            ),
            patch.object(
                launcher_login_module,
                "_wait_for_tokens",
                new=AsyncMock(side_effect=ProxyRejectedError("rejected")),
            ),
            self.assertRaises(ProxyRejectedError),
        ):
            await launcher_login_module.authenticate(
                AuthenticationOptions(
                    email="u@example.com",
                    password="password",
                    mail_provider=FakeMailProvider(),
                    proxy_url="http://127.0.0.1:9000",
                )
            )

    async def test_returns_failure_when_browser_page_is_closed(
        self,
    ) -> None:
        page = MagicMock()
        page.url = "https://auth.ankama.com/login-authorized?code=abc"
        page.goto = AsyncMock()
        page.content = AsyncMock(side_effect=TargetClosedError("page closed"))
        browser_context = FakeBrowserContext(page)
        token_response = TokenResponse(access_token="access", refresh_token="refresh")

        with (
            patch.object(
                launcher_login_module,
                "launch_browser_context",
                return_value=browser_context,
            ),
            patch.object(
                launcher_login_module,
                "fill_credentials_and_submit",
                new=AsyncMock(),
            ),
            patch.object(
                launcher_login_module,
                "_wait_for_tokens",
                new=AsyncMock(return_value=token_response),
            ),
            patch.object(
                launcher_login_module,
                "refresh_api_key_from_oauth",
                side_effect=requests.exceptions.HTTPError("403 forbidden"),
            ),
            patch.object(launcher_login_module.asyncio, "sleep", new=AsyncMock()),
            patch.object(launcher_login_module, "human_wait", new=AsyncMock()),
        ):
            result = await launcher_login_module.authenticate(
                AuthenticationOptions(
                    email="u@example.com",
                    password="password",
                    mail_provider=FakeMailProvider(),
                    proxy_url="http://127.0.0.1:9000",
                )
            )

        self.assertFalse(result.success)
        self.assertEqual(result.error, "403 forbidden")

    async def test_waf_blocked_oauth_removes_mailbox(self) -> None:
        page = MagicMock()
        page.goto = AsyncMock(return_value=None)
        browser_context = FakeBrowserContext(page)

        with (
            patch.object(launcher_login_module, "launch_browser_context", return_value=browser_context),
            patch.object(launcher_login_module, "fill_credentials_and_submit", new=AsyncMock()),
            patch.object(
                launcher_login_module,
                "_wait_for_tokens",
                new=AsyncMock(side_effect=RuntimeError("WAF/CloudFront blocked OAuth page")),
            ),
            patch.object(launcher_login_module, "MailAccountController") as mail_account_controller,
            patch.object(launcher_login_module, "human_wait", new=AsyncMock()),
        ):
            result = await launcher_login_module.authenticate(
                AuthenticationOptions(
                    email="u@example.com",
                    password="password",
                    mail_provider=FakeMailProvider(),
                )
            )

        self.assertFalse(result.success)
        self.assertEqual(result.error, "WAF/CloudFront blocked OAuth page")
        mail_account_controller.return_value.quarantine.assert_called_once_with(
            "u@example.com", "Blocage WAF/CloudFront confirmé"
        )

    async def test_authenticate_records_bad_state_on_shield_code_timeout(
        self,
    ) -> None:
        page = MagicMock()
        page.url = "https://auth.ankama.com/login-authorized?code=abc"
        page.goto = AsyncMock()
        browser_context = FakeBrowserContext(page)
        token_response = TokenResponse(access_token="access", refresh_token="refresh")
        api_key_result = MagicMock()
        api_key_result.key = "api-key"
        api_key_result.account_id = 123
        api_key_result.refresh_token = "refresh"

        with (
            patch.object(
                launcher_login_module,
                "launch_browser_context",
                return_value=browser_context,
            ),
            patch.object(
                launcher_login_module,
                "fill_credentials_and_submit",
                new=AsyncMock(),
            ),
            patch.object(
                launcher_login_module,
                "_wait_for_tokens",
                new=AsyncMock(return_value=token_response),
            ),
            patch.object(
                launcher_login_module,
                "refresh_api_key_from_oauth",
                return_value=api_key_result,
            ),
            patch.object(launcher_login_module, "Haapi") as haapi_class,
            patch.object(
                launcher_login_module,
                "resolve_shield",
                new=AsyncMock(side_effect=MailboxCodeTimeoutError("Timed out waiting for code")),
            ),
            patch.object(launcher_login_module, "MailAccountController") as mail_account_controller,
            patch.object(launcher_login_module.logger, "exception") as log_exception,
            patch.object(launcher_login_module.logger, "error") as log_error,
            patch.object(launcher_login_module.asyncio, "sleep", new=AsyncMock()),
            patch.object(launcher_login_module, "human_wait", new=AsyncMock()),
        ):
            haapi_class.return_value.signOnWithApiKey.return_value = MagicMock()
            result = await launcher_login_module.authenticate(
                AuthenticationOptions(
                    email="u@example.com",
                    password="password",
                    mail_provider=FakeMailProvider(),
                    proxy_url="http://127.0.0.1:9000",
                )
            )

        self.assertFalse(result.success)
        self.assertEqual(result.error, "Timed out waiting for code")
        mail_account_controller.return_value.quarantine.assert_called_once_with(
            "u@example.com", "Délai dépassé pour le code de confirmation"
        )
        log_exception.assert_not_called()
        log_error.assert_called_once()

    async def test_failed_generated_account_auth_clears_stored_key_and_retries(
        self,
    ) -> None:
        account = BotRecord(
            email="u@example.com",
            password="password",
            hardware_id="hw-1",
            schedule_profile="E",
        )
        authenticate = AsyncMock(
            return_value=AuthenticationResult(
                success=False,
                email="u@example.com",
                error="403 forbidden",
            )
        )

        with (
            patch.object(
                launcher_login_module,
                "authenticate",
                new=authenticate,
            ),
            patch.object(launcher_login_module.BotStorageController, "quarantine") as quarantine,
            patch.object(
                launcher_login_module, "resolve_mail_provider", return_value=FakeMailProvider()
            ),
        ):
            result = await launcher_login_module._authenticate_account(
                account, proxy_url="http://127.0.0.1:9000"
            )

        self.assertFalse(result.success)
        authenticate.assert_awaited_once()
        await_args = authenticate.await_args
        assert await_args is not None
        sent_options = cast(AuthenticationOptions, await_args.args[0])
        self.assertEqual(sent_options.proxy_url, "http://127.0.0.1:9000")
        quarantine.assert_called_once_with("u@example.com", "Authentification échouée")

    async def test_successful_generated_account_auth_stores_key(
        self,
    ) -> None:
        account = BotRecord(
            email="u@example.com",
            password="password",
            hardware_id="hw-1",
            schedule_profile="E",
        )
        authenticate = AsyncMock(
            return_value=AuthenticationResult(
                success=True,
                email="u@example.com",
                access_token="access",
                account_id=123,
            )
        )

        with (
            patch.object(
                launcher_login_module,
                "authenticate",
                new=authenticate,
            ),
            patch.object(launcher_login_module.BotStorageController, "quarantine") as quarantine,
            patch.object(
                launcher_login_module, "resolve_mail_provider", return_value=FakeMailProvider()
            ),
        ):
            result = await launcher_login_module._authenticate_account(
                account, proxy_url="http://127.0.0.1:9000"
            )

        self.assertTrue(result.success)
        quarantine.assert_not_called()
