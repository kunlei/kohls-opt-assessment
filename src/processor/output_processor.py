from typing import Dict
import pandas as pd


class OutputProcessor:

    def __init__(self):
        pass

    def process(self, assortment: Dict[int, Dict[str, int]]) -> pd.DataFrame:
        df = pd.DataFrame.from_dict(assortment, orient='index')
        df.index.name = 'store'
        df.columns.name = 'pizza type'
        return df
