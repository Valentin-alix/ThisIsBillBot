from __future__ import annotations

import os
import sys
from datetime import UTC, date, datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from proto_mapper_assembly.scripts import dump as dump_script


class TestDumpScript:
    @staticmethod
    def _write_dump_cs(output_folder: Path, body: str = "class krl {}") -> None:
        """Stand in for Il2CppInspector, whose real output is what the dump marker now hashes."""
        dump_cs = output_folder / dump_script.PROTOCOL_GAME_DUMP_CS_RELATIVE_PATH
        dump_cs.parent.mkdir(parents=True, exist_ok=True)
        dump_cs.write_text(body, encoding="utf-8")

    def _fake_il2cpp_inspector(self, _dll: Path, _meta: Path, output_folder: Path) -> None:
        self._write_dump_cs(output_folder)

    def test_gen_python_removes_bindings_without_a_proto_source(self, tmp_path: Path) -> None:
        """A removed schema must not re-enter descriptor discovery through a stale pb2 module."""
        (tmp_path / "live.proto").write_text('syntax = "proto3";', encoding="utf-8")
        (tmp_path / "live_pb2.py").write_text("", encoding="utf-8")
        stale_binding = tmp_path / "stale_pb2.py"
        stale_stub = tmp_path / "stale_pb2.pyi"
        stale_binding.write_text("", encoding="utf-8")
        stale_stub.write_text("", encoding="utf-8")

        with patch.object(dump_script.subprocess, "run"):
            dump_script.gen_python_from_protoc(tmp_path, tmp_path)

        assert not stale_binding.exists()
        assert not stale_stub.exists()
        assert (tmp_path / "live_pb2.py").exists()

    def test_update_protos_uses_custom_obf_dir_for_inputs_outputs_and_ida(self, tmp_path: Path) -> None:
        obf_dir = tmp_path / "20_05_2026"
        obf_dir.mkdir()
        (obf_dir / "GameAssembly.dll").write_bytes(b"dll-bytes")
        il2cpp_calls: list[tuple[Path, Path, Path]] = []
        protodec_calls: list[tuple[Path, Path]] = []
        protoc_calls: list[tuple[Path, Path]] = []
        ida_calls: list[dict[str, Path | bool | None]] = []

        def fake_run_il2cpp_inspector(
            game_assembly_path: Path, metadata_path: Path, output_folder: Path
        ) -> None:
            il2cpp_calls.append((game_assembly_path, metadata_path, output_folder))
            self._write_dump_cs(output_folder)

        def fake_run_protodec(assembly_path: Path, proto_output: Path) -> None:
            protodec_calls.append((assembly_path, proto_output))
            proto_output.parent.mkdir(parents=True, exist_ok=True)
            proto_output.write_text('syntax = "proto3";', encoding="utf-8")

        def fake_gen_python_from_protoc(proto_input: Path, output_folder: Path) -> None:
            protoc_calls.append((proto_input, output_folder))

        def fake_run_ida_script(
            *,
            use_non_obf: bool,
            base_dir: Path | None = None,
            database_path: Path | None = None,
        ) -> None:
            ida_calls.append(
                {
                    "use_non_obf": use_non_obf,
                    "base_dir": base_dir,
                    "database_path": database_path,
                }
            )

        with (
            patch.object(dump_script, "run_il2cpp_inspector", side_effect=fake_run_il2cpp_inspector),
            patch.object(dump_script, "run_protodec", side_effect=fake_run_protodec),
            patch.object(dump_script, "gen_python_from_protoc", side_effect=fake_gen_python_from_protoc),
            patch.object(dump_script, "run_ida_script", side_effect=fake_run_ida_script),
            patch.object(dump_script, "run_pipeline"),
            patch.object(dump_script, "PINNED_PAIRS_FILE", tmp_path / "pinned_pairs.json"),
            patch.object(dump_script, "RUNTIME_DATA_DIR", tmp_path / "runtime_data"),
        ):
            dump_script.update_protos(use_obf=True, obf_dir=obf_dir)

        assert il2cpp_calls == [(obf_dir / "GameAssembly.dll", obf_dir / "global-metadata.dat", obf_dir)]
        assert protodec_calls == [
            (obf_dir / "dll" / "Ankama.Dofus.Protocol.Game.dll", obf_dir / "game_messages.proto")
        ]
        assert protoc_calls == [(obf_dir / "game_messages.proto", obf_dir)]
        assert ida_calls == [
            {
                "use_non_obf": False,
                "base_dir": obf_dir,
                "database_path": obf_dir / "GameAssembly.dll.i64",
            }
        ]

    def test_update_protos_leaves_the_live_workspace_alone_for_a_custom_obf_dir(self, tmp_path: Path) -> None:
        """Backfilling an archived build must not touch the current pinned pairs or mappings."""
        obf_dir = tmp_path / "20_05_2026"
        obf_dir.mkdir()
        (obf_dir / "GameAssembly.dll").write_bytes(b"dll-bytes")
        pinned_pairs_path = tmp_path / "pinned_pairs.json"
        pinned_pairs_path.write_text('{"pairs": [{"obf": "aB", "non_obf": "Foo"}]}', encoding="utf-8")

        def fake_run_protodec(_assembly_path: Path, proto_output: Path) -> None:
            proto_output.parent.mkdir(parents=True, exist_ok=True)
            proto_output.write_text('syntax = "proto3";', encoding="utf-8")

        with (
            patch.object(dump_script, "run_il2cpp_inspector", side_effect=self._fake_il2cpp_inspector),
            patch.object(dump_script, "run_protodec", side_effect=fake_run_protodec),
            patch.object(dump_script, "gen_python_from_protoc"),
            patch.object(dump_script, "run_ida_script"),
            patch.object(dump_script, "run_pipeline") as run_pipeline_mock,
            patch.object(dump_script, "PINNED_PAIRS_FILE", pinned_pairs_path),
            patch.object(dump_script, "RUNTIME_DATA_DIR", tmp_path / "runtime_data"),
            patch.object(dump_script, "_clear_mapping_inputs_before_pipeline") as clear_mock,
        ):
            dump_script.update_protos(use_obf=True, obf_dir=obf_dir)

        clear_mock.assert_not_called()
        run_pipeline_mock.assert_not_called()
        assert "aB" in pinned_pairs_path.read_text(encoding="utf-8")

    def test_update_protos_clears_mapping_inputs_and_runs_the_pipeline_on_the_live_workspace(
        self, tmp_path: Path
    ) -> None:
        game_assembly = tmp_path / "GameAssembly.dll"
        game_assembly.write_bytes(b"dll-bytes")

        def fake_run_protodec(_assembly_path: Path, proto_output: Path) -> None:
            proto_output.parent.mkdir(parents=True, exist_ok=True)
            proto_output.write_text('syntax = "proto3";', encoding="utf-8")

        with (
            patch.object(dump_script, "OBFUSCATED_DATA_DIR", tmp_path / "obf"),
            patch.object(dump_script, "OBF_GAME_ASSEMBLY_DLL", game_assembly),
            patch.object(dump_script, "OBF_IL2CPP_METADATA_FILE", tmp_path / "global-metadata.dat"),
            patch.object(dump_script, "OBF_PROTO_OUTPUT", tmp_path / "protos"),
            patch.object(dump_script, "OBF_GAME_SNAPSHOTS_DIR", tmp_path / "snapshots"),
            patch.object(dump_script, "run_il2cpp_inspector", side_effect=self._fake_il2cpp_inspector),
            patch.object(dump_script, "run_protodec", side_effect=fake_run_protodec),
            patch.object(dump_script, "gen_python_from_protoc"),
            patch.object(dump_script, "run_ida_script"),
            patch.object(dump_script, "run_pipeline") as run_pipeline_mock,
            patch.object(dump_script, "PINNED_PAIRS_FILE", tmp_path / "pinned_pairs.json"),
            patch.object(dump_script, "RUNTIME_DATA_DIR", tmp_path / "runtime_data"),
            patch.object(dump_script, "_clear_mapping_inputs_before_pipeline") as clear_mock,
        ):
            dump_script.update_protos(use_obf=True)

        clear_mock.assert_called_once_with()
        run_pipeline_mock.assert_called_once_with(do_load_pinned_pair=True)

    def test_update_protos_skips_redumping_when_game_assembly_is_unchanged(self, tmp_path: Path) -> None:
        obf_dir = tmp_path / "20_05_2026"
        obf_dir.mkdir()
        (obf_dir / "GameAssembly.dll").write_bytes(b"dll-bytes")

        def fake_run_protodec(_assembly_path: Path, proto_output: Path) -> None:
            proto_output.parent.mkdir(parents=True, exist_ok=True)
            proto_output.write_text('syntax = "proto3";', encoding="utf-8")

        with (
            patch.object(
                dump_script, "run_il2cpp_inspector", side_effect=self._fake_il2cpp_inspector
            ) as il2cpp_mock,
            patch.object(dump_script, "run_protodec", side_effect=fake_run_protodec),
            patch.object(dump_script, "gen_python_from_protoc"),
            patch.object(dump_script, "run_ida_script"),
            patch.object(dump_script, "run_pipeline"),
            patch.object(dump_script, "PINNED_PAIRS_FILE", tmp_path / "pinned_pairs.json"),
            patch.object(dump_script, "RUNTIME_DATA_DIR", tmp_path / "runtime_data"),
        ):
            dump_script.update_protos(use_obf=True, obf_dir=obf_dir)
            dump_script.update_protos(use_obf=True, obf_dir=obf_dir)

        assert il2cpp_mock.call_count == 1

    def test_update_protos_redumps_an_already_dumped_build_when_forced(self, tmp_path: Path) -> None:
        """An archived build keeps a marker matching its own assembly, so refreshing it needs --force."""
        obf_dir = tmp_path / "21_07_2026"
        obf_dir.mkdir()
        (obf_dir / "GameAssembly.dll").write_bytes(b"dll-bytes")

        def fake_run_protodec(_assembly_path: Path, proto_output: Path) -> None:
            proto_output.parent.mkdir(parents=True, exist_ok=True)
            proto_output.write_text('syntax = "proto3";', encoding="utf-8")

        with (
            patch.object(
                dump_script, "run_il2cpp_inspector", side_effect=self._fake_il2cpp_inspector
            ) as il2cpp_mock,
            patch.object(dump_script, "run_protodec", side_effect=fake_run_protodec),
            patch.object(dump_script, "gen_python_from_protoc"),
            patch.object(dump_script, "run_ida_script") as ida_mock,
            patch.object(dump_script, "run_pipeline"),
            patch.object(dump_script, "PINNED_PAIRS_FILE", tmp_path / "pinned_pairs.json"),
            patch.object(dump_script, "RUNTIME_DATA_DIR", tmp_path / "runtime_data"),
        ):
            dump_script.update_protos(use_obf=True, obf_dir=obf_dir)
            dump_script.update_protos(use_obf=True, obf_dir=obf_dir, force=True)

        assert il2cpp_mock.call_count == 2
        # The dump.cs is byte-identical on the second pass, which would normally short-circuit
        # before the tracer runs; forcing has to carry through to it, since re-tracing is the point.
        assert ida_mock.call_count == 2

    def test_update_protos_redumps_when_game_assembly_changes(self, tmp_path: Path) -> None:
        obf_dir = tmp_path / "20_05_2026"
        obf_dir.mkdir()
        dll_path = obf_dir / "GameAssembly.dll"
        dll_path.write_bytes(b"dll-bytes")
        protodec_call_count = 0

        def fake_run_protodec(_assembly_path: Path, proto_output: Path) -> None:
            nonlocal protodec_call_count
            protodec_call_count += 1
            proto_output.parent.mkdir(parents=True, exist_ok=True)
            proto_output.write_text(f'syntax = "proto3"; // run {protodec_call_count}', encoding="utf-8")

        with (
            patch.object(
                dump_script, "run_il2cpp_inspector", side_effect=self._fake_il2cpp_inspector
            ) as il2cpp_mock,
            patch.object(dump_script, "run_protodec", side_effect=fake_run_protodec),
            patch.object(dump_script, "gen_python_from_protoc"),
            patch.object(dump_script, "run_ida_script"),
            patch.object(dump_script, "run_pipeline"),
            patch.object(dump_script, "PINNED_PAIRS_FILE", tmp_path / "pinned_pairs.json"),
            patch.object(dump_script, "RUNTIME_DATA_DIR", tmp_path / "runtime_data"),
        ):
            dump_script.update_protos(use_obf=True, obf_dir=obf_dir)

            new_mtime_ns = dll_path.stat().st_mtime_ns + 1_000_000_000
            os.utime(dll_path, ns=(new_mtime_ns, new_mtime_ns))

            dump_script.update_protos(use_obf=True, obf_dir=obf_dir)

        assert il2cpp_mock.call_count == 2

    def test_update_protos_archives_previous_obf_dump_next_to_matching_snapshot(self, tmp_path: Path) -> None:
        obf_output_dir = tmp_path / "obf"
        obf_output_dir.mkdir()
        snapshots_root = tmp_path / "snapshots"

        old_snapshot_dir = snapshots_root / "14_07_2026"
        old_snapshot_dir.mkdir(parents=True)
        old_game_assembly = old_snapshot_dir / "GameAssembly.dll"
        old_game_assembly.write_bytes(b"old-dll-bytes")

        new_snapshot_dir = snapshots_root / "21_07_2026"
        new_snapshot_dir.mkdir(parents=True)
        new_game_assembly = new_snapshot_dir / "GameAssembly.dll"
        new_game_assembly.write_bytes(b"new-dll-bytes")
        new_mtime_ns = old_game_assembly.stat().st_mtime_ns + 1_000_000_000
        os.utime(new_game_assembly, ns=(new_mtime_ns, new_mtime_ns))

        def fake_run_protodec(_assembly_path: Path, proto_output: Path) -> None:
            proto_output.parent.mkdir(parents=True, exist_ok=True)
            proto_output.write_text('syntax = "proto3";', encoding="utf-8")

        def run_update(game_assembly: Path) -> None:
            with (
                patch.object(dump_script, "OBFUSCATED_DATA_DIR", obf_output_dir),
                patch.object(dump_script, "OBF_GAME_ASSEMBLY_DLL", game_assembly),
                patch.object(dump_script, "OBF_IL2CPP_METADATA_FILE", tmp_path / "global-metadata.dat"),
                patch.object(dump_script, "OBF_PROTO_OUTPUT", tmp_path / "protos"),
                patch.object(dump_script, "OBF_GAME_SNAPSHOTS_DIR", snapshots_root),
                patch.object(dump_script, "run_il2cpp_inspector", side_effect=self._fake_il2cpp_inspector),
                patch.object(dump_script, "run_protodec", side_effect=fake_run_protodec),
                patch.object(dump_script, "gen_python_from_protoc"),
                patch.object(dump_script, "run_ida_script"),
                patch.object(dump_script, "run_pipeline"),
                patch.object(dump_script, "PINNED_PAIRS_FILE", tmp_path / "pinned_pairs.json"),
                patch.object(dump_script, "RUNTIME_DATA_DIR", tmp_path / "runtime_data"),
            ):
                dump_script.update_protos(use_obf=True)

        run_update(old_game_assembly)

        assert not (old_snapshot_dir / "cs").exists()

        (obf_output_dir / "cs").mkdir(exist_ok=True)
        (obf_output_dir / "cs" / "Sample.cs").write_text("class Sample {}", encoding="utf-8")

        run_update(new_game_assembly)

        assert (old_snapshot_dir / "cs" / "Sample.cs").read_text(encoding="utf-8") == "class Sample {}"
        assert (old_snapshot_dir / dump_script.GAME_ASSEMBLY_MARKER_NAME).exists()
        assert not (new_snapshot_dir / "cs").exists()

    def test_main_rejects_custom_obf_dir_with_non_obf_mode(self, tmp_path: Path) -> None:
        with (
            patch.object(sys, "argv", ["dump.py", "--non-obf", "--obf-dir", str(tmp_path)]),
            patch.object(dump_script, "update_protos") as update_protos,
            pytest.raises(SystemExit) as exc_info,
        ):
            dump_script.main()

        assert exc_info.value.code == 2
        update_protos.assert_not_called()

    def _run_dump_twice_across_builds(
        self, tmp_path: Path, obf_dir: Path, dump_cs_bodies: tuple[str, str]
    ) -> int:
        """Dump twice with a changed assembly, returning how often the tracer ran."""
        dll_path = obf_dir / "GameAssembly.dll"
        dll_path.write_bytes(b"dll-bytes")
        bodies = iter(dump_cs_bodies)

        def fake_run_il2cpp_inspector(_dll: Path, _meta: Path, output_folder: Path) -> None:
            self._write_dump_cs(output_folder, next(bodies))

        def fake_run_protodec(_assembly_path: Path, proto_output: Path) -> None:
            # Deliberately byte-identical across both runs: the shapes did not move, only the names.
            proto_output.parent.mkdir(parents=True, exist_ok=True)
            proto_output.write_text('syntax = "proto3";', encoding="utf-8")

        with (
            patch.object(dump_script, "run_il2cpp_inspector", side_effect=fake_run_il2cpp_inspector),
            patch.object(dump_script, "run_protodec", side_effect=fake_run_protodec),
            patch.object(dump_script, "gen_python_from_protoc"),
            patch.object(dump_script, "run_ida_script") as ida_mock,
            patch.object(dump_script, "run_pipeline"),
            patch.object(dump_script, "PINNED_PAIRS_FILE", tmp_path / "pinned_pairs.json"),
            patch.object(dump_script, "RUNTIME_DATA_DIR", tmp_path / "runtime_data"),
        ):
            dump_script.update_protos(use_obf=True, obf_dir=obf_dir)

            new_mtime_ns = dll_path.stat().st_mtime_ns + 1_000_000_000
            os.utime(dll_path, ns=(new_mtime_ns, new_mtime_ns))

            dump_script.update_protos(use_obf=True, obf_dir=obf_dir)

        return ida_mock.call_count

    def test_update_protos_retraces_when_only_the_dump_cs_changed(self, tmp_path: Path) -> None:
        """A build can reshuffle obfuscated names without moving a single message shape.

        The generated .proto is then byte-identical while `krl` designates a different message, so
        hashing the .proto would short-circuit and leave the IDA trace keyed to the previous build.
        """
        obf_dir = tmp_path / "07_08_2026"
        obf_dir.mkdir()

        ida_call_count = self._run_dump_twice_across_builds(
            tmp_path, obf_dir, ("class krl { string fyvn; }", "class krl { string gaab; }")
        )

        assert ida_call_count == 2

    def test_update_protos_skips_retracing_when_the_dump_cs_is_identical(self, tmp_path: Path) -> None:
        obf_dir = tmp_path / "07_08_2026"
        obf_dir.mkdir()

        ida_call_count = self._run_dump_twice_across_builds(
            tmp_path, obf_dir, ("class krl { string fyvn; }", "class krl { string fyvn; }")
        )

        assert ida_call_count == 1

    def test_clear_mapping_inputs_archives_runtime_captures_instead_of_deleting(self, tmp_path: Path) -> None:
        runtime_dir = tmp_path / "runtime_data"
        runtime_dir.mkdir()
        capture = runtime_dir / f"{dump_script.BASE_FILENAME}.json"
        capture.write_text('{"krl": []}', encoding="utf-8")
        shard = runtime_dir / f"{dump_script.BASE_FILENAME}_2.json"
        shard.write_text('{"kro": []}', encoding="utf-8")

        with (
            patch.object(dump_script, "RUNTIME_DATA_DIR", runtime_dir),
            patch.object(dump_script, "PINNED_PAIRS_FILE", tmp_path / "pinned_pairs.json"),
        ):
            dump_script._clear_mapping_inputs_before_pipeline()

        assert not capture.exists()
        assert not shard.exists()
        backups = sorted(path.name for path in runtime_dir.iterdir())
        today = datetime.now(tz=UTC).astimezone().date().strftime("%d_%m_%Y")
        assert backups == [
            f"{dump_script.BASE_FILENAME}.json.backup.{today}",
            f"{dump_script.BASE_FILENAME}_2.json.backup.{today}",
        ]
        assert (runtime_dir / f"{dump_script.BASE_FILENAME}.json.backup.{today}").read_text(
            encoding="utf-8"
        ) == '{"krl": []}'

    def test_runtime_capture_backups_stay_out_of_the_runtime_store_glob(self, tmp_path: Path) -> None:
        """The archive must not be readable as a capture.

        Obfuscated names are reshuffled every build, so re-merging a previous build's capture would
        feed the matcher payloads keyed to messages that no longer exist under those names.
        """
        runtime_dir = tmp_path / "runtime_data"
        runtime_dir.mkdir()
        capture = runtime_dir / f"{dump_script.BASE_FILENAME}.json"
        capture.write_text("{}", encoding="utf-8")

        backup_path = dump_script._archive_runtime_capture(capture, date(2026, 8, 8))

        assert backup_path.name == f"{dump_script.BASE_FILENAME}.json.backup.08_08_2026"
        assert list(runtime_dir.glob(f"{dump_script.BASE_FILENAME}*.json")) == []

    def test_archiving_twice_the_same_day_keeps_both_captures(self, tmp_path: Path) -> None:
        runtime_dir = tmp_path / "runtime_data"
        runtime_dir.mkdir()
        capture = runtime_dir / f"{dump_script.BASE_FILENAME}.json"

        capture.write_text('{"first": []}', encoding="utf-8")
        first_backup = dump_script._archive_runtime_capture(capture, date(2026, 8, 8))
        capture.write_text('{"second": []}', encoding="utf-8")
        second_backup = dump_script._archive_runtime_capture(capture, date(2026, 8, 8))

        assert first_backup.name == f"{dump_script.BASE_FILENAME}.json.backup.08_08_2026"
        assert second_backup.name == f"{dump_script.BASE_FILENAME}.json.backup.08_08_2026.2"
        assert first_backup.read_text(encoding="utf-8") == '{"first": []}'
        assert second_backup.read_text(encoding="utf-8") == '{"second": []}'
