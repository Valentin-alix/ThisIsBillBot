from unittest.mock import MagicMock

import pytest

from src.core.behaviors.movements.auto_trip.auto_trip_behavior import AutoTripErrorCode
from src.core.behaviors.movements.map_change_behavior import MapChangeError
from src.core.bot.bot import Bot
from src.exceptions import UnhandledErrorCodeException


class TestFarmRecovery:
    def test_auto_equipment_skips_sale_hotel_for_never_subscribed_account(
        self, runtime_bot: Bot, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        auto_equipment_behavior = runtime_bot.auto_bot_behavior.auto_equipment_behavior
        sale_hotel_start = MagicMock()
        collect_and_equip = MagicMock()
        auto_equipment_behavior._to_buy = [MagicMock()]
        monkeypatch.setattr(
            type(runtime_bot.game_state.player),
            "is_sub",
            property(lambda _player_state: False),
        )
        monkeypatch.setattr(
            type(runtime_bot.game_state.player),
            "is_former_sub",
            property(lambda _player_state: False),
        )
        monkeypatch.setattr(
            auto_equipment_behavior.sale_hotel_buy_behavior,
            "start",
            sale_hotel_start,
        )
        monkeypatch.setattr(auto_equipment_behavior, "collect_and_equip", collect_and_equip)

        auto_equipment_behavior.buy_missing_items()

        sale_hotel_start.assert_not_called()
        collect_and_equip.assert_called_once_with()

    def test_auto_equipment_keeps_sale_hotel_for_former_subscriber(
        self, runtime_bot: Bot, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        auto_equipment_behavior = runtime_bot.auto_bot_behavior.auto_equipment_behavior
        sale_hotel_start = MagicMock()
        auto_equipment_behavior._to_buy = [MagicMock()]
        monkeypatch.setattr(
            type(runtime_bot.game_state.player),
            "is_sub",
            property(lambda _player_state: False),
        )
        monkeypatch.setattr(
            type(runtime_bot.game_state.player),
            "is_former_sub",
            property(lambda _player_state: True),
        )
        monkeypatch.setattr(
            auto_equipment_behavior.sale_hotel_buy_behavior,
            "start",
            sale_hotel_start,
        )

        auto_equipment_behavior.buy_missing_items()

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
        runtime_bot.game_state.map.forbidden_edge_transitions.add((MagicMock(), MagicMock(), MagicMock()))

        random_farm_behavior.on_auto_trip_world_behavior_finished(AutoTripErrorCode.PATH_NOT_FOUND)

        request_disconnect.assert_called_once_with()
