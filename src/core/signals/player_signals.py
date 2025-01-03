import datetime

from datas.protos.non_obf.game.common_pb2 import ObjectItemInventory
from PyQt6.QtCore import QObject, pyqtSignal


class GameInfoSignals(QObject):
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    is_ready_to_play = pyqtSignal()
    breed_id = pyqtSignal(int)
    character_id = pyqtSignal(object)  # bc it's a big int
    character_name = pyqtSignal(str)
    subscription_end_date = pyqtSignal(datetime.datetime)
    in_fight = pyqtSignal(bool)
    is_our_turn = pyqtSignal(bool)
    level = pyqtSignal(int)
    life_point = pyqtSignal(int)
    max_life_point = pyqtSignal(int)
    server_id = pyqtSignal(int)
    has_guild = pyqtSignal(bool)
    tab_number = pyqtSignal(int)
    is_in_haven_bag = pyqtSignal(bool)
    last_time_updated_prices = pyqtSignal(datetime.datetime)
    fight_turn = pyqtSignal(int)
    fight_completed = pyqtSignal(int)


class InventorySignals(QObject):
    added_object_item = pyqtSignal(ObjectItemInventory)
    added_object_items_batch = pyqtSignal(list)  # list of ObjectItemInventory
    updated_object_item = pyqtSignal(ObjectItemInventory)
    deleted_object_item_uid = pyqtSignal(int)
    clear_inventory = pyqtSignal()
    inventory_weight = pyqtSignal(int)
    weight_max = pyqtSignal(int)
    kamas = pyqtSignal(int)
    bank_refreshed = pyqtSignal(list)  # list[ObjectItemInventory]
    bank_item_updated = pyqtSignal(ObjectItemInventory)
    bank_item_removed = pyqtSignal(int)  # uid
