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

    @property
    def stores(self) -> Dict[int, Store]:
        return self._stores

    @property
    def pizza_types(self) -> List[str]:
        return self._pizza_types
