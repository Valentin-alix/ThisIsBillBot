"""Explicit generators for protobuf messages used in debug GUI.

Each message name present in `datas/protos/game_mappings.json`
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
from typing import Any, Callable, TypeVar

from datas.protos.non_obf.game.basic_pb2 import TextInformationEvent
from datas.protos.non_obf.game.character_management_pb2 import (
    CharacterSelectionEvent,
)
from datas.protos.non_obf.game.character_pb2 import (
    CharacterCharacteristicsEvent,
    CharacterCharacteristicUpgradeRequest,
)
from datas.protos.non_obf.game.chat_pb2 import (
    ChatChannelMessageEvent,
    ChatChannelMessageRequest,
    ChatPrivateMessageRequest,
)
from datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
)
from datas.protos.non_obf.game.context_pb2 import (
    EntitiesDispositionEvent,
)
from datas.protos.non_obf.game.dialog_pb2 import DialogLeaveRequest
from datas.protos.non_obf.game.exchange_pb2 import (
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
from datas.protos.non_obf.game.fight_pb2 import (
    FightLiveStateEvent,
    FightRefreshCharacterStatsEvent,
    FightTurnFinishRequest,
    FightTurnStartPlayingEvent,
)
from datas.protos.non_obf.game.fight_preparation_pb2 import (
    FightPlacementPositionRequest,
    FightPlacementPossiblePositionsEvent,
    FightReadyRequest,
)
from datas.protos.non_obf.game.game_action_pb2 import (
    GameActionAcknowledgementRequest,
    GameActionFightCastRequest,
    GameActionFightEvent,
    SequenceEndEvent,
)
from datas.protos.non_obf.game.gamemap_pb2 import (
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
from datas.protos.non_obf.game.guild_chest_pb2 import (
    GuildChestCurrentListenersAddEvent,
    GuildChestTabSelectRequest,
)
from datas.protos.non_obf.game.guild_member_pb2 import (
    GuildMembershipEvent,
)
from datas.protos.non_obf.game.haven_bag_pb2 import (
    HavenBagEnterRequest,
    HavenBagExitRequest,
)
from datas.protos.non_obf.game.interactive_element_pb2 import (
    InteractiveUsedEvent,
    InteractiveUseRequest,
    StatedElementUpdatedEvent,
)

# explicit protobuf imports for typing and direct construction
from datas.protos.non_obf.game.inventory_pb2 import (
    InventoryContentEvent,
    InventoryWeightEvent,
    ObjectAddedEvent,
    ObjectQuantityEvent,
    ObjectUseRequest,
    StorageInventoryContentEvent,
)
from datas.protos.non_obf.game.job_pb2 import JobExperiencesUpdateEvent
from datas.protos.non_obf.game.npc_pb2 import (
    NpcDialogQuestionEvent,
    NpcDialogReplyRequest,
    NpcGenericActionRequest,
)
from datas.protos.non_obf.game.roleplay_pb2 import AttackMonsterRequest
from datas.protos.non_obf.game.spell_pb2 import SpellsEvent
from datas.protos.non_obf.game.teleportation_pb2 import (
    TeleportRequest,
    ZaapKnownListEvent,
)
from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.grid.map_point import MAP_POINT_BY_CELL_ID
from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.message import Message
from langchain_community.vectorstores.falkordb_vector import generate_random_string

from src.protocol.protocol_game import _load_game_mappings

GAME_PROTO_PKG = "datas.protos.non_obf.game"
MessageT = TypeVar("MessageT", bound=Message)


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
        if field == FieldDescriptor.LABEL_REPEATED:
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
            if field == FieldDescriptor.LABEL_REPEATED:
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


def _create_and_fill_typed(message_type: type[MessageT]) -> MessageT:
    msg = message_type()
    _fill_message_basic(msg)
    return msg


# --- explicit generator functions (one per message name) ---
# Each of these functions is intentionally explicit so you can edit fields
# individually afterwards.


def generate_SpellsEvent() -> SpellsEvent:
    """Generate a `SpellsEvent` message."""
    return _create_and_fill_typed(SpellsEvent)


def generate_InventoryContentEvent() -> InventoryContentEvent:
    """Generate a `InventoryContentEvent` message."""
    return _create_and_fill_typed(InventoryContentEvent)


def generate_CharacterCharacteristicsEvent() -> CharacterCharacteristicsEvent:
    return _create_and_fill_typed(CharacterCharacteristicsEvent)


def generate_CharacterSelectionEvent() -> CharacterSelectionEvent:
    return _create_and_fill_typed(CharacterSelectionEvent)


def generate_InventoryWeightEvent() -> InventoryWeightEvent:
    return _create_and_fill_typed(InventoryWeightEvent)


def generate_ZaapKnownListEvent() -> ZaapKnownListEvent:
    return _create_and_fill_typed(ZaapKnownListEvent)


def generate_JobExperiencesUpdateEvent() -> JobExperiencesUpdateEvent:
    return _create_and_fill_typed(JobExperiencesUpdateEvent)


def generate_CharacterCharacteristicUpgradeRequest() -> (
    CharacterCharacteristicUpgradeRequest
):
    return _create_and_fill_typed(CharacterCharacteristicUpgradeRequest)


def generate_MapCurrentEvent() -> MapCurrentEvent:
    return _create_and_fill_typed(MapCurrentEvent)


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
    map_complementary_information_event = _create_and_fill_typed(
        MapComplementaryInformationEvent,
    )
    if map_id:
        map_complementary_information_event.map_id = map_id
    for actor in map_complementary_information_event.actors:
        actor.CopyFrom(generate_basicActorPositionInformation())
    while map_complementary_information_event.interactive_elements:
        map_complementary_information_event.interactive_elements.pop()
    return map_complementary_information_event


def generate_MapMovementRequest() -> MapMovementRequest:
    return _create_and_fill_typed(MapMovementRequest)


def generate_MapMovementEvent() -> MapMovementEvent:
    return _create_and_fill_typed(MapMovementEvent)


def generate_MapMovementConfirmRequest() -> MapMovementConfirmRequest:
    return _create_and_fill_typed(MapMovementConfirmRequest)


def generate_MapMovementConfirmResponse() -> MapMovementConfirmResponse:
    return _create_and_fill_typed(MapMovementConfirmResponse)


def generate_MapChangeRequest() -> MapChangeRequest:
    return _create_and_fill_typed(MapChangeRequest)


def generate_InteractiveUseRequest() -> InteractiveUseRequest:
    return _create_and_fill_typed(InteractiveUseRequest)


def generate_StatedElementUpdatedEvent() -> StatedElementUpdatedEvent:
    return _create_and_fill_typed(StatedElementUpdatedEvent)


def generate_InteractiveUsedEvent() -> InteractiveUsedEvent:
    return _create_and_fill_typed(InteractiveUsedEvent)


def generate_NpcGenericActionRequest() -> NpcGenericActionRequest:
    return _create_and_fill_typed(NpcGenericActionRequest)


def generate_NpcDialogQuestionEvent() -> NpcDialogQuestionEvent:
    return _create_and_fill_typed(NpcDialogQuestionEvent)


def generate_NpcDialogReplyRequest() -> NpcDialogReplyRequest:
    return _create_and_fill_typed(NpcDialogReplyRequest)


def generate_ExchangeStartedWithStorageEvent() -> ExchangeStartedWithStorageEvent:
    return _create_and_fill_typed(ExchangeStartedWithStorageEvent)


def generate_StorageInventoryContentEvent() -> StorageInventoryContentEvent:
    return _create_and_fill_typed(StorageInventoryContentEvent)


def generate_ExchangeObjectTransferAllFromInventoryRequest() -> (
    ExchangeObjectTransferAllFromInventoryRequest
):
    return _create_and_fill_typed(ExchangeObjectTransferAllFromInventoryRequest)


def generate_ExchangeObjectMoveRequest() -> ExchangeObjectMoveRequest:
    return _create_and_fill_typed(ExchangeObjectMoveRequest)


def generate_ObjectAddedEvent() -> ObjectAddedEvent:
    return _create_and_fill_typed(ObjectAddedEvent)


def generate_ObjectQuantityEvent() -> ObjectQuantityEvent:
    return _create_and_fill_typed(ObjectQuantityEvent)


def generate_ExchangeMoveKamaRequest() -> ExchangeMoveKamaRequest:
    return _create_and_fill_typed(ExchangeMoveKamaRequest)


def generate_DialogLeaveRequest() -> DialogLeaveRequest:
    return _create_and_fill_typed(DialogLeaveRequest)


def generate_ExchangeLeaveEvent() -> ExchangeLeaveEvent:
    return _create_and_fill_typed(ExchangeLeaveEvent)


def generate_HavenBagEnterRequest() -> HavenBagEnterRequest:
    return _create_and_fill_typed(HavenBagEnterRequest)


def generate_HavenBagExitRequest() -> HavenBagExitRequest:
    return _create_and_fill_typed(HavenBagExitRequest)


def generate_ObjectUseRequest() -> ObjectUseRequest:
    return _create_and_fill_typed(ObjectUseRequest)


def generate_TeleportRequest() -> TeleportRequest:
    return _create_and_fill_typed(TeleportRequest)


def generate_ExchangeBidSellerStartedEvent() -> ExchangeBidSellerStartedEvent:
    return _create_and_fill_typed(ExchangeBidSellerStartedEvent)


def generate_ExchangeBidHouseSearchRequest() -> ExchangeBidHouseSearchRequest:
    return _create_and_fill_typed(ExchangeBidHouseSearchRequest)


def generate_ExchangeBidHousePriceRequest() -> ExchangeBidHousePriceRequest:
    return _create_and_fill_typed(ExchangeBidHousePriceRequest)


def generate_ExchangeBidPriceEvent() -> ExchangeBidPriceEvent:
    return _create_and_fill_typed(ExchangeBidPriceEvent)


def generate_ExchangeObjectMovePricedRequest() -> ExchangeObjectMovePricedRequest:
    return _create_and_fill_typed(ExchangeObjectMovePricedRequest)


def generate_ExchangeObjectModifyPricedRequest() -> ExchangeObjectModifyPricedRequest:
    return _create_and_fill_typed(ExchangeObjectModifyPricedRequest)


def generate_ExchangeBidHouseItemAddedEvent() -> ExchangeBidHouseItemAddedEvent:
    return _create_and_fill_typed(ExchangeBidHouseItemAddedEvent)


def generate_ExchangeBidHouseItemRemovedEvent() -> ExchangeBidHouseItemRemovedEvent:
    return _create_and_fill_typed(ExchangeBidHouseItemRemovedEvent)


def generate_TextInformationEvent() -> TextInformationEvent:
    return _create_and_fill_typed(TextInformationEvent)


def generate_AttackMonsterRequest() -> AttackMonsterRequest:
    return _create_and_fill_typed(AttackMonsterRequest)


def generate_FightMapInformationEvent() -> FightMapInformationEvent:
    return _create_and_fill_typed(FightMapInformationEvent)


def generate_FightPlacementPossiblePositionsEvent() -> (
    FightPlacementPossiblePositionsEvent
):
    return _create_and_fill_typed(FightPlacementPossiblePositionsEvent)


def generate_FightPlacementPositionRequest() -> FightPlacementPositionRequest:
    return _create_and_fill_typed(FightPlacementPositionRequest)


def generate_FightReadyRequest() -> FightReadyRequest:
    return _create_and_fill_typed(FightReadyRequest)


def generate_FightTurnStartPlayingEvent() -> FightTurnStartPlayingEvent:
    return _create_and_fill_typed(FightTurnStartPlayingEvent)


def generate_GameActionFightEvent() -> GameActionFightEvent:
    return _create_and_fill_typed(GameActionFightEvent)


def generate_GameActionFightCastRequest() -> GameActionFightCastRequest:
    return _create_and_fill_typed(GameActionFightCastRequest)


def generate_SequenceEndEvent() -> SequenceEndEvent:
    return _create_and_fill_typed(SequenceEndEvent)


def generate_GameActionAcknowledgementRequest() -> GameActionAcknowledgementRequest:
    return _create_and_fill_typed(GameActionAcknowledgementRequest)


def generate_FightLiveStateEvent() -> FightLiveStateEvent:
    return _create_and_fill_typed(FightLiveStateEvent)


def generate_FightTurnFinishRequest() -> FightTurnFinishRequest:
    return _create_and_fill_typed(FightTurnFinishRequest)


def generate_EntitiesDispositionEvent() -> EntitiesDispositionEvent:
    return _create_and_fill_typed(EntitiesDispositionEvent)


def generate_FightRefreshCharacterStatsEvent() -> FightRefreshCharacterStatsEvent:
    return _create_and_fill_typed(FightRefreshCharacterStatsEvent)


def generate_MapMovementRefusedEvent() -> MapMovementRefusedEvent:
    return _create_and_fill_typed(MapMovementRefusedEvent)


def generate_ChatChannelMessageRequest() -> ChatChannelMessageRequest:
    return _create_and_fill_typed(ChatChannelMessageRequest)


def generate_ChatPrivateMessageRequest() -> ChatPrivateMessageRequest:
    return _create_and_fill_typed(ChatPrivateMessageRequest)


def generate_ChatChannelMessageEvent() -> ChatChannelMessageEvent:
    return _create_and_fill_typed(ChatChannelMessageEvent)


def generate_GuildMembershipEvent() -> GuildMembershipEvent:
    return _create_and_fill_typed(GuildMembershipEvent)


def generate_GuildChestCurrentListenersAddEvent() -> GuildChestCurrentListenersAddEvent:
    return _create_and_fill_typed(GuildChestCurrentListenersAddEvent)


def generate_ExchangeStartedWithMultiTabStorageEvent() -> (
    ExchangeStartedWithMultiTabStorageEvent
):
    return _create_and_fill_typed(ExchangeStartedWithMultiTabStorageEvent)


def generate_GuildChestTabSelectRequest() -> GuildChestTabSelectRequest:
    return _create_and_fill_typed(GuildChestTabSelectRequest)


def generate_ExchangeCraftStartedEvent() -> ExchangeCraftStartedEvent:
    return _create_and_fill_typed(ExchangeCraftStartedEvent)


def generate_ExchangeSetCraftRecipeRequest() -> ExchangeSetCraftRecipeRequest:
    return _create_and_fill_typed(ExchangeSetCraftRecipeRequest)


def generate_ExchangeCraftCountRequest() -> ExchangeCraftCountRequest:
    return _create_and_fill_typed(ExchangeCraftCountRequest)


def generate_ExchangeCraftCountModifiedEvent() -> ExchangeCraftCountModifiedEvent:
    return _create_and_fill_typed(ExchangeCraftCountModifiedEvent)


def generate_ExchangeReadyRequest() -> ExchangeReadyRequest:
    return _create_and_fill_typed(ExchangeReadyRequest)


# utility helpers
def get_generator(name: str) -> Callable[[], Message] | None:
    candidate = globals().get(f"generate_{name}")
    if not callable(candidate):
        return None

    def generator() -> Message:
        result = candidate()
        if not isinstance(result, Message):
            raise TypeError(f"Generator generate_{name} returned {type(result)!r}")
        return result

    if _find_message_class(name) is None:
        return None

    if callable(candidate):
        return generator
    return None


def generate_by_name(name: str) -> Message | None:
    fn = get_generator(name)
    if fn is None:
        return None
    return fn()


def missing_generators() -> list[str]:
    missing: list[str] = []
    for namespace in _load_game_mappings():
        clear_name = namespace[1:]
        if get_generator(clear_name) is None:
            missing.append(clear_name)
    return missing


__all__ = [
    "get_generator",
    "generate_by_name",
    "missing_generators",
]
