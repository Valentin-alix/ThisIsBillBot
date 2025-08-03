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

from src.controller.bot_config import BotConfigService
from src.core.bot.lifecycle.operation_pool import OperationPool

logger = logging.getLogger()

TICK_INTERVAL_MINUTES = 5
MAX_BOTS_PER_SCHEDULE_PROFILE = 5
MIN_AUTHENTICATED_BOTS_FOR_MULE = 13


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


PendingOperation = _AuthOp | _RegisterOp


def _quota_key_of(operation: PendingOperation) -> str:
    """The source proxy, or direct connection, an operation is charged against."""
    match operation:
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
    """Drives account authentication and creation from a shared rate-limit pool.

    Ankama caps these operations at 2 per rolling hour and 4 per rolling day, all
    drawing from the same pool. The scheduler ticks periodically and, whenever quota
    is available, performs a single authentication or account creation.
    """

    on_accounts_synchronized: Callable[[], None]
    on_banned_callback: Callable[[str], None]
    bot_config_controller: BotConfigService = field(default_factory=BotConfigService)
    schedule_profile_controller: ScheduleProfileController = field(default_factory=ScheduleProfileController)
    proxy_controller: ProxyController = field(default_factory=ProxyController)
    bot_storage_controller: BotStorageController = field(default_factory=BotStorageController)
    _job: schedule.Job | None = field(init=False, default=None)
    _pool: OperationPool = field(init=False, default_factory=OperationPool)
    _lock: threading.Lock = field(init=False, default_factory=threading.Lock)
    _operation_in_progress: bool = field(init=False, default=False)

    def start(self) -> None:
        assert self._job is None, "Scheduler is already started"
        self._job = schedule.every(TICK_INTERVAL_MINUTES).minutes.do(self._tick)
        logger.info(f"Account scheduler armed: one operation every {TICK_INTERVAL_MINUTES} min ")

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
                logger.warning(
                    "account %s is available but has no schedule profile, ignored "
                    "(assign one so it can be authenticated)",
                    account.email,
                )
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
            auth_candidates.append(_AuthOp(account.email, account_profile_id, quota_key))
        if auth_candidates:
            return min(
                auth_candidates,
                key=lambda operation: self._pool.count_since_hour(operation.quota_key, now),
            )
        if count_available_emails() > 0:
            profile_counts = self._profile_account_counts(profiles)
            records = self.bot_storage_controller.get_all_records().values()
            authenticated_count = sum(record.encrypted_api_key is not None for record in records)
            has_viable_kamas_mule = any(
                not record.bad_state and profile.kind == "kamas_mule"
                for record in records
                if record.schedule_profile is not None
                if (profile := profiles.get(record.schedule_profile)) is not None
            )
            eligible_candidates = [
                _RegisterOp(profile_id, profile.proxy_id)
                for profile_id, profile in profiles.items()
                if not self.proxy_controller.get_proxy(profile.proxy_id).rejected
                if self._pool.has_quota(profile.proxy_id, now)
                if not self._pool.is_register_cooled_down(profile.proxy_id, now)
            ]
            mule_candidates = [
                operation
                for operation in eligible_candidates
                if profiles[operation.schedule_profile].kind == "kamas_mule"
            ]
            register_candidates = (
                mule_candidates
                if authenticated_count >= MIN_AUTHENTICATED_BOTS_FOR_MULE
                and not has_viable_kamas_mule
                and mule_candidates
                else [
                    operation
                    for operation in eligible_candidates
                    if profiles[operation.schedule_profile].kind == "bot"
                    if profile_counts[operation.schedule_profile] < MAX_BOTS_PER_SCHEDULE_PROFILE
                ]
            )
            if not register_candidates:
                return None
            register_candidates.sort(
                key=lambda operation: self._pool.count_since_hour(operation.quota_key, now)
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
                    f"Unknown schedule profile {profile_id} for generated account {account.email}"
                )
            counts[profile_id] += 1
            counted_logins.add(account.email)
        return counts

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
            login for login, config in bot_configs.items() if config.schedule_profile == profile_id
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
                if candidate_profile.kind == "bot"
                if not self.proxy_controller.get_proxy(candidate_profile.proxy_id).rejected
            )
            for login in sorted(generated_account_logins):
                available_profile_ids = [
                    candidate_profile_id
                    for candidate_profile_id in healthy_profile_ids
                    if profile_counts[candidate_profile_id] < MAX_BOTS_PER_SCHEDULE_PROFILE
                ]
                if not available_profile_ids:
                    mark_account_available_for_auth_retry(login)
                    logger.warning(
                        "No healthy schedule profile has room for %s; keeping its rejected profile",
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
                        self.bot_config_controller.assign_profile(login, schedule_profile)
                        self.on_accounts_synchronized()
                case _RegisterOp(schedule_profile=schedule_profile):
                    result = _run_async(register_next_available_email(schedule_profile))
                    if result is not None and is_aws_waf_marker(result.antibot_marker):
                        self._pool.record_register_cooldown(operation.quota_key)
        finally:
            self._operation_in_progress = False

    def stop(self) -> None:
        assert self._job is not None, "Scheduler is not started"
        schedule.cancel_job(self._job)
        self._job = None
