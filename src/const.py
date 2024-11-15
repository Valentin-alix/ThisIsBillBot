import datetime
import os
import socket
import sys
from pathlib import Path

from d3_mapping.resources.protos.game.dialog_pb2 import DialogLeaveRequest
from d3_mapping.resources.protos.game.fight_pb2 import FightTurnFinishRequest
from d3_mapping.resources.protos.game.gamemap_pb2 import MapMovementConfirmRequest

BACKEND_URL = "http://31.38.182.64:65472"

IS_IN_PYINSTALLER = hasattr(sys, "_MEIPASS")
DEBUG = True
DO_POPULATE = not IS_IN_PYINSTALLER and DEBUG
DO_INSERT_HUMAN_SESSION = False

FILTER_DOFUS = "tcp port 5555"
DOFUS_CONNECTION_URL = "dofus2-co-production.ankama-games.com"
CONNECTION_SERVERS_IPS: list[str] = socket.gethostbyname_ex(DOFUS_CONNECTION_URL)[2]

RESOURCE_FOLDER = os.path.join(Path(__file__).parent.parent, "resources")
MITM_CONFIG_URL = os.path.join(RESOURCE_FOLDER, "config.json")

HUMAN_SESSIONS_FILE = os.path.join(RESOURCE_FOLDER, "human_sessions.json")

MIN_DATE = datetime.datetime(datetime.MINYEAR, 1, 1)

FAKE_INFINITY_VALUE = 99999

MESSAGES_WITH_UID = [
    MapMovementConfirmRequest,
    DialogLeaveRequest,
    FightTurnFinishRequest,
]

RECORDING_FOLDER = os.path.join(Path(__file__).parent, "recordings")
