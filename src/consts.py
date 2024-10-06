import datetime
import os
import socket
from pathlib import Path

FILTER_DOFUS = "tcp port 5555"
CONNECTION_SERVERS_IPS: list[str] = socket.gethostbyname_ex(
    "dofus2-co-beta.ankama-games.com"
)[2]
TYPE_URL_PREFIX = "type.ankama.com/"

RESOURCE_FOLDER = os.path.join(Path(__file__).parent.parent, "resources")


MIN_DATE: datetime = datetime.datetime(datetime.MINYEAR, 1, 1)

# Waiting times timing
VERY_SMALL_RANGE = (0.1, 0.5)
SMALL_RANGE = (0.3, 0.7)
BASE_RANGE = (0.5, 1.5)
ON_NEW_MAP_BEFORE_ACTION = (0.5, 4.5)
