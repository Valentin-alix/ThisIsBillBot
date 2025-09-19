from dataclasses import dataclass

from datas.protos.non_obf.game.dialog_pb2 import DialogLeaveEvent
from datas.protos.non_obf.game.exchange_pb2 import (
    ExchangeBidBuyerStartedEvent,
    ExchangeBidSellerStartedEvent,
    ExchangeCraftStartedEvent,
    ExchangeLeaveEvent,
    ExchangeRequestedTradeEvent,
    ExchangeStartedWithMultiTabStorageEvent,
    ExchangeStartedWithPodsEvent,
    ExchangeStartedWithStorageEvent,
)
from datas.protos.non_obf.game.gamemap_pb2 import MapCurrentEvent
from datas.protos.non_obf.game.guild_information_pb2 import GuildInvitedEvent
from datas.protos.non_obf.game.npc_pb2 import NpcDialogQuestionEvent
from datas.protos.non_obf.game.roleplay_pb2 import PlayerFightFriendlyRequestedEvent
from datas.protos.non_obf.game.teleportation_pb2 import TeleportDestinationsEvent

from src.core.frames.frame import Frame
from src.core.states.dialog_state import OpenDialogKind

BANK_STORAGE_MIN_SLOT = 10_000


@dataclass
class DialogFrame(Frame):
    def __post_init__(self) -> None:
        super().__post_init__()
        self.game_info_signals.disconnected.connect(self.game_state.dialog.clear_state)

        self.event_manager.on(
            ExchangeStartedWithStorageEvent,
            self.on_exchange_started_with_storage_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ExchangeStartedWithMultiTabStorageEvent,
            self.on_exchange_started_with_multi_tab_storage_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ExchangeCraftStartedEvent,
            self.on_exchange_craft_started_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ExchangeBidSellerStartedEvent,
            self.on_exchange_bid_seller_started_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ExchangeBidBuyerStartedEvent,
            self.on_exchange_bid_buyer_started_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ExchangeStartedWithPodsEvent,
            self.on_exchange_started_with_pods_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ExchangeRequestedTradeEvent,
            self.on_exchange_requested_trade_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            TeleportDestinationsEvent,
            self.on_teleport_destinations_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            PlayerFightFriendlyRequestedEvent,
            self.on_player_fight_friendly_requested_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            GuildInvitedEvent,
            self.on_guild_invited_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            NpcDialogQuestionEvent,
            self.on_npc_dialog_question_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            ExchangeLeaveEvent,
            self.on_exchange_leave_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            DialogLeaveEvent,
            self.on_dialog_leave_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            MapCurrentEvent,
            self.on_map_current_event,
            originator=self,
            priority=self.priority,
        )

    def on_exchange_started_with_storage_event(self, msg: ExchangeStartedWithStorageEvent) -> None:
        if msg.storage_max_slot <= BANK_STORAGE_MIN_SLOT:
            return
        self.game_state.dialog.set_open(OpenDialogKind.BANK_STORAGE)

    def on_exchange_started_with_multi_tab_storage_event(
        self, msg: ExchangeStartedWithMultiTabStorageEvent
    ) -> None:
        self.game_state.dialog.set_open(OpenDialogKind.GUILD_CHEST)

    def on_exchange_craft_started_event(self, msg: ExchangeCraftStartedEvent) -> None:
        self.game_state.dialog.set_open(OpenDialogKind.CRAFT, context_id=msg.skill_id)

    def on_exchange_bid_seller_started_event(self, msg: ExchangeBidSellerStartedEvent) -> None:
        self.game_state.dialog.set_open(
            OpenDialogKind.BID_HOUSE_SELL, context_id=self.game_state.map.map_id
        )

    def on_exchange_bid_buyer_started_event(self, msg: ExchangeBidBuyerStartedEvent) -> None:
        self.game_state.dialog.set_open(
            OpenDialogKind.BID_HOUSE_BUY, context_id=self.game_state.map.map_id
        )

    def on_exchange_started_with_pods_event(self, msg: ExchangeStartedWithPodsEvent) -> None:
        self.game_state.dialog.set_open(OpenDialogKind.PLAYER_EXCHANGE)

    def on_exchange_requested_trade_event(self, msg: ExchangeRequestedTradeEvent) -> None:
        self.game_state.dialog.set_open(OpenDialogKind.TRADE_REQUEST)

    def on_teleport_destinations_event(self, msg: TeleportDestinationsEvent) -> None:
        self.game_state.dialog.set_open(OpenDialogKind.ZAAP_DESTINATIONS)

    def on_player_fight_friendly_requested_event(
        self, msg: PlayerFightFriendlyRequestedEvent
    ) -> None:
        if msg.target_id != self.game_state.player.character_id:
            return
        self.game_state.dialog.set_open(
            OpenDialogKind.FRIENDLY_FIGHT_REQUEST,
            context_id=msg.fight_id,
            context_name=self.get_character_name(msg.source_id),
        )

    def on_guild_invited_event(self, msg: GuildInvitedEvent) -> None:
        self.game_state.dialog.set_open(
            OpenDialogKind.GUILD_INVITE, context_name=msg.recruiter_name
        )

    def get_character_name(self, actor_id: int) -> str | None:
        actor = self.game_state.entity.actor_by_id.get(actor_id)
        if actor is None:
            return None
        role_play_actor = actor.actor_information.role_play_actor
        if not role_play_actor.HasField("named_actor"):
            return None
        return role_play_actor.named_actor.name or None

    def on_npc_dialog_question_event(self, msg: NpcDialogQuestionEvent) -> None:
        self.game_state.dialog.set_open(OpenDialogKind.NPC_DIALOG)

    def on_exchange_leave_event(self, msg: ExchangeLeaveEvent) -> None:
        self.game_state.dialog.clear_state()

    def on_dialog_leave_event(self, msg: DialogLeaveEvent) -> None:
        self.game_state.dialog.clear_state()

    def on_map_current_event(self, msg: MapCurrentEvent) -> None:
        self.game_state.dialog.clear_state()
