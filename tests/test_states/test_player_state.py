from datetime import datetime, timezone

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
from src.core.bot.bot_factory import BotFactory
from src.core.signals.shared_farm_signals import SharedSignals
from tests.test_states.state_test_base import StateTestBase, TEST_ACCOUNT


class TestPlayerState(StateTestBase):
    def test_initial_state(self):
        assert self.game_state.player.level == 1
        assert self.game_state.player.character_id == 0
        assert self.game_state.player.character_name == ""
        assert len(self.game_state.player.waypoint_map_ids) == 0
        assert len(self.game_state.player.jobs_lvl_by_id) == 0
        assert self.game_state.player.server_id == 1

    def test_collection_fields_are_not_shared_between_instances(self):
        other_bot = BotFactory.create_bot(
            SharedSignals(), account=TEST_ACCOUNT, is_fake=True
        )

        assert (
            self.game_state.player.waypoint_map_ids
            is not other_bot.game_state.player.waypoint_map_ids
        )
        assert (
            self.game_state.player.jobs_lvl_by_id
            is not other_bot.game_state.player.jobs_lvl_by_id
        )

    def test_clear_state_resets_values(self):
        self.game_state.player.level = 200
        self.game_state.player.character_id = 123456
        self.game_state.player.character_name = "TestPlayer"
        self.game_state.player.waypoint_map_ids = [1, 2, 3]
        self.game_state.player.jobs_lvl_by_id = {1: 100}
        self.game_state.player.server_id = 5
        self.game_state.player.is_ready_to_play_event.set()

        self.game_state.player.clear_state()

        assert self.game_state.player.level == 1
        assert self.game_state.player.character_id == 0
        assert self.game_state.player.character_name == ""
        assert len(self.game_state.player.waypoint_map_ids) == 0
        assert len(self.game_state.player.jobs_lvl_by_id) == 0
        assert self.game_state.player.server_id == -1
        assert not self.game_state.player.is_ready_to_play_event.is_set()

    def test_character_selection_success_sets_character_id(self):
        character = Character(id=123456)
        msg = CharacterSelectionEvent(
            success=CharacterSelectionEvent.Success(character=character)
        )

        self.inject(msg)

        assert self.game_state.player.character_id == 123456

    def test_character_selection_sets_level_and_name(self):
        basic_info = Character.CharacterBasicInformation(level=150, name="TestHero")
        character = Character(id=123456, character_basic_information=basic_info)
        msg = CharacterSelectionEvent(
            success=CharacterSelectionEvent.Success(character=character)
        )

        self.inject(msg)

        assert self.game_state.player.level == 150
        assert self.game_state.player.character_name == "TestHero"

    def test_job_experiences_update_sets_job_levels(self):
        experiences = [
            JobExperience(job_id=1, job_level=100),
            JobExperience(job_id=2, job_level=75),
            JobExperience(job_id=3, job_level=50),
        ]
        msg = JobExperiencesUpdateEvent(experiences=experiences)

        self.inject(msg)

        assert self.game_state.player.jobs_lvl_by_id[1] == 100
        assert self.game_state.player.jobs_lvl_by_id[2] == 70
        assert self.game_state.player.jobs_lvl_by_id[3] == 50

    def test_job_level_minimum_is_one(self):
        experiences = [
            JobExperience(job_id=1, job_level=5),
        ]
        msg = JobExperiencesUpdateEvent(experiences=experiences)

        self.inject(msg)

        assert self.game_state.player.jobs_lvl_by_id[1] == 1

    def test_zaap_known_list_sets_waypoints(self):
        msg = ZaapKnownListEvent(destinations=[10000, 20000, 30000, 40000])

        self.inject(msg)

        assert self.game_state.player.waypoint_map_ids == [10000, 20000, 30000, 40000]

    def test_select_server_request_sets_server_id(self):
        msg = SelectServerRequest(server=42)

        self.inject(msg)

        assert self.game_state.player.server_id == 42

    def test_is_sub_returns_true_when_subscription_active(self):
        future_date = datetime(2099, 12, 31, tzinfo=timezone.utc)
        self.game_state.player.subscription_end_date = future_date

        assert self.game_state.player.is_sub is True

    def test_is_sub_returns_false_when_subscription_expired(self):
        past_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
        self.game_state.player.subscription_end_date = past_date

        assert self.game_state.player.is_sub is False

    def test_limited_lvl_caps_at_200(self):
        self.game_state.player.level = 250

        assert self.game_state.player.limited_lvl == 200

    def test_limited_lvl_returns_level_when_under_200(self):
        self.game_state.player.level = 150

        assert self.game_state.player.limited_lvl == 150

    def test_subscription_end_date_setter_updates_value(self):
        new_date = datetime(2025, 6, 15, tzinfo=timezone.utc)
        self.game_state.player.subscription_end_date = new_date

        assert self.game_state.player.subscription_end_date == new_date

    def test_multiple_job_updates_accumulate(self):
        experiences1 = [JobExperience(job_id=1, job_level=50)]
        self.inject(JobExperiencesUpdateEvent(experiences=experiences1))

        experiences2 = [JobExperience(job_id=2, job_level=60)]
        self.inject(JobExperiencesUpdateEvent(experiences=experiences2))

        assert 1 in self.game_state.player.jobs_lvl_by_id
        assert 2 in self.game_state.player.jobs_lvl_by_id

    def test_job_update_overwrites_previous_level(self):
        experiences1 = [JobExperience(job_id=1, job_level=50)]
        self.inject(JobExperiencesUpdateEvent(experiences=experiences1))

        experiences2 = [JobExperience(job_id=1, job_level=80)]
        self.inject(JobExperiencesUpdateEvent(experiences=experiences2))

        assert self.game_state.player.jobs_lvl_by_id[1] == 80

    def test_zaap_list_update_replaces_previous(self):
        self.inject(ZaapKnownListEvent(destinations=[10000, 20000]))
        self.inject(ZaapKnownListEvent(destinations=[30000, 40000, 50000]))

        assert self.game_state.player.waypoint_map_ids == [30000, 40000, 50000]
