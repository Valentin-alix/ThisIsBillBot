from dataclasses import dataclass
from typing import Any

from pandas import Series

from D3Mapping.d3_mapping.consts import TYPE_URL_PREFIX
from D3Mapping.d3_mapping.controller.instancied_msg_info_controller import (
    InstanciedMessageInfoController,
)
from D3Mapping.d3_mapping.mapping.proto_organization import ProtoOrganization
from D3Mapping.d3_mapping.mapping.validators.global_validators import (
    VALIDATORS_GLOBAL_ON_SET_FIELDS,
)
from D3Mapping.d3_mapping.mapping.validators.set_validators import (
    VALIDATORS_ON_SET_FIELDS,
)
from D3Mapping.d3_mapping.models.mapping_info import FieldMapping, OutputMappingInfo
from D3Mapping.d3_mapping.models.p_enum import PEnum
from D3Mapping.d3_mapping.models.p_message import PMessage


@dataclass
class ProtoValidator:
    clear_struct_by_namespace: dict[str, PMessage | PEnum]
    obf_struct_by_namespace: dict[str, PMessage | PEnum]
    msg_mapping_info_by_obf_namespace: dict[str, OutputMappingInfo]

    def is_valid_clear_by_obf_field_mapping(
        self,
        treated_clear_namespaces: set[str],
        clear_msg: PMessage,
        obf_msg: PMessage,
        clear_by_obf_field_mapping: FieldMapping,
    ):
        # Check if combination of mapped fields is coherent based on validators
        obf_msg_infos = InstanciedMessageInfoController().get_content_by_name(
            obf_msg.name
        )

        values_array_mapped_to_clear_by_clear_msg_name = (
            self.get_values_array_mapped_to_clear(
                treated_clear_namespaces,
                clear_msg=clear_msg,
                obf_msg=obf_msg,
                clear_by_obf_field_mapping=clear_by_obf_field_mapping,
                obf_msg_infos=obf_msg_infos,
                values_array_mapped_to_clear_by_msg={},
            )
        )

        for (
            sub_clear_msg,
            values_array_mapped_to_clear,
        ) in values_array_mapped_to_clear_by_clear_msg_name.items():
            validator_on_whole_msg = VALIDATORS_ON_SET_FIELDS.get(sub_clear_msg.name)
            validator_global_on_whole_msg = VALIDATORS_GLOBAL_ON_SET_FIELDS.get(
                sub_clear_msg.name
            )
            if not validator_on_whole_msg and not validator_global_on_whole_msg:
                continue

            if validator_global_on_whole_msg:
                values_array_mapped_to_clear = list(values_array_mapped_to_clear)
                try:
                    if not validator_global_on_whole_msg[0](
                        values_array_mapped_to_clear
                    ):
                        return False
                except Exception:
                    return False

            if validator_on_whole_msg:
                for values_mapped_to_clear in values_array_mapped_to_clear:
                    try:
                        if not validator_on_whole_msg[0](values_mapped_to_clear):
                            return False
                    except Exception:
                        return False

        return True

    def get_values_array_mapped_to_clear(
        self,
        treated_clear_namespaces: set[str],
        clear_msg: PMessage,
        obf_msg: PMessage,
        clear_by_obf_field_mapping: FieldMapping,
        obf_msg_infos: Series,
        values_array_mapped_to_clear_by_msg: dict[PMessage, list[dict[str, Any]]],
    ) -> dict[PMessage, list[dict[str, Any]]]:
        """get deep values based on mapping with clear mapped field as key"""

        for obf_msg_info in obf_msg_infos:
            values_mapped_to_clear = {}

            for key, value in obf_msg_info.items():
                is_any_value = (
                    type(value) is dict
                    and "type_url" in value
                    and TYPE_URL_PREFIX in value["type_url"]
                )
                if is_any_value:
                    value: dict
                    obf_type_url = value["type_url"].split("/")[1]
                    if obf_type_url in self.msg_mapping_info_by_obf_namespace:
                        value = {
                            "type_url": f"{TYPE_URL_PREFIX}{self.msg_mapping_info_by_obf_namespace[obf_type_url].clear_msg_namespace}"
                        }

                if key not in clear_by_obf_field_mapping:
                    continue
                if (clear_mapping_info := clear_by_obf_field_mapping[key]) is None:
                    continue

                clear_field_name = clear_mapping_info[1]

                if type(value) is dict and not is_any_value:
                    _sub_mapping_info = clear_mapping_info[2]
                    assert _sub_mapping_info is not None
                    _sub_obf_struct = (
                        ProtoOrganization.get_related_struct_from_field_name(
                            self.obf_struct_by_namespace, obf_msg, key
                        )
                    )
                    _sub_clear_struct = self.clear_struct_by_namespace[
                        _sub_mapping_info.clear_msg_namespace
                    ]
                    assert (
                        type(_sub_obf_struct) is PMessage
                        and type(_sub_clear_struct) is PMessage
                    )

                    sub_values_array = self.get_values_array_mapped_to_clear(
                        treated_clear_namespaces,
                        _sub_clear_struct,
                        _sub_obf_struct,
                        _sub_mapping_info.field_mapping,
                        Series([value]),
                        {},
                    )
                    for _key, _value in sub_values_array.items():
                        if _key not in values_array_mapped_to_clear_by_msg:
                            values_array_mapped_to_clear_by_msg[_key] = []
                        values_array_mapped_to_clear_by_msg[_key].extend(_value)
                    value = sub_values_array[_sub_clear_struct][0]
                elif type(value) is list:
                    _value = []
                    for sub_value in value:
                        if type(sub_value) is dict:
                            _sub_mapping_info = clear_mapping_info[2]
                            assert _sub_mapping_info is not None
                            # _value.append(sub_value)
                            _sub_obf_struct = (
                                ProtoOrganization.get_related_struct_from_field_name(
                                    self.obf_struct_by_namespace, obf_msg, key
                                )
                            )
                            _sub_clear_struct = self.clear_struct_by_namespace[
                                _sub_mapping_info.clear_msg_namespace
                            ]
                            assert (
                                type(_sub_obf_struct) is PMessage
                                and type(_sub_clear_struct) is PMessage
                            )
                            sub_values_array = self.get_values_array_mapped_to_clear(
                                treated_clear_namespaces,
                                _sub_clear_struct,
                                _sub_obf_struct,
                                clear_by_obf_field_mapping=_sub_mapping_info.field_mapping,
                                obf_msg_infos=Series([sub_value]),
                                values_array_mapped_to_clear_by_msg={},
                            )

                            for _key, _value in sub_values_array.items():
                                if _key not in values_array_mapped_to_clear_by_msg:
                                    values_array_mapped_to_clear_by_msg[_key] = []
                                values_array_mapped_to_clear_by_msg[_key].extend(_value)
                            sub_value = sub_values_array[_sub_clear_struct][0]
                            _value.append(sub_value)
                        else:
                            _value.append(sub_value)
                    value = _value

                values_mapped_to_clear[clear_field_name] = value

            if clear_msg not in values_array_mapped_to_clear_by_msg:
                values_array_mapped_to_clear_by_msg[clear_msg] = []
            values_array_mapped_to_clear_by_msg[clear_msg].append(
                values_mapped_to_clear
            )

        return values_array_mapped_to_clear_by_msg
