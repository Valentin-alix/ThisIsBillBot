from dataclasses import dataclass

from com.ankama.dofus.server.game.protocol.character.management_pb2 import (
    CharacterSelectionEvent,
)
from com.ankama.dofus.server.game.protocol.character_pb2 import (
    CharacterCharacteristicsEvent,
)
from com.ankama.dofus.server.game.protocol.connection_pb2 import ReloginTokenEvent
from com.ankama.dofus.server.game.protocol.context_pb2 import ContextCreationEvent
from com.ankama.dofus.server.game.protocol.fight_pb2 import FightEndEvent
from src.core.handlers.handler import Handler
from src.core.states.player_state import PlayerState
from src.signals.player_signals import PlayerSignals


@dataclass
class PlayerHandler(Handler):
    player_signals: PlayerSignals
    player_state: PlayerState

    def __post_init__(self):
        self.msg_event.received_game_msg.connect(
            self.on_character_selection_event, CharacterSelectionEvent
        )
        self.msg_event.received_game_msg.connect(
            self.on_re_login_event, ReloginTokenEvent
        )
        self.msg_event.received_game_msg.connect(
            self.on_context_creation_event, ContextCreationEvent
        )
        self.msg_event.received_game_msg.connect(self.on_fight_end_event, FightEndEvent)

        self.msg_event.received_game_msg.connect(
            self.on_character_characteristics, CharacterCharacteristicsEvent
        )

    def on_character_selection_event(self, _, message: CharacterSelectionEvent):
        if message.HasField("success"):
            self.player_state.character = message.success.character
            self.player_signals.connected.emit()

    def on_re_login_event(self, _, message: ReloginTokenEvent):
        self.player_state.character = None
        self.player_signals.disconnected.emit()

    def on_context_creation_event(self, _, message: ContextCreationEvent):
        if message.context == ContextCreationEvent.GameContext.FIGHT:
            self.player_state.is_in_fight = True

    def on_fight_end_event(self, _, message: FightEndEvent):
        self.player_state.is_in_fight = False

    def on_character_characteristics(self, _, message: CharacterCharacteristicsEvent):
        self.player_state.characteristics = message
