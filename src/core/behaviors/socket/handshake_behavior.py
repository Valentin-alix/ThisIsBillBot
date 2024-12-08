from dataclasses import dataclass, field

from datas.protos.non_obf.game.character_management_pb2 import (
    CharacterForceSelectionEvent,
    CharacterForceSelectionReadyRequest,
    CharacterListEvent,
    CharacterListRequest,
    CharacterLoadingCompleteEvent,
    CharacterSelectionEvent,
    CharacterSelectionRequest,
)
from datas.protos.non_obf.game.connection_pb2 import (
    AuthenticationTicketAcceptedEvent,
    IdentificationRequest as GameIdentificationRequest,
)
from datas.protos.non_obf.game.context_pb2 import (
    ContextCreationRequest,
    ContextReadyRequest,
)
from datas.protos.non_obf.game.gamemap_pb2 import (
    MapCurrentEvent,
    MapCurrentInstanceEvent,
)

from src.core.behaviors.behavior import Behavior


@dataclass
class HandshakeBehavior(Behavior):
    _context_creation_sent: bool = field(init=False, default=False)
    _context_ready_sent: bool = field(init=False, default=False)
    _pending_map_id: int | None = field(init=False, default=None)

    def run(self, ticket: str) -> None:
        self._reset_state()
        self._register_bootstrap_listeners()
        self.logger.info("Starting game handshake")
        self.event_manager.send(
            GameIdentificationRequest(ticket_key=ticket, language_code="fr")
        )

    def stop(self) -> None:
        self._reset_state()
        super().stop()

    def _reset_state(self) -> None:
        self._context_creation_sent = False
        self._context_ready_sent = False
        self._pending_map_id = None

    def _register_bootstrap_listeners(self) -> None:
        self.event_manager.on(
            AuthenticationTicketAcceptedEvent,
            self.on_authentication_ticket_accepted_event,
            originator=self,
            once=True,
        )
        self.event_manager.on(
            CharacterListEvent,
            self.on_character_list_event,
            originator=self,
            once=True,
        )
        self.event_manager.on(
            CharacterForceSelectionEvent,
            self.on_character_force_selection_event,
            originator=self,
        )
        self.event_manager.on(
            CharacterSelectionEvent,
            self.on_character_selection_event,
            originator=self,
            once=True,
        )
        self.event_manager.on(
            CharacterLoadingCompleteEvent,
            self.on_character_loading_complete_event,
            originator=self,
            once=True,
        )
        self.event_manager.on(
            MapCurrentEvent,
            self.on_map_current_event,
            originator=self,
            once=True,
        )
        self.event_manager.on(
            MapCurrentInstanceEvent,
            self.on_map_current_instance_event,
            originator=self,
            once=True,
        )

    def on_authentication_ticket_accepted_event(
        self, _msg: AuthenticationTicketAcceptedEvent
    ) -> None:
        self.logger.info("Game ticket accepted, requesting character list")
        self.event_manager.send(CharacterListRequest())

    def on_character_list_event(self, msg: CharacterListEvent) -> None:
        if not msg.characters:
            raise ValueError("CharacterListEvent has no characters")

        character = msg.characters[0]
        self.logger.info(f"Selecting character {character.id}")
        self.event_manager.send(CharacterSelectionRequest(character_id=character.id))

    def on_character_force_selection_event(
        self, msg: CharacterForceSelectionEvent
    ) -> None:
        self.logger.info(f"Character force selection requested for {msg.character_id}")
        self.event_manager.send(CharacterForceSelectionReadyRequest())

    def on_character_selection_event(self, msg: CharacterSelectionEvent) -> None:
        if msg.HasField("error"):
            raise ValueError(f"CharacterSelectionEvent failed: {msg}")
        self.logger.info("Character selected, waiting for loading completion")

    def on_character_loading_complete_event(
        self, _msg: CharacterLoadingCompleteEvent
    ) -> None:
        self.logger.info("Character loading complete, requesting context creation")
        self.event_manager.send(ContextCreationRequest())
        self._context_creation_sent = True
        self._try_send_context_ready()

    def on_map_current_event(self, msg: MapCurrentEvent) -> None:
        self._pending_map_id = msg.map_id
        self.logger.info(f"Received current map id={msg.map_id}")
        self._try_send_context_ready()

    def on_map_current_instance_event(self, msg: MapCurrentInstanceEvent) -> None:
        self._pending_map_id = msg.map_id
        self.logger.info(f"Received current map instance id={msg.map_id}")
        self._try_send_context_ready()

    def _try_send_context_ready(self) -> None:
        if self._context_ready_sent:
            return
        if not self._context_creation_sent or self._pending_map_id is None:
            return

        map_id = self._pending_map_id
        self.logger.info(f"Sending ContextReadyRequest for map {map_id}")
        self.event_manager.send(ContextReadyRequest(map_id=map_id))
        self._context_ready_sent = True
        self.finish()
