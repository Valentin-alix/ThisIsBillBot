import unittest

from src.gui.pages.debugs.sniffer import _parse_sub_msg_name


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
