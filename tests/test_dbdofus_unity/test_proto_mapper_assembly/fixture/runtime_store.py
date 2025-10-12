from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path

import numpy as np


def seed_runtime_content(
    tmp_path: Path,
    content_by_name: Mapping[str, Sequence[Mapping[str, object]]],
    *,
    filename: str = "instancied_msg_infos.json",
) -> None:
    """Write runtime JSON under ``tmp_path`` for tests using the monkeypatched runtime store."""
    entries_by_name = {
        name: [_with_meta_defaults(entry, capture_sequence) for capture_sequence, entry in enumerate(entries)]
        for name, entries in content_by_name.items()
    }
    (tmp_path / filename).write_text(json.dumps(entries_by_name, default=_json_default), encoding="utf-8")


def _with_meta_defaults(entry: Mapping[str, object], capture_sequence: int) -> dict[str, object]:
    payload = dict(entry)
    payload.setdefault("from_server", False)
    payload.setdefault("is_root_msg", False)
    payload.setdefault("is_game_msg", False)
    payload.setdefault("capture_sequence", capture_sequence)
    return payload


def _json_default(value: object) -> object:
    if isinstance(value, np.ndarray):
        return value.tolist()
    err = f"Object of type {type(value).__name__} is not JSON serializable"
    raise TypeError(err)
