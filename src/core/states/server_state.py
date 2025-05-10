from dataclasses import dataclass, field
from datetime import datetime

from src.core.states.state import State


@dataclass
class ServerState(State):
    sent_datetime_ping_request: datetime | None = field(init=False, default=None)
    latency: int | None = field(init=False, default=None)
