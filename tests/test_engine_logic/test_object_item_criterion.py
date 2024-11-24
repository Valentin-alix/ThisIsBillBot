import unittest
from types import SimpleNamespace
from typing import cast

from src.core.engine.movements.world.criterions.items_criterion.object_item_criterion import (
    ObjectItemCriterion,
)
from src.core.states.game_state import GameState


def _make_game_state(item_quantity_by_gid: dict[int, int]) -> GameState:
    objects_by_uid = {
        uid: SimpleNamespace(item=SimpleNamespace(gid=gid, quantity=quantity))
        for uid, (gid, quantity) in enumerate(item_quantity_by_gid.items(), start=1)
    }
    return cast(
        GameState,
        SimpleNamespace(inventory=SimpleNamespace(objects_by_uid=objects_by_uid)),
    )


class TestObjectItemCriterion(unittest.TestCase):
    def test_equal_with_explicit_quantity_matches_exact_quantity(self) -> None:
        criterion = ObjectItemCriterion("PO=123,2")

        self.assertTrue(criterion.is_respected(_make_game_state({123: 2})))
        self.assertFalse(criterion.is_respected(_make_game_state({123: 1})))

    def test_equal_without_quantity_requires_any_positive_quantity(self) -> None:
        criterion = ObjectItemCriterion("PO=123")

        self.assertTrue(criterion.is_respected(_make_game_state({123: 2})))
        self.assertFalse(criterion.is_respected(_make_game_state({})))

    def test_different_without_quantity_requires_item_to_be_absent(self) -> None:
        criterion = ObjectItemCriterion("PO!123")

        self.assertTrue(criterion.is_respected(_make_game_state({})))
        self.assertFalse(criterion.is_respected(_make_game_state({123: 1})))

    def test_superior_uses_explicit_quantity_threshold(self) -> None:
        criterion = ObjectItemCriterion("PO>123,2")

        self.assertTrue(criterion.is_respected(_make_game_state({123: 3})))
        self.assertFalse(criterion.is_respected(_make_game_state({123: 2})))

    def test_inferior_uses_explicit_quantity_threshold(self) -> None:
        criterion = ObjectItemCriterion("PO<123,2")

        self.assertTrue(criterion.is_respected(_make_game_state({123: 1})))
        self.assertFalse(criterion.is_respected(_make_game_state({123: 2})))
