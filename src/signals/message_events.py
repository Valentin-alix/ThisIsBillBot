from dataclasses import dataclass, field

from blinker import Signal


@dataclass
class MessageEvents:
    received_game_msg: Signal = field(default_factory=lambda: Signal())
    received_connection_msg: Signal = field(default_factory=lambda: Signal())
    send_game_msg: Signal = field(default_factory=lambda: Signal())
    send_connection_msg: Signal = field(default_factory=lambda: Signal())
