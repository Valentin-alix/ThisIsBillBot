import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import QEventLoop, QTimer
from PyQt6.QtWidgets import QApplication
from pytest import MonkeyPatch

from src.gui.pages.activity import ActivityPage
from src.services.user_activity import UserActivityService
from utils.singleton import Singleton


def _wait_for_updates() -> None:
    loop = QEventLoop()
    QTimer.singleShot(200, loop.quit)
    loop.exec()


def test_activity_entries_refresh_automatically_in_chronological_order(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    app = QApplication.instance() or QApplication([])
    previous = Singleton._instances.pop(UserActivityService, None)
    if isinstance(previous, UserActivityService):
        previous.close()
    monkeypatch.setattr("src.services.user_activity.USER_ACTIVITY_PATH", tmp_path / "activity.json")

    page = ActivityPage()
    page.resize(800, 500)
    page.show()
    service = UserActivityService()
    service.record("info", "old", login="old@example.com")
    service.record("warning", "new", login="new@example.com")
    service.close()
    _wait_for_updates()

    assert page.activity_table.rowCount() == 2
    first_message = page.activity_table.item(0, 3)
    last_message = page.activity_table.item(1, 3)
    assert first_message is not None
    assert last_message is not None
    assert first_message.text() == "old"
    assert last_message.text() == "new"
    scrollbar = page.activity_table.verticalScrollBar()
    assert scrollbar is not None
    assert scrollbar.value() == scrollbar.maximum()

    page.close()
    app.processEvents()
    Singleton._instances.pop(UserActivityService, None)
