import datetime
import os
import socket
from pathlib import Path

from google.protobuf.message import Message

from d3_mapping.resources.protos.game.challenge_pb2 import ChallengeModSelectRequest
from d3_mapping.resources.protos.game.character_pb2 import (
    CharacterCharacteristicsEvent,
    CharacterLifeStatusEvent,
)
from d3_mapping.resources.protos.game.context_pb2 import (
    ContextCreationEvent,
    ContextRemoveElementEvent,
    EntitiesDispositionEvent,
)
from d3_mapping.resources.protos.game.dialog_pb2 import DialogLeaveRequest
from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeStartedWithMultiTabStorageEvent,
)
from d3_mapping.resources.protos.game.fight_pb2 import (
    FightEndEvent,
    FightFighterShowEvent,
    FightIsTurnReadyEvent,
    FightNewRoundEvent,
    FightSynchronizeEvent,
    FightTurnEndEvent,
    FightTurnEvent,
    FightTurnFinishRequest,
    FightTurnReadyRequest,
)
from d3_mapping.resources.protos.game.fight_preparation_pb2 import (
    FightPlacementPossiblePositionsEvent,
    FightStartingEvent,
    FightTeamUpdateEvent,
)
from d3_mapping.resources.protos.game.game_action_pb2 import GameActionFightEvent
from d3_mapping.resources.protos.game.gamemap_pb2 import (
    FightMapInformationEvent,
    GameRolePlayShowActorsEvent,
    MapComplementaryInformationEvent,
    MapCurrentEvent,
    MapMovementConfirmRequest,
    MapMovementEvent,
    MapMovementRefusedEvent,
    MapTeleportOnSameEvent,
)
from d3_mapping.resources.protos.game.interactive_element_pb2 import (
    InteractiveElementUpdatedEvent,
    InteractiveMapUpdateEvent,
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
from d3_mapping.resources.protos.game.job_pb2 import JobExperiencesUpdateEvent
from d3_mapping.resources.protos.game.spell_pb2 import (
    SpellsEvent,
)

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
VERY_SMALL_RANGE = (0.1, 0.3)
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


NEEDED_MSG_MAPPING: list[type[Message]] = [
    MapComplementaryInformationEvent,
    MapMovementConfirmRequest,
    MapCurrentEvent,
    MapMovementEvent,
    MapTeleportOnSameEvent,
    MapMovementRefusedEvent,
    ContextRemoveElementEvent,
    ContextCreationEvent,
    GameRolePlayShowActorsEvent,
    EntitiesDispositionEvent,
    InteractiveMapUpdateEvent,
    InteractiveElementUpdatedEvent,
    StatedMapUpdateEvent,
    StatedElementUpdatedEvent,
    GameActionFightEvent,
    FightTeamUpdateEvent,
    FightSynchronizeEvent,
    FightFighterShowEvent,
    FightPlacementPossiblePositionsEvent,
    FightEndEvent,
    FightStartingEvent,
    FightNewRoundEvent,
    FightIsTurnReadyEvent,
    FightTurnEvent,
    FightTurnReadyRequest,
    FightTurnFinishRequest,
    FightTurnEndEvent,
    FightMapInformationEvent,
    ChallengeModSelectRequest,
    SpellsEvent,
    CharacterCharacteristicsEvent,
    CharacterLifeStatusEvent,
    ExchangeStartedWithMultiTabStorageEvent,
    InventoryWeightEvent,
    InventoryContentEvent,
    ObjectsDeletedEvent,
    ObjectDeletedEvent,
    ObjectQuantityEvent,
    ObjectsQuantityEvent,
    ObjectAddedEvent,
    ObjectsAddedEvent,
    DialogLeaveRequest,
    JobExperiencesUpdateEvent,
]
