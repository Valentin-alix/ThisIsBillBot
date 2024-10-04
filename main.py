from threading import Thread

from src.core.ankama_launcher import AnkamaLauncher
from src.core.behaviors.interactive_behavior import InteractiveBehavior
from src.core.behaviors.map_behavior import MapBehavior
from src.core.handlers.entity_handler import EntityHandler
from src.core.handlers.interactive_handler import InteractiveHandler
from src.core.handlers.player_handler import PlayerHandler
from src.core.logic.grid.data_map_provider import DataMapProvider
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.modules.harvester import Harvester
from src.core.states.entity_state import EntityState
from src.core.states.interactive_state import InteractiveState
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.player_state import PlayerState
from src.gui.application import launch_gui
from src.interfaces.models.bot import Bot
from src.mitm.listener import Listener
from src.signals.harvester_signals import HarvesterSignals
from src.signals.message_events import MessageEvents
from src.signals.message_signals import MessageInfoSignals
from src.signals.player_signals import PlayerSignals, StatePropertySignals


def main() -> None:
    ankama_launcher = AnkamaLauncher()

    bot_by_account_id: dict[int, Bot] = {}
    for account_id, account in ankama_launcher.account_by_id.items():
        # signal
        harvester_signals = HarvesterSignals()
        msg_event = MessageEvents()
        player_signals = PlayerSignals()
        state_property_signals = StatePropertySignals()
        msg_info_signals = MessageInfoSignals()

        # state
        inventory_state = InventoryState(state_property_signals=state_property_signals)
        map_state = MapState(state_property_signals=state_property_signals)
        player_state = PlayerState(
            state_property_signals=state_property_signals, map_state=map_state
        )
        entity_state = EntityState(state_property_signals=state_property_signals)
        interactive_state = InteractiveState(
            player_state=player_state, state_property_signals=state_property_signals
        )

        # logic
        data_map_provider = DataMapProvider(
            entity_state=entity_state, player_state=player_state, map_state=map_state
        )
        path_finding = Pathfinding(
            data_map_provider=data_map_provider,
            player_state=player_state,
            map_state=map_state,
        )

        # handler
        entity_handler = EntityHandler(
            msg_event=msg_event,
            entity_state=entity_state,
            player_state=player_state,
            data_map_provider=data_map_provider,
        )
        player_handler = PlayerHandler(
            msg_event=msg_event,
            player_signals=player_signals,
            player_state=player_state,
        )
        interactive_handler = InteractiveHandler(
            msg_event=msg_event, interactive_state=interactive_state
        )

        # behavior
        map_behavior = MapBehavior(
            msg_event=msg_event,
            player_state=player_state,
            path_finding=path_finding,
            map_state=map_state,
        )
        interactive_behavior = InteractiveBehavior(
            player_state=player_state, msg_event=msg_event, map_behavior=map_behavior
        )

        # module
        harvester = Harvester(
            msg_event=msg_event,
            harvester_signals=harvester_signals,
            map_behavior=map_behavior,
            interactive_behavior=interactive_behavior,
            interactive_state=interactive_state,
            path_finding=path_finding,
            player_state=player_state,
            inventory_state=inventory_state,
        )

        bot_by_account_id[account_id] = Bot(
            account=account,
            player_signals=player_signals,
            harvester_signals=harvester_signals,
            player_property_signals=state_property_signals,
            msg_info_signals=msg_info_signals,
            msg_events=msg_event,
            harvester=harvester,
            entity_handler=entity_handler,
            player_handler=player_handler,
            interactive_handler=interactive_handler,
        )

    listener = Listener(bot_by_account_id)
    Thread(
        target=lambda: listener.start_listener(
            5555, ("dofus2-co-beta.ankama-games.com", 5555), True
        ),
        daemon=True,
    ).start()
    launch_gui(bot_by_account_id)


if __name__ == "__main__":
    main()
