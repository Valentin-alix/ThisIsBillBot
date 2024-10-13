from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, Iterator, TypeVar

import sortedcontainers

T = TypeVar("T")


class Node(Generic[T]):
    __slots__ = (
        "parent",
        "data",
        "cost_to_node",
        "total_cost",
        "closed",
        "in_open_set",
    )

    def __init__(
        self,
        data: T,
        parent: "Node[T]|None" = None,
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

    def __eq__(self, value: Any) -> bool:
        return isinstance(value, Node) and self.data == value.data

    def __hash__(self) -> int:
        return self.data.__hash__()

    def __lt__(self, other: "Node[T]") -> bool:
        return self.total_cost < other.total_cost


class SearchNodeDict(dict[T, Node[T]]):
    def __missing__(self, key) -> Node[T]:
        value = Node(data=key)
        self.__setitem__(key, value)
        return value


SNType = TypeVar("SNType", bound=Node)


class OpenSet(Generic[SNType]):
    def __init__(self) -> None:
        self.sorted_list = sortedcontainers.SortedList(key=lambda x: x.total_cost)

    def push(self, item: SNType) -> None:
        item.in_open_set = True
        self.sorted_list.add(item)

    def pop(self) -> SNType:
        item = self.sorted_list.pop(0)
        item.in_open_set = False
        return item

    def remove(self, item: SNType) -> None:
        self.sorted_list.remove(item)
        item.in_open_set = False

    def __len__(self) -> int:
        return len(self.sorted_list)


class Astar(ABC, Generic[T]):
    __slots__ = ()

    @abstractmethod
    def get_neighbors(self, data: T) -> Iterator["T"]: ...

    @abstractmethod
    def get_dist(self, current: T, ends: "set[T]") -> float: ...

    def reconstruct_path(self, node: Node[T], do_reverse: bool) -> list:
        def iter_path():
            current: Node[T] | None = node
            path: list[T] = []
            while current:
                path.append(current.data)
                current = current.parent
            return path

        if do_reverse:
            return iter_path()
        else:
            return iter_path()[::-1]

    def is_goal_reached(self, current: T, ends: set[T]) -> bool:
        return current in ends

    def find_path(
        self,
        start: T,
        ends: set[T],
        heuristic_scale: float = 1,
        do_reverse: bool = False,
        max_iteration: int = 9999,
    ) -> list | None:
        open_set: OpenSet[Node[T]] = OpenSet()

        start_node: Node[T] = Node(
            data=start, cost_to_node=0, total_cost=self.get_dist(start, ends)
        )

        search_node_dict = SearchNodeDict()
        search_node_dict[start] = start_node
        open_set.push(start_node)

        iteration = 0
        while open_set and iteration <= max_iteration:
            iteration += 1
            current_node = open_set.pop()
            if self.is_goal_reached(current_node.data, ends):
                return self.reconstruct_path(current_node, do_reverse)

            current_node.closed = True

            for node in (
                search_node_dict[data] for data in self.get_neighbors(current_node.data)
            ):
                if node.closed:
                    continue
                cost_to_node = current_node.cost_to_node + self.get_dist(
                    current_node.data, {node.data}
                )
                if cost_to_node >= node.cost_to_node:
                    continue

                if node.in_open_set:
                    open_set.remove(node)

                node.parent = current_node
                node.cost_to_node = cost_to_node
                node.total_cost = (
                    cost_to_node + self.get_dist(node.data, ends) * heuristic_scale
                )

                open_set.push(node)

        return None


U = TypeVar("U")


def find_path(
    start: U,
    ends: set[U],
    get_neighbors_func: Callable[[U], Iterator[U]],
    distance_between_func: Callable[[U, set[U]], float],
    is_goal_reached_func: Callable[[U, set[U]], bool] = lambda curr, ends: curr in ends,
    do_reverse: bool = False,
) -> list[U] | None:
    """A non-class version of the path finding algorithm"""

    class FindPath(Astar):
        def get_dist(self, node: U, other_node: set[U]) -> float:
            return distance_between_func(node, other_node)

        def get_neighbors(self, node: U) -> Iterator[U]:
            return get_neighbors_func(node)

        def is_goal_reached(self, current: U, ends: set[U]) -> bool:
            return is_goal_reached_func(current, ends)

    return FindPath().find_path(start, ends, do_reverse)
