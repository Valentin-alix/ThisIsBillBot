from D3Database.data_center.data_reader import DataReader
from src.core.signals.world_signals import WorldSignals


def draw_weight_on_map(weight_by_map_id: dict[int, float], world_signals: WorldSignals):
    if len(weight_by_map_id) == 0:
        return
    max_weight = max(weight_by_map_id.values())
    world_signals.reset_weight.emit()
    batch: list[tuple] = []
    for map_id, weight in weight_by_map_id.items():
        if map_id not in DataReader().map_pos_by_map_id:
            continue
        map_data = DataReader().map_pos_by_map_id[map_id]
        weight_color = int(255 * (weight / max_weight))
        batch.append((map_data, (255, 255 - weight_color, 0)))
    if batch:
        world_signals.color_pos_batch.emit(batch)
