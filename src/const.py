import datetime
import os
import socket
from pathlib import Path

FILTER_DOFUS = "tcp port 5555"
DOFUS_CONNECTION_URL = "dofus2-co-production.ankama-games.com"
CONNECTION_SERVERS_IPS: list[str] = socket.gethostbyname_ex(DOFUS_CONNECTION_URL)[2]
TYPE_URL_PREFIX = "type.ankama.com/"

RESOURCE_FOLDER = os.path.join(Path(__file__).parent.parent, "resources")


MIN_DATE: datetime = datetime.datetime(datetime.MINYEAR, 1, 1)

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
