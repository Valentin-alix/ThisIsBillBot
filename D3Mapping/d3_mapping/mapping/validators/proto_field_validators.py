from functools import cache
from typing import Any, Callable

from pydantic import BaseModel

from D3Mapping.d3_mapping.controller.instancied_msg_info_controller import (
    InstanciedMessageInfoController,
)


class ProtoFieldValidator(BaseModel):
    validators: list[Callable[[Any], bool]]


def is_condition_respected(
    msg_namespace: str, field_name: str, field_validator: ProtoFieldValidator
) -> bool:
    obf_msg_infos = InstanciedMessageInfoController().get_content_by_name(msg_namespace)
    for obf_msg_info in obf_msg_infos:
        for validator in field_validator.validators:
            try:
                is_valid = validator(obf_msg_info.get(field_name))
                if not is_valid:
                    return False
            except TypeError:
                return False
    return True


def is_not_always_default_value(msg_name: str, field_name: str) -> bool:
    return any(
        obf_msg_info[field_name] not in [{}, [], None, 0, False, ""]
        for obf_msg_info in InstanciedMessageInfoController().get_content_by_name(
            msg_name
        )
    )


DEFAULT_PROTO_VALUES = [{}, [], None, 0, False, ""]


@cache
def get_count_defined_msg_field_values(msg_namespace: str, field_name: str) -> int:
    obf_msg_infos = InstanciedMessageInfoController().get_content_by_name(msg_namespace)
    unique_values = set()
    is_probably_dict_or_list: bool = True
    for obf_msg_info in obf_msg_infos:
        if (
            field_name not in obf_msg_info
            or (value := obf_msg_info[field_name]) in DEFAULT_PROTO_VALUES
        ):
            continue
        if is_probably_dict_or_list and (type(value) is list or type(value) is dict):
            return len(obf_msg_infos)
        is_probably_dict_or_list = False
        unique_values.add(value)
    return len(unique_values)


def is_parsed_obf_msg(obf_msg_namespace: str):
    return (
        len(InstanciedMessageInfoController().get_content_by_name(obf_msg_namespace))
        > 0
    )
