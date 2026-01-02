from datetime import UTC, datetime
from io import StringIO
from unittest import IsolatedAsyncioTestCase, TestCase
from unittest.mock import AsyncMock, patch

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.mail_providers import (
    manual as manual_module,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web._client.mail_providers.manual import (
    ManualCodeInput,
    wait_for_code_with_manual_fallback,
)

from tests.fixtures.launcher import FakeMailProvider


class TestManualCodeInput(TestCase):
    def test_read_loop_queues_codes_and_ignores_other_lines(self) -> None:
        manual = ManualCodeInput()

        with patch.object(manual_module.sys, "stdin", StringIO("hello\n\n123456\n")):
            manual._read_loop()

        self.assertEqual(manual.poll(), "123456")
        self.assertIsNone(manual.poll())
        self.assertTrue(manual._closed)

    def test_start_returns_none_when_stdin_is_not_a_terminal(self) -> None:
        with patch.object(manual_module.sys, "stdin", StringIO("123456\n")):
            self.assertIsNone(ManualCodeInput.start())


class _StubManualCodeInput:
    def __init__(self, code: str) -> None:
        self._code = code
        self.drained = False

    def drain(self) -> None:
        self.drained = True

    def poll(self) -> str | None:
        return self._code


class TestWaitForCodeWithManualFallback(IsolatedAsyncioTestCase):
    async def test_returns_code_typed_in_terminal_before_provider_resolves(self) -> None:
        manual = _StubManualCodeInput("654321")
        provider = FakeMailProvider(code=None)

        async def never_resolves(*, since: datetime, timeout_seconds: int) -> str | None:
            await manual_module.asyncio.sleep(timeout_seconds)
            return None

        provider.wait_for_code = AsyncMock(side_effect=never_resolves)

        with patch.object(manual_module.ManualCodeInput, "start", return_value=manual):
            code = await wait_for_code_with_manual_fallback(
                provider, since=datetime(2026, 6, 18, 10, 0, tzinfo=UTC), timeout_seconds=5
            )

        self.assertEqual(code, "654321")
        self.assertTrue(manual.drained)

    async def test_returns_code_found_by_provider_when_no_manual_input(self) -> None:
        provider = FakeMailProvider(code="111222")

        with patch.object(manual_module.ManualCodeInput, "start", return_value=None):
            code = await wait_for_code_with_manual_fallback(
                provider, since=datetime(2026, 6, 18, 10, 0, tzinfo=UTC), timeout_seconds=5
            )

        self.assertEqual(code, "111222")
        provider.wait_for_code.assert_awaited_once()

    async def test_returns_none_when_neither_resolves_before_timeout(self) -> None:
        provider = FakeMailProvider(code=None)

        async def never_resolves(*, since: datetime, timeout_seconds: int) -> str | None:
            await manual_module.asyncio.sleep(timeout_seconds + 1)
            return None

        provider.wait_for_code = AsyncMock(side_effect=never_resolves)

        with patch.object(manual_module.ManualCodeInput, "start", return_value=None):
            code = await wait_for_code_with_manual_fallback(
                provider, since=datetime(2026, 6, 18, 10, 0, tzinfo=UTC), timeout_seconds=0
            )

        self.assertIsNone(code)
