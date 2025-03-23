from itertools import chain

from src.parse_grammar import parse_grammar
from src.write_table import write_table, Line


def is_nonterminal(symbol: str) -> bool:
    return symbol.startswith('<') and symbol.endswith('>')


def main() -> None:
    with open("../grammar.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    grammar = parse_grammar(lines)
    rule_indices: dict[str, int] = {}
    index = 0

    for rule in grammar.rules.values():
        rule_indices[rule.nonterminal] = index
        index += sum(len(production.symbols) + 1 for production in rule.productions)

    table: list[Line] = []

    index = 0
    end_set = False
    for rule in grammar.rules.values():
        production_symbols = []
        for production_index, production in enumerate(rule.productions):
            error = production_index == len(rule.productions) - 1
            pointer = index + len(rule.productions) - production_index + sum(
                len(production.symbols) for production in rule.productions[:production_index])
            table.append(Line(index, rule.nonterminal, production.first_set, False, error, pointer, False, False))
            index += 1
            production_symbols.append(production.symbols)
        for symbols_index, symbols in enumerate(production_symbols):
            for symbol_index, symbol in enumerate(symbols):
                first_set = list(
                    set(chain.from_iterable(
                        production.first_set for production in grammar.rules[symbol].productions))) if is_nonterminal(
                    symbol) else rule.productions[symbols_index].first_set if symbol == "ε" else [symbol]
                pointer = rule_indices[symbol] if is_nonterminal(symbol) else None if symbol_index == len(
                    symbols) - 1 else index + 1
                end = not end_set and symbol_index == len(symbols) - 1 and not is_nonterminal(symbol)
                if end:
                    end_set = True
                stack = symbol_index != len(symbols) - 1 if is_nonterminal(symbol) else False
                table.append(
                    Line(index, symbol, first_set, not is_nonterminal(symbol) and symbol != "ε", True, pointer, stack,
                         end))
                index += 1

    write_table(table)


if __name__ == "__main__":
    main()
