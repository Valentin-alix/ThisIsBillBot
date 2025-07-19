import asyncio
import logging
import threading
import time
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from typing import Any

import schedule
from ankama_launcher_emulator_premium.decrypter.crypto_helper import CryptoHelper
from ankama_launcher_emulator_premium.exceptions import (
    BannedException,
    ProxyRejectedError,
)
from ankama_launcher_emulator_premium.interfaces.schedule_profile import (
    ProxyController,
    ScheduleProfile,
    ScheduleProfileController,
)
from ankama_launcher_emulator_premium.utils.bot_storage import BotStorageController
from ankama_launcher_emulator_premium.web.auth.launcher_login import (
    authenticate_next_available_account,
)
from ankama_launcher_emulator_premium.web.auth.registration import (
    count_available_emails,
    is_aws_waf_marker,
    register_next_available_email,
)
from ankama_launcher_emulator_premium.web.auth.storage import (
    load_available_generated_accounts,
    load_bad_state_emails,
    load_generated_accounts,
    mark_account_available_for_auth_retry,
    reassign_account_for_auth_retry,
)
from ankama_launcher_emulator_premium.web.subscription.models import (
    SubscribeOptions,
    SubscribeStatus,
)
from ankama_launcher_emulator_premium.web.subscription.service import (
    SubscribeService,
    build_subscribe_service,
)

from src.controller.bot_config import BotConfigService
from src.core.bot.lifecycle.operation_pool import OperationPool

logger = logging.getLogger()

TICK_INTERVAL_MINUTES = 5
OGRINE_SUBSCRIPTION_MIN_KAMAS = 3_000_000
MAX_BOTS_PER_SCHEDULE_PROFILE = 5


@dataclass(frozen=True)
class _AuthOp:
    """Authenticate the next available generated account for ``schedule_profile``."""

    login: str
    schedule_profile: str
    quota_key: str


@dataclass(frozen=True)
class _RegisterOp:
    """Create the next account from the available-emails queue."""

    schedule_profile: str
    quota_key: str


@dataclass(frozen=True)
class _SubscribeOp:
    """Subscribe or renew a single account."""

    login: str
    options: SubscribeOptions
    quota_key: str


PendingOperation = _AuthOp | _RegisterOp | _SubscribeOp


def _quota_key_of(operation: PendingOperation) -> str:
    """The source proxy, or direct connection, an operation is charged against."""
    match operation:
        case _SubscribeOp(quota_key=quota_key):
            return quota_key
        case _AuthOp(quota_key=quota_key) | _RegisterOp(quota_key=quota_key):
            return quota_key


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
    is available, performs a single operation — preferring an ogrine renewal for a
    sufficiently funded former subscriber, then a first Paysafecard subscription,
    then authentication, and finally creating a new account.
    """

    on_accounts_synchronized: Callable[[], None]
    on_subscribed: Callable[[str], None]
    on_banned_callback: Callable[[str], None]
    bot_config_controller: BotConfigService = field(default_factory=BotConfigService)
    schedule_profile_controller: ScheduleProfileController = field(
        default_factory=ScheduleProfileController
    )
    proxy_controller: ProxyController = field(default_factory=ProxyController)
    subscribe_service: SubscribeService = field(default_factory=build_subscribe_service)
    account_kamas_controller: BotStorageController = field(
        default_factory=BotStorageController
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
            operation = self._next_operation(now)
            if operation is None:
                return
            quota_key = _quota_key_of(operation)
            self._pool.record(quota_key, now)
            self._operation_in_progress = True

        threading.Thread(target=self._run_operation, args=(operation,)).start()

    def _next_operation(self, now: float) -> PendingOperation | None:
        subscription = self._next_subscription_target(now)
        if subscription is not None:
            logger.info(f"let's subscribe for {subscription.login}")
            return subscription
        profiles = self.schedule_profile_controller.get_all_profiles()
        available_accounts = load_available_generated_accounts()
        bad_state_emails = load_bad_state_emails()
        auth_candidates: list[_AuthOp] = []
        for account in available_accounts:
            if account.email in bad_state_emails:
                logger.info(f"email {account.email} in bad state, skipping")
                continue
            account_profile_id = account.schedule_profile
            if account_profile_id is None:
                logger.info(f"account {account.email} has no profile id ?!")
                continue
            account_profile = profiles.get(account_profile_id)
            if account_profile is None:
                raise ValueError(f"Unknown schedule profile {account_profile_id}")
            account_proxy = self.proxy_controller.get_proxy(account_profile.proxy_id)
            if account_proxy.rejected:
                logger.info(
                    "account %s uses rejected profile %s, skipping",
                    account.email,
                    account_profile_id,
                )
                continue
            quota_key = account_profile.proxy_id
            if not self._pool.has_quota(quota_key, now):
                logger.info(f"quota key {quota_key} reached")
                continue
            auth_candidates.append(
                _AuthOp(account.email, account_profile_id, quota_key)
            )
        if auth_candidates:
            return min(
                auth_candidates,
                key=lambda operation: self._pool.count_since_hour(
                    operation.quota_key, now
                ),
            )
        if count_available_emails() > 0:
            profile_counts = self._profile_account_counts(profiles)
            register_candidates = [
                _RegisterOp(profile_id, profile.proxy_id)
                for profile_id, profile in profiles.items()
                if not self.proxy_controller.get_proxy(profile.proxy_id).rejected
                if self._pool.has_quota(profile.proxy_id, now)
                if profile_counts[profile_id] < MAX_BOTS_PER_SCHEDULE_PROFILE
                if not self._pool.is_register_cooled_down(profile.proxy_id, now)
            ]
            if not register_candidates:
                return None
            register_candidates.sort(
                key=lambda operation: self._pool.count_since_hour(
                    operation.quota_key, now
                )
            )
            return min(
                register_candidates,
                key=lambda operation: profile_counts[operation.schedule_profile],
            )
        return None

    @staticmethod
    def _profile_account_counts(
        profiles: dict[str, ScheduleProfile],
    ) -> dict[str, int]:
        counts = {profile_id: 0 for profile_id in profiles}
        counted_logins: set[str] = set()
        for account in load_generated_accounts().root:
            profile_id = account.schedule_profile
            if profile_id is None or account.email in counted_logins:
                continue
            if profile_id not in profiles:
                raise ValueError(
                    f"Unknown schedule profile {profile_id} "
                    f"for generated account {account.email}"
                )
            counts[profile_id] += 1
            counted_logins.add(account.email)
        return counts

    def _next_subscription_target(self, now: float) -> _SubscribeOp | None:
        configs = self.bot_config_controller.get_bot_config_by_login()
        has_paysafecard_pin = bool(self.subscribe_service.paysafecard_pool.load())
        first_subscription: _SubscribeOp | None = None
        for login, config in configs.items():
            if config.schedule_profile is None:
                continue
            proxy = self.bot_config_controller.resolve_bot_proxy(config)
            if proxy.rejected:
                continue
            proxy_url = self.bot_config_controller.resolve_bot_http_proxy_url(config)
            profile = self.schedule_profile_controller.get_profile(
                config.schedule_profile
            )
            assert profile is not None, (
                f"Unknown schedule profile {config.schedule_profile}"
            )
            quota_key = profile.proxy_id
            if not self._pool.has_quota(quota_key, now):
                continue
            info = self.subscribe_service.storage.get_subscribe_info(login)
            if info is None:
                continue
            if info.is_active_beyond_threshold():
                continue
            operation = _SubscribeOp(
                login, SubscribeOptions(proxy_url=proxy_url), quota_key
            )
            if info.is_subscribe or info.is_former_subscribe:
                kamas = self.account_kamas_controller.get_kamas(login)
                if kamas is not None and kamas > OGRINE_SUBSCRIPTION_MIN_KAMAS:
                    return operation
                continue
            if has_paysafecard_pin and first_subscription is None:
                first_subscription = operation
        return first_subscription

    def _handle_proxy_rejection(self, profile_id: str) -> None:
        rejected_profile = self.schedule_profile_controller.get_profile(profile_id)
        if rejected_profile is None:
            raise ValueError(f"Unknown schedule profile {profile_id}")
        self.proxy_controller.record_rejection(rejected_profile.proxy_id)
        bot_configs = self.bot_config_controller.get_bot_config_by_login()
        generated_account_logins = {
            account.email
            for account in load_generated_accounts().root
            if account.schedule_profile == profile_id
        }
        affected_logins = set(generated_account_logins)
        affected_logins.update(
            login
            for login, config in bot_configs.items()
            if config.schedule_profile == profile_id
        )
        logger.error(
            "Proxy rejected for profile %s; recycling %d accounts",
            profile_id,
            len(affected_logins),
        )

        try:
            for login in sorted(affected_logins):
                CryptoHelper.remove_bot(login)

            profiles = self.schedule_profile_controller.get_all_profiles()
            profile_counts = self._profile_account_counts(profiles)
            healthy_profile_ids = sorted(
                candidate_profile_id
                for candidate_profile_id, candidate_profile in profiles.items()
                if not self.proxy_controller.get_proxy(
                    candidate_profile.proxy_id
                ).rejected
            )
            for login in sorted(generated_account_logins):
                available_profile_ids = [
                    candidate_profile_id
                    for candidate_profile_id in healthy_profile_ids
                    if profile_counts[candidate_profile_id]
                    < MAX_BOTS_PER_SCHEDULE_PROFILE
                ]
                if not available_profile_ids:
                    mark_account_available_for_auth_retry(login)
                    logger.warning(
                        "No healthy schedule profile has room for %s; "
                        "keeping its rejected profile",
                        login,
                    )
                    continue
                target_profile_id = min(
                    available_profile_ids,
                    key=lambda candidate_profile_id: (
                        profile_counts[candidate_profile_id],
                        candidate_profile_id,
                    ),
                )
                reassign_account_for_auth_retry(login, target_profile_id)
                if login in bot_configs:
                    self.bot_config_controller.assign_profile(login, target_profile_id)
                profile_counts[target_profile_id] += 1
                logger.info(
                    "Reassigned %s from rejected profiles to profile %s",
                    login,
                    target_profile_id,
                )
        finally:
            self.on_accounts_synchronized()

    def _run_operation(self, operation: PendingOperation) -> None:
        try:
            match operation:
                case _AuthOp(login=login, schedule_profile=schedule_profile):
                    try:
                        result = _run_async(
                            authenticate_next_available_account(
                                email=login, schedule_profile=schedule_profile
                            )
                        )
                    except BannedException:
                        return self.on_banned_callback(login)
                    except ProxyRejectedError:
                        self._handle_proxy_rejection(schedule_profile)
                        return
                    if result is not None and result.success:
                        self.bot_config_controller.assign_profile(
                            login, schedule_profile
                        )
                        self.on_accounts_synchronized()
                case _RegisterOp(schedule_profile=schedule_profile):
                    result = _run_async(register_next_available_email(schedule_profile))
                    if result is not None and is_aws_waf_marker(result.antibot_marker):
                        self._pool.record_register_cooldown(operation.quota_key)
                case _SubscribeOp(login=login, options=options):
                    try:
                        sub_result = self.subscribe_service.run(login, options)
                    except BannedException:
                        return self.on_banned_callback(login)
                    logger.info(f"[{login}] {sub_result}")
                    if sub_result.status == SubscribeStatus.SUBSCRIBED:
                        self.on_subscribed(login)
        finally:
            self._operation_in_progress = False

    def stop(self) -> None:
        assert self._job is not None, "Scheduler is not started"
        schedule.cancel_job(self._job)
        self._job = None
