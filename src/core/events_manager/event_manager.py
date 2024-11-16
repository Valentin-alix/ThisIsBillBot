from collections import defaultdict
from dataclasses import dataclass, field
from threading import _RLock as RLock
from typing import Any, Callable, Type, TypeVar

from google.protobuf.message import Message

from src.core.events_manager.listener import Listener
from src.core.events_manager.modifier import Modifier
from src.core.events_manager.priority import PriorityEnum
from src.services.logging.logger import Logger

T = TypeVar("T", bound=Message)


@dataclass
class EventManager:
    modifier_by_type_msg: dict[Type[Message], Modifier] = field(
        init=False, default_factory=dict
    )
    listeners_by_type_msg: defaultdict[Type[Message], list[Listener]] = field(
        init=False, default_factory=lambda: defaultdict(list)
    )
    on_send_game_callback: Callable[[Any], None] | None = field(
        init=False, default=None
    )
    on_send_conn_callback: Callable[[Any], None] | None = field(
        init=False, default=None
    )
    lock: RLock = field(init=False, default_factory=RLock)
    logger: Logger

    def clear_listener_by_origin(self, originator: object) -> None:
        self.logger.debug(f"Clear listener by origin : {originator.__class__}")
        with self.lock:
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
        self.logger.debug(
            f"Clear listener by origin: {originator.__class__} and type : {msg_type}"
        )
        with self.lock:
            listeners_to_remove: list[Listener] = []
            for listener in self.listeners_by_type_msg[msg_type]:
                if listener.originator == originator:
                    listeners_to_remove.append(listener)

            for listener in listeners_to_remove:
                listener.delete()
                self.logger.debug(
                    f"Removing {msg_type} with listener {listener.originator.__class__}"
                )
                self.listeners_by_type_msg[msg_type].remove(listener)

    def process_msg(self, msg: Message) -> None:
        with self.lock:
            related_listeners = self.listeners_by_type_msg.get(msg.__class__, [])
            related_listeners.sort(key=lambda listener: listener.priority)

            listeners_to_remove: list[Listener] = []
            for listener in related_listeners[::]:
                if listener.once:
                    listeners_to_remove.append(listener)
                listener.callback(msg)

            for listener in listeners_to_remove:
                # check if listener is not deleted since callback method
                if listener in related_listeners:
                    listener.delete()
                    related_listeners.remove(listener)

    def alter_msg(self, msg: Message) -> tuple[Message | None, bool]:
        with self.lock:
            modifier = self.modifier_by_type_msg.get(msg.__class__, None)
            if modifier is None:
                return msg, False
            self.logger.debug(f"Altering msg : {msg.__class__.__name__}")
            return modifier.callback(msg), True

    def before(
        self,
        msg_type: Type[T],
        callback: Callable[[T], T | None],
        originator: object,
    ) -> None:
        with self.lock:
            if msg_type in self.modifier_by_type_msg:
                self.logger.error(
                    f"{msg_type} already in modifier when using before from originator {originator}, override..."
                )
            self.logger.debug(
                f"Add callback before msg : {msg_type} for originator {originator.__class__}"
            )
            self.modifier_by_type_msg[msg_type] = Modifier(
                callback=callback, originator=originator
            )

    def prevent(self, msg_type: Type[Message], originator: object):
        with self.lock:
            self.logger.debug(
                f"Add prevent msg : {msg_type} for originator {originator.__class__}"
            )
            if msg_type in self.modifier_by_type_msg:
                self.logger.error(
                    f"{msg_type} already in modifier when using prevent from originator {originator}, override..."
                )
            self.modifier_by_type_msg[msg_type] = Modifier(
                callback=self.empty_callback, originator=originator
            )

    def empty_callback(self, msg: Message) -> None:
        return None

    def clear_modifier_by_origin(self, originator: object) -> None:
        self.logger.debug(f"Clear modifiers for originator {originator.__class__}")
        with self.lock:
            self.modifier_by_type_msg = {
                type_msg: modifier
                for type_msg, modifier in self.modifier_by_type_msg.items()
                if modifier.originator != originator
            }

    def clear_modifier_by_origin_and_type(
        self, msg_type: Type[Message], originator: object
    ) -> None:
        self.logger.debug(
            f"Clear modifier type : {msg_type} for originator {originator.__class__}"
        )
        with self.lock:
            modifier = self.modifier_by_type_msg.get(msg_type, None)
            if modifier and modifier.originator == originator:
                del self.modifier_by_type_msg[msg_type]

    def on(
        self,
        msg_type: Type[T],
        callback: Callable[[T], Any],
        originator: object,
        once: bool = False,
        priority: PriorityEnum = PriorityEnum.NORMAL,
        timeout: float | None = None,
        on_timeout: Callable[[], Any] | None = None,
        override_on_self: bool = False,
    ) -> None:
        if (timeout is None) != (on_timeout is None):
            raise ValueError(
                f"Incoherent timeout is {timeout} but on timeout definition : {on_timeout is not None}"
            )
        with self.lock:
            if override_on_self:
                self.logger.debug(
                    f"Overriding {msg_type} with originator {originator.__class__}"
                )
                self.clear_listener_by_origin_and_type(msg_type, originator)
            self.logger.debug(
                f"Adding on callback for msg {msg_type} and originator {originator.__class__}"
            )
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
        self.logger.debug(f"Sending {msg.__class__}")
        with self.lock:
            if self.on_send_game_callback is None:
                raise AttributeError(
                    f"sending msg {msg.__class__} but on_send_callback is not defined !"
                )
            self.on_send_game_callback(msg)

    def send_connection_msg(self, msg: Message) -> None:
        self.logger.debug(f"Sending {msg.__class__}")
        with self.lock:
            if self.on_send_conn_callback is None:
                raise AttributeError(
                    f"sending msg {msg.__class__} but on_send_callback is not defined !"
                )
            self.on_send_conn_callback(msg)
