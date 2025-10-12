from DBDofusUnity.proto_mapper_assembly.parsers._dump_cs_structure import collect_file_descriptor_markers


class TestCollectFileDescriptorMarkers:
    def test_static_class_with_file_descriptor_is_detected(self) -> None:
        code = (
            "public static class GameReflection // TypeDefIndex: 1\n"
            "{\n"
            "    public static FileDescriptor Descriptor { get; }\n"
            "}\n"
        )

        markers = collect_file_descriptor_markers(code)

        assert len(markers) == 1
        assert markers[0].value == "GameReflection"
        assert markers[0].type_def_index == 1

    def test_non_static_class_with_file_descriptor_is_ignored(self) -> None:
        code = (
            "public sealed class ChatReflection : IMessage // TypeDefIndex: 2\n"
            "{\n"
            "    public static FileDescriptor Descriptor { get; }\n"
            "}\n"
        )

        markers = collect_file_descriptor_markers(code)

        assert markers == []

    def test_static_class_without_file_descriptor_is_ignored(self) -> None:
        code = "public static class EmptyStatic // TypeDefIndex: 3\n{\n    // nothing here\n}\n"

        markers = collect_file_descriptor_markers(code)

        assert markers == []

    def test_file_descriptor_in_nested_type_does_not_count(self) -> None:
        # FileDescriptor is in a nested class body, not in the direct body
        code = (
            "public static class OuterStatic // TypeDefIndex: 4\n"
            "{\n"
            "    public class Inner // TypeDefIndex: 5\n"
            "    {\n"
            "        public static FileDescriptor Descriptor { get; }\n"
            "    }\n"
            "}\n"
        )

        markers = collect_file_descriptor_markers(code)

        assert markers == []

    def test_multiple_markers_are_sorted_by_type_def_index(self) -> None:
        code = (
            "public static class BReflection // TypeDefIndex: 10\n"
            "{\n"
            "    public static FileDescriptor Descriptor { get; }\n"
            "}\n"
            "public static class AReflection // TypeDefIndex: 5\n"
            "{\n"
            "    public static FileDescriptor Descriptor { get; }\n"
            "}\n"
        )

        markers = collect_file_descriptor_markers(code)

        assert len(markers) == 2
        assert markers[0].value == "AReflection"
        assert markers[1].value == "BReflection"
