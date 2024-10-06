from collections import defaultdict
from dataclasses import dataclass, field
from typing import Type, Callable

from google.protobuf.message import Message
from sortedcontainers import SortedList

from src.common.logger import Logger
from src.interfaces.enums.priority import PriorityEnum
from src.interfaces.models.listener import Listener


@dataclass
class EventManager:
    listeners_by_type_msg: dict[Type[Message], SortedList[Listener]] = field(
        init=False, default_factory=lambda: defaultdict(SortedList)
    )
    on_send_callback: Callable[[Message], None] | None = field(init=False, default=None)

    def clear_listener_by_origin(self, originator: object) -> None:
        for listeners in self.listeners_by_type_msg.values():
            for listener in listeners[:]:
                if listener.originator == originator:
                    listeners.remove(listener)

    def clear_listener_by_origin_and_type(
        self, msg_type: Type[Message], originator: object
    ) -> None:
        for listener in self.listeners_by_type_msg[msg_type][:]:
            if listener.originator == originator:
                self.listeners_by_type_msg[msg_type].remove(listener)

    def process_msg(self, msg: Message) -> None:
        related_listeners = self.listeners_by_type_msg.get(msg.__class__, None)
        if not related_listeners:
            return None
        for listener in related_listeners[:]:
            listener.callback(msg)
            if listener.once and listener in related_listeners:
                related_listeners.remove(listener)

    def on(
        self,
        msg_type: Type[Message],
        callback: Callable,
        originator: object,
        once: bool = False,
        priority: PriorityEnum | None = None,
    ) -> None:
        if priority is None:
            priority = getattr(originator, "priority", PriorityEnum.NORMAL)
        self.listeners_by_type_msg[msg_type].add(
            Listener(
                callback=callback, once=once, originator=originator, priority=priority
            )
        )

    def send(self, msg: Message) -> None:
        Logger().info(f"Sending {msg.__class__}")
        if self.on_send_callback is None:
            raise AttributeError(
                f"sending msg {msg.__class__} but on_send_callback is not defined !"
            )
        self.on_send_callback(msg)
