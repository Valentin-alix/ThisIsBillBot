from pathlib import Path

import pytest
from msgspec import Struct

from DBDofusUnity.dofus_unity_reader.generator.data_cleaning import clean_data_to_output


class SampleData(Struct, frozen=True):
    id: int
    name: str


def test_clean_data_to_output_does_not_rewrite_identical_content(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_path = tmp_path / "sample.json"
    output_path.write_text('{\n  "id": 1,\n  "name": "test"\n}\n', encoding="utf-8")
    write_calls: list[Path] = []
    original_write_text = Path.write_text

    def spy_write_text(
        self: Path,
        data: str,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> int:
        write_calls.append(self)
        return original_write_text(self, data, encoding=encoding, errors=errors, newline=newline)

    monkeypatch.setattr(Path, "write_text", spy_write_text)

    clean_data_to_output(SampleData, output_path)

    assert write_calls == []


def test_clean_data_to_output_rewrites_when_format_changes(tmp_path: Path) -> None:
    output_path = tmp_path / "sample.json"
    output_path.write_text('{"id":1,"name":"test"}', encoding="utf-8")

    clean_data_to_output(SampleData, output_path)

    assert output_path.read_text(encoding="utf-8") == '{\n  "id": 1,\n  "name": "test"\n}\n'
