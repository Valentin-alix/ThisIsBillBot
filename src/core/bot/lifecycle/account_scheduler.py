import asyncio
import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine

import schedule
from ankama_launcher_emulator_premium.utils.internet import (
    get_available_network_interfaces,
)
from ankama_launcher_emulator_premium.web.auth.launcher_login import (
    authenticate_next_available_account,
)
from ankama_launcher_emulator_premium.web.auth.registration import (
    count_available_emails,
    register_next_available_email,
)
from ankama_launcher_emulator_premium.web.auth.storage import (
    load_available_generated_accounts,
)
from ankama_launcher_emulator_premium.web.subscription.models import (
    SubscribeOptions,
    SubscribeStatus,
)
from ankama_launcher_emulator_premium.web.subscription.service import (
    SubscribeService,
    _build_subscribe_service,
)

from src.controller.bot_config import BotConfigController
from src.core.bot.lifecycle.operation_pool import OperationPool
from src.exceptions import UnavailableNetworkInterface

logger = logging.getLogger()

TICK_INTERVAL_MINUTES = 5


@dataclass(frozen=True)
class _AuthOp:
    """Authenticate the next available generated account on ``interface_ip``."""

    interface_ip: str | None


@dataclass(frozen=True)
class _RegisterOp:
    """Create the next account from the available-emails queue, charged to ``interface_ip``."""

    interface_ip: str | None


@dataclass(frozen=True)
class _SubscribeOp:
    """Renew the subscription of a single ``auto_subscribe`` account."""

    login: str
    options: SubscribeOptions


PendingOperation = _AuthOp | _RegisterOp | _SubscribeOp


def _ip_of(operation: PendingOperation) -> str | None:
    """The source IP an operation is charged against in the quota pool."""
    match operation:
        case _SubscribeOp(options=options):
            return options.interface_ip
        case _AuthOp(interface_ip=ip) | _RegisterOp(interface_ip=ip):
            return ip


def _run_async[T](coro: Coroutine[Any, Any, T]) -> T:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@dataclass
class AccountScheduler:
    """Drives account auth, creation and subscription from a shared rate-limit pool.

    Ankama caps these operations at 2 per rolling hour and 4 per rolling day, all
    drawing from the same pool. The scheduler ticks periodically and, whenever quota
    is available, performs a single operation — preferring authentication (which
    turns an already-created account into a usable bot), then subscription renewal
    (which keeps existing bots active), then creating a new account.
    """

    on_accounts_synchronized: Callable[[], None]
    on_subscribed: Callable[[str], None]
    bot_config_controller: BotConfigController = field(
        default_factory=BotConfigController
    )
    subscribe_service: SubscribeService = field(
        default_factory=_build_subscribe_service
    )
    _job: schedule.Job | None = field(init=False, default=None)
    _pool: OperationPool = field(init=False, default_factory=OperationPool)
    _lock: threading.Lock = field(init=False, default_factory=threading.Lock)
    _operation_in_progress: bool = field(init=False, default=False)

    def start(self) -> None:
        assert self._job is None, "Scheduler is already started"
        self._job = schedule.every(TICK_INTERVAL_MINUTES).minutes.do(self._tick)
        logger.info(
            f"Account scheduler armed: one operation every {TICK_INTERVAL_MINUTES} min "
        )

    def _tick(self) -> None:
        with self._lock:
            if self._operation_in_progress:
                return
            now = time.time()
            available_ips = list(get_available_network_interfaces().keys())
            if not available_ips:
                return
            operation = self._next_operation(available_ips, now)
            if operation is None:
                return
            ip = _ip_of(operation)
            assert ip is not None, "selected operation must carry an IP"
            self._pool.record(ip, now)
            self._operation_in_progress = True

        threading.Thread(target=self._run_operation, args=(operation,)).start()

    def _next_operation(
        self, available_ips: list[str], now: float
    ) -> PendingOperation | None:
        subscription = self._next_subscription_target(available_ips, now)
        if subscription is not None:
            return subscription
        ip = self._pool.available_ip(available_ips, now)
        if ip is None:
            return None
        if load_available_generated_accounts():
            return _AuthOp(ip)
        if count_available_emails() > 0:
            return _RegisterOp(ip)
        return None

    def _next_subscription_target(
        self, available_ips: list[str], now: float
    ) -> _SubscribeOp | None:
        configs = self.bot_config_controller.get_bot_config_by_login()
        for login, config in configs.items():
            try:
                interface_ip = self.bot_config_controller.resolve_bot_network_interface(
                    config, available_ips
                )
            except UnavailableNetworkInterface:
                continue
            if interface_ip is None or not self._pool.has_quota(interface_ip, now):
                continue
            info = self.subscribe_service.storage.get_subscribe_info(login)
            if info is None:
                continue
            if not info.is_active_beyond_threshold():
                return _SubscribeOp(login, SubscribeOptions(interface_ip=interface_ip))
        return None

    def _run_operation(self, operation: PendingOperation) -> None:
        match operation:
            case _AuthOp(interface_ip=interface_ip):
                result = _run_async(authenticate_next_available_account(interface_ip))
                if result is not None and result.success:
                    self.on_accounts_synchronized()
            case _RegisterOp():
                _run_async(register_next_available_email())
            case _SubscribeOp(login=login, options=options):
                sub_result = self.subscribe_service.run(login, options)
                logger.info(f"[{login}] {sub_result}")
                if sub_result.status == SubscribeStatus.SUBSCRIBED:
                    self.on_subscribed(login)
        with self._lock:
            self._operation_in_progress = False

    def stop(self) -> None:
        assert self._job is not None, "Scheduler is not started"
        schedule.cancel_job(self._job)
        self._job = None
