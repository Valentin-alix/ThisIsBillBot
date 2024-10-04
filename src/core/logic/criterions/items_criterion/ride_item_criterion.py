from src.core.logic.criterions.item_criterion import ItemCriterion


class RideItemCriterion(ItemCriterion):
    def get_criterion(self, *args, **kwargs) -> int:
        mount_id: int = 0
        mount: MountData = PlayedCharacterManager().mount
        if mount and PlayedCharacterManager().isRidding:
            mount_id = mount.modelId
        return mount_id
