from typing import Dict, List

from src.common.store import Store


class DataCenter:
    """
    this class defines a centralized place to hold all the data required for optimization
    """

    def __init__(self):
        # store id -> store
        self._stores: Dict[int, Store] = {}
        # all the available pizza types
        self._pizza_types: List[str] = ["A", "B", "C"]
        # max. no. of pizza a store can display
        self._max_pizza_count = 20
        # max. budget across the chain
        self._max_budget = 100_000
        # number of groups for each pizza type
        self._num_pizza_groups = 3

    @property
    def stores(self) -> Dict[int, Store]:
        return self._stores

    @property
    def pizza_types(self) -> List[str]:
        return self._pizza_types

    @property
    def max_pizza_count(self):
        return self._max_pizza_count

    @property
    def max_budget(self):
        return self._max_budget

    @property
    def num_pizza_groups(self):
        return self._num_pizza_groups
