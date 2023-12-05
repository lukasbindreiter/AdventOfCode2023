import pytest
from aocd.models import Puzzle
import re


def numbers(text: str) -> list[int]:
    return list(map(int, re.findall(r"\d+", text)))


def ranges(text: str) -> list[tuple[range, int]]:
    nums = numbers(text)

    return [
        (
            range(nums[i + 1], nums[i + 1] + nums[i + 2]),  # source_range
            nums[i] - nums[i + 1],  # offset to destination_range
        )
        for i in range(0, len(nums), 3)
    ]


def parse(data: str):
    parts = data.strip().split("\n\n")
    seeds = numbers(parts[0])

    conversions = [ranges(part) for part in parts[1:]]

    return seeds, conversions


def part1(nums: list[int], conversions: list[list[tuple[range, int]]]) -> int:
    for conversion in conversions:
        for i, num in enumerate(nums):
            for source_range, offset in conversion:
                if num in source_range:
                    nums[i] += offset
                    break
    return min(nums)


def range_intersection(a: range, b: range) -> range:
    return range(max(a.start, b.start), min(a.stop, b.stop))


def part2(nums: list[int], conversions: list[list[tuple[range, int]]]):
    ranges = [range(nums[i], nums[i] + nums[i + 1]) for i in range(0, len(nums), 2)]

    for conversion in conversions:
        mapped = []
        i = 0
        while i < len(ranges):
            r = ranges[i]
            found_intersection = False
            for source_range, offset in conversion:
                intersection = range_intersection(source_range, r)
                if intersection:
                    found_intersection = True
                    mapped.append(
                        range(
                            intersection.start + offset,
                            intersection.stop + offset,
                        )
                    )
                    before = range(r.start, intersection.start)

                    if before:
                        ranges.append(before)

                    after = range(intersection.stop, r.stop)
                    if after:
                        ranges.append(after)

                    break
            if not found_intersection:
                mapped.append(r)

            i += 1
        ranges = mapped

    return min(r.start for r in ranges)


@pytest.fixture()
def puzzle_input():
    return parse(Puzzle(2023, 5).input_data)


@pytest.fixture()
def example_input():
    return parse(
        """
seeds: 79 14 55 13

seed-to-soil map:
50 98 2
52 50 48

soil-to-fertilizer map:
0 15 37
37 52 2
39 0 15

fertilizer-to-water map:
49 53 8
0 11 42
42 0 7
57 7 4

water-to-light map:
88 18 7
18 25 70

light-to-temperature map:
45 77 23
81 45 19
68 64 13

temperature-to-humidity map:
0 69 1
1 0 69

humidity-to-location map:
60 56 37
56 93 4
    """.strip()
    )


def test_part1(puzzle_input):
    assert part1(*puzzle_input) == 165788812


def test_example_part1(example_input):
    assert part1(*example_input) == 35


def test_part2(puzzle_input):
    assert part2(*puzzle_input) == 1928058


def test_example_part2(example_input):
    assert part2(*example_input) == 46
