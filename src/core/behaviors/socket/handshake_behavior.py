from dataclasses import dataclass
from typing import cast

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
)
from datas.protos.non_obf.game.connection_pb2 import (
    IdentificationRequest as GameIdentificationRequest,
)
from datas.protos.non_obf.game.contact_pb2 import (
    AcquaintanceListRequest,
    ContactWarnOnAchievementCompleteSetRequest,
    ContactWarnOnPermanentDeathSetRequest,
    FriendListRequest,
    FriendSetStatusShareRequest,
    FriendSetWarnOnConnectionRequest,
    FriendSetWarnOnLevelGainRequest,
)
from datas.protos.non_obf.game.context_pb2 import ContextCreationRequest
from datas.protos.non_obf.game.guild_information_pb2 import GuildInformationRequest
from datas.protos.non_obf.game.social_pb2 import SpouseInformationRequest

from src.core.behaviors.behavior import Behavior
from src.services.human_timings import get_random_range

_POST_LOAD_DELAY: tuple[float, float] = (1.0, 1.3)
_CONTEXT_CREATION_DELAY: tuple[float, float] = (0.25, 0.4)

_CHANNELS_ENABLED: list[Channel] = [
    Channel.SALES,
    Channel.SEEK,
    Channel.ARENA,
    cast(Channel, 11),
    Channel.EVENT,
]
_CHANNELS_DISABLED: list[Channel] = [
    Channel.GLOBAL,
    Channel.TEAM,
    Channel.GUILD,
    Channel.ALLIANCE,
    Channel.PARTY,
    Channel.ADMIN,
    Channel.PRIVATE,
    Channel.INFO,
    Channel.FIGHT_LOG,
    Channel.EXCHANGE,
    cast(Channel, 17),
    cast(Channel, 18),
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
        self.run_timer(
            get_random_range(_POST_LOAD_DELAY, is_weighted=False),
            self._send_post_load_batch,
        )

    def _send_post_load_batch(self) -> None:
        info_type = GuildInformationRequest.InformationType
        self.event_manager.send(FriendListRequest())
        self.event_manager.send(AcquaintanceListRequest())
        self.event_manager.send(SpouseInformationRequest())
        self.event_manager.send(
            GuildInformationRequest(information_type=info_type.INFO_PADDOCKS)
        )
        self.event_manager.send(
            GuildInformationRequest(information_type=info_type.INFO_HOUSES)
        )
        self.event_manager.send(
            ContactWarnOnAchievementCompleteSetRequest(enable=False)
        )
        self.event_manager.send(FriendSetWarnOnConnectionRequest(enable=False))
        self.event_manager.send(FriendSetWarnOnLevelGainRequest(enable=False))
        self.event_manager.send(ContactWarnOnPermanentDeathSetRequest(enable=False))
        self.event_manager.send(FriendSetStatusShareRequest(share=False))
        self.event_manager.send(
            GuildInformationRequest(information_type=info_type.INFO_PADDOCKS)
        )
        self.event_manager.send(
            GuildInformationRequest(information_type=info_type.INFO_HOUSES)
        )

        self.run_timer(
            get_random_range(_CONTEXT_CREATION_DELAY, is_weighted=False),
            self._send_context_creation,
        )

    def _send_context_creation(self) -> None:
        self.event_manager.send(ContextCreationRequest())
        self.event_manager.send(
            SubscribeMultipleChannelRequest(
                channel_enabled=_CHANNELS_ENABLED,
                channel_disabled=_CHANNELS_DISABLED,
            )
        )
        self.finish(None)
