import pytest
from aocd.models import Puzzle
from math import lcm
from itertools import cycle


def parse(data: str) -> tuple[list[int], dict[str, tuple[str, str]]]:
    parts = data.strip().split("\n\n")
    sequence = ["LR".index(char) for char in parts[0]]

    network = {}
    for line in parts[1].splitlines():
        source = line[:3]
        dest_left = line[7:10]
        dest_right = line[12:15]
        network[source] = dest_left, dest_right

    return sequence, network


def part1(turns: list[int], network: dict[str, tuple[str, str]]) -> int:
    return count_steps("AAA", turns, network)


def part2(turns: list[int], network: dict[str, tuple[str, str]]) -> int:
    start_nodes = [node for node in network if node.endswith("A")]
    steps = [count_steps(node, turns, network, all_z=False) for node in start_nodes]
    return lcm(*steps)


def count_steps(
    node: str, turns: list[int], network: dict[str, tuple[str, str]], all_z: bool = True
) -> int:
    target = (lambda n: n == "ZZZ") if all_z else (lambda n: n.endswith("Z"))
    for i, turn in enumerate(cycle(turns), start=1):
        node = network[node][turn]
        if target(node):
            return i
    return -1  # cycle is already an endless loop


@pytest.fixture()
def puzzle_input():
    return parse(Puzzle(2023, 8).input_data)


@pytest.fixture()
def example_input():
    return parse(
        """
LLR

AAA = (BBB, BBB)
BBB = (AAA, ZZZ)
ZZZ = (ZZZ, ZZZ)
    """.strip()
    )


def test_part1(puzzle_input):
    assert part1(*puzzle_input) == 19631


def test_example_part1(example_input):
    assert part1(*example_input) == 6


def test_part2(puzzle_input):
    assert part2(*puzzle_input) == 21003205388413


@pytest.fixture()
def example_input_2():
    return parse(
        """
LR

11A = (11B, XXX)
11B = (XXX, 11Z)
11Z = (11B, XXX)
22A = (22B, XXX)
22B = (22C, 22C)
22C = (22Z, 22Z)
22Z = (22B, 22B)
XXX = (XXX, XXX)
    """.strip()
    )


def test_example_part2(example_input_2):
    assert part2(*example_input_2) == 6
