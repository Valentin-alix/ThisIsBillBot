from unittest.mock import Mock

from datas.protos.non_obf.game.basic_pb2 import SequenceNumberEvent

from src.core.events_manager.event_manager import EventManager


class FirstOrigin:
    pass


class SecondOrigin:
    pass


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
    event_manager.logger.warning.assert_called_once_with(
        "Skipping listener removed during dispatch: "
        "originator=SecondOrigin, msg_type=SequenceNumberEvent"
    )
