import pytest
from aocd.models import Puzzle
import numpy as np


def parse(data: str) -> np.ndarray:
    return np.array([list(l) for l in data.strip().splitlines()])


def part1(universe: np.ndarray, expand_to: int = 2) -> int:
    galaxies_y, galaxies_x = np.where(universe == "#")
    galaxies_y = expand(galaxies_y, expand_to)
    galaxies_x = expand(galaxies_x, expand_to)

    coords = np.stack([galaxies_y, galaxies_x], axis=1).reshape(1, -1, 2)
    coords_b = coords.reshape(-1, 1, 2)

    distances = np.abs(coords - coords_b).sum(axis=2)
    distances = np.triu(distances, k=1)
    return distances.sum()


def expand(coords: np.ndarray, to: int = 2) -> np.ndarray:
    unique = set(coords)
    # loop from max to 0 to be able to immediately update the coords
    for i in range(max(unique), -1, -1):
        if i not in unique:
            coords[coords > i] += to - 1  # its already 1 large, so -1

    return coords


def part2(universe: np.ndarray, expand_to: int = 1000000) -> int:
    return part1(universe, expand_to)


@pytest.fixture()
def puzzle_input():
    return parse(Puzzle(2023, 11).input_data)


@pytest.fixture()
def example_input():
    return parse(
        """
...#......
.......#..
#.........
..........
......#...
.#........
.........#
..........
.......#..
#...#.....
    """.strip()
    )


def test_part1(puzzle_input):
    assert part1(puzzle_input) == 10276166


def test_example_part1(example_input):
    assert part1(example_input) == 374


def test_part2(puzzle_input):
    assert part2(puzzle_input) == 598693078798


def test_example_part2(example_input):
    assert part2(example_input, 10) == 1030
    assert part2(example_input, 100) == 8410
    assert part2(example_input) == 82000210
