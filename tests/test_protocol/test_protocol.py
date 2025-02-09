import json
import os
import tempfile
import unittest
from pathlib import Path

from src.protocol import protocol_game
from src.protocol.protocol import decode_varint_size, encode_varint
from src.protocol.protocol_game import get_msg_transformer


class ProtocolVarintTests(unittest.TestCase):
    def test_encode_and_decode_varint_round_trip(self) -> None:
        encoded = encode_varint(300)

        decoded_value, next_position = decode_varint_size(encoded)

        self.assertEqual(decoded_value, 300)
        self.assertEqual(next_position, len(encoded))

    def test_encode_and_decode_zero_varint(self) -> None:
        encoded = encode_varint(0)

        decoded_value, next_position = decode_varint_size(encoded)

        self.assertEqual(encoded, b"\x00")
        self.assertEqual(decoded_value, 0)
        self.assertEqual(next_position, 1)

    def test_encode_varint_rejects_negative_values(self) -> None:
        with self.assertRaises(ValueError):
            encode_varint(-1)

    def test_decode_varint_size_rejects_incomplete_payloads(self) -> None:
        with self.assertRaises(ValueError):
            decode_varint_size(b"\x80")


class ProtocolGameTransformerTests(unittest.TestCase):
    def test_get_msg_transformer_returns_none_when_target_descriptor_is_missing(
        self,
    ) -> None:
        transformer = get_msg_transformer(
            "source.message",
            {"source.message": ("missing.message", {})},
        )

        self.assertIsNone(transformer)


class ProtocolGameMappingsTests(unittest.TestCase):
    def test_load_game_mappings_reloads_when_file_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            mappings_path = Path(temp_dir) / "game_mappings.json"
            original_path = protocol_game._GAME_MAPPINGS_PATH
            original_mappings = protocol_game._cached_game_mappings
            original_mtime_ns = protocol_game._cached_game_mappings_mtime_ns

            try:
                protocol_game._GAME_MAPPINGS_PATH = mappings_path
                protocol_game._cached_game_mappings = None
                protocol_game._cached_game_mappings_mtime_ns = None

                first_payload: protocol_game.RawGameMappings = {
                    "first.Message": {"field_mapping": {}}
                }
                second_payload: protocol_game.RawGameMappings = {
                    "second.Message": {"field_mapping": {}}
                }

                mappings_path.write_text(json.dumps(first_payload), encoding="utf-8")
                first_mtime_ns = mappings_path.stat().st_mtime_ns

                self.assertEqual(protocol_game._load_game_mappings(), first_payload)

                mappings_path.write_text(json.dumps(second_payload), encoding="utf-8")
                second_mtime_ns = first_mtime_ns + 1_000_000_000
                os.utime(mappings_path, ns=(second_mtime_ns, second_mtime_ns))

                self.assertEqual(protocol_game._load_game_mappings(), second_payload)
            finally:
                protocol_game._GAME_MAPPINGS_PATH = original_path
                protocol_game._cached_game_mappings = original_mappings
                protocol_game._cached_game_mappings_mtime_ns = original_mtime_ns
