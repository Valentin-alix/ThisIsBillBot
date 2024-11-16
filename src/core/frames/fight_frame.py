from dataclasses import dataclass

from D3Mapping.d3_mapping.resources.protos.game.character_pb2 import (
    CharacterCharacteristicsEvent,
    UpdateLifePointsEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.fight_pb2 import (
    FightLiveStateEvent,
    FightRefreshCharacterStatsEvent,
    FightTurnFinishRequest,
    FightTurnStartPlayingEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.fight_preparation_pb2 import (
    FightPlacementPossiblePositionsEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.game_action_pb2 import (
    GameActionFightCastRequest,
    GameActionFightEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.gamemap_pb2 import (
    FightMapInformationEvent,
    MapComplementaryInformationEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.spell_pb2 import (
    SpellsEvent,
)
from src.core.frames.frame import Frame


@dataclass
class FightFrame(Frame):
    def __post_init__(self):
        self.event_manager.on(
            FightPlacementPossiblePositionsEvent,
            self.on_fight_placement_position_request,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            MapComplementaryInformationEvent,
            self.on_map_complementary_information_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            SpellsEvent,
            self.on_spells_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            GameActionFightCastRequest,
            self.on_game_action_fight_cast_request,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            CharacterCharacteristicsEvent,
            self.on_character_characteristics_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.before(
            FightTurnFinishRequest,
            self.before_fight_turn_finish_request,
            originator=self,
        )
        self.event_manager.on(
            FightTurnStartPlayingEvent,
            self.on_fight_turn_start_playing_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            FightLiveStateEvent,
            self.on_fight_live_state_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            UpdateLifePointsEvent,
            self.on_update_life_points_event,
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
            FightRefreshCharacterStatsEvent,
            self.on_fight_refresh_character_stats_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            CharacterCharacteristicsEvent,
            self.on_character_characteristics_event,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            FightTurnFinishRequest,
            self.on_fight_turn_finish_request,
            originator=self,
            priority=self.priority,
        )
        self.event_manager.on(
            FightMapInformationEvent,
            self.on_fight_map_information_event,
            originator=self,
            priority=self.priority,
        )

    def on_fight_live_state_event(self, msg: FightLiveStateEvent):
        for actor_id in list(self.game_state.entity.actor_by_id.keys()):
            related_entity_state = next(
                (
                    entity_state
                    for entity_state in msg.entities_states
                    if entity_state.entity_id == actor_id
                ),
                None,
            )
            if not related_entity_state or related_entity_state.is_dead:
                self.game_state.entity.remove_actor(actor_id)

    def on_fight_placement_position_request(
        self, msg: FightPlacementPossiblePositionsEvent
    ):
        if (
            self.game_state.map.map_point.cell_id
            in msg.starting_positions.challengers_positions
        ):
            self.game_state.fight.fight_placement_possible_positions = list(
                msg.starting_positions.challengers_positions
            )
        else:
            self.game_state.fight.fight_placement_possible_positions = list(
                msg.starting_positions.defenders_positions
            )

    def on_spells_event(self, message: SpellsEvent):
        self.game_state.fight.spells = list(message.human_spells)

    def on_game_action_fight_cast_request(self, message: GameActionFightCastRequest):
        self.game_state.fight.count_casted_by_spell_id_on_current_turn[
            message.spell_id
        ] = (
            self.game_state.fight.count_casted_by_spell_id_on_current_turn.get(
                message.spell_id, 0
            )
            + 1
        )

    def on_character_characteristics_event(
        self, message: CharacterCharacteristicsEvent
    ):
        self.game_state.fight.modifier_by_type_and_spell_id.clear()
        for spell_modifier in message.stats.spell_modifiers:
            self.game_state.fight.modifier_by_type_and_spell_id[
                (spell_modifier.spell_id, spell_modifier.modifier_type)
            ] = spell_modifier

        for stat in message.stats.characteristics:
            self.game_state.fight.characteristic_by_id[stat.characteristic_id] = stat

    def before_fight_turn_finish_request(
        self, msg: FightTurnFinishRequest
    ) -> FightTurnFinishRequest | None:
        if self.is_playing_event.is_set() and msg.is_active:
            return None
        return msg

    def on_fight_turn_start_playing_event(self, msg: FightTurnStartPlayingEvent):
        self.game_state.fight.count_casted_by_spell_id_on_current_turn.clear()
        self.game_state.fight.is_our_turn = True
        self.game_state.fight.fight_turn += 1

    def on_fight_turn_finish_request(self, msg: FightTurnFinishRequest):
        self.game_state.fight.count_casted_by_spell_id_on_current_turn.clear()
        self.game_state.fight.is_our_turn = False

    def on_map_complementary_information_event(
        self, msg: MapComplementaryInformationEvent
    ):
        self.game_state.fight.is_our_turn = False
        self.game_state.fight.in_fight = False
        self.game_state.fight.fight_turn = 0
        self.game_state.fight.is_map_fight_initialized = False

    def on_update_life_points_event(self, msg: UpdateLifePointsEvent):
        self.game_state.fight.life_point = msg.life_points
        self.game_state.fight.max_life_point = msg.max_life_points

    def on_game_action_fight_event(self, msg: GameActionFightEvent):
        if (
            msg.HasField("life_points_gain")
            and msg.life_points_gain.target_id == self.game_state.player.character_id
        ):
            self.game_state.fight.life_point += msg.life_points_gain.delta
        if (
            msg.HasField("life_points_lost")
            and msg.life_points_lost.target_id == self.game_state.player.character_id
        ):
            self.game_state.fight.life_point -= msg.life_points_lost.loss

    def on_fight_refresh_character_stats_event(
        self, msg: FightRefreshCharacterStatsEvent
    ):
        if self.game_state.player.character_id != msg.fighter_id:
            return
        for characteristic in msg.stats.characteristics:
            self.game_state.fight.characteristic_by_id[
                characteristic.characteristic_id
            ] = characteristic

    def on_fight_map_information_event(self, msg: FightMapInformationEvent):
        self.game_state.fight.count_casted_by_spell_id_on_current_turn.clear()
        self.game_state.fight.modifier_by_type_and_spell_id.clear()
        self.game_state.fight.in_fight = True
        self.game_state.fight.is_map_fight_initialized = True
