from typing import cast
from unittest.mock import MagicMock, Mock, patch

import pytest
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.local_storage import BotRecord
from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.schedule_profile import (
    ProxyConfig,
    ScheduleProfile,
)

from src.core.bot.lifecycle.account_scheduler import (
    AccountScheduler,
    _AuthOp,
    _RegisterOp,
)


def _profile(kind: str, proxy_id: str) -> ScheduleProfile:
    return ScheduleProfile.model_validate(
        {
            "name_fr": proxy_id,
            "proxy_id": proxy_id,
            "slots_by_day": {},
            "kind": kind,
        }
    )


def _proxy(*, rejected: bool = False) -> ProxyConfig:
    return ProxyConfig(
        rejected=rejected,
        host="localhost",
        http_port=8080,
        socks_port=1080,
        username="user",
        password="password",
    )


def _mock(value: object) -> Mock:
    return cast(Mock, value)


def _mail_account_controller(
    *,
    available_email: str | None = "next@example.com",
    bad_state_emails: set[str] | None = None,
) -> MagicMock:
    controller = MagicMock()
    controller.peek_next_available_email.return_value = available_email
    controller.load_bad_state_emails.return_value = bad_state_emails or set()
    return controller


def _bot_record(email: str, *, schedule_profile: str | None, encrypted_api_key: str | None = None) -> BotRecord:
    return BotRecord(
        email=email,
        password="password",
        hardware_id=f"hw-{email}",
        schedule_profile=schedule_profile,
        encrypted_api_key=encrypted_api_key,
    )


def _scheduler(
    profiles: dict[str, ScheduleProfile],
    records: dict[str, BotRecord] | None = None,
    *,
    accounts_needing_auth: list[BotRecord] | None = None,
    generated_account_records: list[BotRecord] | None = None,
) -> AccountScheduler:
    profile_controller = Mock()
    profile_controller.get_all_profiles.return_value = profiles
    profile_controller.get_profile.side_effect = profiles.get
    proxy_controller = Mock()
    proxy_controller.get_proxy.return_value = _proxy()
    bot_storage_controller = Mock()
    bot_storage_controller.get_all_records.return_value = records or {}
    bot_storage_controller.get_accounts_needing_auth.return_value = accounts_needing_auth or []
    bot_storage_controller.get_generated_account_records.return_value = generated_account_records or []
    scheduler = AccountScheduler(
        on_accounts_synchronized=Mock(),
        on_banned_callback=Mock(),
        schedule_profile_controller=profile_controller,
        proxy_controller=proxy_controller,
        bot_storage_controller=bot_storage_controller,
    )
    scheduler._pool = Mock()
    scheduler._pool.has_quota.return_value = True
    scheduler._pool.is_register_cooled_down.return_value = False
    scheduler._pool.count_since_hour.return_value = 0
    return scheduler


def _authenticated_records(count: int) -> dict[str, BotRecord]:
    return {
        f"bot-{index}@example.com": _bot_record(
            f"bot-{index}@example.com",
            schedule_profile="B",
            encrypted_api_key="encrypted",
        )
        for index in range(count)
    }


@pytest.mark.parametrize(
    ("authenticated_count", "expected_profile"),
    [(12, "B"), (13, "M")],
)
def test_registration_selects_mule_only_after_threshold(
    authenticated_count: int,
    expected_profile: str,
) -> None:
    profiles = {
        "B": _profile("bot", "B"),
        "M": _profile("kamas_mule", "M"),
    }
    scheduler = _scheduler(profiles, _authenticated_records(authenticated_count))

    with patch(
        "src.core.bot.lifecycle.account_scheduler.MailAccountController",
        return_value=_mail_account_controller(),
    ):
        operation = scheduler._next_operation(0)

    assert isinstance(operation, _RegisterOp)
    assert operation.schedule_profile == expected_profile


def test_registration_does_not_create_second_pending_mule() -> None:
    profiles = {
        "B": _profile("bot", "B"),
        "M": _profile("kamas_mule", "M"),
    }
    records = _authenticated_records(13)
    records["pending-mule@example.com"] = _bot_record("pending-mule@example.com", schedule_profile="M")
    scheduler = _scheduler(profiles, records)

    with patch(
        "src.core.bot.lifecycle.account_scheduler.MailAccountController",
        return_value=_mail_account_controller(),
    ):
        operation = scheduler._next_operation(0)

    assert isinstance(operation, _RegisterOp)
    assert operation.schedule_profile == "B"


def test_registration_stops_when_all_bot_profiles_are_full() -> None:
    profiles = {"B": _profile("bot", "B")}
    records = _authenticated_records(6)
    scheduler = _scheduler(
        profiles,
        records,
        generated_account_records=list(records.values()),
    )

    with patch(
        "src.core.bot.lifecycle.account_scheduler.MailAccountController",
        return_value=_mail_account_controller(),
    ):
        operation = scheduler._next_operation(0)

    assert operation is None


def test_pending_account_is_authenticated_when_its_full_profile_has_capacity_zero() -> None:
    profiles = {"B": _profile("bot", "B")}
    records = _authenticated_records(4)
    pending_account = _bot_record("pending@example.com", schedule_profile="B")
    records[pending_account.email] = pending_account
    scheduler = _scheduler(
        profiles,
        records,
        accounts_needing_auth=[pending_account],
        generated_account_records=list(records.values()),
    )

    with patch(
        "src.core.bot.lifecycle.account_scheduler.MailAccountController",
        return_value=_mail_account_controller(),
    ):
        operation = scheduler._next_operation(0)

    assert operation == _AuthOp("pending@example.com", "B", "B")


def test_registration_replaces_bad_state_mule() -> None:
    profiles = {
        "B": _profile("bot", "B"),
        "M": _profile("kamas_mule", "M"),
    }
    records = _authenticated_records(13)
    bad_mule = _bot_record("bad-mule@example.com", schedule_profile="M")
    records["bad-mule@example.com"] = bad_mule
    scheduler = _scheduler(
        profiles,
        records,
        accounts_needing_auth=[bad_mule],
        generated_account_records=[bad_mule],
    )

    with patch(
        "src.core.bot.lifecycle.account_scheduler.MailAccountController",
        return_value=_mail_account_controller(bad_state_emails={bad_mule.email}),
    ):
        operation = scheduler._next_operation(0)

    assert isinstance(operation, _RegisterOp)
    assert operation.schedule_profile == "M"


def test_mule_account_can_be_selected_for_authentication() -> None:
    profiles = {"M": _profile("kamas_mule", "M")}
    account = _bot_record("mule@example.com", schedule_profile="M")
    scheduler = _scheduler(profiles, accounts_needing_auth=[account])

    with patch(
        "src.core.bot.lifecycle.account_scheduler.MailAccountController",
        return_value=_mail_account_controller(),
    ):
        operation = scheduler._next_operation(0)

    assert operation == _AuthOp("mule@example.com", "M", "M")


def test_registration_falls_back_when_mule_proxy_is_rejected() -> None:
    profiles = {
        "B": _profile("bot", "B"),
        "M": _profile("kamas_mule", "M"),
    }
    scheduler = _scheduler(profiles, _authenticated_records(13))

    def proxy_by_id(proxy_id: str) -> ProxyConfig:
        return _proxy(rejected=proxy_id == "M")

    _mock(scheduler.proxy_controller.get_proxy).side_effect = proxy_by_id

    with patch(
        "src.core.bot.lifecycle.account_scheduler.MailAccountController",
        return_value=_mail_account_controller(),
    ):
        operation = scheduler._next_operation(0)

    assert isinstance(operation, _RegisterOp)
    assert operation.schedule_profile == "B"
