import unittest
from typing import Iterator

from src.utils.astar import Astar, find_path


class LineAstar(Astar[int]):
    def get_neighbors(self, data: int) -> Iterator[int]:
        if data < 3:
            yield data + 1

    def get_dist(self, current: int, ends: set[int]) -> float:
        return min(abs(current - end) for end in ends)


class TestAstar(unittest.TestCase):
    def test_find_path_helper_honors_do_reverse(self) -> None:
        def get_neighbors(node: int) -> Iterator[int]:
            if node < 3:
                yield node + 1

        def get_distance(current: int, ends: set[int]) -> float:
            return min(abs(current - end) for end in ends)

        path = find_path(
            1,
            {3},
            get_neighbors,
            get_distance,
            do_reverse=True,
        )

        self.assertEqual(path, [3, 2, 1])

    def test_find_path_helper_returns_none_when_unreachable(self) -> None:
        def get_neighbors(node: int) -> Iterator[int]:
            del node
            yield from ()

        def get_distance(current: int, ends: set[int]) -> float:
            return min(abs(current - end) for end in ends)

        path = find_path(1, {3}, get_neighbors, get_distance)

        self.assertIsNone(path)
