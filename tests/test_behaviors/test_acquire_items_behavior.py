
from collections.abc import Callable
from typing import cast
from unittest.mock import MagicMock

from ankama_launcher_emulator_premium.interfaces.zaap_files import GameSubscription
from datas.protos.non_obf.game.common_pb2 import ObjectItem, ObjectItemInventory
from dofus_unity_reader.game_constants.item import CategoryItemEnum, ItemEnum
from pytest import MonkeyPatch

from src.const import MIN_DATE

from src.core.behaviors.items.acquire_items_behavior import (
    AcquireItemsBehavior,
    ItemToAcquire,
)
from src.core.behaviors.storage.enter_chests.enter_bank_chest_behavior import (
    EnterBankChestErrorCode,
)
from src.core.behaviors.storage.loads.load_item_request import LoadItemInfo
from src.core.engine.economy.sale_hotel import ItemToBuyInfo
from src.core.events_manager.event_manager import EventManager
from tests.fixtures.bot_runtime import make_blocking_state_recovery
from tests.fixtures.game_state import GameStateContext

GRAISSE_GELATINEUSE_GID = int(ItemEnum.GRAISSE_GELATINEUSE)
POILS_DE_KERUBIM_GID = int(ItemEnum.POILS_DE_KERUBIM)
AMULETTE_AKWADALA_GID = int(ItemEnum.AMULETTE_AKWADALA)


def _make_behavior(
    game_state_ctx: GameStateContext, monkeypatch: MonkeyPatch
) -> AcquireItemsBehavior:
    def fake_get_game_sub_info(login: str) -> GameSubscription:
        del login
        return GameSubscription(
            isFreeToPlay=True,
            isFormerSubscriber=True,
            isSubscribed=False,
            totalPlayTime=0,
            endOfSubscribe=MIN_DATE,
            id=1,
        )

    monkeypatch.setattr(
        "src.core.states.player_state.get_game_sub_info_by_login",
        fake_get_game_sub_info,
    )
    game_state = game_state_ctx.game_state
    game_state.player.level = 200
    game_state.inventory.kamas = 1_000_000
    game_state.inventory.weight_max = 10_000
    game_state.inventory.inventory_weight = 0
    behavior = AcquireItemsBehavior(
        recovery=make_blocking_state_recovery(),
        event_manager=EventManager(_logger=game_state_ctx.logger),
        game_state=game_state,
        _logger=game_state_ctx.logger,
        load_from_bank_behavior=MagicMock(),
        sale_hotel_buy_behavior=MagicMock(),
    )

    def run_timer_inline(range_time: tuple[float, float] | float, func: Callable[[], None]) -> None:
        del range_time
        func()

    behavior.run_timer = run_timer_inline
    return behavior


def _mock_of(child_behavior: object) -> MagicMock:
    return cast(MagicMock, child_behavior)


def _child_callback(child_behavior: object) -> Callable[..., None]:
    return cast(Callable[..., None], _mock_of(child_behavior).start.call_args.kwargs["callback"])


def _child_kwarg(child_behavior: object, name: str) -> object:
    return _mock_of(child_behavior).start.call_args.kwargs[name]


def _put_in_inventory(behavior: AcquireItemsBehavior, item_gid: int, quantity: int) -> None:
    behavior.game_state.inventory.objects_by_uid[item_gid] = ObjectItemInventory(
        item=ObjectItem(uid=item_gid, gid=item_gid, quantity=quantity)
    )


def _put_in_bank(behavior: AcquireItemsBehavior, item_gid: int, quantity: int) -> None:
    uid = 10_000 + item_gid
    behavior.game_state.inventory.bank_objects_by_uid[uid] = ObjectItemInventory(
        item=ObjectItem(uid=uid, gid=item_gid, quantity=quantity)
    )
    behavior.game_state.inventory.bank_content_known = True


def _start(
    behavior: AcquireItemsBehavior,
    items: list[ItemToAcquire],
    finished: list[tuple[str | None, dict[int, int]]] | None = None,
) -> None:
    def callback(error_code: str | None, missing_by_gid: dict[int, int]) -> None:
        if finished is not None:
            finished.append((error_code, missing_by_gid))

    behavior.start(items=items, callback=callback, parent=None)


def _request(
    item_gid: int,
    quantity: int = 1,
    category: CategoryItemEnum = CategoryItemEnum.RESOURCES,
) -> ItemToAcquire:
    return ItemToAcquire(
        item_gid=item_gid, quantity=quantity, max_kamas=5_000, category=category
    )


def test_nothing_moves_when_the_inventory_already_holds_everything(
    game_state_ctx: GameStateContext, monkeypatch: MonkeyPatch
) -> None:
    behavior = _make_behavior(game_state_ctx, monkeypatch)
    _put_in_inventory(behavior, GRAISSE_GELATINEUSE_GID, 5)
    finished: list[tuple[str | None, dict[int, int]]] = []

    _start(behavior, [_request(GRAISSE_GELATINEUSE_GID, quantity=5)], finished)

    _mock_of(behavior.load_from_bank_behavior).start.assert_not_called()
    _mock_of(behavior.sale_hotel_buy_behavior).start.assert_not_called()
    assert finished == [(None, {})]


def test_an_item_held_in_bank_is_withdrawn_and_never_bought(
    game_state_ctx: GameStateContext, monkeypatch: MonkeyPatch
) -> None:
    behavior = _make_behavior(game_state_ctx, monkeypatch)
    _put_in_bank(behavior, GRAISSE_GELATINEUSE_GID, 20)
    finished: list[tuple[str | None, dict[int, int]]] = []

    _start(behavior, [_request(GRAISSE_GELATINEUSE_GID, quantity=5)], finished)

    load_items = cast(
        list[LoadItemInfo], _child_kwarg(behavior.load_from_bank_behavior, "load_items_infos")
    )
    assert [(item.item_gid, item.remaining_quantity) for item in load_items] == [
        (GRAISSE_GELATINEUSE_GID, 5)
    ]

    _put_in_inventory(behavior, GRAISSE_GELATINEUSE_GID, 5)
    _child_callback(behavior.load_from_bank_behavior)(None, [])

    _mock_of(behavior.sale_hotel_buy_behavior).start.assert_not_called()
    assert finished == [(None, {})]


def test_the_bank_is_not_emptied_on_the_way_in(game_state_ctx: GameStateContext, monkeypatch: MonkeyPatch) -> None:
    behavior = _make_behavior(game_state_ctx, monkeypatch)
    _put_in_bank(behavior, GRAISSE_GELATINEUSE_GID, 20)

    _start(behavior, [_request(GRAISSE_GELATINEUSE_GID, quantity=5)])

    assert _child_kwarg(behavior.load_from_bank_behavior, "unload_first") is False


def test_a_known_bank_without_the_item_spares_the_trip(game_state_ctx: GameStateContext, monkeypatch: MonkeyPatch) -> None:
    behavior = _make_behavior(game_state_ctx, monkeypatch)
    _put_in_bank(behavior, POILS_DE_KERUBIM_GID, 3)

    _start(behavior, [_request(GRAISSE_GELATINEUSE_GID, quantity=5)])

    _mock_of(behavior.load_from_bank_behavior).start.assert_not_called()
    _mock_of(behavior.sale_hotel_buy_behavior).start.assert_called_once()


def test_an_unopened_bank_is_visited_rather_than_assumed_empty(
    game_state_ctx: GameStateContext, monkeypatch: MonkeyPatch
) -> None:
    behavior = _make_behavior(game_state_ctx, monkeypatch)
    assert behavior.game_state.inventory.bank_content_known is False

    _start(behavior, [_request(GRAISSE_GELATINEUSE_GID, quantity=5)])

    _mock_of(behavior.load_from_bank_behavior).start.assert_called_once()
    _mock_of(behavior.sale_hotel_buy_behavior).start.assert_not_called()


def test_only_what_the_bank_could_not_cover_is_bought(game_state_ctx: GameStateContext, monkeypatch: MonkeyPatch) -> None:
    behavior = _make_behavior(game_state_ctx, monkeypatch)
    _put_in_bank(behavior, GRAISSE_GELATINEUSE_GID, 2)

    _start(behavior, [_request(GRAISSE_GELATINEUSE_GID, quantity=5)])
    _put_in_inventory(behavior, GRAISSE_GELATINEUSE_GID, 2)
    _child_callback(behavior.load_from_bank_behavior)(None, [])

    item_infos = cast(
        list[ItemToBuyInfo], _child_kwarg(behavior.sale_hotel_buy_behavior, "item_infos_to_buy")
    )
    assert len(item_infos) == 3
    assert {item_info.item_gid for item_info in item_infos} == {GRAISSE_GELATINEUSE_GID}


def test_a_failing_bank_leg_still_lets_the_purchase_happen(
    game_state_ctx: GameStateContext, monkeypatch: MonkeyPatch
) -> None:
    behavior = _make_behavior(game_state_ctx, monkeypatch)
    _put_in_bank(behavior, GRAISSE_GELATINEUSE_GID, 20)
    finished: list[tuple[str | None, dict[int, int]]] = []

    _start(behavior, [_request(GRAISSE_GELATINEUSE_GID, quantity=5)], finished)
    _child_callback(behavior.load_from_bank_behavior)(EnterBankChestErrorCode.NOT_ENOUGH_LVL, [])

    _mock_of(behavior.sale_hotel_buy_behavior).start.assert_called_once()
    assert finished == []


def test_a_character_without_bank_access_goes_straight_to_the_sale_hotel(
    game_state_ctx: GameStateContext, monkeypatch: MonkeyPatch
) -> None:
    behavior = _make_behavior(game_state_ctx, monkeypatch)
    behavior.game_state.inventory.kamas = 500

    _start(behavior, [_request(GRAISSE_GELATINEUSE_GID, quantity=5)])

    _mock_of(behavior.load_from_bank_behavior).start.assert_not_called()
    _mock_of(behavior.sale_hotel_buy_behavior).start.assert_called_once()


def test_each_category_gets_its_own_sale_hotel_visit(game_state_ctx: GameStateContext, monkeypatch: MonkeyPatch) -> None:
    behavior = _make_behavior(game_state_ctx, monkeypatch)
    behavior.game_state.inventory.bank_content_known = True

    _start(
        behavior,
        [
            _request(GRAISSE_GELATINEUSE_GID, quantity=1, category=CategoryItemEnum.RESOURCES),
            _request(AMULETTE_AKWADALA_GID, quantity=1, category=CategoryItemEnum.EQUIPMENT),
        ],
    )

    assert _child_kwarg(behavior.sale_hotel_buy_behavior, "category") == CategoryItemEnum.EQUIPMENT
    _put_in_inventory(behavior, AMULETTE_AKWADALA_GID, 1)
    _child_callback(behavior.sale_hotel_buy_behavior)(None, [ObjectItemInventory()])

    assert _child_kwarg(behavior.sale_hotel_buy_behavior, "category") == CategoryItemEnum.RESOURCES
    assert _mock_of(behavior.sale_hotel_buy_behavior).start.call_count == 2


def test_full_pods_stop_the_purchase_and_report_what_is_missing(
    game_state_ctx: GameStateContext, monkeypatch: MonkeyPatch
) -> None:
    behavior = _make_behavior(game_state_ctx, monkeypatch)
    behavior.game_state.inventory.bank_content_known = True
    behavior.game_state.inventory.inventory_weight = 9_500
    finished: list[tuple[str | None, dict[int, int]]] = []

    _start(behavior, [_request(GRAISSE_GELATINEUSE_GID, quantity=5)], finished)

    _mock_of(behavior.sale_hotel_buy_behavior).start.assert_not_called()
    assert finished == [(None, {GRAISSE_GELATINEUSE_GID: 5})]


def test_an_upgrade_visits_the_bank_though_nothing_is_missing(
    game_state_ctx: GameStateContext, monkeypatch: MonkeyPatch
) -> None:
    behavior = _make_behavior(game_state_ctx, monkeypatch)
    _put_in_inventory(behavior, AMULETTE_AKWADALA_GID, 1)
    _put_in_bank(behavior, AMULETTE_AKWADALA_GID, 1)

    _start(
        behavior,
        [
            ItemToAcquire(
                item_gid=AMULETTE_AKWADALA_GID,
                max_kamas=10_000,
                category=CategoryItemEnum.EQUIPMENT,
                upgrade_from_bank=True,
            )
        ],
    )

    load_items = cast(
        list[LoadItemInfo], _child_kwarg(behavior.load_from_bank_behavior, "load_items_infos")
    )
    assert [(item.item_gid, item.remaining_quantity) for item in load_items] == [
        (AMULETTE_AKWADALA_GID, 1)
    ]


def test_a_failed_upgrade_never_falls_back_to_buying(
    game_state_ctx: GameStateContext, monkeypatch: MonkeyPatch
) -> None:
    behavior = _make_behavior(game_state_ctx, monkeypatch)
    _put_in_inventory(behavior, AMULETTE_AKWADALA_GID, 1)
    _put_in_bank(behavior, AMULETTE_AKWADALA_GID, 1)
    finished: list[tuple[str | None, dict[int, int]]] = []

    _start(
        behavior,
        [
            ItemToAcquire(
                item_gid=AMULETTE_AKWADALA_GID,
                max_kamas=10_000,
                category=CategoryItemEnum.EQUIPMENT,
                upgrade_from_bank=True,
            )
        ],
        finished,
    )
    _child_callback(behavior.load_from_bank_behavior)(EnterBankChestErrorCode.NOT_ENOUGH_LVL, [])

    _mock_of(behavior.sale_hotel_buy_behavior).start.assert_not_called()
    assert finished == [(None, {})]


def test_an_upgrade_with_an_empty_bank_asks_for_nothing(
    game_state_ctx: GameStateContext, monkeypatch: MonkeyPatch
) -> None:
    behavior = _make_behavior(game_state_ctx, monkeypatch)
    _put_in_inventory(behavior, AMULETTE_AKWADALA_GID, 1)
    behavior.game_state.inventory.bank_content_known = True
    finished: list[tuple[str | None, dict[int, int]]] = []

    _start(
        behavior,
        [
            ItemToAcquire(
                item_gid=AMULETTE_AKWADALA_GID,
                max_kamas=10_000,
                category=CategoryItemEnum.EQUIPMENT,
                upgrade_from_bank=True,
            )
        ],
        finished,
    )

    _mock_of(behavior.load_from_bank_behavior).start.assert_not_called()
    _mock_of(behavior.sale_hotel_buy_behavior).start.assert_not_called()
    assert finished == [(None, {})]
