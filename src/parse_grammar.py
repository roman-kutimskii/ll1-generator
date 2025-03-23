import re
from dataclasses import dataclass


@dataclass
class Production:
    symbols: list[str]
    first_set: list[str]


@dataclass
class Rule:
    nonterminal: str
    productions: list[Production]

    def add_production(self, symbols: list[str], first_set: list[str]):
        self.productions.append(Production(symbols, first_set))


@dataclass
class Grammar:
    rules: dict[str, Rule]

    def add_rule(self, nonterminal: str) -> None:
        self.rules[nonterminal] = Rule(nonterminal, [])

    def add_production(self, nonterminal: str, symbols: list[str], first_set: list[str]):
        if nonterminal not in self.rules:
            self.add_rule(nonterminal)
        self.rules[nonterminal].add_production(symbols, first_set)


def parse_grammar(contents: list[str]) -> Grammar:
    grammar = Grammar({})
    pattern = r"^\s*<(\w+)>\s*->(.*)/\s*(.*)\s*$"
    for rule in contents:
        match = re.match(pattern, rule)
        if match:
            name = match.group(1)
            symbols = match.group(2).strip().split()
            first_set = match.group(3).strip().split()
            grammar.add_production(name, symbols, first_set)
    return grammar
