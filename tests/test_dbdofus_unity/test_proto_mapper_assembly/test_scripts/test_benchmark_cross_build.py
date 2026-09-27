from DBDofusUnity.proto_mapper_assembly.interfaces.pinned_pairs import PinnedPair, PinnedPairsConfig
from DBDofusUnity.proto_mapper_assembly.scripts.benchmark_cross_build import _pins_for_run


def test_leave_one_pin_out_removes_only_the_selected_pair() -> None:
    pins = PinnedPairsConfig(
        pairs=[
            PinnedPair(obf="obf.First", non_obf=".non.ObfFirst"),
            PinnedPair(obf="obf.Second", non_obf="non.ObfSecond"),
        ]
    )

    remaining = _pins_for_run(pins, ".NON.OBFFIRST")

    assert [pair.non_obf for pair in remaining.pairs] == ["non.ObfSecond"]
    assert len(pins.pairs) == 2


def test_regular_benchmark_keeps_the_original_pin_config() -> None:
    pins = PinnedPairsConfig(pairs=[PinnedPair(obf="obf.First", non_obf="non.ObfFirst")])

    assert _pins_for_run(pins, None) is pins
