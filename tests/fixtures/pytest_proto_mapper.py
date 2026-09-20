import uuid
from collections.abc import Callable, Iterator
from functools import cached_property
from pathlib import Path

import pytest
from DBDofusUnity.proto_mapper_assembly.runtime import runtime_store
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore

from src.protocol import protocol_game


@pytest.fixture
def dump_cs(tmp_path_factory: pytest.TempPathFactory) -> Callable[[str], Path]:
    tmp_dir = tmp_path_factory.mktemp("parse_types")
    tmp_file = tmp_dir / f"{uuid.uuid4()}.cs"

    def _dump_cs(code: str) -> Path:
        tmp_file.write_text(code, encoding="utf-8")
        return tmp_file

    return _dump_cs


@pytest.fixture
def runtime_data_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[RuntimeDataStore]:
    monkeypatch.setattr(runtime_store, "RUNTIME_DATA_FILE", tmp_path / "instancied_msg_infos.json")
    monkeypatch.setattr(runtime_store, "ENABLE_MSG_CAPTURE", True)
    instance = RuntimeDataStore()
    instance._capture_sequence_index = None  # pyright: ignore[reportPrivateUsage]
    instance._capture_session_id = None  # pyright: ignore[reportPrivateUsage]
    instance._capture_target_path = None  # pyright: ignore[reportPrivateUsage]
    monkeypatch.setattr(protocol_game, "_on_exit", lambda: None)
    yield instance
    instance._capture_target_path = None  # pyright: ignore[reportPrivateUsage]
    instance.path.unlink(missing_ok=True)
    # Clear singleton cached views so they cannot leak into the next test.
    for name, attribute in vars(type(instance)).items():
        if isinstance(attribute, cached_property):
            instance.__dict__.pop(name, None)  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
