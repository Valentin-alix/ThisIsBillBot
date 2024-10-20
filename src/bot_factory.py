import threading

from ankama_launcher_emulator.interfaces.deciphered_api_key import DecipheredApiKey
from d3_mapping.signals.message_signals import MessageInfoSignals

from src.bot import Bot
from src.common.logger import Logger
from src.core.behaviors.craft.craft_behavior import CraftBehavior
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
from src.core.behaviors.mule_kamas.mule_accept_kamas_behavior import (
    MuleAcceptKamasBehavior,
)
from src.core.behaviors.mule_kamas.mule_give_kamas_behavior import MuleGiveKamasBehavior
from src.core.behaviors.npc_dialog_behavior import NpcDialogBehavior
from src.core.behaviors.sale_hotel.enter_sale_hotel_sell_behavior import (
    EnterSaleHotelSellBehavior,
)
from src.core.behaviors.sale_hotel.sale_hotel_prices_behavior import (
    SaleHotelPricesBehavior,
)
from src.core.behaviors.storage.enter_bank_chest_behavior import EnterBankChestBehavior
from src.core.behaviors.storage.enter_guild_chest_behavior import (
    EnterGuildChestBehavior,
)
from src.core.behaviors.storage.load_from_bank_behavior import LoadFromBankBehavior
from src.core.behaviors.storage.load_from_guild_chest_behavior import (
    LoadFromGuildChestBehavior,
)
from src.core.behaviors.storage.load_recipe_from_guild_chest_behavior import (
    LoadRecipeFromGuildChestBehavior,
)
from src.core.behaviors.storage.unload_behavior import UnloadBehavior
from src.core.behaviors.storage.unload_in_bank_behavior import UnloadInBankBehavior
from src.core.behaviors.storage.unload_in_guild_chest_behavior import (
    UnloadInGuildChestBehavior,
)
from src.core.frames.entity_frame import EntityFrame
from src.core.frames.fight_frame import FightFrame
from src.core.frames.guild_chest_frame import GuildChestFrame
from src.core.frames.interactive_frame import InteractiveFrame
from src.core.frames.inventory_frame import InventoryFrame
from src.core.frames.map_frame import MapFrame
from src.core.frames.player_frame import PlayerFrame
from src.core.frames.sale_hotel_frame import SaleHotelFrame
from src.core.frames.server_frame import ServerFrame
from src.core.logic.farmer.weighted_path import WeightedPath
from src.core.logic.fight.attack import Attacker
from src.core.logic.fight.damage_calculator import DamageCalculator
from src.core.logic.fight.reachable_cells.fight_reachable_cells import (
    FightReachableCells,
)
from src.core.logic.grid.data_map_provider import DataMapProvider
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.logic.world.astar_allow_capability import AstarAllowHavreSac
from src.core.logic.world.astar_no_interactive import AstarNoInteractive
from src.core.logic.world.astar_vertice import AstarWorld
from src.core.logic.world.world_path_finder import WorldPathFinder
from src.core.states.state_factory import StateFactory
from src.event_manager import EventManager
from src.signals.bot_signals import BotSignals
from src.signals.grid_signals import GridSignals
from src.signals.log_signals import LogSignals
from src.signals.player_signals import GameInfoSignals
from src.signals.shared_farm_signals import SharedSignals
from src.signals.world_signals import WorldSignals


class BotFactory:
    @staticmethod
    def create_bot(
        shared_signals: SharedSignals,
        account: DecipheredApiKey,
    ):
        harvester_signals = BotSignals()
        game_info_signals = GameInfoSignals()
        msg_info_signals = MessageInfoSignals()
        grid_signals = GridSignals()
        world_signals = WorldSignals()
        log_signals = LogSignals()

        is_playing_event = threading.Event()
        is_connected_event = threading.Event()
        is_ready_to_play_event = threading.Event()

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
        damage_calculator = DamageCalculator(game_state=game_state)
        attacker = Attacker(
            game_state=game_state,
            path_finding=path_finding,
            logger=logger,
            fight_reachable_cells=fight_reachable_cells,
            damage_calculator=damage_calculator,
        )

        # frames
        entity_frame = EntityFrame(
            event_manager=event_manager,
            game_state=game_state,
            logger=logger,
            game_info_signals=game_info_signals,
            is_playing_event=is_playing_event,
        )
        interactive_frame = InteractiveFrame(
            event_manager=event_manager,
            game_state=game_state,
            logger=logger,
            game_info_signals=game_info_signals,
            is_playing_event=is_playing_event,
        )
        inventory_frame = InventoryFrame(
            event_manager=event_manager,
            game_state=game_state,
            logger=logger,
            game_info_signals=game_info_signals,
            is_playing_event=is_playing_event,
        )
        map_frame = MapFrame(
            event_manager=event_manager,
            game_state=game_state,
            world_signals=world_signals,
            logger=logger,
            game_info_signals=game_info_signals,
            is_playing_event=is_playing_event,
        )
        player_frame = PlayerFrame(
            event_manager=event_manager,
            game_info_signals=game_info_signals,
            game_state=game_state,
            logger=logger,
            is_playing_event=is_playing_event,
        )
        fight_frame = FightFrame(
            event_manager=event_manager,
            game_state=game_state,
            logger=logger,
            game_info_signals=game_info_signals,
            is_playing_event=is_playing_event,
        )
        server_frame = ServerFrame(
            event_manager=event_manager,
            game_state=game_state,
            game_info_signals=game_info_signals,
            logger=logger,
            is_playing_event=is_playing_event,
        )
        guild_chest_frame = GuildChestFrame(
            logger=logger,
            event_manager=event_manager,
            game_state=game_state,
            game_info_signals=game_info_signals,
            is_playing_event=is_playing_event,
        )
        sale_hotel_frame = SaleHotelFrame(
            game_info_signals=game_info_signals,
            game_state=game_state,
            event_manager=event_manager,
            logger=logger,
            is_playing_event=is_playing_event,
        )

        # behavior
        map_change_behavior = MapChangeBehavior(
            event_manager=event_manager,
            game_state=game_state,
            logger=logger,
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
            path_finding=path_finding,
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
            event_manager=event_manager,
            game_state=game_state,
            logger=logger,
        )
        astar_allow_havre_sac = AstarAllowHavreSac(game_state=game_state)
        waypoint_behavior = WaypointBehavior(
            event_manager=event_manager,
            interactive_behavior=interactive_behavior,
            game_state=game_state,
            auto_trip_behavior=auto_trip_behavior,
            astar_allow_havre_sac=astar_allow_havre_sac,
            logger=logger,
            pathfinding=path_finding,
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
            event_manager=event_manager,
            game_state=game_state,
            logger=logger,
        )
        fight_placement_behavior = FightPreparationBehavior(
            game_state=game_state,
            event_manager=event_manager,
            fight_movement_behavior=fight_movement_behavior,
            fight_challenge_behavior=fight_challenge_behavior,
            logger=logger,
        )
        fight_spell_behavior = FightSpellBehavior(
            event_manager=event_manager,
            game_state=game_state,
            logger=logger,
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
            logger=logger,
        )
        enter_guild_chest_behavior = EnterGuildChestBehavior(
            interactive_behavior=interactive_behavior,
            logger=logger,
            event_manager=event_manager,
            auto_trip_world_behavior=auto_trip_world_behavior,
            path_finding=path_finding,
            game_state=game_state,
        )
        unload_in_guild_chest_behavior = UnloadInGuildChestBehavior(
            event_manager=event_manager,
            game_state=game_state,
            logger=logger,
            interactive_behavior=interactive_behavior,
            path_finding=path_finding,
            auto_trip_world_behavior=auto_trip_world_behavior,
            enter_guild_chest_behavior=enter_guild_chest_behavior,
        )

        enter_bank_chest_behavior = EnterBankChestBehavior(
            game_state=game_state,
            auto_trip_world_behavior=auto_trip_world_behavior,
            logger=logger,
            event_manager=event_manager,
            npc_dialog_behavior=npc_dialog_behavior,
        )

        unload_in_bank_behavior = UnloadInBankBehavior(
            event_manager=event_manager,
            npc_dialog_behavior=npc_dialog_behavior,
            auto_trip_world_behavior=auto_trip_world_behavior,
            game_state=game_state,
            logger=logger,
            enter_bank_chest_behavior=enter_bank_chest_behavior,
        )
        enter_sale_hotel_sell_behavior = EnterSaleHotelSellBehavior(
            interactive_behavior=interactive_behavior,
            auto_trip_smart_behavior=auto_trip_world_behavior,
            logger=logger,
            game_state=game_state,
            event_manager=event_manager,
        )

        unload_behavior = UnloadBehavior(
            event_manager=event_manager,
            game_state=game_state,
            logger=logger,
            unload_in_bank_behavior=unload_in_bank_behavior,
            unload_in_guild_chest_behavior=unload_in_guild_chest_behavior,
        )
        load_recipe_from_guild_chest_behavior = LoadRecipeFromGuildChestBehavior(
            logger=logger,
            game_state=game_state,
            unload_behavior=unload_behavior,
            event_manager=event_manager,
            enter_guild_chest_behavior=enter_guild_chest_behavior,
        )
        load_from_guild_chest_behavior = LoadFromGuildChestBehavior(
            event_manager=event_manager,
            logger=logger,
            unload_behavior=unload_behavior,
            game_state=game_state,
            enter_guild_chest_behavior=enter_guild_chest_behavior,
        )
        load_from_bank_behavior = LoadFromBankBehavior(
            event_manager=event_manager,
            logger=logger,
            unload_behavior=unload_behavior,
            game_state=game_state,
            enter_bank_behavior=enter_bank_chest_behavior,
        )
        sale_hotel_prices_behavior = SaleHotelPricesBehavior(
            event_manager=event_manager,
            game_state=game_state,
            logger=logger,
            load_from_bank_behavior=load_from_bank_behavior,
            enter_sale_hotel_sell_behavior=enter_sale_hotel_sell_behavior,
            load_from_guild_chest_behavior=load_from_guild_chest_behavior,
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
        mule_give_kamas_behavior = MuleGiveKamasBehavior(
            event_manager=event_manager,
            game_state=game_state,
            logger=logger,
            auto_trip_smart_behavior=auto_trip_world_behavior,
        )

        # module
        harvester = HarvesterBehavior(
            mule_give_kamas_behavior=mule_give_kamas_behavior,
            event_manager=event_manager,
            collect_behavior=collect_behavior,
            game_state=game_state,
            unload_behavior=unload_behavior,
            random_farm_behavior=random_farm_behavior,
            fight_behavior=fight_behavior,
            logger=logger,
            sale_hotel_prices_behavior=sale_hotel_prices_behavior,
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
            sale_hotel_prices_behavior=sale_hotel_prices_behavior,
        )
        craft_behavior = CraftBehavior(
            event_manager=event_manager,
            game_state=game_state,
            logger=logger,
            load_recipe_from_guild_chest_behavior=load_recipe_from_guild_chest_behavior,
            interactive_behavior=interactive_behavior,
            auto_trip_smart_behavior=auto_trip_world_behavior,
            pathfinding=path_finding,
        )
        mule_accept_kamas_behavior = MuleAcceptKamasBehavior(
            event_manager=event_manager,
            game_state=game_state,
            logger=logger,
            auto_trip_smart_behavior=auto_trip_world_behavior,
        )

        return Bot(
            pid=None,
            account=account,
            grid_signals=grid_signals,
            game_info_signals=game_info_signals,
            bot_signals=harvester_signals,
            msg_info_signals=msg_info_signals,
            event_manager=event_manager,
            harvester_behavior=harvester,
            fight_behavior=fight_behavior,
            mule_accept_kamas_behavior=mule_accept_kamas_behavior,
            frames=[
                map_frame,
                player_frame,
                entity_frame,
                inventory_frame,
                interactive_frame,
                fight_frame,
                server_frame,
                guild_chest_frame,
                sale_hotel_frame,
            ],
            world_signals=world_signals,
            logger=logger,
            log_signals=log_signals,
            game_state=game_state,
            fighter_behavior=fighter_behavior,
            craft_behavior=craft_behavior,
            is_playing_event=is_playing_event,
            shared_signals=shared_signals,
            is_ready_to_play_event=is_ready_to_play_event,
            is_connected_event=is_connected_event,
        )
