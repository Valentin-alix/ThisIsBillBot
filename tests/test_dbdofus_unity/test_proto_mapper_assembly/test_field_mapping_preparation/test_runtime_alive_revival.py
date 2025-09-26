from pathlib import Path

from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.message_builders import (
    make_field_mapping_context,
    make_message_signature,
    make_non_obf_signature,
    make_obf_message_with_unmapped_field,
    prepare_field_mapping_context_for_test,
)
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.runtime_store import seed_runtime_content

from proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore


class TestRuntimeAliveRevival:
    def test_obf_field_is_included_with_non_default_runtime_value(
        self,
        runtime_data_store: RuntimeDataStore,
        tmp_path: Path,
    ) -> None:
        obf_message, sleeping_field = make_obf_message_with_unmapped_field()
        obf_signature = make_message_signature(obf_message, live_field_keys=frozenset())
        non_obf_signature = make_non_obf_signature()
        seed_runtime_content(tmp_path, {obf_message.composed_name: [{"sleeper": 42}]})

        context = prepare_field_mapping_context_for_test(
            non_obf_signature=non_obf_signature,
            obf_signature=obf_signature,
            field_mapping_context=make_field_mapping_context(runtime_data_store),
        )

        assert sleeping_field in context.obf.fields

    def test_obf_field_is_exported_when_runtime_only_has_default_values(
        self,
        runtime_data_store: RuntimeDataStore,
        tmp_path: Path,
    ) -> None:
        obf_message, sleeping_field = make_obf_message_with_unmapped_field()
        obf_signature = make_message_signature(obf_message, live_field_keys=frozenset())
        non_obf_signature = make_non_obf_signature()
        seed_runtime_content(
            tmp_path,
            {
                obf_message.composed_name: [
                    {"sleeper": 0},
                    {"sleeper": ""},
                    {"sleeper": []},
                    {"sleeper": None},
                ]
            },
        )

        context = prepare_field_mapping_context_for_test(
            non_obf_signature=non_obf_signature,
            obf_signature=obf_signature,
            field_mapping_context=make_field_mapping_context(runtime_data_store),
        )

        assert sleeping_field in context.obf.fields

    def test_obf_field_is_exported_when_runtime_store_is_empty(
        self,
        runtime_data_store: RuntimeDataStore,
    ) -> None:
        obf_message, sleeping_field = make_obf_message_with_unmapped_field()
        obf_signature = make_message_signature(obf_message, live_field_keys=frozenset())
        non_obf_signature = make_non_obf_signature()

        context = prepare_field_mapping_context_for_test(
            non_obf_signature=non_obf_signature,
            obf_signature=obf_signature,
            field_mapping_context=make_field_mapping_context(runtime_data_store),
        )

        assert sleeping_field in context.obf.fields
