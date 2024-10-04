import sys
from pathlib import Path

from src.core.repositories.map_reader import MapReader

sys.path.append(str(Path(__file__).parent.parent))

if __name__ == "__main__":
    print(MapReader().get_ref_data_by_element_id(190579712, 512663))
    sys.exit()
    map_id = 88212759
    start = MapPoint.from_cell_id(281)
    end = MapPoint.from_cell_id(357)

    is_in_fight = False

    player_property_signals = PlayerPropertySignals()
    player_state = PlayerAPI(player_property_signals)
    player_state.map_id = map_id
    entity_state = EntityAPI()

    data_map_provider = DataMapProvider(
        entity_state=entity_state, player_state=player_state
    )
    path_finding = Pathfinding(data_map_provider=data_map_provider)

    temp = path_finding.find_path(
        start,
        end,
        allow_diag=not is_in_fight,
        allow_trough_entity=not is_in_fight,
        avoid_obstacles=True,
    )
    icecream.ic(temp.path)

    ans = temp.get_key_cells()
    print(ans)

    # for ans in temp.path:
