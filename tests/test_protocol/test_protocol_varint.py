import pytest

from src.protocol.protocol import decode_varint_size, encode_varint


class TestProtocolVarint:
    def test_encode_and_decode_varint_round_trip(self) -> None:
        encoded = encode_varint(300)

        decoded_value, next_position = decode_varint_size(encoded)

        assert decoded_value == 300
        assert next_position == len(encoded)

    def test_encode_and_decode_zero_varint(self) -> None:
        encoded = encode_varint(0)

        decoded_value, next_position = decode_varint_size(encoded)

        assert encoded == b"\x00"
        assert decoded_value == 0
        assert next_position == 1

    def test_encode_varint_rejects_negative_values(self) -> None:
        with pytest.raises(ValueError):
            encode_varint(-1)

    def test_decode_varint_size_rejects_incomplete_payloads(self) -> None:
        with pytest.raises(ValueError):
            decode_varint_size(b"\x80")
