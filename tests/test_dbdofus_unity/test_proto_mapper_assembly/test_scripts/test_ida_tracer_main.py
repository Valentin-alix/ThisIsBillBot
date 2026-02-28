from __future__ import annotations

import io
import threading
from pathlib import Path
from unittest.mock import patch

import pytest

from DBDofusUnity.proto_mapper_assembly.scripts.ida_tracer_lib import main as ida_main
from DBDofusUnity.proto_mapper_assembly.scripts.ida_tracer_lib.progress import reporter


class _CompletedThread:
    def join(self) -> None:
        return None


class _FakeProcess:
    def __init__(self, return_code: int = 0, stdout_lines: list[str] | None = None) -> None:
        self.stdout = iter(["ida output\n"])
        if stdout_lines is not None:
            self.stdout = iter(stdout_lines)
        self._return_code = return_code

    def wait(self) -> int:
        return self._return_code


class TestIdaTracerMain:
    @pytest.mark.parametrize(
        ("database_exists", "expected_name"),
        [(True, "GameAssembly.dll.i64"), (False, "GameAssembly.dll")],
    )
    def test_select_ida_database_prefers_i64_and_falls_back_to_dll(
        self,
        tmp_path: Path,
        database_exists: bool,
        expected_name: str,
    ) -> None:
        database = tmp_path / "GameAssembly.dll.i64"
        if database_exists:
            database.write_bytes(b"i64")
        else:
            (tmp_path / "GameAssembly.dll").write_bytes(b"dll")

        assert ida_main._select_ida_database(database).name == expected_name

    def test_select_ida_database_raises_when_i64_and_dll_are_missing(self, tmp_path: Path) -> None:
        database = tmp_path / "GameAssembly.dll.i64"

        with (
            patch.object(ida_main, "OBF_GAME_ASSEMBLY_DLL_I64", database),
            pytest.raises(FileNotFoundError) as exc_info,
        ):
            ida_main._select_ida_database(database)

        assert str(database) in str(exc_info.value)

    def test_run_ida_script_passes_progress_path_and_removes_temp_file(self, tmp_path: Path) -> None:
        captured_env: dict[str, str] = {}
        database_path = tmp_path / "GameAssembly.dll"
        database_path.write_bytes(b"dll")

        def fake_popen(
            _command: list[str],
            *,
            stdout: int,
            stderr: int,
            text: bool,
            env: dict[str, str],
        ) -> _FakeProcess:
            del stdout, stderr, text
            captured_env.update(env)
            return _FakeProcess()

        with (
            patch.object(ida_main.subprocess, "Popen", side_effect=fake_popen),
            patch.object(
                ida_main,
                "start_progress_watcher",
                return_value=(threading.Event(), _CompletedThread()),
            ),
        ):
            ida_main.run_ida_script(
                use_non_obf=True,
                ida_exe=Path("ida.exe"),
                script_path=Path("trace.py"),
                database_path=database_path,
            )

        progress_path = Path(captured_env["PROTO_TRACER_PROGRESS_PATH"])
        assert captured_env["PROTO_TRACER_BASE_DIR"] == str(ida_main.NON_OBFUSCATED_DATA_DIR)
        assert not progress_path.exists()

    def test_run_ida_script_uses_explicit_base_dir_and_database_path(self, tmp_path: Path) -> None:
        captured_env: dict[str, str] = {}
        captured_command: list[str] = []
        base_dir = tmp_path / "20_05_2026"
        database_path = base_dir / "GameAssembly.dll.i64"
        database_path.parent.mkdir(parents=True)
        database_path.write_bytes(b"i64")

        def fake_popen(
            command: list[str],
            *,
            stdout: int,
            stderr: int,
            text: bool,
            env: dict[str, str],
        ) -> _FakeProcess:
            del stdout, stderr, text
            captured_command.extend(command)
            captured_env.update(env)
            return _FakeProcess()

        with (
            patch.object(ida_main.subprocess, "Popen", side_effect=fake_popen),
            patch.object(
                ida_main,
                "start_progress_watcher",
                return_value=(threading.Event(), _CompletedThread()),
            ),
        ):
            ida_main.run_ida_script(
                use_non_obf=False,
                ida_exe=Path("ida.exe"),
                script_path=Path("trace.py"),
                base_dir=base_dir,
                database_path=database_path,
            )

        progress_path = Path(captured_env["PROTO_TRACER_PROGRESS_PATH"])
        assert captured_env["PROTO_TRACER_BASE_DIR"] == str(base_dir)
        assert captured_command == ["ida.exe", "-A", "-Strace.py", str(database_path)]
        assert not progress_path.exists()

    def test_run_ida_script_raises_system_exit_for_failed_ida_process(self, tmp_path: Path) -> None:
        captured_env: dict[str, str] = {}
        database_path = tmp_path / "GameAssembly.dll"
        database_path.write_bytes(b"dll")

        def fake_popen(
            _command: list[str],
            *,
            stdout: int,
            stderr: int,
            text: bool,
            env: dict[str, str],
        ) -> _FakeProcess:
            del stdout, stderr, text
            captured_env.update(env)
            return _FakeProcess(return_code=7)

        with (
            patch.object(ida_main.subprocess, "Popen", side_effect=fake_popen),
            patch.object(
                ida_main,
                "start_progress_watcher",
                return_value=(threading.Event(), _CompletedThread()),
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            ida_main.run_ida_script(
                use_non_obf=True,
                ida_exe=Path("ida.exe"),
                script_path=Path("trace.py"),
                database_path=database_path,
            )

        progress_path = Path(captured_env["PROTO_TRACER_PROGRESS_PATH"])
        assert exc_info.value.code == 7
        assert not progress_path.exists()

    def test_watch_progress_file_renders_valid_events_and_ignores_invalid_lines(self, tmp_path: Path) -> None:
        progress_path = tmp_path / "progress.jsonl"
        progress_path.write_text(
            '{"phase": "scan_methods", "current": 1, "total": 2, "label": "Scan methods"}\n'
            "not json\n"
            '{"phase": "scan_methods", "current": 2, "total": 2, "label": "Scan methods", "done": true}',
            encoding="utf-8",
        )
        stop_event = threading.Event()
        stop_event.set()
        stream = io.StringIO()

        reporter._watch_progress_file(progress_path, stop_event, stream)

        output = stream.getvalue()
        assert "Scan methods [############------------]  50.0% 1/2" in output
        assert "Scan methods [########################] 100.0% 2/2" in output
