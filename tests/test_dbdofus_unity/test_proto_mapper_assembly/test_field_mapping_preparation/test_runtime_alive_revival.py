from pathlib import Path

import pytest

from tests.fixtures.proto_mapper.message_builders import (
    make_field_mapping_context,
    make_message_signature,
    make_non_obf_signature,
    make_obf_message_with_unmapped_field,
    prepare_field_mapping_context_for_test,
)
from tests.fixtures.proto_mapper.runtime_store import seed_runtime_content

from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore


@pytest.mark.parametrize(
    "runtime_content",
    [
        [{"sleeper": 42}],
        [{"sleeper": 0}, {"sleeper": ""}, {"sleeper": []}, {"sleeper": None}],
        [],
    ],
    ids=("non-default", "default-only", "no-captures"),
)
class TestRuntimeAliveRevival:
    def test_declared_obf_field_is_exported_regardless_of_runtime_values(
        self,
        runtime_content: list[dict[str, object]],
        runtime_data_store: RuntimeDataStore,
        tmp_path: Path,
    ) -> None:
        obf_message, sleeping_field = make_obf_message_with_unmapped_field()
        obf_signature = make_message_signature(obf_message, live_field_keys=frozenset())
        non_obf_signature = make_non_obf_signature()
        seed_runtime_content(tmp_path, {obf_message.composed_name: runtime_content})

        context = prepare_field_mapping_context_for_test(
            non_obf_signature=non_obf_signature,
            obf_signature=obf_signature,
            field_mapping_context=make_field_mapping_context(runtime_data_store),
        )

        assert sleeping_field in context.obf.fields
