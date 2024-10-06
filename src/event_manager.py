from collections import defaultdict
from dataclasses import dataclass, field
from typing import Type, Callable, TypeVar, Any

from google.protobuf.message import Message

from src.common.logger import Logger
from src.interfaces.enums.priority import PriorityEnum
from src.interfaces.models.listener import Listener

T = TypeVar("T", bound=Message)


@dataclass
class EventManager:
    listeners_by_type_msg: defaultdict[Type[Message], list[Listener]] = field(
        init=False, default_factory=lambda: defaultdict(list)
    )
    on_send_callback: Callable[[Message], None] | None = field(init=False, default=None)

    def clear_listener_by_origin(self, originator: object) -> None:
        listeners_to_remove: list[Listener] = []

        for listeners in self.listeners_by_type_msg.values():
            for listener in listeners:
                if not listener.originator == originator:
                    continue
                listeners_to_remove.append(listener)

        for listener in listeners_to_remove:
            listener.delete()
            self.listeners_by_type_msg[listener.msg_type].remove(listener)

    def clear_listener_by_origin_and_type(
        self, msg_type: Type[Message], originator: object
    ) -> None:
        listeners_to_remove: list[Listener] = []

        for listener in self.listeners_by_type_msg[msg_type]:
            if listener.originator == originator:
                listeners_to_remove.append(listener)

        for listener in listeners_to_remove:
            listener.delete()
            self.listeners_by_type_msg[msg_type].remove(listener)

    def process_msg(self, msg: Message) -> None:
        related_listeners = self.listeners_by_type_msg.get(msg.__class__, [])
        related_listeners.sort(key=lambda listener: listener.priority)

        listeners_to_remove: list[Listener] = []
        for listener in related_listeners:
            if listener.once:
                listeners_to_remove.append(listener)
            listener.callback(msg)

        for listener in listeners_to_remove:
            # check if listener is not deleted since callback method
            if listener in related_listeners:
                listener.delete()
                related_listeners.remove(listener)

    def on(
        self,
        msg_type: Type[T],
        callback: Callable[[T], Any],
        originator: object,
        once: bool = False,
        priority: PriorityEnum | None = None,
        timeout: float | None = None,
        on_timeout: Callable[[], None] | None = None,
    ) -> None:
        if priority is None:
            priority = getattr(originator, "priority", PriorityEnum.NORMAL)
        self.listeners_by_type_msg[msg_type].append(
            Listener(
                msg_type=msg_type,
                callback=callback,
                once=once,
                originator=originator,
                priority=priority,
                timeout=timeout,
                on_timeout=on_timeout,
            )
        )

    def send(self, msg: Message) -> None:
        Logger().info(f"Sending {msg.__class__}")
        if self.on_send_callback is None:
            raise AttributeError(
                f"sending msg {msg.__class__} but on_send_callback is not defined !"
            )
        self.on_send_callback(msg)
