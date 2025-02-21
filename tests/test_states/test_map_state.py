from datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
    EntityDisposition,
)
from datas.protos.non_obf.game.gamemap_pb2 import (
    FightMapInformationEvent,
    MapCurrentEvent,
)

from src.core.bot.bot import Bot


class TestMapState:
    def test_map_current_event_starts_transition_and_resets_map_state(
        self,
        runtime_bot: Bot,
    ):
        actor = ActorPositionInformation(
            actor_id=1,
            disposition=EntityDisposition(
                cell_id=100,
                entity_id=1,
            ),
        )

        runtime_bot.game_state.map.is_in_map_transition = False
        runtime_bot.game_state.entity.set_actor(actor)

        runtime_bot.event_manager.process_msg(MapCurrentEvent(map_id=12345))

        assert runtime_bot.game_state.map.map_id == 12345
        assert runtime_bot.game_state.map.is_in_map_transition is True
        assert runtime_bot.game_state.entity.actor_by_id == {}

    def test_fight_map_information_event_ends_transition_and_exits_haven_bag(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.game_state.map.is_in_map_transition = True
        runtime_bot.game_state.map.is_in_haven_bag = True

        runtime_bot.event_manager.process_msg(FightMapInformationEvent())

        assert runtime_bot.game_state.map.is_in_map_transition is False
        assert runtime_bot.game_state.map.is_in_haven_bag is False
