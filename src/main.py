from src.build_parsing_table import build_parsing_table
from src.check_line import check_line
from src.grammar import factorize_grammar
from src.parse_grammar import parse_grammar, parse_grammar_with_first_set
from src.table import write_table, read_table


def task1() -> None:
    with open("grammar.txt", "r", encoding="utf-8") as f:
        grammar = parse_grammar_with_first_set(f.readlines())

    table = build_parsing_table(grammar)
    write_table(table)


def task2() -> None:
    line = "type a = record b : int end ; c : int ⊥"
    table = read_table()
    print(check_line(line.split(), table))


def task3() -> None:
    with open("grammar.txt", "r", encoding="utf-8") as f:
        grammar, axiom_nonterminal = parse_grammar(f.readlines())

    axiom = grammar.rules[axiom_nonterminal]

    for production in axiom.productions:
        if axiom.nonterminal in production.symbols:
            grammar.add_production("<axiom>", [axiom_nonterminal, "#"], [])
            axiom_nonterminal = "<axiom>"
            break

    grammar = factorize_grammar(grammar)

    for rule in grammar.rules.values():
        print(rule)


if __name__ == "__main__":
    task3()
