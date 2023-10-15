from itertools import combinations


def create_all_pairs_from_list(list_of_value):
    return set(combinations(list_of_value, 2))


def get_dict_shared_items(x, y):
    shared_items = {k: x[k] for k in x if k in y and x[k] == y[k]}
    return shared_items
