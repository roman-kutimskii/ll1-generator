from src.build_parsing_table import build_parsing_table
from src.parse_grammar import parse_grammar
from src.write_table import write_table


def main() -> None:
    with open("../grammar.txt", "r", encoding="utf-8") as f:
        grammar = parse_grammar(f.readlines())

    table = build_parsing_table(grammar)
    write_table(table)


if __name__ == "__main__":
    main()
