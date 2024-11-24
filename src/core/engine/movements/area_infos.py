from d3_database.data_center.data_reader import DataReader
from d3_database.data_center.i18n import I18N
from pydantic import BaseModel


class AreaInfo(BaseModel):
    area_id: int
    sub_area_id: int | None = None
    min_lvl: int = 1
    waypoint_id_needed: int | None = None

    def __str__(self) -> str:
        area_name = I18N().name_by_id[DataReader().area_by_id[self.area_id].nameId]
        if self.sub_area_id:
            sub_area_name = I18N().name_by_id[
                DataReader().sub_area_by_id[self.sub_area_id].nameId
            ]
        else:
            sub_area_name = ""
        return f"{area_name} sub : {sub_area_name}"

    def __hash__(self) -> int:
        return (self.area_id, self.sub_area_id).__hash__()

    def __repr__(self) -> str:
        return super().__str__()
