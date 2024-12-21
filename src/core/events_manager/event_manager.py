from collections import defaultdict
from dataclasses import dataclass, field
from threading import _RLock as RLock
from typing import Callable, TypeVar, cast

from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message

from src.core.events_manager.listener import Listener
from src.core.events_manager.modifier import Modifier
from src.core.events_manager.priority import PriorityEnum
from src.core.signals.event_manager_signals import EventManagerSignals
from src.services.logging.contextual_logger import ContextualLogger

T = TypeVar("T", bound=Message)


@dataclass
class EventManager(ContextualLogger):
    modifier_by_type_msg: dict[type[Message], Modifier[Message]] = field(
        init=False, default_factory=dict[type[Message], Modifier[Message]]
    )
    listeners_by_type_msg: defaultdict[type[Message], list[Listener[Message]]] = field(
        init=False, default_factory=lambda: defaultdict(list)
    )
    on_send_game_callback: Callable[[Message], None] | None = field(
        init=False, default=None
    )
    on_send_obf_game_callback: Callable[[Message], None] | None = field(
        init=False, default=None
    )
    on_send_conn_callback: Callable[[Message], None] | None = field(
        init=False, default=None
    )
    lock: RLock = field(init=False)
    signals: EventManagerSignals = field(init=False)

    def __post_init__(self) -> None:
        self.lock = RLock()
        self.signals = EventManagerSignals()

    def clear_listener_by_origin(self, originator: object) -> None:
        self.logger.info(f"Clearing all listener from {originator.__class__.__name__}")
        with self.lock:
            listeners_to_remove: list[Listener[Message]] = []
            for listeners in self.listeners_by_type_msg.values():
                for listener in listeners:
                    if listener.originator == originator:
                        listeners_to_remove.append(listener)

            for listener in listeners_to_remove:
                listener.delete()
                self.listeners_by_type_msg[listener.msg_type].remove(listener)

        if listeners_to_remove:
            self.signals.listeners_removed.emit(listeners_to_remove)

    def clear_listener_by_origin_and_type(
        self, msg_type: type[Message], originator: object
    ) -> None:
        self.logger.debug(
            f"Clearing listeners {msg_type.__name__} from {originator.__class__.__name__}"
        )
        with self.lock:
            listeners_to_remove: list[Listener[Message]] = []
            for listener in self.listeners_by_type_msg[msg_type]:
                if listener.originator == originator:
                    listeners_to_remove.append(listener)

            for listener in listeners_to_remove:
                listener.delete()
                self.listeners_by_type_msg[msg_type].remove(listener)

        if listeners_to_remove:
            self.signals.listeners_removed.emit(listeners_to_remove)

    def process_msg(self, msg: Message) -> None:
        self.logger.debug(
            f"Received msg {msg.__class__.__name__}, content : {MessageToDict(msg)}"
        )
        with self.lock:
            related_listeners = self.listeners_by_type_msg.get(msg.__class__, [])
            related_listeners.sort(key=lambda listener: listener.priority)

            listeners_to_remove: list[Listener[Message]] = []
            for listener in related_listeners[::]:
                if listener.once:
                    listeners_to_remove.append(listener)
                listener.callback(msg)

            for listener in listeners_to_remove:
                if listener in related_listeners:
                    listener.delete()
                    related_listeners.remove(listener)

    def alter_msg(self, msg: Message) -> tuple[Message | None, bool]:
        with self.lock:
            modifier = self.modifier_by_type_msg.get(msg.__class__)
            if modifier is None:
                return msg, False
            return modifier.callback(msg), True

    def before(
        self,
        msg_type: type[T],
        callback: Callable[[T], T | None],
        originator: object,
    ) -> None:
        with self.lock:
            if msg_type in self.modifier_by_type_msg:
                self.logger.warning(
                    f"Overriding modifier for {msg_type.__name__} (originator: {originator.__class__.__name__})"
                )
            modifier = Modifier(callback=callback, originator=originator)
            self.modifier_by_type_msg[msg_type] = cast(Modifier[Message], modifier)

    def prevent(self, msg_type: type[Message], originator: object) -> None:
        with self.lock:
            if msg_type in self.modifier_by_type_msg:
                self.logger.warning(
                    f"Overriding prevent for {msg_type.__name__} (originator: {originator.__class__.__name__})"
                )
            self.modifier_by_type_msg[msg_type] = Modifier(
                callback=self.empty_callback, originator=originator
            )

    def empty_callback(self, msg: Message) -> None:
        return None

    def clear_modifier_by_origin(self, originator: object) -> None:
        with self.lock:
            self.modifier_by_type_msg = {
                type_msg: modifier
                for type_msg, modifier in self.modifier_by_type_msg.items()
                if modifier.originator != originator
            }

    def clear_modifier_by_origin_and_type(
        self, msg_type: type[Message], originator: object
    ) -> None:
        with self.lock:
            modifier = self.modifier_by_type_msg.get(msg_type)
            if modifier is not None and modifier.originator == originator:
                del self.modifier_by_type_msg[msg_type]

    def on(
        self,
        msg_type: type[T] | list[type[T]],
        callback: Callable[[T], None],
        originator: object,
        once: bool = False,
        priority: PriorityEnum = PriorityEnum.NORMAL,
        timeout: float | None = None,
        on_timeout: Callable[[], None] | None = None,
        override_on_self: bool = False,
    ) -> None:
        if not isinstance(msg_type, list):
            msg_type = [msg_type]

        for part_msg_type in msg_type:
            self.logger.info(
                f"Adding listener {part_msg_type.__name__} from {originator.__class__.__name__}"
            )
            if (timeout is None) != (on_timeout is None):
                raise ValueError(
                    f"Incoherent timeout is {timeout} but on timeout definition : {on_timeout is not None}"
                )
            with self.lock:
                if override_on_self:
                    self.clear_listener_by_origin_and_type(part_msg_type, originator)

                new_listener = Listener(
                    msg_type=part_msg_type,
                    callback=callback,
                    once=once,
                    originator=originator,
                    priority=priority,
                    timeout=timeout,
                    on_timeout=on_timeout,
                    logger=self.logger,
                )
                self.listeners_by_type_msg[part_msg_type].append(
                    cast(Listener[Message], new_listener)
                )

            self.signals.listeners_added.emit([new_listener])

    def send(self, msg: Message) -> None:
        self.logger.debug(f"Sending Game MSG {msg.__class__.__name__}")
        with self.lock:
            if self.on_send_game_callback is None:
                raise AttributeError(
                    f"sending msg {msg.__class__} but on_send_callback is not defined !"
                )
            self.on_send_game_callback(msg)

    def send_obf_msg(self, msg: Message) -> None:
        self.logger.debug(f"Sending Obf Game MSG {msg.__class__.__name__}")
        with self.lock:
            if self.on_send_obf_game_callback is None:
                raise AttributeError(
                    f"sending msg {msg.__class__} but on_send_obf_game_callback is not defined !"
                )
            self.on_send_obf_game_callback(msg)

    def send_connection_msg(self, msg: Message) -> None:
        self.logger.debug(f"Sending Connection MSG {msg.__class__.__name__}")
        with self.lock:
            if self.on_send_conn_callback is None:
                raise AttributeError(
                    f"sending msg {msg.__class__.__name__} but on_send_callback is not defined !"
                )
            self.on_send_conn_callback(msg)
