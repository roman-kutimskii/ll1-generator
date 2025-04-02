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

        for prefix, productions in prefix_map.items():
            if len(productions) == 1:
                new_rule.productions.append(productions[0])
                continue

            new_nonterminal = f"<{nonterminal.strip('<>')}'>"

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


def remove_direct_recursion(grammar: Grammar) -> Grammar:
    new_grammar = Grammar({})

    for nonterminal, rule in grammar.rules.items():
        recursive = []
        non_recursive = []

        for production in rule.productions:
            if production.symbols and production.symbols[0] == nonterminal:
                recursive.append(production.symbols[1:])
            else:
                non_recursive.append(production.symbols)

        if recursive:
            new_nonterminal = f"<{nonterminal.strip('<>')}r>"
            new_grammar.rules[new_nonterminal] = Rule(new_nonterminal, [])

            new_grammar.rules[nonterminal] = Rule(nonterminal, [
                Production(body + [new_nonterminal], []) for body in non_recursive
            ])

            new_grammar.rules[new_nonterminal].productions = [Production(body + [new_nonterminal], []) for body in
                                                              recursive] + [Production(["ε"], [])]
        else:
            new_grammar.rules[nonterminal] = rule

    return new_grammar

def build_dependency_graph(grammar: Grammar) -> dict[str, set[str]]:
    graph = defaultdict(set)
    for nonterminal, rule in grammar.rules.items():
        for production in rule.productions:
            if production.symbols and production.symbols[0] in grammar.rules:
                graph[nonterminal].add(production.symbols[0])
    return graph


def topological_sort(graph: dict[str, set[str]]) -> list[str]:
    visited = set()
    order = []

    def dfs(node):
        if node in visited:
            return
        visited.add(node)
        for neighbor in graph[node]:
            dfs(neighbor)
        order.append(node)

    for node in graph:
        if node not in visited:
            dfs(node)

    return order


def remove_indirect_recursion(grammar: Grammar) -> Grammar:
    graph = build_dependency_graph(grammar)
    order = topological_sort(graph)

    for i, a_i in enumerate(order):
        for j in range(i):
            a_j = order[j]
            new_productions = []

            for production in grammar.rules[a_i].productions:
                if production.symbols and production.symbols[0] == a_j:
                    for a_j_prod in grammar.rules[a_j].productions:
                        new_productions.append(Production(a_j_prod.symbols + production.symbols[1:], []))
                else:
                    new_productions.append(production)

            grammar.rules[a_i].productions = new_productions

    return remove_direct_recursion(grammar)
