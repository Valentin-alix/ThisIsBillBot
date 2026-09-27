from pathlib import Path

import pytest

from tests.fixtures.proto_mapper.field_builders import dump_field
from tests.fixtures.proto_mapper.runtime_store import seed_runtime_content

from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_field_validation import (
    is_runtime_compatible_field_pair,
    get_runtime_validator_values,
)
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore
from DBDofusUnity.proto_mapper_assembly.helpers.utils import strict_validate_call
from DBDofusUnity.proto_mapper_assembly.validators.field_validators import VALIDATORS_BY_NON_OBF_MESSAGE_NAME


def test_runtime_validators_keep_empty_lists_but_skip_other_defaults() -> None:
    assert get_runtime_validator_values(
        [{"empty_list": [], "zero": 0}, {"empty_list": [1], "zero": 2}],
        "empty_list",
    ) == [[], [1]]
    assert get_runtime_validator_values(
        [{"empty_list": [], "zero": 0}, {"empty_list": [1], "zero": 2}],
        "zero",
    ) == [2]


def test_spells_event_field_validators_check_empty_and_non_empty_lists(
    runtime_data_store: RuntimeDataStore,
    tmp_path: Path,
) -> None:
    seed_runtime_content(
        tmp_path,
        {"hnl": [{"fmuv": [{"fmuh": 13108, "fmul": 1}], "fmux": []}]},
    )
    obf_message = DumpCSMessage(file_descriptor="GameReflection", name="hnl")
    non_obf_message = DumpCSMessage(file_descriptor="SpellReflection", name="SpellsEvent")
    obf_messages_by_cls = {"hnl": obf_message}

    def check_pair(obf_field_name: str, non_obf_field_name: str) -> tuple[bool, bool]:
        result = is_runtime_compatible_field_pair(
            non_obf_field=dump_field(
                non_obf_field_name,
                non_obf_field_name,
                1,
                FieldCategoryEnum.REPEATED,
            ),
            obf_field=dump_field(obf_field_name, obf_field_name, 1, FieldCategoryEnum.REPEATED),
            non_obf_message=non_obf_message,
            obf_message=obf_message,
            obf_messages_by_cls=obf_messages_by_cls,
            runtime_data_store=runtime_data_store,
        )
        return result.did_validation_run, result.did_validation_failure

    assert check_pair("fmuv", "human_spells") == (True, False)
    assert check_pair("fmuv", "mutant_spells") == (True, True)
    assert check_pair("fmux", "human_spells") == (True, True)
    assert check_pair("fmux", "mutant_spells") == (True, False)


@pytest.mark.parametrize("error", [None, AttributeError, KeyError, TypeError, ValueError, OSError])
def test_runtime_validation_rejects_invalid_input_but_propagates_internal_errors(
    runtime_data_store: RuntimeDataStore,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    error: type[Exception] | None,
) -> None:
    @strict_validate_call
    def validate(value: int) -> bool:
        if error is not None:
            raise error("internal validator failure")
        return value > 0

    monkeypatch.setitem(VALIDATORS_BY_NON_OBF_MESSAGE_NAME, "TestMessage", {"value": validate})
    seed_runtime_content(tmp_path, {"hnl": [{"fmuv": "invalid" if error is None else 123}]})
    obf_message = DumpCSMessage(file_descriptor="GameReflection", name="hnl")

    def check_pair():
        return is_runtime_compatible_field_pair(
            non_obf_field=dump_field("value", "value", 1, FieldCategoryEnum.NUMBER),
            obf_field=dump_field("fmuv", "fmuv", 1, FieldCategoryEnum.NUMBER),
            non_obf_message=DumpCSMessage(file_descriptor="TestReflection", name="TestMessage"),
            obf_message=obf_message,
            obf_messages_by_cls={"hnl": obf_message},
            runtime_data_store=runtime_data_store,
        )

    if error is not None:
        with pytest.raises(error, match="internal validator failure"):
            check_pair()
    else:
        result = check_pair()
        assert result.did_validation_run
        assert result.did_validation_failure
        assert result.failed_value == "invalid"
