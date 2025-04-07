from src.build_parsing_table import build_parsing_table
from src.check_line import check_line
from src.grammar import factorize_grammar, remove_direct_recursion, remove_indirect_recursion, remove_unreachable_rules, calculate_directing_sets
from src.grammar_utils import parse_grammar, parse_grammar_with_first_set, write_grammar
from src.table import write_table, read_table


def task1() -> None:
    with open("grammar.txt", "r", encoding="utf-8") as f:
        grammar = parse_grammar_with_first_set(f.readlines())

    table = build_parsing_table(grammar)
    write_table(table)


def task2() -> None:
    line = "( - a * - ( - 5 ) ) + - ( 5 + - 5 ) + a #"
    table = read_table()
    print(check_line(line.split(), table))


def task3() -> None:
    with open("grammar.txt", "r", encoding="utf-8") as f:
        grammar, axiom_nonterminal = parse_grammar(f.readlines())


    grammar = factorize_grammar(grammar)

    grammar = remove_indirect_recursion(grammar)

    grammar = remove_direct_recursion(grammar)

    grammar = remove_unreachable_rules(grammar, axiom_nonterminal)

    axiom = grammar.rules[axiom_nonterminal]
    for production in axiom.productions:
        last_symbol = production.symbols[-1]
        if axiom.nonterminal in production.symbols or (last_symbol.startswith('<') and last_symbol.endswith('>')):
            grammar.add_production("<axiom>", [axiom_nonterminal, "#"], [])
            axiom_nonterminal = "<axiom>"
            break

    grammar = calculate_directing_sets(grammar)

    write_grammar(grammar, axiom_nonterminal)


if __name__ == "__main__":
    task3()
