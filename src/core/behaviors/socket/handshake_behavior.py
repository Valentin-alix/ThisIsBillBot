from dataclasses import dataclass
from typing import cast

from datas.protos.non_obf.game.alliance_information_pb2 import AllianceMotdSetRequest
from datas.protos.non_obf.game.bak_pb2 import BakApiTokenRequest
from datas.protos.non_obf.game.breach_pb2 import BreachRoomUnlockRequest
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
    BlockListRequest,
    ContactWarnOnPermanentDeathSetRequest,
    FriendListRequest,
    FriendSetStatusShareRequest,
    FriendSetWarnOnConnectionRequest,
    FriendSetWarnOnLevelGainRequest,
)
from datas.protos.non_obf.game.context_pb2 import ContextCreationRequest
from datas.protos.non_obf.game.guild_information_pb2 import GuildInformationRequest
from datas.protos.non_obf.game.guild_rank_pb2 import GuildRankRemoveRequest
from datas.protos.non_obf.game.social_pb2 import SpouseInformationRequest
from datas.protos.non_obf.game.taxcollector_pb2 import (
    TaxCollectorPresetSpellAddRequest,
)

from src.core.behaviors.behavior import Behavior

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
        self, msg: CharacterLoadingCompleteEvent
    ) -> None:
        self.event_manager.send(FriendListRequest())
        self.event_manager.send(AcquaintanceListRequest())
        self.event_manager.send(AllianceMotdSetRequest())
        self.event_manager.send(
            GuildInformationRequest(
                information_type=GuildInformationRequest.InformationType.INFO_PADDOCKS
            )
        )
        self.event_manager.send(GuildRankRemoveRequest())
        self.event_manager.send(FriendSetWarnOnLevelGainRequest(enable=False))
        self.event_manager.send(FriendSetWarnOnConnectionRequest())
        self.event_manager.send(ContactWarnOnPermanentDeathSetRequest())
        self.event_manager.send(FriendSetStatusShareRequest(share=False))
        self.event_manager.send(
            GuildInformationRequest(
                information_type=GuildInformationRequest.InformationType.INFO_PADDOCKS
            )
        )
        self.event_manager.send(
            GuildInformationRequest(
                information_type=GuildInformationRequest.InformationType.INFO_GENERAL
            )
        )
        self.event_manager.send(TaxCollectorPresetSpellAddRequest())

        self.event_manager.send(ContextCreationRequest())
        self.event_manager.send(BlockListRequest())
        self.event_manager.send(BreachRoomUnlockRequest())
        self.event_manager.send(
            SubscribeMultipleChannelRequest(
                channel_enabled=_CHANNELS_ENABLED,
                channel_disabled=_CHANNELS_DISABLED,
            )
        )
        self.event_manager.send(SpouseInformationRequest())
        self.finish(None)
