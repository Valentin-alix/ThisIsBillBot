from src.core.data_center.data_reader import DataReader

ASTRUB_BANK_MAP = 192415750
BONTA_BANK_MAP = 217059328

BANK_MAP_IDS = [ASTRUB_BANK_MAP, BONTA_BANK_MAP]
GATHERER_ITEM_IDS: set[int] = {
    harvestable
    for sub_area in DataReader().sub_area_by_id.values()
    for harvestable in sub_area.harvestables
}
