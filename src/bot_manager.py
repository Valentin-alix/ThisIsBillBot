import threading
from dataclasses import dataclass, field
from functools import partial

from ankama_launcher_emulator import AnkamaLauncherHandler, AnkamaLauncherServer
from ankama_launcher_emulator.decrypter.crypto_helper import CryptoHelper
from ankama_launcher_emulator.interfaces.deciphered_api_key import DecipheredApiKey

from src.bot import Bot
from src.common.logger import Logger
from src.core.behaviors.craft.craft_behavior import CraftBehavior
from src.core.behaviors.farms.fighter.fighter_behavior import FighterBehavior
from src.core.behaviors.farms.fighter.mule_fighter_behavior import MuleFighterBehavior
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
from src.core.frames.objective_frame import ObjectiveFrame
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
from src.interfaces.models.barrier import SubjectBarrier
from src.signals.bot_signals import BotSignals
from src.signals.grid_signals import GridSignals
from src.signals.internal_subjects import InternalSubjects
from src.signals.log_signals import LogSignals
from src.signals.message_signals import MessageInfoSignals
from src.signals.player_signals import GameInfoSignals
from src.signals.shared_farm_signals import SharedFarmSignals
from src.signals.shared_subjects import SharedSubjects
from src.signals.world_signals import WorldSignals


@dataclass
class BotManager:
    shared_farm_signals: SharedFarmSignals
    ankama_launcher_handler: AnkamaLauncherHandler = field(
        init=False, default_factory=AnkamaLauncherHandler
    )
    account_by_id: dict[int, DecipheredApiKey] = field(
        default_factory=lambda: {}, init=False
    )

    def __post_init__(self):
        self.ankama_launcher = AnkamaLauncherServer(self.ankama_launcher_handler)
        self.bot_by_account_id = self.get_bot_by_account_id(self.get_accounts())
        self.shared_farm_signals.play_fighter.connect(self.on_play_fighter)

    def on_play_fighter(
        self,
        account_id: int,
        area_id: int | None,
        sub_area_id: int | None,
        mule_bots: list["Bot"] | None,
    ):
        bot = self.bot_by_account_id[account_id]
        bot.stop_main_behavior()
        bot.bot_signals.play.emit()
        if mule_bots is None:
            mule_bots = [
                other_bot
                for other_account_id, other_bot in self.bot_by_account_id.items()
                if other_bot.game_state.player.is_connected
                and other_account_id != account_id
                and other_bot.game_state.player.server_id
                == bot.game_state.player.server_id
                and not (
                    other_bot.harvester_behavior.is_running.is_set()
                    or other_bot.fighter_behavior.is_running.is_set()
                    or other_bot.mule_fighter_behavior.is_running.is_set()
                )
            ]
        bot.fighter_behavior.ready_barrier.set_target(len(mule_bots) + 1)
        bot.logger.info(f"Starting fighter with {len(mule_bots)} mules")

        self.safe_stop_bots(mule_bots)

        for mule in mule_bots:
            mule.bot_signals.play.emit()
            mule.mule_fighter_behavior.start(
                callback=partial(
                    self.on_mule_fighter_behavior_finished,
                    mule=mule,
                    leader_account_id=account_id,
                ),
                parent=None,
                leader_id=bot.game_state.player.character_id,
                ready_barrier=bot.fighter_behavior.ready_barrier,
            )

        bot.logger.info("Mules are ready, starting leader fighter")
        bot.fighter_behavior.start(
            callback=partial(
                self.on_leader_fighter_behavior_finished,
                mule_bots=mule_bots,
            ),
            parent=None,
            area_id=area_id,
            sub_area_id=sub_area_id,
            mule_states=[mule_bot.game_state for mule_bot in mule_bots],
        )

    def on_leader_fighter_behavior_finished(
        self, error_code: str | None, mule_bots: list[Bot]
    ):
        for bot in mule_bots:
            bot.bot_signals.stop.emit()
            bot.stop_main_behavior()

    def on_mule_fighter_behavior_finished(
        self, error_code: str | None, mule: Bot, leader_account_id: int
    ):
        mule.bot_signals.stop.emit()
        leader_bot = self.bot_by_account_id[leader_account_id]
        leader_bot.fighter_behavior.mule_states = [
            mule_state
            for mule_state in leader_bot.fighter_behavior.mule_states
            if mule_state.player.character_id != mule.game_state.player.character_id
        ]
        leader_bot.fighter_behavior.ready_barrier.set_target(
            len(leader_bot.fighter_behavior.mule_states) + 1
        )

    def safe_stop_bots(self, bots: list[Bot]):
        threads = [threading.Thread(target=bot.safe_stop, daemon=True) for bot in bots]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

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
        ready_barrier = SubjectBarrier()
        shared_subject = SharedSubjects()

        for account_id, account in account_by_id.items():
            # signal
            harvester_signals = BotSignals()
            game_info_signals = GameInfoSignals()
            msg_info_signals = MessageInfoSignals()
            grid_signals = GridSignals()
            world_signals = WorldSignals()
            log_signals = LogSignals()
            internal_subjects = InternalSubjects()

            is_playing_event = threading.Event()

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
            quest_frame = ObjectiveFrame(
                event_manager=event_manager,
                game_state=game_state,
                logger=logger,
                game_info_signals=game_info_signals,
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
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
            )
            map_move_behavior = MapMoveBehavior(
                event_manager=event_manager,
                game_state=game_state,
                path_finding=path_finding,
                logger=logger,
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
            )
            interactive_behavior = InteractiveBehavior(
                game_state=game_state,
                event_manager=event_manager,
                map_move_behavior=map_move_behavior,
                logger=logger,
                path_finding=path_finding,
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
            )
            edge_behavior = EdgeBehavior(
                event_manager=event_manager,
                interactive_behavior=interactive_behavior,
                game_state=game_state,
                map_change_behavior=map_change_behavior,
                map_move_behavior=map_move_behavior,
                path_finding=path_finding,
                logger=logger,
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
            )
            auto_trip_behavior = AutoTripBehavior(
                event_manager=event_manager,
                world_path_finder=world_path_finder,
                game_state=game_state,
                world_signals=world_signals,
                edge_behavior=edge_behavior,
                logger=logger,
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
            )
            npc_dialog_behavior = NpcDialogBehavior(
                event_manager=event_manager,
                game_state=game_state,
                logger=logger,
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
            )
            astar_allow_havre_sac = AstarAllowHavreSac(game_state=game_state)
            waypoint_behavior = WaypointBehavior(
                event_manager=event_manager,
                interactive_behavior=interactive_behavior,
                game_state=game_state,
                auto_trip_behavior=auto_trip_behavior,
                astar_allow_havre_sac=astar_allow_havre_sac,
                logger=logger,
                shared_subjects=shared_subject,
                pathfinding=path_finding,
                internal_subjects=internal_subjects,
            )
            auto_trip_zaap_behavior = AutoTripZaapBehavior(
                auto_trip_behavior=auto_trip_behavior,
                event_manager=event_manager,
                game_state=game_state,
                waypoint_behavior=waypoint_behavior,
                logger=logger,
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
            )
            auto_trip_explorator_behavior = AutoTripExploratorBehavior(
                event_manager=event_manager,
                game_state=game_state,
                auto_trip_zaap_behavior=auto_trip_zaap_behavior,
                logger=logger,
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
            )
            auto_trip_world_behavior = AutoTripSmartBehavior(
                event_manager=event_manager,
                game_state=game_state,
                npc_dialog_behavior=npc_dialog_behavior,
                auto_trip_explorator_behavior=auto_trip_explorator_behavior,
                logger=logger,
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
            )
            astar_no_interactive = AstarNoInteractive(game_state=game_state)
            fight_movement_behavior = FightMovementBehavior(
                map_move_behavior=map_move_behavior,
                game_state=game_state,
                event_manager=event_manager,
                path_finding=path_finding,
                logger=logger,
                fight_reachable_cells=fight_reachable_cells,
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
            )
            fight_challenge_behavior = FightChallengeBehavior(
                event_manager=event_manager,
                game_state=game_state,
                logger=logger,
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
            )
            fight_placement_behavior = FightPreparationBehavior(
                game_state=game_state,
                event_manager=event_manager,
                fight_movement_behavior=fight_movement_behavior,
                fight_challenge_behavior=fight_challenge_behavior,
                logger=logger,
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
            )
            fight_spell_behavior = FightSpellBehavior(
                event_manager=event_manager,
                game_state=game_state,
                logger=logger,
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
            )
            revive_behavior = ReviveBehavior(
                event_manager=event_manager,
                game_state=game_state,
                auto_trip_behavior=auto_trip_behavior,
                interactive_behavior=interactive_behavior,
                astar_no_interactive=astar_no_interactive,
                path_finding=path_finding,
                logger=logger,
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
            )

            fight_turn_behavior = FightTurnBehavior(
                logger=logger,
                fight_spell_behavior=fight_spell_behavior,
                event_manager=event_manager,
                fight_movement_behavior=fight_movement_behavior,
                path_finding=path_finding,
                game_state=game_state,
                attacker=attacker,
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
            )
            fight_behavior = FightBehavior(
                event_manager=event_manager,
                game_state=game_state,
                fight_preparation_behavior=fight_placement_behavior,
                path_finding=path_finding,
                revive_behavior=revive_behavior,
                logger=logger,
                fight_turn_behavior=fight_turn_behavior,
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
            )

            collect_behavior = CollectBehavior(
                event_manager=event_manager,
                interactive_behavior=interactive_behavior,
                game_state=game_state,
                path_finding=path_finding,
                logger=logger,
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
            )
            enter_guild_chest_behavior = EnterGuildChestBehavior(
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
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
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
                enter_guild_chest_behavior=enter_guild_chest_behavior,
            )

            enter_bank_chest_behavior = EnterBankChestBehavior(
                game_state=game_state,
                auto_trip_world_behavior=auto_trip_world_behavior,
                logger=logger,
                internal_subjects=internal_subjects,
                shared_subjects=shared_subject,
                event_manager=event_manager,
                npc_dialog_behavior=npc_dialog_behavior,
            )

            unload_in_bank_behavior = UnloadInBankBehavior(
                event_manager=event_manager,
                npc_dialog_behavior=npc_dialog_behavior,
                auto_trip_world_behavior=auto_trip_world_behavior,
                game_state=game_state,
                logger=logger,
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
                enter_bank_chest_behavior=enter_bank_chest_behavior,
            )
            enter_sale_hotel_sell_behavior = EnterSaleHotelSellBehavior(
                interactive_behavior=interactive_behavior,
                auto_trip_smart_behavior=auto_trip_world_behavior,
                logger=logger,
                game_state=game_state,
                internal_subjects=internal_subjects,
                shared_subjects=shared_subject,
                event_manager=event_manager,
            )

            unload_behavior = UnloadBehavior(
                event_manager=event_manager,
                game_state=game_state,
                logger=logger,
                unload_in_bank_behavior=unload_in_bank_behavior,
                unload_in_guild_chest_behavior=unload_in_guild_chest_behavior,
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
            )
            load_recipe_from_guild_chest_behavior = LoadRecipeFromGuildChestBehavior(
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
                logger=logger,
                game_state=game_state,
                unload_behavior=unload_behavior,
                event_manager=event_manager,
                enter_guild_chest_behavior=enter_guild_chest_behavior,
            )
            load_from_guild_chest_behavior = LoadFromGuildChestBehavior(
                event_manager=event_manager,
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
                logger=logger,
                unload_behavior=unload_behavior,
                game_state=game_state,
                enter_guild_chest_behavior=enter_guild_chest_behavior,
            )
            sale_hotel_prices_behavior = SaleHotelPricesBehavior(
                event_manager=event_manager,
                game_state=game_state,
                logger=logger,
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
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
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
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
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
                sale_hotel_prices_behavior=sale_hotel_prices_behavior,
            )
            mule_fighter_behavior = MuleFighterBehavior(
                game_state=game_state,
                logger=logger,
                event_manager=event_manager,
                auto_trip_smart_behavior=auto_trip_world_behavior,
                fight_behavior=fight_behavior,
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
                unload_behavior=unload_behavior,
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
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
                ready_barrier=ready_barrier,
            )
            craft_behavior = CraftBehavior(
                event_manager=event_manager,
                game_state=game_state,
                logger=logger,
                shared_subjects=shared_subject,
                internal_subjects=internal_subjects,
                load_recipe_from_guild_chest_behavior=load_recipe_from_guild_chest_behavior,
                interactive_behavior=interactive_behavior,
                auto_trip_smart_behavior=auto_trip_world_behavior,
                pathfinding=path_finding,
            )

            bot_by_account_id[account_id] = Bot(
                account=account,
                grid_signals=grid_signals,
                game_info_signals=game_info_signals,
                bot_signals=harvester_signals,
                msg_info_signals=msg_info_signals,
                event_manager=event_manager,
                harvester_behavior=harvester,
                fight_behavior=fight_behavior,
                frames=[
                    quest_frame,
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
                mule_fighter_behavior=mule_fighter_behavior,
                craft_behavior=craft_behavior,
                is_playing_event=is_playing_event,
            )
        return bot_by_account_id
