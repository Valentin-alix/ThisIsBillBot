from DBDofusUnity.tests.test_proto_mapper_assembly.fixture import ida_environment  # noqa: F401

from proto_mapper_assembly.scripts.ida_tracer_lib.simulation.cfg_stats import build_cfg_stats
from proto_mapper_assembly.scripts.ida_tracer_lib.state.basic_block import BasicBlock, FunctionScanPlan


def _scan_plan(successors_by_block: dict[int, tuple[int, ...]], *, entry: int) -> FunctionScanPlan:
    blocks = {
        block_start: BasicBlock(start_ea=block_start, end_ea=block_start + 1, successors=successors)
        for block_start, successors in successors_by_block.items()
    }
    return FunctionScanPlan(
        blocks=blocks,
        predecessors={block_start: () for block_start in blocks},
        entry_block_start=entry,
        instructions_by_block={block_start: () for block_start in blocks},
    )


class TestCfgStats:
    def test_straight_line_function_has_no_back_edge(self) -> None:
        stats = build_cfg_stats(_scan_plan({1: (2,), 2: (3,), 3: ()}, entry=1))

        assert stats.basic_block_count == 3
        assert stats.edge_count == 2
        assert stats.back_edge_count == 0
        assert stats.max_block_depth == 2
        assert stats.cyclomatic_complexity == 1

    def test_loop_is_reported_as_a_back_edge(self) -> None:
        stats = build_cfg_stats(_scan_plan({1: (2,), 2: (3,), 3: (2,)}, entry=1))

        assert stats.back_edge_count == 1
        assert stats.cyclomatic_complexity == 2

    def test_diamond_join_is_not_a_back_edge(self) -> None:
        stats = build_cfg_stats(_scan_plan({1: (2, 3), 2: (4,), 3: (4,), 4: ()}, entry=1))

        # Both branches reconvene on block 4: that is a forward edge, not a loop.
        assert stats.back_edge_count == 0
        assert stats.edge_count == 4
        assert stats.max_block_depth == 2

    def test_successors_outside_the_function_are_ignored(self) -> None:
        stats = build_cfg_stats(_scan_plan({1: (2, 999), 2: ()}, entry=1))

        assert stats.edge_count == 1
        assert stats.basic_block_count == 2

    def test_single_block_function(self) -> None:
        stats = build_cfg_stats(_scan_plan({1: ()}, entry=1))

        assert stats.basic_block_count == 1
        assert stats.edge_count == 0
        assert stats.back_edge_count == 0
        assert stats.max_block_depth == 0
