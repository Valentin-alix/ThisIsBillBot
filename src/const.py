import datetime
import os
import socket
from pathlib import Path

from d3_mapping.resources.protos.game.arena_pb2 import ArenaSwitchXpRewardsModeRequest
from d3_mapping.resources.protos.game.basic_pb2 import SequenceNumberRequest
from d3_mapping.resources.protos.game.client_verification_pb2 import ClientIdRequest
from d3_mapping.resources.protos.game.connection_pb2 import PingRequest

DEBUG = True
DO_POPULATE = False

FILTER_DOFUS = "tcp port 5555"
DOFUS_CONNECTION_URL = "dofus2-co-production.ankama-games.com"
CONNECTION_SERVERS_IPS: list[str] = socket.gethostbyname_ex(DOFUS_CONNECTION_URL)[2]
TYPE_URL_PREFIX = "type.ankama.com/"

RESOURCE_FOLDER = os.path.join(Path(__file__).parent.parent, "resources")
MITM_CONFIG_URL = os.path.join(RESOURCE_FOLDER, "config.json")

HUMAN_SESSIONS_FILE = os.path.join(RESOURCE_FOLDER, "human_sessions.json")

MIN_DATE = datetime.datetime(datetime.MINYEAR, 1, 1)

FAKE_INFINITY_VALUE = 99999

MESSAGES_WITH_UID = [
    ClientIdRequest,
    SequenceNumberRequest,
    ArenaSwitchXpRewardsModeRequest,
    PingRequest,
]
