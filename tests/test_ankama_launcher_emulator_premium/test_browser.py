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
        trace_directory = Path("debug/traces/20260829_120000_000000")

        with (
            patch.object(browser_module, "async_playwright", return_value=playwright_context),
            patch.object(browser_module, "_trace_directory", return_value=trace_directory),
        ):
            async with browser_module.launch_browser_context(
                proxy_url=None,
                headless=False,
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
    def test_trace_directory_keeps_only_the_five_most_recent_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            traces_directory = Path(temporary_directory)
            expired_trace = traces_directory / "expired"
            expired_trace.mkdir()
            expired_at = time.time() - 8 * 24 * 60 * 60
            os.utime(expired_trace, (expired_at, expired_at))
            recent_traces: list[Path] = []
            for index in range(5):
                trace_directory = traces_directory / f"recent-{index}"
                trace_directory.mkdir()
                modified_at = time.time() - (index + 1) * 60
                os.utime(trace_directory, (modified_at, modified_at))
                recent_traces.append(trace_directory)
            trace_note = traces_directory / "note.txt"
            trace_note.write_text("keep", encoding="utf-8")

            with patch.object(browser_module, "DEBUG_TRACES_DIR", traces_directory):
                active_trace = browser_module._trace_directory()

            self.assertFalse(expired_trace.exists())
            self.assertTrue(active_trace.exists())
            self.assertRegex(active_trace.name, r"^\d{8}_\d{6}_\d{6}$")
            self.assertTrue(trace_note.exists())
            self.assertTrue(all(trace_directory.exists() for trace_directory in recent_traces[:4]))
            self.assertFalse(recent_traces[4].exists())


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
