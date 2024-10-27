import json
import os
from enum import StrEnum

from d3_mapping.consts import UNITY_MAPPER_PATH
from D3Database.utils import cache


@cache
def get_game_mapping_by_obf():
    with open(os.path.join(UNITY_MAPPER_PATH, "GameMapping.json"), "r") as file:
        return {
            key: value if value != "Message" else "GameMessage"
            for key, value in json.load(file).items()
        }


@cache
def get_game_mapping_by_clear():
    return {value: key for key, value in get_game_mapping_by_obf().items()}


@cache
def get_connection_mapping_by_obf():
    with open(os.path.join(UNITY_MAPPER_PATH, "ConnectionMapping.json"), "r") as file:
        return {
            key: value if value != "Message" else "LoginMessage"
            for key, value in json.load(file).items()
        }


@cache
def get_connection_mapping_by_clear():
    return {value: key for key, value in get_connection_mapping_by_obf().items()}


GAME_MAPPING_FIELDS: dict[str, dict[str, str]] = {
    "GameActionFightEvent": {
        "slide": "ejcw",
        "death": "ejds",
        "life_points_gain": "ejdh",
    },
    "Slide": {"start_cell": "ejaw"},
}


RELIABILITY_BY_PROTO_BASE_FIELDS: dict[str, float] = {
    "int32": 1,
    "int64": 1,
    "float": 1,
    "bool": 1,
    "string": 1,
    "google.protobuf.Any": 10,
}

PROTO_BASE_FIELDS: list[str] = list(RELIABILITY_BY_PROTO_BASE_FIELDS.keys())

LIMIT = 0.7

BASE_RELIABILITY = 1
EXTRA_RELIABILITY_REPEATED = 2
EXTRA_RELIABILITY_MAP = 2
EXTRA_RELIABILITY_ENUM = 3
EXTRA_RELIABILITY_MESSAGE = 2
EXTRA_RELIABILITY_WITH_VALIDATOR = 5


class EntryMsg(StrEnum):
    REQUEST = "Request"
    RESPONSE = "Response"
    EVENT = "Event"
