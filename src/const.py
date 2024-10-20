import datetime
import os
import socket
from pathlib import Path

DEBUG = True

FILTER_DOFUS = "tcp port 5555"
DOFUS_CONNECTION_URL = "dofus2-co-production.ankama-games.com"
CONNECTION_SERVERS_IPS: list[str] = socket.gethostbyname_ex(DOFUS_CONNECTION_URL)[2]
TYPE_URL_PREFIX = "type.ankama.com/"

RESOURCE_FOLDER = os.path.join(Path(__file__).parent.parent, "resources")
MITM_CONFIG_URL = os.path.join(RESOURCE_FOLDER, "config.json")

HUMAN_SESSIONS_FOLDER = os.path.join(RESOURCE_FOLDER, "sessions")

MIN_DATE = datetime.datetime(datetime.MINYEAR, 1, 1)

FAKE_INFINITY_VALUE = 99999
