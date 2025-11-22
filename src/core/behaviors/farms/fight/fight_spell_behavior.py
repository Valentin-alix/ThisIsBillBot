from dataclasses import dataclass

from DBDofusUnity.datas.protos.non_obf.game.game_action_pb2 import (
    GameActionFightCastRequest,
    SequenceEndEvent,
    SequenceType,
)
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint

from src.core.behaviors.farms.fight.fight_listener_behavior import FightListenerBehavior
from src.services.human_timings import HumanTimingsService


@dataclass
class FightSpellBehavior(FightListenerBehavior):
    def run(
        self,
        spell_id: int,
        target_mp: MapPoint,
    ) -> None:
        self.launch_spell_on_cell_id(spell_id, target_mp.cell_id)

    def launch_spell_on_cell_id(self, spell_id: int, cell_id: int):
        self.event_manager.on(SequenceEndEvent, self.on_sequence_end_event, originator=self)
        self.register_fight_death_check()
        req = GameActionFightCastRequest(spell_id=spell_id, cell=cell_id)

        self.send_message_delayed(req, HumanTimingsService().get_timing_before_spell_cast())

    def on_sequence_end_event(self, msg: SequenceEndEvent):
        if msg.author_id == self.game_state.player.character_id and msg.sequence_type == SequenceType.SPELL:
            return self.finish()
