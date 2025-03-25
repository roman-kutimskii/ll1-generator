from collections import defaultdict

from src.parse_grammar import Grammar, Rule, Production


def factorize_grammar(grammar: Grammar) -> Grammar:
    new_grammar = Grammar(dict())

    for nonterminal, rule in grammar.rules.items():
        prefix_map = defaultdict(list)

        for production in rule.productions:
            prefix_map[production.symbols[0]].append(production)


        if len(prefix_map) == len(rule.productions):
            new_grammar.rules[nonterminal] = rule
            continue

        new_rule = Rule(nonterminal, [])
        count = 1

        for prefix, productions in prefix_map.items():
            if len(productions) == 1:
                new_rule.productions.append(productions[0])
                continue

            new_nonterminal = f"{nonterminal}'{count}"
            count += 1

            new_rule.productions.append(Production([prefix, new_nonterminal], []))

            new_sub_rule = Rule(new_nonterminal, [])
            for production in productions:
                symbols = production.symbols[1:]
                if len(production.symbols) == 1:
                    symbols = ["ε"]
                new_sub_rule.productions.append(Production(symbols, []))

            new_grammar.rules[new_nonterminal] = new_sub_rule

        new_grammar.rules[nonterminal] = new_rule

    return new_grammar
