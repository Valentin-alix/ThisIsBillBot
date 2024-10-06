from dataclasses import dataclass
from typing import cast

from db_dofus_unity.protos.game.common_pb2 import SpawnInformation
from db_dofus_unity.protos.game.context_pb2 import (
    ContextRemoveElementEvent,
    EntitiesDispositionEvent,
)
from db_dofus_unity.protos.game.fight_pb2 import (
    FightFighterRefreshEvent,
    FightSynchronizeEvent,
    FightFighterShowEvent,
)
from db_dofus_unity.protos.game.game_action_pb2 import GameActionFightEvent
from db_dofus_unity.protos.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
    MapMovementEvent,
    GameRolePlayShowActorsEvent,
    MapCurrentEvent,
)
from src.core.frames.frame import Frame
from src.core.states.entity_state import EntityState
from src.core.states.fight_state import FightState


@dataclass
class EntityFrame(Frame):
    entity_state: EntityState
    fight_state: FightState

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
            MapCurrentEvent, self.on_map_current_event, originator=self
        )

    def on_map_complementary_info_event(
        self, message: MapComplementaryInformationEvent
    ):
        self.entity_state.set_map_obstacles(message.obstacles)
        self.entity_state.set_actors(message.actors)

    def on_map_movement_event(self, message: MapMovementEvent):
        self.entity_state.update_actor_disposition(
            message.character_id, message.direction, message.cells[-1]
        )

    def on_game_role_play_show_actors_event(self, message: GameRolePlayShowActorsEvent):
        for actor in message.actors:
            self.entity_state.set_actor(actor)

    def on_context_remove_element_event(self, message: ContextRemoveElementEvent):
        if message.element_id in self.entity_state.actor_by_id:
            self.entity_state.remove_actor(message.element_id)

    def on_entities_disposition_event(self, msg: EntitiesDispositionEvent):
        for disposition in msg.dispositions:
            self.entity_state.update_actor_disposition(
                disposition.entity_id, disposition.direction, disposition.cell_id
            )

    def on_game_action_fight_event(self, msg: GameActionFightEvent):
        if msg.HasField("death"):
            self.entity_state.remove_actor(msg.death.target_id)
        elif msg.HasField("summons") and msg.summons.HasField(
            "summons_by_context_information"
        ):
            for summon in msg.summons.summons_by_context_information.summons:
                summon = cast(
                    GameActionFightEvent.Summons.SummonsByContextInformation, summon
                )
                for sub_summon in summon.summons:
                    sub_summon = cast(SpawnInformation, sub_summon)
                    self.entity_state.set_actor(sub_summon.position)

    def on_fight_fighter_refresh_event(self, msg: FightFighterRefreshEvent):
        self.entity_state.set_actor(msg.information)

    def on_fight_synchronize_event(self, msg: FightSynchronizeEvent):
        self.entity_state.set_actors(msg.fighters)

    def on_fight_fighter_show_event(self, msg: FightFighterShowEvent):
        self.entity_state.set_actor(msg.information)

    def on_map_current_event(self, msg: MapCurrentEvent):
        self.entity_state.clear_actors()
        self.entity_state.clear_obstacles()
