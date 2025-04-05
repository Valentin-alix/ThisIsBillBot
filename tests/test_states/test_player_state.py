import pytest
from datas.protos.non_obf.connection.login_message_pb2 import (
    SelectServerRequest,
)
from datas.protos.non_obf.game.character_management_pb2 import (
    CharacterSelectionEvent,
)
from datas.protos.non_obf.game.common_pb2 import Character
from datas.protos.non_obf.game.job_pb2 import (
    JobExperience,
    JobExperiencesUpdateEvent,
)
from datas.protos.non_obf.game.teleportation_pb2 import (
    ZaapKnownListEvent,
)

from src.core.bot.bot import Bot


class TestPlayerState:
    def test_character_selection_success_sets_character_state(
        self,
        runtime_bot: Bot,
    ):
        character = Character(
            id=123456,
            character_basic_information=Character.CharacterBasicInformation(
                level=150,
                name="TestHero",
            ),
        )

        runtime_bot.event_manager.process_msg(
            CharacterSelectionEvent(
                success=CharacterSelectionEvent.Success(character=character)
            )
        )

        assert runtime_bot.game_state.player.character_id == 123456
        assert runtime_bot.game_state.player.level == 150
        assert runtime_bot.game_state.player.character_name == "TestHero"

    def test_job_experiences_update_sets_job_levels_round_to_lower(
        self,
        runtime_bot: Bot,
    ):
        experiences = [
            JobExperience(job_id=1, job_level=100),
            JobExperience(job_id=2, job_level=75),
            JobExperience(job_id=3, job_level=50),
        ]

        msg = JobExperiencesUpdateEvent(experiences=experiences)

        runtime_bot.event_manager.process_msg(msg)

        assert runtime_bot.game_state.player.jobs_lvl_by_id[1] == 100
        assert runtime_bot.game_state.player.jobs_lvl_by_id[2] == 70
        assert runtime_bot.game_state.player.jobs_lvl_by_id[3] == 50

    def test_job_level_minimum_is_one(
        self,
        runtime_bot: Bot,
    ):
        experiences = [
            JobExperience(job_id=1, job_level=5),
        ]

        msg = JobExperiencesUpdateEvent(experiences=experiences)

        runtime_bot.event_manager.process_msg(msg)

        assert runtime_bot.game_state.player.jobs_lvl_by_id[1] == 1

    def test_zaap_known_list_sets_waypoints(
        self,
        runtime_bot: Bot,
    ):
        msg = ZaapKnownListEvent(destinations=[10000, 20000, 30000, 40000])

        runtime_bot.event_manager.process_msg(msg)

        assert runtime_bot.game_state.player.waypoint_map_ids == [
            10000,
            20000,
            30000,
            40000,
        ]

    def test_select_server_request_sets_server_id(
        self,
        runtime_bot: Bot,
    ):
        msg = SelectServerRequest(server=42)

        runtime_bot.event_manager.process_msg(msg)

        assert runtime_bot.game_state.player.server_id == 42

    @pytest.mark.parametrize(
        ("level", "expected"),
        [
            (150, 150),
            (200, 200),
            (250, 200),
        ],
    )
    def test_limited_lvl(
        self,
        runtime_bot: Bot,
        level: int,
        expected: int,
    ):
        runtime_bot.game_state.player.level = level

        assert runtime_bot.game_state.player.limited_lvl == expected

    def test_zaap_list_update_replaces_previous(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.event_manager.process_msg(
            ZaapKnownListEvent(destinations=[10000, 20000])
        )

        runtime_bot.event_manager.process_msg(
            ZaapKnownListEvent(destinations=[30000, 40000, 50000])
        )

        assert runtime_bot.game_state.player.waypoint_map_ids == [
            30000,
            40000,
            50000,
        ]
