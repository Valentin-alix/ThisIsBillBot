"""Explicit generators for protobuf messages used in debug GUI.

Each message name present in `D3Mapping.d3_mapping.consts.GAME_VERIFIED_MAPPING_BY_OBF`
has a corresponding function `generate_<MessageName>()` in this module. These
functions create an instance of the protobuf message (if available) and fill
it with readable random values. The body of each generator calls a small
helper so you can manually tune fields per-message later.

Example:
    from debug_gui.random_proto_generators import generate_SpellsEvent
    msg = generate_SpellsEvent()

If a protobuf class is not found for a message name, the corresponding
function will raise `RuntimeError` when called; `missing_generators()` lists
those names ahead-of-time.
"""

from __future__ import annotations

import importlib
import pkgutil
import random
import string
from typing import Any, Callable, cast

from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.message import Message
from langchain_community.vectorstores.falkordb_vector import generate_random_string

from D3Database.data_center.data_reader import DataReader
from D3Database.grid.map_point import MAP_POINT_BY_CELL_ID
from D3Mapping.d3_mapping import verified_mapping as d3_consts
from D3Mapping.d3_mapping.resources.protos.game.basic_pb2 import TextInformationEvent
from D3Mapping.d3_mapping.resources.protos.game.character_management_pb2 import (
    CharacterSelectionEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.character_pb2 import (
    CharacterCharacteristicsEvent,
    CharacterCharacteristicUpgradeRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.chat_pb2 import (
    ChatChannelMessageEvent,
    ChatChannelMessageRequest,
    ChatPrivateMessageRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.common_pb2 import (
    ActorPositionInformation,
)
from D3Mapping.d3_mapping.resources.protos.game.context_pb2 import (
    EntitiesDispositionEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.dialog_pb2 import DialogLeaveRequest
from D3Mapping.d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeBidHouseItemAddedEvent,
    ExchangeBidHouseItemRemovedEvent,
    ExchangeBidHousePriceRequest,
    ExchangeBidHouseSearchRequest,
    ExchangeBidPriceEvent,
    ExchangeBidSellerStartedEvent,
    ExchangeCraftCountModifiedEvent,
    ExchangeCraftCountRequest,
    ExchangeCraftStartedEvent,
    ExchangeLeaveEvent,
    ExchangeMoveKamaRequest,
    ExchangeObjectModifyPricedRequest,
    ExchangeObjectMovePricedRequest,
    ExchangeObjectMoveRequest,
    ExchangeObjectTransferAllFromInventoryRequest,
    ExchangeReadyRequest,
    ExchangeSetCraftRecipeRequest,
    ExchangeStartedWithMultiTabStorageEvent,
    ExchangeStartedWithStorageEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.fight_pb2 import (
    FightLiveStateEvent,
    FightRefreshCharacterStatsEvent,
    FightTurnFinishRequest,
    FightTurnStartPlayingEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.fight_preparation_pb2 import (
    FightPlacementPositionRequest,
    FightPlacementPossiblePositionsEvent,
    FightReadyRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.game_action_pb2 import (
    GameActionAcknowledgementRequest,
    GameActionFightCastRequest,
    GameActionFightEvent,
    SequenceEndEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.gamemap_pb2 import (
    FightMapInformationEvent,
    MapChangeRequest,
    MapComplementaryInformationEvent,
    MapCurrentEvent,
    MapMovementConfirmRequest,
    MapMovementConfirmResponse,
    MapMovementEvent,
    MapMovementRefusedEvent,
    MapMovementRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.guild_chest_pb2 import (
    GuildChestCurrentListenersAddEvent,
    GuildChestTabSelectRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.guild_member_pb2 import (
    GuildMembershipEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.haven_bag_pb2 import (
    HavenBagEnterRequest,
    HavenBagExitRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.interactive_element_pb2 import (
    InteractiveUsedEvent,
    InteractiveUseRequest,
    StatedElementUpdatedEvent,
)

# explicit protobuf imports for typing and direct construction
from D3Mapping.d3_mapping.resources.protos.game.inventory_pb2 import (
    InventoryContentEvent,
    InventoryWeightEvent,
    ObjectAddedEvent,
    ObjectQuantityEvent,
    ObjectUseRequest,
    StorageInventoryContentEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.job_pb2 import JobExperiencesUpdateEvent
from D3Mapping.d3_mapping.resources.protos.game.npc_pb2 import (
    NpcDialogQuestionEvent,
    NpcDialogReplyRequest,
    NpcGenericActionRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.roleplay_pb2 import AttackMonsterRequest
from D3Mapping.d3_mapping.resources.protos.game.spell_pb2 import SpellsEvent
from D3Mapping.d3_mapping.resources.protos.game.teleportation_pb2 import (
    TeleportRequest,
    ZaapKnownListEvent,
)

GAME_PROTO_PKG = "d3_mapping.resources.protos.game"


def _discover_proto_modules() -> list[str]:
    try:
        pkg = importlib.import_module(GAME_PROTO_PKG)
    except Exception:
        return []
    mods: list[str] = []
    if not hasattr(pkg, "__path__"):
        return mods
    for finder, name, ispkg in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
        mods.append(name)
    return mods


def _find_message_class(name: str) -> type[Message] | None:
    try:
        root = importlib.import_module(GAME_PROTO_PKG)
        if hasattr(root, name):
            return getattr(root, name)
    except Exception:
        pass

    for mod_name in _discover_proto_modules():
        try:
            mod = importlib.import_module(mod_name)
        except Exception:
            continue
        if hasattr(mod, name):
            return getattr(mod, name)
    return None


def _random_string(max_len: int = 24) -> str:
    return "".join(
        random.choice(string.ascii_letters + string.digits + " _-")
        for _ in range(random.randint(3, max_len))
    )


def _choose_item_gid() -> int:
    items = list(DataReader().item_by_id.keys())
    return random.choice(items)


def _choose_skill_id() -> int:
    items = list(DataReader().skill_by_id.keys())
    return random.choice(items)


def _choose_cell_id() -> int:
    return random.choice(list(MAP_POINT_BY_CELL_ID.keys()))


def _choose_map_id() -> int:
    keys = list(DataReader().map_pos_by_map_id.keys())
    return random.choice(keys)


def _fill_scalar_field(msg: Message, field: FieldDescriptor, value: Any) -> None:
    try:
        if field.label == FieldDescriptor.LABEL_REPEATED:
            getattr(msg, field.name).append(value)
        else:
            setattr(msg, field.name, value)
    except Exception:
        pass


def _fill_message_basic(msg: Message, max_recurse: int = 5) -> Message:
    """Populate a message using simple heuristics. Tune per-message functions later."""
    if max_recurse <= 0:
        return msg
    desc = msg.DESCRIPTOR
    for field in desc.fields:
        try:
            field_name = field.name.lower()
            if field.label == FieldDescriptor.LABEL_REPEATED:
                count = random.randint(0, 3)
                for _ in range(count):
                    if field.type == FieldDescriptor.TYPE_MESSAGE:
                        sub = getattr(msg, field.name).add()
                        _fill_message_basic(sub, max_recurse - 1)
                    else:
                        _fill_field(msg, field, field_name)
            else:
                if field.type == FieldDescriptor.TYPE_MESSAGE:
                    sub = getattr(msg, field.name)
                    _fill_message_basic(sub, max_recurse - 1)
                else:
                    _fill_field(msg, field, field_name)
        except Exception:
            continue
    return msg


def _fill_field(msg: Message, field: Any, field_name: str):
    if "gid" in field_name:
        _fill_scalar_field(msg, field, _choose_item_gid())
    elif "skill_id" in field_name:
        _fill_scalar_field(msg, field, _choose_skill_id())
    elif "cell" in field_name:
        _fill_scalar_field(msg, field, _choose_cell_id())
    elif "map_id" in field_name:
        _fill_scalar_field(msg, field, _choose_map_id())
    elif field.type == FieldDescriptor.TYPE_STRING:
        _fill_scalar_field(msg, field, _random_string())
    else:
        if field.type in (
            FieldDescriptor.TYPE_INT32,
            FieldDescriptor.TYPE_UINT32,
            FieldDescriptor.TYPE_INT64,
            FieldDescriptor.TYPE_UINT64,
        ):
            _fill_scalar_field(msg, field, random.randint(0, 10000))
        elif field.type == FieldDescriptor.TYPE_BOOL:
            _fill_scalar_field(msg, field, random.choice([True, False]))


def _create_and_fill(name: str) -> Message:
    cls = _find_message_class(name)
    if cls is None:
        raise RuntimeError(f"protobuf class for {name} not found")
    msg = cls()
    _fill_message_basic(msg)
    return msg


# --- explicit generator functions (one per message name) ---
# Each of these functions is intentionally explicit so you can edit fields
# individually afterwards.


def generate_SpellsEvent() -> SpellsEvent:
    """Generate a `SpellsEvent` message."""
    return cast(SpellsEvent, _create_and_fill("SpellsEvent"))


def generate_InventoryContentEvent() -> InventoryContentEvent:
    """Generate a `InventoryContentEvent` message."""
    return cast(InventoryContentEvent, _create_and_fill("InventoryContentEvent"))


def generate_CharacterCharacteristicsEvent() -> CharacterCharacteristicsEvent:
    return cast(
        CharacterCharacteristicsEvent, _create_and_fill("CharacterCharacteristicsEvent")
    )


def generate_CharacterSelectionEvent() -> CharacterSelectionEvent:
    return cast(CharacterSelectionEvent, _create_and_fill("CharacterSelectionEvent"))


def generate_InventoryWeightEvent() -> InventoryWeightEvent:
    return cast(InventoryWeightEvent, _create_and_fill("InventoryWeightEvent"))


def generate_ZaapKnownListEvent() -> ZaapKnownListEvent:
    return cast(ZaapKnownListEvent, _create_and_fill("ZaapKnownListEvent"))


def generate_JobExperiencesUpdateEvent() -> JobExperiencesUpdateEvent:
    return cast(
        JobExperiencesUpdateEvent, _create_and_fill("JobExperiencesUpdateEvent")
    )


def generate_CharacterCharacteristicUpgradeRequest() -> (
    CharacterCharacteristicUpgradeRequest
):
    return cast(
        CharacterCharacteristicUpgradeRequest,
        _create_and_fill("CharacterCharacteristicUpgradeRequest"),
    )


def generate_MapCurrentEvent() -> MapCurrentEvent:
    return cast(MapCurrentEvent, _create_and_fill("MapCurrentEvent"))


def generate_basicActorPositionInformation() -> ActorPositionInformation:
    return ActorPositionInformation(
        actor_id=random.randint(1, 2000),
        actor_information=ActorPositionInformation.ActorInformation(
            role_play_actor=ActorPositionInformation.ActorInformation.RolePlayActor(
                named_actor=ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor(
                    name=generate_random_string(8)
                )
            )
        ),
    )


def generate_MapComplementaryInformationEvent(
    map_id: int | None = None,
) -> MapComplementaryInformationEvent:
    map_complementary_information_event = cast(
        MapComplementaryInformationEvent,
        _create_and_fill("MapComplementaryInformationEvent"),
    )
    if map_id:
        map_complementary_information_event.map_id = map_id
    for actor in map_complementary_information_event.actors:
        actor.CopyFrom(generate_basicActorPositionInformation())
    while map_complementary_information_event.interactive_elements:
        map_complementary_information_event.interactive_elements.pop()
    return map_complementary_information_event


def generate_MapMovementRequest() -> MapMovementRequest:
    return cast(MapMovementRequest, _create_and_fill("MapMovementRequest"))


def generate_MapMovementEvent() -> MapMovementEvent:
    return cast(MapMovementEvent, _create_and_fill("MapMovementEvent"))


def generate_MapMovementConfirmRequest() -> MapMovementConfirmRequest:
    return cast(
        MapMovementConfirmRequest,
        _create_and_fill("MapMovementConfirmRequest"),
    )


def generate_MapMovementConfirmResponse() -> MapMovementConfirmResponse:
    return cast(
        MapMovementConfirmResponse,
        _create_and_fill("MapMovementConfirmResponse"),
    )


def generate_MapChangeRequest() -> MapChangeRequest:
    return cast(MapChangeRequest, _create_and_fill("MapChangeRequest"))


def generate_InteractiveUseRequest() -> InteractiveUseRequest:
    return cast(InteractiveUseRequest, _create_and_fill("InteractiveUseRequest"))


def generate_StatedElementUpdatedEvent() -> StatedElementUpdatedEvent:
    return cast(
        StatedElementUpdatedEvent,
        _create_and_fill("StatedElementUpdatedEvent"),
    )


def generate_InteractiveUsedEvent() -> InteractiveUsedEvent:
    return cast(InteractiveUsedEvent, _create_and_fill("InteractiveUsedEvent"))


def generate_NpcGenericActionRequest() -> NpcGenericActionRequest:
    return cast(NpcGenericActionRequest, _create_and_fill("NpcGenericActionRequest"))


def generate_NpcDialogQuestionEvent() -> NpcDialogQuestionEvent:
    return cast(NpcDialogQuestionEvent, _create_and_fill("NpcDialogQuestionEvent"))


def generate_NpcDialogReplyRequest() -> NpcDialogReplyRequest:
    return cast(NpcDialogReplyRequest, _create_and_fill("NpcDialogReplyRequest"))


def generate_ExchangeStartedWithStorageEvent() -> ExchangeStartedWithStorageEvent:
    return cast(
        ExchangeStartedWithStorageEvent,
        _create_and_fill("ExchangeStartedWithStorageEvent"),
    )


def generate_StorageInventoryContentEvent() -> StorageInventoryContentEvent:
    return cast(
        StorageInventoryContentEvent,
        _create_and_fill("StorageInventoryContentEvent"),
    )


def generate_ExchangeObjectTransferAllFromInventoryRequest() -> (
    ExchangeObjectTransferAllFromInventoryRequest
):
    return cast(
        ExchangeObjectTransferAllFromInventoryRequest,
        _create_and_fill("ExchangeObjectTransferAllFromInventoryRequest"),
    )


def generate_ExchangeObjectMoveRequest() -> ExchangeObjectMoveRequest:
    return cast(
        ExchangeObjectMoveRequest,
        _create_and_fill("ExchangeObjectMoveRequest"),
    )


def generate_ObjectAddedEvent() -> ObjectAddedEvent:
    return cast(ObjectAddedEvent, _create_and_fill("ObjectAddedEvent"))


def generate_ObjectQuantityEvent() -> ObjectQuantityEvent:
    return cast(ObjectQuantityEvent, _create_and_fill("ObjectQuantityEvent"))


def generate_ExchangeMoveKamaRequest() -> ExchangeMoveKamaRequest:
    return cast(ExchangeMoveKamaRequest, _create_and_fill("ExchangeMoveKamaRequest"))


def generate_DialogLeaveRequest() -> DialogLeaveRequest:
    return cast(DialogLeaveRequest, _create_and_fill("DialogLeaveRequest"))


def generate_ExchangeLeaveEvent() -> ExchangeLeaveEvent:
    return cast(ExchangeLeaveEvent, _create_and_fill("ExchangeLeaveEvent"))


def generate_HavenBagEnterRequest() -> HavenBagEnterRequest:
    return cast(HavenBagEnterRequest, _create_and_fill("HavenBagEnterRequest"))


def generate_HavenBagExitRequest() -> HavenBagExitRequest:
    return cast(HavenBagExitRequest, _create_and_fill("HavenBagExitRequest"))


def generate_ObjectUseRequest() -> ObjectUseRequest:
    return cast(ObjectUseRequest, _create_and_fill("ObjectUseRequest"))


def generate_TeleportRequest() -> TeleportRequest:
    return cast(TeleportRequest, _create_and_fill("TeleportRequest"))


def generate_ExchangeBidSellerStartedEvent() -> ExchangeBidSellerStartedEvent:
    return cast(
        ExchangeBidSellerStartedEvent,
        _create_and_fill("ExchangeBidSellerStartedEvent"),
    )


def generate_ExchangeBidHouseSearchRequest() -> ExchangeBidHouseSearchRequest:
    return cast(
        ExchangeBidHouseSearchRequest,
        _create_and_fill("ExchangeBidHouseSearchRequest"),
    )


def generate_ExchangeBidHousePriceRequest() -> ExchangeBidHousePriceRequest:
    return cast(
        ExchangeBidHousePriceRequest,
        _create_and_fill("ExchangeBidHousePriceRequest"),
    )


def generate_ExchangeBidPriceEvent() -> ExchangeBidPriceEvent:
    return cast(ExchangeBidPriceEvent, _create_and_fill("ExchangeBidPriceEvent"))


def generate_ExchangeObjectMovePricedRequest() -> ExchangeObjectMovePricedRequest:
    return cast(
        ExchangeObjectMovePricedRequest,
        _create_and_fill("ExchangeObjectMovePricedRequest"),
    )


def generate_ExchangeObjectModifyPricedRequest() -> ExchangeObjectModifyPricedRequest:
    return cast(
        ExchangeObjectModifyPricedRequest,
        _create_and_fill("ExchangeObjectModifyPricedRequest"),
    )


def generate_ExchangeBidHouseItemAddedEvent() -> ExchangeBidHouseItemAddedEvent:
    return cast(
        ExchangeBidHouseItemAddedEvent,
        _create_and_fill("ExchangeBidHouseItemAddedEvent"),
    )


def generate_ExchangeBidHouseItemRemovedEvent() -> ExchangeBidHouseItemRemovedEvent:
    return cast(
        ExchangeBidHouseItemRemovedEvent,
        _create_and_fill("ExchangeBidHouseItemRemovedEvent"),
    )


def generate_TextInformationEvent() -> TextInformationEvent:
    return cast(TextInformationEvent, _create_and_fill("TextInformationEvent"))


def generate_AttackMonsterRequest() -> AttackMonsterRequest:
    return cast(AttackMonsterRequest, _create_and_fill("AttackMonsterRequest"))


def generate_FightMapInformationEvent() -> FightMapInformationEvent:
    return cast(
        FightMapInformationEvent,
        _create_and_fill("FightMapInformationEvent"),
    )


def generate_FightPlacementPossiblePositionsEvent() -> (
    FightPlacementPossiblePositionsEvent
):
    return cast(
        FightPlacementPossiblePositionsEvent,
        _create_and_fill("FightPlacementPossiblePositionsEvent"),
    )


def generate_FightPlacementPositionRequest() -> FightPlacementPositionRequest:
    return cast(
        FightPlacementPositionRequest,
        _create_and_fill("FightPlacementPositionRequest"),
    )


def generate_FightReadyRequest() -> FightReadyRequest:
    return cast(FightReadyRequest, _create_and_fill("FightReadyRequest"))


def generate_FightTurnStartPlayingEvent() -> FightTurnStartPlayingEvent:
    return cast(
        FightTurnStartPlayingEvent,
        _create_and_fill("FightTurnStartPlayingEvent"),
    )


def generate_GameActionFightEvent() -> GameActionFightEvent:
    return cast(GameActionFightEvent, _create_and_fill("GameActionFightEvent"))


def generate_GameActionFightCastRequest() -> GameActionFightCastRequest:
    return cast(
        GameActionFightCastRequest,
        _create_and_fill("GameActionFightCastRequest"),
    )


def generate_SequenceEndEvent() -> SequenceEndEvent:
    return cast(SequenceEndEvent, _create_and_fill("SequenceEndEvent"))


def generate_GameActionAcknowledgementRequest() -> GameActionAcknowledgementRequest:
    return cast(
        GameActionAcknowledgementRequest,
        _create_and_fill("GameActionAcknowledgementRequest"),
    )


def generate_FightLiveStateEvent() -> FightLiveStateEvent:
    return cast(FightLiveStateEvent, _create_and_fill("FightLiveStateEvent"))


def generate_FightTurnFinishRequest() -> FightTurnFinishRequest:
    return cast(FightTurnFinishRequest, _create_and_fill("FightTurnFinishRequest"))


def generate_EntitiesDispositionEvent() -> EntitiesDispositionEvent:
    return cast(
        EntitiesDispositionEvent,
        _create_and_fill("EntitiesDispositionEvent"),
    )


def generate_FightRefreshCharacterStatsEvent() -> FightRefreshCharacterStatsEvent:
    return cast(
        FightRefreshCharacterStatsEvent,
        _create_and_fill("FightRefreshCharacterStatsEvent"),
    )


def generate_MapMovementRefusedEvent() -> MapMovementRefusedEvent:
    return cast(MapMovementRefusedEvent, _create_and_fill("MapMovementRefusedEvent"))


def generate_ChatChannelMessageRequest() -> ChatChannelMessageRequest:
    return cast(
        ChatChannelMessageRequest,
        _create_and_fill("ChatChannelMessageRequest"),
    )


def generate_ChatPrivateMessageRequest() -> ChatPrivateMessageRequest:
    return cast(
        ChatPrivateMessageRequest,
        _create_and_fill("ChatPrivateMessageRequest"),
    )


def generate_ChatChannelMessageEvent() -> ChatChannelMessageEvent:
    return cast(
        ChatChannelMessageEvent,
        _create_and_fill("ChatChannelMessageEvent"),
    )


def generate_GuildMembershipEvent() -> GuildMembershipEvent:
    return cast(GuildMembershipEvent, _create_and_fill("GuildMembershipEvent"))


def generate_GuildChestCurrentListenersAddEvent() -> GuildChestCurrentListenersAddEvent:
    return cast(
        GuildChestCurrentListenersAddEvent,
        _create_and_fill("GuildChestCurrentListenersAddEvent"),
    )


def generate_ExchangeStartedWithMultiTabStorageEvent() -> (
    ExchangeStartedWithMultiTabStorageEvent
):
    return cast(
        ExchangeStartedWithMultiTabStorageEvent,
        _create_and_fill("ExchangeStartedWithMultiTabStorageEvent"),
    )


def generate_GuildChestTabSelectRequest() -> GuildChestTabSelectRequest:
    return cast(
        GuildChestTabSelectRequest,
        _create_and_fill("GuildChestTabSelectRequest"),
    )


def generate_ExchangeCraftStartedEvent() -> ExchangeCraftStartedEvent:
    return cast(
        ExchangeCraftStartedEvent,
        _create_and_fill("ExchangeCraftStartedEvent"),
    )


def generate_ExchangeSetCraftRecipeRequest() -> ExchangeSetCraftRecipeRequest:
    return cast(
        ExchangeSetCraftRecipeRequest,
        _create_and_fill("ExchangeSetCraftRecipeRequest"),
    )


def generate_ExchangeCraftCountRequest() -> ExchangeCraftCountRequest:
    return cast(
        ExchangeCraftCountRequest,
        _create_and_fill("ExchangeCraftCountRequest"),
    )


def generate_ExchangeCraftCountModifiedEvent() -> ExchangeCraftCountModifiedEvent:
    return cast(
        ExchangeCraftCountModifiedEvent,
        _create_and_fill("ExchangeCraftCountModifiedEvent"),
    )


def generate_ExchangeReadyRequest() -> ExchangeReadyRequest:
    return cast(ExchangeReadyRequest, _create_and_fill("ExchangeReadyRequest"))


# utility helpers
def get_generator(name: str) -> Callable[[], Message] | None:
    fn = globals().get(f"generate_{name}")
    if callable(fn):
        return fn  # type: ignore
    return None


def generate_by_name(name: str) -> Message | None:
    fn = get_generator(name)
    if fn is None:
        return None
    return fn()


def missing_generators() -> list[str]:
    missing: list[str] = []
    for obf, clear in d3_consts.GAME_VERIFIED_MAPPING_BY_OBF.items():
        if get_generator(clear) is None:
            missing.append(clear)
    return missing


__all__ = [
    "get_generator",
    "generate_by_name",
    "missing_generators",
]
