from typing import Dict

from src.common.store import Store


class DataCenter:
    """
    this class defines a centralized place to hold all the data required for optimization
    """

    def __init__(self):
        # store id -> store
        self._stores: Dict[int, Store] = {}

    @property
    def stores(self):
        return self._stores
