from collections import defaultdict
from dataclasses import dataclass, field
from typing import Type, Callable

from google.protobuf.message import Message

from src.interfaces.enums.priority import PriorityEnum
from src.interfaces.models.listener import Listener


@dataclass
class EventManager:
    listeners_by_type_msg: dict[Type[Message], list[Listener]] = field(
        init=False, default_factory=lambda: defaultdict(list)
    )
    on_send_callback: Callable[[Message], None] | None = field(init=False, default=None)

    def clear_listener_by_origin(self, originator: object) -> None:
        for msg_type, listeners in self.listeners_by_type_msg.items():
            self.listeners_by_type_msg[msg_type] = [
                listener for listener in listeners if listener.originator != originator
            ]

    def process_msg(self, msg: Message) -> None:
        related_listeners = sorted(
            self.listeners_by_type_msg.get(msg.__class__, []),
            key=lambda listener: listener.priority,
        )
        for listener in related_listeners:
            listener.callback(msg)
            if listener.once and listener in related_listeners:
                related_listeners.remove(listener)

    def on(
        self,
        msg_type: Type[Message],
        callback: Callable,
        originator: object | None = None,
        once: bool = False,
        priority: PriorityEnum = PriorityEnum.NORMAL,
    ) -> None:
        self.listeners_by_type_msg[msg_type].append(
            Listener(
                callback=callback, once=once, originator=originator, priority=priority
            )
        )

    def send(self, msg: Message) -> None:
        if self.on_send_callback is None:
            raise AttributeError(
                f"sending msg {msg.__class__.__name__} but on_send_callback is not defined !"
            )
        self.on_send_callback(msg)
