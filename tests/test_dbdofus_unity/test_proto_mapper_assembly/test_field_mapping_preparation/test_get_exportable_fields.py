from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.field_builders import (
    dump_field,
    make_oneof_field,
)
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.message_builders import (
    field_signature,
    make_field_mapping_context,
    make_message_signature,
    prepare_field_mapping_context_for_test,
)

from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, DumpCSMessageField
from proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from proto_mapper_assembly.interfaces.pinned_pairs import PinnedPair
from proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore


class TestGetExportableFields:
    def test_exports_live_oneof_group_members(self) -> None:
        live_field = make_oneof_field(
            "field_a_",
            0x10,
            group_name="my_oneof",
            proto_decl_order=1,
            property_name="FieldA",
        )
        grouped_field = make_oneof_field(
            "field_b_",
            0x18,
            group_name="my_oneof",
            proto_decl_order=2,
            property_name="FieldB",
        )
        signature = make_message_signature(
            DumpCSMessage(file_descriptor="FD", name="OneofMsg", fields=[live_field, grouped_field]),
            live_field_keys=frozenset({live_field.field_key}),
        )

        fields = signature.get_exportable_fields()

        assert fields == (live_field, grouped_field)

    def test_exports_named_fields_and_excludes_unnamed_fields(self) -> None:
        inactive_oneof = make_oneof_field(
            "dead_field_",
            0x10,
            group_name="inactive_oneof",
            proto_decl_order=1,
            property_name="DeadField",
        )
        live_without_property = make_oneof_field(
            "noprop_",
            0x18,
            group_name="named_oneof",
            proto_decl_order=1,
            property_name=None,
        )
        signature = make_message_signature(
            DumpCSMessage(
                file_descriptor="FD",
                name="InactiveMsg",
                fields=[inactive_oneof, live_without_property],
            ),
            live_field_keys=frozenset({live_without_property.field_key}),
        )

        assert signature.get_exportable_fields() == (inactive_oneof,)


class TestPrepareFieldMappingContext:
    def test_keeps_oneof_variants_with_shared_offset_as_distinct_signatures(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        message_variant = DumpCSMessageField(
            clr_type="Child",
            normalized_type="Child",
            category=FieldCategoryEnum.MESSAGE,
            memory_offset=0x18,
            field_name="message_variant_",
            property_name="MessageVariant",
            proto_decl_order=1,
            oneof_group_name="choice",
            is_synthetic_oneof_variant=True,
        )
        enum_variant = DumpCSMessageField(
            clr_type="ChoiceEnum",
            normalized_type="ChoiceEnum",
            category=FieldCategoryEnum.ENUM,
            memory_offset=0x18,
            field_name="enum_variant_",
            property_name="EnumVariant",
            proto_decl_order=2,
            oneof_group_name="choice",
            is_synthetic_oneof_variant=True,
            enum_value_type="ChoiceEnum",
        )
        obf_field = dump_field("fab", "Fab", 0x20, FieldCategoryEnum.NUMBER)
        non_obf_message = DumpCSMessage(
            file_descriptor="FD",
            name="OneofMessage",
            fields=[message_variant, enum_variant],
        )
        obf_message = DumpCSMessage(file_descriptor="FD", name="aab", fields=[obf_field])
        non_obf_signature = make_message_signature(
            non_obf_message,
            live_field_keys=frozenset({message_variant.field_key, enum_variant.field_key}),
            field_signatures=[
                field_signature(
                    message_variant.memory_offset,
                    message_variant.field_type_shape,
                    field_key=message_variant.field_key,
                ),
                field_signature(
                    enum_variant.memory_offset,
                    enum_variant.field_type_shape,
                    field_key=enum_variant.field_key,
                ),
            ],
        )
        obf_signature = make_message_signature(
            obf_message,
            live_field_keys=frozenset({obf_field.field_key}),
        )

        context = prepare_field_mapping_context_for_test(
            non_obf_signature=non_obf_signature,
            obf_signature=obf_signature,
            field_mapping_context=make_field_mapping_context(runtime_data_store),
        )

        assert context.non_obf.field_signature_by_field_key[message_variant.field_key].field_type_shape == (
            message_variant.field_type_shape
        )
        assert context.non_obf.field_signature_by_field_key[enum_variant.field_key].field_type_shape == (
            enum_variant.field_type_shape
        )

    def test_includes_pinned_non_obf_field_without_live_access(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        pinned_field = dump_field("summon_id_", "SummonId", 0x10, FieldCategoryEnum.NUMBER)
        dead_field = dump_field("ignored_", "Ignored", 0x18, FieldCategoryEnum.NUMBER)
        obf_field = dump_field("fab", "Fab", 0x20, FieldCategoryEnum.NUMBER)
        non_obf_message = DumpCSMessage(
            file_descriptor="FD",
            name="SummonContextInformation",
            fields=[pinned_field, dead_field],
        )
        obf_message = DumpCSMessage(file_descriptor="FD", name="aab", fields=[obf_field])
        non_obf_signature = make_message_signature(non_obf_message)
        obf_signature = make_message_signature(
            obf_message,
            live_field_keys=frozenset({obf_field.field_key}),
        )

        context = prepare_field_mapping_context_for_test(
            non_obf_signature=non_obf_signature,
            obf_signature=obf_signature,
            field_mapping_context=make_field_mapping_context(runtime_data_store),
            pinned_pair=PinnedPair(
                obf=obf_message.composed_name,
                non_obf=non_obf_message.composed_name,
                field_mapping_by_obf={"fab": "summon_id"},
            ),
        )

        assert sorted(field.clean_field_name for field in context.non_obf.fields) == [
            "ignored",
            "summon_id",
        ]
        non_obf_field_keys = {field.field_key for field in context.non_obf.fields}
        assert pinned_field.field_key in non_obf_field_keys
        assert dead_field.field_key in non_obf_field_keys
        access_signature = context.non_obf.field_signature_by_field_key[pinned_field.field_key]
        assert access_signature.field_offset == pinned_field.memory_offset
        assert access_signature.accesses == []

    def test_adds_synthetic_access_signature_for_active_oneof_variant(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        live_field = make_oneof_field(
            "live_value_",
            0x10,
            group_name="choice",
            proto_decl_order=1,
            property_name="LiveValue",
        )
        grouped_field_without_access = make_oneof_field(
            "grouped_value_",
            0x18,
            group_name="choice",
            proto_decl_order=2,
            property_name="GroupedValue",
        )
        obf_field = dump_field("fab", "Fab", 0x20, FieldCategoryEnum.NUMBER)
        non_obf_message = DumpCSMessage(
            file_descriptor="FD",
            name="OneofMessage",
            fields=[live_field, grouped_field_without_access],
        )
        obf_message = DumpCSMessage(file_descriptor="FD", name="aab", fields=[obf_field])
        non_obf_signature = make_message_signature(
            non_obf_message,
            live_field_keys=frozenset({live_field.field_key}),
            field_signatures=[field_signature(live_field.memory_offset, None)],
        )
        obf_signature = make_message_signature(
            obf_message,
            live_field_keys=frozenset({obf_field.field_key}),
            field_signatures=[field_signature(obf_field.memory_offset, None)],
        )

        context = prepare_field_mapping_context_for_test(
            non_obf_signature=non_obf_signature,
            obf_signature=obf_signature,
            field_mapping_context=make_field_mapping_context(runtime_data_store),
        )

        assert grouped_field_without_access in context.non_obf.fields
        assert grouped_field_without_access.field_key in context.non_obf.field_signature_by_field_key
