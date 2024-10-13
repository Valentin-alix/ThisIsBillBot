from dataclasses import field, dataclass
from threading import Timer

from protos.connection.login_message_pb2 import Request
from protos.connection.login_message_pb2 import (
    SelectServerRequest,
    IdentificationResponse,
)
from protos.game.basic_pb2 import (
    SequenceNumberEvent,
    SequenceNumberRequest,
    BasicLatencyStatsEvent,
    BasicLatencyStatsRequest,
)
from protos.game.character_management_pb2 import CharacterSelectionEvent
from protos.game.connection_pb2 import PingRequest
from src.core.frames.frame import Frame

INTERVAL_HANDSHAKE = 20


@dataclass
class ServerFrame(Frame):
    _timer_handshake: Timer | None = field(init=False, default=None)

    def __post_init__(self):
        self.game_info_signals.disconnected.connect(self.on_disconnected)
        self.event_manager.on(
            CharacterSelectionEvent, self.on_character_selection_event, originator=self
        )
        self.event_manager.on(
            SelectServerRequest, self.on_select_server_request, originator=self
        )
        self.event_manager.before(
            SequenceNumberRequest, self.before_sequence_number_request, originator=self
        )
        self.event_manager.on(
            SequenceNumberEvent, self.on_sequence_number_event, originator=self
        )
        self.event_manager.before(
            BasicLatencyStatsRequest,
            self.before_basic_latency_stats_request,
            originator=self,
        )
        self.event_manager.on(
            BasicLatencyStatsEvent, self.on_basic_latency_stats_event, originator=self
        )
        self.event_manager.on(
            IdentificationResponse, self.on_identification_response, originator=self
        )

    def on_disconnected(self):
        if self._timer_handshake is not None:
            self._timer_handshake.cancel()
            self._timer_handshake = None
        self.game_state.server.clear_state()

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

    def on_select_server_request(self, msg: SelectServerRequest):
        self.game_state.player.server_id = msg.server

    def before_sequence_number_request(self, msg: SequenceNumberRequest):
        if self.game_state.server.is_socket:
            return None
        return msg

    def on_sequence_number_event(self, msg: SequenceNumberEvent):
        self.game_state.server.sequence_number += 1
        if self.game_state.server.is_socket:
            req = SequenceNumberRequest(number=self.game_state.server.sequence_number)
            self.event_manager.send(req)

    def before_basic_latency_stats_request(self, msg: BasicLatencyStatsRequest):
        if self.game_state.server.is_socket:
            return None
        return msg

    def on_basic_latency_stats_event(self, msg: BasicLatencyStatsEvent):
        if self.game_state.server.is_socket:
            latency_average = self.game_state.server.latency_average
            req = BasicLatencyStatsRequest(latency=latency_average)
            self.event_manager.send(req)

    def on_identification_response(self, msg: IdentificationResponse):
        return

        def on_timeout_select_server_request():
            if self.game_state.player.server_id != 0 and self.is_playing_event.is_set():
                self.logger.info("Manual select server, player is probably in fight")
                req = Request(
                    selectServer=SelectServerRequest(
                        server=self.game_state.player.server_id
                    )
                )
                self.event_manager.send(req)

        self.event_manager.on(
            SelectServerRequest,
            callback=lambda _: _,
            originator=self,
            once=True,
            timeout=5,
            on_timeout=on_timeout_select_server_request,
        )
