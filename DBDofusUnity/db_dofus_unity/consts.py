import os
from pathlib import Path

from D3Database.consts import DOFUS_PATH


UABEA_PATH_EXE = os.path.join(
    Path(__file__).parent.parent,
    "UABEA",
    "UABEAvalonia",
    "bin",
    "Debug",
    "net6.0",
    "UABEAvalonia.exe",
)

PATH_STANDALONE_BUNDLES = os.path.join(
    DOFUS_PATH, "Dofus_Data", "StreamingAssets", "aa", "StandaloneWindows64"
)
PATH_MAPS = os.path.join(
    DOFUS_PATH, "Dofus_Data", "StreamingAssets", "Content", "Map", "Data"
)
PATH_DATAS = os.path.join(
    DOFUS_PATH, "Dofus_Data", "StreamingAssets", "Content", "Data"
)
