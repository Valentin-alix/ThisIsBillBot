from enum import StrEnum, auto
from typing import Annotated, Literal

from DBDofusUnity.dofus_unity_reader.game_constants.item import CategoryItemEnum
from DBDofusUnity.dofus_unity_reader.game_constants.npc import NpcActionEnum
from DBDofusUnity.dofus_unity_reader.game_constants.world import WorldMapEnum
from pydantic import BaseModel, Field, model_validator

from src.core.engine.npcs.dialog_turn import DialogTurn


class QuestCooldown(StrEnum):
    NONE = auto()
    DAILY = auto()
    WEEKLY = auto()


class StepWithDestination(BaseModel):
    coord: tuple[int, int] | None = None
    world: int = WorldMapEnum.OVERWORLD
    map_name: str | None = None
    sub_area_id: int | None = None
    map_ids: set[int] | None = None

    @model_validator(mode="after")
    def _check_destination(self):
        if self.coord is not None and self.map_ids is not None:
            raise ValueError("coord and map_ids are mutually exclusive")
        if self.coord is None:
            for field_name in ("map_name", "sub_area_id"):
                if getattr(self, field_name) is not None:
                    raise ValueError(f"{field_name} only narrows a coord")
        return self


class GoToStep(StepWithDestination):
    type: Literal["go_to"] = "go_to"

    @model_validator(mode="after")
    def _check_has_destination(self):
        if self.coord is None and self.map_ids is None:
            raise ValueError("go_to needs either coord or map_ids")
        return self


class TalkToNpcStep(StepWithDestination):
    type: Literal["talk_to_npc"] = "talk_to_npc"
    npc_name: str | None = None
    npc_id: int | None = None
    bones_id: int | None = None
    cell_id: int | None = None
    npc_action_id: int = NpcActionEnum.TALK
    turns: list[DialogTurn] = Field(default_factory=list[DialogTurn])
    turn_variants: list[list[DialogTurn]] = Field(default_factory=list[list[DialogTurn]])

    @model_validator(mode="after")
    def _check_npc_identity(self):
        if self.npc_name is None and self.npc_id is None and self.bones_id is None:
            raise ValueError("talk_to_npc needs either npc_name, npc_id or bones_id")
        return self

    @model_validator(mode="after")
    def _fold_turns_into_variants(self):
        if not self.turn_variants:
            self.turn_variants = [self.turns]
        elif self.turns and self.turn_variants != [self.turns]:
            raise ValueError("turns and turn_variants are mutually exclusive")
        return self


class FightStep(StepWithDestination):
    type: Literal["fight"] = "fight"
    count: int = 1
    wait_for_group: bool = True
    lvl_limit: float | None = None
    monster_name: str | None = None
    monster_id: int | None = None

    @model_validator(mode="after")
    def _check_monster_identity(self):
        if self.monster_name is not None and self.monster_id is not None:
            raise ValueError("monster_name and monster_id are mutually exclusive")
        return self


class UseInteractiveStep(StepWithDestination):
    type: Literal["use_interactive"] = "use_interactive"
    cell_id: int
    skill_id: int | None = None


class UseMapInteractiveStep(StepWithDestination):
    """Utiliser le premier interactif hors sortie de map ; un objectif valide saute son etape."""

    type: Literal["use_map_interactive"] = "use_map_interactive"
    skill_id: int | None = None


class CraftItemStep(BaseModel):
    type: Literal["craft_item"] = "craft_item"
    item_gid: int
    quantity: int = 1


class BuyItemStep(BaseModel):
    """Acheter jusqu'a quantity, en comptant le stock existant pour eviter les rachats a la reprise."""

    type: Literal["buy_item"] = "buy_item"
    item_gid: int
    max_kamas: int
    """Prix plafond d'un lot de 1."""
    quantity: int = 1
    category: CategoryItemEnum = CategoryItemEnum.RESOURCES


class EnsureItemStep(BaseModel):
    type: Literal["ensure_item"] = "ensure_item"
    item_gid: int
    quantity: int = 1


type QuestStep = Annotated[
    GoToStep
    | TalkToNpcStep
    | FightStep
    | UseInteractiveStep
    | UseMapInteractiveStep
    | CraftItemStep
    | BuyItemStep
    | EnsureItemStep,
    Field(discriminator="type"),
]


class QuestScript(BaseModel):
    name: str
    quest_id: int | None = None
    cooldown: QuestCooldown = QuestCooldown.DAILY
    level_min: int = 1
    steps: list[QuestStep]
    server_step_id_by_index: dict[int, int] = Field(default_factory=dict[int, int])
    objective_id_by_index: dict[int, int] = Field(default_factory=dict[int, int])
    objective_ids_with_untrusted_map: set[int] = Field(default_factory=set[int])
    """Objectifs dont mapId indique l'entree du batiment plutot que la map de validation."""

    @model_validator(mode="after")
    def _check_steps(self):
        if not self.steps:
            raise ValueError(f"quest script {self.name!r} has no step")
        for mapping in (self.server_step_id_by_index, self.objective_id_by_index):
            for index in mapping:
                if not 0 <= index < len(self.steps):
                    raise ValueError(
                        f"quest script {self.name!r} maps step index {index} outside of its steps"
                    )
        return self

    def index_for_server_step_id(self, step_id: int) -> int | None:
        for index, mapped_step_id in self.server_step_id_by_index.items():
            if mapped_step_id == step_id:
                return index
        return None
