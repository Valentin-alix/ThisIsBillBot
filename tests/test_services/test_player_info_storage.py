from datetime import datetime
from pathlib import Path

from pytest import MonkeyPatch

from src.controller.player_info_storage import PlayerInfoSnapshot, PlayerInfoStorage


def _snapshot(character_id: int) -> PlayerInfoSnapshot:
    return PlayerInfoSnapshot(
        updated_at=datetime.now(),
        character_id=character_id,
        character_name=f"character-{character_id}",
        breed_id=1,
        level=20,
        kamas=1_000,
        server_id=1,
        job_levels_by_id={},
        map_id=0,
        has_guild=False,
        guild_chest_tab_number=0,
    )


def test_get_all_snapshots_returns_every_stored_player(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(PlayerInfoStorage, "_FILE_PATH", tmp_path / "bot_player_infos.json")
    storage = PlayerInfoStorage()
    storage.save_snapshot("first@example.com", _snapshot(1))
    storage.save_snapshot("second@example.com", _snapshot(2))

    snapshots = storage.get_all_snapshots()

    assert set(snapshots) == {"first@example.com", "second@example.com"}
    assert snapshots["first@example.com"].character_name == "character-1"
