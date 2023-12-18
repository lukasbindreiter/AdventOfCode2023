import pytest
from aocd.models import Puzzle


def parse(data: str) -> list[tuple[str, int, str]]:
    lines = data.splitlines()
    plan = [line.split(" ") for line in lines]
    return [
        (direction, int(num), hex_value.lstrip("(#").rstrip(")"))
        for direction, num, hex_value in plan
    ]


def part1(plan: list[tuple[str, int, str]]) -> int:
    directions = {
        "R": (0, 1),
        "L": (0, -1),
        "U": (-1, 0),
        "D": (1, 0),
    }
    return calc_area([(directions[direction], num) for direction, num, _ in plan])


def calc_area(plan: list[tuple[tuple[int, int], int]]) -> int:
    # apparently we can use the shoelace formula to calculate the area of a polygon
    # given its vertices
    # however in our grid case, we need to account for the perimeter as well, since the
    # vertices are actually the center points of 1x1 squares
    # to correct for this we can use pick's theorem

    perimeter, shoelace = 0, 0

    # shoelace formula
    y1, x1 = 0, 0
    for (dy, dx), n in plan:
        y2, x2 = y1 + dy * n, x1 + dx * n
        perimeter += abs(y2 - y1) + abs(x2 - x1)
        shoelace += x1 * y2 - y1 * x2
        y1, x1 = y2, x2

    shoelace_area: float = abs(shoelace) / 2

    area = shoelace_area + perimeter / 2 + 1  # pick's theorem
    return int(area)


def part2(plan: list[tuple[str, int, str]]) -> int:
    directions = {
        0: (0, 1),  # right
        1: (1, 0),  # down
        2: (0, -1),  # left
        3: (-1, 0),  # up
    }
    return calc_area(
        [
            (directions[int(hex_value[5])], int(hex_value[:5], 16))
            for _, _, hex_value in plan
        ]
    )


@pytest.fixture()
def puzzle_input():
    return parse(Puzzle(2023, 18).input_data)


@pytest.fixture()
def example_input():
    return parse(
        """
R 6 (#70c710)
D 5 (#0dc571)
L 2 (#5713f0)
D 2 (#d2c081)
R 2 (#59c680)
D 2 (#411b91)
L 5 (#8ceee2)
U 2 (#caa173)
L 1 (#1b58a2)
U 2 (#caa171)
R 2 (#7807d2)
U 3 (#a77fa3)
L 2 (#015232)
U 2 (#7a21e3)
    """.strip()
    )


def test_part1(puzzle_input):
    assert part1(puzzle_input) == 38188


def test_example_part1(example_input):
    assert part1(example_input) == 62


def test_part2(puzzle_input):
    assert part2(puzzle_input) == 93325849869340


def test_example_part2(example_input):
    assert part2(example_input) == 952408144115
