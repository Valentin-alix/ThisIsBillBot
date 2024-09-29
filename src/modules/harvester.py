from dataclasses import dataclass
from threading import Thread

from src.core.logic.inventory import Inventory


@dataclass
class Harvester:
    inventory: Inventory

    def __post_init__(self):
        Thread(target=self.start, daemon=True).start()

    def start(self): ...
