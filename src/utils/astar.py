from __future__ import annotations

from abc import ABC, abstractmethod
from bisect import insort
from collections.abc import Iterator
from typing import Generic, Protocol, TypeVar, cast

T = TypeVar("T")
PathResultT = TypeVar("PathResultT")


class Node(Generic[T]):
    __slots__ = (
        "parent",
        "data",
        "cost_to_node",
        "total_cost",
        "closed",
        "in_open_set",
    )

    parent: Node[T] | None
    data: T
    cost_to_node: float
    total_cost: float
    closed: bool
    in_open_set: bool

    def __init__(
        self,
        data: T,
        parent: Node[T] | None = None,
        cost_to_node: float = float("inf"),
        total_cost: float = float("inf"),
        closed: bool = False,
        in_open_set: bool = False,
    ) -> None:
        self.parent = parent
        self.data = data
        self.cost_to_node = cost_to_node
        self.total_cost = total_cost
        self.closed = closed
        self.in_open_set = in_open_set

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return False
        other_node = cast(Node[T], other)
        return self.data == other_node.data

    def __hash__(self) -> int:
        return hash(self.data)

    def __lt__(self, other: Node[T]) -> bool:
        return self.total_cost < other.total_cost


class SearchNodeDict(dict[T, Node[T]]):
    def __missing__(self, key: T) -> Node[T]:
        value = Node(data=key)
        self[key] = value
        return value


class OpenSet(Generic[T]):
    def __init__(self) -> None:
        self.sorted_list: list[Node[T]] = []

    def push(self, item: Node[T]) -> None:
        item.in_open_set = True
        insort(self.sorted_list, item)

    def pop(self) -> Node[T]:
        item = self.sorted_list.pop(0)
        item.in_open_set = False
        return item

    def remove(self, item: Node[T]) -> None:
        self.sorted_list.remove(item)
        item.in_open_set = False

    def __len__(self) -> int:
        return len(self.sorted_list)

    def __bool__(self) -> bool:
        return bool(self.sorted_list)


class Astar(ABC, Generic[T, PathResultT]):
    __slots__ = ()

    @abstractmethod
    def get_neighbors(self, data: T) -> Iterator[T]:
        raise NotImplementedError

    @abstractmethod
    def get_dist(self, current: T, ends: set[T]) -> float:
        raise NotImplementedError

    @abstractmethod
    def reconstruct_path(self, node: Node[T], do_reverse: bool) -> list[PathResultT]:
        raise NotImplementedError

    def is_goal_reached(self, current: T, ends: set[T]) -> bool:
        return current in ends

    def find_path(
        self,
        start: T,
        ends: set[T],
        heuristic_scale: float = 1,
        do_reverse: bool = False,
        max_iteration: int = 9999,
    ) -> list[PathResultT] | None:
        open_set: OpenSet[T] = OpenSet()

        start_node = Node(
            data=start,
            cost_to_node=0,
            total_cost=self.get_dist(start, ends),
        )

        search_node_dict = SearchNodeDict[T]()
        search_node_dict[start] = start_node
        open_set.push(start_node)

        iteration = 0
        while open_set and iteration <= max_iteration:
            iteration += 1
            current_node = open_set.pop()
            if self.is_goal_reached(current_node.data, ends):
                return self.reconstruct_path(current_node, do_reverse)

            current_node.closed = True

            for node in (search_node_dict[data] for data in self.get_neighbors(current_node.data)):
                if node.closed:
                    continue

                try:
                    cost_to_node = current_node.cost_to_node + self.get_dist(
                        current_node.data,
                        {node.data},
                    )
                except KeyError:
                    continue

                if cost_to_node >= node.cost_to_node:
                    continue

                if node.in_open_set:
                    open_set.remove(node)

                node.parent = current_node
                node.cost_to_node = cost_to_node
                node.total_cost = cost_to_node + self.get_dist(node.data, ends) * heuristic_scale

                open_set.push(node)

        return None


class DataAstar(Astar[T, T], ABC):
    def reconstruct_path(self, node: Node[T], do_reverse: bool) -> list[T]:
        current: Node[T] | None = node
        path: list[T] = []

        while current is not None:
            path.append(current.data)
            current = current.parent

        if do_reverse:
            return path
        return path[::-1]


PathT = TypeVar("PathT")
CallablePathT = TypeVar("CallablePathT")


def _default_is_goal_reached(current: PathT, ends: set[PathT]) -> bool:
    return current in ends


class NeighborProvider(Protocol[T]):
    def __call__(self, node: T) -> Iterator[T]: ...


class DistanceProvider(Protocol[T]):
    def __call__(self, current: T, ends: set[T]) -> float: ...


class GoalReachedProvider(Protocol[T]):
    def __call__(self, current: T, ends: set[T]) -> bool: ...


class _CallableAstar(DataAstar[CallablePathT]):
    def __init__(
        self,
        get_neighbors_func: NeighborProvider[CallablePathT],
        distance_between_func: DistanceProvider[CallablePathT],
        is_goal_reached_func: GoalReachedProvider[CallablePathT],
    ) -> None:
        self._get_neighbors_func = get_neighbors_func
        self._distance_between_func = distance_between_func
        self._is_goal_reached_func = is_goal_reached_func

    def get_dist(self, current: CallablePathT, ends: set[CallablePathT]) -> float:
        return self._distance_between_func(current, ends)

    def get_neighbors(self, data: CallablePathT) -> Iterator[CallablePathT]:
        return self._get_neighbors_func(data)

    def is_goal_reached(self, current: CallablePathT, ends: set[CallablePathT]) -> bool:
        return self._is_goal_reached_func(current, ends)


def find_path(
    start: PathT,
    ends: set[PathT],
    get_neighbors_func: NeighborProvider[PathT],
    distance_between_func: DistanceProvider[PathT],
    is_goal_reached_func: GoalReachedProvider[PathT] = _default_is_goal_reached,
    do_reverse: bool = False,
) -> list[PathT] | None:
    """A non-class version of the path finding algorithm."""
    astar = _CallableAstar(
        get_neighbors_func,
        distance_between_func,
        is_goal_reached_func,
    )
    return astar.find_path(start, ends, do_reverse=do_reverse)
