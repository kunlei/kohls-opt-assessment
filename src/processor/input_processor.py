import pandas as pd
import logging

from src.common.store import Store
from src.common.data_center import DataCenter


class InputProcessor:
    """
    this class defines processors to parse input from various data sources
    """

    def __init__(self):
        pass

    def process(self, pizza_data: pd.DataFrame) -> DataCenter:
        logging.info("InputProcessor starts.")
        data_center = DataCenter()
        stores = data_center.stores

        for idx, row in pizza_data.iterrows():
            store_id = row['store']
            if store_id not in stores:
                # create a new store if not exists
                stores[store_id] = Store(store_id)

            # parse and save store data
            pizza_type = str(row['type'])
            price = row['price']
            cost = row['cost']
            alpha = row['alpha']
            beta = row['beta']
            store = stores[store_id]
            store.prices[pizza_type] = price
            store.costs[pizza_type] = cost
            store.alpha[pizza_type] = alpha
            store.beta[pizza_type] = beta

        logging.info("InputProcessor completes.")
        return data_center
