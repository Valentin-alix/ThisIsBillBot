import pytest

from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage


class TestDumpCSMessage:
    @pytest.mark.parametrize(
        ("message", "expected"),
        [
            (
                DumpCSMessage(
                    file_descriptor="FD",
                    name="Inner",
                    parent_name="Outer.Types",
                    namespace="Game.Messages",
                ),
                "Outer.Types.Inner",
            ),
            (
                DumpCSMessage(file_descriptor="FD", name="Inner", namespace="Game.Messages"),
                "Game.Messages.Inner",
            ),
            (DumpCSMessage(file_descriptor="FD", name="Inner"), "Inner"),
        ],
    )
    def test_composed_name_uses_parent_namespace_or_name(self, message: DumpCSMessage, expected: str) -> None:
        assert message.composed_name == expected
