from dataclasses import dataclass, field

from src.core.states.state import State


@dataclass
class ServerState(State):
    is_socket: bool = field(init=False, default=False)
    sequence_number: int = field(init=False, default=0)
    latency_buffer: list[float] = field(init=False, default_factory=list)
    latest_sent: float | None = field(init=False, default=None)

    @property
    def latency_average(self) -> int:
        if len(self.latency_buffer) == 0:
            return 0
        return min(
            32767, round(sum(self.latency_buffer) / len(self.latency_buffer) * 1000)
        )
