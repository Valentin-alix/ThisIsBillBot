from enum import IntEnum


class SpellStateEnum(IntEnum):
    """
    Notable fight state ids (subset of the game's SpellStateId catalog).

    Mirrors Bubble.DamageCalculation/SpellStateId.cs; extend as more states become
    relevant to combat decisions (e.g. fragilise / resource removal).
    """

    # States granting full damage invulnerability.
    INVULNERABLE = 56
    INVULNERABLE_269 = 269
    INVULNERABLE_365 = 365
    INVULNERABLE_399 = 399
    INVULNERABLE_659 = 659
