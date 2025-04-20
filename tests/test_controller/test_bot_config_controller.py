import pytest
from consts import PC_ID

from src.controller.bot_config import BotConfig, BotConfigController
from src.controller.schedule_profile_controller import (
    ScheduleProfile,
    ScheduleProfileController,
)


def _profiles(*ids: str) -> dict[str, ScheduleProfile]:
    return {
        profile_id: ScheduleProfile(name_fr=profile_id, slots_by_day={})
        for profile_id in ids
    }


class TestAssignLeastUsedProfile:
    def test_picks_least_represented_profile_and_persists_it(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        controller = BotConfigController()

        def fake_get_all_profiles(_self: ScheduleProfileController):
            return _profiles("A", "B", "C", "E")

        monkeypatch.setattr(
            ScheduleProfileController, "get_all_profiles", fake_get_all_profiles
        )

        # A used twice, B once, C/E never -> C must win (alpha tie-break before E).
        existing_configs: dict[str, BotConfig] = {
            "a@x.fr": BotConfig(pc_id=PC_ID, schedule_profile="A"),
            "b@x.fr": BotConfig(pc_id=PC_ID, schedule_profile="A"),
            "c@x.fr": BotConfig(pc_id=PC_ID, schedule_profile="B"),
        }
        written: dict[str, BotConfig] = {}

        def fake_get() -> dict[str, BotConfig]:
            return dict(existing_configs)

        def fake_write(configs: dict[str, BotConfig]) -> None:
            written.update(configs)

        monkeypatch.setattr(controller, "_get_all_configs", fake_get)
        monkeypatch.setattr(controller, "_write_all_configs", fake_write)

        chosen = controller.assign_least_used_profile("new@x.fr")

        assert chosen == "C"
        assert written["new@x.fr"].schedule_profile == "C"

    def test_ignores_configs_from_other_pc_ids(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        controller = BotConfigController()

        def fake_get_all_profiles(_self: ScheduleProfileController):
            return _profiles("A", "B")

        monkeypatch.setattr(
            ScheduleProfileController, "get_all_profiles", fake_get_all_profiles
        )

        # B is heavily used but only on another PC -> must be ignored, A wins.
        existing_configs: dict[str, BotConfig] = {
            "other1@x.fr": BotConfig(pc_id=PC_ID + 1, schedule_profile="A"),
            "other2@x.fr": BotConfig(pc_id=PC_ID + 1, schedule_profile="A"),
            "mine@x.fr": BotConfig(pc_id=PC_ID, schedule_profile="B"),
        }

        def fake_get() -> dict[str, BotConfig]:
            return dict(existing_configs)

        def fake_write(_configs: dict[str, BotConfig]) -> None:
            return None

        monkeypatch.setattr(controller, "_get_all_configs", fake_get)
        monkeypatch.setattr(controller, "_write_all_configs", fake_write)

        chosen = controller.assign_least_used_profile("new@x.fr")

        assert chosen == "A"

    def test_returns_none_when_no_profiles_configured(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        controller = BotConfigController()

        def fake_get_all_profiles(_self: ScheduleProfileController) -> dict[str, ScheduleProfile]:
            return {}

        monkeypatch.setattr(
            ScheduleProfileController, "get_all_profiles", fake_get_all_profiles
        )

        def fail_write(_configs: dict[str, BotConfig]) -> None:
            raise AssertionError("must not write when no profile is available")

        monkeypatch.setattr(controller, "_write_all_configs", fail_write)

        assert controller.assign_least_used_profile("new@x.fr") is None
