from src.core.engine.fights.zones.z_rectangle import ZRectangle


class Square(ZRectangle):
    def __init__(self, min_radius: int, size: int, is_diagonal_free: bool):
        super().__init__(
            min_radius=min_radius,
            alternative_size=size,
            size=size,
            is_diagonal_free=is_diagonal_free,
        )
