import os
import subprocess
import sys

import pytest


@pytest.mark.parametrize("packaged", [False, True])
def test_packaging_disables_capture_and_profiling(packaged: bool) -> None:
    code = f"""
import sys
sys.frozen = {packaged!r}
from src.core.config import ENABLE_MSG_CAPTURE
from src.gui.utils.profiling import PROFILING_ENABLED
assert ENABLE_MSG_CAPTURE is {(not packaged)!r}
assert PROFILING_ENABLED is {(not packaged)!r}
"""
    environment = dict(
        os.environ,
        DEBUG="1",
        ENABLE_MSG_CAPTURE="1",
        PROFILING_ENABLED="1",
        PYTHON_DOTENV_DISABLED="1",
    )
    result = subprocess.run(
        [sys.executable, "-c", code], env=environment, capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, result.stderr
