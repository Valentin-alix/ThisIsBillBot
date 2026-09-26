from pathlib import Path

import pytest

from DBDofusUnity.proto_mapper_assembly.interfaces.game_mappings import GameMappingsDocument
from DBDofusUnity.proto_mapper_assembly.interfaces.pinned_pairs import PinnedPair, PinnedPairsConfig
from DBDofusUnity.proto_mapper_assembly.scripts import benchmark_cross_build as benchmark
from tests.fixtures.proto_mapper.pipeline_builders import detailed_game_mapping_entry


def test_required_fields_detect_wrong_message_and_missing_reference(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract_path = tmp_path / "contract.json"
    contract_path.write_text(
        '{"version":3,"thresholds":{"message_score":0.5,"match_margin":0.05,"field_score":0.5},'
        '"messages":[{"message":".Clear","fields":["value","unknown"]}]}',
        encoding="utf-8",
    )
    monkeypatch.setattr(benchmark, "AUTO_MODE_MAPPING_CONTRACT_FILE", contract_path)
    reference = GameMappingsDocument(root={".Clear": detailed_game_mapping_entry("old", {"x": "value"})})
    candidate = GameMappingsDocument(root={".Clear": detailed_game_mapping_entry("wrong", {"x": "value"})})
    messages, unverified, fields = benchmark._score_current_requirements(
        reference_document=reference,
        candidate_document=candidate,
        pinned_pairs=PinnedPairsConfig(pairs=[]),
    )
    assert not messages[0].is_recovered
    assert unverified == ()
    assert [(field.field, field.status) for field in fields] == [
        ("value", "wrong"),
        ("unknown", "unverified"),
    ]

    candidate = GameMappingsDocument(root={".Clear": detailed_game_mapping_entry("new", {"y": "value"})})
    messages, _, fields = benchmark._score_current_requirements(
        reference_document=reference,
        candidate_document=candidate,
        pinned_pairs=PinnedPairsConfig(
            pairs=[
                PinnedPair(
                    obf="new_full",
                    non_obf="Clear",
                    field_mapping_by_obf={"y": "value"},
                )
            ]
        ),
    )
    assert messages[0].is_recovered
    assert fields[0].status == "correct"
    assert fields[0].reference_kind == "pin"
    assert fields[1].status == "unverified"


def test_missing_message_is_not_a_correct_field_match() -> None:
    outcome = benchmark.FieldOutcome(".Clear", "value", "a", None, "x", None, "pin")
    assert outcome.status == "unmapped"
