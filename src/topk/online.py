import math
import heapq


class Heap:
    def __init__(self, capacity: int):
        self._capacity = capacity
        self._list = []

    def pop(self):
        return heapq.heappop(self._list)

    def push(self, item, item_id):
        if len(self._list) == self._capacity:
            if not self.is_empty() and item > self._list[0][0]:
                self.pop()
            else:
                return
        heapq.heappush(self._list, (item, item_id))

    def is_empty(self):
        return len(self._list) == 0

    def min_value(self):
        if self.is_empty():
            return -1.0
        return self._list[0][0]

    # def complete_minus_1(self):
    #     self._list = [(-1.0, -1)] * (self._capacity - len(self._list)) + self._list




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
    heaps = {category: Heap(capacity=floor) for category, (floor, _) in diversity_constraints.items()}

    floor_sum = sum(f for f, _ in diversity_constraints.values())
    slack = K - floor_sum
    N = len(items)
    r = math.floor(warmup_ratio * (N / math.e))
    T = Heap(capacity=slack)
    total_seen = 0

    for score, category, item_id in items:
        floor, ceil = diversity_constraints[category]
        if total_seen < r:
            T.push(score, item_id)
        if visited_categories[category] < R[category]:
            heaps[category].push(score, item_id)
        # ((ki < floori)∧(score(x) > дetMinElement(Ti))∨(ni −mi == floori −ki)
        elif (num_items_category[category] < floor and score > heaps[category].min_value()) or category_count[category] - \
                visited_categories[category] == floor - num_items_category[category]:

            if not heaps[category].is_empty():
                heaps[category].pop()

            selected.append(item_id)
            num_items_category[category] += 1
        elif total_seen >= r and score > T.min_value() and num_items_category[category] < ceil and slack > 0:
            if not T.is_empty():
                T.pop()
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
