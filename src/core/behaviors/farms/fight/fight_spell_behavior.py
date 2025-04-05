from dataclasses import dataclass, field

from datas.protos.non_obf.game.game_action_pb2 import (
    GameActionAcknowledgementRequest,
    GameActionFightCastRequest,
    SequenceEndEvent,
)
from dofus_unity_reader.grid.map_point import MapPoint

from src.core.behaviors.behavior import Behavior
from src.services.human_timings import HumanTimingsService


@dataclass
class FightSpellBehavior(Behavior):
    _pending_spell_action_id: int | None = field(init=False, default=None)

    def run(
        self,
        spell_id: int,
        target_mp: MapPoint,
    ) -> None:
        self._pending_spell_action_id = None
        self.launch_spell_on_cell_id(spell_id, target_mp.cell_id)

    def launch_spell_on_cell_id(self, spell_id: int, cell_id: int):
        self.event_manager.on(
            SequenceEndEvent, self.on_sequence_end_event, originator=self
        )
        self.event_manager.on(
            GameActionAcknowledgementRequest,
            self.on_game_action_acknowledgement_request,
            originator=self,
        )
        req = GameActionFightCastRequest(spell_id=spell_id, cell=cell_id)

        self.send_message_delayed(
            req, HumanTimingsService().get_micro_jitter("spell_cast")
        )

    def on_sequence_end_event(self, msg: SequenceEndEvent):
        if msg.author_id == self.game_state.player.character_id:
            self._pending_spell_action_id = msg.action_id

    def on_game_action_acknowledgement_request(
        self, msg: GameActionAcknowledgementRequest
    ) -> None:
        if msg.valid and msg.action_id == self._pending_spell_action_id:
            self.finish()
