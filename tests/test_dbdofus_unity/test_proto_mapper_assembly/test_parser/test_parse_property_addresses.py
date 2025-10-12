import pytest

from DBDofusUnity.proto_mapper_assembly.parsers._message_body_scan import _parse_property_addresses


class TestParsePropertyAddresses:
    @pytest.mark.parametrize(
        ("comment", "expected_getter", "expected_setter"),
        [
            ("0x00000001807A3E30-0x00000001807A3E90", 0x00000001807A3E30, None),
            (
                "0x00000001807A3E30-0x00000001807A3E90 0x0000000180785910-0x0000000180785920",
                0x00000001807A3E30,
                0x0000000180785910,
            ),
            ("", None, None),
            ("some text without hex addresses", None, None),
        ],
    )
    def test_parses_getter_and_setter_addresses(
        self,
        comment: str,
        expected_getter: int | None,
        expected_setter: int | None,
    ) -> None:
        getter, setter = _parse_property_addresses(comment)
        assert getter == expected_getter
        assert setter == expected_setter
