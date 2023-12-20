from collections import defaultdict
import pytest
from aocd.models import Puzzle
import math


class PulseMachine:
    def __init__(self, module_config: list[tuple[str, list[str]]]):
        self.low_pulses = 0
        self.high_pulses = 0

        self.modules: dict[str, Module] = {}
        self.inputs_per_module = defaultdict(
            list
        )  # Conjunctions need to know their inputs
        for module_name, outputs in module_config:
            module_type: type = Broadcaster
            if module_name[0] == "%":
                module_type = FlipFlop
                module_name = module_name[1:]
            elif module_name[0] == "&":
                module_type = Conjunction
                module_name = module_name[1:]

            for output in outputs:
                self.inputs_per_module[output].append(module_name)
            self.modules[module_name] = module_type(module_name, outputs)

        for module_name, inputs in self.inputs_per_module.items():
            # instantiate unknown output modules (they don't emit any pulses)
            if module_name not in self.modules:
                self.modules[module_name] = Module(module_name, [])  # unknown modules

            # tell conjunction modules about their inputs
            module = self.modules[module_name]
            if isinstance(module, Conjunction):
                for input_module in inputs:
                    module.add_input(input_module)

    def press_button(self, signal: bool):
        # for part 2 we need to monitor certain conjunction modules after each button
        # press, so we reset them before simulating the button press pulses
        for module in self.modules.values():
            if isinstance(module, Conjunction):
                module.had_high_signal = False

        # the initial button signal
        signals: list[tuple[str, str, bool]] = [("button", "broadcaster", signal)]

        while signals:
            input_module, output_module, signal = signals.pop(0)
            if signal:
                self.high_pulses += 1
            else:
                self.low_pulses += 1
            signals.extend(self.modules[output_module](input_module, signal))

    def __getitem__(self, key: str) -> "Module":
        return self.modules[key]


class Module:
    def __init__(self, name: str, outputs: list[str]):
        self.name = name
        self.outputs = outputs

    def __call__(self, input_module: str, signal: bool) -> list[tuple[str, str, bool]]:
        return []


class Broadcaster(Module):
    def __call__(self, input_module: str, signal: bool) -> list[tuple[str, str, bool]]:
        return [(self.name, output, signal) for output in self.outputs]


class FlipFlop(Module):
    def __init__(self, name: str, outputs: list[str]):
        super().__init__(name, outputs)
        self.on = False

    def __call__(self, input_module: str, signal: bool) -> list[tuple[str, str, bool]]:
        # If a flip-flop module receives a high pulse, it is ignored and nothing happens
        if signal:
            return []

        # If a flip-flop module receives a low pulse, it toggles its state and sends
        # its new state
        self.on = not self.on
        return [(self.name, output, self.on) for output in self.outputs]


class Conjunction(Module):
    def __init__(self, name: str, outputs: list[str]):
        super().__init__(name, outputs)
        self.inputs: dict[str, bool] = {}
        self.had_high_signal = False

    def add_input(self, name: str):
        self.inputs[name] = False

    def __call__(self, input_module: str, signal: bool) -> list[tuple[str, str, bool]]:
        self.inputs[input_module] = signal
        output_signal = not all(self.inputs.values())
        if output_signal:
            self.had_high_signal = True

        return [(self.name, output, output_signal) for output in self.outputs]


def parse(data: str) -> list[tuple[str, list[str]]]:
    lines = data.split("\n")
    return [parse_module(*line.split(" -> ")) for line in lines]


def parse_module(module_name: str, outputs: str) -> tuple[str, list[str]]:
    return module_name, outputs.split(", ")


def part1(module_config: list[tuple[str, list[str]]]) -> int:
    machine = PulseMachine(module_config)
    for _ in range(1000):
        machine.press_button(False)
    return machine.low_pulses * machine.high_pulses


def part2(module_config: list[tuple[str, list[str]]], max_cycles: int = 100000) -> int:
    machine = PulseMachine(module_config)

    # this is a bit of hardcoding for the puzzle input, but not really away around
    # this without brute forcing the solution

    # we seem to have multiple binary counters. The start of the counters are flip-flops
    # that are the outputs of the broadcaster.
    # Each flip flop in a counter is connected to a next flip-flop as well as a
    # conjuntion module. That conjuntion module is the output of the counter.
    # It is again connected to another conjunction module, which will only emit a
    # pulse when the counter reaches a certain value. Afterwards the counter will reset
    # and the cycle starts again.
    #
    # By finding the cycle length then for each counter and calculating the least common
    # multiple of those cycle lengths we should arrive at the right answer.

    broadcaster_outputs = [machine[output] for output in machine["broadcaster"].outputs]
    counter_outputs = [
        find_counter_output(machine, counter_first_flip_flop)
        for counter_first_flip_flop in broadcaster_outputs
    ]
    counters = {
        counter_output.name: counter_output for counter_output in counter_outputs
    }

    cycle_lengths = {}
    for i in range(1, max_cycles):
        machine.press_button(False)

        # copy with list to allow deletion while iterating
        for counter_name, counter in list(counters.items()):
            # check if the counters have reached their cycle length
            if counter.had_high_signal:
                cycle_lengths[counter_name] = i
                del counters[counter_name]

        if len(counters) == 0:
            break

    return math.lcm(*cycle_lengths.values())


def find_counter_output(machine: PulseMachine, counter_input: Module) -> Conjunction:
    # find the conjunction module that is the end of the counter
    possible_conjunctions = [machine[output] for output in counter_input.outputs]
    conjunction = find_conjunction(possible_conjunctions)

    # now find the conjunction module among the outputs of the previous conjunction
    conjunction = find_conjunction([machine[output] for output in conjunction.outputs])

    # this conjunction should have only one output
    assert len(conjunction.outputs) == 1

    # and that one output should have an output to "rx"
    conjunction_output = machine[conjunction.outputs[0]]
    assert conjunction_output.outputs == ["rx"]

    return conjunction  # the conjunction output of the counter


def find_conjunction(modules: list[Module]) -> Conjunction:
    possible_conjunctions = [
        module for module in modules if isinstance(module, Conjunction)
    ]
    assert len(possible_conjunctions) == 1
    return possible_conjunctions[0]


@pytest.fixture()
def puzzle_input():
    return parse(Puzzle(2023, 20).input_data)


@pytest.fixture()
def example_input():
    return parse(
        """
broadcaster -> a, b, c
%a -> b
%b -> c
%c -> inv
&inv -> a
    """.strip()
    )


@pytest.fixture()
def example_input_2():
    return parse(
        """
broadcaster -> a
%a -> inv, con
&inv -> b
%b -> con
&con -> output
    """.strip()
    )


def test_part1(puzzle_input):
    assert part1(puzzle_input) == 684125385


def test_example_part1(example_input):
    assert part1(example_input) == 32000000


def test_example2_part1(example_input_2):
    assert part1(example_input_2) == 11687500


def test_part2(puzzle_input):
    assert part2(puzzle_input) == 225872806380073
