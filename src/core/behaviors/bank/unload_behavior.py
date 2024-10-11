from dataclasses import dataclass

from src.core.behaviors.bank.consts import GATHERER_ITEM_IDS
from src.core.behaviors.bank.unload_in_bank_behavior import UnloadInBankBehavior
from src.core.behaviors.bank.unload_in_guild_chest_behavior import (
    UnloadInGuildChestBehavior,
)
from src.core.behaviors.behavior import Behavior
from src.exceptions import UnhandledErrorCodeException


@dataclass
class UnloadBehavior(Behavior):
    unload_in_bank_behavior: UnloadInBankBehavior
    unload_in_guild_chest_behavior: UnloadInGuildChestBehavior

    def run(self) -> None:
        self.unload_in_guild_chest_behavior.start(
            unload_item_ids=GATHERER_ITEM_IDS,
            parent=self,
            callback=self.on_unload_in_guild_chest_behavior_finished,
        )

    def on_unload_in_guild_chest_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.unload_in_bank_behavior.start(callback=self.finish, parent=self)
