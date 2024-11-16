from typing import Any


def flatten_json(_json: dict | list | Any, parent_key="", sep="."):
    human_value: str = ""
    if isinstance(_json, dict):
        for sub_key, sub_value in _json.items():
            human_value += f" {flatten_json(sub_value, sub_key, sep=sep)}"
    elif isinstance(_json, list):
        for sub_index, sub_value in enumerate(_json):
            human_value += f" {flatten_json(sub_value, str(sub_index), sep=sep)}"
    else:
        human_value += f" {parent_key} = {_json}"
    return human_value
