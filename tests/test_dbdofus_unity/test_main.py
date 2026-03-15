import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from pydantic import ValidationError

from DBDofusUnity import main
from DBDofusUnity.main import build_argument_parser

_RUN_PIPELINE = "DBDofusUnity.proto_mapper_assembly.pipeline.run_pipeline"


@pytest.fixture
def update_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    release = tmp_path / "release.json"
    release.write_text(json.dumps({"location": str(tmp_path), "version": "6.0_3.6.11.15"}))
    version = tmp_path / "VERSION"
    version.write_text("6.0_3.6.10.11\n", encoding="utf-8")
    monkeypatch.setattr(main, "RELEASE_JSON_PATH", str(release))
    monkeypatch.setattr(main, "OBF_GAME_DIR", tmp_path)
    monkeypatch.setattr(main, "VERSION_PATH", version)
    return release, version


def test_update_maj_writes_version_after_success(update_files: tuple[Path, Path]) -> None:
    _, version = update_files
    previous = version.read_bytes()

    def check_previous_version(*args: object, **kwargs: object) -> None:
        assert version.read_bytes() == previous

    with (
        patch("DBDofusUnity.dofus_unity_reader.get_datas.update_all_datas", side_effect=check_previous_version),
        patch.object(main, "update_protos", side_effect=check_previous_version),
    ):
        main.main(["update-maj"])

    assert version.read_text(encoding="utf-8") == "6.0_3.6.11.15\n"


@pytest.mark.parametrize("failed_step", ["data", "protos"])
def test_update_maj_preserves_version_on_failure(update_files: tuple[Path, Path], failed_step: str) -> None:
    _, version = update_files
    previous = version.read_bytes()
    with (
        patch("DBDofusUnity.dofus_unity_reader.get_datas.update_all_datas") as data,
        patch.object(main, "update_protos") as protos,
    ):
        failed: Mock = data if failed_step == "data" else protos
        failed.side_effect = RuntimeError("Update failed")
        with pytest.raises(RuntimeError, match="Update failed"):
            main.main(["update-maj"])

    assert version.read_bytes() == previous


@pytest.mark.parametrize("invalid_release", ["missing", "broken", "version", "location"])
def test_update_maj_rejects_invalid_release_before_updates(
    update_files: tuple[Path, Path], invalid_release: str,
) -> None:
    release, version = update_files
    previous = version.read_bytes()
    if invalid_release == "missing":
        release.unlink()
    elif invalid_release == "broken":
        release.write_text("broken")
    else:
        release.write_text(json.dumps({
            "location": str(release.parent / "other" if invalid_release == "location" else release.parent),
            "version": "1.0.4" if invalid_release == "version" else "6.0_3.6.11.15",
        }))
    with (
        patch("DBDofusUnity.dofus_unity_reader.get_datas.update_all_datas") as data,
        patch.object(main, "update_protos") as protos,
        pytest.raises((OSError, ValidationError, RuntimeError)),
    ):
        main.main(["update-maj"])

    data.assert_not_called()
    protos.assert_not_called()
    assert version.read_bytes() == previous


def test_update_maj_preserves_version_if_game_changes(update_files: tuple[Path, Path]) -> None:
    release, version = update_files
    previous = version.read_bytes()

    def change_game_version(*, use_obf: bool) -> None:
        release.write_text(json.dumps({"location": str(release.parent), "version": "6.0_3.6.12.1"}))

    with (
        patch("DBDofusUnity.dofus_unity_reader.get_datas.update_all_datas"),
        patch.object(main, "update_protos", side_effect=change_game_version),
        pytest.raises(RuntimeError, match="changed during update-maj"),
    ):
        main.main(["update-maj"])

    assert version.read_bytes() == previous


class TestSynchronizeProtosCommand:
    def test_synchronize_protos_command_chains_all_steps(self) -> None:
        arguments = build_argument_parser().parse_args(["synchronize-protos"])

        with (
            patch("DBDofusUnity.main.gen_python") as gen_python,
            patch("DBDofusUnity.main.validate_unknown_names") as validate_unknown_names,
            patch("DBDofusUnity.main.synchronize_non_obf_mapping_artifacts") as synchronize_artifacts,
            patch("DBDofusUnity.main.run_export_signature_overrides") as run_export_signature_overrides,
            patch(_RUN_PIPELINE) as run_pipeline,
        ):
            arguments.handler(arguments)

        gen_python.assert_called_once_with(arguments)
        validate_unknown_names.assert_called_once_with()
        synchronize_artifacts.assert_called_once_with()
        run_export_signature_overrides.assert_called_once_with()
        run_pipeline.assert_called_once_with(do_load_pinned_pair=True)
