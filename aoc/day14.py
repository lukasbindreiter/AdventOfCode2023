from typing import Callable
import pytest
from aocd.models import Puzzle
import numpy as np


NORTH = (
    1,
    lambda rocks: sorted(rocks, key=lambda rock: rock.real, reverse=True),
)
SOUTH = (
    -1,
    lambda rocks: sorted(rocks, key=lambda rock: rock.real, reverse=False),
)
EAST = (
    1j,
    lambda rocks: sorted(rocks, key=lambda rock: rock.imag, reverse=True),
)
WEST = (
    -1j,
    lambda rocks: sorted(rocks, key=lambda rock: rock.imag, reverse=False),
)


def parse(data: str) -> np.ndarray:
    return np.array([list(l) for l in data.strip().splitlines()])


def _coords(grid: np.ndarray, value: str) -> set[complex]:
    height = grid.shape[0]
    y, x = np.where(grid == value)
    # reverse y to have our y coordinates equal the row number for load calculation
    return {complex(height - yi - 1, xi) for yi, xi in zip(y, x)}


def coords(platform: np.ndarray) -> tuple[set[complex], set[complex]]:
    # wall in our platform to avoid having to check out of bounds:
    # bonus advantage: index starts at 1, which is the value we want later for the load
    platform = np.pad(platform, 1, constant_values="#")
    return _coords(platform, "O"), _coords(platform, "#")


def part1(platform: np.ndarray) -> int:
    round_rocks, cube_rocks = coords(platform)
    round_rocks = tilt(round_rocks, cube_rocks, NORTH)
    return calc_load(round_rocks)


def part2(platform: np.ndarray) -> int:
    round_rocks, cube_rocks = coords(platform)

    cycle_start, cycle_length = find_cycle(round_rocks, cube_rocks)

    for _ in range(cycle_start):
        round_rocks = cycle(round_rocks, cube_rocks)

    remaining = 1000000000 - cycle_start
    remaining %= cycle_length

    for _ in range(remaining):
        round_rocks = cycle(round_rocks, cube_rocks)

    return calc_load(round_rocks)


def cycle(round_rocks: set[complex], cube_rocks: set[complex]) -> set[complex]:
    round_rocks = tilt(round_rocks, cube_rocks, NORTH)
    round_rocks = tilt(round_rocks, cube_rocks, WEST)
    round_rocks = tilt(round_rocks, cube_rocks, SOUTH)
    round_rocks = tilt(round_rocks, cube_rocks, EAST)
    return round_rocks


def find_cycle(round_rocks: set[complex], cube_rocks: set[complex]) -> tuple[int, int]:
    cycles = 0
    seen_states: dict[int, int] = {rock_hash(round_rocks): cycles}
    while True:
        round_rocks = cycle(round_rocks, cube_rocks)
        cycles += 1

        current_hash = rock_hash(round_rocks)
        if current_hash in seen_states:
            cycle_start = seen_states[current_hash]
            cycle_length = cycles - cycle_start
            return cycle_start, cycle_length

        seen_states[current_hash] = cycles

    return 0, 0


def tilt(
    round_rocks: set[complex],
    cube_rocks: set[complex],
    direction: tuple[complex, Callable[[set[complex]], list[complex]]],
) -> set[complex]:
    direction_vector, sort_function = direction

    moved_any = True

    while moved_any:
        moved_any = False
        moved_round_rocks = set()
        for rock in sort_function(round_rocks):
            # check if we can move this rock (no collision)
            new_position = rock + direction_vector
            if new_position not in cube_rocks and new_position not in moved_round_rocks:
                rock = new_position
                moved_any = True
            moved_round_rocks.add(rock)
        round_rocks = moved_round_rocks

    return round_rocks


def calc_load(rocks: set[complex]) -> int:
    return int(sum(rock.real for rock in rocks))


def rock_hash(rocks: set[complex]) -> int:
    return hash(tuple((int(rock.real), int(rock.imag)) for rock in rocks))


@pytest.fixture()
def puzzle_input():
    return parse(Puzzle(2023, 14).input_data)


@pytest.fixture()
def example_input():
    return parse(
        """
O....#....
O.OO#....#
.....##...
OO.#O....O
.O.....O#.
O.#..O.#.#
..O..#O..O
.......O..
#....###..
#OO..#....
    """.strip()
    )


@pytest.fixture()
def example_input2():
    return parse(
        """
.....#....
....#....#
.....##...
...#......
........#.
..#....#.#
.....#....
..........
#....###..
#....#....
    """.strip()
    )


def test_part1(puzzle_input):
    assert part1(puzzle_input) == 109665


def test_example_part1(example_input):
    assert part1(example_input) == 136


def test_part2(puzzle_input):
    assert part2(puzzle_input) == 96061


def test_example_part2(example_input):
    assert part2(example_input) == 64
