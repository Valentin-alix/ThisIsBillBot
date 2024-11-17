import re
import socket

from pydantic import validate_call

from D3Mapping.d3_mapping.models.mapping_info import Percentage


@validate_call
def set_percentage(value: Percentage) -> float:
    return min(value, 1)


def to_snake_case(value: str):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", value).lower()


def get_local_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as Socket:
        Socket.connect(("8.8.8.8", 80))
        return Socket.getsockname()[0]


def get_value_with_len_malus(value: float, len_clear_elems: int, len_obf_elems: int) -> float:
    malus = 2 if len_clear_elems > len_obf_elems else 1
    if len_obf_elems - 1 == len_clear_elems:
        return value / 1.1

    min_len_elems = min(len_clear_elems, len_obf_elems)
    max_len_elems = max(len_clear_elems, len_obf_elems)
    return value * (min_len_elems / max_len_elems) / malus
