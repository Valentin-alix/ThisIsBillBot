from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.data_center.i18n import I18N


def format_item_name(gid: int) -> str:
    item = DataReader().item_by_id[gid]
    return I18N().name_by_id[item.nameId]
