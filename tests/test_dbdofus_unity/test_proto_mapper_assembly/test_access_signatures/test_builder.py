import pytest
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.field_builders import dump_cs_field
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.shapes import (
    ANY_MESSAGE_SHAPE,
    ENUM_SHAPE,
    MAP_STRING_ANY_SHAPE,
    MESSAGE_SHAPE,
    NUMBER_SHAPE,
    REPEATED_ANY_SHAPE,
    STRING_SHAPE,
)
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.signatures import (
    build_access_signatures_for_test,
    build_field_resolution_lookup,
    build_file_descriptor_lookup,
    build_proto_accesses,
    builder_field_access_entry,
    builder_handler_registration_access_entry,
    builder_typeinfo_access_entry,
    enum_signature_entry,
    function_access_info,
)

from DBDofusUnity.proto_mapper_assembly.controllers.access_signatures import build_message_access_signatures_by_cls
from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import ReturnRole
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, FieldKey
from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import FieldTypeShape


class TestBuildMessageAccessSignatures:
    def test_creates_one_projection_per_accessed_class(self) -> None:
        function = function_access_info(
            name="Mapper::Void Join(MessageA, MessageB)",
            parameters=("MessageA", "MessageB"),
            size=256,
            access_infos=(
                builder_field_access_entry(cls="Com.Game.MessageA", field_offset=24),
                builder_field_access_entry(cls="Com.Game.MessageB", field_offset=32),
            ),
        )

        signatures = build_access_signatures_for_test(
            function,
            message_classes=("Com.Game.MessageA", "Com.Game.MessageB"),
        )

        assert set(signatures) == {"Com.Game.MessageA", "Com.Game.MessageB"}
        assert signatures["Com.Game.MessageA"].function_signatures[0].foreign_access_summary == ["field:read"]
        assert signatures["Com.Game.MessageB"].function_signatures[0].foreign_access_summary == ["field:read"]

    def test_normalizes_parameter_and_return_roles(self) -> None:
        function = function_access_info(
            name="Factory::RankInformation Build(Alteration)",
            parameters=("Alteration",),
            return_type="RankInformation",
            size=200,
            access_infos=(
                builder_field_access_entry(cls="Com.Ankama.Dofus.Server.Game.Protocol.Alteration.Alteration"),
                builder_field_access_entry(
                    cls="Com.Ankama.Dofus.Server.Game.Protocol.Common.RankInformation",
                    property_name=None,
                ),
            ),
        )

        signatures = build_access_signatures_for_test(
            function,
            message_classes=(
                "Com.Ankama.Dofus.Server.Game.Protocol.Alteration.Alteration",
                "Com.Ankama.Dofus.Server.Game.Protocol.Common.RankInformation",
            ),
        )

        assert (
            signatures["Com.Ankama.Dofus.Server.Game.Protocol.Alteration.Alteration"]
            .function_signatures[0]
            .takes_message_parameter
            is True
        )
        assert (
            signatures["Com.Ankama.Dofus.Server.Game.Protocol.Common.RankInformation"]
            .function_signatures[0]
            .return_role
            == ReturnRole.SELF
        )

    def test_aggregates_same_offset_field_accesses(self) -> None:
        first = function_access_info(
            name="Mapper::Void First(Message)",
            access_infos=(builder_field_access_entry(cls="Message", field="raw_a"),),
        )
        second = function_access_info(
            name="Mapper::Void Second(Message)",
            access_infos=(builder_field_access_entry(cls="Message", field="raw_b"),),
        )

        signature = build_access_signatures_for_test(first, second, message_classes=("Message",))["Message"]

        assert len(signature.field_signatures) == 1
        assert signature.field_signatures[0].field_offset == 24
        assert len(signature.field_signatures[0].accesses) == 2
        assert (
            signature.field_signatures[0].accesses[0].model_dump()
            == signature.field_signatures[0].accesses[1].model_dump()
        )

    def test_typeinfo_access_enriches_function_without_field_signature(self) -> None:
        function = function_access_info(
            name="Mapper::Message Build(Message)",
            return_type="Message",
            access_infos=(builder_typeinfo_access_entry(cls="Message"),),
        )

        signature = build_access_signatures_for_test(function, message_classes=("Message",))["Message"]

        assert signature.field_signatures == []
        assert len(signature.function_signatures) == 1
        assert signature.function_signatures[0].self_accesses[0].field_offset is None
        assert signature.function_signatures[0].self_accesses[0].entry_type == "typeinfo"

    def test_handler_registration_does_not_create_matching_signature(self) -> None:
        function = function_access_info(
            name="Mapper::Void Enable()",
            parameters=(),
            access_infos=(builder_handler_registration_access_entry(cls="Message"),),
        )

        signature = build_access_signatures_for_test(function, message_classes=("Message",))["Message"]

        assert signature.function_signatures == []
        assert signature.field_signatures == []

    def test_property_name_only_matters_by_presence(self) -> None:
        with_alpha = function_access_info(
            name="Mapper::Void Alpha(Message)",
            access_infos=(
                builder_field_access_entry(cls="Message", access_kind="getter", property_name="Alpha"),
            ),
        )
        with_beta = function_access_info(
            name="Mapper::Void Beta(Message)",
            access_infos=(
                builder_field_access_entry(cls="Message", access_kind="getter", property_name="Beta"),
            ),
        )
        without_property = function_access_info(
            name="Mapper::Void Raw(Message)",
            access_infos=(builder_field_access_entry(cls="Message", property_name=None),),
        )

        signature = build_access_signatures_for_test(
            with_alpha,
            with_beta,
            without_property,
            message_classes=("Message",),
        )["Message"]

        with_property_name = [
            current
            for current in signature.function_signatures
            if current.self_accesses[0].access_kind == "getter"
        ]
        without_property_name = [
            current
            for current in signature.function_signatures
            if current.self_accesses[0].access_kind != "getter"
        ]

        assert len(with_property_name) == 2
        assert len(without_property_name) == 1
        assert with_property_name[0].model_dump() == with_property_name[1].model_dump()
        assert without_property_name[0].model_dump() != with_property_name[0].model_dump()

    def test_uses_dump_message_file_descriptor(self) -> None:
        message = DumpCSMessage(file_descriptor="GamemapReflection", name="Message")
        function = function_access_info(access_infos=(builder_field_access_entry(cls="Message"),))

        signature = build_access_signatures_for_test(function, messages=(message,))["Message"]

        assert signature.file_descriptor == "GamemapReflection"

    def test_supports_nested_message_lookup_keys(self) -> None:
        message = DumpCSMessage(file_descriptor="NestedReflection", name="Inner", parent_name="Outer.Types")
        function = function_access_info(
            name="Mapper::Void Run(Outer.Types.Inner)",
            parameters=("Inner",),
            access_infos=(builder_field_access_entry(cls="Outer.Types.Inner"),),
        )

        signature = build_access_signatures_for_test(function, messages=(message,))["Outer.Types.Inner"]

        assert signature.file_descriptor == "NestedReflection"

    def test_raises_when_runtime_message_class_is_missing_from_dump_cs_lookup(self) -> None:
        function = function_access_info(access_infos=(builder_field_access_entry(cls="Com.Game.Message"),))

        with pytest.raises(KeyError, match=r"Com.Game.Message"):
            build_message_access_signatures_by_cls(build_proto_accesses(function), {}, {}, {})

    def test_raises_when_runtime_message_class_is_missing_from_field_resolution_lookup(self) -> None:
        function = function_access_info(access_infos=(builder_field_access_entry(cls="Com.Game.Message"),))

        with pytest.raises(KeyError, match=r"Com.Game.Message"):
            build_message_access_signatures_by_cls(
                build_proto_accesses(function),
                build_file_descriptor_lookup("Com.Game.Message"),
                {},
                {},
            )

    @pytest.mark.parametrize(
        ("message_name", "field_name", "clr_type", "expected_shape"),
        [
            ("Message", "count_", "int", NUMBER_SHAPE),
            ("LongMessage", "value_", "long", NUMBER_SHAPE),
            (
                "InventoryMessage",
                "event_",
                "Com.Ankama.Dofus.Server.Game.Protocol.Inventory.InventoryEvent",
                MESSAGE_SHAPE,
            ),
            ("AnyMessage", "payload_", "Google.Protobuf.WellKnownTypes.Any", ANY_MESSAGE_SHAPE),
            ("ShortAnyMessage", "payload_", "Any", ANY_MESSAGE_SHAPE),
            (
                "RepeatedAnyMessage",
                "payloads_",
                "RepeatedField<Google.Protobuf.WellKnownTypes.Any>",
                REPEATED_ANY_SHAPE,
            ),
            (
                "MapAnyMessage",
                "payloads_by_id_",
                "MapField<string, Google.Protobuf.WellKnownTypes.Any>",
                MAP_STRING_ANY_SHAPE,
            ),
        ],
    )
    def test_resolves_accessed_field_type_shape(
        self,
        message_name: str,
        field_name: str,
        clr_type: str,
        expected_shape: FieldTypeShape,
    ) -> None:
        message = DumpCSMessage(
            file_descriptor="FD",
            name=message_name,
            fields=[dump_cs_field(clr_type, offset=0x18, field_name=field_name)],
        )
        function = function_access_info(
            name=f"Mapper::Void Run({message_name})",
            parameters=(message_name,),
            access_infos=(
                builder_field_access_entry(
                    cls=message_name,
                    field=field_name,
                    property_name=None,
                    field_offset=0x18,
                ),
            ),
        )

        signature = build_access_signatures_for_test(function, messages=(message,))[message_name]

        assert signature.function_signatures[0].self_accesses[0].field_type_shape == expected_shape
        assert signature.field_signatures[0].field_type_shape == expected_shape

    def test_getter_resolves_field_type_shape_from_property_name(self) -> None:
        field = dump_cs_field(
            "Direction",
            offset=0x18,
            field_name="direction_",
            enum_names=frozenset({"Direction"}),
        )
        field.property_name = "Direction"
        message = DumpCSMessage(file_descriptor="FD", name="Message", fields=[field])
        function = function_access_info(
            name="Mapper::Message Build(Message)",
            return_type="Message",
            access_infos=(
                builder_field_access_entry(
                    cls="Message",
                    field="unknown_",
                    access_kind="getter",
                    property_name="Direction",
                    field_offset=0x18,
                ),
            ),
        )

        signature = build_access_signatures_for_test(function, messages=(message,))["Message"]

        assert signature.function_signatures[0].self_accesses[0].field_type_shape == ENUM_SHAPE
        assert signature.field_signatures[0].field_type_shape == ENUM_SHAPE

    def test_ambiguous_offset_access_fails_field_resolution(self) -> None:
        message = DumpCSMessage(
            file_descriptor="FD",
            name="Message",
            fields=[
                dump_cs_field("int", offset=0x18, field_name="first_"),
                dump_cs_field("string", offset=0x18, field_name="second_"),
            ],
        )
        function = function_access_info(
            access_infos=(
                builder_field_access_entry(
                    cls="Message",
                    field="missing_",
                    property_name=None,
                    field_offset=0x18,
                ),
            ),
        )

        with pytest.raises(KeyError):
            build_access_signatures_for_test(function, messages=(message,))

    def test_declared_similarity_fields_include_only_observed_proto_fields(self) -> None:
        scalar_field = dump_cs_field("int", offset=0x18, field_name="value_")
        oneof_backing_field = dump_cs_field("object", offset=0x20, field_name="choice_")
        oneof_variant_field = dump_cs_field("string", offset=0x20, field_name="ChoiceOne")
        oneof_variant_field.property_name = "ChoiceOne"
        oneof_variant_field.oneof_group_name = "choice"
        oneof_variant_field.is_synthetic_oneof_variant = True
        message = DumpCSMessage(
            file_descriptor="FD",
            name="Message",
            fields=[scalar_field, oneof_backing_field, oneof_variant_field],
        )
        function = function_access_info(
            access_infos=(
                builder_field_access_entry(
                    cls="Message", field="value_", property_name=None, field_offset=0x18
                ),
                builder_field_access_entry(
                    cls="Message",
                    field="ChoiceOne",
                    access_kind="getter",
                    property_name="ChoiceOne",
                    field_offset=None,
                ),
            ),
        )

        signature = build_access_signatures_for_test(function, messages=(message,))["Message"]

        assert sorted(
            (field.field_type_shape, field.oneof_group_name is not None)
            for field in signature.declared_similarity_fields
        ) == sorted(
            [
                (NUMBER_SHAPE, False),
                (STRING_SHAPE, True),
            ]
        )

    def test_declared_similarity_fields_ignore_decl_order_for_observed_fields(self) -> None:
        first_a = dump_cs_field("int", offset=0x18, field_name="value_")
        first_a.property_name = "Value"
        first_a.proto_decl_order = 0
        second_a = dump_cs_field("bool", offset=0x20, field_name="flag_")
        second_a.property_name = "Flag"
        second_a.proto_decl_order = 1
        first_b = dump_cs_field("int", offset=0x18, field_name="value_")
        first_b.property_name = "Value"
        first_b.proto_decl_order = 9
        second_b = dump_cs_field("bool", offset=0x20, field_name="flag_")
        second_b.property_name = "Flag"
        second_b.proto_decl_order = 5
        message_a = DumpCSMessage(file_descriptor="FD", name="MessageA", fields=[first_a, second_a])
        message_b = DumpCSMessage(file_descriptor="FD", name="MessageB", fields=[first_b, second_b])
        first_function = function_access_info(
            name="Mapper::Void RunA(MessageA)",
            parameters=("MessageA",),
            access_infos=(
                builder_field_access_entry(
                    cls="MessageA", field="value_", property_name="Value", field_offset=0x18
                ),
                builder_field_access_entry(
                    cls="MessageA", field="flag_", property_name="Flag", field_offset=0x20
                ),
            ),
        )
        second_function = function_access_info(
            name="Mapper::Void RunB(MessageB)",
            parameters=("MessageB",),
            access_infos=(
                builder_field_access_entry(
                    cls="MessageB", field="value_", property_name="Value", field_offset=0x18
                ),
                builder_field_access_entry(
                    cls="MessageB", field="flag_", property_name="Flag", field_offset=0x20
                ),
            ),
        )

        signatures = build_access_signatures_for_test(
            first_function,
            second_function,
            messages=(message_a, message_b),
        )

        assert tuple(
            field.field_type_shape for field in signatures["MessageA"].declared_similarity_fields
        ) == tuple(field.field_type_shape for field in signatures["MessageB"].declared_similarity_fields)

    def test_declared_similarity_fields_only_include_resolved_proto_fields(self) -> None:
        first_field = dump_cs_field("long", offset=0x18, field_name="map_id_")
        first_field.property_name = "MapId"
        second_field = dump_cs_field("long", offset=0x20, field_name="instance_id_")
        second_field.property_name = "InstanceId"
        message = DumpCSMessage(file_descriptor="FD", name="Message", fields=[first_field, second_field])
        function = function_access_info(
            access_infos=(
                builder_field_access_entry(
                    cls="Message", field="map_id_", property_name="MapId", field_offset=0x18
                ),
            ),
        )

        signature = build_access_signatures_for_test(function, messages=(message,))["Message"]

        assert signature.live_field_keys == frozenset({FieldKey(0x18, "map_id_")})
        assert signature.field_signatures[0].field_key == FieldKey(0x18, "map_id_")
        assert tuple(field.field_type_shape for field in signature.declared_similarity_fields) == (
            NUMBER_SHAPE,
        )

    def test_includes_dump_cs_messages_without_proto_accesses(self) -> None:
        accessed_field = dump_cs_field("long", offset=0x18, field_name="map_id_")
        accessed_field.property_name = "MapId"
        missing_field = dump_cs_field("bool", offset=0x18, field_name="is_valid_")
        missing_field.property_name = "IsValid"
        accessed_message = DumpCSMessage(
            file_descriptor="FD", name="AccessedMessage", fields=[accessed_field]
        )
        missing_message = DumpCSMessage(file_descriptor="FD", name="MissingMessage", fields=[missing_field])
        function = function_access_info(
            name="Mapper::Void Run(AccessedMessage)",
            parameters=("AccessedMessage",),
            access_infos=(
                builder_field_access_entry(
                    cls="AccessedMessage", field="map_id_", property_name="MapId", field_offset=0x18
                ),
            ),
        )

        signatures = build_access_signatures_for_test(function, messages=(accessed_message, missing_message))

        assert set(signatures) == {"AccessedMessage", "MissingMessage"}
        assert signatures["MissingMessage"].function_signatures == []
        assert signatures["MissingMessage"].field_signatures == []
        assert missing_field in signatures["MissingMessage"].dump_cs_msg.fields
        assert signatures["MissingMessage"].live_field_keys == frozenset()

    def test_parameter_only_proto_class_gets_signature_with_empty_self_accesses(self) -> None:
        function = function_access_info(
            name="Handler::Void Handle(EmptyMessage)",
            parameters=("EmptyMessage",),
            access_infos=(),
        )

        signature = build_access_signatures_for_test(function, message_classes=("EmptyMessage",))[
            "EmptyMessage"
        ]

        assert len(signature.function_signatures) == 1
        assert signature.function_signatures[0].self_accesses == []
        assert signature.function_signatures[0].takes_message_parameter is True
        assert signature.function_signatures[0].return_role == "void"
        assert signature.function_signatures[0].size == 80

    def test_parameter_only_does_not_duplicate_when_already_in_accesses(self) -> None:
        function = function_access_info(
            name="Handler::Void Handle(Message)",
            parameters=("Message",),
            access_infos=(builder_field_access_entry(cls="Com.Game.Message"),),
        )

        signature = build_access_signatures_for_test(function, message_classes=("Com.Game.Message",))[
            "Com.Game.Message"
        ]

        assert len(signature.function_signatures) == 1
        assert signature.function_signatures[0].self_accesses != []

    def test_parameter_only_skipped_when_short_name_is_ambiguous(self) -> None:
        function = function_access_info(
            name="Handler::Void Handle(Inner)",
            parameters=("Inner",),
            access_infos=(),
        )

        signatures = build_access_signatures_for_test(
            function,
            message_classes=("Namespace.A.Inner", "Namespace.B.Inner"),
        )

        assert signatures["Namespace.A.Inner"].function_signatures == []
        assert signatures["Namespace.B.Inner"].function_signatures == []

    def test_parameter_only_ignored_when_type_not_in_resolution_lookup(self) -> None:
        function = function_access_info(
            name="Handler::Void Handle(UnknownType)",
            parameters=("UnknownType",),
            access_infos=(builder_field_access_entry(cls="Com.Game.Message"),),
        )

        signature = build_access_signatures_for_test(function, message_classes=("Com.Game.Message",))[
            "Com.Game.Message"
        ]

        assert len(signature.function_signatures) == 1

    def test_enum_accesses_mark_matching_field_as_live_without_ida_data(self) -> None:
        enum_field = dump_cs_field(
            "Direction",
            offset=0x28,
            field_name="direction_",
            enum_names=frozenset({"Direction"}),
        )
        message = DumpCSMessage(file_descriptor="FD", name="Message", fields=[enum_field])

        signature = build_message_access_signatures_by_cls(
            build_proto_accesses(),
            {"Message": message},
            build_field_resolution_lookup(message),
            enum_signatures={"Direction": enum_signature_entry(field_offset=0x28)},
        )["Message"]

        assert signature.live_field_keys == frozenset({FieldKey(0x28, "direction_")})
        assert signature.field_signatures[0].field_key == FieldKey(0x28, "direction_")
        assert tuple(field.field_type_shape for field in signature.declared_similarity_fields) == (
            ENUM_SHAPE,
        )
        assert signature.declared_similarity_fields[0].enum_value_type == "Direction"
        assert len(signature.field_signatures) == 1
        assert signature.field_signatures[0].field_offset == 0x28
        assert signature.field_signatures[0].accesses == []

    def test_enum_accesses_ignore_field_when_offset_does_not_match(self) -> None:
        enum_field = dump_cs_field(
            "Direction",
            offset=0x28,
            field_name="direction_",
            enum_names=frozenset({"Direction"}),
        )
        message = DumpCSMessage(file_descriptor="FD", name="Message", fields=[enum_field])

        signature = build_message_access_signatures_by_cls(
            build_proto_accesses(),
            build_file_descriptor_lookup("Message"),
            build_field_resolution_lookup(message),
            enum_signatures={"Direction": enum_signature_entry(field_offset=0x18)},
        )["Message"]

        assert signature.live_field_keys == frozenset()
        assert signature.field_signatures == []

    def test_enum_accesses_merge_with_proto_accesses_without_duplicate_field_signature(self) -> None:
        scalar_field = dump_cs_field("int", offset=0x18, field_name="value_")
        enum_field = dump_cs_field(
            "Direction",
            offset=0x28,
            field_name="direction_",
            enum_names=frozenset({"Direction"}),
        )
        enum_field.property_name = "Direction"
        message = DumpCSMessage(file_descriptor="FD", name="Message", fields=[scalar_field, enum_field])
        function = function_access_info(
            access_infos=(
                builder_field_access_entry(
                    cls="Message", field="value_", property_name=None, field_offset=0x18
                ),
                builder_field_access_entry(
                    cls="Message", field="direction_", property_name="Direction", field_offset=0x28
                ),
            ),
        )

        signature = build_access_signatures_for_test(
            function,
            messages=(message,),
            enum_signatures={"Direction": enum_signature_entry(field_offset=0x28)},
        )["Message"]

        assert signature.live_field_keys == frozenset(
            {FieldKey(0x18, "value_"), FieldKey(0x28, "direction_")}
        )
        assert [field_signature.field_offset for field_signature in signature.field_signatures] == [
            0x18,
            0x28,
        ]
        assert len(signature.field_signatures[1].accesses) == 1
