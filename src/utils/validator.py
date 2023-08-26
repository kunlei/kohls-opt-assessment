from typing import Dict

from src.common.data_center import DataCenter

class Validator:

    def __init__(self, data_center: DataCenter):
        self._data_center = data_center

    def validate_model1_solution(self, assortment: Dict[int, Dict[str, int]]) -> Dict[str, str]:
        errors = {}
        error_pizza_count = self._check_max_pizza_count(assortment)
        if len(error_pizza_count) > 0:
            errors.update(error_pizza_count)

        error_budget = self._check_max_budget(assortment)
        if len(error_budget) > 0:
            errors.update(error_budget)

        return errors


    def validate_model2_solution(self, assortment: Dict[int, Dict[str, int]]) -> Dict[str, str]:
        errors = {}
        error_pizza_count = self._check_max_pizza_count(assortment)
        if len(error_pizza_count) > 0:
            errors.update(error_pizza_count)

        error_budget = self._check_max_budget(assortment)
        if len(error_budget) > 0:
            errors.update(error_budget)

        return errors

    def _check_max_pizza_count(self, assortment: Dict[int, Dict[str, int]]) -> Dict[int, str]:
        error_msg = {}
        for store_id in assortment.keys():
            total_count = sum(assortment[store_id].values())
            if total_count > self._data_center.max_pizza_count:
                error_msg[store_id] = f'pizza count observed - allocated: {total_count}, limit: {self._data_center.max_pizza_count}'
        return error_msg

    def _check_max_budget(self, assortment: Dict[int, Dict[str, int]]) -> Dict[int, str]:
        total_costs = 0
        for store_id in assortment.keys():
            store = self._data_center.stores[store_id]
            for pizza_type in assortment[store_id]:
                total_costs += assortment[store_id][pizza_type] * store.costs[pizza_type]
        error_msg = {}
        if total_costs > self._data_center.max_budget:
            error_msg = {f"budget breach observed - used: {total_costs}, limit: {self._data_center.max_budget}"}
        return error_msg


