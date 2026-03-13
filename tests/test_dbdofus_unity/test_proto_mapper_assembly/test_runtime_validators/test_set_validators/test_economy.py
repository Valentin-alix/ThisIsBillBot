from typing import Any

import pulp
import pytest
from DBDofusUnity.datas.protos.non_obf.game.bak_pb2 import BidAction

from DBDofusUnity.proto_mapper_assembly.field_mapping.pulp.constraints import (
    SET_VALIDATOR_FIELD_GROUPS,
    build_ilp_validator_constraints,
    has_applicable_constraints,
)
from DBDofusUnity.proto_mapper_assembly.validators.set_validators import (
    validator_bak_action_event,
    validator_bak_action_request,
    validator_exchange_requested_trade_event,
    validator_subscribe_multiple_channel_request,
)
from tests.fixtures.proto_mapper.field_builders import scalar_field

EXCHANGE_REQUEST_CASES: list[tuple[dict[str, Any], bool]] = [
    ({"source_id": 10, "target_id": 11}, True),
    ({"source_id": 10, "target_id": 10}, False),
]


@pytest.mark.parametrize(("payload", "expected"), EXCHANGE_REQUEST_CASES)
def test_exchange_requested_trade(payload: dict[str, Any], expected: bool) -> None:
    assert validator_exchange_requested_trade_event(payload) is expected


@pytest.mark.parametrize("character", ["first", "second"])
@pytest.mark.parametrize(("weight", "expected"), [(50, True), (100, True), (150, False)])
def test_exchange_pods_constraints_accept_only_valid_weights(
    character: str, weight: int, expected: bool
) -> None:
    group = next(
        group
        for group in SET_VALIDATOR_FIELD_GROUPS
        if group.message_short_name == "ExchangeStartedWithPodsEvent"
        and group.field_names[0] == f"{character}_character_max_weight"
    )
    problem = pulp.LpProblem("exchange_pods")
    variables = {
        (i, j): pulp.LpVariable(f"x_{i}_{j}", cat="Binary") for i in range(2) for j in range(2)
    }
    build_ilp_validator_constraints(
        group=group,
        non_obf_fields=tuple(
            scalar_field(name, 0x10 + 4 * i) for i, name in enumerate(group.field_names)
        ),
        obf_fields=(scalar_field("max_", 0x10), scalar_field("cur_", 0x14)),
        runtime_instances=({"max": 100, "cur": weight},),
        lp_variable_by_idxs=variables,
        problem=problem,
    )
    for (i, j), variable in variables.items():
        variable.varValue = int(i == j)

    assert problem.valid() is expected


def test_validator_constraints_reject_missing_required_field() -> None:
    group = next(
        group
        for group in SET_VALIDATOR_FIELD_GROUPS
        if group.message_short_name == "ExchangeStartedWithPodsEvent"
    )
    with pytest.raises(KeyError, match="first_character_max_weight"):
        build_ilp_validator_constraints(
            group=group,
            non_obf_fields=(),
            obf_fields=(),
            runtime_instances=(),
            lp_variable_by_idxs={},
            problem=pulp.LpProblem("missing_field"),
        )


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
