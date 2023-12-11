import pytest
from aocd.models import Puzzle
import numpy as np
import math

NORTH = -1
SOUTH = 1
WEST = -1j
EAST = 1j

PIPES = {
    "|": (NORTH, SOUTH),
    "-": (EAST, WEST),
    "L": (NORTH, EAST),
    "J": (NORTH, WEST),
    "7": (SOUTH, WEST),
    "F": (SOUTH, EAST),
}


def parse(data: str) -> np.ndarray:
    return np.array([list(l) for l in data.strip().splitlines()])


def part1(grid: np.ndarray) -> int:
    y, x = np.where(grid == "S")
    start_pos = y.item() + x.item() * 1j

    loop_start, loop_end = list(connected_neighbours_4(grid, start_pos))
    pipe_forward = trace_pipe(grid, loop_start, start_pos, loop_end)
    return math.ceil(len(pipe_forward) / 2)


def neighbours_4(grid: np.ndarray, pos: complex):
    height, width = grid.shape
    for direction in [-1, 1j, 1, -1j]:
        neighbour = pos + direction
        y, x = int(neighbour.real), int(neighbour.imag)
        if y >= 0 and y < height and x >= 0 and x < width:
            symbol = grid[y, x].item()
            if symbol in PIPES:
                yield neighbour, symbol


def connected_neighbours_4(grid: np.ndarray, pos: complex):
    """Find the starting neighbours for a position, e.g. any adjacent pipes
    connected to the given position
    """
    for neighbour, symbol in neighbours_4(grid, pos):
        direction = pos - neighbour
        if direction in PIPES[symbol]:
            yield neighbour


def trace_pipe(
    grid: np.ndarray, pos: complex, prev_pos: complex, stop_at: complex
) -> list[complex]:
    pipe = [pos]

    while pos != stop_at:
        direction = prev_pos - pos
        y, x = int(pos.real), int(pos.imag)
        symbol = grid[y, x].item()
        pipe_type = PIPES[symbol]
        assert direction in pipe_type
        next_direction = pipe_type[0] if direction == pipe_type[1] else pipe_type[1]

        prev_pos = pos
        pos = prev_pos + next_direction

        pipe.append(pos)

    return pipe


def part2(grid: np.ndarray) -> int:
    y, x = np.where(grid == "S")
    start_pos = y.item() + x.item() * 1j

    loop_start, loop_end = list(connected_neighbours_4(grid, start_pos))
    pipe = [start_pos] + trace_pipe(grid, loop_start, start_pos, loop_end)

    # replace the S symbol with the correct symbol
    by_directions = {dirs: symbol for symbol, dirs in PIPES.items()}
    try:
        start_symbol = by_directions[(loop_start - start_pos, loop_end - start_pos)]
    except KeyError:
        start_symbol = by_directions[(loop_end - start_pos, loop_start - start_pos)]
    grid[int(start_pos.real), int(start_pos.imag)] = start_symbol

    # now count how many F L and - pipes are north of each position
    # wherever this is odd, we have an enclosed area
    pipe_grid = np.zeros(shape=grid.shape, dtype=int)
    northern_crossings = np.zeros(shape=grid.shape, dtype=int)
    for pos in pipe:
        pipe_grid[int(pos.real), int(pos.imag)] = 1
        if grid[int(pos.real), int(pos.imag)] in "FL-":
            northern_crossings[int(pos.real), int(pos.imag)] = 1

    counts = count_pipes_from_north(northern_crossings)
    enclosed = ((counts % 2 == 1) & (pipe_grid == 0)).astype(int)
    return enclosed.sum()


def count_pipes_from_north(grid: np.ndarray) -> np.ndarray:
    return np.cumsum(grid, axis=0)


@pytest.fixture()
def puzzle_input():
    return parse(Puzzle(2023, 10).input_data)


@pytest.fixture()
def example_input():
    return parse(
        """
..F7.
.FJ|.
SJ.L7
|F--J
LJ...
    """.strip()
    )


def test_part1(puzzle_input):
    assert part1(puzzle_input) == 6717


def test_example_part1(example_input):
    assert part1(example_input) == 8


def test_part2(puzzle_input):
    assert part2(puzzle_input) == 381


def test_example_part2():
    assert (
        part2(
            parse(
                """
.F----7F7F7F7F-7....
.|F--7||||||||FJ....
.||.FJ||||||||L7....
FJL7L7LJLJ||LJ.L-7..
L--J.L7...LJS7F-7L7.
....F-J..F7FJ|L7L7L7
....L7.F7||L7|.L7L7|
.....|FJLJ|FJ|F7|.LJ
....FJL-7.||.||||...
....L---J.LJ.LJLJ...
"""
            )
        )
        == 8
    )

    assert (
        part2(
            parse(
                """
FF7FSF7F7F7F7F7F---7
L|LJ||||||||||||F--J
FL-7LJLJ||||||LJL-77
F--JF--7||LJLJ7F7FJ-
L---JF-JLJ.||-FJLJJ7
|F|F-JF---7F7-L7L|7|
|FFJF7L7F-JF7|JL---7
7-L-JL7||F7|L7F-7F7|
L.L7LFJ|||||FJL7||LJ
L7JLJL-JLJLJL--JLJ.L
"""
            )
        )
        == 10
    )
