from collections.abc import Callable
from pathlib import Path

from DBDofusUnity.proto_mapper_assembly.parsers.dump_cs_parser import parse_types

CODE = (
    "public class fal // TypeDefIndex: 1\n"
    "{\n"
    "    private struct _DelayPlacementDisplay_d__10 : IAsyncStateMachine"
    " // TypeDefIndex: 2\n"
    "    {\n"
    "        public fal __4__this; // 0x10\n"
    "        public jcm message; // 0x18\n"
    "    }\n"
    "}\n"
    "\n"
    "public class Child : fal, IDisposable // TypeDefIndex: 4\n"
    "{\n"
    "}\n"
    "\n"
    "public sealed class jcm : IMessage<jcm>, IBufferMessage // TypeDefIndex: 3\n"
    "{\n"
    "    private int value_; // 0x18\n"
    "}\n"
)


class TestParseTypes:
    def test_private_state_machine_keeps_message_field(self, dump_cs: Callable[[str], Path]) -> None:
        path = str(dump_cs(CODE))
        parsed_types = parse_types(path)

        state_machine = next(
            current_type
            for current_type in parsed_types
            if current_type.composed_name == "fal._DelayPlacementDisplay_d__10"
        )
        message_field = next(
            (field for field in state_machine.fields if field.field_name == "message"),
            None,
        )

        assert message_field is not None
        assert message_field.normalized_type == "jcm"
        assert message_field.memory_offset == 0x18

    def test_type_base_class_name_is_parsed_from_first_base_clause_entry(
        self, dump_cs: Callable[[str], Path]
    ) -> None:
        path = str(dump_cs(CODE))
        parsed_types = parse_types(path)

        child = next(current_type for current_type in parsed_types if current_type.composed_name == "Child")

        assert child.base_class_name == "fal"
