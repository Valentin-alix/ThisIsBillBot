import datas.protos.non_obf.game  # noqa: F401  (sys.path bootstrap)

from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.i18n import I18N

reader = DataReader()
TARGETS = {15923: "astrub bank", 63535: "bonta bank", 36982: "incarnam hesitate", 36980: "incarnam confirm"}
owners: dict[int, list[str]] = {reply_id: [] for reply_id in TARGETS}
for npc in reader.npc_by_id.values():
    for dialog_reply in npc.dialogReplies:
        reply_id = dialog_reply.values[0]
        if reply_id in owners:
            owners[reply_id].append(f"{npc.id} {I18N().name_by_id.get(npc.nameId)!r}")
for reply_id, label in TARGETS.items():
    print(f"{label} (reply {reply_id}): {owners[reply_id]}")
