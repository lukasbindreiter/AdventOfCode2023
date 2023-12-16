from collections.abc import Iterator
import pytest
from aocd.models import Puzzle
import numpy as np

UP = -1
DOWN = 1
LEFT = -1j
RIGHT = 1j


def parse(data: str) -> np.ndarray:
    return np.array([list(l) for l in data.strip().splitlines()])


def part1(grid: np.ndarray) -> int:
    return calc_energized(grid, 0 + 0j, RIGHT)


def calc_energized(
    grid: np.ndarray, start_beam: complex, start_direction: complex
) -> int:
    energized = np.zeros_like(grid, dtype=bool)
    trace([(start_beam, start_direction)], grid, energized)

    return energized.sum()


def trace(
    beams: list[tuple[complex, complex]], grid: np.ndarray, energized: np.ndarray
):
    height, width = grid.shape
    seen = set()
    while beams:
        # beam coordinates and directions for the next iteration
        next_beams: list[tuple[complex, complex]] = []
        for beam_pos, beam_direction in beams:
            seen.add((beam_pos, beam_direction))
            y, x = int(beam_pos.real), int(beam_pos.imag)
            if not (0 <= y < height and 0 <= x < width):  # beam out of bounds
                continue

            energized[y, x] = True

            is_left_right = beam_direction == LEFT or beam_direction == RIGHT

            if grid[y, x] == "/":
                beam_direction *= 1j if is_left_right else -1j
                next_beams.append((beam_pos + beam_direction, beam_direction))
            elif grid[y, x] == "\\":
                beam_direction *= -1j if is_left_right else 1j
                next_beams.append((beam_pos + beam_direction, beam_direction))
            elif grid[y, x] == "|" and is_left_right:
                next_beams.append((beam_pos + UP, UP))
                next_beams.append((beam_pos + DOWN, DOWN))
            elif grid[y, x] == "-" and not is_left_right:
                next_beams.append((beam_pos + LEFT, LEFT))
                next_beams.append((beam_pos + RIGHT, RIGHT))
            else:  # continue straight
                next_beams.append((beam_pos + beam_direction, beam_direction))

        beams = [beam for beam in next_beams if beam not in seen]

    return energized.sum()


def part2(grid: np.ndarray) -> int:
    return max(calc_energized(grid, *start_beam) for start_beam in start_beams(grid))


def start_beams(grid: np.ndarray) -> Iterator[tuple[complex, complex]]:
    height, width = grid.shape

    for row in range(height):
        yield row, RIGHT  # from left
        yield row + (width - 1) * 1j, LEFT  # from right

    for col in range(width):
        yield col * 1j, DOWN
        yield (height - 1) + col * 1j, UP


@pytest.fixture()
def puzzle_input():
    return parse(Puzzle(2023, 16).input_data)


@pytest.fixture()
def example_input():
    return parse(
        r"""
.|...\....
|.-.\.....
.....|-...
........|.
..........
.........\
..../.\\..
.-.-/..|..
.|....-|.\
..//.|....
    """.strip()
    )


def test_part1(puzzle_input):
    assert part1(puzzle_input) == 7517


def test_example_part1(example_input):
    assert part1(example_input) == 46


def test_part2(puzzle_input):
    assert part2(puzzle_input) == 7741


def test_example_part2(example_input):
    assert part2(example_input) == 51
