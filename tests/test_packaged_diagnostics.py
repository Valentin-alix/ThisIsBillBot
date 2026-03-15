import os
import subprocess
import sys

import pytest


@pytest.mark.parametrize("packaged", [False, True])
@pytest.mark.parametrize("debug", [False, True])
@pytest.mark.parametrize("capture", [False, True])
def test_packaged_capture_is_never_enabled(packaged: bool, debug: bool, capture: bool) -> None:
    code = f"""
import sys
sys.frozen = {packaged!r}
from src.core.config import DEBUG, ENABLE_MSG_CAPTURE
from src.gui.utils.profiling import PROFILING_ENABLED
assert DEBUG is {debug!r}
assert ENABLE_MSG_CAPTURE is {(capture and not packaged)!r}
assert PROFILING_ENABLED is {(not packaged)!r}
"""
    environment = dict(
        os.environ,
        DEBUG=str(int(debug)),
        ENABLE_MSG_CAPTURE=str(int(capture)),
        PROFILING_ENABLED="1",
        PYTHON_DOTENV_DISABLED="1",
    )
    result = subprocess.run(
        [sys.executable, "-c", code], env=environment, capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, result.stderr
