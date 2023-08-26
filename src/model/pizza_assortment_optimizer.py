import logging
import cvxpy as cpy
from typing import Dict, List
import pandas as pd

from src.common.store import Store
from src.common.data_center import DataCenter


class PizzaAssortmentOptimizer:
    """
    this class aims to find the optimal number of pizzas for each store
    """

    def __init__(self):
        self._data_center: DataCenter = None
        # store + type -> integer variable
        self._var_pizza_count: Dict[int, Dict[str, cpy.Variable]] = {}
        self._objective = None
        self._constraints: List = []
        self._problem: cpy.Problem = None

        # optimal solution
        self._opt_obj: float = None
        self._opt_pizza_count: Dict[int, Dict[str, int]] = {}

    def optimize(self, data_center: DataCenter):
        logging.info("PizzaAssortOptimizer optimizer() starts.")
        self._data_center = data_center

        # build model
        self._create_variables()
        self._create_objective()
        self._create_constr_max_pizza_count()
        self._create_constr_max_budget()
        self._create_constr_variable_types()
        self._problem = cpy.Problem(self._objective, self._constraints)

        # solve the problem
        self._problem.solve(solver=cpy.MOSEK, verbose=True)

        # obtain optimal solution
        if self._problem.status == "optimal":
            logging.info(f"solve success, opt_obj: {self._problem.value}")
            self._opt_obj = float(self._problem.value)
            self._retrieve_opt_values()
            self._show_opt_values()
        else:
            logging.info(f"solve failure, status: {self._problem.status}")

        logging.info("PizzaAssortOptimizer optimizer() completes.")

    def _create_variables(self):
        for store_id, store in self._data_center.stores.items():
            var_per_type = {
                pizza_type: cpy.Variable(name=f"x_s{store_id}_t{pizza_type}",
                                         integer=True)
                for pizza_type in store.prices
            }
            self._var_pizza_count[store_id] = var_per_type
        logging.info("finish creating decision variables.")

    def _create_objective(self):
        obj_expr = [
            store.prices[pizza_type] *
            store.alpha[pizza_type] *
            self._var_pizza_count[store_id][pizza_type] ** store.beta[pizza_type]
            for store_id, store in self._data_center.stores.items()
            for pizza_type in self._data_center.pizza_types
        ]
        self._objective = cpy.Maximize(cpy.sum(obj_expr))
        logging.info("finish creating objective function.")

    def _create_constr_max_pizza_count(self):
        for store in self._data_center.stores.values():
            constr_expr = [
                self._var_pizza_count[store.id][pizza_type]
                for pizza_type in self._data_center.pizza_types
            ]
            self._constraints.append(cpy.sum(constr_expr) <= self._data_center.max_pizza_count)
        logging.info("finish creating max pizza count constraints.")

    def _create_constr_max_budget(self):
        constr_expr = [
            self._var_pizza_count[store.id][pizza_type] * store.costs[pizza_type]
            for store in self._data_center.stores.values()
            for pizza_type in self._data_center.pizza_types
        ]
        self._constraints.append(cpy.sum(constr_expr) <= self._data_center.max_budget)
        logging.info("finish creating the budget constraint.")

    def _create_constr_variable_types(self):
        for store in self._data_center.stores.values():
            for pizza_type in self._data_center.pizza_types:
                self._constraints.append(self._var_pizza_count[store.id][pizza_type] >= 0)
                self._constraints.append(
                    self._var_pizza_count[store.id][pizza_type] <= self._data_center.max_pizza_count
                )
        logging.info("finish creating variable bound constraints.")

    def _retrieve_opt_values(self):
        for store in self._data_center.stores.values():
            opt_count = {
                pizza_type: round(float(self._var_pizza_count[store.id][pizza_type].value))
                for pizza_type in self._data_center.pizza_types
            }
            self._opt_pizza_count[store.id] = opt_count
        logging.info("finish retrieving the optimal solution from solver.")

    def _show_opt_values(self):
        df = pd.DataFrame(self._opt_pizza_count)
        print(df)

    @property
    def maximal_profits(self):
        return self._opt_obj

    @property
    def optimal_assortment(self):
        return self._opt_pizza_count
