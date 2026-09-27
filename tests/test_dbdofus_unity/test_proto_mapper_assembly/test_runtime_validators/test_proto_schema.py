from pathlib import Path

import pytest

from DBDofusUnity.proto_mapper_assembly.runtime.proto_schema import get_obfuscated_proto_schema_fingerprint


def test_proto_schema_fingerprint_is_stable_and_tracks_schema_content(tmp_path: Path) -> None:
    first = tmp_path / "first.proto"
    second = tmp_path / "nested" / "second.proto"
    second.parent.mkdir()
    first.write_text("syntax = 'proto3';", encoding="utf-8")
    second.write_text("message Second {}", encoding="utf-8")

    original_fingerprint = get_obfuscated_proto_schema_fingerprint(tmp_path)
    assert get_obfuscated_proto_schema_fingerprint(tmp_path) == original_fingerprint

    second.write_text("message Second { int32 value = 1; }", encoding="utf-8")

    assert get_obfuscated_proto_schema_fingerprint(tmp_path) != original_fingerprint


def test_proto_schema_fingerprint_requires_at_least_one_proto_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="No obfuscated protobuf schema files"):
        get_obfuscated_proto_schema_fingerprint(tmp_path)
