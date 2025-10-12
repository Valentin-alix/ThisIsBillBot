from dataclasses import dataclass, field
from threading import Event, Thread
from unittest.mock import Mock, patch

import pytest
from google.protobuf.message import Message

from DBDofusUnity.datas.protos.non_obf.game.basic_pb2 import (
    DateRequest,
    SequenceNumberEvent,
    SequenceNumberRequest,
)
from DBDofusUnity.datas.protos.non_obf.game.connection_pb2 import PingRequest

from src.core.behaviors.behavior import Behavior
from src.core.events_manager.event_manager import EventManager
from tests.fixtures.game_state import GameStateContext


class FirstOrigin:
    pass


class SecondOrigin:
    pass


@dataclass
class BlockingBehavior(Behavior):
    run_started: Event = field(default_factory=Event)
    release_run: Event = field(default_factory=Event)

    def run(self) -> None:
        self.run_started.set()
        self.release_run.wait()


def test_successful_non_heartbeat_send_marks_activity() -> None:
    event_manager = EventManager(_logger=Mock())
    sent_messages: list[Message] = []
    event_manager.on_send_game_callback = sent_messages.append
    event_manager.last_activity_monotonic = 10.0

    with patch("src.core.events_manager.event_manager.time.monotonic", return_value=20.0):
        request = SequenceNumberRequest(number=1)
        event_manager.send(request)

    assert sent_messages == [request]
    assert event_manager.last_activity_monotonic == 20.0


@pytest.mark.parametrize(
    "heartbeat_message",
    [DateRequest(), PingRequest(quiet=True)],
)
def test_successful_heartbeat_send_does_not_mark_activity(
    heartbeat_message: Message,
) -> None:
    event_manager = EventManager(_logger=Mock())
    sent_messages: list[Message] = []
    event_manager.on_send_game_callback = sent_messages.append
    event_manager.last_activity_monotonic = 10.0

    with patch("src.core.events_manager.event_manager.time.monotonic", return_value=20.0):
        event_manager.send(heartbeat_message)

    assert sent_messages == [heartbeat_message]
    assert event_manager.last_activity_monotonic == 10.0


def test_failed_send_does_not_mark_activity() -> None:
    event_manager = EventManager(_logger=Mock())
    event_manager.last_activity_monotonic = 10.0

    def fail_send(_message: Message) -> None:
        raise OSError("send failed")

    event_manager.on_send_game_callback = fail_send

    with (
        patch("src.core.events_manager.event_manager.time.monotonic", return_value=20.0),
        pytest.raises(OSError, match="send failed"),
    ):
        event_manager.send(SequenceNumberRequest(number=1))

    assert event_manager.last_activity_monotonic == 10.0


def test_listener_removed_during_dispatch_is_not_called() -> None:
    logger = Mock()
    event_manager = EventManager(_logger=logger)
    event_manager.logger = logger
    calls: list[str] = []
    second_origin = SecondOrigin()

    def first_listener(message: SequenceNumberEvent) -> None:
        del message
        calls.append("first")
        event_manager.clear_listener_by_origin(second_origin)

    def second_listener(message: SequenceNumberEvent) -> None:
        del message
        calls.append("second")

    event_manager.on(
        SequenceNumberEvent,
        first_listener,
        originator=FirstOrigin(),
    )
    event_manager.on(
        SequenceNumberEvent,
        second_listener,
        originator=second_origin,
    )

    event_manager.process_msg(SequenceNumberEvent())

    assert calls == ["first"]
    event_manager.logger.debug.assert_any_call(
        "Skipping listener removed during dispatch: originator=SecondOrigin, msg_type=SequenceNumberEvent"
    )


def test_blocking_behavior_run_does_not_block_listener_cleanup(
    game_state_ctx: GameStateContext,
) -> None:
    event_manager = EventManager(_logger=game_state_ctx.logger)
    cleanup_finished = Event()
    behavior = BlockingBehavior(
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        _logger=game_state_ctx.logger,
    )
    origin = FirstOrigin()
    event_manager.on(
        SequenceNumberEvent,
        lambda _message: None,
        originator=origin,
    )

    behavior_thread = Thread(
        target=lambda: behavior.start(callback=None, parent=None),
    )
    behavior_thread.start()
    assert behavior.run_started.wait(timeout=1)

    def clear_listener() -> None:
        event_manager.clear_listener_by_origin(origin)
        cleanup_finished.set()

    cleanup_thread = Thread(target=clear_listener)
    cleanup_thread.start()
    try:
        assert cleanup_finished.wait(timeout=1)
    finally:
        behavior.release_run.set()
        behavior_thread.join(timeout=1)
        cleanup_thread.join(timeout=1)

    assert not behavior_thread.is_alive()
    assert not cleanup_thread.is_alive()


def test_blocking_listener_does_not_block_listener_cleanup() -> None:
    event_manager = EventManager(_logger=Mock())
    callback_started = Event()
    release_callback = Event()
    cleanup_finished = Event()
    blocking_origin = FirstOrigin()
    removable_origin = SecondOrigin()

    def blocking_listener(_message: SequenceNumberEvent) -> None:
        callback_started.set()
        release_callback.wait()

    event_manager.on(
        SequenceNumberEvent,
        blocking_listener,
        originator=blocking_origin,
    )
    event_manager.on(
        SequenceNumberEvent,
        lambda _message: None,
        originator=removable_origin,
    )

    dispatch_thread = Thread(target=lambda: event_manager.process_msg(SequenceNumberEvent()))
    dispatch_thread.start()
    assert callback_started.wait(timeout=1)

    def clear_listener() -> None:
        event_manager.clear_listener_by_origin(removable_origin)
        cleanup_finished.set()

    cleanup_thread = Thread(target=clear_listener)
    cleanup_thread.start()
    try:
        assert cleanup_finished.wait(timeout=1)
    finally:
        release_callback.set()
        dispatch_thread.join(timeout=1)
        cleanup_thread.join(timeout=1)

    assert not dispatch_thread.is_alive()
    assert not cleanup_thread.is_alive()
