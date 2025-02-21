from unittest.mock import MagicMock

import pytest

from src.core.engine.movements.world.edge import (
    _get_transition_to_valid_criterions,
)
from tests.fixtures.map_world import make_transition


class TestEdge:
    def test_get_transition_to_valid_criterions_keeps_empty_and_skips_invalid_criterions(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        empty_transition = make_transition("", 1)
        invalid_transition = make_transition("ZZ>0", 2)
        valid_transition = make_transition("Ad>0", 3)

        criterion = MagicMock()
        mock_group_criterion = MagicMock(return_value=criterion)

        monkeypatch.setattr(
            "src.core.engine.movements.world.edge.GroupItemCriterion",
            mock_group_criterion,
        )

        result = _get_transition_to_valid_criterions(
            (empty_transition, invalid_transition, valid_transition),
        )

        assert result == [
            (empty_transition, None),
            (valid_transition, criterion),
        ]
        mock_group_criterion.assert_called_once_with("Ad>0")
