import simplify

def add_rule(rules, source, target, *tags):
    src = simplify.simplify_expr(source)
    tgt = simplify.simplify_expr(target)

    rules.append(simplify.Rule(src, tgt, *tags))
    if 'oneway' not in tags:
        rules.append(simplify.Rule(tgt, src, *tags))

def filter_rules(rules, *tags):
    filtered_rules = []

    for rule in rules:
        for tag in rule.tags:
            if tag in tags:
                filtered_rules.append(rule)

    return filtered_rules
