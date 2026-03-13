from dataclasses import dataclass

from DBDofusUnity.dofus_unity_reader.game_constants.breed import BreedEnum

from src.core.engine.contexts import AttackContext
from src.core.engine.fights.attack.breed import sacrier
from src.core.engine.fights.attack.breed.types import ReservedApProvider, SupportAction, SupportActionRule
from src.core.engine.fights.damage_calculator import DamageCalculator
from src.core.engine.fights.reachable_cells.fight_reachable_cells import FightReachableCells
from src.services.logging_utils.contextual_logger import ContextualLogger

_BREED_RULES: dict[int, list[SupportActionRule]] = {
    BreedEnum.SACRIER: sacrier.RULES,
}

_BREED_URGENT_RULES: dict[int, list[SupportActionRule]] = {
    BreedEnum.SACRIER: sacrier.URGENT_RULES,
}

_RESERVED_AP_PROVIDERS: dict[int, ReservedApProvider] = {
    BreedEnum.SACRIER: sacrier.get_reserved_ap,
}


@dataclass
class BreedAbilitySelector(ContextualLogger):
    fight_reachable_cells: FightReachableCells
    damage_calculator: DamageCalculator

    def find_support_action(self, context: AttackContext) -> SupportAction | None:
        for rule in _BREED_RULES.get(context.breed_id, []):
            action = rule(context, self.fight_reachable_cells, self.damage_calculator)
            if action is not None:
                _, spell_lvl, target_mp = action
                self.logger.info(
                    f"Breed support action selected: spell {spell_lvl.spellId} -> cell {target_mp.cell_id}"
                )
                return action
        return None

    def find_urgent_support_action(self, context: AttackContext) -> SupportAction | None:
        for rule in _BREED_URGENT_RULES.get(context.breed_id, []):
            action = rule(context, self.fight_reachable_cells, self.damage_calculator)
            if action is not None:
                _, spell_lvl, target_mp = action
                self.logger.info(
                    f"Breed urgent support action selected: spell {spell_lvl.spellId} -> cell {target_mp.cell_id}"
                )
                return action
        return None

    def get_reserved_ap(self, context: AttackContext) -> int:
        provider = _RESERVED_AP_PROVIDERS.get(context.breed_id)
        return provider(context, self.damage_calculator) if provider is not None else 0
