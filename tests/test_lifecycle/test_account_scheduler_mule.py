from typing import cast
from unittest.mock import Mock, patch

import pytest
from ankama_launcher_emulator_premium.interfaces.local_storage import (
    BotRecord,
    GeneratedAccountEntry,
    GeneratedAccountsFile,
)
from ankama_launcher_emulator_premium.interfaces.schedule_profile import (
    ScheduleProfile,
)
from ankama_launcher_emulator_premium.utils.proxy import ProxyConfig
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


def _scheduler(
    profiles: dict[str, ScheduleProfile],
    records: dict[str, BotRecord] | None = None,
) -> AccountScheduler:
    config_controller = Mock()
    config_controller.get_bot_config_by_login.return_value = {}
    profile_controller = Mock()
    profile_controller.get_all_profiles.return_value = profiles
    profile_controller.get_profile.side_effect = profiles.get
    proxy_controller = Mock()
    proxy_controller.get_proxy.return_value = _proxy()
    bot_storage_controller = Mock()
    bot_storage_controller.get_all_records.return_value = records or {}
    scheduler = AccountScheduler(
        on_accounts_synchronized=Mock(),
        on_banned_callback=Mock(),
        bot_config_controller=config_controller,
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
        f"bot-{index}@example.com": BotRecord(
            email=f"bot-{index}@example.com",
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

    with (
        patch(
            "src.core.bot.lifecycle.account_scheduler.load_available_generated_accounts",
            return_value=[],
        ),
        patch(
            "src.core.bot.lifecycle.account_scheduler.load_bad_state_emails",
            return_value=set(),
        ),
        patch(
            "src.core.bot.lifecycle.account_scheduler.load_generated_accounts",
            return_value=GeneratedAccountsFile(root=[]),
        ),
        patch(
            "src.core.bot.lifecycle.account_scheduler.count_available_emails",
            return_value=1,
        ),
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
    records["pending-mule@example.com"] = BotRecord(
        email="pending-mule@example.com",
        password="password",
        available=True,
        schedule_profile="M",
    )
    scheduler = _scheduler(profiles, records)

    with (
        patch(
            "src.core.bot.lifecycle.account_scheduler.load_available_generated_accounts",
            return_value=[],
        ),
        patch(
            "src.core.bot.lifecycle.account_scheduler.load_bad_state_emails",
            return_value=set(),
        ),
        patch(
            "src.core.bot.lifecycle.account_scheduler.load_generated_accounts",
            return_value=GeneratedAccountsFile(root=[]),
        ),
        patch(
            "src.core.bot.lifecycle.account_scheduler.count_available_emails",
            return_value=1,
        ),
    ):
        operation = scheduler._next_operation(0)

    assert isinstance(operation, _RegisterOp)
    assert operation.schedule_profile == "B"


def test_registration_replaces_bad_state_mule() -> None:
    profiles = {
        "B": _profile("bot", "B"),
        "M": _profile("kamas_mule", "M"),
    }
    records = _authenticated_records(13)
    records["bad-mule@example.com"] = BotRecord(
        email="bad-mule@example.com",
        password="password",
        available=True,
        bad_state=True,
        schedule_profile="M",
    )
    scheduler = _scheduler(profiles, records)
    bad_mule = GeneratedAccountEntry(
        email="bad-mule@example.com",
        password="password",
        available=True,
        schedule_profile="M",
    )

    with (
        patch(
            "src.core.bot.lifecycle.account_scheduler.load_available_generated_accounts",
            return_value=[bad_mule],
        ),
        patch(
            "src.core.bot.lifecycle.account_scheduler.load_bad_state_emails",
            return_value={bad_mule.email},
        ),
        patch(
            "src.core.bot.lifecycle.account_scheduler.load_generated_accounts",
            return_value=GeneratedAccountsFile(root=[bad_mule]),
        ),
        patch(
            "src.core.bot.lifecycle.account_scheduler.count_available_emails",
            return_value=1,
        ),
    ):
        operation = scheduler._next_operation(0)

    assert isinstance(operation, _RegisterOp)
    assert operation.schedule_profile == "M"


def test_mule_account_can_be_selected_for_authentication() -> None:
    profiles = {"M": _profile("kamas_mule", "M")}
    scheduler = _scheduler(profiles)
    account = GeneratedAccountEntry(
        email="mule@example.com",
        password="password",
        available=True,
        schedule_profile="M",
    )

    with (
        patch(
            "src.core.bot.lifecycle.account_scheduler.load_available_generated_accounts",
            return_value=[account],
        ),
        patch(
            "src.core.bot.lifecycle.account_scheduler.load_bad_state_emails",
            return_value=set(),
        ),
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

    with (
        patch(
            "src.core.bot.lifecycle.account_scheduler.load_available_generated_accounts",
            return_value=[],
        ),
        patch(
            "src.core.bot.lifecycle.account_scheduler.load_bad_state_emails",
            return_value=set(),
        ),
        patch(
            "src.core.bot.lifecycle.account_scheduler.load_generated_accounts",
            return_value=GeneratedAccountsFile(root=[]),
        ),
        patch(
            "src.core.bot.lifecycle.account_scheduler.count_available_emails",
            return_value=1,
        ),
    ):
        operation = scheduler._next_operation(0)

    assert isinstance(operation, _RegisterOp)
    assert operation.schedule_profile == "B"
