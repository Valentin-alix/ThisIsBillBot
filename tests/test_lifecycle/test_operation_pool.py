from pathlib import Path

from src.core.bot.lifecycle.operation_pool import (
    ONE_HOUR_SEC,
    OperationPool,
)

IP_A = "192.168.1.10"
IP_B = "192.168.1.11"


def _pool(tmp_path: Path) -> OperationPool:
    return OperationPool(path=str(tmp_path / "account_operations.json"))


class TestOperationPool:
    def test_fresh_pool_has_quota(self, tmp_path: Path) -> None:
        pool = _pool(tmp_path)

        assert pool.has_quota(IP_A, now=0.0)

    def test_hourly_cap_blocks_after_two_attempts(self, tmp_path: Path) -> None:
        pool = _pool(tmp_path)
        pool.record(IP_A, now=0.0)
        pool.record(IP_A, now=10.0)

        assert not pool.has_quota(IP_A, now=20.0)

    def test_quota_is_independent_per_ip(self, tmp_path: Path) -> None:
        pool = _pool(tmp_path)
        # Saturate IP_A's hourly cap; IP_B is untouched.
        pool.record(IP_A, now=0.0)
        pool.record(IP_A, now=10.0)

        assert not pool.has_quota(IP_A, now=20.0)
        assert pool.has_quota(IP_B, now=20.0)

    def test_hourly_window_frees_up_while_daily_quota_remains(
        self, tmp_path: Path
    ) -> None:
        pool = _pool(tmp_path)
        pool.record(IP_A, now=0.0)
        pool.record(IP_A, now=10.0)

        # Both attempts are now older than one hour: hourly quota is free again
        # and only 2 of the 4 daily slots are used.
        assert pool.has_quota(IP_A, now=ONE_HOUR_SEC + 20.0)

    def test_daily_cap_blocks_even_when_hourly_window_is_clear(
        self, tmp_path: Path
    ) -> None:
        pool = _pool(tmp_path)
        # Four attempts spaced more than an hour apart: hourly cap is never the
        # limiter, but the daily cap of 4 is reached.
        for index in range(4):
            pool.record(IP_A, now=index * (ONE_HOUR_SEC + 1))

        last = 3 * (ONE_HOUR_SEC + 1)
        assert not pool.has_quota(IP_A, now=last + 1.0)

    def test_daily_window_resets_after_24h(self, tmp_path: Path) -> None:
        pool = _pool(tmp_path)
        for index in range(4):
            pool.record(IP_A, now=index * (ONE_HOUR_SEC + 1))

        # A full day after the last attempt, every slot has aged out.
        assert pool.has_quota(IP_A, now=4 * 24 * ONE_HOUR_SEC)

    def test_attempts_survive_reload(self, tmp_path: Path) -> None:
        path = str(tmp_path / "account_operations.json")
        first = OperationPool(path=path)
        first.record(IP_A, now=0.0)
        first.record(IP_A, now=10.0)

        reloaded = OperationPool(path=path)

        assert not reloaded.has_quota(IP_A, now=20.0)

    def test_old_attempts_are_pruned_from_disk(self, tmp_path: Path) -> None:
        path = str(tmp_path / "account_operations.json")
        pool = OperationPool(path=path)
        pool.record(IP_A, now=0.0)
        # A record more than a day later prunes the stale entry.
        pool.record(IP_A, now=2 * 24 * ONE_HOUR_SEC)

        reloaded = OperationPool(path=path)
        # Only the recent attempt remains, so hourly/daily quota is available.
        assert reloaded.has_quota(IP_A, now=2 * 24 * ONE_HOUR_SEC + 20.0)


class TestAvailableIp:
    def test_returns_an_ip_with_quota(self, tmp_path: Path) -> None:
        pool = _pool(tmp_path)

        assert pool.available_ip([IP_A, IP_B], now=0.0) in {IP_A, IP_B}

    def test_skips_saturated_ip(self, tmp_path: Path) -> None:
        pool = _pool(tmp_path)
        pool.record(IP_A, now=0.0)
        pool.record(IP_A, now=10.0)

        assert pool.available_ip([IP_A, IP_B], now=20.0) == IP_B

    def test_returns_none_when_all_saturated(self, tmp_path: Path) -> None:
        pool = _pool(tmp_path)
        for ip in (IP_A, IP_B):
            pool.record(ip, now=0.0)
            pool.record(ip, now=10.0)

        assert pool.available_ip([IP_A, IP_B], now=20.0) is None

    def test_prefers_least_recently_used_ip(self, tmp_path: Path) -> None:
        pool = _pool(tmp_path)
        # IP_A has one recent attempt; IP_B has none, so it is preferred.
        pool.record(IP_A, now=0.0)

        assert pool.available_ip([IP_A, IP_B], now=10.0) == IP_B
