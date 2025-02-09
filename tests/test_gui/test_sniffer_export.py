import datetime
import unittest

from src.gui.pages.debugs.sniffer import (
    _extract_obf_msg_name_for_pinned_pair,
    _extract_pinned_pair_names_for_fields,
    _parse_sub_msg_name,
    _resolve_pinned_field_message_pair,
)
from src.gui.pages.debugs.message_detail import SelectedPinnedField
from src.protocol.message import MessageInfo


class TestParseSubMsgName(unittest.TestCase):
    def test_game_msg_decoded(self) -> None:
        obf, decoded = _parse_sub_msg_name("com.ankama.dofus.Obf -> DecodedName")
        self.assertEqual(obf, "com.ankama.dofus.Obf")
        self.assertEqual(decoded, "DecodedName")

    def test_game_msg_not_decoded(self) -> None:
        obf, decoded = _parse_sub_msg_name("com.ankama.dofus.Obf -> ObfClass")
        self.assertEqual(obf, "com.ankama.dofus.Obf")
        self.assertEqual(decoded, "ObfClass")

    def test_connection_msg(self) -> None:
        obf, decoded = _parse_sub_msg_name("LoginQuestion")
        self.assertIsNone(obf)
        self.assertEqual(decoded, "LoginQuestion")

    def test_multiple_arrows(self) -> None:
        obf, decoded = _parse_sub_msg_name("a -> b -> c")
        self.assertEqual(obf, "a")
        self.assertEqual(decoded, "b -> c")


class TestPinnedPairHelpers(unittest.TestCase):
    def test_extract_obf_msg_name_from_decoded_game_message(self) -> None:
        msg_info = MessageInfo(
            received_time=datetime.datetime.now(),
            from_server=True,
            sub_msg_name="abc -> InventoryContentEvent",
            obf_msg_json={},
        )

        self.assertEqual(_extract_obf_msg_name_for_pinned_pair(msg_info), "abc")

    def test_extract_obf_msg_name_from_unmapped_game_message(self) -> None:
        msg_info = MessageInfo(
            received_time=datetime.datetime.now(),
            from_server=True,
            sub_msg_name="abc",
            obf_msg_json={},
        )

        self.assertEqual(_extract_obf_msg_name_for_pinned_pair(msg_info), "abc")

    def test_extract_obf_msg_name_ignores_non_obf_only_message(self) -> None:
        msg_info = MessageInfo(
            received_time=datetime.datetime.now(),
            from_server=True,
            sub_msg_name="LoginQuestion",
            msg_json={},
        )

        self.assertIsNone(_extract_obf_msg_name_for_pinned_pair(msg_info))

    def test_extract_pinned_pair_names_for_fields_from_mapped_game_message(
        self,
    ) -> None:
        msg_info = MessageInfo(
            received_time=datetime.datetime.now(),
            from_server=True,
            sub_msg_name="abc -> InventoryContentEvent",
            msg_json={},
            obf_msg_json={},
        )

        self.assertEqual(
            _extract_pinned_pair_names_for_fields(msg_info),
            ("abc", "InventoryContentEvent"),
        )

    def test_extract_pinned_pair_names_for_fields_requires_clear_content(
        self,
    ) -> None:
        msg_info = MessageInfo(
            received_time=datetime.datetime.now(),
            from_server=True,
            sub_msg_name="abc -> InventoryContentEvent",
            obf_msg_json={},
        )

        self.assertIsNone(_extract_pinned_pair_names_for_fields(msg_info))

    def test_resolve_pinned_field_message_pair_uses_root_pair_for_root_fields(
        self,
    ) -> None:
        self.assertEqual(
            _resolve_pinned_field_message_pair(
                ("obf.Msg", "ClearMsg"),
                SelectedPinnedField(None, "a", ("a",)),
                SelectedPinnedField(None, "field_a", ("field_a",)),
            ),
            ("obf.Msg", "ClearMsg"),
        )
