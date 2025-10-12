import threading
from dataclasses import dataclass, field
from datetime import datetime

from DBDofusUnity.datas.protos.non_obf.game.basic_pb2 import DateRequest
from DBDofusUnity.datas.protos.non_obf.game.connection_pb2 import PingRequest

from src.core.behaviors.behavior import Behavior

_HEARTBEAT_INTERVAL_SECONDS = 30


@dataclass
class HearthBeatBehavior(Behavior):
    _heartbeat_stop: threading.Event = field(init=False, default_factory=threading.Event)

    def run(self) -> None:
        self._heartbeat_stop.clear()
        self._send_ping()
        threading.Thread(target=self._heartbeat_loop, daemon=True).start()

    def _heartbeat_loop(self) -> None:
        while not self._heartbeat_stop.wait(_HEARTBEAT_INTERVAL_SECONDS):
            self.event_manager.send(DateRequest())
            if self._heartbeat_stop.wait(_HEARTBEAT_INTERVAL_SECONDS):
                break
            self._send_ping()

    def _send_ping(self) -> None:
        now = datetime.now()
        previous_ping_datetime = self.game_state.server.sent_datetime_ping_request
        if previous_ping_datetime is not None:
            pending_ping_age_ms = int((now - previous_ping_datetime).total_seconds() * 1_000)
            self.logger.warning(
                "Sending PingRequest while previous ping is still pending: "
                f"pending_ping_age_ms={pending_ping_age_ms}"
            )
        self.game_state.server.sent_datetime_ping_request = now
        self.event_manager.send(PingRequest(quiet=True))

    def stop(self) -> None:
        self._heartbeat_stop.set()
        return super().stop()
