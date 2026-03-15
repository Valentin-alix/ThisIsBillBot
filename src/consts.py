import datetime
import os
import socket
from functools import cache
from pathlib import Path

from dotenv import load_dotenv
from google.protobuf.message import Message

from DBDofusUnity.datas.protos.non_obf.game.admin_console_pb2 import ConsoleCommand
from DBDofusUnity.datas.protos.non_obf.game.arena_pb2 import (
    ArenaFightAnswerRequest,
    ArenaModesStatusRequest,
    ArenaRegisterRequest,
)
from DBDofusUnity.datas.protos.non_obf.game.basic_pb2 import BasicLatencyStatsRequest
from DBDofusUnity.datas.protos.non_obf.game.breeding_pb2 import (
    MountBoostRequest,
)
from DBDofusUnity.datas.protos.non_obf.game.character_pb2 import (
    CharacterCharacteristicUpgradeRequest,
)
from DBDofusUnity.datas.protos.non_obf.game.client_verification_pb2 import (
    ClientChallengeInitRequest,
    ClientChallengeProofRequest,
    ClientIdRequest,
)
from DBDofusUnity.datas.protos.non_obf.game.player_info_pb2 import PlayerInfoRequest
from DBDofusUnity.datas.protos.non_obf.game.preset_pb2 import (
    CharacterPresetResetRequest,
    PresetDeleteRequest,
    PresetEquipmentUpdateRequest,
    PresetOutfitUpdateRequest,
    PresetRenameRequest,
    PresetSaveRequest,
    PresetSetFavoriteRequest,
    PresetSymbolUpdateRequest,
    PresetUseRequest,
)
from DBDofusUnity.datas.protos.non_obf.game.report_pb2 import ReportRequest
from DBDofusUnity.datas.protos.non_obf.game.tag_storage_pb2 import (
    AddTagStorageRequest,
    RemoveTagStorageRequest,
    UpdateTagStorageContentRequest,
)
from src.utils.project_paths import BUNDLE_ROOT, ENV_PATH, USER_DATA_ROOT
from src.core.config import DEBUG as DEBUG

load_dotenv(ENV_PATH)


BACKEND_URL = "http://localhost:8000"

FILTER_DOFUS = "tcp port 5555"
DOFUS_CONNECTION_URL = "dofus2-co-production.ankama-games.com"


@cache
def get_connection_servers_ips() -> list[str]:
    return [*socket.gethostbyname_ex(DOFUS_CONNECTION_URL)[2], DOFUS_CONNECTION_URL]


RESOURCE_FOLDER = os.path.join(USER_DATA_ROOT, "resources")
LOGO_FILE = str(BUNDLE_ROOT / "resources" / "icons" / "logo.png")
BOT_DEBUG_LOGS_DIR = Path(RESOURCE_FOLDER) / "debug" / "bots"

MIN_DATE = datetime.datetime(datetime.MINYEAR, 1, 1)
FAKE_INFINITY_VALUE = 99999

SUBSCRIPTION_CATEGORY_ID = 698
DOFUS_SUBSCRIPTION_REFERENCE_ID = "10"
SUBSCRIPTION_DAYS = 7
SUBSCRIPTION_EVENT_TIMEOUT_SECONDS = 15
SUBSCRIPTION_MIN_LEVEL = 30
SUBSCRIPTION_MIN_KAMAS = 15_000
MAX_BOTS_PER_SCHEDULE_PROFILE = 6

MESSAGES_WITH_UID: list[type[Message]] = [
    ClientIdRequest,
    ClientChallengeInitRequest,
    ClientChallengeProofRequest,
    PresetSaveRequest,
    PresetUseRequest,
    PresetDeleteRequest,
    PresetRenameRequest,
    PresetSymbolUpdateRequest,
    PresetSetFavoriteRequest,
    PresetEquipmentUpdateRequest,
    PresetOutfitUpdateRequest,
    CharacterPresetResetRequest,
    MountBoostRequest,
    AddTagStorageRequest,
    RemoveTagStorageRequest,
    UpdateTagStorageContentRequest,
    ArenaRegisterRequest,
    ArenaFightAnswerRequest,
    ArenaModesStatusRequest,
    PlayerInfoRequest,
    ReportRequest,
    CharacterCharacteristicUpgradeRequest,
    BasicLatencyStatsRequest,
    ConsoleCommand,
]
