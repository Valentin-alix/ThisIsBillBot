from proto_schema_parser import Field, Message
from proto_schema_parser.ast import Enum, MapField, OneOf

from D3Mapping.d3_mapping.exceptions import UnhandledTypeCase
from D3Mapping.d3_mapping.factories.p_enum_factory import PEnumFactory
from D3Mapping.d3_mapping.models.p_enum import PEnum
from D3Mapping.d3_mapping.models.p_message import (
    PField,
    PMapField,
    PMessage,
    POneOf,
)


class PMessageFactory:
    @staticmethod
    def create_p_messages_with_namespace(
        proto_message: Message, namespace: str = ""
    ) -> dict[str, PMessage | PEnum]:
        p_struct_with_namespace: dict[str, PMessage | PEnum] = {}
        p_msg_elems: list[PField | POneOf | PMapField] = []
        for elem in proto_message.elements:
            if type(elem) is Field:
                p_msg_elems.append(
                    PField(
                        type_name=elem.type,
                        name=elem.name,
                        number=elem.number,
                        cardinality=elem.cardinality,
                    )
                )
            elif type(elem) is OneOf:
                p_msg_elems.append(POneOfFactory.create_p_one_of(elem))
            elif type(elem) is Message:
                p_struct_with_namespace |= (
                    PMessageFactory.create_p_messages_with_namespace(
                        elem, namespace=namespace + f".{elem.name}"
                    )
                )
            elif type(elem) is Enum:
                enum_namespace = namespace + f".{elem.name}"
                p_struct_with_namespace[enum_namespace] = PEnumFactory.create_p_enum(
                    elem, namespace=enum_namespace
                )
            elif type(elem) is MapField:
                p_msg_elems.append(PMapFieldFactory.create_p_map_field(elem))
            else:
                raise UnhandledTypeCase(type(elem))

        p_struct_with_namespace[namespace] = PMessage(
            name=proto_message.name, elements=p_msg_elems, namespace=namespace
        )

        return p_struct_with_namespace


class POneOfFactory:
    @staticmethod
    def create_p_one_of(proto_one_of: OneOf) -> POneOf:
        p_one_of_elements: list[PField] = []
        for elem in proto_one_of.elements:
            if type(elem) is Field:
                p_one_of_elements.append(
                    PField(
                        type_name=elem.type,
                        name=elem.name,
                        number=elem.number,
                        cardinality=elem.cardinality,
                    )
                )
            else:
                raise UnhandledTypeCase(type(elem))
        return POneOf(name=proto_one_of.name, elements=p_one_of_elements)


class PMapFieldFactory:
    @staticmethod
    def create_p_map_field(map_field: MapField) -> PMapField:
        value_p_field = PField(
            type_name=map_field.value_type,
            name=map_field.name,
            number=map_field.number,
            cardinality=None,
        )
        return PMapField(
            name=map_field.name,
            key_type=map_field.key_type,
            value_p_field=value_p_field,
            number=map_field.number,
        )
