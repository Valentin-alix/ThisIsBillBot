from pathlib import Path

from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.helper_builders import (
    snapshot_layout,
    write_snapshot,
)

from DBDofusUnity.proto_mapper_assembly.helpers.archived_builds import (
    PROTO_ACCESSES_RELATIVE_PATH,
    PROTOCOL_GAME_DUMP_CS_RELATIVE_PATH,
    iter_archived_build_dirs,
)


def _write_obf_artifacts(build_dir: Path) -> None:
    dump_cs_path = build_dir / PROTOCOL_GAME_DUMP_CS_RELATIVE_PATH
    dump_cs_path.parent.mkdir(parents=True, exist_ok=True)
    dump_cs_path.write_text("// dump", encoding="utf-8")
    (build_dir / PROTO_ACCESSES_RELATIVE_PATH).write_text("{}", encoding="utf-8")


class TestIterArchivedBuildDirs:
    def test_orders_by_game_assembly_mtime_rather_than_directory_name(self, tmp_path: Path) -> None:
        layout = snapshot_layout(tmp_path)
        older = write_snapshot(layout.snapshots_root / "30_06_2026", assembly_mtime_ns=100)
        newer = write_snapshot(layout.snapshots_root / "04_08_2026", assembly_mtime_ns=300)
        middle = write_snapshot(layout.snapshots_root / "BETA_BUILD", assembly_mtime_ns=200)

        assert iter_archived_build_dirs(snapshots_root=layout.snapshots_root) == [newer, middle, older]

    def test_excludes_the_non_obfuscated_build_stored_alongside_the_archives(self, tmp_path: Path) -> None:
        layout = snapshot_layout(tmp_path)
        write_snapshot(layout.non_obf_game_dir, assembly_mtime_ns=900)
        archived = write_snapshot(layout.snapshots_root / "04_08_2026", assembly_mtime_ns=300)

        build_dirs = iter_archived_build_dirs(
            snapshots_root=layout.snapshots_root, exclude_dir=layout.non_obf_game_dir
        )

        assert build_dirs == [archived]

    def test_skips_builds_missing_a_required_artifact(self, tmp_path: Path) -> None:
        layout = snapshot_layout(tmp_path)
        complete = write_snapshot(layout.snapshots_root / "04_08_2026", assembly_mtime_ns=300)
        _write_obf_artifacts(complete)
        write_snapshot(layout.snapshots_root / "30_06_2026", assembly_mtime_ns=100)

        build_dirs = iter_archived_build_dirs(
            snapshots_root=layout.snapshots_root,
            required_files=(PROTOCOL_GAME_DUMP_CS_RELATIVE_PATH, PROTO_ACCESSES_RELATIVE_PATH),
        )

        assert build_dirs == [complete]

    def test_skips_directories_without_a_game_assembly(self, tmp_path: Path) -> None:
        layout = snapshot_layout(tmp_path)
        archived = write_snapshot(layout.snapshots_root / "04_08_2026", assembly_mtime_ns=300)
        (layout.snapshots_root / "cache").mkdir()

        assert iter_archived_build_dirs(snapshots_root=layout.snapshots_root) == [archived]

    def test_returns_nothing_when_the_snapshots_root_is_absent(self, tmp_path: Path) -> None:
        assert iter_archived_build_dirs(snapshots_root=tmp_path / "missing") == []
