import pytest
from aocd.models import Puzzle
from typing import Iterator
from functools import cache

EMPTY = 0
SPRING = 1
UNKNOWN = -1


def parse(data: str) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    lines = [line.split(" ") for line in data.splitlines()]
    mapping = {".": EMPTY, "#": SPRING, "?": UNKNOWN}
    return [
        (tuple(map(lambda ch: mapping[ch], line[0])), tuple(map(int, line[1].split(",")))) for line in lines
    ]


def part1(lines: list[tuple[tuple[int, ...], tuple[int, ...]]]) -> int:
    return sum(arrangements(springs, groups) for (springs, groups) in lines)



def arrangements(springs: tuple[int, ...], expected_groups: tuple[int, ...]) -> int:
    """
    Calculate the number of possible arrangments of UNKNOWN springs to end up with
    the expected groups.
    """
    @cache  # <-- dynamic programming :D
    def _arrangements(groups: tuple[int, ...], springs: tuple[int, ...], last_was_zero: bool = True) -> int:
        """
        Calcualte number of possible arrangments

        Scans the springs from left to right and stores the current groups. As new 
        springs are processed the current groups are updated.

        If an unkown spring is encountered recursively calls itself with both
        possibilities.

        Args:
            groups: The groups we have computed so far
            springs: The springs left to process in the line
            last_was_zero: Flag indicating whether the last processed symbol
                in our line was zero or not.
                Decides whether a new spring will be the first of a new group
                or added to the last existing group.
        """
        already_final = groups[:-1]  # early stopping
        if already_final != expected_groups[:len(already_final)]:
            return 0

        try:
            index = springs.index(UNKNOWN)
        except ValueError:  # no more unknowns
            groups, _ = combine(groups, springs, last_was_zero)
            return 1 if groups == expected_groups else 0
        
        # fast forward to the next UNKNOWN, and then calculate both options
        groups, last_was_zero = combine(groups, springs[:index], last_was_zero)
        remaining = springs[index+1:]

        groups_a, was_zero_a = combine(groups, (0,), last_was_zero)
        groups_b, was_zero_b = combine(groups, (1,), last_was_zero)

        return _arrangements(groups_a, remaining, was_zero_a) + _arrangements(groups_b, remaining, was_zero_b)

    return _arrangements((), springs, True)

def combine(groups: tuple[int, ...], springs: tuple[int, ...], new_group: bool = True):
    if not springs:
        return groups, new_group

    if new_group:
        existing = list(groups)
        count = 0
    else:
        existing = list(groups[:-1])
        count = groups[-1]

    for spring in springs:
        if spring > 0:
            count += spring
        elif count > 0:
            existing.append(count)
            count = 0
    
    if count > 0:
        existing.append(count)
    
    return tuple(existing), springs[-1] == EMPTY  # if we ended with EMPTY, start a new group



def part2(lines: list[tuple[tuple[int, ...], tuple[int, ...]]]) -> int:
    s = 0
    for springs, groups in lines:
        springs = ((springs + (UNKNOWN, )) * 5)[:-1]
        groups = groups * 5
        s += arrangements(springs, groups)

    return s


@pytest.fixture()
def puzzle_input():
    return parse(Puzzle(2023, 12).input_data)


@pytest.fixture()
def example_input():
    return parse(
        """
???.### 1,1,3
.??..??...?##. 1,1,3
?#?#?#?#?#?#?#? 1,3,1,6
????.#...#... 4,1,1
????.######..#####. 1,6,5
?###???????? 3,2,1
    """.strip()
    )


def test_combine():
    assert combine((), (1, 0, 1, 0, 1, 1, 1))[0] == (1, 1, 3)
    assert combine((), (1, 0, 1, 0, 3))[0] == (1, 1, 3)
    assert combine((), (0, 1, 1, 0, 0, 1, 1))[0] == (2, 2)
    assert combine((), (0, 1, 1, 0, 0, 1, 1, 0, 0))[0] == (2, 2)

    assert combine((2, 2,), (0, 1, 1, 0, 0, 1, 1, 0, 0))[0] == (2, 2, 2, 2)
    assert combine((2, 1,), (1, 0, 1, 1, 0, 0, 1, 1, 0, 0), True)[0] == (2, 1, 1, 2, 2)
    assert combine((2, 1,), (1, 0, 1, 1, 0, 0, 1, 1, 0, 0), False)[0] == (2, 2, 2, 2)
    assert combine((3,), (1, 0, 1), False)[0] == (4, 1)

    groups, new_group = (), True
    for x in [1, 0, 1, 0, 1, 1, 1]:
        groups, new_group = combine(groups, (x,), new_group)
    
    assert groups == (1, 1, 3)


def test_part1(puzzle_input):
    assert part1(puzzle_input) == 7506


def test_example_part1(example_input):
    assert part1(example_input) == 21


def test_single_example_part1():
    assert part1(parse("????.######..#####. 1,6,5")) == 4


def test_part2(puzzle_input):
    assert part2(puzzle_input) == 548241300348335

def test_single_example_part2():
    assert part2(parse(".??..??...?##. 1,1,3")) == 16384


def test_example_part2(example_input):
    assert part2(example_input) == 525152
