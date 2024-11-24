from dataclasses import dataclass, field
from threading import Timer

from d3_database.protos.non_obf.connection.login_message_pb2 import (
    SelectServerRequest,
)
from src.core.frames.frame import Frame

INTERVAL_HANDSHAKE = 10


@dataclass
class ServerFrame(Frame):
    _timer_handshake: Timer | None = field(init=False, default=None)

    def __post_init__(self):
        self.game_info_signals.disconnected.connect(self.on_disconnected)
        self.event_manager.on(
            SelectServerRequest,
            self.on_select_server_request,
            originator=self,
            priority=self.priority,
        )

    def on_disconnected(self):
        if self._timer_handshake is not None:
            self._timer_handshake.cancel()
            self._timer_handshake = None

    def on_select_server_request(self, msg: SelectServerRequest):
        self.game_state.player.server_id = msg.server
        self.logger.info(f"Connected on server {msg.server}")
