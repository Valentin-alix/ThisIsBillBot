from typing import cast
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch

from ankama_launcher_emulator_premium.exceptions import BannedException
from ankama_launcher_emulator_premium.web._client import (
    credentials as credentials_module,
)
from ankama_launcher_emulator_premium.web._client.browser_interactions import (
    accept_cookies_if_present,
    detect_antibot_marker,
)
from playwright.async_api import Page

from tests.test_ankama_launcher_emulator_premium._fakes import FakeLocator


class _FakeCookiePage:
    def __init__(self, selector_counts: dict[str, int]) -> None:
        self._selectors = {selector: FakeLocator(count) for selector, count in selector_counts.items()}
        self.missing_locator = FakeLocator(0)

    def locator(self, selector: str) -> FakeLocator:
        return self._selectors.get(selector, self.missing_locator)


class _FakeCredentialsPage:
    def __init__(self) -> None:
        self.wait_for_selector = AsyncMock()
        self.wait_for_load_state = AsyncMock()
        self.banned_alert = FakeLocator(1)
        self.default_locator = FakeLocator(1)
        self.default_locator.wait_for.side_effect = AssertionError("Unexpected ban selector")

    def locator(self, selector: str) -> FakeLocator:
        if "votre compte est banni" in selector:
            return self.banned_alert
        return self.default_locator


class TestBrowserInteractions(IsolatedAsyncioTestCase):
    async def test_accept_cookies_clicks_first_present_consent_button(self) -> None:
        page = _FakeCookiePage({"#didomi-notice-agree-button": 1})

        accepted = await accept_cookies_if_present(cast(Page, page))

        self.assertTrue(accepted)
        page.locator("#didomi-notice-agree-button").click.assert_awaited_once_with(timeout=2_000)

    async def test_accept_cookies_returns_false_without_known_consent_button(
        self,
    ) -> None:
        page = _FakeCookiePage({})

        accepted = await accept_cookies_if_present(cast(Page, page))

        self.assertFalse(accepted)
        page.missing_locator.click.assert_not_awaited()

    async def test_detect_antibot_marker_returns_known_markers(self) -> None:
        for html, expected_name, expected_marker in (
            ("<html>turnstile widget</html>", "turnstile", "turnstile"),
            (
                '<script src="https://edge.sdk.awswaf.com/challenge.js"></script>',
                "aws waf block",
                "awswaf",
            ),
        ):
            with self.subTest(expected_name=expected_name):
                detection = detect_antibot_marker(html)

                self.assertIsNotNone(detection)
                assert detection is not None
                self.assertEqual(detection.name, expected_name)
                self.assertEqual(detection.marker, expected_marker)

    async def test_fill_credentials_raises_when_account_is_banned(self) -> None:
        page = _FakeCredentialsPage()

        with (
            patch.object(credentials_module, "human_type_selector", new=AsyncMock()) as type_selector,
            patch.object(credentials_module, "human_click_selector", new=AsyncMock()) as click_selector,
            patch.object(credentials_module, "human_wait", new=AsyncMock()),
            self.assertRaises(BannedException),
        ):
            await credentials_module.fill_credentials_and_submit(
                cast(Page, page), "u@example.com", "password"
            )

        page.wait_for_selector.assert_awaited_once_with("#ankama-login", timeout=10_000)
        self.assertEqual(type_selector.await_count, 2)
        click_selector.assert_awaited_once_with(cast(Page, page), "button[type='submit']")
