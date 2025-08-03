from typing import Any

import pytest
from datas.protos.non_obf.game.bak_pb2 import BidAction

from proto_mapper_assembly.field_mapping.pulp.constraints import has_applicable_constraints
from proto_mapper_assembly.validators.set_validators import (
    validator_bak_action_event,
    validator_bak_action_request,
    validator_exchange_requested_trade_event,
    validator_exchange_started_with_pods_event,
    validator_subscribe_multiple_channel_request,
)

EXCHANGE_REQUEST_CASES: list[tuple[dict[str, Any], bool]] = [
    ({"source_id": 10, "target_id": 11}, True),
    ({"source_id": 10, "target_id": 10}, False),
]


@pytest.mark.parametrize(("payload", "expected"), EXCHANGE_REQUEST_CASES)
def test_exchange_requested_trade(payload: dict[str, Any], expected: bool) -> None:
    assert validator_exchange_requested_trade_event(payload) is expected


EXCHANGE_STARTED_CASES: list[tuple[dict[str, Any], bool]] = [
    (
        {
            "first_character_max_weight": 100,
            "first_character_current_weight": 50,
            "second_character_max_weight": 10,
            "second_character_current_weight": 20,
        },
        False,
    ),
    (
        {
            "first_character_max_weight": 5,
            "first_character_current_weight": 50,
            "second_character_max_weight": 10,
            "second_character_current_weight": 20,
        },
        False,
    ),
    (
        {
            "first_character_max_weight": 500,
            "first_character_current_weight": 50,
            "second_character_max_weight": 1000,
            "second_character_current_weight": 200,
        },
        True,
    ),
]


@pytest.mark.parametrize(("payload", "expected"), EXCHANGE_STARTED_CASES)
def test_exchange_started_with_pods(payload: dict[str, Any], expected: bool) -> None:
    assert validator_exchange_started_with_pods_event(payload) is expected


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"channel_enabled": [1, 2], "channel_disabled": [3, 4]}, True),
        ({"channel_enabled": [1], "channel_disabled": []}, True),
        ({"channel_enabled": [1, 2], "channel_disabled": [2, 3]}, False),
        ({"channel_enabled": [], "channel_disabled": []}, False),
    ],
)
def test_subscribe_multiple_channel_request(payload: dict[str, Any], expected: bool) -> None:
    assert validator_subscribe_multiple_channel_request(payload) is expected


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        (
            {
                "kamas": 450_000,
                "ogrines": 1_500,
                "rate": 300,
                "bid_action": BidAction.BID_BUY_OGRINE,
            },
            True,
        ),
        (
            {
                "kamas": 449_999,
                "ogrines": 1_500,
                "rate": 300,
                "bid_action": "BID_BUY_OGRINE",
            },
            False,
        ),
        (
            {
                "kamas": 1,
                "ogrines": 1_500,
                "rate": 300,
                "bid_action": BidAction.BID_BUY_KAMA,
            },
            True,
        ),
    ],
)
def test_bak_action_request(payload: dict[str, Any], expected: bool) -> None:
    assert validator_bak_action_request(payload) is expected


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        (
            {
                "kamas": 450_000,
                "amount": 1_500,
                "rate": 300,
                "bid_action": BidAction.BID_BUY_OGRINE,
            },
            True,
        ),
        (
            {
                "kamas": 450_000,
                "amount": 1_499,
                "rate": 300,
                "bid_action": "BID_BUY_OGRINE",
            },
            False,
        ),
        (
            {
                "kamas": 1,
                "amount": 1_500,
                "rate": 300,
                "bid_action": BidAction.BID_BUY_KAMA,
            },
            True,
        ),
    ],
)
def test_bak_action_event(payload: dict[str, Any], expected: bool) -> None:
    assert validator_bak_action_event(payload) is expected


def test_bak_action_validators_are_applied_by_field_mapper() -> None:
    assert has_applicable_constraints("BakActionRequest") is True
    assert has_applicable_constraints("BakActionEvent") is True
