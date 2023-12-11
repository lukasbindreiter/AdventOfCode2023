from collections import Counter
import pytest
from aocd.models import Puzzle
import re
import numpy as np

_CARD_VALUES = {"A": 14, "K": 13, "Q": 12, "J": 11, "T": 10} | {
    str(i): i for i in range(2, 10)
}


def numbers(text: str) -> list[int]:
    return list(map(int, re.findall(r"\d+", text)))


def parse_line(line: str) -> tuple[tuple[int, ...], int]:
    hand, bid = line.split(" ")
    hand_values = tuple(_CARD_VALUES[card] for card in hand)
    return hand_values, int(bid)


def parse(data: str) -> list[tuple[tuple[int, ...], int]]:
    return [parse_line(line) for line in data.strip().splitlines()]


def part1(input: list[tuple[tuple[int, ...], int]]) -> int:
    hands = [((hand_type(hand, use_jokers=False), hand), bid) for hand, bid in input]
    # Sort by hand type (ascending) then by cards (ascending)
    # this will sort from weakest to strongest hand
    hands = sorted(hands, key=lambda x: x[0])
    bids = np.array([bid for _, bid in hands])
    ranks = np.arange(1, len(bids) + 1)

    return (ranks * bids).sum()


def hand_type(hand: tuple[int, ...], use_jokers: bool = False) -> int:
    if not use_jokers:
        counts = tuple(val for _, val in Counter(hand).most_common())
    else:
        jokers = tuple(card for card in hand if card == 11)
        non_jokers = tuple(card for card in hand if card != 11)
        counts = tuple(val for _, val in Counter(non_jokers).most_common())
        # add number of jokers to the count of the most common card
        if len(counts) < 2:  # only one kind of non-joker card or only jokers
            counts = (len(hand),)
        else:
            counts = tuple([counts[0] + len(jokers), *counts[1:]])

    assert sum(counts) == len(hand)

    match counts:
        case (5,):  # Five of a kind
            return 6
        case (4, 1):  # Four of a kind
            return 5
        case (3, 2):  # Full house
            return 4
        case (3, 1, 1):  # Three of a kind
            return 3
        case (2, 2, 1):  # Two pair
            return 2
        case (2, 1, 1, 1):  # One pair
            return 1
        case _:  # High card
            return 0


def part2(input: list[tuple[tuple[int, ...], int]]) -> int:
    hands = [((hand_type(hand, use_jokers=True), hand), bid) for hand, bid in input]

    # Replace jokers with a value of 1 to make them the weakest card
    hands = [
        ((hand_type, tuple([card if card != 11 else 1 for card in hand])), bid)
        for (hand_type, hand), bid in hands
    ]

    # Sort by hand type (ascending) then by cards (ascending)
    # this will sort from weakest to strongest hand
    hands = sorted(hands, key=lambda x: x[0])
    bids = np.array([bid for _, bid in hands])
    ranks = np.arange(1, len(bids) + 1)

    return (ranks * bids).sum()


@pytest.fixture()
def puzzle_input():
    return parse(Puzzle(2023, 7).input_data)


@pytest.fixture()
def example_input():
    return parse(
        """
32T3K 765
T55J5 684
KK677 28
KTJJT 220
QQQJA 483
    """.strip()
    )


def test_part1(puzzle_input):
    assert part1(puzzle_input) == 250898830


def test_example_part1(example_input):
    assert part1(example_input) == 6440


def test_part2(puzzle_input):
    assert part2(puzzle_input) == 252127335


def test_example_part2(example_input):
    assert part2(example_input) == 5905
