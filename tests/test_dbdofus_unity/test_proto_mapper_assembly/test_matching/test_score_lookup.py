from __future__ import annotations

import numpy as np
import pytest
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.matching_builders import simple_workspace

from proto_mapper_assembly.interfaces.message_pair import MatchPairKey
from proto_mapper_assembly.matching.score_lookup import (
    LazyScoreByPair,
    build_lazy_score_by_pair_lookup_from_matrix,
)


class TestScoreLookup:
    def test_lazy_score_by_pair_caches_values_and_raises_for_missing_key(self) -> None:
        calls: list[tuple[str, str]] = []

        def resolver(obf_cls: str, non_obf_cls: str) -> float:
            calls.append((obf_cls, non_obf_cls))
            if (obf_cls, non_obf_cls) == ("obf", "non"):
                return 0.42
            raise KeyError((obf_cls, non_obf_cls))

        lookup = LazyScoreByPair(resolver)

        assert lookup[MatchPairKey("obf", "non")] == 0.42
        assert lookup[MatchPairKey("obf", "non")] == 0.42
        assert calls == [("obf", "non")]

        with pytest.raises(KeyError):
            _ = lookup[MatchPairKey("missing", "non")]

    def test_build_lazy_score_by_pair_lookup_from_matrix_reads_from_matrix(self) -> None:
        workspace = simple_workspace(
            obf_classes=("obf",),
            non_obf_classes=("non",),
        )
        lookup = build_lazy_score_by_pair_lookup_from_matrix(
            workspace=workspace,
            scores_matrix=np.array([[0.25]]),
        )

        assert lookup[MatchPairKey("obf", "non")] == 0.25
        assert lookup[MatchPairKey("obf", "non")] == 0.25

        with pytest.raises(KeyError):
            _ = lookup[MatchPairKey("missing", "non")]
