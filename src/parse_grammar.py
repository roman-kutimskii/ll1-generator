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

    def add_production(self, symbols: list[str], first_set: list[str]) -> None:
        self.productions.append(Production(symbols, first_set))


@dataclass
class Grammar:
    rules: dict[str, Rule]

    def add_production(self, nonterminal: str, symbols: list[str], first_set: list[str]) -> None:
        if nonterminal not in self.rules:
            self.rules[nonterminal] = Rule(nonterminal, [])
        self.rules[nonterminal].add_production(symbols, first_set)


def parse_grammar(contents: list[str]) -> Grammar:
    grammar = Grammar(dict())
    pattern = re.compile(r"^\s*(<\w+>)\s*->(.*)/\s*(.*)\s*$")

    for rule in contents:
        match = pattern.match(rule)
        if match:
            nonterminal, symbols, first_set = match.groups()
            grammar.add_production(nonterminal.strip(), symbols.strip().split(), first_set.strip().split())

    return grammar
