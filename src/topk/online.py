import math
import heapq


def online_diverse_selection(items, K, diversity_constraints, warmup_ratio = 1.0):
    """
    Implements the online version of the diverse selection algorithm.

    :param items: List of tuples (score, category, item_id), arriving in random order.
    :param K: Number of items to select.
    :param diversity_constraints: Dict {category: (floor, ceil)}
    :return: List of selected item IDs.
    """
    selected = []

    num_items_category = {k: 0 for k in diversity_constraints}
    visited_categories = {m: 0 for m in diversity_constraints}

    category_count = {c: 0 for c in diversity_constraints}
    for _, category, _ in items:
        category_count[category] += 1

    R = {category: math.floor(warmup_ratio * (category_count[category] / math.e)) for category in diversity_constraints}
    heaps = {category: [(floor, -1)] for category, (floor, ceil) in diversity_constraints.items()}

    floor_sum = sum(f for f, _ in diversity_constraints.values())
    slack = K - floor_sum
    N = len(items)
    r = math.floor(warmup_ratio * (N / math.e))
    T = [(slack, -1)]  # TODO maybe replace -1 with if statement
    total_seen = 0

    for score, category, item_id in items:
        floor, ceil = diversity_constraints[category]
        if total_seen < r:
            heapq.heappush(T, (score, item_id))
        if visited_categories[category] < R[category]:
            heapq.heappush(heaps[category], (score, item_id))
        # ((ki < floori)∧(score(x) > дetMinElement(Ti))∨(ni −mi == floori −ki)
        elif (num_items_category[category] < floor and score > heaps[category][0][0]) or category_count[category] - \
                visited_categories[category] == floor - num_items_category[category]:
            heapq.heappop(heaps[category])
            selected.append(item_id)
            num_items_category[category] += 1
        elif total_seen >= r and score > T[0][0] and num_items_category[category] < ceil and slack > 0:
            heapq.heappop(T)
            selected.append(item_id)
            num_items_category[category] += 1
            slack -= 1
        elif num_items_category[category] < ceil:
            num_feasible_items = sum(
                (category_count[category] - visited_categories[category])
                for category, (_, ceil) in diversity_constraints.items()
                if (ceil - num_items_category[category]) > 0)
            if num_feasible_items == (K - len(selected)):
                selected.append(item_id)
                num_items_category[category] += 1
                slack -= 1
        visited_categories[category] += 1
        total_seen += 1

        if len(selected) == K:
            break

    return selected, total_seen
