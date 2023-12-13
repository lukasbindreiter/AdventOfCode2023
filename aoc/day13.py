import pytest
from aocd.models import Puzzle
import numpy as np


def parse(data: str) -> list[np.ndarray]:
    patterns = data.split("\n\n")
    return [np.array([list(l) for l in pattern.splitlines()]) for pattern in patterns]


def part1(patterns: list[np.ndarray]) -> int:
    return sum(find_reflection(pattern) for pattern in patterns)


def find_reflection(pattern: np.ndarray, smudge: int = 0) -> int:
    column = find_vertical_line_reflection(pattern, smudge)
    if column:
        return column

    row = find_vertical_line_reflection(pattern.T, smudge)
    if row:
        return row * 100

    raise ValueError("No reflection found")


def find_vertical_line_reflection(pattern: np.ndarray, smudge: int = 0) -> int | None:
    for i in range(1, pattern.shape[1]):  # try all possible columns as reflection line
        left = pattern[:, :i]
        right = pattern[:, i:]
        left = left[:, ::-1]  # mirror left side
        # now make sure both sides have the same width
        cropped_width = min(left.shape[1], right.shape[1])
        left = left[:, :cropped_width]
        right = right[:, :cropped_width]

        unequal = (left != right).sum()  # check how many pixels are different
        if unequal == smudge:  # if that equals the smudge, we found a reflection
            return i

    return None


def part2(patterns: list[np.ndarray]) -> int:
    return sum(find_reflection(pattern, smudge=1) for pattern in patterns)


@pytest.fixture()
def puzzle_input():
    return parse(Puzzle(2023, 13).input_data)


@pytest.fixture()
def example_input():
    return parse(
        """
#.##..##.
..#.##.#.
##......#
##......#
..#.##.#.
..##..##.
#.#.##.#.

#...##..#
#....#..#
..##..###
#####.##.
#####.##.
..##..###
#....#..#
    """.strip()
    )


def test_part1(puzzle_input):
    assert part1(puzzle_input) == 42974


def test_example_part1(example_input):
    assert part1(example_input) == 405


def test_part2(puzzle_input):
    assert part2(puzzle_input) == 27587


def test_example_part2(example_input):
    assert part2(example_input) == 400
