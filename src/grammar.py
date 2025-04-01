from collections import defaultdict
from src.grammar_utils import Grammar, Rule, Production


def factorize_grammar(grammar: Grammar) -> Grammar:
    new_grammar = Grammar({})

    for nonterminal, rule in grammar.rules.items():
        prefix_map = defaultdict(list)

        for production in rule.productions:
            prefix_map[production.symbols[0]].append(production)

        if len(prefix_map) == len(rule.productions):
            new_grammar.rules[nonterminal] = rule
            continue

        new_rule = Rule(nonterminal, [])
        count = 0

        for prefix, productions in prefix_map.items():
            if len(productions) == 1:
                new_rule.productions.append(productions[0])
                continue

            new_nonterminal = f"<{nonterminal.strip('<>')}'{count}>"
            count += 1

            new_rule.productions.append(Production([prefix, new_nonterminal], []))

            new_grammar.rules[new_nonterminal] = Rule(
                new_nonterminal,
                [
                    Production(production.symbols[1:] or ["ε"], [])
                    for production in productions
                ],
            )

        new_grammar.rules[nonterminal] = new_rule

    if any(len(set(p.symbols[0] for p in rule.productions)) < len(rule.productions)
           for rule in new_grammar.rules.values()):
        return factorize_grammar(new_grammar)

    return new_grammar
