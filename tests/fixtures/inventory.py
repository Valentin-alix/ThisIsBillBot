from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import ObjectItem, ObjectItemInventory

from src.core.bot.bot_factory import BotFactory
from src.core.engine.contexts import CriterionContext
from src.core.signals.shared_farm_signals import SharedSignals
from src.core.states.game_state import GameState
from tests.fixtures.accounts import make_account


def make_inventory_item(gid: int, quantity: int, uid: int = 0) -> ObjectItemInventory:
    return ObjectItemInventory(item=ObjectItem(uid=uid, gid=gid, quantity=quantity))


def make_game_state_with_inventory(item_quantity_by_gid: dict[int, int]) -> GameState:
    game_state = BotFactory.create_bot(
        SharedSignals(),
        account=make_account("TestBot", 1),
        is_fake=True,
    ).game_state
    objects = [
        make_inventory_item(gid=gid, quantity=quantity, uid=uid)
        for uid, (gid, quantity) in enumerate(item_quantity_by_gid.items(), start=1)
    ]
    game_state.inventory.set_objects(objects)
    return game_state


def make_criterion_context_with_inventory(
    item_quantity_by_gid: dict[int, int],
) -> CriterionContext:
    game_state = make_game_state_with_inventory(item_quantity_by_gid)
    return CriterionContext(
        is_sub=game_state.player.is_sub,
        player_level=game_state.player.level,
        player_limited_level=game_state.player.limited_lvl,
        player_subscription_end_date=game_state.player.subscription_end_date,
        player_jobs_lvl_by_id=game_state.player.jobs_lvl_by_id,
        player_waypoint_map_ids=frozenset(game_state.player.waypoint_map_ids),
        player_server_id=game_state.player.server_id,
        player_character_id=game_state.player.character_id,
        map_id=game_state.map.map_id,
        sub_area_id=game_state.map.sub_area_id,
        fight_breed_id=game_state.fight.breed_id,
        fight_characteristic_by_id=game_state.fight.characteristic_by_id,
        inventory_objects_by_uid=game_state.inventory.objects_by_uid,
        positive_actor_count=sum(1 for actor_id in game_state.entity.actor_by_id if actor_id > 0),
    )
