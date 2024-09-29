import os
import socket
from pathlib import Path

FILTER_DOFUS = "tcp port 5555"
CONNECTION_SERVERS_IPS: list[str] = socket.gethostbyname_ex(
    "dofus2-co-beta.ankama-games.com"
)[2]
TYPE_URL_PREFIX = "type.ankama.com/"
RANGE_WAIT: tuple[float, float] = (0.1, 0.3)


PROTO_ROOT_PATH = os.path.join(Path(__file__).parent.parent, "com")
DESCRIPTOR_FOLDER = os.path.join(
    Path(__file__).parent.parent.parent, "resources", "descriptors"
)


DOFUS_FOLDER = os.path.join(os.environ["LOCALAPPDATA"], "Ankama", "Dofus-beta")
DOFUS_CONTENT_FOLDER = os.path.join(
    DOFUS_FOLDER, "Dofus_Data", "StreamingAssets", "Content"
)
DOFUS_DATA_PATH = os.path.join(DOFUS_CONTENT_FOLDER, "Data", "exported")
USEFUL_DATAS_JSON: dict[str, str] = {"Items": "ItemsRoot.json", "Jobs": "JobsRoot.json"}
OUTPUT_CLASS_DATAS = os.path.join(
    Path(__file__).parent.parent, "src", "interfaces", "dicts", "gen_datas"
)

DOFUS_MAP_PATH = os.path.join(DOFUS_CONTENT_FOLDER, "Map", "exported")
I18N_PATH = os.path.join(DOFUS_CONTENT_FOLDER, "I18n", "fr.bin")
