import asyncio
import logging
import threading
import time
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from typing import Any

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.consts import SONJI_API_KEY
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.bot_storage import (
    BotStorageController,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.mail_account import (
    MailAccountController,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.proxy import ProxyController
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.controller.schedule_profile import (
    ScheduleProfileController,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.decrypter.crypto_helper import (
    CryptoHelper,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.exceptions import (
    BannedException,
    ProxyRejectedError,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.schedule_profile import (
    ScheduleProfile,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web.auth.launcher_login import (
    authenticate_next_available_account,
)
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.web.auth.registration import (
    is_aws_waf_marker,
    register_next_available_email,
)
from src.core.bot.lifecycle.operation_pool import OperationPool

logger = logging.getLogger()

POLL_INTERVAL_SECONDS = 5
MAX_BOTS_PER_SCHEDULE_PROFILE = 5
MIN_AUTHENTICATED_BOTS_FOR_MULE = 13


@dataclass(frozen=True)
class _AuthOp:
    login: str
    schedule_profile: str
    quota_key: str


@dataclass(frozen=True)
class _RegisterOp:
    schedule_profile: str
    quota_key: str


PendingOperation = _AuthOp | _RegisterOp


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
    drawing from the same pool. The scheduler runs operations back-to-back, starting
    the next one as soon as the previous one finishes and quota allows.
    """

    on_accounts_synchronized: Callable[[], None]
    on_banned_callback: Callable[[str], None]
    schedule_profile_controller: ScheduleProfileController = field(default_factory=ScheduleProfileController)
    proxy_controller: ProxyController = field(default_factory=ProxyController)
    bot_storage_controller: BotStorageController = field(default_factory=BotStorageController)
    _thread: threading.Thread | None = field(init=False, default=None)
    _pool: OperationPool = field(init=False, default_factory=OperationPool)
    _stop_event: threading.Event = field(init=False, default_factory=threading.Event)

    def start(self) -> None:
        assert self._thread is None, "Scheduler is already started"
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        logger.info("Account scheduler armed: next operation runs as soon as the previous one finishes")

    def _loop(self) -> None:
        while not self._stop_event.is_set():
            now = time.time()
            operation = self._next_operation(now)
            if operation is None:
                self._stop_event.wait(POLL_INTERVAL_SECONDS)
                continue
            self._pool.record(operation.quota_key, now)
            try:
                self._run_operation(operation)
            except Exception:
                logger.exception("Unexpected error running scheduled operation %r", operation)

    def _next_operation(self, now: float) -> PendingOperation | None:
        profiles_by_letter = self.schedule_profile_controller.get_all_profiles()
        available_accounts = self.bot_storage_controller.get_accounts_needing_auth()
        bad_state_emails = MailAccountController().load_bad_state_emails()
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
            account_profile = profiles_by_letter.get(account_profile_id)
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
        if MailAccountController().peek_next_available_email() is not None or SONJI_API_KEY is not None:
            profile_counts = self._profile_account_counts(profiles_by_letter)
            records = self.bot_storage_controller.get_all_records().values()
            authenticated_count = sum(record.encrypted_api_key is not None for record in records)
            has_viable_kamas_mule = any(
                record.email not in bad_state_emails and profile.kind == "kamas_mule"
                for record in records
                if record.schedule_profile is not None
                if (profile := profiles_by_letter.get(record.schedule_profile)) is not None
            )
            eligible_candidates = [
                _RegisterOp(profile_id, profile.proxy_id)
                for profile_id, profile in profiles_by_letter.items()
                if not self.proxy_controller.get_proxy(profile.proxy_id).rejected
                if self._pool.has_quota_for(profile.proxy_id, 2, now)
                if not self._pool.is_register_cooled_down(profile.proxy_id, now)
            ]
            mule_candidates = [
                operation
                for operation in eligible_candidates
                if profiles_by_letter[operation.schedule_profile].kind == "kamas_mule"
            ]
            register_candidates = (
                mule_candidates
                if authenticated_count >= MIN_AUTHENTICATED_BOTS_FOR_MULE
                and not has_viable_kamas_mule
                and mule_candidates
                else [
                    operation
                    for operation in eligible_candidates
                    if profiles_by_letter[operation.schedule_profile].kind == "bot"
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

    def _profile_account_counts(
        self,
        profiles: dict[str, ScheduleProfile],
    ) -> dict[str, int]:
        counts = {profile_id: 0 for profile_id in profiles}
        counted_logins: set[str] = set()
        for account in self.bot_storage_controller.get_generated_account_records():
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
        generated_account_logins = {
            account.email
            for account in self.bot_storage_controller.get_generated_account_records()
            if account.schedule_profile == profile_id
        }
        logger.error(
            "Proxy rejected for profile %s; recycling %d accounts",
            profile_id,
            len(generated_account_logins),
        )

        try:
            for login in sorted(generated_account_logins):
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
                self.bot_storage_controller.reassign_schedule_profile(login, target_profile_id)
                profile_counts[target_profile_id] += 1
                logger.info(
                    "Reassigned %s from rejected profiles to profile %s",
                    login,
                    target_profile_id,
                )
        finally:
            self.on_accounts_synchronized()

    def _run_operation(self, operation: PendingOperation) -> None:
        match operation:
            case _AuthOp(login=login, schedule_profile=schedule_profile):
                self._authenticate(login, schedule_profile)
            case _RegisterOp(schedule_profile=schedule_profile, quota_key=quota_key):
                result = _run_async(register_next_available_email(schedule_profile))
                if result is not None and is_aws_waf_marker(result.antibot_marker):
                    self._pool.record_register_cooldown(quota_key)
                if result is not None and result.success:
                    self._pool.record(quota_key, time.time())
                    self._authenticate(result.email, schedule_profile)

    def _authenticate(self, login: str, schedule_profile: str) -> None:
        try:
            result = _run_async(
                authenticate_next_available_account(email=login, schedule_profile=schedule_profile)
            )
        except BannedException:
            return self.on_banned_callback(login)
        except ProxyRejectedError:
            self._handle_proxy_rejection(schedule_profile)
            return
        if result is not None and result.success:
            self.on_accounts_synchronized()

    def stop(self) -> None:
        assert self._thread is not None, "Scheduler is not started"
        self._stop_event.set()
        self._thread = None
