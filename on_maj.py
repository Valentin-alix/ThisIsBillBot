from D3Mapping.d3_mapping.main import update_proto_on_new_version
from DBDofusUnity.db_dofus_unity.get_datas import update_all_datas

if __name__ == "__main__":
    update_all_datas()
    print("Updating protos")
    update_proto_on_new_version()
    print("Please play sniffer with sacri eau and redo mapping.")
