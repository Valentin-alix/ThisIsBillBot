import threading

from ankama_launcher_emulator_premium.interfaces.deciphered_api_key import (
    DecipheredApiKey,
)

from src.core.behaviors.communication.chat_behavior import ChatBehavior
from src.core.behaviors.craft.craft_behavior import CraftBehavior
from src.core.behaviors.farms.auto_bot_behavior import AutoBotBehavior
from src.core.behaviors.farms.fight.attacker_behavior import AttackerBehavior
from src.core.behaviors.farms.fight.fight_behavior import FightBehavior
from src.core.behaviors.farms.fight.fight_movement_behavior import FightMovementBehavior
from src.core.behaviors.farms.fight.fight_preparation_behavior import (
    FightPreparationBehavior,
)
from src.core.behaviors.farms.fight.fight_spell_behavior import FightSpellBehavior
from src.core.behaviors.farms.fight.fight_turn_behavior import FightTurnBehavior
from src.core.behaviors.farms.fighter_behavior import FighterBehavior
from src.core.behaviors.farms.harvester_behavior import HarvesterBehavior
from src.core.behaviors.farms.multi_farming_behavior import MultiFarmingBehavior
from src.core.behaviors.farms.random_farm_behavior import RandomFarmBehavior
from src.core.behaviors.idle_behavior import IdleBehavior
from src.core.behaviors.interactives.collect_behavior import CollectBehavior
from src.core.behaviors.interactives.fake_bad_interactive_behavior import (
    FakeBadInteractiveBehavior,
)
from src.core.behaviors.interactives.interactive_behavior import InteractiveBehavior
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
from src.core.behaviors.movements.fake_bad_movement_behavior import (
    FakeBadMovementBehavior,
)
from src.core.behaviors.movements.map_change_behavior import MapChangeBehavior
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior
from src.core.behaviors.movements.waypoint_behavior import WaypointBehavior
from src.core.behaviors.mule_storage.mule_accept_behavior import MuleAcceptBehavior
from src.core.behaviors.mule_storage.mule_give_behavior import MuleGiveBehavior
from src.core.behaviors.npcs.npc_dialog_behavior import NpcDialogBehavior
from src.core.behaviors.quests.dungeon_behavior import DungeonBehavior
from src.core.behaviors.sale_hotel.enter_sale_hotel_behavior import (
    EnterSaleHotelBehavior,
)
from src.core.behaviors.sale_hotel.enter_sale_hotel_sell_behavior import (
    EnterSaleHotelSellBehavior,
)
from src.core.behaviors.sale_hotel.sale_hotel_prices_behavior import (
    SaleHotelPricesBehavior,
)
from src.core.behaviors.sale_hotel.sale_hotel_scraping_behavior import (
    SaleHotelScrapingBehavior,
)
from src.core.behaviors.socket.connection_behavior import ConnectionBehavior
from src.core.behaviors.storage.enter_chests.enter_bank_chest_behavior import (
    EnterBankChestBehavior,
)
from src.core.behaviors.storage.enter_chests.enter_guild_chest_behavior import (
    EnterGuildChestBehavior,
)
from src.core.behaviors.storage.loads.load_from_bank_behavior import (
    LoadFromBankBehavior,
)
from src.core.behaviors.storage.loads.load_from_guild_chest_behavior import (
    LoadFromGuildChestBehavior,
)
from src.core.behaviors.storage.loads.load_recipe_behavior import LoadRecipeBehavior
from src.core.behaviors.storage.loads.load_recipe_from_bank_chest_behavior import (
    LoadRecipeFromBankChestBehavior,
)
from src.core.behaviors.storage.loads.load_recipe_from_guild_chest_behavior import (
    LoadRecipeFromGuildChestBehavior,
)
from src.core.behaviors.storage.unloads.unload_behavior import UnloadBehavior
from src.core.behaviors.storage.unloads.unload_in_bank_behavior import (
    UnloadInBankBehavior,
)
from src.core.behaviors.storage.unloads.unload_in_guild_chest_behavior import (
    UnloadInGuildChestBehavior,
)
from src.core.bot.bot import Bot
from src.core.engine.fights.attack import Attacker
from src.core.engine.fights.damage_calculator import DamageCalculator
from src.core.engine.fights.reachable_cells.fight_reachable_cells import (
    FightReachableCells,
)
from src.core.engine.movements.map.map_data_adapter import DataMapProvider
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.core.engine.movements.world.astar_allow_capability import AstarAllowHavreSac
from src.core.engine.movements.world.astar_vertice import AstarWorld
from src.core.engine.movements.world.world_path_finder import WorldPathFinder
from src.core.engine.weights.weighted_path import WeightedPath
from src.core.events_manager.event_manager import EventManager
from src.core.frames.chat_frame import ChatFrame
from src.core.frames.craft_frame import CraftFrame
from src.core.frames.entity_frame import EntityFrame
from src.core.frames.fight_frame import FightFrame
from src.core.frames.guild_chest_frame import GuildChestFrame
from src.core.frames.interactive_frame import InteractiveFrame
from src.core.frames.inventory_frame import InventoryFrame
from src.core.frames.map_frame import MapFrame
from src.core.frames.player_frame import PlayerFrame
from src.core.frames.sale_hotel_frame import SaleHotelFrame
from src.core.frames.server_frame import ServerFrame
from src.core.signals.bot_signals import BotSignals
from src.core.signals.grid_signals import GridSignals
from src.core.signals.log_signals import LogSignals
from src.core.signals.message_signals import MessageInfoSignals
from src.core.signals.player_signals import GameInfoSignals, InventorySignals
from src.core.signals.shared_farm_signals import SharedSignals
from src.core.signals.world_signals import WorldSignals
from src.core.states.state_factory import StateFactory
from src.services.logging.logger import Logger


class BotFactory:
    @staticmethod
    def create_bot(
        shared_signals: SharedSignals, account: DecipheredApiKey, is_fake: bool = False
    ):
        harvester_signals = BotSignals()
        game_info_signals = GameInfoSignals()
        msg_info_signals = MessageInfoSignals()
        grid_signals = GridSignals()
        inventory_signals = InventorySignals()
        world_signals = WorldSignals()
        log_signals = LogSignals()

        is_playing_event = threading.Event()
        is_connected_event = threading.Event()
        is_ready_to_play_event = threading.Event()

        logger = Logger(title=account["apikey"]["login"], log_signals=log_signals)

        event_manager = EventManager(_logger=logger)

        # state
        game_state = StateFactory.create_game_state(
            inventory_signals=inventory_signals,
            game_info_signals=game_info_signals,
            grid_signals=grid_signals,
            logger=logger,
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
            _logger=logger,
            game_info_signals=game_info_signals,
            inventory_signals=inventory_signals,
            is_playing_event=is_playing_event,
        )
        chat_frame = ChatFrame(
            event_manager=event_manager,
            game_state=game_state,
            game_info_signals=game_info_signals,
            inventory_signals=inventory_signals,
            _logger=logger,
            is_playing_event=is_playing_event,
        )
        interactive_frame = InteractiveFrame(
            event_manager=event_manager,
            inventory_signals=inventory_signals,
            game_state=game_state,
            _logger=logger,
            game_info_signals=game_info_signals,
            is_playing_event=is_playing_event,
        )
        inventory_frame = InventoryFrame(
            event_manager=event_manager,
            game_state=game_state,
            _logger=logger,
            game_info_signals=game_info_signals,
            inventory_signals=inventory_signals,
            is_playing_event=is_playing_event,
        )
        map_frame = MapFrame(
            event_manager=event_manager,
            game_state=game_state,
            world_signals=world_signals,
            inventory_signals=inventory_signals,
            _logger=logger,
            game_info_signals=game_info_signals,
            is_playing_event=is_playing_event,
        )
        player_frame = PlayerFrame(
            event_manager=event_manager,
            game_info_signals=game_info_signals,
            inventory_signals=inventory_signals,
            game_state=game_state,
            _logger=logger,
            is_playing_event=is_playing_event,
        )
        fight_frame = FightFrame(
            event_manager=event_manager,
            game_state=game_state,
            inventory_signals=inventory_signals,
            _logger=logger,
            game_info_signals=game_info_signals,
            is_playing_event=is_playing_event,
        )
        server_frame = ServerFrame(
            event_manager=event_manager,
            game_state=game_state,
            game_info_signals=game_info_signals,
            inventory_signals=inventory_signals,
            _logger=logger,
            is_playing_event=is_playing_event,
        )
        guild_chest_frame = GuildChestFrame(
            _logger=logger,
            event_manager=event_manager,
            inventory_signals=inventory_signals,
            game_state=game_state,
            game_info_signals=game_info_signals,
            is_playing_event=is_playing_event,
        )
        sale_hotel_frame = SaleHotelFrame(
            game_info_signals=game_info_signals,
            inventory_signals=inventory_signals,
            game_state=game_state,
            event_manager=event_manager,
            _logger=logger,
            is_playing_event=is_playing_event,
        )
        craft_frame = CraftFrame(
            event_manager=event_manager,
            game_state=game_state,
            game_info_signals=game_info_signals,
            inventory_signals=inventory_signals,
            _logger=logger,
            is_playing_event=is_playing_event,
        )
        # behavior
        map_change_behavior = MapChangeBehavior(
            event_manager=event_manager,
            game_state=game_state,
            _logger=logger,
        )
        map_move_behavior = MapMoveBehavior(
            event_manager=event_manager,
            game_state=game_state,
            path_finding=path_finding,
            _logger=logger,
        )
        interactive_behavior = InteractiveBehavior(
            game_state=game_state,
            event_manager=event_manager,
            map_move_behavior=map_move_behavior,
            _logger=logger,
            path_finding=path_finding,
        )
        fight_movement_behavior = FightMovementBehavior(
            map_move_behavior=map_move_behavior,
            game_state=game_state,
            event_manager=event_manager,
            path_finding=path_finding,
            _logger=logger,
            fight_reachable_cells=fight_reachable_cells,
        )
        fight_placement_behavior = FightPreparationBehavior(
            game_state=game_state,
            event_manager=event_manager,
            fight_movement_behavior=fight_movement_behavior,
            _logger=logger,
        )
        fight_spell_behavior = FightSpellBehavior(
            event_manager=event_manager,
            game_state=game_state,
            _logger=logger,
        )

        fight_turn_behavior = FightTurnBehavior(
            _logger=logger,
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
            _logger=logger,
            fight_turn_behavior=fight_turn_behavior,
            login=account["apikey"]["login"],
            shared_signals=shared_signals,
        )
        edge_behavior = EdgeBehavior(
            event_manager=event_manager,
            interactive_behavior=interactive_behavior,
            game_state=game_state,
            map_change_behavior=map_change_behavior,
            map_move_behavior=map_move_behavior,
            path_finding=path_finding,
            _logger=logger,
            fight_behavior=fight_behavior,
        )
        auto_trip_behavior = AutoTripBehavior(
            event_manager=event_manager,
            world_path_finder=world_path_finder,
            game_state=game_state,
            world_signals=world_signals,
            edge_behavior=edge_behavior,
            _logger=logger,
        )
        npc_dialog_behavior = NpcDialogBehavior(
            event_manager=event_manager,
            game_state=game_state,
            _logger=logger,
        )
        astar_allow_havre_sac = AstarAllowHavreSac(game_state=game_state)
        waypoint_behavior = WaypointBehavior(
            event_manager=event_manager,
            interactive_behavior=interactive_behavior,
            game_state=game_state,
            auto_trip_behavior=auto_trip_behavior,
            astar_allow_havre_sac=astar_allow_havre_sac,
            _logger=logger,
            pathfinding=path_finding,
        )
        auto_trip_zaap_behavior = AutoTripZaapBehavior(
            auto_trip_behavior=auto_trip_behavior,
            event_manager=event_manager,
            game_state=game_state,
            waypoint_behavior=waypoint_behavior,
            _logger=logger,
        )
        auto_trip_explorator_behavior = AutoTripExploratorBehavior(
            event_manager=event_manager,
            game_state=game_state,
            auto_trip_zaap_behavior=auto_trip_zaap_behavior,
            _logger=logger,
        )
        auto_trip_world_behavior = AutoTripSmartBehavior(
            event_manager=event_manager,
            game_state=game_state,
            npc_dialog_behavior=npc_dialog_behavior,
            auto_trip_explorator_behavior=auto_trip_explorator_behavior,
            _logger=logger,
        )
        collect_behavior = CollectBehavior(
            event_manager=event_manager,
            interactive_behavior=interactive_behavior,
            game_state=game_state,
            path_finding=path_finding,
            _logger=logger,
        )
        enter_guild_chest_behavior = EnterGuildChestBehavior(
            interactive_behavior=interactive_behavior,
            _logger=logger,
            event_manager=event_manager,
            auto_trip_world_behavior=auto_trip_world_behavior,
            path_finding=path_finding,
            game_state=game_state,
        )
        unload_in_guild_chest_behavior = UnloadInGuildChestBehavior(
            event_manager=event_manager,
            game_state=game_state,
            _logger=logger,
            interactive_behavior=interactive_behavior,
            path_finding=path_finding,
            auto_trip_world_behavior=auto_trip_world_behavior,
            enter_guild_chest_behavior=enter_guild_chest_behavior,
        )

        enter_bank_chest_behavior = EnterBankChestBehavior(
            game_state=game_state,
            auto_trip_world_behavior=auto_trip_world_behavior,
            _logger=logger,
            event_manager=event_manager,
            npc_dialog_behavior=npc_dialog_behavior,
        )

        unload_in_bank_behavior = UnloadInBankBehavior(
            event_manager=event_manager,
            auto_trip_world_behavior=auto_trip_world_behavior,
            game_state=game_state,
            _logger=logger,
            enter_bank_chest_behavior=enter_bank_chest_behavior,
        )
        enter_sale_hotel_behavior = EnterSaleHotelBehavior(
            event_manager=event_manager,
            game_state=game_state,
            _logger=logger,
            auto_trip_smart_behavior=auto_trip_world_behavior,
            interactive_behavior=interactive_behavior,
        )
        enter_sale_hotel_sell_behavior = EnterSaleHotelSellBehavior(
            _logger=logger,
            game_state=game_state,
            event_manager=event_manager,
            enter_sale_hotel_behavior=enter_sale_hotel_behavior,
        )

        unload_behavior = UnloadBehavior(
            event_manager=event_manager,
            game_state=game_state,
            _logger=logger,
            unload_in_bank_behavior=unload_in_bank_behavior,
            unload_in_guild_chest_behavior=unload_in_guild_chest_behavior,
        )
        load_recipe_from_guild_chest_behavior = LoadRecipeFromGuildChestBehavior(
            _logger=logger,
            game_state=game_state,
            unload_behavior=unload_behavior,
            event_manager=event_manager,
            enter_guild_chest_behavior=enter_guild_chest_behavior,
        )
        load_from_guild_chest_behavior = LoadFromGuildChestBehavior(
            event_manager=event_manager,
            _logger=logger,
            unload_behavior=unload_behavior,
            game_state=game_state,
            enter_guild_chest_behavior=enter_guild_chest_behavior,
        )
        load_from_bank_behavior = LoadFromBankBehavior(
            event_manager=event_manager,
            _logger=logger,
            unload_behavior=unload_behavior,
            game_state=game_state,
            enter_bank_behavior=enter_bank_chest_behavior,
        )
        sale_hotel_prices_behavior = SaleHotelPricesBehavior(
            event_manager=event_manager,
            game_state=game_state,
            _logger=logger,
            load_from_bank_behavior=load_from_bank_behavior,
            enter_sale_hotel_sell_behavior=enter_sale_hotel_sell_behavior,
            load_from_guild_chest_behavior=load_from_guild_chest_behavior,
        )

        weighted_path = WeightedPath(game_state=game_state)
        random_farm_behavior = RandomFarmBehavior(
            event_manager=event_manager,
            game_state=game_state,
            auto_trip_smart_behavior=auto_trip_world_behavior,
            weighted_path=weighted_path,
            world_signals=world_signals,
            edge_behavior=edge_behavior,
            _logger=logger,
        )
        mule_give_behavior = MuleGiveBehavior(
            event_manager=event_manager,
            game_state=game_state,
            _logger=logger,
            auto_trip_smart_behavior=auto_trip_world_behavior,
        )

        # module
        load_recipe_from_bank_chest_behavior = LoadRecipeFromBankChestBehavior(
            event_manager=event_manager,
            game_state=game_state,
            _logger=logger,
            enter_bank_chest_behavior=enter_bank_chest_behavior,
            unload_behavior=unload_behavior,
        )
        load_recipe_behavior = LoadRecipeBehavior(
            event_manager=event_manager,
            game_state=game_state,
            _logger=logger,
            load_recipe_from_bank_chest_behavior=load_recipe_from_bank_chest_behavior,
            load_recipe_from_guild_chest_behavior=load_recipe_from_guild_chest_behavior,
        )
        craft_behavior = CraftBehavior(
            event_manager=event_manager,
            game_state=game_state,
            _logger=logger,
            load_recipe_behavior=load_recipe_behavior,
            interactive_behavior=interactive_behavior,
            auto_trip_smart_behavior=auto_trip_world_behavior,
            pathfinding=path_finding,
        )
        harvester = HarvesterBehavior(
            mule_give_behavior=mule_give_behavior,
            event_manager=event_manager,
            collect_behavior=collect_behavior,
            game_state=game_state,
            unload_behavior=unload_behavior,
            random_farm_behavior=random_farm_behavior,
            fight_behavior=fight_behavior,
            _logger=logger,
            craft_behavior=craft_behavior,
            sale_hotel_prices_behavior=sale_hotel_prices_behavior,
        )
        attacker_behavior = AttackerBehavior(
            event_manager=event_manager,
            fight_behavior=fight_behavior,
            map_move_behavior=map_move_behavior,
            path_finding=path_finding,
            game_state=game_state,
            _logger=logger,
            bot_signals=harvester_signals,
            game_info_signals=game_info_signals,
        )
        fighter_behavior = FighterBehavior(
            event_manager=event_manager,
            attacker_behavior=attacker_behavior,
            map_move_behavior=map_move_behavior,
            path_finding=path_finding,
            random_farm_behavior=random_farm_behavior,
            game_state=game_state,
            unload_behavior=unload_behavior,
            _logger=logger,
            craft_behavior=craft_behavior,
            sale_hotel_prices_behavior=sale_hotel_prices_behavior,
            mule_give_behavior=mule_give_behavior,
        )

        chat_behavior = ChatBehavior(
            event_manager=event_manager, game_state=game_state, _logger=logger
        )
        fake_bad_movement_behavior = FakeBadMovementBehavior(
            event_manager=event_manager, game_state=game_state, _logger=logger
        )
        sale_hotel_scraping_behavior = SaleHotelScrapingBehavior(
            event_manager=event_manager,
            enter_sale_hotel_behavior=enter_sale_hotel_behavior,
            game_state=game_state,
            _logger=logger,
        )
        mule_accept_kamas_behavior = MuleAcceptBehavior(
            event_manager=event_manager,
            game_state=game_state,
            _logger=logger,
            auto_trip_smart_behavior=auto_trip_world_behavior,
            unload_behavior=unload_behavior,
            sale_hotel_prices_behavior=sale_hotel_prices_behavior,
            sale_hotel_scraping_behavior=sale_hotel_scraping_behavior,
        )
        dungeon_behavior = DungeonBehavior(
            event_manager=event_manager,
            game_state=game_state,
            _logger=logger,
            npc_dialog_behavior=npc_dialog_behavior,
            attacker_behavior=attacker_behavior,
            auto_trip_smart_behavior=auto_trip_world_behavior,
        )
        idle_behavior = IdleBehavior(
            event_manager=event_manager,
            game_state=game_state,
            _logger=logger,
        )
        connection_behavior = ConnectionBehavior(
            _logger=logger, event_manager=event_manager, game_state=game_state
        )
        multi_farming_behavior = MultiFarmingBehavior(
            chat_behavior=chat_behavior,
            mule_give_behavior=mule_give_behavior,
            event_manager=event_manager,
            collect_behavior=collect_behavior,
            game_state=game_state,
            unload_behavior=unload_behavior,
            random_farm_behavior=random_farm_behavior,
            fight_behavior=fight_behavior,
            _logger=logger,
            sale_hotel_prices_behavior=sale_hotel_prices_behavior,
            attacker_behavior=attacker_behavior,
            craft_behavior=craft_behavior,
            dungeon_behavior=dungeon_behavior,
            idle_behavior=idle_behavior,
        )
        auto_bot_behavior = AutoBotBehavior(
            event_manager=event_manager,
            game_state=game_state,
            _logger=logger,
            fighter_behavior=fighter_behavior,
            harvester_behavior=harvester,
            multi_farming_behavior=multi_farming_behavior,
        )

        fake_bad_interactive_behavior = FakeBadInteractiveBehavior(
            _logger=logger, event_manager=event_manager, game_state=game_state
        )

        return Bot(
            usable_behaviors=[
                mule_give_behavior,
                mule_accept_kamas_behavior,
                dungeon_behavior,
                sale_hotel_prices_behavior,
                sale_hotel_scraping_behavior,
                fake_bad_movement_behavior,
                fake_bad_interactive_behavior,
            ],
            account=account,
            grid_signals=grid_signals,
            game_info_signals=game_info_signals,
            bot_signals=harvester_signals,
            msg_info_signals=msg_info_signals,
            inventory_signals=inventory_signals,
            event_manager=event_manager,
            harvester_behavior=harvester,
            fight_behavior=fight_behavior,
            connection_behavior=connection_behavior,
            mule_accept_kamas_behavior=mule_accept_kamas_behavior,
            dungeon_behavior=dungeon_behavior,
            frames=[
                map_frame,
                player_frame,
                entity_frame,
                inventory_frame,
                interactive_frame,
                chat_frame,
                fight_frame,
                server_frame,
                guild_chest_frame,
                sale_hotel_frame,
                craft_frame,
            ],
            world_signals=world_signals,
            _logger=logger,
            log_signals=log_signals,
            game_state=game_state,
            fighter_behavior=fighter_behavior,
            craft_behavior=craft_behavior,
            auto_bot_behavior=auto_bot_behavior,
            is_playing_event=is_playing_event,
            shared_signals=shared_signals,
            is_ready_to_play_event=is_ready_to_play_event,
            is_connected_event=is_connected_event,
            is_fake=is_fake,
        )
