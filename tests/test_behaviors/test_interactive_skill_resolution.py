"""The skill instance uid must be resolved when the request is sent, not when it is scheduled.

The server disables the skills of an element as soon as somebody uses it, and several seconds can
pass between the moment a behavior decides to interact and the moment the character arrives.
"""

from collections.abc import Callable
from unittest.mock import MagicMock

import pytest
from datas.protos.non_obf.game.common_pb2 import InteractiveElement
from datas.protos.non_obf.game.interactive_element_pb2 import InteractiveUseRequest
from dofus_unity_reader.grid.map_point import MapPoint

from src.core.behaviors.interactives.interactive_behavior import (
    MAX_APPROACH_RETRIES,
    InteractiveBehavior,
    InteractiveError,
)
from src.core.behaviors.movements.map_move_behavior import MapMoveError
from src.core.bot.bot import Bot
from src.core.engine.movements.map.path_finding.movement_path import MovementPath
from src.core.states.map_state import MapState

ELEMENT_ID = 4242
ELEMENT_CELL_ID = 241
PLAYER_CELL_ID = 269
FIRST_SKILL = (69, 1001)
SECOND_SKILL = (71, 1002)


def _element(*skills: tuple[int, int]) -> InteractiveElement:
    return InteractiveElement(
        element_id=ELEMENT_ID,
        on_current_map=True,
        enabled_skills=[
            InteractiveElement.InteractiveElementSkill(skill_id=skill_id, skill_instance_uid=uid)
            for skill_id, uid in skills
        ],
    )


@pytest.fixture
def behavior(runtime_bot: Bot, monkeypatch: pytest.MonkeyPatch) -> InteractiveBehavior:
    monkeypatch.setattr(
        MapState,
        "map_point",
        property(lambda _map_state: MapPoint.from_cell_id(PLAYER_CELL_ID)),
    )
    return runtime_bot.fighter_behavior.random_farm_behavior.edge_behavior.interactive_behavior


@pytest.fixture
def sent_messages(behavior: InteractiveBehavior, monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    send = MagicMock()
    monkeypatch.setattr(behavior.event_manager, "send", send)
    return send


def _mock_approach(
    behavior: InteractiveBehavior, monkeypatch: pytest.MonkeyPatch, end_cell_id: int
) -> None:
    path = MovementPath(
        start=MapPoint.from_cell_id(PLAYER_CELL_ID),
        end=MapPoint.from_cell_id(end_cell_id),
        path=[],
    )
    monkeypatch.setattr(
        behavior.path_finding, "get_interactive_near_path", MagicMock(return_value=path)
    )


def _run_now(range_time: tuple[float, float] | float, func: Callable[[], None]) -> None:
    """Drop the retry delay so the test can drive the retries synchronously."""
    del range_time
    func()


def _use_requests(send: MagicMock) -> list[InteractiveUseRequest]:
    return [
        call.args[0]
        for call in send.call_args_list
        if isinstance(call.args[0], InteractiveUseRequest)
    ]


def _start(behavior: InteractiveBehavior, callback: MagicMock, skill_id: int | None = None) -> None:
    behavior.start(
        callback=callback,
        parent=None,
        element_mp=MapPoint.from_cell_id(ELEMENT_CELL_ID),
        element_id=ELEMENT_ID,
        skill_id=skill_id,
    )


def test_uses_the_first_enabled_skill_by_default(
    behavior: InteractiveBehavior, sent_messages: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    behavior.game_state.interactive.interactive_element_by_id[ELEMENT_ID] = _element(
        FIRST_SKILL, SECOND_SKILL
    )
    _mock_approach(behavior, monkeypatch, PLAYER_CELL_ID)

    _start(behavior, MagicMock())

    requests = _use_requests(sent_messages)
    assert len(requests) == 1
    assert requests[0].skill_instance_uid == FIRST_SKILL[1]


def test_uses_the_requested_skill_not_the_first_one(
    behavior: InteractiveBehavior, sent_messages: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    behavior.game_state.interactive.interactive_element_by_id[ELEMENT_ID] = _element(
        FIRST_SKILL, SECOND_SKILL
    )
    _mock_approach(behavior, monkeypatch, PLAYER_CELL_ID)

    _start(behavior, MagicMock(), skill_id=SECOND_SKILL[0])

    requests = _use_requests(sent_messages)
    assert len(requests) == 1
    assert requests[0].skill_instance_uid == SECOND_SKILL[1]


def test_aborts_when_the_requested_skill_is_not_enabled(
    behavior: InteractiveBehavior, sent_messages: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    behavior.game_state.interactive.interactive_element_by_id[ELEMENT_ID] = _element(FIRST_SKILL)
    _mock_approach(behavior, monkeypatch, PLAYER_CELL_ID)
    callback = MagicMock()

    _start(behavior, callback, skill_id=SECOND_SKILL[0])

    assert _use_requests(sent_messages) == []
    callback.assert_called_once_with(InteractiveError.SKILL_NOT_AVAILABLE)


def test_aborts_when_the_element_has_no_enabled_skill_left(
    behavior: InteractiveBehavior, sent_messages: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    behavior.game_state.interactive.interactive_element_by_id[ELEMENT_ID] = _element()
    _mock_approach(behavior, monkeypatch, PLAYER_CELL_ID)
    callback = MagicMock()

    _start(behavior, callback)

    assert _use_requests(sent_messages) == []
    callback.assert_called_once_with(InteractiveError.SKILL_NOT_AVAILABLE)


def test_gives_up_as_unreachable_after_too_many_canceled_approaches(
    behavior: InteractiveBehavior, sent_messages: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A player parked on the approach cell makes the server truncate every movement. Giving up
    # must report UNREACHABLE_ELEMENT: a bare CANCELED_MOVEMENT is not handled by CollectBehavior,
    # which would then wait forever for a harvest that never happened.
    behavior.game_state.interactive.interactive_element_by_id[ELEMENT_ID] = _element(FIRST_SKILL)
    _mock_approach(behavior, monkeypatch, ELEMENT_CELL_ID)
    monkeypatch.setattr(behavior, "run_timer", _run_now)
    move_start = MagicMock()
    monkeypatch.setattr(behavior.map_move_behavior, "start", move_start)
    callback = MagicMock()

    _start(behavior, callback)
    for _ in range(MAX_APPROACH_RETRIES + 1):
        move_start.call_args.kwargs["callback"](MapMoveError.CANCELED_MOVEMENT)

    assert move_start.call_count == MAX_APPROACH_RETRIES + 1
    assert _use_requests(sent_messages) == []
    callback.assert_called_once_with(InteractiveError.UNREACHABLE_ELEMENT)


def test_aborts_when_the_element_lost_its_skills_during_the_walk(
    behavior: InteractiveBehavior, sent_messages: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The element is still usable when we decide to interact...
    behavior.game_state.interactive.interactive_element_by_id[ELEMENT_ID] = _element(FIRST_SKILL)
    _mock_approach(behavior, monkeypatch, ELEMENT_CELL_ID)
    move_start = MagicMock()
    monkeypatch.setattr(behavior.map_move_behavior, "start", move_start)
    callback = MagicMock()

    _start(behavior, callback)
    move_start.assert_called_once()

    # ... but somebody else harvested it while we were walking.
    behavior.game_state.interactive.interactive_element_by_id[ELEMENT_ID] = _element()
    move_start.call_args.kwargs["callback"](None)

    assert _use_requests(sent_messages) == []
    callback.assert_called_once_with(InteractiveError.SKILL_NOT_AVAILABLE)
