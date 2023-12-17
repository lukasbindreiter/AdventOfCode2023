from queue import PriorityQueue
import pytest
from aocd.models import Puzzle
import numpy as np
from dataclasses import field, dataclass


def parse(data: str) -> np.ndarray:
    return np.array([list(l) for l in data.strip().splitlines()]).astype(int)


def part1(grid: np.ndarray) -> int:
    return minimum_heat_loss(grid)


@dataclass(order=True)
class CityBlock:
    min_heat_loss: int
    pos: tuple[int, int] = field(compare=False)
    direction: int = field(compare=False)  # 1 = up/down, -1 = left/right
    prev: "CityBlock | None" = field(compare=False, default=None)


def minimum_heat_loss(
    grid: np.ndarray, min_straight: int = 1, max_straight: int = 3
) -> int:
    height, width = grid.shape
    target = (height - 1, width - 1)

    # dijkstra using below priority queue
    # instead of keeping track of the number of steps since the last turn, each state
    # transition is a turn. And each state can transition to multiple states, taking
    # between (min_straight, max_straight) steps in a straight line perpendicular to the
    # previous direction

    states = PriorityQueue()
    states.put(CityBlock(0, (0, 0), 1))  # start at the top left corner, facing down
    states.put(CityBlock(0, (0, 0), -1))  # or facing right

    visited = set()

    while not states.empty():
        state = states.get()
        if state.pos == target:
            return state.min_heat_loss

        # check if we have already visited this state before, if so skip it
        # because the previous visit must have had a lower heat loss
        if (state.pos, state.direction) in visited:
            continue
        visited.add((state.pos, state.direction))

        y, x = state.pos

        # now we either go straight up/down or left/right, depending on direction
        # to avoid an if and duplicated code with swapped dimensions, we just transpose
        # the grid and state if we are facing left/right instead

        # transitions to neighboring states
        if state.direction == 1:  # current: up or down => transition to left or right
            for sign in (-1, 1):  # go straight in one direction and then the other
                sum_straight = 0
                for step in range(1, max_straight + 1):  # left and right
                    next_x = x + step * sign
                    if next_x < 0 or next_x >= width:
                        break

                    sum_straight += grid[y, next_x]
                    if step >= min_straight:
                        states.put(
                            CityBlock(
                                state.min_heat_loss + sum_straight,
                                (y, next_x),
                                state.direction * -1,
                                state,
                            )
                        )
        else:  # current left or right => transition to up or down
            for sign in (-1, 1):  # go straight in one direction and then the other
                sum_straight = 0
                for step in range(1, max_straight + 1):  # left and right
                    next_y = y + step * sign
                    if next_y < 0 or next_y >= height:
                        break

                    sum_straight += grid[next_y, x]
                    if step >= min_straight:
                        states.put(
                            CityBlock(
                                state.min_heat_loss + sum_straight,
                                (next_y, x),
                                state.direction * -1,
                                state,
                            )
                        )

    return -1


def part2(grid: np.ndarray) -> int:
    return minimum_heat_loss(grid, 4, 10)


@pytest.fixture()
def puzzle_input():
    return parse(Puzzle(2023, 17).input_data)


@pytest.fixture()
def example_input():
    return parse(
        """
2413432311323
3215453535623
3255245654254
3446585845452
4546657867536
1438598798454
4457876987766
3637877979653
4654967986887
4564679986453
1224686865563
2546548887735
4322674655533
    """.strip()
    )


def test_part1(puzzle_input):
    assert part1(puzzle_input) == 665


def test_example_part1(example_input):
    assert part1(example_input) == 102


def test_part2(puzzle_input):
    assert part2(puzzle_input) == 809


def test_example_part2(example_input):
    assert part2(example_input) == 94
