import os
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass

from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
    CharacterCharacteristic,
    CharacterCharacteristicValue,
    EntityDisposition,
    FightCharacteristics,
    SpawnInformation,
    Team,
)
from DBDofusUnity.datas.protos.non_obf.game.spell_pb2 import SpellItem
from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.game_constants.breed import BreedEnum
from DBDofusUnity.dofus_unity_reader.game_constants.characteristic import CharacteristicEnum

from src.core.engine.fights.attack.attacker import Attacker
from src.core.engine.fights.damage_calculator import DamageCalculator
from src.core.engine.fights.reachable_cells.fight_reachable_cells import (
    FightReachableCells,
)
from src.core.engine.monsters.monster_group import (
    AIFighter,
    FightFighterInformation,
    MonsterFighter,
    NamedFighterInformation,
)
from src.core.engine.movements.map.map_data_adapter import DataMapProvider
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.core.engine.movements.world.astar_vertice import AstarWorld
from src.core.engine.movements.world.world_path_finder import WorldPathFinder
from src.core.signals.grid_signals import GridSignals
from src.core.signals.log_signals import LogSignals
from src.core.signals.player_signals import GameInfoSignals, InventorySignals
from src.core.signals.world_signals import WorldSignals
from src.core.states.game_state import GameState
from src.core.states.state_factory import StateFactory
from src.services.debug_recorder import DebugRecorder
from src.services.logging_utils.loggers import BotLogger


@dataclass
class GameStateContext:
    game_info_signals: GameInfoSignals
    grid_signals: GridSignals
    log_signals: LogSignals
    world_signals: WorldSignals
    inventory_signals: InventorySignals
    logger: BotLogger
    debug_recorder: DebugRecorder
    game_state: GameState
    damage_calculator: DamageCalculator
    data_map_provider: DataMapProvider
    pathfinding: Pathfinding
    fight_reachable_cells: FightReachableCells
    attacker: Attacker
    world_path_finder: WorldPathFinder


def make_game_state_ctx(debug_recorder: DebugRecorder | None = None) -> GameStateContext:
    game_info_signals = GameInfoSignals()
    grid_signals = GridSignals()
    log_signals = LogSignals()
    world_signals = WorldSignals()
    inventory_signals = InventorySignals()

    debug_recorder = debug_recorder or DebugRecorder(
        file_path=os.path.join(tempfile.gettempdir(), "gamestatefixture.debug.jsonl")
    )
    logger = BotLogger(
        log_signals=log_signals,
        title="gamestatefixture",
        debug_recorder=debug_recorder,
    )

    game_state = StateFactory.create_game_state(
        inventory_signals=inventory_signals,
        game_info_signals=game_info_signals,
        grid_signals=grid_signals,
        logger=logger,
        login="yolo",
    )

    damage_calculator = DamageCalculator()
    data_map_provider = DataMapProvider()

    pathfinding = Pathfinding(
        data_map_provider=data_map_provider,
        logger=logger,
    )

    fight_reachable_cells = FightReachableCells()

    attacker = Attacker(
        _logger=logger,
        damage_calculator=damage_calculator,
        path_finding=pathfinding,
        fight_reachable_cells=fight_reachable_cells,
    )

    astar_world = AstarWorld(world_signals=world_signals)

    world_path_finder = WorldPathFinder(
        path_finding=pathfinding,
        astar_world=astar_world,
    )

    return GameStateContext(
        game_info_signals=game_info_signals,
        grid_signals=grid_signals,
        log_signals=log_signals,
        world_signals=world_signals,
        inventory_signals=inventory_signals,
        logger=logger,
        debug_recorder=debug_recorder,
        game_state=game_state,
        damage_calculator=damage_calculator,
        data_map_provider=data_map_provider,
        pathfinding=pathfinding,
        fight_reachable_cells=fight_reachable_cells,
        attacker=attacker,
        world_path_finder=world_path_finder,
    )


def set_game_state(
    game_state: GameState,
    *,
    player_cell_id: int,
    enemy_cell_ids: Iterable[int],
    include_spell_ids: Iterable[int] | None = None,
    map_id: int = 88090898,
    movement_point: int = 5,
) -> None:
    player_id = -1
    data_reader = DataReader()

    game_state.map.map_id = map_id
    game_state.player.character_id = player_id
    game_state.fight.breed_id = BreedEnum.CRA
    game_state.player.level = 200

    characteristics: dict[CharacteristicEnum, int] = {
        CharacteristicEnum.AGILITY: 700,
        CharacteristicEnum.LIFE_POINTS: 1500,
        CharacteristicEnum.ACTION_POINTS: 10,
        CharacteristicEnum.MOVEMENT_POINTS: movement_point,
        CharacteristicEnum.RANGE: 10,
    }

    for characteristic_id, value in characteristics.items():
        game_state.fight.characteristic_by_id[characteristic_id] = CharacterCharacteristic(
            characteristic_id=characteristic_id,
            value=CharacterCharacteristicValue(total=value),
        )

    included_spell_ids = set(include_spell_ids) if include_spell_ids is not None else None

    for spell_variant in data_reader.spell_variant_by_breed_id[game_state.fight.breed_id]:
        spell_id = spell_variant.spellIds[0]

        if included_spell_ids is not None and spell_id not in included_spell_ids:
            continue

        game_state.fight.spells.append(
            SpellItem(
                spell_id=spell_id,
                spell_level=0,
                available=True,
            )
        )

    player_actor = ActorPositionInformation(
        actor_id=player_id,
        disposition=EntityDisposition(
            entity_id=player_id,
            cell_id=player_cell_id,
        ),
        actor_information=ActorPositionInformation.ActorInformation(
            fighter=FightFighterInformation(
                named_fighter=NamedFighterInformation(
                    character_information=NamedFighterInformation.FightCharacterInformation()
                ),
                stats=FightCharacteristics(characteristics=game_state.fight.characteristic_by_id.values()),
            )
        ),
    )

    game_state.entity.set_actor(player_actor)

    monster_gid = next(iter(data_reader.monsters_by_id))

    for actor_id, enemy_cell_id in enumerate(enemy_cell_ids):
        enemy_actor = ActorPositionInformation(
            actor_id=actor_id,
            disposition=EntityDisposition(
                entity_id=actor_id,
                cell_id=enemy_cell_id,
            ),
            actor_information=ActorPositionInformation.ActorInformation(
                fighter=FightFighterInformation(
                    ai_fighter=AIFighter(
                        monster_fighter_information=MonsterFighter(
                            monster_gid=monster_gid,
                            creature_level=50,
                            creature_grade=1,
                        )
                    ),
                    spawn_information=SpawnInformation(team=Team.TEAM_DEFENDER),
                    stats=FightCharacteristics(
                        characteristics=[
                            CharacterCharacteristic(
                                characteristic_id=CharacteristicEnum.LIFE_POINTS,
                                value=CharacterCharacteristicValue(total=700),
                            )
                        ]
                    ),
                )
            ),
        )

        game_state.entity.set_actor(enemy_actor)
