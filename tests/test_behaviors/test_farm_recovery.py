from unittest.mock import MagicMock
from datetime import datetime, timedelta

import pytest

from dofus_unity_reader.game_constants.item import CategoryItemEnum, ItemEnum

from datas.protos.non_obf.game.gamemap_pb2 import MapComplementaryInformationEvent, MapCurrentEvent

from src.core.behaviors.farms.random_farm_behavior import MAX_CONSECUTIVE_UNEXPECTED_NEW_MAPS
from src.core.behaviors.items.acquire_items_behavior import (
    AcquireItemsBehavior,
    ItemToAcquire,
)
from src.core.behaviors.movements.auto_trip.auto_trip_behavior import AutoTripErrorCode
from src.core.behaviors.movements.map_change_behavior import MapChangeError
from src.core.engine.movements.world.transition_ban import BannedTransition, TransitionBanScope
from src.core.bot.bot import Bot
from src.core.bot.session_activity_plan import SessionActivity, SessionActivityPlan, SessionActivitySlot
from src.exceptions import UnhandledErrorCodeException


class TestFarmRecovery:
    def test_empty_activity_is_removed_and_remaining_slots_are_redistributed(self) -> None:
        session_start = datetime(2026, 8, 12, 8)
        session_end = session_start + timedelta(hours=8)
        reschedule_at = session_start + timedelta(hours=2)
        plan = SessionActivityPlan(
            session_start=session_start,
            session_end=session_end,
            slots=[
                SessionActivitySlot(SessionActivity.QUEST, session_start + timedelta(hours=1)),
                SessionActivitySlot(SessionActivity.DUNGEON, session_start + timedelta(hours=3)),
                SessionActivitySlot(SessionActivity.CRAFT, session_start + timedelta(hours=5)),
            ],
        )

        plan.discard_empty_activity(SessionActivity.QUEST, reschedule_at)

        assert plan.completed_activities == {SessionActivity.QUEST}
        assert [slot.activity for slot in plan.slots] == [SessionActivity.DUNGEON, SessionActivity.CRAFT]
        assert all(reschedule_at < slot.starts_at < session_end for slot in plan.slots)

    def test_auto_bot_redistributes_slots_after_an_empty_activity(
        self, runtime_bot: Bot, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        auto_bot_behavior = runtime_bot.auto_bot_behavior
        session_start = datetime.now() - timedelta(hours=2)
        session_end = session_start + timedelta(hours=8)
        auto_bot_behavior._session_activity_plan = SessionActivityPlan(
            session_start=session_start,
            session_end=session_end,
            slots=[
                SessionActivitySlot(SessionActivity.QUEST, session_start + timedelta(hours=1)),
                SessionActivitySlot(SessionActivity.DUNGEON, session_start + timedelta(hours=3)),
            ],
        )
        monkeypatch.setattr(auto_bot_behavior, "run_timer", MagicMock())

        auto_bot_behavior._on_session_activity_finished(SessionActivity.QUEST, None)

        assert auto_bot_behavior._session_activity_plan.completed_activities == {SessionActivity.QUEST}
        assert [slot.activity for slot in auto_bot_behavior._session_activity_plan.slots] == [
            SessionActivity.DUNGEON
        ]

    @staticmethod
    def _prepare_sourcing(
        runtime_bot: Bot, monkeypatch: pytest.MonkeyPatch, *, is_former_sub: bool
    ) -> tuple[AcquireItemsBehavior, MagicMock]:
        acquire_items_behavior = runtime_bot.auto_bot_behavior.auto_equipment_behavior.acquire_items_behavior
        sale_hotel_start = MagicMock()
        monkeypatch.setattr(acquire_items_behavior.sale_hotel_buy_behavior, "start", sale_hotel_start)
        monkeypatch.setattr(acquire_items_behavior.load_from_bank_behavior, "start", MagicMock())
        monkeypatch.setattr(
            type(runtime_bot.game_state.player),
            "is_sub",
            property(lambda _player_state: False),
        )
        monkeypatch.setattr(
            type(runtime_bot.game_state.player),
            "is_former_sub",
            property(lambda _player_state: is_former_sub),
        )
        runtime_bot.game_state.inventory.bank_content_known = True
        return acquire_items_behavior, sale_hotel_start

    def test_sourcing_skips_sale_hotel_for_never_subscribed_account(
        self, runtime_bot: Bot, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        acquire_items_behavior, sale_hotel_start = self._prepare_sourcing(
            runtime_bot, monkeypatch, is_former_sub=False
        )

        acquire_items_behavior.start(
            items=[
                ItemToAcquire(
                    item_gid=ItemEnum.AMULETTE_AKWADALA,
                    max_kamas=10_000,
                    category=CategoryItemEnum.EQUIPMENT,
                )
            ],
            callback=None,
            parent=None,
        )

        sale_hotel_start.assert_not_called()

    def test_sourcing_keeps_sale_hotel_for_former_subscriber(
        self, runtime_bot: Bot, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        acquire_items_behavior, sale_hotel_start = self._prepare_sourcing(
            runtime_bot, monkeypatch, is_former_sub=True
        )

        acquire_items_behavior.start(
            items=[
                ItemToAcquire(
                    item_gid=ItemEnum.AMULETTE_AKWADALA,
                    max_kamas=10_000,
                    category=CategoryItemEnum.EQUIPMENT,
                )
            ],
            callback=None,
            parent=None,
        )

        sale_hotel_start.assert_called_once()

    def test_interactive_transition_accepts_fight_interruption(self, runtime_bot: Bot) -> None:
        edge_behavior = runtime_bot.fighter_behavior.random_farm_behavior.edge_behavior
        edge = MagicMock()
        transition = MagicMock()
        edge.m_to.m_mapId = 123
        runtime_bot.game_state.map.map_id = 124
        runtime_bot.game_state.fight.in_fight = True

        edge_behavior.on_interactive_behavior_finished(
            MapChangeError.UNEXPECTED_NEW_MAP,
            edge=edge,
            transition=transition,
            element_id=456,
        )

    def test_interactive_transition_rejects_unexpected_roleplay_map(self, runtime_bot: Bot) -> None:
        edge_behavior = runtime_bot.fighter_behavior.random_farm_behavior.edge_behavior
        edge = MagicMock()
        transition = MagicMock()
        edge.m_to.m_mapId = 123
        runtime_bot.game_state.map.map_id = 124
        runtime_bot.game_state.fight.in_fight = False

        with pytest.raises(UnhandledErrorCodeException):
            edge_behavior.on_interactive_behavior_finished(
                MapChangeError.UNEXPECTED_NEW_MAP,
                edge=edge,
                transition=transition,
                element_id=456,
            )

    def test_incomplete_fight_initialization_requests_disconnect(
        self, runtime_bot: Bot, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        attacker_behavior = runtime_bot.fighter_behavior.attacker_behavior
        request_disconnect = MagicMock()
        attack_enemy = MagicMock()
        runtime_bot.game_state.fight.in_fight = True
        runtime_bot.event_manager.request_disconnect_callback = request_disconnect
        monkeypatch.setattr(attacker_behavior, "attack_enemy", attack_enemy)

        attacker_behavior.on_fight_map_information_timeout(-20_003)

        request_disconnect.assert_called_once_with()
        attack_enemy.assert_not_called()

    def test_path_blocked_by_forbidden_transition_requests_disconnect(self, runtime_bot: Bot) -> None:
        random_farm_behavior = runtime_bot.fighter_behavior.random_farm_behavior
        request_disconnect = MagicMock()
        runtime_bot.event_manager.request_disconnect_callback = request_disconnect
        runtime_bot.game_state.map.banned_edge_transitions.add(
            BannedTransition(MagicMock(), MagicMock(), MagicMock(), TransitionBanScope.SESSION)
        )

        random_farm_behavior.on_auto_trip_world_behavior_finished(AutoTripErrorCode.PATH_NOT_FOUND)

        request_disconnect.assert_called_once_with()

    def test_landing_on_an_unexpected_map_forbids_the_transition(self, runtime_bot: Bot) -> None:
        """An outdated world graph would otherwise send the bot back and forth forever."""
        edge_behavior = runtime_bot.fighter_behavior.random_farm_behavior.edge_behavior
        edge = MagicMock()
        transition = MagicMock()
        edge.m_to.m_mapId = 147981825
        runtime_bot.game_state.fight.in_fight = False

        edge_behavior.on_map_current_event(
            MapCurrentEvent(map_id=149947392), edge=edge, transition=transition
        )

        assert runtime_bot.game_state.map.has_session_banned_transitions

    def test_landing_on_the_expected_map_keeps_the_transition(self, runtime_bot: Bot) -> None:
        edge_behavior = runtime_bot.fighter_behavior.random_farm_behavior.edge_behavior
        edge = MagicMock()
        transition = MagicMock()
        edge.m_to.m_mapId = 147981825
        runtime_bot.game_state.fight.in_fight = False

        edge_behavior.on_map_current_event(
            MapCurrentEvent(map_id=147981825), edge=edge, transition=transition
        )

        assert not runtime_bot.game_state.map.banned_edge_transitions

    def test_repeated_unexpected_map_changes_request_disconnect(self, runtime_bot: Bot) -> None:
        random_farm_behavior = runtime_bot.fighter_behavior.random_farm_behavior
        request_disconnect = MagicMock()
        runtime_bot.event_manager.request_disconnect_callback = request_disconnect
        edge = MagicMock()

        for _ in range(MAX_CONSECUTIVE_UNEXPECTED_NEW_MAPS):
            random_farm_behavior.edge_path = [edge]
            random_farm_behavior.on_edge_behavior_finished(MapChangeError.UNEXPECTED_NEW_MAP, edge=edge)

        request_disconnect.assert_called_once_with()

    def test_an_exit_out_of_reach_is_only_banned_for_the_current_map_stay(self, runtime_bot: Bot) -> None:
        """Map 193331717 is split in two zones: its other zone exits are reachable once we enter it."""
        edge_behavior = runtime_bot.fighter_behavior.random_farm_behavior.edge_behavior
        edge = MagicMock()
        transition = MagicMock()

        edge_behavior.handle_unreachable_transition(edge, transition)

        assert not runtime_bot.game_state.map.has_session_banned_transitions
        assert (edge.m_from, edge.m_to, transition) in (
            runtime_bot.game_state.get_world_transition_context().forbidden_edge_transitions
        )

        runtime_bot.event_manager.process_msg(
            MapComplementaryInformationEvent(map_id=runtime_bot.game_state.map.map_id)
        )

        assert not runtime_bot.game_state.map.banned_edge_transitions
