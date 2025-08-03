from __future__ import annotations

import shutil
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

_GAME_ASSEMBLY_NAME = "GameAssembly.dll"
_GAME_ASSEMBLY_I64_NAME = "GameAssembly.dll.i64"
_METADATA_NAME = "global-metadata.dat"
_METADATA_RELATIVE_PATH = Path("Dofus_Data") / "il2cpp_data" / "Metadata" / _METADATA_NAME


@dataclass(frozen=True)
class ObfGameSnapshot:
    game_assembly: Path
    metadata: Path


def resolve_obf_game_snapshot(
    *,
    real_game_dir: Path,
    snapshots_root: Path,
    non_obf_game_dir: Path,
    today: date | None = None,
) -> ObfGameSnapshot:
    real_game_assembly = real_game_dir / _GAME_ASSEMBLY_NAME
    real_metadata = real_game_dir / _METADATA_RELATIVE_PATH
    current_snapshot = _find_current_snapshot(snapshots_root, non_obf_game_dir)

    if current_snapshot is not None:
        snapshot_assembly = current_snapshot / _GAME_ASSEMBLY_NAME
        snapshot_metadata = current_snapshot / _METADATA_NAME
        if snapshot_metadata.exists() and _has_same_mtime(snapshot_assembly, real_game_assembly):
            return ObfGameSnapshot(game_assembly=snapshot_assembly, metadata=snapshot_metadata)

    snapshot_date = today or datetime.now(tz=UTC).astimezone().date()
    snapshot_dir = snapshots_root / snapshot_date.strftime("%d_%m_%Y")
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    snapshot_assembly = snapshot_dir / _GAME_ASSEMBLY_NAME
    snapshot_metadata = snapshot_dir / _METADATA_NAME

    shutil.copy2(real_game_assembly, snapshot_assembly)
    shutil.copy2(real_metadata, snapshot_metadata)

    stale_i64 = snapshot_dir / _GAME_ASSEMBLY_I64_NAME
    if stale_i64.exists():
        stale_i64.unlink()

    return ObfGameSnapshot(game_assembly=snapshot_assembly, metadata=snapshot_metadata)


def find_snapshot_dir_by_game_assembly_mtime_ns(snapshots_root: Path, mtime_ns: int) -> Path | None:
    if not snapshots_root.exists():
        return None

    for snapshot_dir in snapshots_root.iterdir():
        game_assembly = snapshot_dir / _GAME_ASSEMBLY_NAME
        if snapshot_dir.is_dir() and game_assembly.is_file() and game_assembly.stat().st_mtime_ns == mtime_ns:
            return snapshot_dir
    return None


def _find_current_snapshot(snapshots_root: Path, non_obf_game_dir: Path) -> Path | None:
    if not snapshots_root.exists():
        return None

    snapshot_dirs = [
        snapshot_dir
        for snapshot_dir in snapshots_root.iterdir()
        if snapshot_dir.is_dir()
        and not _same_path(snapshot_dir, non_obf_game_dir)
        and (snapshot_dir / _GAME_ASSEMBLY_NAME).is_file()
    ]
    if not snapshot_dirs:
        return None

    return max(
        snapshot_dirs,
        key=lambda snapshot_dir: (snapshot_dir / _GAME_ASSEMBLY_NAME).stat().st_mtime_ns,
    )


def _same_path(left: Path, right: Path) -> bool:
    return left.resolve() == right.resolve()


def _has_same_mtime(left: Path, right: Path) -> bool:
    return left.stat().st_mtime_ns == right.stat().st_mtime_ns
