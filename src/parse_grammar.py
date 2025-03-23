import pprint
import re
from dataclasses import dataclass


@dataclass
class Rule:
    name: str
    content: list[str]
    symbols: list[str]


def parse_grammar(contents: list[str]) -> list[Rule]:
    rules = []
    pattern = r"^\s*(<\w+>)\s*->(.*)/\s*(.*)\s*$"
    for rule in contents:
        match = re.match(pattern, rule)
        if match:
            name = match.group(1)
            content = match.group(2).strip().split()
            symbols = match.group(3).strip().split()
            rules.append(Rule(name, content, symbols))
    return rules
