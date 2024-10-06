import os
import socket
from pathlib import Path

FILTER_DOFUS = "tcp port 5555"
CONNECTION_SERVERS_IPS: list[str] = socket.gethostbyname_ex(
    "dofus2-co-beta.ankama-games.com"
)[2]
TYPE_URL_PREFIX = "type.ankama.com/"

RESOURCE_FOLDER = os.path.join(Path(__file__).parent.parent, "resources")
