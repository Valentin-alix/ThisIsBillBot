import unittest


from d3_mapping.consts import OBFUSCATED_PROTO_GAME, PROTO_GAME_PATH
from d3_mapping.factories.p_mapper_factory import PMapperFactory


class TestReliabilityCalculator(unittest.TestCase):
    def setUp(self) -> None:
        self.game_p_mapper = PMapperFactory.create_p_mapper(
            PROTO_GAME_PATH, OBFUSCATED_PROTO_GAME
        )
        return super().setUp()

    def test_sorted_clear_files_by_reliability(self):
        sorted_clear_files = self.game_p_mapper.reliability_calculator.get_sorted_clear_files_by_reliability()
        print(sorted_clear_files[:5])
