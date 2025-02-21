from datas.protos.non_obf.game.common_pb2 import InteractiveElement

from src.core.engine.interactives.collectable import Collectable


def make_interactive_element(
    skill_id: int,
    on_current_map: bool = True,
    element_id: int = 10,
) -> InteractiveElement:
    return InteractiveElement(
        element_id=element_id,
        on_current_map=on_current_map,
        enabled_skills=[
            InteractiveElement.InteractiveElementSkill(skill_id=skill_id),
        ],
    )


def make_collectable(element_id: int) -> Collectable:
    return Collectable(
        map_id=1,
        interactive_element=InteractiveElement(
            element_id=element_id,
            element_type_id=1,
        ),
        skill=InteractiveElement.InteractiveElementSkill(
            skill_id=1,
            skill_instance_uid=1,
        ),
        resource_item_id=1,
    )
