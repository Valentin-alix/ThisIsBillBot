from dataclasses import dataclass


@dataclass
class Entity[T]:
    cell_id: int
    entity: T
