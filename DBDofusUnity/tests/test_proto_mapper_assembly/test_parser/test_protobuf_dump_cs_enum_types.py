from google.protobuf import descriptor_pb2
from google.protobuf.descriptor import Descriptor
from google.protobuf.descriptor_pool import DescriptorPool

from proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum, FieldTypeLeafKind
from proto_mapper_assembly.parsers.protobuf_dump_cs import _descriptor_to_dump_cs

_ENUM_NAME = "Origin"


def _build_sample_descriptor() -> Descriptor:
    """A message holding a singular, a repeated and a mapped enum field."""
    file_proto = descriptor_pb2.FileDescriptorProto()
    file_proto.name = "enum_shape_fixture.proto"
    file_proto.package = "com.example"
    file_proto.syntax = "proto3"

    enum_proto = file_proto.enum_type.add()
    enum_proto.name = _ENUM_NAME
    for number, name in enumerate(("ORIGIN_BANK", "ORIGIN_HAVEN_BAG")):
        value_proto = enum_proto.value.add()
        value_proto.name = name
        value_proto.number = number

    message_proto = file_proto.message_type.add()
    message_proto.name = "Sample"

    map_entry = message_proto.nested_type.add()
    map_entry.name = "MappedEntry"
    map_entry.options.map_entry = True
    map_key = map_entry.field.add()
    map_key.name = "key"
    map_key.number = 1
    map_key.type = descriptor_pb2.FieldDescriptorProto.TYPE_INT32
    map_key.label = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL
    map_value = map_entry.field.add()
    map_value.name = "value"
    map_value.number = 2
    map_value.type = descriptor_pb2.FieldDescriptorProto.TYPE_ENUM
    map_value.type_name = f".com.example.{_ENUM_NAME}"
    map_value.label = descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL

    for number, (name, label, type_name) in enumerate(
        (
            ("single", descriptor_pb2.FieldDescriptorProto.LABEL_OPTIONAL, f".com.example.{_ENUM_NAME}"),
            ("many", descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED, f".com.example.{_ENUM_NAME}"),
        ),
        start=1,
    ):
        field_proto = message_proto.field.add()
        field_proto.name = name
        field_proto.number = number
        field_proto.type = descriptor_pb2.FieldDescriptorProto.TYPE_ENUM
        field_proto.type_name = type_name
        field_proto.label = label

    mapped_field = message_proto.field.add()
    mapped_field.name = "mapped"
    mapped_field.number = 3
    mapped_field.type = descriptor_pb2.FieldDescriptorProto.TYPE_MESSAGE
    mapped_field.type_name = ".com.example.Sample.MappedEntry"
    mapped_field.label = descriptor_pb2.FieldDescriptorProto.LABEL_REPEATED

    pool = DescriptorPool()
    pool.Add(file_proto)
    return pool.FindMessageTypeByName("com.example.Sample")


class TestProtobufDumpCsEnumTypes:
    def test_enum_fields_carry_their_enum_name_as_value_type(self) -> None:
        message = _descriptor_to_dump_cs(_build_sample_descriptor(), enum_names=frozenset({_ENUM_NAME}))
        value_types_by_property = {field.property_name: field.enum_value_type for field in message.fields}

        assert value_types_by_property == {
            "Single": _ENUM_NAME,
            "Many": _ENUM_NAME,
            "Mapped": _ENUM_NAME,
        }

    def test_repeated_enum_field_shape_is_an_enum_not_a_message(self) -> None:
        # Without the enum value type, resolve_non_container_field_kind falls back to
        # MESSAGE and the shape stops matching the obfuscated RepeatedField<enum> side,
        # which makes the signature override export reject the pinned pair.
        message = _descriptor_to_dump_cs(_build_sample_descriptor(), enum_names=frozenset({_ENUM_NAME}))
        shapes_by_property = {field.property_name: field.field_type_shape for field in message.fields}

        repeated_shape = shapes_by_property["Many"]
        assert repeated_shape.category is FieldCategoryEnum.REPEATED
        assert repeated_shape.inner_kind is FieldTypeLeafKind.ENUM
