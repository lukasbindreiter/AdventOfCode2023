from collections import defaultdict
from functools import cache
import pytest
from aocd.models import Puzzle


def parse(data: str) -> list[str]:
    return data.strip().split(",")


def part1(lens: list[str]) -> int:
    return sum(calc_hash(l) for l in lens)


@cache
def calc_hash(s: str) -> int:
    value = 0
    for ch in s:
        value += ord(ch)
        value *= 17
        value %= 256
    return value


def part2(lenses) -> int:
    # fortunately, python dicts preserve insertion order
    # so, let's use a hashmap to implement a hashmap
    boxes: dict[int, dict[str, int]] = defaultdict(dict)

    for op in lenses:
        if "-" in op:
            lens = op[:-1]
            box = calc_hash(lens)
            if lens in boxes[box]:
                del boxes[box][lens]
        else:
            assert "=" in op
            lens, focal_length = op.split("=")
            box = calc_hash(lens)
            boxes[box][lens] = int(focal_length)

    print(boxes)

    return calc_focusing_power(boxes)


def calc_focusing_power(boxes: dict[int, dict[str, int]]) -> int:
    focusing_power = 0
    for box, lenses in boxes.items():
        for slot, focal_length in enumerate(lenses.values()):
            focusing_power += (box + 1) * (slot + 1) * focal_length

    return focusing_power


@pytest.fixture()
def puzzle_input():
    return parse(Puzzle(2023, 15).input_data)


@pytest.fixture()
def example_input():
    return parse(
        """
rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7
    """.strip()
    )


def test_part1(puzzle_input):
    assert part1(puzzle_input) == 505459


def test_example_part1(example_input):
    assert part1(example_input) == 1320


def test_part2(puzzle_input):
    assert part2(puzzle_input) == 228508


def test_example_part2(example_input):
    assert part2(example_input) == 145
