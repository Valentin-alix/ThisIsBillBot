from typing import Iterable
from d3_mapping.models.p_enum import PEnum
from d3_mapping.models.p_message import PField, PMapField, PMessage, POneOf


class ProtoOrganization:
    @staticmethod
    def get_related_struct(
        struct_by_namespace: dict[str, PMessage | PEnum],
        msg_namespace: str,
        type_name: str,
    ):
        struct = struct_by_namespace.get(msg_namespace + "." + type_name)
        if struct is None:
            struct = struct_by_namespace[type_name]
        return struct

    @staticmethod
    def get_flat_elements(
        elements: Iterable[PMapField | PField | POneOf],
    ) -> dict[int, PMapField | PField]:
        len_elems: int = 0
        elem_by_index: dict[int, PMapField | PField] = {}
        for elem in elements:
            if isinstance(elem, POneOf):
                for one_of_elem in elem.elements:
                    elem_by_index[len_elems] = one_of_elem
                    len_elems += 1
            else:
                elem_by_index[len_elems] = elem
                len_elems += 1
        return elem_by_index
