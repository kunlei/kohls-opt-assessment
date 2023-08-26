from typing import Dict, List

from src.common.store import Store


class DataCenter:
    """
    this class defines a centralized place to hold all the data required for optimization
    """

    def __init__(self):
        # store id -> store
        self._stores: Dict[int, Store] = {}
        self._pizza_types: List[str] = ["A", "B", "C"]

        self._max_pizza_count = 20
        self._max_budget = 100_000

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
