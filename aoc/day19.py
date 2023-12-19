from attr import dataclass
import pytest
from aocd.models import Puzzle
from math import prod


@dataclass
class RuleComparison:
    prop: str  # x, m, a or s
    op: str  # < or >
    value: int  # value to compare to

    @classmethod
    def parse(cls, data: str) -> "RuleComparison":
        prop, op, value = data[0], data[1], int(data[2:])
        return cls(prop, op, value)


@dataclass
class Rule:
    comparison: RuleComparison
    next_workflow: str

    @classmethod
    def parse(cls, data: str) -> "Rule":
        comparison, next_workflow = data.split(":")
        return cls(RuleComparison.parse(comparison), next_workflow)


@dataclass
class Workflow:
    name: str
    rules: list[Rule]
    fallback_workflow: str

    @classmethod
    def parse(cls, data: str) -> "Workflow":
        name, rules_line = data.split("{")
        rules_line = rules_line.rstrip("}")
        workflow_rules = []
        rules = rules_line.split(",")
        for rule in rules[:-1]:
            workflow_rules.append(Rule.parse(rule))

        return cls(name, workflow_rules, rules[-1])


@dataclass
class Part:
    x: int
    m: int
    a: int
    s: int

    def sum(self):
        return self.x + self.m + self.a + self.s

    @classmethod
    def parse(cls, data: str) -> "Part":
        part = {}
        props = data.lstrip("{").rstrip("}").split(",")
        for prop in props:
            key, value = prop.split("=")
            part[key] = int(value)

        return cls(**part)


def parse(data: str) -> tuple[dict[str, Workflow], list[Part]]:
    workflows, parts = data.split("\n\n")
    return parse_workflows(workflows), parse_parts(parts)


def parse_workflows(workflows_data: str) -> dict[str, Workflow]:
    workflows = [Workflow.parse(line) for line in workflows_data.split("\n")]
    return {workflow.name: workflow for workflow in workflows}


def parse_parts(parts_data: str) -> list[Part]:
    return [Part.parse(line) for line in parts_data.split("\n")]


def part1(workflows: dict[str, Workflow], parts: list[Part]) -> int:
    return sum(part.sum() for part in parts if is_accepted(workflows, part))


def is_accepted(workflows: dict[str, Workflow], part: Part) -> bool:
    workflow = "in"
    while workflow != "R" and workflow != "A":
        workflow = compute_workflow(workflows[workflow], part)

    return workflow == "A"


OPS = {
    "<": lambda a, b: a < b,
    ">": lambda a, b: a > b,
}


def compute_workflow(workflow: Workflow, part: Part) -> str:
    for rule in workflow.rules:
        part_prop = getattr(part, rule.comparison.prop)
        if OPS[rule.comparison.op](part_prop, rule.comparison.value):
            return rule.next_workflow

    return workflow.fallback_workflow


def part2(workflows: dict[str, Workflow], maximum: int = 4000) -> int:
    ranges = {prop: range(1, maximum + 1) for prop in "xmas"}

    return compute_accepted_for_ranges(ranges, "in", workflows)


def compute_accepted_for_ranges(
    ranges: dict[str, range], workflow: str, workflows: dict[str, Workflow]
) -> int:
    """
    Compute how many parts are accepted for the given ranges of part properties
    and workflows.

    This is done by splitting the range of the respective property for every rule
    into two ranges, one where the rule is true and one where it is false.

    For the true range we recursively compute the number of accepted parts for the
    next workflow. For the false range we continue with the next rule in the workflow,
    or the fallback next workflow if it was the last rule already.

    If the workflow is "A" or "R", we are done and return the number of accepted parts,
    which is just the product of the lengths of the ranges for all properties.
    """
    if workflow == "A":
        return prod(len(r) for r in ranges.values())

    if workflow == "R":
        return 0

    accepted = 0
    for rule in workflows[workflow].rules:
        true_branch, false_branch = split_range(
            ranges[rule.comparison.prop], rule.comparison.value, rule.comparison.op
        )
        if true_branch:
            accepted += compute_accepted_for_ranges(
                # overwrite the one range of the current rule
                {**ranges, rule.comparison.prop: true_branch},
                rule.next_workflow,
                workflows,
            )
        if not false_branch:  # empty range, so no more parts can be accepted here
            return accepted

        # continue with the else branch of the current rule
        ranges[rule.comparison.prop] = false_branch

    # continue with the fallback workflow
    accepted += compute_accepted_for_ranges(
        ranges, workflows[workflow].fallback_workflow, workflows
    )

    return accepted


def split_range(r: range, value: int, op: str) -> tuple[range, range]:
    """
    Split a range into two ranges, a true and a false range.

    For every value v in the true range, the comparison: v OP value is true.
    For every value v in the false range, the comparison: v OP value is false.
    OP is either "<" or ">".
    """
    if op == "<":
        split = min(max(r.start, value), r.stop)
        return range(r.start, split), range(split, r.stop)
    else:
        split = min(max(r.start, value + 1), r.stop)
        return range(split, r.stop), range(r.start, split)


@pytest.fixture()
def puzzle_input():
    return parse(Puzzle(2023, 19).input_data)


@pytest.fixture()
def example_input():
    return parse(
        """
px{a<2006:qkq,m>2090:A,rfg}
pv{a>1716:R,A}
lnx{m>1548:A,A}
rfg{s<537:gd,x>2440:R,A}
qs{s>3448:A,lnx}
qkq{x<1416:A,crn}
crn{x>2662:A,R}
in{s<1351:px,qqz}
qqz{s>2770:qs,m<1801:hdj,R}
gd{a>3333:R,R}
hdj{m>838:A,pv}

{x=787,m=2655,a=1222,s=2876}
{x=1679,m=44,a=2067,s=496}
{x=2036,m=264,a=79,s=2244}
{x=2461,m=1339,a=466,s=291}
{x=2127,m=1623,a=2188,s=1013}
    """.strip()
    )


def test_part1(puzzle_input):
    assert part1(*puzzle_input) == 333263


def test_example_part1(example_input):
    assert part1(*example_input) == 19114


def test_part2(puzzle_input):
    assert part2(puzzle_input[0]) == 130745440937650


def test_example_part2(example_input):
    assert part2(example_input[0]) == 167409079868000


def test_split_range():
    assert split_range(range(1, 10), 5, "<") == (range(1, 5), range(5, 10))
    assert split_range(range(5, 10), 5, "<") == (range(5, 5), range(5, 10))
    assert split_range(range(5, 10), 4, "<") == (range(5, 5), range(5, 10))
    assert split_range(range(5, 10), 11, "<") == (range(5, 10), range(10, 10))

    assert split_range(range(1, 10), 5, ">") == (range(6, 10), range(1, 6))
    assert split_range(range(5, 10), 5, ">") == (range(6, 10), range(5, 6))
    assert split_range(range(5, 10), 4, ">") == (range(5, 10), range(5, 5))
    assert split_range(range(5, 10), 10, ">") == (range(10, 10), range(5, 10))
