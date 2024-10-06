from dataclasses import dataclass, field

from ankama_launcher_emulator import AnkamaLauncherHandler, AnkamaLauncherServer
from ankama_launcher_emulator.decrypter.crypto_helper import CryptoHelper
from ankama_launcher_emulator.interfaces.deciphered_api_key import DecipheredApiKey

from src.bot import Bot
from src.core.behaviors.bank.unload_in_bank_behavior import UnloadInBankBehavior
from src.core.behaviors.farms.collect_behavior import CollectBehavior
from src.core.behaviors.farms.fighter_behavior import FighterBehavior
from src.core.behaviors.farms.harvester_behavior import HarvesterBehavior
from src.core.behaviors.fight.fight_behavior import FightBehavior
from src.core.behaviors.fight.fight_placement_behavior import FightPlacementBehavior
from src.core.behaviors.interactive_behavior import InteractiveBehavior
from src.core.behaviors.movements.auto_trip_behavior import AutoTripBehavior
from src.core.behaviors.movements.map_change_behavior import MapChangeBehavior
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior
from src.core.behaviors.npc_dialog_behavior import NpcDialogBehavior
from src.core.frames.entity_frame import EntityFrame
from src.core.frames.fight_frame import FightFrame
from src.core.frames.interactive_frame import InteractiveFrame
from src.core.frames.inventory_frame import InventoryFrame
from src.core.frames.map_frame import MapFrame
from src.core.frames.objective_frame import ObjectiveFrame
from src.core.frames.player_frame import PlayerFrame
from src.core.logic.grid.data_map_provider import DataMapProvider
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.logic.world.world_path_finder import WorldPathFinder
from src.core.states.entity_state import EntityState
from src.core.states.fight_state import FightState
from src.core.states.interactive_state import InteractiveState
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.objective_state import ObjectiveState
from src.core.states.player_state import PlayerState
from src.event_manager import EventManager
from src.interfaces.metaclasses.singleton import Singleton
from src.signals.harvester_signals import HarvesterSignals
from src.signals.message_signals import MessageInfoSignals
from src.signals.player_signals import PlayerSignals, StatePropertySignals


@dataclass
class BotManager(metaclass=Singleton):
    ankama_launcher_handler: AnkamaLauncherHandler = field(
        init=False, default_factory=AnkamaLauncherHandler
    )
    account_by_id: dict[int, DecipheredApiKey] = field(
        default_factory=lambda: {}, init=False
    )

    def __post_init__(self):
        self.ankama_launcher = AnkamaLauncherServer(self.ankama_launcher_handler)
        self.bot_by_account_id = self.get_bot_by_account_id(self.get_accounts())

    @staticmethod
    def get_accounts() -> dict[int, DecipheredApiKey]:
        account_by_id: dict[int, DecipheredApiKey] = {}
        api_keys_datas = CryptoHelper.getStoredApiKeys()
        for api_key_data in api_keys_datas:
            account_by_id[api_key_data["apikey"]["accountId"]] = api_key_data
        return account_by_id

    @staticmethod
    def get_bot_by_account_id(account_by_id: dict[int, DecipheredApiKey]):
        bot_by_account_id: dict[int, Bot] = {}
        for account_id, account in account_by_id.items():
            event_manager = EventManager()

            # signal
            harvester_signals = HarvesterSignals()
            player_signals = PlayerSignals()
            state_property_signals = StatePropertySignals()
            msg_info_signals = MessageInfoSignals()

            # state
            entity_state = EntityState(state_property_signals=state_property_signals)
            interactive_state = InteractiveState(
                state_property_signals=state_property_signals
            )
            inventory_state = InventoryState(
                state_property_signals=state_property_signals
            )
            map_state = MapState(state_property_signals=state_property_signals)
            fight_state = FightState(state_property_signals=state_property_signals)

            player_state = PlayerState(
                state_property_signals=state_property_signals,
                map_state=map_state,
                interactive_state=interactive_state,
                entity_state=entity_state,
                fight_state=fight_state,
            )
            quest_state = ObjectiveState(state_property_signals=state_property_signals)

            # logic
            data_map_provider = DataMapProvider(
                entity_state=entity_state,
                player_state=player_state,
                map_state=map_state,
                fight_state=fight_state,
            )
            path_finding = Pathfinding(
                data_map_provider=data_map_provider,
                player_state=player_state,
                map_state=map_state,
                entity_state=entity_state,
            )
            world_path_finder = WorldPathFinder(
                path_finding=path_finding,
                player_state=player_state,
                map_state=map_state,
                quest_state=quest_state,
                entity_state=entity_state,
                inventory_state=inventory_state,
            )

            # frames
            entity_frame = EntityFrame(
                event_manager=event_manager,
                entity_state=entity_state,
                fight_state=fight_state,
            )
            interactive_frame = InteractiveFrame(
                event_manager=event_manager, interactive_state=interactive_state
            )
            inventory_frame = InventoryFrame(
                event_manager=event_manager, inventory_state=inventory_state
            )
            map_frame = MapFrame(event_manager=event_manager, map_state=map_state)
            player_frame = PlayerFrame(
                event_manager=event_manager,
                player_signals=player_signals,
                player_state=player_state,
                entity_state=entity_state,
            )
            quest_frame = ObjectiveFrame(
                event_manager=event_manager, objective_state=quest_state
            )
            fight_frame = FightFrame(
                event_manager=event_manager, fight_state=fight_state
            )

            # behavior
            map_change_behavior = MapChangeBehavior(event_manager=event_manager)
            map_move_behavior = MapMoveBehavior(
                event_manager=event_manager,
                player_state=player_state,
                path_finding=path_finding,
                map_state=map_state,
                fight_state=fight_state,
            )
            interactive_behavior = InteractiveBehavior(
                player_state=player_state,
                event_manager=event_manager,
                map_behavior=map_move_behavior,
            )
            auto_trip_behavior = AutoTripBehavior(
                event_manager=event_manager,
                map_move_behavior=map_move_behavior,
                map_change_behavior=map_change_behavior,
                interactive_behavior=interactive_behavior,
                interactive_state=interactive_state,
                player_state=player_state,
                world_path_finder=world_path_finder,
            )
            collect_behavior = CollectBehavior(
                event_manager=event_manager,
                path_finding=path_finding,
                interactive_behavior=interactive_behavior,
                interactive_state=interactive_state,
                player_state=player_state,
                inventory_state=inventory_state,
            )
            npc_dialog_behavior = NpcDialogBehavior(
                event_manager=event_manager, auto_trip_behavior=auto_trip_behavior
            )
            unload_in_bank_behavior = UnloadInBankBehavior(
                event_manager=event_manager, npc_dialog_behavior=npc_dialog_behavior
            )
            fight_placement_behavior = FightPlacementBehavior(
                fight_state=fight_state,
                player_state=player_state,
                event_manager=event_manager,
                entity_state=entity_state,
            )
            fight_behavior = FightBehavior(
                event_manager=event_manager,
                fight_state=fight_state,
                player_state=player_state,
                fight_placement_behavior=fight_placement_behavior,
            )

            # module
            harvester = HarvesterBehavior(
                event_manager=event_manager,
                auto_trip_behavior=auto_trip_behavior,
                collect_behavior=collect_behavior,
                path_finding=path_finding,
                player_state=player_state,
                inventory_state=inventory_state,
                map_state=map_state,
                objective_state=quest_state,
                entity_state=entity_state,
                interactive_state=interactive_state,
                unload_in_bank_behavior=unload_in_bank_behavior,
            )
            fighter_behavior = FighterBehavior(
                event_manager=event_manager,
                fight_behavior=fight_behavior,
                entity_state=entity_state,
                map_move_behavior=map_move_behavior,
            )

            bot_by_account_id[account_id] = Bot(
                account=account,
                player_signals=player_signals,
                harvester_signals=harvester_signals,
                player_property_signals=state_property_signals,
                msg_info_signals=msg_info_signals,
                event_manager=event_manager,
                harvester_behavior=harvester,
                frames=[
                    quest_frame,
                    map_frame,
                    player_frame,
                    entity_frame,
                    inventory_frame,
                    interactive_frame,
                    fight_frame,
                ],
                fighter_behavior=fighter_behavior,
            )
        return bot_by_account_id
