import unittest

from src.common.dataclass_utils import apply_dict_to_dataclass, dataclass_to_dict
from src.tools.recorder import Recorder
from tests.fixtures.random_generator import (
    generate_random_bot,
    generate_random_inventory,
)


class TestDeserialiser(unittest.TestCase):
    def test_deserialiser(self):
        # fake_bot.game_info_signals.objects_by_uid_updated.emit(
        #     generate_random_inventory()
        # )
        recorder = Recorder()
        game_state = generate_random_bot().game_state
        for uid, object_item_inv in generate_random_inventory().items():
            game_state.inventory.objects_by_uid[uid] = object_item_inv
        dict_game_state = dataclass_to_dict(game_state)

        game_state.inventory.objects_by_uid.clear()

        apply_dict_to_dataclass(game_state, dict_game_state)

        print(game_state.inventory.objects_by_uid)
