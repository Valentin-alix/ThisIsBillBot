from dataclasses import dataclass, field
from unittest.mock import patch

from datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
    EntityDisposition,
)
from datas.protos.non_obf.game.fight_pb2 import FightIsTurnReadyEvent

from src.core.behaviors.behavior import Behavior, BehaviorState
from tests.test_states.state_test_base import StateTestBase


@dataclass
class CountingBehavior(Behavior):
    run_count: int = field(init=False, default=0)

    def run(self) -> None:
        self.run_count += 1


class TestFightBehavior(StateTestBase):
    def setUp(self) -> None:
        super().setUp()
        self.fight_behavior = self.bot.fight_behavior
        self.game_state.player.character_id = 123

    def _add_player_actor(self) -> None:
        self.game_state.entity.set_actor(
            ActorPositionInformation(
                actor_id=123,
                disposition=EntityDisposition(cell_id=300, entity_id=123),
            )
        )

    def test_enemy_turn_ready_event_does_not_schedule_player_turn(self) -> None:
        self.game_state.fight.in_fight = True
        self._add_player_actor()

        with patch.object(self.fight_behavior, "run_timer") as run_timer:
            self.fight_behavior.on_player_turn_event(
                FightIsTurnReadyEvent(character_id=-1)
            )

        run_timer.assert_not_called()

    def test_player_turn_is_ignored_when_player_actor_missing(self) -> None:
        self.game_state.fight.in_fight = True

        with patch.object(self.fight_behavior, "run_timer") as run_timer:
            self.fight_behavior.on_player_turn()

        run_timer.assert_not_called()

    def test_player_turn_is_ignored_when_turn_behavior_already_running(self) -> None:
        self.game_state.fight.in_fight = True
        self._add_player_actor()
        self.fight_behavior.fight_turn_behavior._state = BehaviorState.RUNNING

        with patch.object(self.fight_behavior, "run_timer") as run_timer:
            self.fight_behavior.on_player_turn()

        run_timer.assert_not_called()

    def test_behavior_start_does_not_run_when_already_running(self) -> None:
        behavior = CountingBehavior(
            self.bot._logger, self.event_manager, self.game_state
        )

        behavior.start(callback=None, parent=None)
        behavior.start(callback=None, parent=None)

        assert behavior.state == BehaviorState.RUNNING
        assert behavior.run_count == 1
