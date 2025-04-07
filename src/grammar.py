from collections import defaultdict
from src.grammar_utils import Grammar, Rule, Production


def factorize_grammar(grammar: Grammar) -> Grammar:
    new_grammar = Grammar({})

    for nonterminal, rule in grammar.rules.items():
        # Группируем продукции с общими префиксами максимальной длины
        productions_by_prefix = find_common_prefixes(rule.productions)

        # Если нет продукций с общими префиксами, оставляем правило без изменений
        if len(productions_by_prefix) == len(rule.productions):
            new_grammar.rules[nonterminal] = rule
            continue

        new_rule = Rule(nonterminal, [])

        for prefix, productions in productions_by_prefix.items():
            if len(productions) == 1:
                # Если префикс уникален, добавляем продукцию без изменений
                new_rule.productions.append(productions[0])
                continue

            # Создаем новый нетерминал для общего префикса
            new_nonterminal = f"<{nonterminal.strip('<>')}'>"

            # Добавляем новую продукцию с общим префиксом и новым нетерминалом
            prefix_symbols = prefix.split('|')
            new_rule.productions.append(Production(prefix_symbols + [new_nonterminal], []))

            # Создаем правило для нового нетерминала с оставшимися частями продукций
            suffix_productions = []
            for production in productions:
                # Извлекаем суффикс после общего префикса
                suffix = production.symbols[len(prefix_symbols):]
                # Если суффикс пуст, добавляем эпсилон
                suffix_productions.append(Production(suffix or ["ε"], []))

            new_grammar.rules[new_nonterminal] = Rule(new_nonterminal, suffix_productions)

        new_grammar.rules[nonterminal] = new_rule

    # Проверяем, нужна ли дополнительная факторизация
    if any(len(find_common_prefixes(rule.productions)) < len(rule.productions)
           for rule in new_grammar.rules.values()):
        return factorize_grammar(new_grammar)

    return new_grammar


def find_common_prefixes(productions: list[Production]) -> dict[str, list[Production]]:
    """
    Находит общие префиксы максимальной длины среди продукций.
    Возвращает словарь, где ключ - это общий префикс (символы через |),
    а значение - список продукций с этим префиксом.
    """
    if not productions:
        return {}

    # Инициализируем результат уникальными продукциями
    result = {}
    processed = set()

    for i, prod1 in enumerate(productions):
        if i in processed:
            continue

        # Найдем все продукции с общим префиксом максимальной длины
        common_prefix = []
        common_productions = [prod1]
        processed.add(i)

        # Определяем максимальную длину общего префикса
        for j, prod2 in enumerate(productions[i + 1:], i + 1):
            if j in processed:
                continue

            # Находим длину общего префикса
            common_length = 0
            min_length = min(len(prod1.symbols), len(prod2.symbols))

            for k in range(min_length):
                if prod1.symbols[k] == prod2.symbols[k]:
                    common_length = k + 1
                else:
                    break

            # Если нашли общий префикс
            if common_length > 0:
                # Если это первый общий префикс или он длиннее текущего
                if not common_prefix or common_length >= len(common_prefix):
                    # Если он длиннее, сбрасываем список продукций
                    if common_length > len(common_prefix):
                        common_prefix = prod1.symbols[:common_length]
                        common_productions = [prod1, prod2]
                    else:
                        common_productions.append(prod2)
                    processed.add(j)

        # Добавляем найденный общий префикс в результат
        if len(common_productions) > 1:
            prefix_key = '|'.join(common_prefix)
            result[prefix_key] = common_productions
        else:
            # Для уникальных продукций используем первый символ как ключ
            prefix_key = f"{prod1.symbols[0] if prod1.symbols else 'ε'}_unique_{i}"
            result[prefix_key] = [prod1]

    return result


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


def topological_sort(graph: dict[str, set[str]], nonterminal: str) -> tuple[list[str], bool]:
    visited = []
    order = []

    def dfs(node: str) -> None:
        if node in visited:
            visited.append(node)
            return
        visited.append(node)
        for neighbor in graph[node]:
            if neighbor != node:
                dfs(neighbor)
        order.append(node)

    dfs(nonterminal)

    return order, len(visited) != len(order)


def remove_indirect_recursion(grammar: Grammar) -> Grammar:
    graph = build_dependency_graph(grammar)

    for node in graph:
        order, is_indirect = topological_sort(graph, node)
        order = order[:-1]
        if not is_indirect:
            continue

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

    return grammar


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


def calculate_directing_sets(grammar: Grammar) -> Grammar:
    # Step 1: Calculate FIRST sets for each symbol and production
    first_sets = {}

    # Initialize first sets for terminals and ε
    for rule in grammar.rules.values():
        for production in rule.productions:
            for symbol in production.symbols:
                if not symbol.startswith('<'):
                    first_sets[symbol] = {symbol}

    # Initialize empty first sets for nonterminals
    for nonterminal in grammar.rules:
        first_sets[nonterminal] = set()

    # Calculate first sets for nonterminals using fixed-point iteration
    changed = True
    while changed:
        changed = False
        for nonterminal, rule in grammar.rules.items():
            for production in rule.productions:
                # Process symbols in the production
                all_can_derive_empty = True
                for symbol in production.symbols:
                    if symbol == "ε":
                        continue

                    # If symbol is a terminal, add to FIRST and stop
                    if not symbol.startswith('<'):
                        if symbol not in first_sets[nonterminal]:
                            first_sets[nonterminal].add(symbol)
                            changed = True
                        all_can_derive_empty = False
                        break

                    # If symbol is a nonterminal, add its FIRST set (except ε)
                    # to the current nonterminal's FIRST set
                    for sym in first_sets.get(symbol, set()):
                        if sym != "ε" and sym not in first_sets[nonterminal]:
                            first_sets[nonterminal].add(sym)
                            changed = True

                    # If this symbol can't derive ε, stop adding symbols
                    if "ε" not in first_sets.get(symbol, set()):
                        all_can_derive_empty = False
                        break

                # If all symbols can derive ε, add ε to FIRST
                if all_can_derive_empty and "ε" not in first_sets[nonterminal]:
                    first_sets[nonterminal].add("ε")
                    changed = True

    # Step 2: Calculate FOLLOW sets
    follow_sets = {nonterminal: set() for nonterminal in grammar.rules}

    # Initialize FOLLOW set for start symbol with # (EOF marker)
    # Assuming the first rule in the grammar is the start symbol
    start_symbol = next(iter(grammar.rules))
    follow_sets[start_symbol].add("#")

    # Calculate FOLLOW sets using fixed-point iteration
    changed = True
    while changed:
        changed = False
        for nonterminal, rule in grammar.rules.items():
            for production in rule.productions:
                for i, symbol in enumerate(production.symbols):
                    # Skip terminals
                    if not symbol.startswith('<') or symbol == "ε":
                        continue

                    # Get FIRST of everything that follows this symbol
                    trailing_first = set()
                    all_can_derive_empty = True

                    # Check all symbols after the current one
                    for j in range(i + 1, len(production.symbols)):
                        next_symbol = production.symbols[j]
                        if next_symbol == "ε":
                            continue

                        # Add FIRST(next_symbol) to trailing_first, except ε
                        symbol_first = first_sets.get(next_symbol, {next_symbol})
                        for sym in symbol_first:
                            if sym != "ε":
                                trailing_first.add(sym)

                        # If this symbol can't derive ε, stop processing
                        if "ε" not in symbol_first:
                            all_can_derive_empty = False
                            break

                    # If all remaining symbols can derive ε, or we're at the end of the production,
                    # add FOLLOW(nonterminal) to FOLLOW(symbol)
                    if all_can_derive_empty or i == len(production.symbols) - 1:
                        for follow_sym in follow_sets[nonterminal]:
                            if follow_sym not in follow_sets[symbol]:
                                follow_sets[symbol].add(follow_sym)
                                changed = True

                    # Add trailing_first to FOLLOW(symbol)
                    for sym in trailing_first:
                        if sym not in follow_sets[symbol]:
                            follow_sets[symbol].add(sym)
                            changed = True

    # Step 3: Calculate directing sets for each production
    new_grammar = Grammar({})
    for nonterminal, rule in grammar.rules.items():
        new_rule = Rule(nonterminal, [])
        for production in rule.productions:
            # Calculate FIRST set of the production
            prod_first = calculate_production_first(production.symbols, first_sets)

            # Determine if this production can derive ε
            can_derive_empty = True
            for symbol in production.symbols:
                if symbol == "ε":
                    continue
                symbol_first = first_sets.get(symbol, {symbol})
                if "ε" not in symbol_first:
                    can_derive_empty = False
                    break

            # Calculate directing set
            directing_set = set()
            for sym in prod_first:
                if sym != "ε":
                    directing_set.add(sym)

            # If production can derive ε, add FOLLOW(nonterminal)
            if can_derive_empty or "ε" in prod_first:
                directing_set.update(follow_sets[nonterminal])

            # Create a new production with the directing set
            new_production = Production(
                symbols=production.symbols,
                first_set=[sym for sym in directing_set if sym != "ε"]
            )
            new_rule.productions.append(new_production)

        new_grammar.rules[nonterminal] = new_rule

    return new_grammar


def calculate_production_first(symbols: list[str], first_sets: dict[str, set[str]]) -> set[str]:
    """Calculate the FIRST set of a sequence of symbols"""
    if not symbols or symbols[0] == "ε":
        return {"ε"}

    result = set()
    all_can_derive_empty = True

    for symbol in symbols:
        if symbol == "ε":
            continue

        # If terminal, add to result and stop
        if not symbol.startswith('<'):
            result.add(symbol)
            all_can_derive_empty = False
            break

        # Add all non-ε symbols from FIRST(symbol)
        symbol_first = first_sets.get(symbol, set())
        for sym in symbol_first:
            if sym != "ε":
                result.add(sym)

        # If this symbol can't derive ε, stop
        if "ε" not in symbol_first:
            all_can_derive_empty = False
            break

    # If all symbols can derive ε, add ε to result
    if all_can_derive_empty:
        result.add("ε")

    return result
