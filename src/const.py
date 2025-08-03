"""
Constantes système et infrastructure du bot.
Configuration de l'environnement d'exécution, chemins, connexions réseau.

⚠️ Ces valeurs concernent le système d'exécution, pas le jeu Dofus.
Pour les constantes du jeu, voir DBDofusUnity/dofus_unity_reader/enums/.
Pour la configuration du bot, voir src/core/config.py
"""

import datetime
import os
import socket
from pathlib import Path

from datas.protos.non_obf.game.admin_console_pb2 import ConsoleCommand
from datas.protos.non_obf.game.arena_pb2 import (
    ArenaFightAnswerRequest,
    ArenaModesStatusRequest,
    ArenaRegisterRequest,
)
from datas.protos.non_obf.game.basic_pb2 import BasicLatencyStatsRequest
from datas.protos.non_obf.game.breeding_pb2 import (
    MountBoostRequest,
    UnknownHqv,
    UnknownHqw,
    UnknownHut,
)
from datas.protos.non_obf.game.character_pb2 import (
    CharacterCharacteristicUpgradeRequest,
)
from datas.protos.non_obf.game.client_verification_pb2 import (
    ClientChallengeInitRequest,
    ClientChallengeProofRequest,
    ClientIdRequest,
)
from datas.protos.non_obf.game.player_info_pb2 import PlayerInfoRequest, UnknownLag
from datas.protos.non_obf.game.preset_pb2 import (
    CharacterPresetResetRequest,
    PresetDeleteRequest,
    PresetEquipmentUpdateRequest,
    PresetOutfitUpdateRequest,
    PresetRenameRequest,
    PresetSaveRequest,
    PresetSetFavoriteRequest,
    PresetSymbolUpdateRequest,
    PresetUseRequest,
    UnknownIin,
)
from datas.protos.non_obf.game.report_pb2 import ReportRequest
from datas.protos.non_obf.game.tag_storage_pb2 import (
    AddTagStorageRequest,
    RemoveTagStorageRequest,
    UpdateTagStorageContentRequest,
)
from dotenv import load_dotenv
from google.protobuf.message import Message

from project_paths import ENV_PATH

load_dotenv(ENV_PATH)


def _read_bool_env(name: str, default: bool) -> bool:
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default
    normalized = raw_value.strip().lower()
    return bool(int(normalized))


# ============================================================================
# SYSTÈME
# ============================================================================

DEBUG = _read_bool_env("DEBUG", True)

# ============================================================================
# BACKEND & RÉSEAU
# ============================================================================

BACKEND_URL = "http://localhost:8000"

FILTER_DOFUS = "tcp port 5555"
DOFUS_CONNECTION_URL = "dofus2-co-production.ankama-games.com"
CONNECTION_SERVERS_IPS: list[str] = [
    *socket.gethostbyname_ex(DOFUS_CONNECTION_URL)[2],
    DOFUS_CONNECTION_URL,
]


# ============================================================================
# CHEMINS FICHIERS
# ============================================================================

RESOURCE_FOLDER = os.path.join(Path(__file__).parent.parent, "resources")
LOGO_FILE = os.path.join(RESOURCE_FOLDER, "icons", "logo.png")

# ============================================================================
# UTILITAIRES
# ============================================================================

MIN_DATE = datetime.datetime(datetime.MINYEAR, 1, 1)
FAKE_INFINITY_VALUE = 99999

# ============================================================================
# MESSAGES PROTOBUF
# ============================================================================

MESSAGES_WITH_UID: list[type[Message]] = [
    # Verification client (handshake)
    ClientIdRequest,
    ClientChallengeInitRequest,
    ClientChallengeProofRequest,
    # Presets
    PresetSaveRequest,
    PresetUseRequest,
    PresetDeleteRequest,
    PresetRenameRequest,
    PresetSymbolUpdateRequest,
    PresetSetFavoriteRequest,
    PresetEquipmentUpdateRequest,
    PresetOutfitUpdateRequest,
    CharacterPresetResetRequest,
    UnknownIin,
    # Montures
    MountBoostRequest,
    UnknownHut,
    UnknownHqv,
    UnknownHqw,
    # Tags de stockage
    AddTagStorageRequest,
    RemoveTagStorageRequest,
    UpdateTagStorageContentRequest,
    # Arene
    ArenaRegisterRequest,
    ArenaFightAnswerRequest,
    ArenaModesStatusRequest,
    # Joueur / signalement
    PlayerInfoRequest,
    UnknownLag,
    ReportRequest,
    # Divers
    CharacterCharacteristicUpgradeRequest,
    BasicLatencyStatsRequest,
    ConsoleCommand,
]
