from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
    Direction,
    EntityDisposition,
    SpawnInformation,
    Team,
)


def make_fighter(
    actor_id: int,
    cell_id: int,
    alive: bool = True,
    team: Team = Team.TEAM_DEFENDER,
) -> ActorPositionInformation:
    return ActorPositionInformation(
        actor_id=actor_id,
        disposition=EntityDisposition(cell_id=cell_id, entity_id=actor_id),
        actor_information=ActorPositionInformation.ActorInformation(
            fighter=ActorPositionInformation.ActorInformation.FightFighterInformation(
                spawn_information=SpawnInformation(team=team, alive=alive)
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
