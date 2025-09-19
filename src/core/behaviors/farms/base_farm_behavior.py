from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum, auto

from src.core.behaviors.recovery import RecoverableBehavior
from src.core.behaviors.equipment.auto_equipment_behavior import (
    AutoEquipmentBehavior,
)
from src.core.behaviors.farms.random_farm_behavior import RandomFarmBehavior
from src.core.behaviors.storage.enter_chests.enter_bank_chest_behavior import (
    EnterBankChestErrorCode,
)
from src.core.behaviors.storage.unloads.unload_behavior import UnloadBehavior


class BaseFarmingErrorCode(StrEnum):
    STOP_CONDITION_TRIGGERED = auto()


@dataclass
class BaseFarmBehavior(RecoverableBehavior, ABC):
    """Abstract behavior that unloads a full inventory before resuming its farm cycle."""

    auto_equipment_behavior: AutoEquipmentBehavior
    random_farm_behavior: RandomFarmBehavior
    unload_behavior: UnloadBehavior

    is_stopped_at_new_map_condition: Callable[[], bool] | None = field(init=False, default=None)

    @abstractmethod
    def on_new_map(self):
        pass

    @abstractmethod
    def run_next_step(self):
        pass

    def check_stop_condition(self) -> bool:
        if self.is_stopped_at_new_map_condition is None:
            return False

        if self.is_stopped_at_new_map_condition():
            self.logger.info("Stop condition triggered, let's call callback")
            self.finish(BaseFarmingErrorCode.STOP_CONDITION_TRIGGERED)
            return True
        return False

    def on_full_pods(self):
        if not self.game_state.inventory.can_use_bank:
            self.logger.info("No bank access: stopping farming to switch mode")
            return self.finish(EnterBankChestErrorCode.NOT_ENOUGH_KAMAS)
        self.unload_behavior.start(parent=self, callback=self.on_unload_finished)

    def on_unload_finished(self, error_code: str | None) -> None:
        if error_code is not None:
            self.logger.error("Can't unload")
            return self.finish(error_code)

        self.auto_equipment_behavior.start(callback=self.on_auto_equipment_finished, parent=self)

    def on_auto_equipment_finished(self, error_code: str | None) -> None:
        self.raise_if_error(error_code)
        self.on_new_map()
