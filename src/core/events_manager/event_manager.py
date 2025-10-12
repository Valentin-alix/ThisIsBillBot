import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from threading import _RLock as RLock
from typing import Any, TypeVar, cast

from google.protobuf.message import Message

from DBDofusUnity.datas.protos.non_obf.game.basic_pb2 import DateRequest
from DBDofusUnity.datas.protos.non_obf.game.connection_pb2 import PingRequest

from src import consts
from src.core.events_manager.listener import Listener
from src.core.events_manager.modifier import Modifier
from src.core.events_manager.priority import PriorityEnum
from src.core.signals.event_manager_signals import EventManagerSignals
from src.services.debug_recorder import DebugRecorder
from src.services.logging_utils.contextual_logger import ContextualLogger

T = TypeVar("T", bound=Message)

_HEARTBEAT_MESSAGE_TYPES: frozenset[type[Message]] = frozenset({DateRequest, PingRequest})


@dataclass
class EventManager(ContextualLogger):
    debug_recorder: DebugRecorder | None = None
    modifier_by_type_msg: dict[type[Message], Modifier[Message]] = field(
        init=False, default_factory=dict[type[Message], Modifier[Message]]
    )
    listeners_by_type_msg: defaultdict[type[Message], list[Listener[Message]]] = field(
        init=False, default_factory=lambda: defaultdict(list)
    )
    on_send_game_callback: Callable[[Message], None] | None = field(init=False, default=None)
    on_send_obf_game_callback: Callable[[Message], None] | None = field(init=False, default=None)
    on_send_conn_callback: Callable[[Message], None] | None = field(init=False, default=None)
    request_disconnect_callback: Callable[[], None] | None = field(init=False, default=None)
    is_socket_mode: bool = field(init=False, default=False)
    lock: RLock = field(init=False, default_factory=RLock)
    signals: EventManagerSignals = field(init=False, default_factory=EventManagerSignals)
    last_activity_monotonic: float = field(init=False, default_factory=time.monotonic)
    last_message_activity_monotonic: float = field(init=False, default_factory=time.monotonic)
    last_message_name: str | None = field(init=False, default=None)

    def mark_activity(self) -> None:
        self.last_activity_monotonic = time.monotonic()

    def listeners_debug_snapshot(self) -> list[dict[str, Any]]:
        """Snapshot of registered listeners with their age, sorted oldest
        first. Long-lived listeners without a timeout are the prime suspects
        for an infinite wait."""
        now = datetime.now()
        snapshot: list[dict[str, Any]] = []
        with self.lock:
            for listeners in self.listeners_by_type_msg.values():
                for listener in listeners:
                    age_s = round((now - listener.registered_at).total_seconds(), 1)
                    snapshot.append(
                        {
                            "msg_type": listener.msg_type.__name__,
                            "originator": listener.originator.__class__.__name__,
                            "age_s": age_s,
                            "without_timeout": listener.timeout is None,
                        }
                    )
        snapshot.sort(key=lambda entry: float(entry["age_s"]), reverse=True)
        return snapshot

    def clear_listener_by_origin(self, originator: object) -> None:
        self.logger.debug(f"Clearing all listener from {originator.__class__.__name__}")
        with self.lock:
            listeners_to_remove: list[Listener[Message]] = []
            for listeners in self.listeners_by_type_msg.values():
                for listener in listeners:
                    if listener.originator == originator:
                        listeners_to_remove.append(listener)

            for listener in listeners_to_remove:
                listener.delete()
                self.listeners_by_type_msg[listener.msg_type].remove(listener)

        if listeners_to_remove and consts.DEBUG:
            self.signals.listeners_removed.emit(listeners_to_remove)

    def clear_listener_by_origin_and_type(self, msg_type: type[Message], originator: object) -> None:
        self.logger.debug(f"Clearing listeners {msg_type.__name__} from {originator.__class__.__name__}")
        with self.lock:
            listeners_to_remove: list[Listener[Message]] = []
            for listener in self.listeners_by_type_msg[msg_type]:
                if listener.originator == originator:
                    listeners_to_remove.append(listener)

            for listener in listeners_to_remove:
                listener.delete()
                self.listeners_by_type_msg[msg_type].remove(listener)

        if listeners_to_remove and consts.DEBUG:
            self.signals.listeners_removed.emit(listeners_to_remove)

    def process_msg(self, msg: Message) -> None:
        with self.lock:
            self.last_message_name = msg.__class__.__name__
            self.last_message_activity_monotonic = time.monotonic()
            related_listeners = self.listeners_by_type_msg.get(msg.__class__)
            if not related_listeners:
                return
            listeners_snapshot = list(related_listeners)

        listeners_to_remove: list[Listener[Message]] = []
        for listener in listeners_snapshot:
            with self.lock:
                related_listeners = self.listeners_by_type_msg.get(msg.__class__)
                listener_is_active = (
                    related_listeners is not None and listener in related_listeners and not listener._deleted
                )
            if not listener_is_active:
                self.logger.debug(
                    "Skipping listener removed during dispatch: "
                    f"originator={listener.originator.__class__.__name__}, "
                    f"msg_type={msg.__class__.__name__}"
                )
                continue
            if listener.once:
                listeners_to_remove.append(listener)
            try:
                listener.callback(msg)
            except Exception:
                self.logger.exception(
                    f"Listener {listener.originator.__class__.__name__} "
                    f"raised while handling {msg.__class__.__name__}; "
                    "continuing dispatch"
                )

        with self.lock:
            related_listeners = self.listeners_by_type_msg.get(msg.__class__)
            if related_listeners is None:
                return
            for listener in listeners_to_remove:
                if listener not in related_listeners or listener._deleted:
                    continue
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
            self.logger.debug(
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
                listeners = self.listeners_by_type_msg[part_msg_type]
                listeners.append(cast(Listener[Message], new_listener))
                listeners.sort(key=lambda listener: listener.priority)

            if consts.DEBUG:
                self.signals.listeners_added.emit([new_listener])

    def send(self, msg: Message) -> None:
        self.logger.debug(f"Sending Game MSG {msg.__class__.__name__}")
        with self.lock:
            send_game = self.on_send_game_callback
            if send_game is None:
                raise AttributeError(f"sending msg {msg.__class__} but on_send_callback is not defined !")
        send_game(msg)
        if type(msg) not in _HEARTBEAT_MESSAGE_TYPES:
            self.mark_activity()

    def send_obf_msg(self, msg: Message) -> None:
        self.logger.debug(f"Sending Obf Game MSG {msg.__class__.__name__}")
        with self.lock:
            send_obf_game = self.on_send_obf_game_callback
            if send_obf_game is None:
                raise AttributeError(
                    f"sending msg {msg.__class__} but on_send_obf_game_callback is not defined !"
                )
        send_obf_game(msg)

    def send_connection_msg(self, msg: Message) -> None:
        self.logger.debug(f"Sending Connection MSG {msg.__class__.__name__}")
        with self.lock:
            send_connection = self.on_send_conn_callback
            if send_connection is None:
                raise AttributeError(
                    f"sending msg {msg.__class__.__name__} but on_send_callback is not defined !"
                )
        send_connection(msg)
