import pytest

from src.core.engine.movements.world.criterions.items_criterion.object_item_criterion import (
    ObjectItemCriterion,
)
from tests.fixtures.inventory import make_criterion_context_with_inventory


@pytest.mark.parametrize(
    ("criterion_str", "inventory", "expected"),
    [
        ("PO=123,2", {123: 2}, True),
        ("PO=123,2", {123: 1}, False),
        ("PO=123", {123: 2}, True),
        ("PO=123", {}, False),
        ("PO!123", {}, True),
        ("PO!123", {123: 1}, False),
        ("PO>123,2", {123: 3}, True),
        ("PO>123,2", {123: 2}, False),
        ("PO<123,2", {123: 1}, True),
        ("PO<123,2", {123: 2}, False),
    ],
)
def test_object_item_criterion(
    criterion_str: str,
    inventory: dict[int, int],
    expected: bool,
) -> None:
    criterion = ObjectItemCriterion(criterion_str)

    assert (
        criterion.is_respected(make_criterion_context_with_inventory(inventory))
        is expected
    )
