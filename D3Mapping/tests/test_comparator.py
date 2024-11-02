import unittest

from d3_mapping.consts import (
    OBFUSCATED_PROTO_GAME,
    PROTO_GAME_PATH,
    get_game_mapping_by_obf,
)
from d3_mapping.factories.p_mapper_factory import PMapperFactory
from tests.utils import ComparisonInfo, test_comparisons


class TestComparator(unittest.TestCase):
    def setUp(self) -> None:
        self.game_p_mapper = PMapperFactory.create_p_mapper(
            PROTO_GAME_PATH, OBFUSCATED_PROTO_GAME, get_game_mapping_by_obf(), {}
        )
        # self.conn_p_mapper = PMapperFactory.create_p_mapper(
        #     PROTO_CONNECTION_PATH,
        #     OBFUSCATED_PROTO_CONNECTION,
        #     get_connection_mapping_by_obf(),
        #     {},
        # )
        return super().setUp()

    def test_game_msg(self):
        comparisons: list[ComparisonInfo] = [
            (
                ".com.ankama.dofus.server.game.protocol.common.ObjectItem",
                "bpcb",
            )
        ]
        test_comparisons(self.game_p_mapper, comparisons)
