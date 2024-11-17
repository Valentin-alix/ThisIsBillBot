import json

from pydantic import RootModel

from D3Mapping.d3_mapping.consts import (
    MAPPING_CONN_PROTO_PATH,
    MAPPING_GAME_PROTO_PATH,
)
from D3Mapping.d3_mapping.models.mapping_info import OutputMappingInfo


class MappingObfToClear(RootModel):
    root: dict[str, OutputMappingInfo]


class MessageMappingController:
    @staticmethod
    def dump_mapping(mapping: dict[str, OutputMappingInfo], output: str):
        with open(output, "w+") as file:
            file.write(
                MappingObfToClear(
                    dict(sorted(mapping.items(), key=lambda elem: elem[0]))
                ).model_dump_json(indent=2)
            )

    @staticmethod
    def get_mapping_conn():
        with open(MAPPING_CONN_PROTO_PATH, "r") as file:
            return MappingObfToClear.model_validate(json.load(file)).root

    @staticmethod
    def get_mapping_game():
        with open(MAPPING_GAME_PROTO_PATH, "r") as file:
            return MappingObfToClear.model_validate(json.load(file)).root
