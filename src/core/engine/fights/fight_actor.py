from dataclasses import dataclass


@dataclass
class FightActor:
    life_point: int
    is_summoned: bool
