from datetime import date
from pathlib import Path

from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.helper_builders import (
    snapshot_layout,
    write_real_game_files,
    write_snapshot,
)

from proto_mapper_assembly.helpers.obf_game_snapshot import (
    find_snapshot_dir_by_game_assembly_mtime_ns,
    resolve_obf_game_snapshot,
)


class TestObfGameSnapshot:
    def test_uses_latest_snapshot_when_game_assembly_mtime_matches_real_game(self, tmp_path: Path) -> None:
        layout = snapshot_layout(tmp_path)
        real_assembly, _ = write_real_game_files(layout.real_game_dir, mtime_ns=300)
        old_snapshot = write_snapshot(layout.snapshots_root / "22_04_2026", assembly_mtime_ns=200)
        current_snapshot = write_snapshot(layout.snapshots_root / "05_05_2026", assembly_mtime_ns=300)

        snapshot = resolve_obf_game_snapshot(
            real_game_dir=layout.real_game_dir,
            snapshots_root=layout.snapshots_root,
            non_obf_game_dir=layout.non_obf_game_dir,
            today=date(2026, 5, 6),
        )

        assert snapshot.game_assembly == current_snapshot / "GameAssembly.dll"
        assert snapshot.metadata == current_snapshot / "global-metadata.dat"
        assert real_assembly.stat().st_mtime_ns == snapshot.game_assembly.stat().st_mtime_ns
        assert (old_snapshot / "GameAssembly.dll").exists()

    def test_refreshes_today_snapshot_and_removes_stale_i64(self, tmp_path: Path) -> None:
        layout = snapshot_layout(tmp_path)
        real_assembly, real_metadata = write_real_game_files(layout.real_game_dir, mtime_ns=500)
        today_snapshot = write_snapshot(layout.snapshots_root / "05_05_2026", assembly_mtime_ns=400)
        stale_i64 = today_snapshot / "GameAssembly.dll.i64"
        stale_i64.write_bytes(b"stale")

        snapshot = resolve_obf_game_snapshot(
            real_game_dir=layout.real_game_dir,
            snapshots_root=layout.snapshots_root,
            non_obf_game_dir=layout.non_obf_game_dir,
            today=date(2026, 5, 5),
        )

        assert snapshot.game_assembly == today_snapshot / "GameAssembly.dll"
        assert snapshot.metadata == today_snapshot / "global-metadata.dat"
        assert snapshot.game_assembly.read_bytes() == real_assembly.read_bytes()
        assert snapshot.metadata.read_bytes() == real_metadata.read_bytes()
        assert not stale_i64.exists()

    def test_ignores_non_obf_game_dir_when_selecting_current_snapshot(self, tmp_path: Path) -> None:
        layout = snapshot_layout(tmp_path)
        write_real_game_files(layout.real_game_dir, mtime_ns=300)
        write_snapshot(layout.non_obf_game_dir, assembly_mtime_ns=900)
        obf_snapshot = write_snapshot(layout.snapshots_root / "05_05_2026", assembly_mtime_ns=300)

        snapshot = resolve_obf_game_snapshot(
            real_game_dir=layout.real_game_dir,
            snapshots_root=layout.snapshots_root,
            non_obf_game_dir=layout.non_obf_game_dir,
            today=date(2026, 5, 6),
        )

        assert snapshot.game_assembly == obf_snapshot / "GameAssembly.dll"


class TestFindSnapshotDirByGameAssemblyMtimeNs:
    def test_returns_matching_snapshot_dir(self, tmp_path: Path) -> None:
        layout = snapshot_layout(tmp_path)
        write_snapshot(layout.snapshots_root / "22_04_2026", assembly_mtime_ns=200)
        matching_snapshot = write_snapshot(layout.snapshots_root / "05_05_2026", assembly_mtime_ns=300)

        found = find_snapshot_dir_by_game_assembly_mtime_ns(layout.snapshots_root, 300)

        assert found == matching_snapshot

    def test_returns_none_when_no_snapshot_matches(self, tmp_path: Path) -> None:
        layout = snapshot_layout(tmp_path)
        write_snapshot(layout.snapshots_root / "22_04_2026", assembly_mtime_ns=200)

        found = find_snapshot_dir_by_game_assembly_mtime_ns(layout.snapshots_root, 999)

        assert found is None

    def test_returns_none_when_snapshots_root_missing(self, tmp_path: Path) -> None:
        found = find_snapshot_dir_by_game_assembly_mtime_ns(tmp_path / "missing", 300)

        assert found is None
