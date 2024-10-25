from dataclasses import dataclass, field
from threading import Timer

from d3_mapping.resources.protos.game.character_management_pb2 import (
    CharacterSelectionEvent,
)
from d3_mapping.resources.protos.game.connection_pb2 import PingRequest

from src.core.frames.frame import Frame

INTERVAL_HANDSHAKE = 10


@dataclass
class ServerFrame(Frame):
    _timer_handshake: Timer | None = field(init=False, default=None)

    def __post_init__(self):
        self.game_info_signals.disconnected.connect(self.on_disconnected)
        self.event_manager.on(
            CharacterSelectionEvent,
            self.on_character_selection_event,
            originator=self,
            priority=self.priority,
        )

    def on_disconnected(self):
        if self._timer_handshake is not None:
            self._timer_handshake.cancel()
            self._timer_handshake = None

    def on_character_selection_event(self, msg: CharacterSelectionEvent):
        self._timer_handshake = Timer(
            interval=INTERVAL_HANDSHAKE, function=self.handle_handshake
        )
        self._timer_handshake.start()

    def handle_handshake(self):
        if self.is_playing_event.is_set():
            req = PingRequest(quiet=True)
            self.event_manager.send(req)
        self._timer_handshake = Timer(
            interval=INTERVAL_HANDSHAKE, function=self.handle_handshake
        )
        self._timer_handshake.start()
