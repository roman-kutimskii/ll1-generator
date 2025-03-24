from src.build_parsing_table import build_parsing_table
from src.check_line import check_line
from src.parse_grammar import parse_grammar
from src.table import write_table, read_table


def task1() -> None:
    with open("../grammar.txt", "r", encoding="utf-8") as f:
        grammar = parse_grammar(f.readlines())

    table = build_parsing_table(grammar)
    write_table(table)


def task2() -> None:
    line = "type a = record b : int end ; c : int ⊥"
    table = read_table()
    print(check_line(line.split(), table))


if __name__ == "__main__":
    task2()
