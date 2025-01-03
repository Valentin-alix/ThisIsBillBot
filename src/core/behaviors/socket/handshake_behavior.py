from dataclasses import dataclass

from datas.protos.non_obf.game.bak_pb2 import BakApiTokenRequest
from datas.protos.non_obf.game.character_management_pb2 import (
    CharacterListEvent,
    CharacterListRequest,
    CharacterLoadingCompleteEvent,
    CharacterSelectionRequest,
)
from datas.protos.non_obf.game.chat_pb2 import Channel, SubscribeMultipleChannelRequest
from datas.protos.non_obf.game.connection_pb2 import (
    AuthenticationTicketAcceptedEvent,
    IdentificationRequest as GameIdentificationRequest,
)
from datas.protos.non_obf.game.context_pb2 import ContextCreationRequest

from src.core.behaviors.behavior import Behavior

_SUBSCRIBE_CHANNELS = [
    Channel.GLOBAL,
    Channel.TEAM,
    Channel.GUILD,
    Channel.PARTY,
    Channel.NOOB,
    Channel.ADMIN,
    Channel.PRIVATE,
    Channel.INFO,
    Channel.ADS,
    Channel.ARENA,
    Channel.EVENT,
    Channel.FIGHT_LOG,
]


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
        self, _msg: AuthenticationTicketAcceptedEvent
    ) -> None:
        self.event_manager.send(CharacterListRequest())
        self.event_manager.send(BakApiTokenRequest())
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
        self.event_manager.on(
            CharacterLoadingCompleteEvent,
            self.on_character_loading_complete_event,
            originator=self,
            once=True,
        )

    def on_character_loading_complete_event(
        self, _msg: CharacterLoadingCompleteEvent
    ) -> None:
        self.event_manager.send(ContextCreationRequest())
        self.event_manager.send(
            SubscribeMultipleChannelRequest(
                channel_enabled=_SUBSCRIBE_CHANNELS,
                channel_disabled=[],
            )
        )
        self.finish(None)
