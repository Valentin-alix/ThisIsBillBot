from proto_mapper_assembly.parsers._dump_cs_structure import parse_enum_member_values


class TestParseEnumMemberValues:
    def test_simple_enum(self) -> None:
        code = "public enum Channel\n{\n    Global = 0,\n    Team = 1,\n    Sales = 5\n}\n"
        result = parse_enum_member_values(code)
        assert result == {"Channel": {"Global": 0, "Team": 1, "Sales": 5}}

    def test_negative_value(self) -> None:
        code = "public enum Status\n{\n    Unknown = -1,\n    Active = 0\n}\n"
        result = parse_enum_member_values(code)
        assert result == {"Status": {"Unknown": -1, "Active": 0}}

    def test_multiple_enums(self) -> None:
        code = "public enum A\n{ X = 0, Y = 1 }\npublic enum B\n{ P = 10, Q = 20 }\n"
        result = parse_enum_member_values(code)
        assert "A" in result
        assert "B" in result
        assert result["A"] == {"X": 0, "Y": 1}
        assert result["B"] == {"P": 10, "Q": 20}

    def test_enum_without_values_excluded(self) -> None:
        code = "public enum Empty\n{\n}\n"
        result = parse_enum_member_values(code)
        assert "Empty" not in result

    def test_no_enums_returns_empty(self) -> None:
        code = "public class Foo {}\n"
        result = parse_enum_member_values(code)
        assert result == {}

    def test_non_public_enum_excluded(self) -> None:
        code = "private enum Hidden\n{ A = 0 }\npublic enum Visible\n{ B = 1 }\n"
        result = parse_enum_member_values(code)
        assert "Hidden" not in result
        assert "Visible" in result
