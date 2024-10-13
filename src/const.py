import datetime
import os
import socket
from pathlib import Path

from google.protobuf.message import Message

from d3_mapping.resources.protos.game.challenge_pb2 import ChallengeModSelectRequest
from d3_mapping.resources.protos.game.character_management_pb2 import (
    CharacterSelectionEvent,
)
from d3_mapping.resources.protos.game.character_pb2 import (
    CharacterCharacteristicsEvent,
    CharacterLifeStatusEvent,
)
from d3_mapping.resources.protos.game.context_pb2 import (
    ContextCreationEvent,
    ContextRemoveElementEvent,
    EntitiesDispositionEvent,
)
from d3_mapping.resources.protos.game.dialog_pb2 import (
    DialogLeaveEvent,
    DialogLeaveRequest,
)
from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeBidHouseItemAddedEvent,
    ExchangeBidHouseItemRemovedEvent,
    ExchangeBidHouseSearchRequest,
    ExchangeBidPriceEvent,
    ExchangeBidSellerStartedEvent,
    ExchangeStartedWithMultiTabStorageEvent,
    ObjectAveragePricesEvent,
)
from d3_mapping.resources.protos.game.fight_pb2 import (
    FightEndEvent,
    FightFighterRefreshEvent,
    FightFighterShowEvent,
    FightIsTurnReadyEvent,
    FightRefreshCharacterStatsEvent,
    FightSynchronizeEvent,
    FightTurnEndEvent,
    FightTurnEvent,
    FightTurnFinishRequest,
    FightTurnReadyRequest,
)
from d3_mapping.resources.protos.game.fight_preparation_pb2 import (
    FightPlacementPossiblePositionsEvent,
    FightStartingEvent,
)
from d3_mapping.resources.protos.game.game_action_pb2 import (
    GameActionAcknowledgementRequest,
    GameActionFightEvent,
    SequenceEndEvent,
)
from d3_mapping.resources.protos.game.gamemap_pb2 import (
    FightMapInformationEvent,
    GameRolePlayShowActorsEvent,
    MapChangeRequest,
    MapComplementaryInformationEvent,
    MapCurrentEvent,
    MapMovementConfirmRequest,
    MapMovementConfirmResponse,
    MapMovementEvent,
    MapMovementRefusedEvent,
    MapTeleportOnSameEvent,
)
from d3_mapping.resources.protos.game.haven_bag_pb2 import (
    HavenBagEnterRequest,
    HavenBagFurnitureEvent,
)
from d3_mapping.resources.protos.game.interactive_element_pb2 import (
    InteractiveElementUpdatedEvent,
    InteractiveMapUpdateEvent,
    InteractiveUseErrorEvent,
    InteractiveUseRequest,
    InteractiveUsedEvent,
    StatedElementUpdatedEvent,
    StatedMapUpdateEvent,
)
from d3_mapping.resources.protos.game.inventory_pb2 import (
    InventoryContentEvent,
    InventoryWeightEvent,
    ObjectAddedEvent,
    ObjectDeletedEvent,
    ObjectQuantityEvent,
    ObjectsAddedEvent,
    ObjectsDeletedEvent,
    ObjectsQuantityEvent,
)
from d3_mapping.resources.protos.game.spell_pb2 import (
    SpellsEvent,
)
from d3_mapping.resources.protos.game.teleportation_pb2 import ZaapKnownListEvent

DEBUG = True

FILTER_DOFUS = "tcp port 5555"
DOFUS_CONNECTION_URL = "dofus2-co-production.ankama-games.com"
CONNECTION_SERVERS_IPS: list[str] = socket.gethostbyname_ex(DOFUS_CONNECTION_URL)[2]
TYPE_URL_PREFIX = "type.ankama.com/"

RESOURCE_FOLDER = os.path.join(Path(__file__).parent.parent, "resources")
MITM_CONFIG_URL = os.path.join(RESOURCE_FOLDER, "config.json")

MIN_DATE = datetime.datetime(datetime.MINYEAR, 1, 1)

FAKE_INFINITY_VALUE = 99999

# Waiting times timing
VERY_SMALL_RANGE = (0.2, 0.4)
SMALL_RANGE = (0.3, 1)
BASE_RANGE = (0.5, 1.5)
ON_NEW_MAP_BEFORE_ACTION = (0.5, 4.5)

# Bank
ON_OPENED_INVENTORY = BASE_RANGE
BEFORE_CLOSING_INVENTORY = BASE_RANGE

# Fight
ON_STARTED_FIGHT = BASE_RANGE
ON_PLAYER_TURN = SMALL_RANGE
ON_PLAYER_MOVED = SMALL_RANGE
ON_PLAYED_SPELL = VERY_SMALL_RANGE
ON_CHALLENGE = VERY_SMALL_RANGE

# Npc
BETWEEN_REPLY = BASE_RANGE


# below msgs are needed msg
NEEDED_MSG_MAPPING: list[type[Message]] = [
    ChallengeModSelectRequest,
    CharacterCharacteristicsEvent,
    CharacterLifeStatusEvent,  # for phenix
    CharacterSelectionEvent,
    ContextCreationEvent,
    ContextRemoveElementEvent,
    DialogLeaveEvent,
    DialogLeaveRequest,
    EntitiesDispositionEvent,
    ExchangeBidHouseItemAddedEvent,
    ExchangeBidHouseItemRemovedEvent,
    ExchangeBidHouseSearchRequest,
    ExchangeBidPriceEvent,
    ExchangeBidSellerStartedEvent,
    ExchangeStartedWithMultiTabStorageEvent,
    FightEndEvent,
    FightFighterRefreshEvent,
    FightFighterShowEvent,
    FightIsTurnReadyEvent,
    FightMapInformationEvent,
    FightPlacementPossiblePositionsEvent,
    FightRefreshCharacterStatsEvent,
    FightStartingEvent,
    FightSynchronizeEvent,
    FightTurnEndEvent,
    FightTurnEvent,
    FightTurnFinishRequest,
    FightTurnReadyRequest,
    GameActionAcknowledgementRequest,
    GameActionFightEvent,
    GameRolePlayShowActorsEvent,
    HavenBagEnterRequest,
    HavenBagFurnitureEvent,
    InteractiveElementUpdatedEvent,
    InteractiveMapUpdateEvent,
    InteractiveUseErrorEvent,
    InteractiveUsedEvent,
    InteractiveUseRequest,
    InventoryContentEvent,
    InventoryWeightEvent,
    MapChangeRequest,
    MapComplementaryInformationEvent,
    MapCurrentEvent,
    MapMovementConfirmRequest,
    MapMovementConfirmResponse,
    MapMovementEvent,
    MapMovementRefusedEvent,
    MapTeleportOnSameEvent,
    ObjectAddedEvent,
    ObjectAveragePricesEvent,
    ObjectDeletedEvent,
    ObjectQuantityEvent,
    ObjectsAddedEvent,
    ObjectsDeletedEvent,
    ObjectsQuantityEvent,
    SequenceEndEvent,
    SpellsEvent,
    StatedElementUpdatedEvent,
    StatedMapUpdateEvent,
    ZaapKnownListEvent,
]
