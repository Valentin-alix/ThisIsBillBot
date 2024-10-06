from dataclasses import dataclass
from functools import partial

from db_dofus_unity.protos.game.fight_pb2 import FightEndEvent
from db_dofus_unity.protos.game.game_action_pb2 import (
    GameActionFightCastRequest,
    GameActionAcknowledgementRequest,
    SequenceEndEvent,
    SequenceType,
)
from src.common.logger import Logger
from src.consts import VERY_SMALL_RANGE
from src.core.behaviors.behavior import Behavior
from src.core.logic.fight.los_detector import LosDetector
from src.core.logic.grid.map_point import MapPoint
from src.core.repositories.data_reader import DataReader
from src.core.states.entity_state import EntityState
from src.core.states.fight_state import FightState
from src.core.states.map_state import MapState
from src.core.states.player_state import PlayerState
from src.interfaces.enums.stat_id import StatIds


@dataclass
class FightSpellBehavior(Behavior):
    player_state: PlayerState
    fight_state: FightState
    entity_state: EntityState
    map_state: MapState

    def run(self):
        self.event_manager.on(FightEndEvent, lambda _: self.finish(), originator=self)
        self.choose_and_launch_spell()

    def choose_and_launch_spell(self):
        spell_id = 12791
        spell_lvl = DataReader().spell_lvl_by_spell_id[spell_id][0]

        stat_pa = self.player_state.get_stat_usable_by_id(StatIds.ACTION_POINTS)
        if stat_pa < spell_lvl.apCost:
            Logger().info(f"player does not have enough pa")
            return self.finish()

        Logger().info("on player placed")
        for enemy in self.entity_state.get_enemies(self.fight_state.team):
            mp_enemy = MapPoint.from_cell_id(enemy.disposition.cell_id)
            if (
                mp_enemy.distance_to_map_point(self.player_state.map_point)
                > spell_lvl.range - 1
            ):
                Logger().info(f"enemy at {mp_enemy} too far")
                continue
            if not LosDetector.los_between(
                map_id=self.map_state.map_id,
                entity_state=self.entity_state,
                start=self.player_state.map_point,
                end=mp_enemy,
            ):
                Logger().info(f"enemy at {mp_enemy} don't have los")
                continue

            return self.launch_spell_on_cell_id(spell_id, mp_enemy.cell_id)

        self.finish()

    def on_sequence_end_event(self, msg: SequenceEndEvent):
        if (
            msg.sequence_type == SequenceType.SPELL
            and msg.author_id == self.player_state.character_id
        ):
            self.event_manager.clear_listener_by_origin_and_type(SequenceEndEvent, self)
            self.event_manager.on(
                GameActionAcknowledgementRequest,
                partial(
                    self.on_game_action_acknowledgement_request,
                    target_action_id=msg.action_id,
                ),
                originator=self,
            )

    def on_game_action_acknowledgement_request(
        self, msg: GameActionAcknowledgementRequest, target_action_id: int
    ):
        if msg.action_id == target_action_id:
            self.event_manager.clear_listener_by_origin_and_type(
                GameActionAcknowledgementRequest, self
            )
            self.run_timer(VERY_SMALL_RANGE, self.choose_and_launch_spell)

    def launch_spell_on_cell_id(self, spell_id: int, cell_id: int):
        self.event_manager.on(
            SequenceEndEvent, self.on_sequence_end_event, originator=self
        )
        req = GameActionFightCastRequest(spell_id=spell_id, cell=cell_id)
        self.event_manager.send(req)


if __name__ == "__main__":
    spell_id = 12791
    spell_lvl = DataReader().spell_lvl_by_spell_id[spell_id][0]

    mp_enemy = MapPoint.from_cell_id(410)
    temp = mp_enemy.distance_to_map_point(MapPoint.from_cell_id(342))
    print(temp)

    print(spell_lvl.range)
    # for spell_lvl in DataReader().spell_lvl_by_spell_id[spell_id]:
    #     print(spell_lvl.range)
