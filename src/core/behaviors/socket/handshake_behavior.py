from dataclasses import dataclass

from client_verification_pb2 import ServerVerificationEvent
from datas.protos.non_obf.game.character_management_pb2 import (
    CharacterListEvent,
    CharacterListRequest,
    CharacterSelectionRequest,
)
from datas.protos.non_obf.game.connection_pb2 import (
    AuthenticationTicketAcceptedEvent,
)
from datas.protos.non_obf.game.connection_pb2 import (
    IdentificationRequest as GameIdentificationRequest,
)

from src.core.behaviors.behavior import Behavior


@dataclass
class HandshakeBehavior(Behavior):
    def run(self, ticket: str) -> None:
        self.event_manager.on(
            AuthenticationTicketAcceptedEvent,
            self.on_authentication_ticket_accepted_event,
            originator=self,
            once=True,
        )
        self.event_manager.send(
            GameIdentificationRequest(ticket_key=ticket, language_code="fr")
        )

    def on_authentication_ticket_accepted_event(
        self, msg: AuthenticationTicketAcceptedEvent
    ) -> None:
        self.event_manager.on(
            ServerVerificationEvent,
            self.on_server_verification_event,
            originator=self,
            once=True,
        )

    def on_server_verification_event(self, msg: ServerVerificationEvent):
        req = CharacterListRequest()
        self.event_manager.send(req)

        # def on_leg_message ?
        # ClientIDRequest
        self.event_manager.on(
            CharacterListEvent,
            self.on_character_list_event,
            originator=self,
            once=True,
        )

    def on_character_list_event(self, msg: CharacterListEvent) -> None:
        if not msg.characters:
            raise ValueError("CharacterListEvent has no characters")

        character = msg.characters[0]
        self.logger.info(f"Selecting character {character.id}")
        self.event_manager.send(CharacterSelectionRequest(character_id=character.id))
        self.event_manager.send(CharacterSelectionRequest(character_id=character.id))
