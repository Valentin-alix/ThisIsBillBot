from dataclasses import dataclass, field
from enum import StrEnum, auto

from src.core.states.state import State


class OpenDialogKind(StrEnum):
    BANK_STORAGE = auto()
    GUILD_CHEST = auto()
    CRAFT = auto()
    BID_HOUSE_SELL = auto()
    BID_HOUSE_BUY = auto()
    PLAYER_EXCHANGE = auto()
    TRADE_REQUEST = auto()
    NPC_DIALOG = auto()
    ZAAP_DESTINATIONS = auto()
    FRIENDLY_FIGHT_REQUEST = auto()
    GUILD_INVITE = auto()


@dataclass
class DialogState(State):
    kind: OpenDialogKind | None = field(init=False, default=None)
    context_id: int | None = field(init=False, default=None)
    context_name: str | None = field(init=False, default=None)

    def set_open(
        self,
        kind: OpenDialogKind,
        context_id: int | None = None,
        context_name: str | None = None,
    ) -> None:
        if self.kind is not kind or self.context_id != context_id:
            self.logger.info(f"Dialog opened : {kind} (context {context_id})")
        self.kind = kind
        self.context_id = context_id
        self.context_name = context_name

    def is_open(self, kind: OpenDialogKind, context_id: int | None = None) -> bool:
        if self.kind is not kind:
            return False
        return context_id is None or self.context_id == context_id

    @property
    def is_any_open(self) -> bool:
        return self.kind is not None

    def clear_state(self) -> None:
        if self.kind is not None:
            self.logger.info(f"Dialog closed : {self.kind}")
        self.kind = None
        self.context_id = None
        self.context_name = None
