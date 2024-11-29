from dataclasses import dataclass, field


@dataclass
class MiniState:
    foo: int = 0
    bar: str = ""


@dataclass
class MiniGameState:
    player: MiniState = field(default_factory=MiniState)


class DummyEventManager:
    def __init__(self) -> None:
        self.received: list[object] = []

    def process_msg(self, msg: object) -> None:
        self.received.append(msg)


class DummyBot:
    def __init__(self) -> None:
        self.event_manager: DummyEventManager = DummyEventManager()
        self.game_state: MiniGameState = MiniGameState()
