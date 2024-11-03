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
    "jka": "CharacterSelectionEvent",  # 34389033310
    "iib": "MapMovementRequest",
    "iiu": "MapMovementEvent",
    "iht": "MapMovementConfirmRequest",
    "iit": "MapMovementConfirmResponse",
    "hmx": "NpcGenericActionRequest",
    "hnm": "NpcDialogQuestionEvent",
    "hnh": "NpcDialogReplyRequest",
    "htn": "StorageInventoryContentEvent",
    "jak": "DialogLeaveRequest",
    "hrq": "JobExperiencesUpdateEvent",
    "ihy": "MapComplementaryInformationEvent",
    "izb": "ExchangeObjectTransferAllFromInventoryRequest",
    "hwg": "InteractiveUseRequest",
    "hwo": "StatedElementUpdatedEvent",
    "hwn": "InteractiveUsedEvent",
    "ihc": "MapChangeRequest",
    "iik": "MapCurrentEvent",
    "ibp": "HavenBagEnterRequest",
    "guu": "ZaapKnownListEvent",
    "guf": "TeleportRequest",
    "htq": "ObjectUseRequest",
    # fight
    "iri": "FightPlacementPossiblePositionsEvent",
    "ipk": "FightTurnStartPlayingEvent",
    "gyu": "SpellsEvent",  # 12728
    "iqc": "FightPlacementPositionRequest",
    "imu": "GameActionFightEvent",
    "ijv": "GameActionFightCastRequest",
    "ipc": "FightTurnFinishRequest",
    "ijy": "SequenceEndEvent",
    "iih": "FightMapInformationEvent",
    "jca": "EntitiesDispositionEvent",
    "jhx": "CharacterCharacteristicsEvent",
    "iqg": "FightReadyRequest",
    "ijx": "GameActionAcknowledgementRequest",
    "iob": "FightRefreshCharacterStatsEvent",
    "hus": "InventoryWeightEvent",
    "irs": "ExchangeLeaveEvent",
    # # # revive
    # "jef": "FreeSoulRequest",
    # "jdz": "CharacterLifeStatusEvent",
    # # # sale hotel
    "itn": "ExchangeBidSellerStartedEvent",
    "isp": "ExchangeBidHouseSearchRequest",
    "isk": "ExchangeBidHousePriceRequest",
    "iuv": "ExchangeBidPriceEvent",
    "isu": "ExchangeObjectMovePricedRequest",
    "ivj": "ExchangeObjectModifyPricedRequest",
    "iux": "ExchangeBidHouseItemAddedEvent",
    "ito": "ExchangeBidHouseItemRemovedEvent",
    "itf": "ExchangeObjectMoveRequest",
    "kbj": "TextInformationEvent",
    "iyt": "ExchangeStartedWithStorageEvent",
    "hut": "InventoryContentEvent",
    "huf": "ObjectAddedEvent",
    # kamas
    "its": "ExchangeMoveKamaRequest",
    # # # fighter
    "hbn": "AttackMonsterRequest",
    "ihs": "MapMovementRefusedEvent",
    "jio": "CharacterCharacteristicUpgradeRequest",
    "iqa": "FightLiveStateEvent",
    "iaz": "HavenBagExitRequest",
    "jhp": "ChatChannelMessageRequest",
    "jhf": "ChatPrivateMessageRequest",
    "jhd": "ChatChannelMessageEvent",
}


GAME_MAPPING_FIELDS: dict[str, dict[str, str]] = {
    # "GameMessage": {"request": "euht", "event": "euhr", "response": "euhs"},
    "InteractiveElement": {"enabled_skills": "fhsp"},
    "InteractiveUseRequest": {"element_id": "ezia"},
    "CharacterCharacteristic": {"usable": "fhtr"},
    "MapChangeRequest": {"map_id": "fbaw"},
    "GameActionFightEvent": {"slide": "fbyw", "exchange_positions": "fbyi"},
    "CharacterCharacteristicDetailedUsable": {
        "base": "ffzc",
        "additional": "ffze",
        "objects_and_mount_bonus": "ffzb",
        "alignment_gift_bonus": "ffzg",
        "context_modification": "ffzh",
        "used": "ffzd",
        "temporary": "ffzf",
    },
}


RELIABILITY_BY_PROTO_BASE_FIELDS: dict[str, float] = {
    "int32": 1,
    "uint32": 1,
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
