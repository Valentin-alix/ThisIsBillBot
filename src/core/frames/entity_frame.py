from dataclasses import dataclass
from typing import cast

from D3Database.grid.map_point import MapPoint
from D3Mapping.d3_mapping.resources.protos.game.common_pb2 import (
    ActorPositionInformation,
    Direction,
    SpawnInformation,
)
from D3Mapping.d3_mapping.resources.protos.game.context_pb2 import (
    EntitiesDispositionEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.fight_pb2 import (
    FightFighterRefreshEvent,
    FightFighterShowEvent,
    FightSynchronizeEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.game_action_pb2 import (
    GameActionFightEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
    MapMovementEvent,
    MapMovementRefusedEvent,
    MapTeleportOnSameEvent,
)
from src.core.engine.monsters.monster_group import (
    AIFighter,
    EntityFighterInformation,
    MonsterFighter,
    NamedFighterInformation,
)
from src.core.frames.frame import Frame


@dataclass
class EntityFrame(Frame):
    def __post_init__(self):
        self.event_manager.on(
            MapComplementaryInformationEvent,
            self.on_map_complementary_info_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            MapMovementEvent,
            self.on_map_movement_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            EntitiesDispositionEvent,
            self.on_entities_disposition_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            GameActionFightEvent,
            self.on_game_action_fight_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            FightSynchronizeEvent,
            self.on_fight_synchronize_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            FightFighterShowEvent,
            self.on_fight_fighter_show_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            FightFighterRefreshEvent,
            self.on_fight_fighter_refresh_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            MapTeleportOnSameEvent,
            self.on_map_teleport_on_same_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            MapMovementRefusedEvent,
            self.on_map_movement_refused_event,
            originator=self,
            priority=self.priority,
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

    def on_entities_disposition_event(self, msg: EntitiesDispositionEvent):
        for disposition in msg.dispositions:
            self.game_state.entity.update_actor_disposition(
                disposition.entity_id, disposition.direction, disposition.cell_id
            )

    def on_game_action_fight_event(self, msg: GameActionFightEvent):
        try:
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
                        GameActionFightEvent.Summons.SummonsByContextInformation.SummonContextInformation,
                        summon,
                    )

                    entity_info = {}
                    if summon.spawn_information.HasField("monster"):
                        entity_info["ai_fighter"] = AIFighter(
                            monster_fighter_information=MonsterFighter(
                                monster_gid=summon.spawn_information.monster.monster_gid,
                                creature_grade=summon.spawn_information.monster.grade,
                            )
                        )
                    elif summon.spawn_information.HasField("character"):
                        entity_info["named_fighter"] = NamedFighterInformation(
                            name=summon.spawn_information.character.name
                        )
                    elif summon.spawn_information.HasField("companion"):
                        entity_info["entity_fighter"] = EntityFighterInformation(
                            entity_model_id=summon.spawn_information.companion.model_id,
                            master_id=summon.spawn_information.companion.owner_id,
                            level=summon.spawn_information.companion.level,
                        )
                    for sub_summon in summon.summons:
                        related_actor_pos_information = ActorPositionInformation(
                            actor_information=ActorPositionInformation.ActorInformation(
                                fighter=ActorPositionInformation.ActorInformation.FightFighterInformation(
                                    spawn_information=SpawnInformation(
                                        team=related_team,
                                        alive=sub_summon.alive,
                                        position=sub_summon.position,
                                    ),
                                    **entity_info,
                                    stats=summon.characteristics,
                                )
                            ),
                            actor_id=sub_summon.position.actor_id,
                            disposition=sub_summon.position.disposition,
                        )
                        self.game_state.entity.set_actor(
                            related_actor_pos_information, True
                        )
            elif msg.HasField("slide"):
                old_cell_id = self.game_state.entity.actor_by_id[
                    msg.slide.target_id
                ].disposition.cell_id
                direction = self.game_state.entity.actor_by_id[
                    msg.slide.target_id
                ].disposition.direction

                if old_cell_id == msg.slide.start_cell:
                    self.game_state.entity.update_actor_disposition(
                        msg.slide.target_id,
                        direction=direction,
                        cell_id=msg.slide.end_cell,
                    )
                else:
                    self.game_state.entity.update_actor_disposition(
                        msg.slide.target_id,
                        direction=direction,
                        cell_id=msg.slide.start_cell,
                    )

            elif msg.HasField("exchange_positions"):
                source_cell_id = self.game_state.entity.actor_by_id[
                    msg.source_id
                ].disposition.cell_id
                if not msg.exchange_positions.caster_cell_id == source_cell_id:
                    msg.exchange_positions.target_cell_id = (
                        msg.exchange_positions.caster_cell_id
                    )
                    msg.exchange_positions.caster_cell_id = source_cell_id

                target_direction = self.game_state.entity.actor_by_id[
                    msg.exchange_positions.target_id
                ].disposition.direction
                caster_direction = self.game_state.entity.actor_by_id[
                    msg.source_id
                ].disposition.direction

                self.game_state.entity.update_actor_disposition(
                    msg.exchange_positions.target_id,
                    direction=target_direction,
                    cell_id=msg.exchange_positions.caster_cell_id,
                )
                self.game_state.entity.update_actor_disposition(
                    msg.source_id,
                    direction=caster_direction,
                    cell_id=msg.exchange_positions.target_cell_id,
                )
            elif msg.HasField("teleport_on_same_map"):
                if (
                    msg.teleport_on_same_map.target_id
                    in self.game_state.entity.actor_by_id
                ):
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
        except KeyError as err:
            self.logger.error(str(err))

    def on_fight_fighter_refresh_event(self, msg: FightFighterRefreshEvent):
        self.game_state.entity.update_actor_disposition(
            msg.information.actor_id,
            msg.information.disposition.direction,
            msg.information.disposition.cell_id,
        )

    def on_fight_synchronize_event(self, msg: FightSynchronizeEvent):
        for actor in msg.fighters:
            if not actor.actor_information.fighter.spawn_information.alive:
                self.game_state.entity.remove_actor(actor.actor_id)
                self.logger.info("Actor is not alive, let's remove it")
            else:
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
        if self.game_state.map.is_in_map_transition or (
            msg.cell_x == 0 and msg.cell_y == 0
        ):
            return
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
