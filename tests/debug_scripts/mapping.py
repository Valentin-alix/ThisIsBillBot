import itertools
import os
from pathlib import Path
from typing import Any, Mapping

from dotenv import load_dotenv

load_dotenv(os.path.join(Path(__file__).parent.parent, ".env"))


from d3_mapping.controller.instancied_msg_info_controller import (
    InstanciedMessageInfoController,
)
from d3_mapping.mapping.validators.field_validators import (
    is_valid_gid,
    is_valid_positive,
    is_valid_positive_total_quantity,
)
from d3_mapping.protocol.protocol_game import (
    get_mapping_proto_to_real,
)


def generate_all_possible_mapping(clear_mapping_by_obf: Mapping[str, str | None]):
    all_mappings: list[dict[str, str | None]] = []
    obf_fields = list(clear_mapping_by_obf.values())
    clear_fields = list(clear_mapping_by_obf.keys())
    for perm in itertools.permutations(clear_fields, len(obf_fields)):
        mapping = dict(zip(perm, obf_fields))
        all_mappings.append(mapping)
    return all_mappings


def convert_obf_values_to_clear_values(obf_msg_name: str):
    values: list[dict[str, Any]] = []
    clear_mapping_by_obf = get_mapping_proto_to_real()[obf_msg_name][1]
    all_content = InstanciedMessageInfoController().get_content_by_name(obf_msg_name)
    for obf_msg_info in all_content:
        value_msg_info: dict[str, Any] = {}
        for key, value in obf_msg_info.items():
            if key not in clear_mapping_by_obf:
                continue
            clear_key = clear_mapping_by_obf[key]
            if clear_key is not None:
                value_msg_info[clear_key] = value
        values.append(value_msg_info)
    return values


if __name__ == "__main__":
    clear_values = convert_obf_values_to_clear_values("jei")
    for clear_value in clear_values:
        if not is_valid_gid(clear_value["gid"]):
            print(clear_value)
        if not is_valid_positive_total_quantity(clear_value["quantity"]):
            print(clear_value)
        if not is_valid_positive(clear_value["uid"]):
            print(clear_value)

    # for _, value in df.iterrows():
    #     if not validator_slide(value.to_dict()):
    #         print(value)
