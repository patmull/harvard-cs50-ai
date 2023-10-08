from itertools import combinations


def create_all_pairs_from_list(list_of_value):
    return set(combinations(list_of_value, 2))
