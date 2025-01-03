import threading
from dataclasses import dataclass, field

from datas.protos.non_obf.game.basic_pb2 import DateRequest
from datas.protos.non_obf.game.connection_pb2 import PingRequest

from src.core.behaviors.behavior import Behavior

_HEARTBEAT_INTERVAL_SECONDS = 30


@dataclass
class HearthBeatBehavior(Behavior):
    _heartbeat_stop: threading.Event = field(
        init=False, default_factory=threading.Event
    )

    def run(self):
        threading.Thread(target=self._heartbeat_loop, daemon=True).start()

    def _heartbeat_loop(self) -> None:
        while not self._heartbeat_stop.wait(_HEARTBEAT_INTERVAL_SECONDS):
            self.event_manager.send(PingRequest(quiet=True))
            if self._heartbeat_stop.wait(_HEARTBEAT_INTERVAL_SECONDS):
                break
            self.event_manager.send(DateRequest())

    def stop(self):
        self._heartbeat_stop.set()
        return super().stop()
