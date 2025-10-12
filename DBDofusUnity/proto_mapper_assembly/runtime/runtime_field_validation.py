from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, DumpCSMessageField
from DBDofusUnity.proto_mapper_assembly.interfaces.runtime import FieldValidatorRuntimeMetadata
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore
from DBDofusUnity.proto_mapper_assembly.validators.field_validators import (
    VALIDATORS_BY_NON_OBF_MESSAGE_NAME,
    ValidatorFn,
)

_DEFAULT_RUNTIME_CONTAINER_VALUES: tuple[dict[object, object], list[object]] = ({}, [])
_DEFAULT_RUNTIME_SCALAR_VALUES: tuple[None | int | bool | str, ...] = (None, 0, False, "")
_RUNTIME_METADATA_FIELD_NAMES: frozenset[str] = frozenset({"capture_sequence"})


def is_runtime_compatible_field_pair(
    *,
    non_obf_field: DumpCSMessageField,
    obf_field: DumpCSMessageField,
    non_obf_message: DumpCSMessage,
    obf_message: DumpCSMessage,
    obf_messages_by_cls: Mapping[str, DumpCSMessage],
    runtime_data_store: RuntimeDataStore | None,
) -> FieldValidatorRuntimeMetadata:
    if runtime_data_store is None:
        return FieldValidatorRuntimeMetadata(did_validation_run=False, did_validation_failure=False)

    field_validators = _get_runtime_field_validator(
        message_name=non_obf_message.name,
        field_name=non_obf_field.clean_field_name,
    )
    if field_validators is None:
        return FieldValidatorRuntimeMetadata(did_validation_run=False, did_validation_failure=False)

    runtime_instances = runtime_data_store.get_normalized_content_for_obf_message(
        message=obf_message,
        obf_messages_by_cls=obf_messages_by_cls,
    )
    runtime_values = get_defined_runtime_values(runtime_instances, obf_field.clean_field_name)
    if not runtime_values:
        return FieldValidatorRuntimeMetadata(did_validation_run=False, did_validation_failure=False)

    failed_value = _find_first_invalid_runtime_field_value(runtime_values, field_validators)
    did_validation_failed = failed_value is not None
    return FieldValidatorRuntimeMetadata(
        did_validation_run=True,
        did_validation_failure=did_validation_failed,
        failed_value=failed_value,
    )


def build_runtime_field_validator_confidence(
    *,
    field_mapping: dict[str, str],
    obf_message: DumpCSMessage,
    obf_messages_by_cls: Mapping[str, DumpCSMessage],
    non_obf_message: DumpCSMessage,
    runtime_data_store: RuntimeDataStore,
    validated_non_obf_field_names: set[str],
) -> float | None:
    """Score how well a field mapping satisfies field-local runtime validators."""
    field_validators_by_name = VALIDATORS_BY_NON_OBF_MESSAGE_NAME.get(non_obf_message.name)
    if field_validators_by_name is None:
        return None

    runtime_instances = runtime_data_store.get_normalized_content_for_obf_message(
        message=obf_message,
        obf_messages_by_cls=obf_messages_by_cls,
    )
    if not runtime_instances:
        return None

    obf_field_name_by_non_obf_field_name = {
        non_obf_field_name: obf_field_name for obf_field_name, non_obf_field_name in field_mapping.items()
    }
    validators_executed = False
    for non_obf_field_name, field_validator in field_validators_by_name.items():
        if non_obf_field_name not in validated_non_obf_field_names:
            continue
        obf_field_name = obf_field_name_by_non_obf_field_name.get(non_obf_field_name)
        if obf_field_name is None:
            return 0.0

        runtime_values = get_defined_runtime_values(runtime_instances, obf_field_name)
        if not runtime_values:
            continue

        validators_executed = True
        if not _all_runtime_field_values_are_valid(runtime_values, field_validator):
            return 0.0

    return 1.0 if validators_executed else None


def _get_runtime_field_validator(
    *,
    message_name: str,
    field_name: str,
) -> ValidatorFn[Any] | None:
    validators_by_field = VALIDATORS_BY_NON_OBF_MESSAGE_NAME.get(message_name)
    if validators_by_field is None:
        return None
    return validators_by_field.get(field_name)


def collect_runtime_alive_field_names(
    instances: Sequence[Mapping[str, object]],
) -> frozenset[str]:
    """Return the set of field names that have at least one non-default runtime value."""
    alive: set[str] = set()
    for instance in instances:
        for field_name, raw_value in instance.items():
            if field_name in alive:
                continue
            if field_name in _RUNTIME_METADATA_FIELD_NAMES:
                continue
            if _is_default_runtime_value(raw_value):
                continue
            alive.add(field_name)
    return frozenset(alive)


def collect_validated_field_names(message_name: str) -> frozenset[str]:
    validators_by_field = VALIDATORS_BY_NON_OBF_MESSAGE_NAME.get(message_name)
    if validators_by_field is None:
        return frozenset()
    return frozenset(validators_by_field)


def get_defined_runtime_values(
    instances: Sequence[dict[str, object]],
    field_name: str,
) -> list[object]:
    defined_values: list[object] = []
    for instance in instances:
        if field_name not in instance:
            continue
        value = instance[field_name]
        if _is_default_runtime_value(value):
            continue
        defined_values.append(value)
    return defined_values


def _all_runtime_field_values_are_valid(
    values: Sequence[object],
    field_validator: ValidatorFn[Any],
) -> bool:
    return _find_first_invalid_runtime_field_value(values, field_validator) is None


def _find_first_invalid_runtime_field_value(
    values: Sequence[object],
    field_validator: ValidatorFn[Any],
) -> object | None:
    for value in values:
        try:
            if not field_validator(value):
                return value
        except (AttributeError, KeyError, TypeError, ValueError, OSError):
            return value
    return None


def _is_default_runtime_value(value: object) -> bool:
    if isinstance(value, (list, dict)):
        return value in _DEFAULT_RUNTIME_CONTAINER_VALUES
    return value in _DEFAULT_RUNTIME_SCALAR_VALUES
