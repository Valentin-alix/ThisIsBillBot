import json
from pathlib import Path
from typing import Any

from src.services.debug_recorder import DebugRecorder


def _read_entries(file_path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in file_path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def test_record_behavior_entry_schema(tmp_path: Path) -> None:
    file_path = tmp_path / "behavior.debug.jsonl"
    recorder = DebugRecorder(file_path=str(file_path))
    recorder.record_behavior(
        behavior="HarvesterBehavior",
        event="finish",
        tree=["HarvesterBehavior[RUNNING] <-", "  CollectBehavior[RUNNING]"],
        from_state="RUNNING",
        to_state="STOPPING",
        error_code="NO_VALID_TRANSITION",
        parent=None,
        reason="stop() called",
    )
    recorder.stop()

    (entry,) = _read_entries(file_path)
    assert entry["categorie"] == "behavior"
    assert entry["behavior"] == "HarvesterBehavior"
    assert entry["event"] == "finish"
    assert entry["error_code"] == "NO_VALID_TRANSITION"
    assert entry["tree"] == [
        "HarvesterBehavior[RUNNING] <-",
        "  CollectBehavior[RUNNING]",
    ]
    assert "datetime" in entry


def test_record_state_entry_schema(tmp_path: Path) -> None:
    file_path = tmp_path / "state.debug.jsonl"
    recorder = DebugRecorder(file_path=str(file_path))
    snapshot: dict[str, Any] = {"map_id": 12345, "in_fight": True, "fight_turn": 3}
    recorder.record_state(trigger="FightBehavior.start", snapshot=snapshot)
    recorder.stop()

    (entry,) = _read_entries(file_path)
    assert entry["categorie"] == "state"
    assert entry["trigger"] == "FightBehavior.start"
    assert entry["snapshot"] == snapshot


def test_record_stuck_entry_schema(tmp_path: Path) -> None:
    file_path = tmp_path / "stuck.debug.jsonl"
    recorder = DebugRecorder(file_path=str(file_path))
    listeners: list[dict[str, Any]] = [
        {
            "msg_type": "FightMapInformationEvent",
            "originator": "AttackerBehavior",
            "age_s": 120.0,
            "without_timeout": True,
        }
    ]
    recorder.record_stuck(
        reason="No bot progress for 95s while FighterBehavior is running",
        seconds_since_progress=95.0,
        tree=["FighterBehavior[RUNNING] <-"],
        snapshot={"map_id": 1},
        listeners=listeners,
        last_message="MapComplementaryInformationEvent",
    )
    recorder.stop()

    (entry,) = _read_entries(file_path)
    assert entry["categorie"] == "stuck"
    assert entry["seconds_since_progress"] == 95.0
    assert entry["listeners"] == listeners
    assert entry["last_message"] == "MapComplementaryInformationEvent"
    assert entry["tree"] == ["FighterBehavior[RUNNING] <-"]
