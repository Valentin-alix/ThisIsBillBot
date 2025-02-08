import unittest

from src.protocol.message_names import load_non_obf_game_message_names


class TestMessageNames(unittest.TestCase):
    def test_load_non_obf_game_message_names_has_known_unique_names(self) -> None:
        names = load_non_obf_game_message_names()

        self.assertIn("InventoryContentEvent", names)
        self.assertEqual(len(names), len(set(names)))
