import logging
import cvxpy as cpy
from typing import Dict, List
import pandas as pd

from src.common.data_center import DataCenter


class PizzaAssortmentOptimizerWtGroup:
    """
    this class aims to find the optimal number of pizzas for each store, with
    extra operational constraints
    """

    def __init__(self):
        self._data_center: DataCenter = None
        # store + type -> integer variable
        self._var_count_per_store_type: Dict[int, Dict[str, cpy.Variable]] = {}
        # store + type + group -> integer variable
        self._var_count_per_store_type_group: Dict[int, Dict[str, Dict[int, cpy.Variable]]] = {}
        # store + type + group -> binary variable
        self._var_assign_store_type_group: Dict[int, Dict[str, Dict[int, cpy.Variable]]] = {}
        # type + group -> integer variable
        self._var_count_per_type_group: Dict[str, Dict[int, cpy.Variable]] = {}
        self._objective = None
        self._constraints: List = []
        self._problem: cpy.Problem = None
        self._BIG_M = None

        # optimal solution
        self._opt_obj: float = None
        self._opt_count_per_store_type = {}
        self._opt_count_per_store_type_group = {}
        self._opt_assign_store_type_group = {}
        self._opt_count_per_type_group = {}

    def optimize(self, data_center: DataCenter):
        logging.info("PizzaAssortOptimizerWtGroup optimizer() starts.")
        self._data_center = data_center
        self._BIG_M = self._data_center.max_pizza_count

        # build model
        self._create_variables()
        self._create_objective()
        self._create_constr_max_pizza_count()
        self._create_constr_max_budget()
        self._create_constr_derive_count_per_store_type()
        self._create_constr_enforce_one_group_per_pizza_type()
        self._create_constr_min_stores_in_group()
        self._create_constr_linearization()
        self._create_constr_variable_types()
        self._problem = cpy.Problem(self._objective, self._constraints)

        # solve the problem
        self._problem.solve(solver=cpy.MOSEK, verbose=True,
                            mosek_params={'MSK_DPAR_OPTIMIZER_MAX_TIME': 20.0,
                                          'MSK_IPAR_INTPNT_SOLVE_FORM': 'MSK_SOLVE_DUAL'}
                            )

        # obtain optimal solution
        if self._problem.status not in ("infeasible", "unbounded"):
            logging.info(f"solve success, opt_obj: {self._problem.value}")
            self._opt_obj = float(self._problem.value)
            self._retrieve_opt_values()
            self._show_opt_values()
        else:
            logging.info(f"solve failure, status: {self._problem.status}")

        logging.info("PizzaAssortOptimizerWtGroup optimizer() completes.")

    def _create_variables(self):
        # store + type -> pizza count variable
        for store_id, store in self._data_center.stores.items():
            var_per_type = {
                pizza_type: cpy.Variable(name=f"x_s{store_id}_t{pizza_type}",
                                         integer=True)
                for pizza_type in store.prices
            }
            self._var_count_per_store_type[store_id] = var_per_type

        # store + type + group -> pizza count variables
        for store_id, store in self._data_center.stores.items():
            var_per_type = {}
            for pizza_type in self._data_center.pizza_types:
                var_per_group = {
                    group: cpy.Variable(name=f"v_s{store_id}_t{pizza_type}_g{group}",
                                        integer=True)
                    for group in range(self._data_center.num_pizza_groups)
                }
                var_per_type[pizza_type] = var_per_group
            self._var_count_per_store_type_group[store_id] = var_per_type

        # store + type + group -> binary assignment variable
        for store_id, store in self._data_center.stores.items():
            var_per_type = {}
            for pizza_type in self._data_center.pizza_types:
                var_per_group = {
                    group: cpy.Variable(name=f"y_s{store_id}_t{pizza_type}_g{group}",
                                        integer=True)
                    for group in range(self._data_center.num_pizza_groups)
                }
                var_per_type[pizza_type] = var_per_group
            self._var_assign_store_type_group[store_id] = var_per_type

        # type + group -> integer variable
        for pizza_type in self._data_center.pizza_types:
            var_per_group = {
                group: cpy.Variable(name=f"z_t{pizza_type}_g{group}",
                                    integer=True)
                for group in range(self._data_center.num_pizza_groups)
            }
            self._var_count_per_type_group[pizza_type] = var_per_group
        logging.info("finish creating decision variables.")

    def _create_objective(self):
        obj_expr = [
            store.prices[pizza_type] *
            store.alpha[pizza_type] *
            self._var_count_per_store_type[store_id][pizza_type] ** store.beta[pizza_type]
            for store_id, store in self._data_center.stores.items()
            for pizza_type in self._data_center.pizza_types
        ]
        self._objective = cpy.Maximize(cpy.sum(obj_expr))
        logging.info("finish creating objective function.")

    def _create_constr_max_pizza_count(self):
        for store in self._data_center.stores.values():
            constr_expr = [
                self._var_count_per_store_type[store.id][pizza_type]
                for pizza_type in self._data_center.pizza_types
            ]
            self._constraints.append(cpy.sum(constr_expr) <= self._data_center.max_pizza_count)
        logging.info("finish creating max pizza count constraints.")

    def _create_constr_max_budget(self):
        constr_expr = [
            self._var_count_per_store_type[store.id][pizza_type] * store.costs[pizza_type]
            for store in self._data_center.stores.values()
            for pizza_type in self._data_center.pizza_types
        ]
        self._constraints.append(cpy.sum(constr_expr) <= self._data_center.max_budget)
        logging.info("finish creating the budget constraint.")

    def _create_constr_derive_count_per_store_type(self):
        for store_id, store in self._data_center.stores.items():
            for pizza_type in self._data_center.pizza_types:
                constr_expr = [
                    self._var_count_per_store_type_group[store_id][pizza_type][group]
                    for group in range(self._data_center.num_pizza_groups)
                ]
                self._constraints.append(cpy.sum(constr_expr) == self._var_count_per_store_type[store_id][pizza_type])
        logging.info("finish creating linking constraints.")

    def _create_constr_enforce_one_group_per_pizza_type(self):
        for store_id, store in self._data_center.stores.items():
            for pizza_type in self._data_center.pizza_types:
                constr_expr = [
                    self._var_assign_store_type_group[store_id][pizza_type][group]
                    for group in range(self._data_center.num_pizza_groups)
                ]
                self._constraints.append(cpy.sum(constr_expr) == 1)
        logging.info("finish creating constraints to make sure a pizza type is assigned to only one group.")

    def _create_constr_min_stores_in_group(self):
        for pizza_type in self._data_center.pizza_types:
            for group in range(self._data_center.num_pizza_groups):
                constr_expr = [
                    self._var_assign_store_type_group[store_id][pizza_type][group]
                    for store_id in self._data_center.stores.keys()
                ]
                self._constraints.append(cpy.sum(constr_expr) >= 2)
        logging.info("finish creating constraints to limit min. no. of stores in a group.")

    def _create_constr_linearization(self):
        for store_id, store in self._data_center.stores.items():
            for pizza_type in self._data_center.pizza_types:
                for group in range(self._data_center.num_pizza_groups):
                    self._constraints.append(
                        self._var_count_per_store_type_group[store_id][pizza_type][group] >=
                        self._var_count_per_type_group[pizza_type][group] -
                        self._BIG_M * (1 - self._var_assign_store_type_group[store_id][pizza_type][group])
                    )
                    self._constraints.append(
                        self._var_count_per_store_type_group[store_id][pizza_type][group] <=
                        self._BIG_M * self._var_assign_store_type_group[store_id][pizza_type][group]
                    )
                    self._constraints.append(
                        self._var_count_per_store_type_group[store_id][pizza_type][group] >= 0
                    )
                    self._constraints.append(
                        self._var_count_per_store_type_group[store_id][pizza_type][group] <=
                        self._var_count_per_type_group[pizza_type][group]
                    )
        logging.info("finish creating linearization constraints.")

    def _create_constr_variable_types(self):
        for store_id, store in self._data_center.stores.items():
            for pizza_type in self._data_center.pizza_types:
                self._constraints.append(self._var_count_per_store_type[store_id][pizza_type] >= 0)
                self._constraints.append(
                    self._var_count_per_store_type[store_id][pizza_type] <= self._data_center.max_pizza_count)

                for group in range(self._data_center.num_pizza_groups):
                    self._constraints.append(self._var_count_per_store_type_group[store_id][pizza_type][group] >= 0)
                    self._constraints.append(self._var_count_per_store_type_group[store_id][pizza_type][
                                                 group] <= self._data_center.max_pizza_count)

                    self._constraints.append(self._var_assign_store_type_group[store_id][pizza_type][group] >= 0)
                    self._constraints.append(self._var_assign_store_type_group[store_id][pizza_type][group] <= 1)

        for pizza_type in self._data_center.pizza_types:
            for group in range(self._data_center.num_pizza_groups):
                self._constraints.append(self._var_count_per_type_group[pizza_type][group] >= 0)
                self._constraints.append(
                    self._var_count_per_type_group[pizza_type][group] <= self._data_center.max_pizza_count)
        logging.info("finish creating data type variables.")

    def _retrieve_opt_values(self):
        # retrieve optimal values for _var_count_per_store_type
        for store_id, store in self._data_center.stores.items():
            opt_count_per_type = {}
            for pizza_type in self._data_center.pizza_types:
                opt_count_per_type[pizza_type] = round(
                    float(self._var_count_per_store_type[store_id][pizza_type].value))
            self._opt_count_per_store_type[store_id] = opt_count_per_type

        # retrieve optimal values for _var_count_per_store_type_group and _var_assign_store_type_group
        for store_id, store in self._data_center.stores.items():
            opt_count_per_store_type = {}
            opt_assign_per_store_type = {}
            for pizza_type in self._data_center.pizza_types:
                opt_count_per_group = {
                    group: round(float(self._var_count_per_store_type_group[store_id][pizza_type][group].value))
                    for group in range(self._data_center.num_pizza_groups)
                }
                opt_assign_per_group = {
                    group: round(float(self._var_assign_store_type_group[store_id][pizza_type][group].value))
                    for group in range(self._data_center.num_pizza_groups)
                }
                opt_count_per_store_type[pizza_type] = opt_count_per_group
                opt_assign_per_store_type[pizza_type] = opt_assign_per_group
            self._opt_count_per_store_type_group[store_id] = opt_count_per_store_type
            self._opt_assign_store_type_group[store_id] = opt_assign_per_store_type

        # retrieve optimal values for _var_count_type_group
        for pizza_type in self._data_center.pizza_types:
            opt_count_per_group = {
                group: round(float(self._var_count_per_type_group[pizza_type][group].value))
                for group in range(self._data_center.num_pizza_groups)
            }
            self._opt_count_per_type_group[pizza_type] = opt_count_per_group

    def _show_opt_values(self):
        df_x = pd.DataFrame.from_dict(self._opt_count_per_store_type, orient='index')
        df_x.index.name = 'store'
        df_x.columns.name = 'pizza type'
        print("\nshow pizza assortment results: ")
        print(df_x)

        df_v = pd.DataFrame.from_dict(self._opt_count_per_store_type_group, orient='index')
        df_v.index.name = 'store'
        df_v.columns.name = 'pizza type'
        print("\nshow pizza count in each pizza type: ")
        print(df_v)

        df_y = pd.DataFrame.from_dict(self._opt_assign_store_type_group, orient='index')
        df_y.index.name = 'store'
        df_y.columns.name = 'pizza type'
        print("\nshow store assignment in each pizza type: ")
        print(df_y)

        df_z = pd.DataFrame.from_dict(self._opt_count_per_type_group)
        df_z.index.name = 'group'
        df_z.columns.name = 'pizza type'
        print("\nshow pizza count for each group")
        print(df_z)

    @property
    def maximal_profits(self):
        return self._opt_obj

    @property
    def optimal_assortment(self):
        return self._opt_count_per_store_type

    @property
    def optimal_count_per_store_type_group(self):
        return self._opt_count_per_store_type_group

    @property
    def optimal_assign_store_type_group(self):
        return self._opt_assign_store_type_group

    @property
    def optimal_count_per_type_group(self):
        return self._opt_count_per_type_group
