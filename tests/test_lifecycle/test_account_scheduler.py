from typing import Callable
from unittest.mock import MagicMock

import pytest
from ankama_launcher_emulator_premium.web.auth.models import (
    AuthenticationResult,
    RegistrationResult,
)
from ankama_launcher_emulator_premium.web.subscription.models import SubscribeResult

from src.controller.bot_config import BotConfig
from src.core.bot.lifecycle import account_scheduler as account_scheduler_module
from src.core.bot.lifecycle.account_scheduler import (
    AccountScheduler,
    _AuthOp,
    _RegisterOp,
    _SubscribeOp,
)

MODULE = "src.core.bot.lifecycle.account_scheduler"

IP = "192.168.1.50"
IP_B = "192.168.1.51"


def _patch_interfaces(monkeypatch: pytest.MonkeyPatch, *ips: str) -> None:
    interfaces = {ip: (f"eth{index}", "1.2.3.4") for index, ip in enumerate(ips)}
    monkeypatch.setattr(
        MODULE + ".get_available_network_interfaces", lambda: interfaces
    )


class _SyncThread:
    """Drop-in for ``threading.Thread`` that runs the target inline."""

    def __init__(
        self, target: Callable[..., None], args: tuple[object, ...] = ()
    ) -> None:
        self._target = target
        self._args = args

    def start(self) -> None:
        self._target(*self._args)


class _FakePool:
    def __init__(self, *, quota: bool) -> None:
        self.quota = quota
        self.records: list[str] = []

    def has_quota(self, ip: str, now: float | None = None) -> bool:
        return self.quota

    def available_ip(self, ips: list[str], now: float | None = None) -> str | None:
        return ips[0] if self.quota and ips else None

    def record(self, ip: str, now: float | None = None) -> None:
        self.records.append(ip)


class _SelectivePool:
    """Pool where specific IPs are saturated and ``available_ip`` hands out a chosen one."""

    def __init__(self, *, no_quota: set[str], available: str | None) -> None:
        self._no_quota = no_quota
        self._available = available
        self.records: list[str] = []

    def has_quota(self, ip: str, now: float | None = None) -> bool:
        return ip not in self._no_quota

    def available_ip(self, ips: list[str], now: float | None = None) -> str | None:
        return self._available if self._available in ips else None

    def record(self, ip: str, now: float | None = None) -> None:
        self.records.append(ip)


class _FakeSubscribeInfo:
    def __init__(self, *, active_beyond_threshold: bool) -> None:
        self._active = active_beyond_threshold

    def is_active_beyond_threshold(self) -> bool:
        return self._active


class _FakeStorage:
    def __init__(self, info_by_login: dict[str, _FakeSubscribeInfo]) -> None:
        self._info_by_login = info_by_login

    def get_subscribe_info(self, login: str) -> _FakeSubscribeInfo | None:
        return self._info_by_login.get(login)


class _FakeSubscribeService:
    def __init__(
        self, info_by_login: dict[str, _FakeSubscribeInfo] | None = None
    ) -> None:
        self.storage = _FakeStorage(info_by_login or {})
        self.runs: list[str] = []

    def run(self, login: str, options: object) -> SubscribeResult:
        self.runs.append(login)
        return SubscribeResult.failed("stub")


class _FakeConfigController:
    def __init__(
        self,
        configs: dict[str, BotConfig],
        profile_ips: dict[str, str] | None = None,
    ) -> None:
        self._configs = configs
        self._profile_ips = profile_ips or {"A": IP, "B": IP_B}

    def get_bot_config_by_login(self) -> dict[str, BotConfig]:
        return self._configs

    def resolve_bot_network_interface(
        self, config: BotConfig | None, available_interfaces: list[str]
    ) -> str | None:
        if config is None or config.schedule_profile is None:
            return None
        interface_ip = self._profile_ips.get(config.schedule_profile)
        if interface_ip not in available_interfaces:
            return None
        return interface_ip


def _make_scheduler(
    quota: bool,
    *,
    configs: dict[str, BotConfig] | None = None,
    subscribe_info: dict[str, _FakeSubscribeInfo] | None = None,
) -> AccountScheduler:
    scheduler = AccountScheduler(
        on_accounts_synchronized=MagicMock(),
        bot_config_controller=_FakeConfigController(configs or {}),  # type: ignore
        subscribe_service=_FakeSubscribeService(subscribe_info),  # type: ignore
        on_subscribed=lambda _: None,
    )
    scheduler._pool = _FakePool(quota=quota)  # type: ignore[assignment]
    return scheduler


def _sub_config(*, schedule_profile: str | None = "A") -> BotConfig:
    return BotConfig(schedule_profile=schedule_profile)


class TestNextOperation:
    def test_subscription_is_preferred_over_everything(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            MODULE + ".load_available_generated_accounts", lambda: ["acc"]
        )
        monkeypatch.setattr(MODULE + ".count_available_emails", lambda: 5)

        scheduler = _make_scheduler(
            quota=True,
            configs={"sub@x.com": _sub_config()},
            subscribe_info={
                "sub@x.com": _FakeSubscribeInfo(active_beyond_threshold=False)
            },
        )
        assert scheduler._next_operation([IP], 0.0) == _SubscribeOp(
            "sub@x.com",
            account_scheduler_module.SubscribeOptions(interface_ip=IP),
        )

    def test_auth_is_preferred_over_register(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            MODULE + ".load_available_generated_accounts", lambda: ["acc"]
        )
        monkeypatch.setattr(MODULE + ".count_available_emails", lambda: 5)

        scheduler = _make_scheduler(
            quota=True,
            configs={"sub@x.com": _sub_config()},
            subscribe_info={
                "sub@x.com": _FakeSubscribeInfo(active_beyond_threshold=True)
            },
        )
        assert scheduler._next_operation([IP], 0.0) == _AuthOp(IP)

    def test_subscribe_is_preferred_over_register(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        no_accounts: list[str] = []
        monkeypatch.setattr(
            MODULE + ".load_available_generated_accounts", lambda: no_accounts
        )
        monkeypatch.setattr(MODULE + ".count_available_emails", lambda: 5)

        scheduler = _make_scheduler(
            quota=True,
            configs={"sub@x.com": _sub_config()},
            subscribe_info={
                "sub@x.com": _FakeSubscribeInfo(active_beyond_threshold=False)
            },
        )
        operation = scheduler._next_operation([IP], 0.0)
        assert operation == _SubscribeOp(
            "sub@x.com",
            account_scheduler_module.SubscribeOptions(interface_ip=IP),
        )

    def test_register_when_no_auth_or_subscription_pending(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        no_accounts: list[str] = []
        monkeypatch.setattr(
            MODULE + ".load_available_generated_accounts", lambda: no_accounts
        )
        monkeypatch.setattr(MODULE + ".count_available_emails", lambda: 3)

        scheduler = _make_scheduler(
            quota=True,
            configs={"sub@x.com": _sub_config()},
            subscribe_info={
                "sub@x.com": _FakeSubscribeInfo(active_beyond_threshold=True)
            },
        )
        assert scheduler._next_operation([IP], 0.0) == _RegisterOp(IP)

    def test_subscription_on_saturated_ip_falls_through_to_auth(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # The due subscription is pinned to profile A's IP (no quota), but a second interface
        # IP_B still has quota, so auth proceeds there instead of stalling.
        monkeypatch.setattr(
            MODULE + ".load_available_generated_accounts", lambda: ["acc"]
        )
        monkeypatch.setattr(MODULE + ".count_available_emails", lambda: 0)

        scheduler = _make_scheduler(
            quota=True,
            configs={"sub@x.com": _sub_config()},
            subscribe_info={
                "sub@x.com": _FakeSubscribeInfo(active_beyond_threshold=False)
            },
        )
        # Pool reports the subscription's IP as saturated but hands out IP_B for auth.
        scheduler._pool = _SelectivePool(  # type: ignore[assignment]
            no_quota={IP}, available=IP_B
        )
        assert scheduler._next_operation([IP, IP_B], 0.0) == _AuthOp(IP_B)

    def test_none_when_no_work(self, monkeypatch: pytest.MonkeyPatch) -> None:
        no_accounts: list[str] = []
        monkeypatch.setattr(
            MODULE + ".load_available_generated_accounts", lambda: no_accounts
        )
        monkeypatch.setattr(MODULE + ".count_available_emails", lambda: 0)

        assert _make_scheduler(quota=True)._next_operation([IP], 0.0) is None


class TestNextSubscriptionTarget:
    def test_active_account_is_skipped(self) -> None:
        scheduler = _make_scheduler(
            quota=True,
            configs={"active@x.com": _sub_config()},
            subscribe_info={
                "active@x.com": _FakeSubscribeInfo(active_beyond_threshold=True)
            },
        )
        assert scheduler._next_subscription_target([IP], 0.0) is None

    def test_account_without_profile_is_skipped(self) -> None:
        scheduler = _make_scheduler(
            quota=True,
            configs={"no-profile@x.com": _sub_config(schedule_profile=None)},
            subscribe_info={
                "no-profile@x.com": _FakeSubscribeInfo(active_beyond_threshold=False)
            },
        )
        assert scheduler._next_subscription_target([IP], 0.0) is None

    def test_account_without_local_record_is_skipped(self) -> None:
        scheduler = _make_scheduler(
            quota=True,
            configs={
                "boom@x.com": _sub_config(),
                "ok@x.com": _sub_config(),
            },
            # "boom@x.com" has not signed on yet -> no local record -> None -> skipped.
            subscribe_info={
                "ok@x.com": _FakeSubscribeInfo(active_beyond_threshold=False)
            },
        )
        assert scheduler._next_subscription_target([IP], 0.0) == _SubscribeOp(
            "ok@x.com", account_scheduler_module.SubscribeOptions(interface_ip=IP)
        )


class TestTick:
    def test_tick_consumes_a_slot_and_runs_auth(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            MODULE + ".load_available_generated_accounts", lambda: ["acc"]
        )
        monkeypatch.setattr(MODULE + ".count_available_emails", lambda: 0)
        monkeypatch.setattr(account_scheduler_module.threading, "Thread", _SyncThread)
        _patch_interfaces(monkeypatch, IP)

        captured: list[str | None] = []

        async def fake_auth(interface_ip: str | None = None) -> AuthenticationResult:
            captured.append(interface_ip)
            return AuthenticationResult(success=True, email="bot@x.com")

        monkeypatch.setattr(MODULE + ".authenticate_next_available_account", fake_auth)

        scheduler = _make_scheduler(quota=True)
        scheduler._tick()

        pool: _FakePool = scheduler._pool  # type: ignore[assignment]
        assert pool.records == [IP]
        assert captured == [IP]
        assert scheduler.on_accounts_synchronized is not None
        scheduler.on_accounts_synchronized.assert_called_once()  # type: ignore[attr-defined]
        assert scheduler._operation_in_progress is False

    def test_tick_does_nothing_without_quota(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            MODULE + ".load_available_generated_accounts", lambda: ["acc"]
        )
        monkeypatch.setattr(MODULE + ".count_available_emails", lambda: 0)
        _patch_interfaces(monkeypatch, IP)

        started = MagicMock()
        monkeypatch.setattr(account_scheduler_module.threading, "Thread", started)

        scheduler = _make_scheduler(quota=False)
        scheduler._tick()

        pool: _FakePool = scheduler._pool  # type: ignore[assignment]
        assert pool.records == []
        started.assert_not_called()

    def test_tick_does_nothing_without_available_interfaces(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            MODULE + ".load_available_generated_accounts", lambda: ["acc"]
        )
        monkeypatch.setattr(MODULE + ".count_available_emails", lambda: 0)
        _patch_interfaces(monkeypatch)  # no interfaces up

        started = MagicMock()
        monkeypatch.setattr(account_scheduler_module.threading, "Thread", started)

        scheduler = _make_scheduler(quota=True)
        scheduler._tick()

        pool: _FakePool = scheduler._pool  # type: ignore[assignment]
        assert pool.records == []
        started.assert_not_called()

    def test_tick_skips_when_operation_in_progress(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        started = MagicMock()
        monkeypatch.setattr(account_scheduler_module.threading, "Thread", started)

        scheduler = _make_scheduler(quota=True)
        scheduler._operation_in_progress = True
        scheduler._tick()

        pool: _FakePool = scheduler._pool  # type: ignore[assignment]
        assert pool.records == []
        started.assert_not_called()


class TestRunOperation:
    def test_failed_auth_does_not_synchronize(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        async def fake_auth(interface_ip: str | None = None) -> AuthenticationResult:
            return AuthenticationResult(success=False, email="bot@x.com", error="boom")

        monkeypatch.setattr(MODULE + ".authenticate_next_available_account", fake_auth)

        scheduler = _make_scheduler(quota=True)
        scheduler._operation_in_progress = True
        scheduler._run_operation(_AuthOp(IP))

        scheduler.on_accounts_synchronized.assert_not_called()  # type: ignore[attr-defined]
        assert scheduler._operation_in_progress is False

    def test_register_runs_without_synchronizing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        calls: list[str] = []

        async def fake_register() -> RegistrationResult:
            calls.append("register")
            return RegistrationResult(True, "bot@x.com", "pw", "url")

        monkeypatch.setattr(MODULE + ".register_next_available_email", fake_register)

        scheduler = _make_scheduler(quota=True)
        scheduler._operation_in_progress = True
        scheduler._run_operation(_RegisterOp(IP))

        assert calls == ["register"]
        scheduler.on_accounts_synchronized.assert_not_called()  # type: ignore[attr-defined]
        assert scheduler._operation_in_progress is False

    def test_subscribe_runs_service_without_synchronizing(self) -> None:
        scheduler = _make_scheduler(quota=True)
        scheduler._operation_in_progress = True
        scheduler._run_operation(
            _SubscribeOp("sub@x.com", account_scheduler_module.SubscribeOptions())
        )

        service: _FakeSubscribeService = scheduler.subscribe_service  # type: ignore[assignment]
        assert service.runs == ["sub@x.com"]
        scheduler.on_accounts_synchronized.assert_not_called()  # type: ignore[attr-defined]
        assert scheduler._operation_in_progress is False
