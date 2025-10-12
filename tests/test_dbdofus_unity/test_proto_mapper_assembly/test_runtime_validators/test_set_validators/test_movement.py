from typing import Any

import pytest

from DBDofusUnity.proto_mapper_assembly.validators.set_validators import validator_exchange_positions, validator_slide

SLIDE_CASES: list[tuple[dict[str, Any], bool]] = [
    ({"start_cell": -1, "end_cell": -1}, False),
    ({"start_cell": 0, "end_cell": 0}, False),
    ({"start_cell": 10, "end_cell": 13}, True),
]


@pytest.mark.parametrize(("payload", "expected"), SLIDE_CASES)
def test_slide(payload: dict[str, Any], expected: bool) -> None:
    try:
        res = validator_slide(payload)
    except KeyError:
        res = False
    assert res is expected


EXCHANGE_POSITIONS_CASES: list[tuple[dict[str, Any], bool]] = [
    ({"caster_cell_id": 0, "target_cell_id": 0}, False),
    ({"caster_cell_id": 0, "target_cell_id": 559}, False),
    ({"caster_cell_id": -2, "target_cell_id": 0}, False),
]


@pytest.mark.parametrize(("payload", "expected"), EXCHANGE_POSITIONS_CASES)
def test_exchange_positions(payload: dict[str, Any], expected: bool) -> None:
    try:
        res = validator_exchange_positions(payload)
    except KeyError:
        res = False
    assert res is expected
