import re
import sys

from lab6.main import task
from src.build_parsing_table import build_parsing_table
from src.check_line import check_line
from src.grammar import factorize_grammar, remove_direct_recursion, remove_indirect_recursion, remove_unreachable_rules, \
    calculate_directing_sets
from src.grammar_utils import parse_grammar, parse_grammar_with_first_set, write_grammar, Grammar
from src.table import write_table, read_table


def task1() -> None:
    with open("new-grammar.txt", "r", encoding="utf-8") as f:
        grammar = parse_grammar_with_first_set(f.readlines())

    table = build_parsing_table(grammar, list(grammar.rules.keys())[0])
    write_table(table)


def task2(line: str) -> str:
    table = read_table()
    return check_line(line.split(), table)


def task3() -> tuple[Grammar, str]:
    with open("grammar.txt", "r", encoding="utf-8") as f:
        grammar, axiom_nonterminal = parse_grammar(f.readlines())

    grammar = factorize_grammar(grammar)

    grammar = remove_indirect_recursion(grammar)

    grammar = remove_direct_recursion(grammar)

    grammar = remove_unreachable_rules(grammar, axiom_nonterminal)

    axiom = grammar.rules[axiom_nonterminal]

    needs_new_axiom = False
    if len(axiom.productions) > 1:
        needs_new_axiom = True
    elif axiom.productions and (axiom.nonterminal in axiom.productions[0].symbols or (
            axiom.productions[0].symbols and axiom.productions[0].symbols[-1].startswith('<') and
            axiom.productions[0].symbols[-1].endswith('>'))):
        needs_new_axiom = True

    if needs_new_axiom:
        grammar.add_production("<axiom>", [axiom_nonterminal, "#"], [])
        axiom_nonterminal = "<axiom>"

    grammar = calculate_directing_sets(grammar, axiom_nonterminal)

    write_grammar(grammar, axiom_nonterminal)

    return grammar, axiom_nonterminal


def task4() -> None:
    if len(sys.argv) != 2:
        print(f'Usage: python {sys.argv[0]} <input-file>')
        return

    input_file = sys.argv[1]

    tokens = task(input_file)

    line = " ".join(token.type for token in tokens)

    task3()
    task1()
    error = task2(line)
    if error != "Ok":
        pattern = r"Error at index (\d+): '([^']+)'.*"
        match = re.match(pattern, error)
        if match:
            index = int(match.group(1))
            symbol = match.group(2)
            print(f"Index: {tokens[index].pos}")
            print(f"Symbol: {symbol}")

    print(error)


if __name__ == "__main__":
    task4()
