from D3Mapping.d3_mapping.models.p_enum import PEnum
from D3Mapping.d3_mapping.utils import get_value_with_len_malus, set_percentage


def compare_p_enum(clear_enum: PEnum, obf_enum: PEnum) -> float:
    return set_percentage(
        get_value_with_len_malus(1, len(clear_enum.elements), len(obf_enum.elements))
    )
