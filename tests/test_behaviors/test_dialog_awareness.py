"""Le bot ne rouvre plus ce qui est deja ouvert, et ne ferme qu'au dernier moment."""

from collections.abc import Callable
from threading import Event
from unittest.mock import MagicMock

import pytest

from datas.protos.non_obf.game.dialog_pb2 import DialogLeaveEvent, DialogLeaveRequest
from datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeCraftStartedEvent,
    ExchangeLeaveEvent,
    ExchangeRequestedTradeEvent,
    ExchangeStartedWithStorageEvent,
)
from datas.protos.non_obf.game.contact_pb2 import IgnoreRequest
from datas.protos.non_obf.game.gamemap_pb2 import MapCurrentEvent, MapMovementRequest
from datas.protos.non_obf.game.guild_information_pb2 import (
    GuildInvitationAnswerRequest,
    GuildInvitedEvent,
)
from datas.protos.non_obf.game.npc_pb2 import NpcDialogQuestionEvent
from datas.protos.non_obf.game.roleplay_pb2 import (
    PlayerFightFriendlyAnswerRequest,
    PlayerFightFriendlyRequestedEvent,
)
from datas.protos.non_obf.game.teleportation_pb2 import TeleportDestinationsEvent
from datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
    EntityDisposition,
)
from dofus_unity_reader.grid.map_point import MapPoint
from google.protobuf.message import Message

from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior
from src.core.behaviors.storage.enter_chests.enter_bank_chest_behavior import (
    EnterBankChestBehavior,
)
from src.core.engine.movements.map.path_finding.movement_path import MovementPath
from src.core.events_manager.event_manager import EventManager
from src.core.frames.dialog_frame import DialogFrame
from src.core.states.dialog_state import OpenDialogKind
from src.core.states.map_state import MapState
from tests.fixtures.bot_runtime import make_blocking_state_recovery
from tests.fixtures.game_state import GameStateContext

BANK_STORAGE_SLOT = 20_000
SMALL_STORAGE_SLOT = 50
START_CELL_ID = 305
END_CELL_ID = 306
CRAFT_SKILL_ID = 42


def _run_timer_inline(range_time: tuple[float, float] | float, func: Callable[[], None]) -> None:
    del range_time
    func()


def _make_event_manager(game_state_ctx: GameStateContext) -> tuple[EventManager, list[Message]]:
    event_manager = EventManager(_logger=game_state_ctx.logger)
    sent_messages: list[Message] = []
    event_manager.on_send_game_callback = sent_messages.append
    return event_manager, sent_messages


def _make_dialog_frame(game_state_ctx: GameStateContext) -> EventManager:
    event_manager, _ = _make_event_manager(game_state_ctx)
    DialogFrame(
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        game_info_signals=game_state_ctx.game_info_signals,
        inventory_signals=game_state_ctx.inventory_signals,
        is_playing_event=Event(),
        _logger=game_state_ctx.logger,
    )
    return event_manager


def test_opening_the_personal_chest_is_recorded(game_state_ctx: GameStateContext) -> None:
    event_manager = _make_dialog_frame(game_state_ctx)

    event_manager.process_msg(ExchangeStartedWithStorageEvent(storage_max_slot=BANK_STORAGE_SLOT))

    assert game_state_ctx.game_state.dialog.is_open(OpenDialogKind.BANK_STORAGE)


def test_a_small_storage_is_not_the_personal_chest(game_state_ctx: GameStateContext) -> None:
    event_manager = _make_dialog_frame(game_state_ctx)

    event_manager.process_msg(ExchangeStartedWithStorageEvent(storage_max_slot=SMALL_STORAGE_SLOT))

    assert not game_state_ctx.game_state.dialog.is_any_open


def test_a_workshop_is_recorded_with_its_skill(game_state_ctx: GameStateContext) -> None:
    event_manager = _make_dialog_frame(game_state_ctx)

    event_manager.process_msg(ExchangeCraftStartedEvent(skill_id=CRAFT_SKILL_ID))

    assert game_state_ctx.game_state.dialog.is_open(OpenDialogKind.CRAFT, context_id=CRAFT_SKILL_ID)
    assert not game_state_ctx.game_state.dialog.is_open(
        OpenDialogKind.CRAFT, context_id=CRAFT_SKILL_ID + 1
    )


def test_a_npc_question_is_recorded(game_state_ctx: GameStateContext) -> None:
    event_manager = _make_dialog_frame(game_state_ctx)

    event_manager.process_msg(NpcDialogQuestionEvent(message_id=1))

    assert game_state_ctx.game_state.dialog.is_open(OpenDialogKind.NPC_DIALOG)


def test_the_zaap_destination_screen_is_recorded(game_state_ctx: GameStateContext) -> None:
    event_manager = _make_dialog_frame(game_state_ctx)

    event_manager.process_msg(TeleportDestinationsEvent())

    assert game_state_ctx.game_state.dialog.is_open(OpenDialogKind.ZAAP_DESTINATIONS)


def test_a_trade_request_from_another_player_is_recorded(
    game_state_ctx: GameStateContext,
) -> None:
    event_manager = _make_dialog_frame(game_state_ctx)

    event_manager.process_msg(ExchangeRequestedTradeEvent(source_id=1, target_id=2))

    assert game_state_ctx.game_state.dialog.is_open(OpenDialogKind.TRADE_REQUEST)


def test_leaving_an_exchange_clears_the_state(game_state_ctx: GameStateContext) -> None:
    event_manager = _make_dialog_frame(game_state_ctx)
    event_manager.process_msg(ExchangeStartedWithStorageEvent(storage_max_slot=BANK_STORAGE_SLOT))

    event_manager.process_msg(ExchangeLeaveEvent())

    assert not game_state_ctx.game_state.dialog.is_any_open


def test_changing_map_clears_the_state(game_state_ctx: GameStateContext) -> None:
    event_manager = _make_dialog_frame(game_state_ctx)
    event_manager.process_msg(ExchangeStartedWithStorageEvent(storage_max_slot=BANK_STORAGE_SLOT))

    event_manager.process_msg(MapCurrentEvent(map_id=1))

    assert not game_state_ctx.game_state.dialog.is_any_open


def test_an_open_bank_is_reused_instead_of_being_reopened(
    game_state_ctx: GameStateContext,
) -> None:
    event_manager, sent_messages = _make_event_manager(game_state_ctx)
    game_state_ctx.game_state.player.level = 200
    game_state_ctx.game_state.dialog.set_open(OpenDialogKind.BANK_STORAGE)
    auto_trip_behavior = MagicMock()
    behavior = EnterBankChestBehavior(
        recovery=make_blocking_state_recovery(),
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        _logger=game_state_ctx.logger,
        npc_dialog_behavior=MagicMock(),
        auto_trip_world_behavior=auto_trip_behavior,
    )
    finished: list[str | None] = []

    behavior.start(callback=finished.append, parent=None)

    assert finished == [None]
    assert sent_messages == []
    auto_trip_behavior.start.assert_not_called()


def _make_map_move_behavior(
    game_state_ctx: GameStateContext,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[MapMoveBehavior, list[Message]]:
    monkeypatch.setattr(
        MapState,
        "map_point",
        property(lambda _map_state: MapPoint.from_cell_id(START_CELL_ID)),
    )
    event_manager, sent_messages = _make_event_manager(game_state_ctx)
    behavior = MapMoveBehavior(
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        path_finding=game_state_ctx.pathfinding,
        _logger=game_state_ctx.logger,
    )
    behavior.run_timer = _run_timer_inline
    return behavior, sent_messages


def _move_path() -> MovementPath:
    return MovementPath(
        start=MapPoint.from_cell_id(START_CELL_ID),
        end=MapPoint.from_cell_id(END_CELL_ID),
        path=MovementPath.get_path_elements_from_cells([START_CELL_ID, END_CELL_ID]),
    )


def test_moving_closes_whatever_is_still_open_first(
    game_state_ctx: GameStateContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    behavior, sent_messages = _make_map_move_behavior(game_state_ctx, monkeypatch)
    game_state_ctx.game_state.dialog.set_open(OpenDialogKind.BANK_STORAGE)

    behavior.start(callback=None, parent=None, move_path=_move_path())

    assert [type(message) for message in sent_messages] == [DialogLeaveRequest]

    game_state_ctx.game_state.dialog.clear_state()
    behavior.event_manager.process_msg(ExchangeLeaveEvent())

    assert [type(message) for message in sent_messages] == [DialogLeaveRequest, MapMovementRequest]


def test_moving_with_nothing_open_goes_straight_ahead(
    game_state_ctx: GameStateContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    behavior, sent_messages = _make_map_move_behavior(game_state_ctx, monkeypatch)

    behavior.start(callback=None, parent=None, move_path=_move_path())

    assert [type(message) for message in sent_messages] == [MapMovementRequest]


def test_leaving_a_dialog_that_is_not_open_sends_nothing(
    game_state_ctx: GameStateContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    behavior, sent_messages = _make_map_move_behavior(game_state_ctx, monkeypatch)
    left: list[ExchangeLeaveEvent] = []

    behavior.start(callback=None, parent=None, move_path=_move_path())
    sent_messages.clear()
    behavior.leave_dialog(on_leave_callback=left.append)

    assert sent_messages == []
    assert len(left) == 1


def test_closing_a_npc_dialog_waits_for_the_dialog_leave_event(
    game_state_ctx: GameStateContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    behavior, sent_messages = _make_map_move_behavior(game_state_ctx, monkeypatch)
    behavior.start(callback=None, parent=None, move_path=_move_path())
    game_state_ctx.game_state.dialog.set_open(OpenDialogKind.NPC_DIALOG)
    closed: list[bool] = []
    sent_messages.clear()

    behavior.ensure_dialog_closed(lambda: closed.append(True))

    assert [type(message) for message in sent_messages] == [DialogLeaveRequest]
    assert closed == []

    behavior.event_manager.process_msg(DialogLeaveEvent())

    assert closed == [True]


PLAYER_ID = 42
CHALLENGER_ID = 7
CHALLENGER_NAME = "Provocateur"
FIGHT_ID = 1234


def _add_challenger(game_state_ctx: GameStateContext) -> None:
    actor = ActorPositionInformation(
        actor_id=CHALLENGER_ID,
        disposition=EntityDisposition(entity_id=CHALLENGER_ID, cell_id=1),
    )
    actor.actor_information.role_play_actor.named_actor.name = CHALLENGER_NAME
    game_state_ctx.game_state.entity.set_actor(actor)


def _challenge(target_id: int = PLAYER_ID) -> PlayerFightFriendlyRequestedEvent:
    return PlayerFightFriendlyRequestedEvent(
        fight_id=FIGHT_ID, source_id=CHALLENGER_ID, target_id=target_id
    )


def test_a_challenge_aimed_at_us_is_recorded(game_state_ctx: GameStateContext) -> None:
    game_state_ctx.game_state.player.character_id = PLAYER_ID
    event_manager = _make_dialog_frame(game_state_ctx)
    _add_challenger(game_state_ctx)

    event_manager.process_msg(_challenge())

    dialog = game_state_ctx.game_state.dialog
    assert dialog.is_open(OpenDialogKind.FRIENDLY_FIGHT_REQUEST, context_id=FIGHT_ID)
    assert dialog.context_name == CHALLENGER_NAME


def test_a_challenge_aimed_at_someone_else_is_left_alone(
    game_state_ctx: GameStateContext,
) -> None:
    game_state_ctx.game_state.player.character_id = PLAYER_ID
    event_manager = _make_dialog_frame(game_state_ctx)

    event_manager.process_msg(_challenge(target_id=PLAYER_ID + 1))

    assert not game_state_ctx.game_state.dialog.is_any_open


def test_a_guild_invitation_is_recorded(game_state_ctx: GameStateContext) -> None:
    event_manager = _make_dialog_frame(game_state_ctx)

    event_manager.process_msg(GuildInvitedEvent(recruiter_name="Recruteur"))

    assert game_state_ctx.game_state.dialog.is_open(OpenDialogKind.GUILD_INVITE)


def test_a_pending_challenge_is_declined_when_the_bot_needs_the_screen(
    game_state_ctx: GameStateContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    behavior, sent_messages = _make_map_move_behavior(game_state_ctx, monkeypatch)
    game_state_ctx.game_state.dialog.set_open(
        OpenDialogKind.FRIENDLY_FIGHT_REQUEST,
        context_id=FIGHT_ID,
        context_name=CHALLENGER_NAME,
    )

    behavior.start(callback=None, parent=None, move_path=_move_path())

    assert [type(message) for message in sent_messages] == [
        IgnoreRequest,
        PlayerFightFriendlyAnswerRequest,
        MapMovementRequest,
    ]
    ignore_request = sent_messages[0]
    answer = sent_messages[1]
    assert isinstance(ignore_request, IgnoreRequest)
    assert isinstance(answer, PlayerFightFriendlyAnswerRequest)
    assert ignore_request.player_search.search_by_character_name.name == CHALLENGER_NAME
    assert answer.fight_id == FIGHT_ID
    assert answer.accept is False


def test_a_pending_guild_invitation_is_declined_when_the_bot_needs_the_screen(
    game_state_ctx: GameStateContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    behavior, sent_messages = _make_map_move_behavior(game_state_ctx, monkeypatch)
    game_state_ctx.game_state.dialog.set_open(OpenDialogKind.GUILD_INVITE)

    behavior.start(callback=None, parent=None, move_path=_move_path())

    assert [type(message) for message in sent_messages] == [
        GuildInvitationAnswerRequest,
        MapMovementRequest,
    ]
    answer = sent_messages[0]
    assert isinstance(answer, GuildInvitationAnswerRequest)
    assert answer.accepted is False
