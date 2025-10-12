from unittest.mock import patch

from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.schedule_profile import (
    ScheduleProfile,
)

from src.controller.bot_config import BotConfig, BotConfigService


def test_mule_role_is_derived_from_schedule_profile_kind() -> None:
    service = BotConfigService()
    mule_profile = ScheduleProfile(
        name_fr="Mule",
        proxy_id="M",
        slots_by_day={},
        kind="kamas_mule",
    )
    with (
        patch.object(
            service,
            "get_bot_config",
            return_value=BotConfig(schedule_profile="M"),
        ),
        patch(
            "src.controller.bot_config.ScheduleProfileController.get_profile",
            return_value=mule_profile,
        ),
    ):
        assert service.is_kamas_mule("mule@example.com")
