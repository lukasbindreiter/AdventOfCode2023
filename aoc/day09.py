import pytest
from aocd.models import Puzzle
from math import lcm
import numpy as np
from itertools import cycle


def parse(data: str) -> list[np.ndarray]:
    return [np.fromstring(line, dtype=int, sep=' ') for line in data.strip().splitlines()]
    


def part1(reports: list[np.ndarray]) -> int:
    return sum(next_value(report) for report in reports)


def next_value(report: np.ndarray) -> int:
    if (report == 0).all():
        return 0
    
    differences = report[1:] - report[:-1]
    next_difference = next_value(differences)
    return report[-1] + next_difference


def part2(reports: list[np.ndarray]) -> int:
    return part1([report[::-1] for report in reports])



@pytest.fixture()
def puzzle_input():
    return parse(Puzzle(2023, 9).input_data)


@pytest.fixture()
def example_input():
    return parse(
        """
0 3 6 9 12 15
1 3 6 10 15 21
10 13 16 21 30 45
    """.strip()
    )


def test_part1(puzzle_input):
    assert part1(puzzle_input) == 1938731307


def test_example_part1(example_input):
    assert part1(example_input) == 114


def test_part2(puzzle_input):
    assert part2(puzzle_input) == 948



def test_example_part2(example_input):
    assert part2(example_input) == 2
