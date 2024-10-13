from src.core.logic.criterions.group_item_criterion import GroupItemCriterion
from tests.setup_factory import GameStateFixture


class TestCriterion(GameStateFixture):
    def test_valid_criterion(self):
        criterion = GroupItemCriterion("MI=515576,1")
        is_respected = criterion.is_respected(self.game_state)
        print(is_respected)
