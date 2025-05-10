from dataclasses import dataclass, field
from threading import Timer

from datas.protos.non_obf.connection.login_message_pb2 import (
    SelectServerRequest,
)
from datas.protos.non_obf.game.basic_pb2 import (
    TextInformationEvent,
)
from datas.protos.non_obf.game.gamemap_pb2 import (
    MapCurrentEvent,
)

from src.core.config import OCCUPIED_MESSAGE_ID, OCCUPIED_STUCK_LIMIT
from src.core.events_manager.event_manager import ServerTextInformationError
from src.core.frames.frame import Frame

INTERVAL_HANDSHAKE = 10


@dataclass
class ServerFrame(Frame):
    _timer_handshake: Timer | None = field(init=False, default=None)
    _occupied_stuck_counter: int = field(init=False, default=0)

    def __post_init__(self):
        self.game_info_signals.disconnected.connect(self.on_disconnected)
        self.event_manager.on(
            SelectServerRequest,
            self.on_select_server_request,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            TextInformationEvent,
            self.on_text_information_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            MapCurrentEvent,
            self.on_map_current_event,
            originator=self,
            priority=self.priority,
        )

    def on_disconnected(self):
        self._occupied_stuck_counter = 0
        if self._timer_handshake is not None:
            self._timer_handshake.cancel()
            self._timer_handshake = None

    def on_select_server_request(self, msg: SelectServerRequest):
        self.game_state.player.server_id = msg.server
        self.logger.info(f"Connected on server {msg.server}")

    def on_map_current_event(self, _: MapCurrentEvent):
        # New map = progress: only consecutive "occupied" errors count.
        self._occupied_stuck_counter = 0

    def on_text_information_event(self, msg: TextInformationEvent):
        if (
            msg.message_type
            is not TextInformationEvent.TextInformationType.TEXT_INFORMATION_ERROR
        ):
            return

        # Lets us capture the real "occupied" message id from the logs.
        self.logger.debug(
            f"TextInformation error id={msg.message_id} params={msg.parameters}"
        )
        self.event_manager.last_text_information_error = ServerTextInformationError(
            message_id=msg.message_id,
            parameters=tuple(str(parameter) for parameter in msg.parameters),
        )

        if OCCUPIED_MESSAGE_ID is None or msg.message_id != OCCUPIED_MESSAGE_ID:
            return

        self._occupied_stuck_counter += 1
        if self._occupied_stuck_counter > OCCUPIED_STUCK_LIMIT:
            self.logger.warning(
                f"Occupied-stuck detected ({self._occupied_stuck_counter}x), "
                "forcing reconnect to resync"
            )
            self._occupied_stuck_counter = 0
            request_disconnect = self.event_manager.request_disconnect_callback
            if request_disconnect is not None:
                request_disconnect()
