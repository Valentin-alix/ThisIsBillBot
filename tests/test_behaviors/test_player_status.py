import pytest
from google.protobuf.message import Message

from DBDofusUnity.datas.protos.non_obf.game.character_pb2 import PlayerStatusUpdateRequest
from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import CharacterStatus
from src.core.bot.bot import Bot
from src.core.frames.player_frame import PlayerFrame


@pytest.mark.parametrize("playing", [False, True])
def test_connection_ready_sets_solo_only_for_automation(runtime_bot: Bot, playing: bool) -> None:
    sent: list[Message] = []
    runtime_bot.event_manager.on_send_game_callback = sent.append
    if playing:
        runtime_bot.is_playing_event.set()
    else:
        runtime_bot.is_playing_event.clear()
    frame = next(frame for frame in runtime_bot.frames if isinstance(frame, PlayerFrame))
    frame.on_ready_to_play()
    expected = [PlayerStatusUpdateRequest(status=CharacterStatus(status=CharacterStatus.STATUS_SOLO))]
    assert sent == (expected if playing else [])


@pytest.mark.parametrize("ready", [False, True])
def test_starting_automation_sets_solo_when_character_is_ready(runtime_bot: Bot, ready: bool) -> None:
    sent: list[Message] = []
    runtime_bot.event_manager.on_send_game_callback = sent.append
    if ready:
        runtime_bot.is_ready_to_play_event.set()
    else:
        runtime_bot.is_ready_to_play_event.clear()
    runtime_bot.behavior_coordinator.on_play(from_manual_play=False)
    expected = [PlayerStatusUpdateRequest(status=CharacterStatus(status=CharacterStatus.STATUS_SOLO))]
    assert sent == (expected if ready else [])
