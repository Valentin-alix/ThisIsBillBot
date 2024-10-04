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
DOFUS_FOLDER = os.path.join(os.environ["LOCALAPPDATA"], "Ankama", "Dofus-beta")
DESCRIPTOR_FOLDER = os.path.join(DOFUS_FOLDER, "output")

DOFUS_ASSETS_FOLDER = os.path.join(DOFUS_FOLDER, "Dofus_Data", "StreamingAssets")
DOFUS_CONTENT_FOLDER = os.path.join(DOFUS_ASSETS_FOLDER, "Content")

DOFUS_DATA_PATH = os.path.join(DOFUS_CONTENT_FOLDER, "Data", "exported")
DOFUS_MAP_PATH = os.path.join(DOFUS_CONTENT_FOLDER, "Map", "exported")
DOFUS_STANDALONE_PATH = os.path.join(
    DOFUS_ASSETS_FOLDER, "aa", "StandaloneWindows64", "exported"
)
I18N_PATH = os.path.join(DOFUS_CONTENT_FOLDER, "I18n", "fr.bin")
WORLD_GRAPH_FILENAME = "worldgraph.json"


OUTPUT_CLASS_GEN = os.path.join(Path(__file__).parent.parent, "resources", "gen")
OUTPUT_CLASS_DATAS = os.path.join(OUTPUT_CLASS_GEN, "gen_datas")
OUTPUT_CLASS_MAPS = os.path.join(OUTPUT_CLASS_GEN, "gen_maps")
OUTPUT_CLASS_STANDALONE = os.path.join(OUTPUT_CLASS_GEN, "gen_standalone")
