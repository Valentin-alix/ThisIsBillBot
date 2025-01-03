"""
Constantes système et infrastructure du bot.
Configuration de l'environnement d'exécution, chemins, connexions réseau.

⚠️ Ces valeurs concernent le système d'exécution, pas le jeu Dofus.
Pour les constantes du jeu, voir src/core/game_constants.py
Pour la configuration du bot, voir src/core/config.py
"""

import datetime
import os
import socket
from pathlib import Path

from dotenv import load_dotenv
from datas.protos.non_obf.game.dialog_pb2 import DialogLeaveRequest
from datas.protos.non_obf.game.fight_pb2 import (
    FightTurnFinishRequest,
)
from datas.protos.non_obf.game.gamemap_pb2 import (
    MapMovementConfirmRequest,
)
from google.protobuf.message import Message

ENV_PATH = os.path.join(Path(__file__).parent.parent, ".env")
load_dotenv(ENV_PATH)

_TRUE_ENV_VALUES = {"1", "true", "yes", "on", "debug"}
_FALSE_ENV_VALUES = {"0", "false", "no", "off", "release"}


def _read_bool_env(name: str, default: bool) -> bool:
    raw_value = os.environ.get(name)
    if raw_value is None:
        return default
    normalized = raw_value.strip().lower()
    if normalized in _TRUE_ENV_VALUES:
        return True
    if normalized in _FALSE_ENV_VALUES:
        return False
    error = f"Unsupported boolean env value for {name}: {raw_value!r}"
    raise ValueError(error)


# ============================================================================
# SYSTÈME
# ============================================================================

DEBUG = _read_bool_env("DEBUG", True)
STRICT_MODE = _read_bool_env("STRICT_MODE", False)
DO_INSERT_HUMAN_SESSION = False

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
HUMAN_SESSIONS_FILE = os.path.join(RESOURCE_FOLDER, "human_sessions.json")
LOG_FOLDER: str = os.path.join(RESOURCE_FOLDER, "logs")

# ============================================================================
# UTILITAIRES
# ============================================================================

MIN_DATE = datetime.datetime(datetime.MINYEAR, 1, 1)
FAKE_INFINITY_VALUE = 99999

# ============================================================================
# MESSAGES PROTOBUF
# ============================================================================

MESSAGES_WITH_UID: list[type[Message]] = [
    MapMovementConfirmRequest,
    DialogLeaveRequest,
    FightTurnFinishRequest,
]
