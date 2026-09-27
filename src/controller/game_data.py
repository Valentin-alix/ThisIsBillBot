from collections import defaultdict
from pathlib import Path
from threading import RLock

from utils.singleton import Singleton
from DBDofusUnity.dofus_unity_reader.game_constants.job import JobEnum
from pydantic import BaseModel, Field

from src.consts import RESOURCE_FOLDER


class SaleHotelServerData(BaseModel):
    avg_price_by_gid: dict[int, float] = Field(default_factory=dict[int, float])
    bid_seller_item_by_uid_by_player_id: dict[int, dict[int, tuple[int, int, int]]] = Field(
        default_factory=dict[int, dict[int, tuple[int, int, int]]]
    )


class GameDataFile(BaseModel):
    gfx_to_item: dict[int, tuple[int, int]] = Field(default_factory=dict[int, tuple[int, int]])
    collectable_map_checked: set[int] = Field(default_factory=set[int])
    sale_hotel_by_server: dict[int, SaleHotelServerData] = Field(
        default_factory=dict[int, SaleHotelServerData]
    )


class GameDataController(metaclass=Singleton):
    _LOCK = RLock()
    _FILE_PATH = Path(RESOURCE_FOLDER) / "game_data.json"
    _DEFEAT_THRESHOLD = 6
    _loaded_path: Path | None = None
    _game_data: GameDataFile | None = None

    def _load(self) -> GameDataFile:
        if self._loaded_path != self._FILE_PATH or self._game_data is None:
            self._game_data = (
                GameDataFile.model_validate_json(self._FILE_PATH.read_text(encoding="utf-8"))
                if self._FILE_PATH.exists()
                else GameDataFile()
            )
            self._loaded_path = self._FILE_PATH
        return self._game_data

    def _save(self, game_data: GameDataFile) -> None:
        self._FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        self._FILE_PATH.write_text(game_data.model_dump_json(indent=2), encoding="utf-8")
        self._game_data = game_data
        self._loaded_path = self._FILE_PATH

    def get_item_job_by_gfx(self) -> dict[int, tuple[int, int]]:
        with self._LOCK:
            return self._load().gfx_to_item

    def add_item_jobs_by_gfx(
        self,
        item_job_by_gfx: dict[int, tuple[int, int]],
    ) -> None:
        if not item_job_by_gfx:
            return
        with self._LOCK:
            game_data = self._load()
            changed = False
            for gfx_id, item_and_job in item_job_by_gfx.items():
                if gfx_id not in game_data.gfx_to_item:
                    game_data.gfx_to_item[gfx_id] = item_and_job
                    changed = True
            if changed:
                self._save(game_data)

    def add_multiple_item_job_by_gfx(
        self,
        item_and_job_by_gfx_array: list[tuple[int, int, JobEnum]],
    ) -> None:
        self.add_item_jobs_by_gfx(
            {gfx_id: (item_id, int(job_id)) for gfx_id, item_id, job_id in item_and_job_by_gfx_array}
        )

    def get_map_ids_checked(self) -> set[int]:
        with self._LOCK:
            return self._load().collectable_map_checked

    def add_map_id_checked(self, map_id: int) -> None:
        with self._LOCK:
            game_data = self._load()
            if map_id in game_data.collectable_map_checked:
                return
            game_data.collectable_map_checked.add(map_id)
            self._save(game_data)

    def get_sale_hotel_server(self, server_id: int) -> SaleHotelServerData:
        with self._LOCK:
            return self._load().sale_hotel_by_server.get(
                server_id,
                SaleHotelServerData(),
            )

    def get_avg_price_by_gid(self, server_id: int) -> dict[int, float]:
        return self.get_sale_hotel_server(server_id).avg_price_by_gid

    def add_multiple_avg_price_by_gid(
        self,
        server_id: int,
        avg_price_gid_array: list[tuple[int, int]],
    ) -> None:
        if not avg_price_gid_array:
            return
        with self._LOCK:
            game_data = self._load()
            server_data = game_data.sale_hotel_by_server.setdefault(
                server_id,
                SaleHotelServerData(),
            )
            for avg_price, gid in avg_price_gid_array:
                if avg_price != 0:
                    server_data.avg_price_by_gid[gid] = avg_price
            self._save(game_data)

    def get_hdv_by_uid_by_player(
        self,
        server_id: int,
    ) -> dict[int, dict[int, tuple[int, int, int]]]:
        return self.get_sale_hotel_server(server_id).bid_seller_item_by_uid_by_player_id

    def get_minimal_price_by_gid_and_quantity(self, server_id: int) -> dict[tuple[int, int], int]:
        minimal_price_by_gid_and_quantity: dict[tuple[int, int], int] = {}
        for player_bids in self.get_hdv_by_uid_by_player(server_id).values():
            for gid, quantity, price in player_bids.values():
                current_minimal_price = minimal_price_by_gid_and_quantity.get((gid, quantity))
                if current_minimal_price is None or current_minimal_price > price:
                    minimal_price_by_gid_and_quantity[(gid, quantity)] = price
        return minimal_price_by_gid_and_quantity

    def get_item_sell_quantity_by_gid(self, server_id: int) -> defaultdict[int, int]:
        item_sell_quantity_by_gid: dict[int, int] = defaultdict(int)
        for player_bids in self.get_hdv_by_uid_by_player(server_id).values():
            for gid, quantity, _price in player_bids.values():
                item_sell_quantity_by_gid[gid] += quantity
        return item_sell_quantity_by_gid

    def update_hdv(
        self,
        server_id: int,
        player_id: int,
        gid_and_quantity_and_price_by_uid: dict[int, tuple[int, int, int]],
    ) -> None:
        with self._LOCK:
            game_data = self._load()
            server_data = game_data.sale_hotel_by_server.setdefault(
                server_id,
                SaleHotelServerData(),
            )
            server_data.bid_seller_item_by_uid_by_player_id[player_id] = gid_and_quantity_and_price_by_uid
            self._save(game_data)

    def add_gid_quantity_by_uid_by_player_id(
        self,
        server_id: int,
        player_id: int,
        gid: int,
        quantity: int,
        price: int,
        uid: int,
    ) -> None:
        with self._LOCK:
            game_data = self._load()
            server_data = game_data.sale_hotel_by_server.setdefault(
                server_id,
                SaleHotelServerData(),
            )
            player_bids = server_data.bid_seller_item_by_uid_by_player_id.setdefault(
                player_id,
                {},
            )
            player_bids[uid] = (gid, quantity, price)
            self._save(game_data)

    def remove_uid_for_player_id(self, server_id: int, player_id: int, uid: int) -> None:
        with self._LOCK:
            game_data = self._load()
            server_data = game_data.sale_hotel_by_server.setdefault(
                server_id,
                SaleHotelServerData(),
            )
            player_bids = server_data.bid_seller_item_by_uid_by_player_id.setdefault(
                player_id,
                {},
            )
            player_bids.pop(uid, None)
            self._save(game_data)
