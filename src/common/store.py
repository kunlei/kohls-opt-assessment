from typing import Dict
import logging


class Store:
    """
    this class defines a data container to hold all the data related to a specific store
    """

    def __init__(self, store_id: int):
        """
        constructor
        """
        # unique store identifier
        self._id: int = store_id
        # pizza type -> price
        self._prices: Dict[str, float] = {}
        # pizza type -> cost
        self._costs: Dict[str, float] = {}
        # pizza type -> alpha value
        self._alpha: Dict[str, float] = {}
        # pizza type -> beta value
        self._beta: Dict[str, float] = {}

    @property
    def id(self) -> int:
        return self._id

    @property
    def prices(self) -> Dict[str, float]:
        return self._prices

    @prices.setter
    def prices(self, value) -> None:
        if type(value) is not dict:
            logging.error(f"invalid store prices: {value}")
        self._prices = value

    @property
    def costs(self) -> Dict[str, float]:
        return self._costs

    @costs.setter
    def costs(self, value) -> None:
        if type(value) is not dict:
            logging.error(f"invalid store costs: {value}")
        self._costs = value

    @property
    def alpha(self) -> Dict[str, float]:
        return self._alpha

    @alpha.setter
    def alpha(self, value) -> None:
        if type(value) is not dict:
            logging.error(f"invalid store alpha: {value}")
        self._alpha = value

    @property
    def beta(self) -> Dict[str, float]:
        return self._beta

    @beta.setter
    def beta(self, value) -> None:
        if type(value) is not dict:
            logging.error(f"invalid store beta: {value}")
        self._beta = value

    def __str__(self):
        return f"""id: {self._id}, prices: {self._prices},
        costs: {self._costs}, alpha: {self._alpha},
        beta: {self._beta}
        """
