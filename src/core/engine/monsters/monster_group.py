from logging import Logger

from datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
)
from dofus_unity_reader.game_constants.monster import MonsterGidEnum
from dofus_unity_reader.grid.map_point import MapPoint


def get_level_monster_group(
    monster_group: ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor,
) -> int:
    """
    Calculate total level of a monster group.

    Args:
        monster_group: The MonsterGroupActor to calculate level for

    Returns:
        Total level (main creature + all underlings)
    """
    total_group_lvl = 0
    total_group_lvl += monster_group.identification.main_creature.level
    for underling in monster_group.identification.underlings:
        total_group_lvl += underling.level
    return total_group_lvl


def get_monster_group_gids(
    monster_group: ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor,
) -> set[int]:
    gids = {monster_group.identification.main_creature.gid}
    gids.update(underling.gid for underling in monster_group.identification.underlings)
    return gids


MonsterGroup = tuple[
    int,
    MapPoint,
    ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor,
]


def get_monster_groups(
    actor_by_id: dict[int, ActorPositionInformation],
) -> list[MonsterGroup]:
    """
    Extract all monster groups from actors dictionary.

    Args:
        actor_by_id: Dictionary of actor_id -> ActorPositionInformation

    Returns:
        List of MonsterGroup tuples: (actor_id, MapPoint, MonsterGroupActor)
    """
    monster_groups: list[MonsterGroup] = []

    for actor in actor_by_id.values():
        if not (
            actor.actor_information.HasField("role_play_actor")
            and actor.actor_information.role_play_actor.HasField("monster_group_actor")
        ):
            continue

        monster_groups.append(
            (
                actor.actor_id,
                MapPoint.from_cell_id(actor.disposition.cell_id),
                actor.actor_information.role_play_actor.monster_group_actor,
            )
        )

    return monster_groups


FightFighterInformation = ActorPositionInformation.ActorInformation.FightFighterInformation


EntityFighterInformation = FightFighterInformation.EntityFighterInformation
NamedFighterInformation = FightFighterInformation.NamedFighterInformation
AIFighter = FightFighterInformation.AIFighterInformation
MonsterFighter = AIFighter.MonsterFighter


def is_valid_monster_group(
    logger: Logger,
    monster_group: ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor,
    monster_group_lvl: int,
    lvl_limit: float,
) -> bool:
    """
    Validate if a monster group is acceptable for farming.

    Args:
        logger: Logger instance for info messages
        monster_group: The MonsterGroupActor to validate
        monster_group_lvl: Total level of the monster group
        lvl_limit: Maximum acceptable level for the group

    Returns:
        True if monster group is valid, False otherwise
    """
    # Filter out forbidden monsters
    if monster_group.identification.main_creature.gid in [
        MonsterGidEnum.POUTCH,
        MonsterGidEnum.PRESPIC,
    ]:
        return False

    logger.info(f"lvl : {lvl_limit} against monster group lvl : {monster_group_lvl}")
    return monster_group_lvl <= lvl_limit
