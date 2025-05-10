import pytest
from consts import PC_ID

from src.controller.bot_config import BotConfig, BotConfigController
from src.controller.schedule_profile_controller import (
    ScheduleProfile,
    ScheduleProfileController,
)


def _profiles(*profile_ids: str) -> dict[str, ScheduleProfile]:
    return {
        profile_id: ScheduleProfile(name_fr=profile_id, slots_by_day={})
        for profile_id in profile_ids
    }


class TestAssignLeastUsedProfile:
    def test_picks_least_represented_profile_and_persists_it(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        controller = BotConfigController()

        def fake_get_all_profiles(
            _controller: ScheduleProfileController,
        ) -> dict[str, ScheduleProfile]:
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

    def test_resolves_profile_network_interface_when_profiles_define_index(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        controller = BotConfigController()

        profile = ScheduleProfile(
            name_fr="B", network_interface_index=2, slots_by_day={}
        )

        def fake_get_profile(
            _controller: ScheduleProfileController, profile_id: str
        ) -> ScheduleProfile | None:
            if profile_id == "B":
                return profile
            return None

        monkeypatch.setattr(
            ScheduleProfileController,
            "get_profile",
            fake_get_profile,
        )

        interface_ip = controller.resolve_bot_network_interface(
            BotConfig(schedule_profile="B"), ["192.168.1.156", "192.168.0.117"]
        )

        assert interface_ip == "192.168.0.117"

    def test_ignores_configs_from_other_pc_ids(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        controller = BotConfigController()

        def fake_get_all_profiles(
            _controller: ScheduleProfileController,
        ) -> dict[str, ScheduleProfile]:
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

    def test_raises_when_no_profiles_configured(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        controller = BotConfigController()

        def fake_get_all_profiles(
            _controller: ScheduleProfileController,
        ) -> dict[str, ScheduleProfile]:
            return {}

        monkeypatch.setattr(
            ScheduleProfileController, "get_all_profiles", fake_get_all_profiles
        )

        def fail_write(_configs: dict[str, BotConfig]) -> None:
            raise AssertionError("must not write when no profile is available")

        monkeypatch.setattr(controller, "_write_all_configs", fail_write)

        with pytest.raises(ValueError, match="Did not found any profile"):
            controller.assign_least_used_profile("new@x.fr")

    def test_raises_when_profile_interface_index_is_not_available(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        controller = BotConfigController()

        def fake_get_all_profiles(
            _controller: ScheduleProfileController,
        ) -> dict[str, ScheduleProfile]:
            return {
                "A": ScheduleProfile(
                    name_fr="A", network_interface_index=3, slots_by_day={}
                )
            }

        monkeypatch.setattr(
            ScheduleProfileController, "get_all_profiles", fake_get_all_profiles
        )

        def fake_get_profile(
            _controller: ScheduleProfileController, profile_id: str
        ) -> ScheduleProfile:
            return fake_get_all_profiles(_controller)[profile_id]

        monkeypatch.setattr(
            ScheduleProfileController,
            "get_profile",
            fake_get_profile,
        )

        def fake_get() -> dict[str, BotConfig]:
            return {}

        monkeypatch.setattr(controller, "_get_all_configs", fake_get)

        def fail_write(_configs: dict[str, BotConfig]) -> None:
            raise AssertionError("must not write when profile interface is unavailable")

        monkeypatch.setattr(controller, "_write_all_configs", fail_write)

        with pytest.raises(ValueError, match="requires network interface index 3"):
            controller.resolve_profile_network_interface("A", ["192.168.1.156"])
