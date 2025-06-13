from dataclasses import dataclass

from character_management_pb2 import (
    CharacterCreationRequest,
    CharacterFirstSelectionRequest,
    CharacterListEvent,
    CharacterNameSuggestionEvent,
    CharacterNameSuggestionRequest,
)
from datas.protos.non_obf.game.common_pb2 import CharacterRemodelingInformation, Gender
from dofus_unity_reader.game_constants.breed import BreedEnum

from src.core.behaviors.behavior import Behavior
from src.core.config import BIG_RANGE, VERY_BIG_RANGE


@dataclass
class CharacterCreationBehavior(Behavior):
    def run(self):
        self.event_manager.on(
            CharacterNameSuggestionEvent,
            self.on_character_name_suggestion_event,
            originator=self,
            once=True,
        )
        self.send_message_delayed(CharacterNameSuggestionRequest(), BIG_RANGE)

    def on_character_name_suggestion_event(self, msg: CharacterNameSuggestionEvent):
        self.event_manager.on(
            CharacterListEvent, self.on_character_list_event, originator=self, once=True
        )

        req = CharacterCreationRequest(
            modeling_information=CharacterRemodelingInformation(
                name=msg.suggestion,
                breed_id=BreedEnum.SACRIER,
                gender=Gender.FEMALE,
                colors=[-1, -1, -1, -1, -1, -1],
                cosmetic_id=169,
                unknown=27,
            )
        )
        self.send_message_delayed(req, VERY_BIG_RANGE)

    def on_character_list_event(self, msg: CharacterListEvent):
        assert len(msg.characters) > 0
        req = CharacterFirstSelectionRequest(character_id=msg.characters[0].id)
        self.event_manager.send(req)
        self.finish()
