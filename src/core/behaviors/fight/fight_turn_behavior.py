from dataclasses import dataclass, field
from functools import partial
from typing import Callable

from d3_mapping.resources.protos.game.fight_pb2 import (
    FightIsTurnReadyEvent,
    FightTurnEndEvent,
    FightTurnFinishRequest,
)

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.fight.fight_movement_behavior import FightMovementBehavior
from src.core.behaviors.fight.fight_spell_behavior import FightSpellBehavior
from src.core.behaviors.movements.map_move_behavior import MapMoveError
from src.core.controller.human_timings import HumanTimingsController
from src.core.logic.fight.attack import Attacker
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.exceptions import UnhandledErrorCodeException
from src.interfaces.enums.breed import Breed

RUNAWAY_BREED: set[int] = {Breed.CRA, Breed.SACRIER, 0}  # always run away


@dataclass
class FightTurnBehavior(Behavior):
    fight_movement_behavior: FightMovementBehavior
    path_finding: Pathfinding
    fight_spell_behavior: FightSpellBehavior
    attacker: Attacker

    did_attack: bool = field(init=False, default=False)

    def run(self) -> None:
        self.did_attack = False
        self.event_manager.on(
            FightTurnEndEvent, lambda _: self.finish(), originator=self
        )
        self.event_manager.on(
            FightIsTurnReadyEvent, lambda _: self.finish(), originator=self
        )
        self.find_and_do_attack()

    def find_and_do_attack(self):
        attack_info = self.attacker.find_best_attack_from_mp()
        if attack_info is None:
            self.logger.info(f"Breed id : {self.game_state.player.breed_id}")
            if self.game_state.player.breed_id in RUNAWAY_BREED and self.did_attack:
                self.logger.info("Go go run away")
                run_away = True
            else:
                run_away = False

            return self.fight_movement_behavior.start(
                callback=partial(
                    self.on_fight_movement_behavior_finished,
                    callback=lambda: self.run_timer(
                        HumanTimingsController().get_timing_before_pass_turn(),
                        self.pass_turn,
                    ),
                ),
                parent=self,
                run_away=run_away,
            )

        self.did_attack = True
        move_mp, spell_lvl, attack_mp = attack_info

        move_path = self.path_finding.find_path(
            self.game_state.player.map_point,
            {move_mp},
            allow_diag=False,
            allow_trough_entity=False,
        )

        self.fight_movement_behavior.start(
            callback=partial(
                self.on_fight_movement_behavior_finished,
                callback=lambda: self.run_timer(
                    HumanTimingsController().get_timing_attack_finish_after_movement_or_attack(),
                    lambda: self.fight_spell_behavior.start(
                        spell_id=spell_lvl.spellId,
                        target_mp=attack_mp,
                        parent=self,
                        callback=self.on_fight_spell_behavior_finished,
                    ),
                ),
            ),
            parent=self,
            move_path=move_path,
        )

    def on_fight_movement_behavior_finished(
        self, error_code: str | None, callback: Callable[[], None]
    ):
        if error_code is MapMoveError.CANCELED_MOVEMENT:
            return self.find_and_do_attack()
        elif error_code in [MapMoveError.REFUSED, MapMoveError.CELL_TAKEN]:
            # cell is probably taken by invisible enemy
            return self.finish()
        elif error_code is not None:
            return self.finish()
        callback()

    def on_fight_spell_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)

        self.find_and_do_attack()

    def pass_turn(self):
        req = FightTurnFinishRequest()
        self.event_manager.send(req)
