from DBDofusUnity.proto_mapper_assembly.parsers._dump_cs_structure import get_stripped_direct_body


class TestGetStrippedDirectBody:
    def test_strips_nested_class_body_but_keeps_declaration(self) -> None:
        code = (
            "public class Outer // TypeDefIndex: 1\n"
            "{\n"
            "    public class Inner // TypeDefIndex: 2\n"
            "    {\n"
            "        private int secret;\n"
            "    }\n"
            "    private string name;\n"
            "}\n"
        )

        body = get_stripped_direct_body(0, code)

        assert "Inner" in body
        assert "secret" not in body
        assert "name" in body

    def test_returns_empty_string_when_no_opening_brace(self) -> None:
        code = "public class NoBrace // TypeDefIndex: 1"

        body = get_stripped_direct_body(0, code)

        assert body == ""

    def test_returns_empty_string_when_brace_unclosed(self) -> None:
        code = "public class Unclosed // TypeDefIndex: 1\n{ unclosed body"

        body = get_stripped_direct_body(0, code)

        assert body == ""

    def test_strips_nested_struct_body(self) -> None:
        code = (
            "public class Outer // TypeDefIndex: 1\n"
            "{\n"
            "    public struct Point // TypeDefIndex: 2\n"
            "    {\n"
            "        public int x;\n"
            "    }\n"
            "    public int value;\n"
            "}\n"
        )

        body = get_stripped_direct_body(0, code)

        assert "Point" in body
        assert "int x" not in body
        assert "value" in body
