import unittest

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
