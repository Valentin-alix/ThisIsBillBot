from dataclasses import dataclass, field


@dataclass
class MiniState:
    foo: int = 0
    bar: str = ""


@dataclass
class MiniGameState:
    player: MiniState = field(default_factory=MiniState)


class DummyEventManager:
    def __init__(self):
        self.received = []

    def process_msg(self, msg):
        self.received.append(msg)


class DummyBot:
    def __init__(self):
        self.event_manager = DummyEventManager()
        self.game_state = MiniGameState()
