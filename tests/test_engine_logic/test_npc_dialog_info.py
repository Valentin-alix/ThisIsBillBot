import unittest

from src.core.engine.npcs.npc_dialog_info import NpcDialogInfo, ReplyInfo
from src.core.engine.npcs.npc_info import NpcInfo


class TestNpcDialogInfo(unittest.TestCase):
    def test_npc_dialog_info_defaults_create_independent_collections(self) -> None:
        first = NpcDialogInfo()
        second = NpcDialogInfo()

        first.reply_info_by_message_id[1] = ReplyInfo(reply_id=42)
        first.forbidden_action_ids.append(7)

        self.assertEqual(first.reply_info_by_message_id[1].reply_id, 42)
        self.assertEqual(first.forbidden_action_ids, [7])
        self.assertEqual(second.reply_info_by_message_id, {})
        self.assertEqual(second.forbidden_action_ids, [])

    def test_npc_info_keeps_npc_map_id_and_dialog_data(self) -> None:
        npc = NpcInfo(
            npc_map_id=123,
            npc_id=7,
            reply_info_by_message_id={8: ReplyInfo(reply_id=9)},
            forbidden_action_ids=[10],
        )

        self.assertEqual(npc.npc_map_id, 123)
        self.assertEqual(npc.npc_id, 7)
        self.assertEqual(npc.reply_info_by_message_id[8].reply_id, 9)
        self.assertEqual(npc.forbidden_action_ids, [10])
