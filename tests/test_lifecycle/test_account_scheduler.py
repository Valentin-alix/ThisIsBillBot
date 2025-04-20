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


class _SyncThread:
    """Drop-in for ``threading.Thread`` that runs the target inline."""

    def __init__(self, target: Callable[..., None], args: tuple[object, ...] = ()) -> None:
        self._target = target
        self._args = args

    def start(self) -> None:
        self._target(*self._args)


class _FakePool:
    def __init__(self, *, quota: bool) -> None:
        self.quota = quota
        self.records = 0

    def has_quota(self, now: float | None = None) -> bool:
        return self.quota

    def record(self, now: float | None = None) -> None:
        self.records += 1


class _FakeSubscribeInfo:
    def __init__(self, *, active_beyond_threshold: bool) -> None:
        self._active = active_beyond_threshold

    def is_active_beyond_threshold(self) -> bool:
        return self._active


class _FakeStorage:
    def __init__(self, info_by_login: dict[str, _FakeSubscribeInfo]) -> None:
        self._info_by_login = info_by_login

    def get_subscribe_info(self, login: str) -> _FakeSubscribeInfo:
        return self._info_by_login[login]


class _FakeSubscribeService:
    def __init__(self, info_by_login: dict[str, _FakeSubscribeInfo] | None = None) -> None:
        self.storage = _FakeStorage(info_by_login or {})
        self.runs: list[str] = []

    def run(self, login: str, options: object) -> SubscribeResult:
        self.runs.append(login)
        return SubscribeResult.failed("stub")


class _FakeConfigController:
    def __init__(self, configs: dict[str, BotConfig]) -> None:
        self._configs = configs

    def get_bot_config_by_login(self) -> dict[str, BotConfig]:
        return self._configs


def _make_scheduler(
    quota: bool,
    *,
    configs: dict[str, BotConfig] | None = None,
    subscribe_info: dict[str, _FakeSubscribeInfo] | None = None,
) -> AccountScheduler:
    scheduler = AccountScheduler(
        on_accounts_synchronized=MagicMock(),
        bot_config_controller=_FakeConfigController(configs or {}),  # type: ignore[arg-type]
        subscribe_service=_FakeSubscribeService(subscribe_info),  # type: ignore[arg-type]
    )
    scheduler._pool = _FakePool(quota=quota)  # type: ignore[assignment]
    return scheduler


def _sub_config(*, auto_subscribe: bool = True, proxy: str | None = None) -> BotConfig:
    return BotConfig(auto_subscribe=auto_subscribe, subscribe_proxy=proxy)


class TestNextOperation:
    def test_auth_is_preferred_over_everything(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(MODULE + ".load_available_generated_accounts", lambda: ["acc"])
        monkeypatch.setattr(MODULE + ".count_available_emails", lambda: 5)

        scheduler = _make_scheduler(
            quota=True,
            configs={"sub@x.com": _sub_config()},
            subscribe_info={"sub@x.com": _FakeSubscribeInfo(active_beyond_threshold=False)},
        )
        assert scheduler._next_operation() == _AuthOp()

    def test_subscribe_is_preferred_over_register(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        no_accounts: list[str] = []
        monkeypatch.setattr(MODULE + ".load_available_generated_accounts", lambda: no_accounts)
        monkeypatch.setattr(MODULE + ".count_available_emails", lambda: 5)

        scheduler = _make_scheduler(
            quota=True,
            configs={"sub@x.com": _sub_config(proxy="http://p")},
            subscribe_info={"sub@x.com": _FakeSubscribeInfo(active_beyond_threshold=False)},
        )
        operation = scheduler._next_operation()
        assert operation == _SubscribeOp("sub@x.com", account_scheduler_module.SubscribeOptions(proxy="http://p"))

    def test_register_when_no_auth_or_subscription_pending(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        no_accounts: list[str] = []
        monkeypatch.setattr(MODULE + ".load_available_generated_accounts", lambda: no_accounts)
        monkeypatch.setattr(MODULE + ".count_available_emails", lambda: 3)

        scheduler = _make_scheduler(
            quota=True,
            configs={"sub@x.com": _sub_config()},
            subscribe_info={"sub@x.com": _FakeSubscribeInfo(active_beyond_threshold=True)},
        )
        assert scheduler._next_operation() == _RegisterOp()

    def test_none_when_no_work(self, monkeypatch: pytest.MonkeyPatch) -> None:
        no_accounts: list[str] = []
        monkeypatch.setattr(MODULE + ".load_available_generated_accounts", lambda: no_accounts)
        monkeypatch.setattr(MODULE + ".count_available_emails", lambda: 0)

        assert _make_scheduler(quota=True)._next_operation() is None


class TestNextSubscriptionTarget:
    def test_active_account_is_skipped(self) -> None:
        scheduler = _make_scheduler(
            quota=True,
            configs={"active@x.com": _sub_config()},
            subscribe_info={"active@x.com": _FakeSubscribeInfo(active_beyond_threshold=True)},
        )
        assert scheduler._next_subscription_target() is None

    def test_non_auto_subscribe_account_is_skipped(self) -> None:
        scheduler = _make_scheduler(
            quota=True,
            configs={"opt-out@x.com": _sub_config(auto_subscribe=False)},
            subscribe_info={"opt-out@x.com": _FakeSubscribeInfo(active_beyond_threshold=False)},
        )
        assert scheduler._next_subscription_target() is None

    def test_failing_account_is_skipped_and_next_is_evaluated(self) -> None:
        scheduler = _make_scheduler(
            quota=True,
            configs={
                "boom@x.com": _sub_config(),
                "ok@x.com": _sub_config(),
            },
            # "boom@x.com" missing from storage -> KeyError -> skipped.
            subscribe_info={"ok@x.com": _FakeSubscribeInfo(active_beyond_threshold=False)},
        )
        assert scheduler._next_subscription_target() == _SubscribeOp(
            "ok@x.com", account_scheduler_module.SubscribeOptions(proxy=None)
        )


class TestTick:
    def test_tick_consumes_a_slot_and_runs_auth(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(MODULE + ".load_available_generated_accounts", lambda: ["acc"])
        monkeypatch.setattr(MODULE + ".count_available_emails", lambda: 0)
        monkeypatch.setattr(account_scheduler_module.threading, "Thread", _SyncThread)

        async def fake_auth() -> AuthenticationResult:
            return AuthenticationResult(success=True, email="bot@x.com")

        monkeypatch.setattr(MODULE + ".authenticate_next_available_account", fake_auth)

        scheduler = _make_scheduler(quota=True)
        scheduler._tick()

        pool: _FakePool = scheduler._pool  # type: ignore[assignment]
        assert pool.records == 1
        assert scheduler.on_accounts_synchronized is not None
        scheduler.on_accounts_synchronized.assert_called_once()  # type: ignore[attr-defined]
        assert scheduler._operation_in_progress is False

    def test_tick_does_nothing_without_quota(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(MODULE + ".load_available_generated_accounts", lambda: ["acc"])
        monkeypatch.setattr(MODULE + ".count_available_emails", lambda: 0)

        started = MagicMock()
        monkeypatch.setattr(account_scheduler_module.threading, "Thread", started)

        scheduler = _make_scheduler(quota=False)
        scheduler._tick()

        pool: _FakePool = scheduler._pool  # type: ignore[assignment]
        assert pool.records == 0
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
        assert pool.records == 0
        started.assert_not_called()


class TestRunOperation:
    def test_failed_auth_does_not_synchronize(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        async def fake_auth() -> AuthenticationResult:
            return AuthenticationResult(success=False, email="bot@x.com", error="boom")

        monkeypatch.setattr(MODULE + ".authenticate_next_available_account", fake_auth)

        scheduler = _make_scheduler(quota=True)
        scheduler._operation_in_progress = True
        scheduler._run_operation(_AuthOp())

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
        scheduler._run_operation(_RegisterOp())

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
