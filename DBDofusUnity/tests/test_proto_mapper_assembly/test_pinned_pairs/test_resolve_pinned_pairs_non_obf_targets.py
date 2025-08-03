import pytest

from proto_mapper_assembly.controllers.pinned_pairs import resolve_pinned_pairs_non_obf_targets

from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.helper_builders import (
    PinnedResolveCase,
    PinnedResolveErrorCase,
    pinned_resolve_case,
    pinned_resolve_error_case,
)

RESOLVE_CASES: tuple[PinnedResolveCase, ...] = (
    pinned_resolve_case("root_non_obf"),
    pinned_resolve_case("nested_types_non_obf"),
    pinned_resolve_case("obf_static_container"),
)

ERROR_CASES: tuple[PinnedResolveErrorCase, ...] = (
    pinned_resolve_error_case("unknown"),
    pinned_resolve_error_case("ambiguous"),
)


class TestResolvePinnedPairsNonObfTargets:
    @pytest.mark.parametrize("case", RESOLVE_CASES)
    def test_resolves_aliases(self, case: PinnedResolveCase) -> None:
        result = resolve_pinned_pairs_non_obf_targets(
            pinned_pairs=case.pinned_pairs,
            obf_messages_by_cls=case.obf_messages_by_cls,
            non_obf_messages_by_cls=case.non_obf_messages_by_cls,
        )

        assert result.pairs[0].obf == case.expected_obf
        assert result.pairs[0].non_obf == case.expected_non_obf

    @pytest.mark.parametrize("case", ERROR_CASES)
    def test_raises_for_unresolvable_non_obf_alias(self, case: PinnedResolveErrorCase) -> None:
        with pytest.raises(ValueError, match=case.match):
            resolve_pinned_pairs_non_obf_targets(
                pinned_pairs=case.pinned_pairs,
                obf_messages_by_cls=case.obf_messages_by_cls,
                non_obf_messages_by_cls=case.non_obf_messages_by_cls,
            )
