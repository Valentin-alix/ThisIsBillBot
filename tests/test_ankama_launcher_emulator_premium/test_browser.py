import os
import tempfile
import time
from unittest import IsolatedAsyncioTestCase, TestCase
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client import (
    browser as browser_module,
)


class TestLaunchBrowserContext(IsolatedAsyncioTestCase):
    async def test_uses_visible_browser_configuration(self) -> None:
        playwright, browser, context, playwright_context = _browser_launch_fakes()
        trace_directory = Path("debug/traces/20260829_120000_000000_u@example.com")

        with (
            patch.object(browser_module, "async_playwright", return_value=playwright_context),
            patch.object(browser_module, "_trace_directory", return_value=trace_directory),
        ):
            async with browser_module.launch_browser_context(
                login="u@example.com", proxy_url=None, headless=False
            ) as returned_context:
                self.assertIs(returned_context, context)

        playwright.chromium.launch.assert_awaited_once_with(
            headless=False,
            traces_dir=trace_directory,
            channel="chromium",
            args=browser_module.BROWSER_ARGS,
            proxy=None,
        )
        browser.new_context.assert_awaited_once_with(
            color_scheme="dark",
            viewport={"width": 1280, "height": 720},
            locale="fr-FR",
            timezone_id="Europe/Paris",
        )
        context.tracing.start.assert_awaited_once_with(
            name="session",
            screenshots=True,
            snapshots=True,
            sources=True,
        )
        context.tracing.stop.assert_awaited_once_with(path=trace_directory / "trace.zip")
        browser.close.assert_awaited_once()


class TestTraceRetention(TestCase):
    def test_trace_directory_removes_only_expired_traces(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            traces_directory = Path(temporary_directory)
            expired_trace = traces_directory / "expired"
            expired_trace.mkdir()
            expired_at = time.time() - 8 * 24 * 60 * 60
            os.utime(expired_trace, (expired_at, expired_at))
            recent_trace = traces_directory / "recent"
            recent_trace.mkdir()

            with patch.object(browser_module, "DEBUG_TRACES_DIR", traces_directory):
                active_trace = browser_module._trace_directory("u@example.com")

            self.assertFalse(expired_trace.exists())
            self.assertTrue(recent_trace.exists())
            self.assertTrue(active_trace.exists())


def _browser_launch_fakes() -> tuple[MagicMock, MagicMock, MagicMock, MagicMock]:
    context = MagicMock()
    context.tracing.start = AsyncMock()
    context.tracing.stop = AsyncMock()
    browser = MagicMock()
    browser.new_context = AsyncMock(return_value=context)
    browser.close = AsyncMock()
    playwright = MagicMock()
    playwright.chromium.launch = AsyncMock(return_value=browser)
    playwright_context = MagicMock()
    playwright_context.__aenter__ = AsyncMock(return_value=playwright)
    playwright_context.__aexit__ = AsyncMock(return_value=False)
    return playwright, browser, context, playwright_context
