from dataclasses import dataclass

from dofus_unity_reader.grid.map_point import MapPoint
from datas.protos.non_obf.game.fight_pb2 import FightEndEvent
from datas.protos.non_obf.game.game_action_pb2 import (
    GameActionFightCastRequest,
    SequenceEndEvent,
    SequenceType,
)

from src.core.behaviors.behavior import Behavior
from src.services.human_timings import HumanTimingsService


@dataclass
class FightSpellBehavior(Behavior):
    def run(
        self,
        spell_id: int,
        target_mp: MapPoint,
    ) -> None:
        self.event_manager.on(
            FightEndEvent, lambda _: self.finish(), originator=self, once=True
        )
        self.launch_spell_on_cell_id(spell_id, target_mp.cell_id)

    def launch_spell_on_cell_id(self, spell_id: int, cell_id: int):
        self.event_manager.on(
            SequenceEndEvent, self.on_sequence_end_event, originator=self
        )
        req = GameActionFightCastRequest(spell_id=spell_id, cell=cell_id)

        self.run_timer(
            HumanTimingsService().get_micro_jitter("spell_cast"),
            lambda: self.event_manager.send(req),
        )

    def on_sequence_end_event(self, msg: SequenceEndEvent):
        if (
            msg.sequence_type == SequenceType.SPELL
            and msg.author_id == self.game_state.player.character_id
        ):
            self.finish()
