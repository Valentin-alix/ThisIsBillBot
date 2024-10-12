from dataclasses import dataclass

from protos.game.fight_pb2 import FightEndEvent
from protos.game.game_action_pb2 import (
    GameActionFightCastRequest,
    SequenceEndEvent,
    SequenceType,
)
from src.core.behaviors.behavior import Behavior
from src.core.data_center.data_reader import DataReader
from src.core.data_center.i18n import I18N
from src.core.logic.grid.map_point import MapPoint


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
        req = GameActionFightCastRequest(spell_id=spell_id, cell=cell_id)
        self.event_manager.send(req)

    def on_sequence_end_event(self, msg: SequenceEndEvent):
        if (
            msg.sequence_type == SequenceType.SPELL
            and msg.author_id == self.game_state.player.character_id
        ):
            self.finish()


if __name__ == "__main__":
    spell_id = 12794

    spell = DataReader().spell_by_id[spell_id]
    print(I18N().name_by_id[spell.nameId])
    spell_lvl = DataReader().spell_lvl_by_spell_id[spell_id][0]

    print(spell_lvl)
