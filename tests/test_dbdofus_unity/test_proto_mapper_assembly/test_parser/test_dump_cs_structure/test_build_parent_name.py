from DBDofusUnity.proto_mapper_assembly.parsers._dump_cs_structure import _Span, build_parent_name


class TestBuildParentName:
    def test_span_with_no_enclosing_parent_returns_none(self) -> None:
        child_span = _Span(start=0, end=100, name="Foo")
        cache: dict[int, str | None] = {}

        result = build_parent_name(child_span, [child_span], cache)

        assert result is None

    def test_deeply_nested_span_builds_dotted_chain(self) -> None:
        grandparent = _Span(start=0, end=300, name="GrandParent")
        parent = _Span(start=10, end=200, name="Parent")
        child = _Span(start=20, end=100, name="Child")
        all_spans = [grandparent, parent, child]
        cache: dict[int, str | None] = {}

        result = build_parent_name(child, all_spans, cache)

        assert result == "GrandParent.Parent"
