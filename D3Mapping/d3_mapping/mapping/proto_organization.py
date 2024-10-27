from d3_mapping.consts import PROTO_BASE_FIELDS
from d3_mapping.models.p_enum import PEnum
from d3_mapping.models.p_message import PField, PMapField, PMessage, POneOf


class ProtoOrganization:
    @staticmethod
    def get_related_struct_from_type_name(
        struct_by_namespace: dict[str, PMessage | PEnum],
        msg_namespace: str,
        type_name: str,
    ):
        struct = struct_by_namespace.get(msg_namespace + "." + type_name)
        if struct is None:
            struct = struct_by_namespace[type_name]
        return struct

    @staticmethod
    def get_related_struct_from_field_name(
        struct_by_namespace: dict[str, PMessage | PEnum],
        msg: PMessage,
        field_name: str,
    ):
        related_elem = next(
            elem
            for elem in ProtoOrganization.get_flat_elements(msg).values()
            if elem.name == field_name
        )
        type_name = (
            related_elem.type_name
            if isinstance(related_elem, PField)
            else related_elem.value_p_field.type_name
        )
        if type_name in PROTO_BASE_FIELDS:
            return None
        return ProtoOrganization.get_related_struct_from_type_name(
            struct_by_namespace, msg.namespace, type_name
        )

    @staticmethod
    def get_flat_elements(
        msg: PMessage,
    ) -> dict[int, PMapField | PField]:
        len_elems: int = 0
        elem_by_index: dict[int, PMapField | PField] = {}
        for elem in msg.elements:
            if isinstance(elem, POneOf):
                for one_of_elem in elem.elements:
                    elem_by_index[len_elems] = one_of_elem
                    len_elems += 1
            else:
                elem_by_index[len_elems] = elem
                len_elems += 1
        return elem_by_index
