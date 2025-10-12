from DBDofusUnity.proto_mapper_assembly.parsers._dump_cs_structure import collect_namespace_spans


class TestCollectNamespaceSpans:
    def test_namespace_without_brace_is_ignored(self) -> None:
        code = "namespace NoBrace.Here\n// no brace follows\n"

        spans = collect_namespace_spans(code)

        assert spans == []

    def test_valid_namespace_is_collected(self) -> None:
        code = "namespace Game.Messages\n{\n    // content\n}\n"

        spans = collect_namespace_spans(code)

        assert len(spans) == 1
        assert spans[0].name == "Game.Messages"
