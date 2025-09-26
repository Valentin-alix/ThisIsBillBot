from collections.abc import Mapping, Sequence

from proto_mapper_assembly.runtime.runtime_field_validation import collect_runtime_alive_field_names


class TestCollectRuntimeAliveFieldNames:
    def test_returns_field_with_non_default_value(self) -> None:
        instances = ({"a": 1, "b": 0},)
        assert collect_runtime_alive_field_names(instances) == frozenset({"a"})

    def test_filters_default_scalar_values(self) -> None:
        instances: Sequence[Mapping[str, object]] = ({"x": None, "y": 0, "z": False, "w": ""},)
        assert collect_runtime_alive_field_names(instances) == frozenset()

    def test_filters_default_container_values(self) -> None:
        instances: Sequence[Mapping[str, object]] = ({"items": [], "lookup": {}},)
        assert collect_runtime_alive_field_names(instances) == frozenset()

    def test_aggregates_across_instances(self) -> None:
        instances: Sequence[Mapping[str, object]] = (
            {"a": 0, "b": 0},
            {"a": 7, "b": 0},
            {"a": 0, "b": "value"},
        )
        assert collect_runtime_alive_field_names(instances) == frozenset({"a", "b"})

    def test_empty_instances_returns_empty_set(self) -> None:
        assert collect_runtime_alive_field_names(()) == frozenset()
