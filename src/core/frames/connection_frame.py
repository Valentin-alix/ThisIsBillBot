from dataclasses import dataclass, field
from threading import Timer

from protos.game.character_management_pb2 import CharacterSelectionEvent
from protos.game.connection_pb2 import PingRequest, ReloginTokenEvent
from src.core.frames.frame import Frame
from src.signals.player_signals import GameInfoSignals

INTERVAL_HANDSHAKE = 20


@dataclass
class ConnectionFrame(Frame):
    timer_handshake: Timer | None = field(init=False, default=None)
    game_info_signals: GameInfoSignals

    def __post_init__(self):
        self.game_info_signals.disconnected.connect(self.on_disconnected)
        self.event_manager.on(
            ReloginTokenEvent, lambda _: self.on_disconnected(), originator=self
        )
        self.event_manager.on(
            CharacterSelectionEvent, self.on_character_selection_event, originator=self
        )

    def on_disconnected(self):
        if self.timer_handshake is not None:
            self.timer_handshake.cancel()
            self.timer_handshake = None

    def on_character_selection_event(self, msg: CharacterSelectionEvent):
        self.timer_handshake = Timer(
            interval=INTERVAL_HANDSHAKE, function=self.handle_handshake
        )
        self.timer_handshake.start()

    def handle_handshake(self):
        req = PingRequest(quiet=True)
        self.event_manager.send(req)
        self.timer_handshake = Timer(
            interval=INTERVAL_HANDSHAKE, function=self.handle_handshake
        )
        self.timer_handshake.start()
