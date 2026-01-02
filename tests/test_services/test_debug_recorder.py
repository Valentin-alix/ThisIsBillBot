import os
import time
from pathlib import Path

from src.services.debug_recorder import recorder


def test_prune_bot_debug_sessions_removes_only_expired_files(tmp_path: Path) -> None:
    active_session = tmp_path / "active.debug.jsonl"
    active_session.touch()
    expired_session = tmp_path / "expired.debug.jsonl.gz"
    expired_session.touch()
    expired_at = time.time() - 8 * 24 * 60 * 60
    os.utime(
        expired_session,
        (expired_at, expired_at),
    )
    recent_sessions = [tmp_path / f"recent-{index}.debug.jsonl.gz" for index in range(11)]
    for session in recent_sessions:
        session.touch()

    recorder._prune_bot_debug_sessions(tmp_path, active_session)

    assert not expired_session.exists()
    assert active_session.exists()
    assert all(session.exists() for session in recent_sessions)
