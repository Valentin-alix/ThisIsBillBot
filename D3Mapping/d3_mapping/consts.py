import os
from enum import StrEnum
from pathlib import Path

from D3Database.consts import DOFUS_PATH

ROOT_PATH = Path(__file__).parent.parent

TYPE_URL_PREFIX = "type.ankama.com/"

IL2_CPP_DUMPER_PATH_EXE = os.path.join(
    ROOT_PATH,
    "Il2CppDumper",
    "Il2CppDumper",
    "bin",
    "Debug",
    "net8.0",
    "IL2CppDumper.exe",
)
PROTODEC_PATH_EXE = os.path.join(
    Path(__file__).parent.parent,
    "protodec",
    "bin",
    "protodec",
    "Debug",
    "net8.0",
    "protodec.exe",
)

ASSEMBLIES_PATH = os.path.join(DOFUS_PATH, "assemblies")
GAME_ASSEMBLY_PATH = os.path.join(DOFUS_PATH, "GameAssembly.dll")
GLOBAL_METADATA_PATH = os.path.join(
    DOFUS_PATH, "Dofus_Data", "il2cpp_data", "Metadata", "global-metadata.dat"
)


PROTO_CONNECTION_ASSEMBLY_PATH = os.path.join(
    ASSEMBLIES_PATH, "DummyDll", "Ankama.Dofus.Protocol.Connection.dll"
)
PROTO_GAME_ASSEMBLY_PATH = os.path.join(
    ASSEMBLIES_PATH, "DummyDll", "Ankama.Dofus.Protocol.Game.dll"
)


RESOURCE_PATH = os.path.join(ROOT_PATH, "d3_mapping", "resources")

OBFUSCATED_PROTOS = os.path.join(RESOURCE_PATH, "obf_protos")
OBFUSCATED_PROTO_CONNECTION = os.path.join(OBFUSCATED_PROTOS, "connection")
OBFUSCATED_PROTO_CONNECTION_FILE = os.path.join(
    OBFUSCATED_PROTO_CONNECTION, "connection_messages.proto"
)
OBFUSCATED_PROTO_GAME = os.path.join(OBFUSCATED_PROTOS, "game")
OBFUSCATED_PROTO_GAME_FILE = os.path.join(OBFUSCATED_PROTO_GAME, "game_messages.proto")

PROTO_ROOT_PATH = os.path.join(RESOURCE_PATH, "protos")
PROTO_CONNECTION_PATH = os.path.join(PROTO_ROOT_PATH, "connection")
PROTO_GAME_PATH = os.path.join(PROTO_ROOT_PATH, "game")

MAPPING_CONN_PROTO_PATH = os.path.join(RESOURCE_PATH, "connection_mappings.json")
MAPPING_GAME_PROTO_PATH = os.path.join(RESOURCE_PATH, "game_mappings.json")

GAME_VERIFIED_MAPPING_BY_OBF: dict[str, str] = {
    "jfq": "CharacterSelectionEvent",
    "ifr": "MapMovementRequest",
    "ifn": "MapMovementEvent",
    "igb": "MapMovementConfirmRequest",
    "iex": "MapMovementConfirmResponse",
    "hla": "NpcGenericActionRequest",
    "hku": "NpcDialogQuestionEvent",
    "hkx": "NpcDialogReplyRequest",
    "htf": "StorageInventoryContentEvent",
    "iwn": "DialogLeaveRequest",
    "hpv": "JobExperiencesUpdateEvent",
    "igm": "MapComplementaryInformationEvent",
    "iup": "ExchangeObjectTransferAllFromInventoryRequest",
    "hts": "InteractiveUseRequest",
    "htz": "StatedElementUpdatedEvent",
    "hua": "InteractiveUsedEvent",
    "ifa": "MapChangeRequest",
    "ifz": "MapCurrentEvent",
    "hzc": "HavenBagEnterRequest",
    "grt": "ZaapKnownListEvent",
    "grs": "TeleportRequest",
    "hsn": "ObjectUseRequest",
    # # fight
    "ioq": "FightPlacementPossiblePositionsEvent",
    "iky": "FightTurnStartPlayingEvent",
    "gvw": "SpellsEvent",  # 12728
    "ion": "FightPlacementPositionRequest",
    "ijd": "GameActionFightEvent",
    "ijv": "GameActionFightCastRequest",
    "imu": "FightTurnFinishRequest",
    "ije": "SequenceEndEvent",
    "ifc": "FightMapInformationEvent",
    "ixw": "EntitiesDispositionEvent",
    "jem": "CharacterCharacteristicsEvent",
    "ine": "FightReadyRequest",
    "ika": "GameActionAcknowledgementRequest",
    "iki": "FightRefreshCharacterStatsEvent",
    "hrp": "InventoryWeightEvent",
    "irv": "ExchangeLeaveEvent",
    # # revive
    "jef": "FreeSoulRequest",
    "jdz": "CharacterLifeStatusEvent",
    # # sale hotel
    "ipm": "ExchangeBidSellerStartedEvent",
    "iqe": "ExchangeBidHouseSearchRequest",
    "iqo": "ExchangeBidHousePriceRequest",
    "irf": "ExchangeBidPriceEvent",
    "iqu": "ExchangeObjectMovePricedRequest",
    "iqc": "ExchangeObjectModifyPricedRequest",
    "ivb": "ExchangeBidHouseItemAddedEvent",
    "iqx": "ExchangeBidHouseItemRemovedEvent",
    "ipv": "ExchangeObjectMoveRequest",
    "jxv": "TextInformationEvent",
    "ios": "ExchangeStartedWithStorageEvent",
    "hrk": "InventoryContentEvent",
    "hsf": "ObjectAddedEvent",
    # # kamas
    "iux": "ExchangeMoveKamaRequest",
    # # fighter
    "gym": "AttackMonsterRequest",
    "ifx": "MapMovementRefusedEvent",
    "jdn": "ChatChannelMessageRequest",
    "jea": "CharacterCharacteristicUpgradeRequest",
    "inc": "FightLiveStateEvent",
}


GAME_MAPPING_FIELDS: dict[str, dict[str, str]] = {
    "GameMessage": {"request": "eqwb", "event": "eqwc", "response": "eqwd"},
    "InteractiveElement": {"enabled_skills": "fecc"},
    "InteractiveUseRequest": {"element_id": "evtn"},
}


RELIABILITY_BY_PROTO_BASE_FIELDS: dict[str, float] = {
    "int32": 1,
    "int64": 1,
    "float": 1,
    "bool": 1,
    "string": 1,
    "google.protobuf.Any": 10,
}

PROTO_BASE_FIELDS: list[str] = list(RELIABILITY_BY_PROTO_BASE_FIELDS.keys())

LIMIT = 0.7

BASE_RELIABILITY = 1
EXTRA_RELIABILITY_REPEATED = 2
EXTRA_RELIABILITY_MAP = 2
EXTRA_RELIABILITY_ENUM = 3
EXTRA_RELIABILITY_MESSAGE = 2
EXTRA_RELIABILITY_WITH_VALIDATOR = 5


class EntryMsg(StrEnum):
    REQUEST = "Request"
    RESPONSE = "Response"
    EVENT = "Event"
