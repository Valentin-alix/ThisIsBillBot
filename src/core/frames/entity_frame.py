from dataclasses import dataclass
from typing import cast

from protos.game.common_pb2 import (
    SpawnInformation,
    ActorPositionInformation,
    Direction,
)
from protos.game.context_pb2 import (
    ContextRemoveElementEvent,
    EntitiesDispositionEvent,
)
from protos.game.fight_pb2 import (
    FightFighterRefreshEvent,
    FightSynchronizeEvent,
    FightFighterShowEvent,
)
from protos.game.game_action_pb2 import GameActionFightEvent
from protos.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
    MapMovementEvent,
    GameRolePlayShowActorsEvent,
    MapTeleportOnSameEvent,
    MapMovementRefusedEvent,
)
from protos.game.map_confirm_response_pb2 import MapMovementConfirmResponse
from src.core.frames.frame import Frame
from src.core.logic.grid.map_point import MapPoint


@dataclass
class EntityFrame(Frame):

    def __post_init__(self):
        self.event_manager.on(
            MapComplementaryInformationEvent,
            self.on_map_complementary_info_event,
            originator=self,
        )
        self.event_manager.on(
            MapMovementEvent,
            self.on_map_movement_event,
            originator=self,
        )
        self.event_manager.on(
            GameRolePlayShowActorsEvent,
            self.on_game_role_play_show_actors_event,
            originator=self,
        )
        self.event_manager.on(
            ContextRemoveElementEvent,
            self.on_context_remove_element_event,
            originator=self,
        )
        self.event_manager.on(
            EntitiesDispositionEvent,
            self.on_entities_disposition_event,
            originator=self,
        )
        self.event_manager.on(
            GameActionFightEvent, self.on_game_action_fight_event, originator=self
        )
        self.event_manager.on(
            FightSynchronizeEvent, self.on_fight_synchronize_event, originator=self
        )
        self.event_manager.on(
            FightFighterShowEvent, self.on_fight_fighter_show_event, originator=self
        )
        self.event_manager.on(
            FightFighterRefreshEvent,
            self.on_fight_fighter_refresh_event,
            originator=self,
        )
        self.event_manager.on(
            MapTeleportOnSameEvent, self.on_map_teleport_on_same_event, originator=self
        )
        self.event_manager.on(
            MapMovementRefusedEvent, self.on_map_movement_refused_event, originator=self
        )

    def on_map_complementary_info_event(
        self, message: MapComplementaryInformationEvent
    ):
        self.game_state.entity.set_map_obstacles(message.obstacles)
        self.game_state.entity.set_actors(message.actors)

    def on_map_movement_event(self, message: MapMovementEvent):
        self.game_state.entity.update_actor_disposition(
            message.character_id, message.direction, message.cells[-1]
        )

    def on_game_role_play_show_actors_event(self, message: GameRolePlayShowActorsEvent):
        for actor in message.actors:
            self.game_state.entity.set_actor(actor)

    def on_context_remove_element_event(self, message: ContextRemoveElementEvent):
        if message.element_id in self.game_state.entity.actor_by_id:
            self.game_state.entity.remove_actor(message.element_id)

    def on_entities_disposition_event(self, msg: EntitiesDispositionEvent):
        for disposition in msg.dispositions:
            self.game_state.entity.update_actor_disposition(
                disposition.entity_id, disposition.direction, disposition.cell_id
            )

    def on_game_action_fight_event(self, msg: GameActionFightEvent):
        if msg.HasField("death"):
            self.game_state.entity.remove_actor(msg.death.target_id)
        elif msg.HasField("summons") and msg.summons.HasField(
            "summons_by_context_information"
        ):
            related_team = self.game_state.entity.actor_by_id[
                msg.source_id
            ].actor_information.fighter.spawn_information.team
            for summon in msg.summons.summons_by_context_information.summons:
                summon = cast(
                    GameActionFightEvent.Summons.SummonsByContextInformation, summon
                )
                for sub_summon in summon.summons:
                    sub_summon = cast(SpawnInformation, sub_summon)
                    related_actor_information = ActorPositionInformation.ActorInformation(
                        fighter=ActorPositionInformation.ActorInformation.FightFighterInformation(
                            spawn_information=SpawnInformation(team=related_team)
                        )
                    )
                    sub_summon.position.actor_information.CopyFrom(
                        related_actor_information
                    )
                    self.game_state.entity.set_actor(sub_summon.position, True)
        elif msg.HasField("slide"):
            direction = self.game_state.entity.actor_by_id[
                msg.slide.target_id
            ].disposition.direction
            self.game_state.entity.update_actor_disposition(
                msg.slide.target_id, direction=direction, cell_id=msg.slide.end_cell
            )
        elif msg.HasField("exchange_positions"):
            target_direction = self.game_state.entity.actor_by_id[
                msg.exchange_positions.target_id
            ].disposition.direction
            caster_direction = self.game_state.entity.actor_by_id[
                msg.source_id
            ].disposition.direction

            self.game_state.entity.update_actor_disposition(
                msg.exchange_positions.target_id,
                direction=target_direction,
                cell_id=msg.exchange_positions.target_cell_id,
            )
            self.game_state.entity.update_actor_disposition(
                msg.source_id,
                direction=caster_direction,
                cell_id=msg.exchange_positions.caster_cell_id,
            )
        elif msg.HasField("teleport_on_same_map"):
            if msg.teleport_on_same_map.target_id in self.game_state.entity.actor_by_id:
                target_direction = self.game_state.entity.actor_by_id[
                    msg.teleport_on_same_map.target_id
                ].disposition.direction
            else:
                target_direction = Direction.DIRECTION_EAST
            self.game_state.entity.update_actor_disposition(
                cell_id=msg.teleport_on_same_map.cell,
                direction=target_direction,
                actor_id=msg.teleport_on_same_map.target_id,
            )

    def on_fight_fighter_refresh_event(self, msg: FightFighterRefreshEvent):
        self.game_state.entity.set_actor(msg.information)

    def on_fight_synchronize_event(self, msg: FightSynchronizeEvent):
        self.game_state.entity.set_actors(msg.fighters)

    def on_fight_fighter_show_event(self, msg: FightFighterShowEvent):
        self.game_state.entity.set_actor(msg.information)

    def on_map_teleport_on_same_event(self, msg: MapTeleportOnSameEvent):
        if msg.player_id in self.game_state.entity.actor_by_id:
            old_direction = self.game_state.entity.actor_by_id[
                msg.player_id
            ].disposition.direction
        else:
            old_direction = Direction.DIRECTION_EAST
        self.game_state.entity.update_actor_disposition(
            msg.player_id, direction=old_direction, cell_id=msg.cell_id
        )

    def on_map_movement_refused_event(self, msg: MapMovementRefusedEvent):
        self.event_manager.clear_listener_by_origin_and_type(
            MapMovementConfirmResponse, self
        )
        if self.game_state.player.character_id in self.game_state.entity.actor_by_id:
            direction = self.game_state.entity.actor_by_id[
                self.game_state.player.character_id
            ].disposition.direction
        else:
            direction = Direction.DIRECTION_EAST

        self.game_state.entity.update_actor_disposition(
            self.game_state.player.character_id,
            direction=direction,
            cell_id=MapPoint.from_coords(msg.cell_x, msg.cell_y).cell_id,
        )
