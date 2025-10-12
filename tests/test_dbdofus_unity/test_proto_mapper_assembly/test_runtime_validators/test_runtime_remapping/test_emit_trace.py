from DBDofusUnity.proto_mapper_assembly.interfaces.runtime import RuntimeRemappingTraceEvent
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_remapping import _emit_trace


class TestEmitTrace:
    def test_noop_when_trace_handler_is_none(self) -> None:
        # Should not raise
        _emit_trace(
            trace_handler=None,
            path=("a", "b"),
            message="test_msg",
            mapping_failure_origin=None,
        )

    def test_calls_handler_with_event(self) -> None:
        events: list[RuntimeRemappingTraceEvent] = []
        _emit_trace(
            trace_handler=events.append,
            path=("x",),
            message="something_wrong",
            mapping_failure_origin="child",
        )

        assert len(events) == 1
        assert events[0].kind == "failure"
        assert events[0].path == ("x",)
        assert events[0].message == "something_wrong"
        assert events[0].mapping_failure_origin == "child"
