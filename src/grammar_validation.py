from src.build_parsing_table import is_terminal
from src.grammar_utils import Grammar


def check_reachability(grammar: Grammar, start_symbol: str) -> bool:
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

    all_nonterminals = set(grammar.rules.keys())
    unreachable = all_nonterminals - reachable

    return len(unreachable) == 0


def check_productivity(grammar: Grammar) -> str | None:
    productive = set()
    changed = True

    for nonterminal, rule in grammar.rules.items():
        for production in rule.productions:
            if all(is_terminal(symbol) or symbol == "ε" for symbol in production.symbols):
                productive.add(nonterminal)
                break

    while changed:
        changed = False
        for nonterminal, rule in grammar.rules.items():
            if nonterminal in productive:
                continue

            for production in rule.productions:
                if all(is_terminal(symbol) or symbol == "ε" or symbol in productive for symbol in production.symbols):
                    productive.add(nonterminal)
                    changed = True
                    break

    all_nonterminals = set(grammar.rules.keys())
    unproductive = all_nonterminals - productive

    if unproductive:
        dependency_graph = {nt: set() for nt in all_nonterminals}

        for nonterminal, rule in grammar.rules.items():
            for production in rule.productions:
                for symbol in production.symbols:
                    if symbol in grammar.rules:
                        dependency_graph[nonterminal].add(symbol)

        new_unproductive = set()
        for nt in unproductive:
            if all(dep in unproductive for dep in dependency_graph[nt]):
                new_unproductive.add(nt)

        if new_unproductive:
            return "Grammar is not productive. This nonterminals create a cycle: " + ",".join(sorted(new_unproductive))

    return None if len(unproductive) == 0 else "Grammar is not productive."


def validate_grammar(grammar: Grammar, start_symbol: str) -> str | None:
    if not check_reachability(grammar, start_symbol):
        return 'Grammar is not reachable from start symbol.'

    return check_productivity(grammar)
