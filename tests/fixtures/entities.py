from common_pb2 import (
    ActorPositionInformation,
    Direction,
    EntityDisposition,
    SpawnInformation,
    Team,
)


def make_monster_group_actor(
    main_gid: int,
    main_level: int,
    underlings: list[tuple[int, int]] | None = None,
) -> ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor:
    monster_group = (
        ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor()
    )
    monster_group.identification.main_creature.gid = main_gid
    monster_group.identification.main_creature.level = main_level

    for underling_gid, underling_level in underlings or []:
        underling = monster_group.identification.underlings.add()
        underling.gid = underling_gid
        underling.level = underling_level

    return monster_group


def make_monster_actor(
    actor_id: int,
    cell_id: int,
    monster_group: ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor,
) -> ActorPositionInformation:
    return ActorPositionInformation(
        actor_id=actor_id,
        disposition=EntityDisposition(cell_id=cell_id),
        actor_information=ActorPositionInformation.ActorInformation(
            role_play_actor=ActorPositionInformation.ActorInformation.RolePlayActor(
                monster_group_actor=monster_group,
            ),
        ),
    )


def make_fight_actor(actor_id: int, team: Team) -> ActorPositionInformation:
    return ActorPositionInformation(
        actor_id=actor_id,
        actor_information=ActorPositionInformation.ActorInformation(
            fighter=ActorPositionInformation.ActorInformation.FightFighterInformation(
                spawn_information=SpawnInformation(team=team)
            )
        ),
    )


def make_actor(
    actor_id: int,
    cell_id: int,
    direction: Direction = Direction.DIRECTION_EAST,
) -> ActorPositionInformation:
    return ActorPositionInformation(
        actor_id=actor_id,
        disposition=EntityDisposition(
            cell_id=cell_id,
            entity_id=actor_id,
            direction=direction,
        ),
    )
