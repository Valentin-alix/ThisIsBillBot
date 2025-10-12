from typing import Any

import pytest

from DBDofusUnity.proto_mapper_assembly.field_mapping.pulp.constraints import has_applicable_constraints
from DBDofusUnity.proto_mapper_assembly.validators.set_validators import (
    validator_character_characteristic_detailed_usable,
    validator_character_characteristic_upgrade_request,
    validator_update_life_points_event,
)

CHARACTERISTIC_CASES: list[tuple[dict[str, Any], bool]] = [
    (
        {
            "used": 3,
            "base": 6,
            "objects_and_mount_bonus": 0,
            "alignment_gift_bonus": 0,
            "additional": 0,
            "context_modification": 0,
        },
        True,
    ),
    (
        {
            "used": 8,
            "base": 6,
            "objects_and_mount_bonus": 1,
            "alignment_gift_bonus": 0,
            "additional": 0,
            "context_modification": 0,
        },
        False,
    ),
]


@pytest.mark.parametrize(("payload", "expected"), CHARACTERISTIC_CASES)
def test_characteristic_validators(payload: dict[str, Any], expected: bool) -> None:
    assert validator_character_characteristic_detailed_usable(payload) is expected


def test_characteristic_usable_validator_is_applied_by_field_mapper() -> None:
    assert has_applicable_constraints("CharacterCharacteristicDetailedUsable") is True


LIFE_POINTS_CASES: list[tuple[dict[str, Any], bool]] = [
    ({"max_life_points": 10, "life_points": 9}, True),
    ({"max_life_points": 4, "life_points": 10}, False),
]


@pytest.mark.parametrize(("payload", "expected"), LIFE_POINTS_CASES)
def test_update_life_points(payload: dict[str, Any], expected: bool) -> None:
    assert validator_update_life_points_event(payload) is expected


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        (
            {
                "strength": 0,
                "vitality": 10,
                "wisdom": 0,
                "chance": 0,
                "agility": 0,
                "intelligence": 0,
            },
            True,
        ),
        (
            {
                "strength": 0,
                "vitality": 992,
                "wisdom": 0,
                "chance": 0,
                "agility": 0,
                "intelligence": 0,
            },
            False,
        ),
        (
            {
                "strength": 0,
                "vitality": 0,
                "wisdom": 995,
                "chance": 0,
                "agility": 0,
                "intelligence": 0,
            },
            False,
        ),
        (
            {
                "strength": 0,
                "vitality": 0,
                "wisdom": 0,
                "chance": 0,
                "agility": 0,
                "intelligence": 0,
            },
            False,
        ),
        (
            {
                "strength": 100,
                "vitality": 5,
                "wisdom": 0,
                "chance": 0,
                "agility": 0,
                "intelligence": 0,
            },
            True,
        ),
        (
            {
                "strength": -1,
                "vitality": 10,
                "wisdom": 0,
                "chance": 0,
                "agility": 0,
                "intelligence": 0,
            },
            False,
        ),
        (
            {
                "strength": 0,
                "vitality": 0,
                "wisdom": 0,
                "chance": 0,
                "agility": 0,
                "intelligence": 992,
            },
            True,
        ),
        (
            {
                "strength": 0,
                "vitality": 0,
                "wisdom": 993,
                "chance": 0,
                "agility": 0,
                "intelligence": 0,
            },
            True,
        ),
    ],
)
def test_characteristic_upgrade_request(payload: dict[str, Any], expected: bool) -> None:
    assert validator_character_characteristic_upgrade_request(payload) is expected
