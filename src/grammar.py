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
    graph = dict()
    for nonterminal, rule in grammar.rules.items():
        for production in rule.productions:
            graph.setdefault(nonterminal, set())
            if production.symbols and production.symbols[0] in grammar.rules:
                graph[nonterminal].add(production.symbols[0])
    return graph


def topological_sort(graph: dict[str, set[str]], nonterminal: str) -> list[str]:
    visited = set()
    order = []

    def dfs(node: str) -> None:
        if node in visited:
            return
        visited.add(node)
        for neighbor in graph[node]:
            dfs(neighbor)
        order.append(node)

    dfs(nonterminal)

    return order


def remove_indirect_recursion(grammar: Grammar, start_symbol: str) -> Grammar:
    graph = build_dependency_graph(grammar)

    for node in graph:
        order = topological_sort(graph, node)[:-1]

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

    return remove_direct_recursion(remove_unreachable_rules(grammar, start_symbol))


def remove_unreachable_rules(grammar: Grammar, start_symbol: str) -> Grammar:
    reachable = set()
    queue = [start_symbol]

    while queue:
        current = queue.pop()
        if current in reachable:
            continue
        reachable.add(current)
        if current in grammar.rules:
            for production in grammar.rules[current].productions:
                for symbol in production.symbols:
                    if symbol in grammar.rules and symbol not in reachable:
                        queue.append(symbol)

    new_rules = {nt: rule for nt, rule in grammar.rules.items() if nt in reachable}
    return Grammar(new_rules)
