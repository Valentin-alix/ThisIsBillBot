from pathlib import Path

from pytest import MonkeyPatch

from src.services.user_activity import UserActivityFile, UserActivityService
from utils.singleton import Singleton


def _create_service(monkeypatch: MonkeyPatch, path: Path) -> UserActivityService:
    previous = Singleton._instances.pop(UserActivityService, None)
    if isinstance(previous, UserActivityService):
        previous.close()
    monkeypatch.setattr("src.services.user_activity.USER_ACTIVITY_PATH", path)
    return UserActivityService()


def test_activity_history_is_bounded_and_keeps_newest_entries(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    activity_path = tmp_path / "activity.json"
    service = _create_service(monkeypatch, activity_path)

    for index in range(501):
        service.record("info", f"event-{index}", login="bot@example.com")

    service.close()
    entries = service.recent()

    assert len(entries) == 500
    assert entries[0].message == "event-1"
    assert entries[-1].message == "event-500"
    assert len(UserActivityFile.model_validate_json(activity_path.read_text()).entries) == 500


def test_corrupt_activity_history_does_not_interrupt_recording(
    monkeypatch: MonkeyPatch, tmp_path: Path
) -> None:
    activity_path = tmp_path / "activity.json"
    activity_path.write_text("not-json", encoding="utf-8")
    service = _create_service(monkeypatch, activity_path)
    service.record("info", "safe event")

    service.close()
    assert service.recent()[0].message == "safe event"
    assert UserActivityFile.model_validate_json(activity_path.read_text()).entries[0].message == "safe event"
