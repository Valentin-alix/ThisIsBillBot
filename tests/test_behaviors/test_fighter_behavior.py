from typing import cast
from unittest.mock import Mock

import pytest

from src.core.behaviors.craft.craft_behavior import CraftBehavior
from src.core.behaviors.equipment.auto_equipment_behavior import (
    AutoEquipmentBehavior,
)
from src.core.behaviors.farms.fight.attacker_behavior import AttackerBehavior
from src.core.behaviors.farms.fighter_behavior import FighterBehavior
from src.core.behaviors.farms.random_farm_behavior import RandomFarmBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_behavior import AutoTripErrorCode
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior
from src.core.behaviors.mule_storage.mule_give_behavior import MuleGiveBehavior
from src.core.behaviors.sale_hotel.sale_hotel_sell_behavior import (
    SaleHotelSellBehavior,
)
from src.core.behaviors.storage.unloads.unload_behavior import UnloadBehavior
from src.core.events_manager.event_manager import EventManager
from src.exceptions import UnhandledErrorCodeException
from tests.fixtures.game_state import GameStateContext


def test_fighter_does_not_retry_path_not_found(
    game_state_ctx: GameStateContext,
) -> None:
    behavior = FighterBehavior(
        event_manager=EventManager(_logger=game_state_ctx.logger),
        game_state=game_state_ctx.game_state,
        _logger=game_state_ctx.logger,
        random_farm_behavior=cast(RandomFarmBehavior, Mock()),
        unload_behavior=cast(UnloadBehavior, Mock()),
        sale_hotel_prices_behavior=cast(SaleHotelSellBehavior, Mock()),
        mule_give_behavior=cast(MuleGiveBehavior, Mock()),
        craft_behavior=cast(CraftBehavior, Mock()),
        map_move_behavior=cast(MapMoveBehavior, Mock()),
        path_finding=game_state_ctx.pathfinding,
        attacker_behavior=cast(AttackerBehavior, Mock()),
        auto_equipment_behavior=cast(AutoEquipmentBehavior, Mock()),
    )
    behavior.run_next_step = Mock()  # type: ignore[method-assign]

    with pytest.raises(UnhandledErrorCodeException):
        behavior.on_random_farm_behavior_finished(AutoTripErrorCode.PATH_NOT_FOUND)

    behavior.run_next_step.assert_not_called()
