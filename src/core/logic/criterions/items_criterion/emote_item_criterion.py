from src.core.logic.criterions.item_criterion import ItemCriterion


class EmoteItemCriterion(ItemCriterion):
    def get_emotes_list(self) -> list:
        emoticonFrame: EmoticonFrame = Kernel().worker.getFrame("EmoticonFrame")
        if emoticonFrame:
            return emoticonFrame.emotesList
        return None

    def is_respected(self, *args, **kwargs) -> bool:
        emote_wrapper: EmoteWrapper = None
        for emote_wrapper in self.get_emotes_list():
            if emote_wrapper.emote.id == self.criterion_value:
                return False
        return True

    def get_criterion(self, *args, **kwargs) -> int:
        id: int = 0
        for id in self.get_emotes_list():
            if id == self.criterion_value:
                return 1
        return 0
