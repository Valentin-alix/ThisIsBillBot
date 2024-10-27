import os
from pathlib import Path
import sys


sys.path.append(os.path.join(Path(__file__).parent))
sys.path.append(os.path.join(Path(__file__).parent, "D3Mapping"))
sys.path.append(os.path.join(Path(__file__).parent, "DBDofusUnity"))
sys.path.append(os.path.join(Path(__file__).parent, "D3Database"))

from d3_mapping.main import update_proto_on_new_version
from db_dofus_unity.get_datas import update_all_datas

if __name__ == "__main__":
    update_all_datas()
    print("Updating protos")
    update_proto_on_new_version()
    print("Please play sniffer with sacri eau and redo mapping.")
