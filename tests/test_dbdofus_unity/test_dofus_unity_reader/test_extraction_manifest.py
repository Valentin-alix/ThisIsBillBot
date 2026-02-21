from pathlib import Path

from DBDofusUnity.dofus_unity_reader.extraction_manifest import ExtractionManifest


def test_manifest_marks_a_source_with_no_required_exports_as_up_to_date(tmp_path: Path) -> None:
    source_path = tmp_path / "unused.bundle"
    source_path.write_bytes(b"source")
    manifest = ExtractionManifest(tmp_path / "manifest.json")

    manifest.mark_success(source_path, output_paths=[])

    assert manifest.is_up_to_date(source_path)
