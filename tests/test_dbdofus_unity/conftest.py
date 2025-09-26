from __future__ import annotations

import uuid
from collections.abc import Callable, Iterator
from functools import cached_property
from pathlib import Path

import pytest
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.ida_environment import (
    install_mock_ida_environment,
)
from src.protocol import protocol_game

from proto_mapper_assembly.runtime import runtime_store
from proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore

install_mock_ida_environment()


@pytest.fixture
def dump_cs(tmp_path_factory: pytest.TempPathFactory) -> Callable[[str], Path]:
    tmp_dir = tmp_path_factory.mktemp("parse_types")
    tmp_file = tmp_dir / f"{uuid.uuid4()}.cs"

    def _dump_cs(code: str) -> Path:
        tmp_file.write_text(code, encoding="utf-8")
        return tmp_file

    return _dump_cs


@pytest.fixture
def tmp_json_path(tmp_path: Path) -> Path:
    return tmp_path / f"{uuid.uuid4()}.json"


@pytest.fixture
def runtime_data_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[RuntimeDataStore]:
    monkeypatch.setattr(runtime_store, "RUNTIME_DATA_DIR", tmp_path)
    instance = RuntimeDataStore()
    instance._capture_sequence_index = None  # pyright: ignore[reportPrivateUsage]
    instance._capture_session_id = None  # pyright: ignore[reportPrivateUsage]
    instance._capture_target_path = None  # pyright: ignore[reportPrivateUsage]
    monkeypatch.setattr(protocol_game, "_on_exit", lambda: None)
    yield instance
    instance._capture_target_path = None  # pyright: ignore[reportPrivateUsage]
    instance.path.unlink(missing_ok=True)
    # The store is a singleton, so every cached view has to go or the next test reads this one's data.
    for name, attribute in vars(type(instance)).items():
        if isinstance(attribute, cached_property):
            instance.__dict__.pop(name, None)  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
