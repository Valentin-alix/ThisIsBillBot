from dataclasses import dataclass

from d3_mapping.resources.protos.game.fight_pb2 import FightEndEvent
from d3_mapping.resources.protos.game.game_action_pb2 import (
    GameActionFightCastOnTargetRequest,
    GameActionFightCastRequest,
    SequenceEndEvent,
    SequenceType,
)
from src.core.behaviors.behavior import Behavior
from grid.map_point import MapPoint


@dataclass
class FightSpellBehavior(Behavior):
    def run(self, spell_id: int, target_mp: MapPoint):
        self.event_manager.on(
            FightEndEvent, lambda _: self.finish(), originator=self, once=True
        )
        self.launch_spell_on_cell_id(spell_id, target_mp.cell_id)

    def launch_spell_on_cell_id(self, spell_id: int, cell_id: int):
        self.event_manager.on(
            SequenceEndEvent, self.on_sequence_end_event, originator=self
        )
        actor_on_mp = self.game_state.entity.get_first_actor_on_cell_id(cell_id)
        if actor_on_mp is not None:
            req = GameActionFightCastOnTargetRequest(
                spell_id=spell_id, target_id=actor_on_mp.actor_id
            )
        else:
            req = GameActionFightCastRequest(spell_id=spell_id, cell=cell_id)

        self.event_manager.send(req)

    def on_sequence_end_event(self, msg: SequenceEndEvent):
        if (
            msg.sequence_type == SequenceType.SPELL
            and msg.author_id == self.game_state.player.character_id
        ):
            self.finish()
