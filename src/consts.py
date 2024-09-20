import os
import socket
from pathlib import Path

FILTER_DOFUS = "tcp port 5555"

PROTO_ROOT_PATH = os.path.join(Path(__file__).parent.parent, "com")

CONNECTION_SERVERS_IPS: list[str] = socket.gethostbyname_ex(
    "dofus2-co-beta.ankama-games.com"
)[2]
