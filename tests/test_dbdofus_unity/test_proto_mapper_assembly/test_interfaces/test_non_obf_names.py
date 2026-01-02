from tests.fixtures.proto_mapper.field_builders import number_field

from DBDofusUnity.proto_mapper_assembly.helpers.non_obf_names import (
    build_filtered_message_namespace,
    build_pinned_non_obf_name,
    normalize_exported_non_obf_namespace,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage


class TestNonObfNames:
    def test_build_pinned_non_obf_name_flattens_container_only_types_segments(self) -> None:
        namespace = "Com.Ankama.Dofus.Server.Game.Protocol.Game.Action"
        outer = DumpCSMessage(
            file_descriptor="GameReflection",
            name="GameActionFightEvent",
            namespace=namespace,
            fields=[number_field()],
        )
        types = DumpCSMessage(
            file_descriptor="GameReflection",
            name="Types",
            namespace=namespace,
            parent_name="GameActionFightEvent",
        )
        child = DumpCSMessage(
            file_descriptor="GameReflection",
            name="LifePointsLost",
            namespace=namespace,
            parent_name="GameActionFightEvent.Types",
            fields=[number_field("loss_")],
        )
        messages_by_cls = {
            outer.composed_name: outer,
            types.composed_name: types,
            child.composed_name: child,
        }

        assert (
            build_filtered_message_namespace(
                is_obf=False,
                message=child,
                messages_by_cls=messages_by_cls,
            )
            == ".com.ankama.dofus.server.game.protocol.game.action.GameActionFightEvent.LifePointsLost"
        )
        assert (
            build_pinned_non_obf_name(message=child, messages_by_cls=messages_by_cls)
            == "Com.Ankama.Dofus.Server.Game.Protocol.Game.Action.GameActionFightEvent.LifePointsLost"
        )

    def test_normalize_exported_non_obf_namespace_restores_authoring_case(self) -> None:
        assert (
            normalize_exported_non_obf_namespace(
                ".com.ankama.dofus.server.game.protocol.game.action.GameActionFightEvent.LifePointsLost"
            )
            == "Com.Ankama.Dofus.Server.Game.Protocol.Game.Action.GameActionFightEvent.LifePointsLost"
        )
