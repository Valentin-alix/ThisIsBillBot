from pydantic import BaseModel


class RuneSchema(BaseModel):
    quantity: int
    name: str


class StatSchema(BaseModel):
    name: str
    weight: int
    runes: list[RuneSchema]


class LineSchema(BaseModel):
    value: int
    stat: StatSchema


class EquipmentSchema(BaseModel):
    item_id: int
    lines: list[LineSchema]
