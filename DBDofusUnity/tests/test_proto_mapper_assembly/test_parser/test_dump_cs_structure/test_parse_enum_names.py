from proto_mapper_assembly.parsers._dump_cs_structure import parse_enum_names


class TestParseEnumNames:
    def test_enum_names_are_extracted(self) -> None:
        code = "public enum Direction { North, South }\npublic enum Color { Red, Blue }\n"

        names = parse_enum_names(code)

        assert names == {"Direction", "Color"}

    def test_empty_code_returns_empty_set(self) -> None:
        names = parse_enum_names("")

        assert names == frozenset()
