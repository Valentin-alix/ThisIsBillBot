from dataclasses import dataclass, field

from ankama_launcher_emulator import AnkamaLauncherHandler, AnkamaLauncherServer
from ankama_launcher_emulator.decrypter.crypto_helper import CryptoHelper
from ankama_launcher_emulator.interfaces.deciphered_api_key import DecipheredApiKey

from src.bot import Bot
from src.common.logger import Logger
from src.core.behaviors.bank.unload_behavior import UnloadBehavior
from src.core.behaviors.bank.unload_in_bank_behavior import UnloadInBankBehavior
from src.core.behaviors.bank.unload_in_guild_chest_behavior import (
    UnloadInGuildChestBehavior,
)
from src.core.behaviors.farms.fighter.fighter_behavior import FighterBehavior
from src.core.behaviors.farms.harvest.collect_behavior import CollectBehavior
from src.core.behaviors.farms.harvest.harvester_behavior import HarvesterBehavior
from src.core.behaviors.farms.random_farm_behavior import RandomFarmBehavior
from src.core.behaviors.fight.fight_behavior import FightBehavior
from src.core.behaviors.fight.fight_challenge_behavior import FightChallengeBehavior
from src.core.behaviors.fight.fight_movement_behavior import FightMovementBehavior
from src.core.behaviors.fight.fight_preparation_behavior import FightPreparationBehavior
from src.core.behaviors.fight.fight_spell_behavior import FightSpellBehavior
from src.core.behaviors.fight.fight_turn_behavior import FightTurnBehavior
from src.core.behaviors.fight.revive_behavior import ReviveBehavior
from src.core.behaviors.interactive_behavior import InteractiveBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_behavior import AutoTripBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_explorator_behavior import (
    AutoTripExploratorBehavior,
)
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.movements.auto_trip.auto_trip_zaap_behavior import (
    AutoTripZaapBehavior,
)
from src.core.behaviors.movements.edge_behavior import EdgeBehavior
from src.core.behaviors.movements.map_change_behavior import MapChangeBehavior
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior
from src.core.behaviors.movements.waypoint_behavior import WaypointBehavior
from src.core.behaviors.npc_dialog_behavior import NpcDialogBehavior
from src.core.frames.connection_frame import ConnectionFrame
from src.core.frames.entity_frame import EntityFrame
from src.core.frames.fight_frame import FightFrame
from src.core.frames.interactive_frame import InteractiveFrame
from src.core.frames.inventory_frame import InventoryFrame
from src.core.frames.map_frame import MapFrame
from src.core.frames.objective_frame import ObjectiveFrame
from src.core.frames.player_frame import PlayerFrame
from src.core.logic.farmer.weighted_path import WeightedPath
from src.core.logic.fight.attack import Attacker
from src.core.logic.fight.reachable_cells.fight_reachable_cells import (
    FightReachableCells,
)
from src.core.logic.grid.data_map_provider import DataMapProvider
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.logic.world.astar_allow_capability import AstarAllowHavreSac
from src.core.logic.world.astar_no_interactive import AstarNoInteractive
from src.core.logic.world.astar_world import AstarWorld
from src.core.logic.world.world_path_finder import WorldPathFinder
from src.core.states.state_factory import StateFactory
from src.event_manager import EventManager
from src.interfaces.metaclasses.singleton import Singleton
from src.signals.grid_signals import GridSignals
from src.signals.harvester_signals import FarmActionSignals
from src.signals.log_signals import LogSignals
from src.signals.message_signals import MessageInfoSignals
from src.signals.player_signals import GameInfoSignals
from src.signals.world_signals import WorldSignals


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
            # signal
            harvester_signals = FarmActionSignals()
            game_info_signals = GameInfoSignals()
            msg_info_signals = MessageInfoSignals()
            grid_signals = GridSignals()
            world_signals = WorldSignals()
            log_signals = LogSignals()

            logger = Logger(title=account["apikey"]["login"], log_signals=log_signals)

            event_manager = EventManager(logger=logger)

            # state
            game_state = StateFactory.create_game_state(
                game_info_signals, grid_signals, logger=logger
            )

            # logic
            data_map_provider = DataMapProvider(game_state=game_state)
            path_finding = Pathfinding(
                data_map_provider=data_map_provider,
                game_state=game_state,
                logger=logger,
            )
            astar_world = AstarWorld(game_state=game_state)
            world_path_finder = WorldPathFinder(
                path_finding=path_finding,
                game_state=game_state,
                astar_world=astar_world,
            )
            fight_reachable_cells = FightReachableCells(game_state=game_state)
            attacker = Attacker(
                game_state=game_state,
                path_finding=path_finding,
                logger=logger,
                fight_reachable_cells=fight_reachable_cells,
            )

            # frames
            entity_frame = EntityFrame(
                event_manager=event_manager, game_state=game_state, logger=logger
            )
            interactive_frame = InteractiveFrame(
                event_manager=event_manager, game_state=game_state, logger=logger
            )
            inventory_frame = InventoryFrame(
                event_manager=event_manager, game_state=game_state, logger=logger
            )
            map_frame = MapFrame(
                event_manager=event_manager,
                game_state=game_state,
                world_signals=world_signals,
                logger=logger,
            )
            player_frame = PlayerFrame(
                event_manager=event_manager,
                game_info_signals=game_info_signals,
                game_state=game_state,
                logger=logger,
            )
            quest_frame = ObjectiveFrame(
                event_manager=event_manager, game_state=game_state, logger=logger
            )
            fight_frame = FightFrame(
                event_manager=event_manager, game_state=game_state, logger=logger
            )
            connection_frame = ConnectionFrame(
                event_manager=event_manager,
                game_state=game_state,
                game_info_signals=game_info_signals,
                logger=logger,
            )

            # behavior
            map_change_behavior = MapChangeBehavior(
                event_manager=event_manager, game_state=game_state, logger=logger
            )
            map_move_behavior = MapMoveBehavior(
                event_manager=event_manager,
                game_state=game_state,
                path_finding=path_finding,
                logger=logger,
            )
            interactive_behavior = InteractiveBehavior(
                game_state=game_state,
                event_manager=event_manager,
                map_move_behavior=map_move_behavior,
                logger=logger,
            )
            edge_behavior = EdgeBehavior(
                event_manager=event_manager,
                interactive_behavior=interactive_behavior,
                game_state=game_state,
                map_change_behavior=map_change_behavior,
                map_move_behavior=map_move_behavior,
                path_finding=path_finding,
                logger=logger,
            )
            auto_trip_behavior = AutoTripBehavior(
                event_manager=event_manager,
                world_path_finder=world_path_finder,
                game_state=game_state,
                world_signals=world_signals,
                edge_behavior=edge_behavior,
                logger=logger,
            )
            npc_dialog_behavior = NpcDialogBehavior(
                event_manager=event_manager, game_state=game_state, logger=logger
            )
            astar_allow_havre_sac = AstarAllowHavreSac(game_state=game_state)
            waypoint_behavior = WaypointBehavior(
                event_manager=event_manager,
                interactive_behavior=interactive_behavior,
                game_state=game_state,
                auto_trip_behavior=auto_trip_behavior,
                astar_allow_havre_sac=astar_allow_havre_sac,
                logger=logger,
            )
            auto_trip_zaap_behavior = AutoTripZaapBehavior(
                auto_trip_behavior=auto_trip_behavior,
                event_manager=event_manager,
                game_state=game_state,
                waypoint_behavior=waypoint_behavior,
                logger=logger,
            )
            auto_trip_explorator_behavior = AutoTripExploratorBehavior(
                event_manager=event_manager,
                game_state=game_state,
                auto_trip_zaap_behavior=auto_trip_zaap_behavior,
                logger=logger,
            )
            auto_trip_world_behavior = AutoTripSmartBehavior(
                event_manager=event_manager,
                game_state=game_state,
                npc_dialog_behavior=npc_dialog_behavior,
                auto_trip_explorator_behavior=auto_trip_explorator_behavior,
                logger=logger,
            )
            astar_no_interactive = AstarNoInteractive(game_state=game_state)
            fight_movement_behavior = FightMovementBehavior(
                map_move_behavior=map_move_behavior,
                game_state=game_state,
                event_manager=event_manager,
                path_finding=path_finding,
                logger=logger,
                fight_reachable_cells=fight_reachable_cells,
            )
            fight_challenge_behavior = FightChallengeBehavior(
                event_manager=event_manager, game_state=game_state, logger=logger
            )
            fight_placement_behavior = FightPreparationBehavior(
                game_state=game_state,
                event_manager=event_manager,
                fight_movement_behavior=fight_movement_behavior,
                fight_challenge_behavior=fight_challenge_behavior,
                logger=logger,
            )
            fight_spell_behavior = FightSpellBehavior(
                event_manager=event_manager, game_state=game_state, logger=logger
            )
            revive_behavior = ReviveBehavior(
                event_manager=event_manager,
                game_state=game_state,
                auto_trip_behavior=auto_trip_behavior,
                interactive_behavior=interactive_behavior,
                astar_no_interactive=astar_no_interactive,
                path_finding=path_finding,
                logger=logger,
            )

            fight_turn_behavior = FightTurnBehavior(
                logger=logger,
                fight_spell_behavior=fight_spell_behavior,
                event_manager=event_manager,
                fight_movement_behavior=fight_movement_behavior,
                path_finding=path_finding,
                game_state=game_state,
                attacker=attacker,
            )
            fight_behavior = FightBehavior(
                event_manager=event_manager,
                game_state=game_state,
                fight_preparation_behavior=fight_placement_behavior,
                path_finding=path_finding,
                revive_behavior=revive_behavior,
                logger=logger,
                fight_turn_behavior=fight_turn_behavior,
            )

            collect_behavior = CollectBehavior(
                event_manager=event_manager,
                interactive_behavior=interactive_behavior,
                game_state=game_state,
                path_finding=path_finding,
                data_map_provider=data_map_provider,
                logger=logger,
            )

            unload_in_guild_chest_behavior = UnloadInGuildChestBehavior(
                event_manager,
                game_state,
                logger,
                interactive_behavior,
                path_finding,
                auto_trip_world_behavior,
            )

            unload_in_bank_behavior = UnloadInBankBehavior(
                event_manager=event_manager,
                npc_dialog_behavior=npc_dialog_behavior,
                auto_trip_world_behavior=auto_trip_world_behavior,
                game_state=game_state,
                logger=logger,
            )

            unload_behavior = UnloadBehavior(
                event_manager,
                game_state,
                logger,
                unload_in_bank_behavior,
                unload_in_guild_chest_behavior,
            )

            weighted_path = WeightedPath(game_state=game_state)
            random_farm_behavior = RandomFarmBehavior(
                event_manager=event_manager,
                game_state=game_state,
                auto_trip_world_behavior=auto_trip_world_behavior,
                weighted_path=weighted_path,
                world_signals=world_signals,
                edge_behavior=edge_behavior,
                logger=logger,
            )

            # module
            harvester = HarvesterBehavior(
                auto_trip_smart_behavior=auto_trip_world_behavior,
                event_manager=event_manager,
                collect_behavior=collect_behavior,
                game_state=game_state,
                unload_behavior=unload_behavior,
                random_farm_behavior=random_farm_behavior,
                world_path_finder=world_path_finder,
                fight_behavior=fight_behavior,
                logger=logger,
            )
            fighter_behavior = FighterBehavior(
                event_manager=event_manager,
                fight_behavior=fight_behavior,
                map_move_behavior=map_move_behavior,
                path_finding=path_finding,
                random_farm_behavior=random_farm_behavior,
                game_state=game_state,
                unload_behavior=unload_behavior,
                logger=logger,
            )

            bot_by_account_id[account_id] = Bot(
                account=account,
                grid_signals=grid_signals,
                game_info_signals=game_info_signals,
                farm_action_signals=harvester_signals,
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
                    connection_frame,
                ],
                fighter_behavior=fighter_behavior,
                world_signals=world_signals,
                logger=logger,
                log_signals=log_signals,
            )
        return bot_by_account_id
