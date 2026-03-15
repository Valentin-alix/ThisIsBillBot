import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from PyQt6.QtWidgets import QDialog, QWidget
from PyQt6.QtCore import QEventLoop, QTimer
from qfluentwidgets import LineEdit

from ankama_launcher_emulator.web._client.mail_providers.manual import wait_for_code_with_manual_fallback
from src.gui.components.manual_confirmation import ManualConfirmationDialogs
from src.services.manual_confirmation import ManualConfirmationBroker, manual_confirmation


def _process_events() -> None:
    loop = QEventLoop()
    QTimer.singleShot(10, loop.quit)
    loop.exec()


def test_requests_are_correlated_and_expiration_and_shutdown_release_waiters() -> None:
    async def scenario() -> None:
        broker = ManualConfirmationBroker()
        requests: list[str] = []
        broker.install(lambda request: requests.append(request.identifier), lambda _: None)
        first = asyncio.create_task(broker.wait("first@example.com", 10))
        second = asyncio.create_task(broker.wait("second@example.com", 10))
        await asyncio.sleep(0)
        with pytest.raises(ValueError):
            broker.submit(requests[0], "123")
        broker.submit(requests[1], "654321")
        assert await second == "654321"
        assert not first.done()
        broker.shutdown()
        assert await first is None
        broker.install(lambda request: requests.append(request.identifier), lambda _: None)
        assert await broker.wait("expired@example.com", 0.001) is None
        assert not broker.is_pending(requests[-1])
        broker.submit(requests[-1], "111111")

    asyncio.run(scenario())


def test_gui_code_entry_and_cancellation() -> None:
    window = QWidget()
    dialogs = ManualConfirmationDialogs(window)

    async def scenario() -> None:
        pending = asyncio.create_task(manual_confirmation.wait("manual@example.com", 5))
        await asyncio.sleep(0)
        _process_events()
        dialog = next(iter(dialogs.dialogs.values()))
        edit = dialog.findChild(LineEdit)
        assert edit is not None
        edit.setText("123456")
        dialog.accept()
        assert await pending == "123456"
        assert not dialogs.dialogs
        cancelled = asyncio.create_task(manual_confirmation.wait("cancel@example.com", 5))
        await asyncio.sleep(0)
        _process_events()
        next(iter(dialogs.dialogs.values())).done(QDialog.DialogCode.Rejected)
        assert await cancelled is None

    try:
        asyncio.run(scenario())
    finally:
        dialogs.shutdown()
        window.deleteLater()
        _process_events()


def test_mailbox_result_closes_gui_request_and_gui_cancel_stops_polling() -> None:
    async def scenario() -> None:
        identifiers: list[str] = []
        closed: list[str] = []
        manual_confirmation.install(lambda request: identifiers.append(request.identifier), closed.append)
        provider = AsyncMock()
        provider.wait_for_code.return_value = "123456"
        assert (
            await wait_for_code_with_manual_fallback(
                provider, since=datetime.now(UTC), timeout_seconds=5, email="mail@example.com"
            )
            == "123456"
        )
        assert identifiers[-1] in closed
        cancelled = asyncio.Event()

        async def wait_forever(**_kwargs: object) -> str:
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()
            return ""

        provider.wait_for_code.side_effect = wait_forever
        task = asyncio.create_task(
            wait_for_code_with_manual_fallback(
                provider, since=datetime.now(UTC), timeout_seconds=5, email="mail@example.com"
            )
        )
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        manual_confirmation.submit(identifiers[-1], None)
        assert await task is None
        assert cancelled.is_set()

    try:
        asyncio.run(scenario())
    finally:
        manual_confirmation.shutdown()
