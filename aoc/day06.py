import pytest
from aocd.models import Puzzle
import re
import numpy as np
from numba import jit


def numbers(text: str) -> list[int]:
    return list(map(int, re.findall(r"\d+", text)))


def parse(data: str) -> tuple[list[int], list[int]]:
    times, distances = data.strip().split("\n")
    return numbers(times), numbers(distances)


@jit(nopython=True)
def _count_wins_bruteforce(time: int, distance: int) -> int:
    wins = 0
    for hold in range(1, time):  # no need to check outcomes with 0
        if (time - hold) * hold > distance:
            wins += 1
    return wins


def _count_wins(time: int, distance: int) -> int:
    """
    We want to solve for:

    (time - hold) * hold = distance
    time * hold - hold^2 = distance
    hold^2 - time * hold + distance = 0

    is the same as:

    x^2 + p*x + q = 0
    with:
      x = hold
      p = -time
      q = distance

    solving for x:

    x1,2 = -(p/2) +- sqrt((p/2)^2 - q)
    """

    p_half = -time / 2
    q = distance

    x_1 = -p_half + np.sqrt(p_half**2 - q)
    x_2 = -p_half - np.sqrt(p_half**2 - q)

    min_hold = int(np.ceil(x_2 + 0.01))  # round up
    max_hold = int(np.floor(x_1 - 0.01))  # round down

    return max_hold - min_hold + 1


def part1(times: list[int], distances: list[int]) -> int:
    return np.prod([_count_wins(time, dist) for time, dist in zip(times, distances)])


def part2(times: list[int], distances: list[int]) -> int:
    time = int("".join(map(str, times)))
    distance = int("".join(map(str, distances)))
    # brute force for the win
    return _count_wins(time, distance)


@pytest.fixture()
def puzzle_input():
    return parse(Puzzle(2023, 6).input_data)


@pytest.fixture()
def example_input():
    return parse(
        """
Time:      7  15   30
Distance:  9  40  200
    """.strip()
    )


def test_part1(puzzle_input):
    assert part1(*puzzle_input) == 1159152


def test_example_part1(example_input):
    assert part1(*example_input) == 288


def test_part2(puzzle_input):
    assert part2(*puzzle_input) == 41513103


def test_example_part2(example_input):
    assert part2(*example_input) == 71503
