from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int

    def distance_to_point(self, point: "Point") -> float:
        return abs(self.x - point.x) + abs(self.y - point.y)
