import unittest
from types import SimpleNamespace
from typing import cast
from unittest.mock import Mock

from datas.protos.non_obf.game.common_pb2 import EntityDisposition
from datas.protos.non_obf.game.context_pb2 import EntitiesDispositionEvent

from src.core.behaviors.farms.fight.fight_movement_behavior import (
    FightMovementBehavior,
)
from src.core.behaviors.farms.fight.fight_preparation_behavior import (
    FightPreparationBehavior,
)
from src.core.events_manager.event_manager import EventManager
from src.core.states.game_state import GameState
from src.services.logging.logger import Logger


class _TestFightPreparationBehavior(FightPreparationBehavior):
    placement_done_calls: int

    def on_player_placement_done(self) -> None:
        self.placement_done_calls += 1


class TestFightPreparationBehavior(unittest.TestCase):
    def _create_behavior(self) -> _TestFightPreparationBehavior:
        game_state = cast(
            GameState,
            SimpleNamespace(player=SimpleNamespace(character_id=123)),
        )
        behavior = _TestFightPreparationBehavior(
            event_manager=cast(EventManager, Mock()),
            game_state=game_state,
            _logger=cast(Logger, Mock()),
            fight_movement_behavior=cast(FightMovementBehavior, Mock()),
        )
        behavior.placement_done_calls = 0
        return behavior

    def test_on_entity_disposition_event_advances_when_matching_cell(self) -> None:
        behavior = self._create_behavior()
        message = EntitiesDispositionEvent(
            dispositions=[
                EntityDisposition(
                    cell_id=123,
                    entity_id=123,
                    carrying_character_id=0,
                )
            ]
        )

        behavior.on_entity_disposition_event(message, requested_cell_id=123)

        self.assertEqual(behavior.placement_done_calls, 1)

    def test_on_entity_disposition_event_ignores_other_cells(self) -> None:
        behavior = self._create_behavior()
        message = EntitiesDispositionEvent(
            dispositions=[
                EntityDisposition(
                    cell_id=999,
                    entity_id=123,
                    carrying_character_id=0,
                )
            ]
        )

        behavior.on_entity_disposition_event(message, requested_cell_id=123)

        self.assertEqual(behavior.placement_done_calls, 0)


if __name__ == "__main__":
    unittest.main()
