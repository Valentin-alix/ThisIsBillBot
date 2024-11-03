import json
import os

from pydantic import BaseModel, Field

from d3_mapping.consts import (
    GAME_ASSEMBLY_PATH,
    MAPPING_CONN_PROTO_PATH,
    MAPPING_GAME_PROTO_PATH,
)
from d3_mapping.models.mapping_info import OutputMappingInfo


class MappingObfToClear(BaseModel):
    obf_to_clear: dict[str, OutputMappingInfo]
    version_date: float = Field(
        default_factory=lambda: os.path.getmtime(GAME_ASSEMBLY_PATH)
    )


class MessageMappingController:
    @staticmethod
    def dump_mapping(mapping: dict[str, OutputMappingInfo], output: str):
        with open(output, "w+") as file:
            file.write(
                MappingObfToClear(obf_to_clear=mapping).model_dump_json(indent=2)
            )

    @staticmethod
    def get_mapping_conn():
        with open(MAPPING_CONN_PROTO_PATH, "r") as file:
            return MappingObfToClear.model_validate(json.load(file)).obf_to_clear

    @staticmethod
    def get_mapping_game():
        with open(MAPPING_GAME_PROTO_PATH, "r") as file:
            return MappingObfToClear.model_validate(json.load(file)).obf_to_clear

    @staticmethod
    def get_mapping_game_version():
        with open(MAPPING_GAME_PROTO_PATH, "r") as file:
            return MappingObfToClear.model_validate(json.load(file)).version_date
