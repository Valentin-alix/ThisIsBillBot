from __future__ import annotations

JSONValue = str | int | float | bool | None | list["JSONValue"] | dict[str, "JSONValue"]


def flatten_json(json_value: JSONValue, parent_key: str = "", sep: str = ".") -> str:
    human_value: str = ""
    if isinstance(json_value, dict):
        for sub_key, sub_value in json_value.items():
            child_key = f"{parent_key}{sep}{sub_key}" if parent_key else sub_key
            human_value += f" {flatten_json(sub_value, child_key, sep=sep)}"
    elif isinstance(json_value, list):
        for sub_index, sub_value in enumerate(json_value):
            child_key = f"{parent_key}{sep}{sub_index}" if parent_key else str(sub_index)
            human_value += f" {flatten_json(sub_value, child_key, sep=sep)}"
    else:
        human_value += f" {parent_key} = {json_value}"
    return human_value
