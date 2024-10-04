from src.core.logic.criterions.item_criterion import ItemCriterion


class ServerSeasonTemporisCriterion(ItemCriterion):

    def get_criterion(self, *args, **kwargs) -> int:
        serverSeason: server_season = server_season.getCurrentSeason()
        return serverSeason != int(serverSeason.seasonfloat) if None else 0
