import random
import math


def assign_minimum_diversity(K, count_per_category):
    """
    Implements the Minimum Diversity Constraint logic.

    :param K: Number of items to select.
    :param num_items_category: Dictionary {category: total available items (n_j)}
    :return: Dictionary {category: (floor, ceil)}
    """
    diversity_constraints = {}

    d = len(count_per_category)  # Total number of categories

    # Case 1: If K ≥ d, cover all categories
    if K >= d:
        # Set floor_i = ceil_i = 1 for all categories
        diversity_constraints = {category: (1, 1) for category in count_per_category}

        # Compute remaining slots
        r = K - d

        # TODO: What if there is not such j

        # If there are extra positions, assign them to random categories with enough items
        if r > 0:
            eligible_categories = [category for category, count in count_per_category.items() if
                                   count >= diversity_constraints[category][1] + r]

            chosen_category = random.choice(eligible_categories)
            floor, ceil = diversity_constraints[chosen_category]
            diversity_constraints[chosen_category] = (floor, ceil + 1)

    # Case 2: If K < d, select K categories at random and exclude others
    else:
        # Select K random categories to receive floor_i = ceil_i = 1
        selected_categories = random.sample(list(count_per_category.keys()), K)

        # Assign constraints
        diversity_constraints = {category: (1, 1) if category in selected_categories else (0, 0) for category in
                                 count_per_category}

    return diversity_constraints


def assign_average_diversity(K, num_items_category):
    """
    Implements the Average Diversity Constraint logic.

    :param K: Number of items to select.
    :param num_items_category: Dictionary {category: total available items (n_j)}
    :return: Dictionary {category: (floor, ceil)}
    """

    d = len(num_items_category)  # Total number of categories

    # Case 1: If K ≥ d, assign equal numbers per category
    if K >= d:
        # Compute initial floor and ceil constraints
        floor_constraints = {category: min(math.floor(K / d), num_items_category[category]) for category in
                             num_items_category}
        ceil_constraints = {category: min(math.ceil(K / d), num_items_category[category]) for category in
                            num_items_category}

        # Compute r = sum(ceil_i)
        r = sum(ceil_constraints.values())

        # If r < K, assign remaining slots to random eligible categories
        remaining_slots = K - r
        if remaining_slots > 0:
            eligible_categories = [category for category, count in num_items_category.items() if
                                   count >= ceil_constraints[category] + r]

            chosen_category = random.choice(eligible_categories)
            ceil_constraints[chosen_category] += r

        # Merge floor and ceil constraints into final dictionary
        diversity_constraints = {category: (floor_constraints[category], ceil_constraints[category]) for category in
                                 num_items_category}

    # Case 2: If K < d, assign as per Minimum Diversity
    else:
        selected_categories = random.sample(list(num_items_category.keys()), K)
        diversity_constraints = {category: (1, 1) if category in selected_categories else (0, 0) for category in
                                 num_items_category}

    return diversity_constraints


def assign_proportion_diversity(K, num_items_category):
    """
    Implements the Proportional Diversity Constraint logic.

    :param K: Number of items to select.
    :param num_items_category: Dictionary {category: total available items (n_j)}
    :return: Dictionary {category: (floor, ceil)}
    """
    diversity_constraints = {}

    d = len(num_items_category)  # Total number of categories
    N = sum(num_items_category.values())  # Total number of available items

    # Case 1: If K ≥ d, allocate proportionally
    if K >= d:
        # Compute proportional allocation for each category
        floor_constraints = {category: math.floor(K * (num_items_category[category] / N)) for category in
                             num_items_category}
        ceil_constraints = {category: math.ceil(K * (num_items_category[category] / N)) for category in
                            num_items_category}

        # Merge floor and ceil constraints into final dictionary
        diversity_constraints = {category: (floor_constraints[category], ceil_constraints[category]) for category in
                                 num_items_category}

    # Case 2: If K < d, use Minimum Diversity allocation
    else:
        selected_categories = random.sample(list(num_items_category.keys()), K)
        diversity_constraints = {category: (1, 1) if category in selected_categories else (0, 0) for category in
                                 num_items_category}

    return diversity_constraints


def assign_relaxed_average_diversity(K, num_items_category, t):
    """
    Implements the Relaxed Average Diversity Constraint logic.

    :param K: Number of items to select.
    :param num_items_category: Dictionary {category: total available items (n_j)}
    :param t: Tightness threshold (integer).
    :return: Dictionary {category: (floor, ceil)}
    """
    diversity_constraints = {}

    d = len(num_items_category)  # Total number of categories

    # Case 1: If K ≥ d, assign equal numbers per category with relaxation
    if K >= d:
        # Compute initial floor and ceil constraints using Average Diversity Constraint
        floor_constraints = {category: min(math.floor(K / d), num_items_category[category]) for category in
                             num_items_category}
        ceil_constraints = {category: min(math.ceil(K / d), num_items_category[category]) for category in
                            num_items_category}

        # Apply relaxation: Adjust floor and ceil within limits
        floor_constraints = {category: max(floor_constraints[category] - t, 0) for category in num_items_category}
        ceil_constraints = {category: min(ceil_constraints[category] + t, num_items_category[category]) for category in
                            num_items_category}

        # Merge floor and ceil constraints into final dictionary
        diversity_constraints = {category: (floor_constraints[category], ceil_constraints[category]) for category in
                                 num_items_category}

    # Case 2: If K < d, use Minimum Diversity allocation
    else:
        selected_categories = random.sample(list(num_items_category.keys()), K)
        diversity_constraints = {category: (1, 1) if category in selected_categories else (0, 0) for category in
                                 num_items_category}

    return diversity_constraints


def assign_relaxed_proportion_diversity(K, num_items_category, t):
    """
    Implements the Relaxed Proportion Diversity Constraint logic.

    :param K: Number of items to select.
    :param num_items_category: Dictionary {category: total available items (n_j)}
    :param t: Tightness threshold (integer).
    :return: Dictionary {category: (floor, ceil)}
    """
    diversity_constraints = {}

    d = len(num_items_category)  # Total number of categories
    N = sum(num_items_category.values())  # Total number of available items

    # Case 1: If K ≥ d, allocate proportionally with relaxation
    if K >= d:
        # Compute proportional allocation for each category
        floor_constraints = {category: math.floor(K * (num_items_category[category] / N)) for category in
                             num_items_category}
        ceil_constraints = {category: math.ceil(K * (num_items_category[category] / N)) for category in
                            num_items_category}

        # Apply relaxation: Adjust floor and ceil within limits
        floor_constraints = {category: max(floor_constraints[category] - t, 0) for category in num_items_category}
        ceil_constraints = {category: min(ceil_constraints[category] + t, num_items_category[category]) for category in
                            num_items_category}

        # Merge floor and ceil constraints into final dictionary
        diversity_constraints = {category: (floor_constraints[category], ceil_constraints[category]) for category in
                                 num_items_category}

    # Case 2: If K < d, use Minimum Diversity allocation
    else:
        selected_categories = random.sample(list(num_items_category.keys()), K)
        diversity_constraints = {category: (1, 1) if category in selected_categories else (0, 0) for category in
                                 num_items_category}

    return diversity_constraints
