from abc import ABC
from dataclasses import dataclass
from typing import Callable

from d3_database.protos.non_obf.game.dialog_pb2 import DialogLeaveRequest
from d3_database.protos.non_obf.game.exchange_pb2 import ExchangeLeaveEvent
from src.core.behaviors.behavior import Behavior


@dataclass
class DialogHandlerBehavior(Behavior, ABC):
    def leave_dialog(
        self, on_leave_callback: Callable[[ExchangeLeaveEvent], None] | None = None
    ) -> None:
        if on_leave_callback:
            self.event_manager.on(
                ExchangeLeaveEvent,
                callback=on_leave_callback,
                originator=self,
                once=True,
                override_on_self=True,
            )
        self.event_manager.send(DialogLeaveRequest())
