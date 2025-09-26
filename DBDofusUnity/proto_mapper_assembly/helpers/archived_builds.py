"""Layout of an archived game build directory, and how to enumerate those directories.

Every archived build under ``OBF_GAME_SNAPSHOTS_DIR`` carries the same file names as the working
set, so the relative paths below are the single description of that layout. They live here rather
than in ``consts`` because ``consts`` imports this package while resolving the current snapshot.

Ordering always follows the ``GameAssembly.dll`` modification time rather than the directory name:
names like ``BETA`` carry no date, and a build is identified by the assembly it ships.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

GAME_ASSEMBLY_NAME = "GameAssembly.dll"
GAME_ASSEMBLY_I64_NAME = f"{GAME_ASSEMBLY_NAME}.i64"
IL2CPP_METADATA_NAME = "global-metadata.dat"

PROTOCOL_GAME_DUMP_CS_RELATIVE_PATH: Path = Path("cs") / "Ankama.Dofus.Protocol.Game.cs"
PROTO_ACCESSES_RELATIVE_PATH: Path = Path("proto_accesses.json")
GAME_MAPPINGS_RELATIVE_PATH: Path = Path("game_mappings.json")

NON_OBF_SUBDIR: Path = Path("non_obf")
NON_OBF_PROTOCOL_GAME_DUMP_CS_RELATIVE_PATH: Path = NON_OBF_SUBDIR / PROTOCOL_GAME_DUMP_CS_RELATIVE_PATH
NON_OBF_PROTO_ACCESSES_RELATIVE_PATH: Path = NON_OBF_SUBDIR / PROTO_ACCESSES_RELATIVE_PATH


def iter_archived_build_dirs(
    *,
    snapshots_root: Path,
    exclude_dir: Path | None = None,
    required_files: Sequence[Path] = (),
) -> list[Path]:
    """List the archived build directories, newest first.

    ``exclude_dir`` drops one directory from the result: the non-obfuscated build is stored
    alongside the archived obfuscated ones, and is not one of them.
    """
    if not snapshots_root.exists():
        return []

    resolved_exclusion = exclude_dir.resolve() if exclude_dir is not None else None
    build_dirs = [
        build_dir
        for build_dir in snapshots_root.iterdir()
        if build_dir.is_dir()
        and (build_dir / GAME_ASSEMBLY_NAME).is_file()
        and build_dir.resolve() != resolved_exclusion
        and all((build_dir / required_file).is_file() for required_file in required_files)
    ]
    return sorted(build_dirs, key=game_assembly_mtime_ns, reverse=True)


def game_assembly_mtime_ns(build_dir: Path) -> int:
    return (build_dir / GAME_ASSEMBLY_NAME).stat().st_mtime_ns
