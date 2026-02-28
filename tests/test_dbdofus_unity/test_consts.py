import subprocess
import sys
from pathlib import Path


def test_runtime_store_import_does_not_require_the_dofus_toolchain() -> None:
    source = """
import os
from pathlib import Path

import project_paths

project_paths.ENV_PATH = Path.cwd() / "missing-test.env"
for variable in ("OBF_GAME_DIR", "NON_OBF_GAME_DIR", "PROTOC_PATH", "IDA_EXE"):
    os.environ.pop(variable, None)

from DBDofusUnity.consts import require_game_toolchain
from DBDofusUnity.proto_mapper_assembly.runtime import runtime_store

assert runtime_store.RuntimeDataStore
try:
    require_game_toolchain()
except ValueError as error:
    assert str(error) == "Missing required path environment variable: OBF_GAME_DIR"
else:
    raise AssertionError("The missing Dofus toolchain must fail when it is used.")
"""
    result = subprocess.run(
        [sys.executable, "-c", source],
        cwd=Path(__file__).parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
