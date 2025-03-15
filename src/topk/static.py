
def diverse_top_k(items, K, diversity_constraints):
    """
    Selects K items maximizing utility while ensuring diversity constraints.

    :param items: List of tuples (score, category, item_id), sorted by decreasing score.
    :param K: Total number of items to select.
    :param diversity_constraints: Dict {category: (floor, ceil)}
    :return: List of selected item IDs.
    """
    selected = []
    category_count = {k_: 0 for k_ in diversity_constraints}

    # Compute slack
    floor_sum = sum(f for f, _ in diversity_constraints.values())
    slack = K - floor_sum

    for score, category, item_id in items:
        floor, ceil = diversity_constraints[category]

        # Always select items needed to meet floor constraints
        if category_count[category] < floor:
            selected.append(item_id)
            category_count[category] += 1
        elif category_count[category] < ceil and slack > 0:
            selected.append(item_id)
            category_count[category] += 1
            slack -= 1

        if len(selected) == K:
            break

    return selected
