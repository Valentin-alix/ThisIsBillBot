from typing import Any

import pytest

from DBDofusUnity.proto_mapper_assembly.validators.set_validators import validator_game_action_fight_event

FIGHT_CASES: list[tuple[dict[str, Any], bool]] = [
    ({"source_id": -1}, True),
    ({"source_id": 1}, False),
    ({"source_id": 1, "slide": {"bonjour": 3}}, True),
]


@pytest.mark.parametrize(("payload", "expected"), FIGHT_CASES)
def test_game_action_fight(payload: dict[str, Any], expected: bool) -> None:
    assert validator_game_action_fight_event(payload) is expected
