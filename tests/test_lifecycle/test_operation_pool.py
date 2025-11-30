from unittest.mock import MagicMock

from src.core.bot.lifecycle.operation_pool import OperationPool


def _pool() -> OperationPool:
    proxy_controller = MagicMock()
    proxy_controller.get_operation_timestamps.return_value = {}
    proxy_controller.get_register_cooldowns.return_value = {}
    return OperationPool(proxy_controller=proxy_controller)


def test_has_quota_for_requires_room_in_both_windows() -> None:
    pool = _pool()
    now = 1_000_000.0

    assert pool.has_quota_for("proxy", 2, now)

    pool.record("proxy", now)
    assert pool.has_quota_for("proxy", 1, now)
    assert not pool.has_quota_for("proxy", 2, now)

    pool.record("proxy", now)
    assert not pool.has_quota_for("proxy", 1, now)
    assert not pool.has_quota("proxy", now)
