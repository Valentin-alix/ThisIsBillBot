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
import sys
from pathlib import Path

from d3_database.protos.non_obf.game.dialog_pb2 import DialogLeaveRequest
from d3_database.protos.non_obf.game.fight_pb2 import (
    FightTurnFinishRequest,
)
from d3_database.protos.non_obf.game.gamemap_pb2 import (
    MapMovementConfirmRequest,
)

ENV_PATH = os.path.join(Path(__file__).parent.parent, ".env")

# ============================================================================
# SYSTÈME
# ============================================================================

IS_IN_PYINSTALLER = hasattr(sys, "_MEIPASS")
DEBUG = bool(int(os.environ.get("DEBUG", 1)))
STRICT_MODE = bool(int(os.environ.get("STRICT_MODE", 0)))
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

MESSAGES_WITH_UID = [
    MapMovementConfirmRequest,
    DialogLeaveRequest,
    FightTurnFinishRequest,
]
