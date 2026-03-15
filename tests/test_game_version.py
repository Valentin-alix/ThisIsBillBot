import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest
import requests

from src.services import game_version
from src.utils.runtime_support import RuntimeSetupError

VERSION = "6.0_3.6.10.11"
NEW_VERSION = "6.0_3.6.11.15"


@pytest.fixture
def version_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path, Mock]:
    release = tmp_path / "release.json"
    release.write_text(json.dumps({"location": str(tmp_path), "version": VERSION}))
    compatibility = tmp_path / "VERSION"
    compatibility.write_text(VERSION, encoding="utf-8")
    monkeypatch.setattr(game_version, "RELEASE_JSON_PATH", str(release))
    monkeypatch.setattr(game_version, "VERSION_PATH", compatibility)
    response = Mock()
    response.content = json.dumps({"games": {"dofus": {"platforms": {"windows": {"dofus3": VERSION}}}}})
    request = Mock()
    request.return_value.__enter__ = Mock(return_value=response)
    request.return_value.__exit__ = Mock(return_value=False)
    monkeypatch.setattr(game_version.requests, "get", request)
    return release, compatibility, response


@pytest.mark.parametrize(
    ("installed", "compatible", "latest", "message"),
    [
        (VERSION, VERSION, VERSION, None),
        (VERSION, VERSION, NEW_VERSION, "Dofus is out of date"),
        (NEW_VERSION, VERSION, NEW_VERSION, "The bot is out of date"),
        (VERSION, NEW_VERSION, VERSION, "The bot is out of date"),
    ],
)
def test_version_compatibility(
    version_files: tuple[Path, Path, Mock], installed: str, compatible: str,
    latest: str, message: str | None,
) -> None:
    release, compatibility, response = version_files
    release.write_text(json.dumps({"location": ".", "version": installed}))
    compatibility.write_text(compatible, encoding="utf-8")
    response.content = json.dumps({"games": {"dofus": {"platforms": {"windows": {"dofus3": latest}}}}})
    if message is None:
        game_version.validate_game_version()
    else:
        with pytest.raises(RuntimeSetupError, match=message):
            game_version.validate_game_version()


@pytest.mark.parametrize("file_index", [0, 1])
@pytest.mark.parametrize("content", [None, "", " ", "broken", "{}", '{"version": " "}', '{"version": 123}'])
def test_invalid_local_metadata_blocks(
    version_files: tuple[Path, Path, Mock], file_index: int, content: str | None,
) -> None:
    path = version_files[file_index]
    if content is None:
        path.unlink()
    else:
        path.write_text(content)
    with pytest.raises(RuntimeSetupError, match="missing or|missing or invalid"):
        game_version.validate_game_version()


@pytest.mark.parametrize("content", [f"{VERSION}\n", f"  {VERSION}\r\n"])
def test_version_whitespace_is_accepted(version_files: tuple[Path, Path, Mock], content: str) -> None:
    version_files[1].write_text(content, encoding="utf-8")
    game_version.validate_game_version()


@pytest.mark.parametrize("content", [b"\xff", b"1.0.4", b"null", b"6.0_3.6.10.11\n6.0_3.6.11.15"])
def test_invalid_version_blocks(version_files: tuple[Path, Path, Mock], content: bytes) -> None:
    version_files[1].write_bytes(content)
    with pytest.raises(RuntimeSetupError, match="VERSION file is missing or invalid"):
        game_version.validate_game_version()


@pytest.mark.parametrize("failure", [requests.Timeout(), requests.ConnectionError(), requests.HTTPError()])
def test_network_failure_blocks(version_files: tuple[Path, Path, Mock], failure: Exception) -> None:
    version_files[2].raise_for_status.side_effect = failure
    with pytest.raises(RuntimeSetupError, match="Unable to check"):
        game_version.validate_game_version()


@pytest.mark.parametrize("content", ["broken", "{}", '{"games": {"dofus": {"platforms": {}}}}'])
def test_invalid_remote_metadata_blocks(version_files: tuple[Path, Path, Mock], content: str) -> None:
    version_files[2].content = content
    with pytest.raises(RuntimeSetupError, match="Unable to check"):
        game_version.validate_game_version()


@pytest.mark.parametrize("blocked", [True, False])
def test_entrypoint_checks_version_before_starting_gui(monkeypatch: pytest.MonkeyPatch, blocked: bool) -> None:
    spec = importlib.util.spec_from_file_location("version_entry", Path(__file__).parents[1] / "__main__.py")
    assert spec is not None and spec.loader is not None
    entry = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, entry)
    spec.loader.exec_module(entry)
    actions = Mock()
    for name in ("check_platform", "validate_game_version", "validate_resources", "validate_browser",
                 "ensure_packaged_runtime_data", "run_gui", "report_fatal"):
        monkeypatch.setattr(entry, name, getattr(actions, name))
    actions.run_gui.return_value = 0
    if blocked:
        actions.validate_game_version.side_effect = RuntimeSetupError("Version incompatible")
    assert entry.main(["bot", "--no-auto"]) == (1 if blocked else 0)
    names = [call[0] for call in actions.mock_calls]
    if blocked:
        assert names == ["check_platform", "validate_game_version", "report_fatal"]
    else:
        assert names == ["check_platform", "validate_game_version", "validate_resources", "validate_browser",
                         "ensure_packaged_runtime_data", "run_gui"]
