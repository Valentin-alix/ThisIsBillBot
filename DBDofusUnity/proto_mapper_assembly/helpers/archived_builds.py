"""Order archived builds by GameAssembly.dll mtime; directory names need not contain dates."""


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
