from d3_mapping.consts import (
    MAPPING_CONN_PROTO_PATH,
    MAPPING_GAME_PROTO_PATH,
    OBFUSCATED_PROTO_CONNECTION,
    OBFUSCATED_PROTO_GAME,
    PROTO_CONNECTION_PATH,
    PROTO_GAME_PATH,
)
from d3_mapping.controller.message_mapping_controller import (
    MessageMappingController,
)
from d3_mapping.factories.p_mapper_factory import PMapperFactory
from d3_mapping.mapping.consts import (
    GAME_MAPPING_FIELDS,
    get_connection_mapping_by_obf,
    get_game_mapping_by_obf,
)


def generate_mapping_proto(
    clear_directory: str,
    obf_directory: str,
    output: str,
    verified_mapping_by_obf: dict[str, str],
    verified_mapping_fields: dict[str, dict[str, str]],
):
    mapping = PMapperFactory.create_p_mapper(
        clear_directory,
        obf_directory,
        verified_mapping_by_obf=verified_mapping_by_obf,
        verified_mapping_fields=verified_mapping_fields,
    ).run_mapping()
    MessageMappingController.dump_mapping(mapping, output)


def generate_all_mapping():
    generate_mapping_proto(
        PROTO_CONNECTION_PATH,
        OBFUSCATED_PROTO_CONNECTION,
        MAPPING_CONN_PROTO_PATH,
        get_connection_mapping_by_obf(),
        {},
    )
    generate_mapping_proto(
        PROTO_GAME_PATH,
        OBFUSCATED_PROTO_GAME,
        MAPPING_GAME_PROTO_PATH,
        get_game_mapping_by_obf(),
        GAME_MAPPING_FIELDS,
    )
