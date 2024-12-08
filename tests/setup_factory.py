import unittest
from typing import Iterable

from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.enums.breed import Breed
from dofus_unity_reader.enums.characteristic_enum import CharacteristicEnum
from datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
    CharacterCharacteristic,
    CharacterCharacteristicValue,
    EntityDisposition,
    FightCharacteristics,
    SpawnInformation,
    Team,
)
from datas.protos.non_obf.game.spell_pb2 import SpellItem
from src.core.engine.fights.attack import Attacker
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
from src.core.states.state_factory import StateFactory
from src.services.logging.logger import Logger


class GameStateFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.game_info_signals = GameInfoSignals()
        self.grid_signals = GridSignals()
        self.log_signals = LogSignals()
        self.world_signals = WorldSignals()
        self.inventory_signals = InventorySignals()
        self.logger = Logger(log_signals=LogSignals(), title="gamestatefixture")
        self.game_state = StateFactory.create_game_state(
            inventory_signals=self.inventory_signals,
            game_info_signals=self.game_info_signals,
            grid_signals=self.grid_signals,
            logger=self.logger,
        )
        self.damage_calculator = DamageCalculator(game_state=self.game_state)
        self.data_map_provider = DataMapProvider(game_state=self.game_state)
        self.pathfinding = Pathfinding(
            data_map_provider=self.data_map_provider,
            game_state=self.game_state,
            logger=self.logger,
        )
        self.fight_reachable_cells = FightReachableCells(game_state=self.game_state)
        self.attacker = Attacker(
            game_state=self.game_state,
            logger=self.logger,
            damage_calculator=self.damage_calculator,
            path_finding=self.pathfinding,
            fight_reachable_cells=self.fight_reachable_cells,
        )
        astar_world = AstarWorld(
            game_state=self.game_state, world_signals=self.world_signals
        )
        self.world_path_finder = WorldPathFinder(
            path_finding=self.pathfinding,
            game_state=self.game_state,
            astar_world=astar_world,
        )

    def tearDown(self) -> None:
        self.logger.close()

    def set_game_state(
        self,
        player_cell_id: int,
        enemy_cell_ids: Iterable[int],
        include_spell_ids: Iterable[int] | None = None,
        map_id: int = 88090898,
        movement_point: int = 5,
    ) -> None:
        player_id = -1
        self.game_state.map.map_id = map_id
        self.game_state.player.character_id = player_id
        self.game_state.fight.breed_id = Breed.CRA
        self.game_state.player.level = 200

        player_characteristics: dict[CharacteristicEnum, int] = {
            CharacteristicEnum.AGILITY: 700,
            CharacteristicEnum.LIFE_POINTS: 1500,
            CharacteristicEnum.ACTION_POINTS: 10,
            CharacteristicEnum.MOVEMENT_POINTS: movement_point,
            CharacteristicEnum.RANGE: 10,
        }
        for char, value in player_characteristics.items():
            self.game_state.fight.characteristic_by_id[char] = CharacterCharacteristic(
                characteristic_id=char,
                value=CharacterCharacteristicValue(total=value),
            )

        for spell_variant in DataReader().spell_variant_by_breed_id[
            self.game_state.fight.breed_id
        ]:
            if (
                include_spell_ids is None
                or spell_variant.spellIds[0] in include_spell_ids
            ):
                self.game_state.fight.spells.append(
                    SpellItem(
                        spell_id=spell_variant.spellIds[0],
                        spell_level=0,
                        available=True,
                    )
                )

        player_actor = ActorPositionInformation(
            actor_id=player_id,
            disposition=EntityDisposition(entity_id=player_id, cell_id=player_cell_id),
            actor_information=ActorPositionInformation.ActorInformation(
                fighter=FightFighterInformation(
                    named_fighter=NamedFighterInformation(
                        character_information=NamedFighterInformation.FightCharacterInformation()
                    ),
                    stats=FightCharacteristics(
                        characteristics=self.game_state.fight.characteristic_by_id.values()
                    ),
                )
            ),
        )
        self.game_state.entity.set_actor(player_actor)

        monster_gid = next(iter(DataReader().monsters_by_id))

        for index, enemy_cell_id in enumerate(enemy_cell_ids):
            enemy_actor = ActorPositionInformation(
                actor_id=index,
                disposition=EntityDisposition(entity_id=index, cell_id=enemy_cell_id),
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
            self.game_state.entity.set_actor(enemy_actor)
