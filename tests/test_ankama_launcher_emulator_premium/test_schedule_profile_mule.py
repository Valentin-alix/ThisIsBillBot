from AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.interfaces.schedule_profile import (
    ScheduleProfile,
)


def _profile(
    start: str,
    end: str,
    *,
    kind: str = "bot",
) -> ScheduleProfile:
    return ScheduleProfile.model_validate(
        {
            "name_fr": "Test",
            "proxy_id": "test",
            "kind": kind,
            "slots_by_day": {str(day): [{"start": start, "end": end}] for day in range(7)},
        }
    )


def test_existing_profile_defaults_to_bot_kind() -> None:
    profile = ScheduleProfile(
        name_fr="Normal",
        proxy_id="normal",
        slots_by_day={},
    )

    assert profile.kind == "bot"


def test_mule_profile_kind_is_accepted() -> None:
    profile = _profile("11:00", "11:30", kind="kamas_mule")

    assert profile.kind == "kamas_mule"
