from src.parse_grammar import parse_grammar


def main() -> None:
    with open("../grammar.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    grammar = parse_grammar(lines)
    rule_indices: dict[str, int] = {}
    index = 0

    for rule in grammar.rules.values():
        rule_indices[rule.nonterminal] = index
        index += sum(len(production.symbols) + 1 for production in rule.productions)


if __name__ == "__main__":
    main()
