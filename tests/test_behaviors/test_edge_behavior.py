from typing import cast
from unittest.mock import Mock

from datas.protos.non_obf.game.gamemap_pb2 import (
    MapCurrentEvent,
    MapMovementRefusedEvent,
)
from dofus_unity_reader.game_constants.transition_type import TransitionTypeEnum
from dofus_unity_reader.grid.map_point import MapPoint
from dofus_unity_reader.models.world_graph import Edge, Transition, Vertice

from src.core.behaviors.behavior import BehaviorState
from src.core.behaviors.farms.fight.fight_behavior import FightBehavior
from src.core.behaviors.interactives.interactive_behavior import InteractiveBehavior
from src.core.behaviors.movements.edge_behavior import EdgeBehavior
from src.core.behaviors.movements.map_change_behavior import (
    MapChangeBehavior,
    MapChangeError,
)
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior
from src.core.engine.movements.map.path_finding.movement_path import MovementPath
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.core.events_manager.event_manager import EventManager
from tests.fixtures.game_state import GameStateContext, set_game_state

SOURCE_MAP_ID = 185862149
DESTINATION_MAP_ID = 185862148
WRONG_MAP_ID = 185862661
PLAYER_START_CELL_ID = 100
SERVER_REFUSED_CELL_ID = 101
TRANSITION_CELL_ID = 7


def make_scroll_edge() -> Edge:
    return Edge(
        m_from=Vertice(m_mapId=SOURCE_MAP_ID, m_zoneId=1, m_uid=SOURCE_MAP_ID),
        m_to=Vertice(
            m_mapId=DESTINATION_MAP_ID,
            m_zoneId=1,
            m_uid=DESTINATION_MAP_ID,
        ),
        m_transitions=[
            Transition(
                m_type=TransitionTypeEnum.SCROLL,
                m_direction=6,
                m_skillId=-1,
                m_criterion="",
                m_transitionMapId=DESTINATION_MAP_ID,
                m_cellId=TRANSITION_CELL_ID,
                m_id=-1,
            )
        ],
    )


def make_movement_path() -> MovementPath:
    path_elements = MovementPath.get_path_elements_from_cells(
        [PLAYER_START_CELL_ID, TRANSITION_CELL_ID]
    )
    return MovementPath(
        start=MapPoint.from_cell_id(PLAYER_START_CELL_ID),
        end=MapPoint.from_cell_id(TRANSITION_CELL_ID),
        path=path_elements,
    )


def make_edge_behavior(game_state_ctx: GameStateContext) -> EdgeBehavior:
    event_manager = EventManager(_logger=game_state_ctx.logger)
    sent_messages: list[object] = []
    event_manager.on_send_game_callback = sent_messages.append

    path_finding = Mock(spec=Pathfinding)
    path_finding.find_path.return_value = make_movement_path()

    map_move_behavior = MapMoveBehavior(
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        path_finding=game_state_ctx.pathfinding,
        _logger=game_state_ctx.logger,
    )

    return EdgeBehavior(
        event_manager=event_manager,
        game_state=game_state_ctx.game_state,
        interactive_behavior=cast(InteractiveBehavior, Mock()),
        map_move_behavior=map_move_behavior,
        map_change_behavior=cast(MapChangeBehavior, Mock()),
        path_finding=cast(Pathfinding, path_finding),
        fight_behavior=cast(FightBehavior, Mock()),
        _logger=game_state_ctx.logger,
    )


def refuse_movement_from_different_server_cell(edge_behavior: EdgeBehavior) -> None:
    refused_map_point = MapPoint.from_cell_id(SERVER_REFUSED_CELL_ID)
    edge_behavior.event_manager.process_msg(
        MapMovementRefusedEvent(
            cell_x=refused_map_point.x,
            cell_y=refused_map_point.y,
        )
    )


class TestEdgeBehavior:
    def test_finishes_when_expected_map_current_arrives_after_invalid_move(
        self, game_state_ctx: GameStateContext
    ) -> None:
        set_game_state(
            game_state_ctx.game_state,
            player_cell_id=PLAYER_START_CELL_ID,
            enemy_cell_ids=[],
            map_id=SOURCE_MAP_ID,
        )
        edge_behavior = make_edge_behavior(game_state_ctx)
        finished_error_codes: list[str | None] = []

        edge_behavior.start(
            callback=finished_error_codes.append,
            parent=None,
            edge=make_scroll_edge(),
        )
        refuse_movement_from_different_server_cell(edge_behavior)

        assert edge_behavior.state == BehaviorState.RUNNING

        edge_behavior.event_manager.process_msg(
            MapCurrentEvent(map_id=DESTINATION_MAP_ID)
        )

        assert finished_error_codes == [None]
        assert edge_behavior.state == BehaviorState.STOPPED

    def test_finishes_with_unexpected_new_map_on_unrelated_map_current(
        self, game_state_ctx: GameStateContext
    ) -> None:
        set_game_state(
            game_state_ctx.game_state,
            player_cell_id=PLAYER_START_CELL_ID,
            enemy_cell_ids=[],
            map_id=SOURCE_MAP_ID,
        )
        edge_behavior = make_edge_behavior(game_state_ctx)
        finished_error_codes: list[str | None] = []

        edge_behavior.start(
            callback=finished_error_codes.append,
            parent=None,
            edge=make_scroll_edge(),
        )

        edge_behavior.event_manager.process_msg(MapCurrentEvent(map_id=WRONG_MAP_ID))

        assert finished_error_codes == [MapChangeError.UNEXPECTED_NEW_MAP]
        assert edge_behavior.state == BehaviorState.STOPPED
