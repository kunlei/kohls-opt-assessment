from typing import Dict

from src.common.data_center import DataCenter


class Validator:
    """
    this class is responsible for validating the various model outputs to make sure all the
    operational constraints are met.
    """

    def __init__(self, data_center: DataCenter):
        self._data_center = data_center

    def validate_model1_solution(self, assortment: Dict[int, Dict[str, int]]) -> Dict[str, str]:
        """
        validate model 1 result
        :param assortment: model 1 output
        :return: error message if any
        """
        errors = {}
        error_pizza_count = self._check_max_pizza_count(assortment)
        if len(error_pizza_count) > 0:
            errors.update(error_pizza_count)

        error_budget = self._check_max_budget(assortment)
        if len(error_budget) > 0:
            errors.update(error_budget)

        return errors

    def validate_model2_solution(self, assortment: Dict[int, Dict[str, int]],
                                 group_assignment: Dict[int, Dict[str, Dict[int, int]]]) -> Dict[str, str]:
        """
        validate model 2 result
        :param assortment: model 2 output
        :return: error message if any
        """
        errors = {}
        error_pizza_count = self._check_max_pizza_count(assortment)
        if len(error_pizza_count) > 0:
            errors.update(error_pizza_count)

        error_budget = self._check_max_budget(assortment)
        if len(error_budget) > 0:
            errors.update(error_budget)

        error_group = self._check_pizza_type_groups(assortment, group_assignment)
        if len(error_group) > 0:
            errors.update(error_group)

        return errors

    def _check_max_pizza_count(self, assortment: Dict[int, Dict[str, int]]) -> Dict[int, str]:
        """
        this function checks if the total number of displayed pizzas exceeds the given limit
        :param assortment: input assortment for validation
        :return: error messages if any
        """
        error_msg = {}
        for store_id in assortment.keys():
            total_count = sum(assortment[store_id].values())
            if total_count > self._data_center.max_pizza_count:
                error_msg[store_id] = (f'pizza count observed - allocated: {total_count}, '
                                       f'limit: {self._data_center.max_pizza_count}')
        return error_msg

    def _check_max_budget(self, assortment: Dict[int, Dict[str, int]]) -> Dict[int, str]:
        """
        this function checks if the budget constraint is violated or not
        :param assortment: assortment for validation
        :return: error message if any
        """
        total_costs = 0
        for store_id in assortment.keys():
            store = self._data_center.stores[store_id]
            for pizza_type in assortment[store_id]:
                total_costs += assortment[store_id][pizza_type] * store.costs[pizza_type]
        error_msg = {}
        if total_costs > self._data_center.max_budget:
            error_msg = {f"budget breach observed - used: {total_costs}, limit: {self._data_center.max_budget}"}
        return error_msg

    def _check_pizza_type_groups(self, assortment: Dict[int, Dict[str, int]],
                                 group_assignment: Dict[int, Dict[str, Dict[int, int]]]) -> Dict[int, str]:
        """
        this function checks if whether
        1) each pizza type has exactly three groups and
        2) each group has at least two stores
        3) all stores in the same group have the same number of pizzas
        :param assortment: assortment for validation
        :param group_assignment: store-type-group assignment results
        :return: error message if any
        """
        groups_by_type = {}
        for pizza_type in self._data_center.pizza_types:
            groups_by_type[pizza_type] = {
                group: {}
                for group in range(self._data_center.num_pizza_groups)
            }

        for store_id, count_per_type in assortment.items():
            for pizza_type, count in count_per_type.items():
                group_assign = group_assignment[store_id][pizza_type]
                for group, indicator in group_assign.items():
                    if indicator == 1:
                        groups_by_type[pizza_type][group][store_id] = count

        import pandas as pd
        df = pd.DataFrame.from_dict(groups_by_type, orient='index')
        df.index.name = 'pizza type'
        df.columns.name = 'pizza group'
        print("\nshow store groups by pizza type: ")
        print(df)

        error_msg = {}
        for pizza_type in self._data_center.pizza_types:
            groups = groups_by_type[pizza_type]
            for group, store_allocation in groups.items():
                if len(store_allocation) < 2:
                    # not enough stores assigned to a group
                    error_msg[(pizza_type, group)] = (f"not enough stores assigned to group: {group} "
                                                      f"for pizza type: {pizza_type}")

                # check if all the stores in the same group have the same allocation or not
                if len(set(store_allocation.values())) != 1:
                    error_msg[(pizza_type, group)] += (f"stores have different allocations in group: {group}"
                                                       f"for pizza type: {pizza_type}")

        return error_msg
