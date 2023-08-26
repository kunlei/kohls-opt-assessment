import cvxpy as cpy
from typing import Dict, List
import pandas as pd

from src.common.store import Store
from src.common.data_center import DataCenter


class PizzaAssortOptimizer:
    MAX_PIZZA_PER_STORE = 20
    MAX_BUDGET = 100_000

    def __init__(self):
        self._data_center: DataCenter = None
        # store + type -> integer variable
        self._var_pizza_count = {}
        self._objective = None
        self._constraints = []
        self._problem = None

        # optimal solution
        self._opt_pizza_count = {}

    def optimize(self, data_center: DataCenter):
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
        print("status:", self._problem.status)
        print("optimal value", self._problem.value)
        self._retrieve_opt_values()
        self._show_opt_values()

    def _create_variables(self):
        stores: Dict[int, Store] = self._data_center.stores
        for store in stores.values():
            store_id = store.id
            var_per_type = {}
            for pizza_type in store.prices:
                var_per_type[pizza_type] = cpy.Variable(name=f"x_s{store_id}_t{pizza_type}",
                                                        integer=True)
            self._var_pizza_count[store_id] = var_per_type

    def _create_objective(self):
        stores: Dict[int, Store] = self._data_center.stores
        pizza_types: List[str] = self._data_center.pizza_types
        obj_expr = []
        for store in stores.values():
            prices = store.prices
            alpha = store.alpha
            beta = store.beta
            for pizza_type in pizza_types:
                expr = prices[pizza_type] * \
                       alpha[pizza_type] * \
                       self._var_pizza_count[store.id][pizza_type] ** beta[pizza_type]
                obj_expr.append(expr)
        self._objective = cpy.Maximize(cpy.sum(obj_expr))

    def _create_constr_max_pizza_count(self):
        stores: Dict[int, Store] = self._data_center.stores
        pizza_types: List[str] = self._data_center.pizza_types
        for store in stores.values():
            constr_expr = [self._var_pizza_count[store.id][pizza_type]
                           for pizza_type in pizza_types]
            self._constraints.append(cpy.sum(constr_expr) <= PizzaAssortOptimizer.MAX_PIZZA_PER_STORE)

    def _create_constr_max_budget(self):
        stores: Dict[int, Store] = self._data_center.stores
        pizza_types: List[str] = self._data_center.pizza_types
        expr = [
            self._var_pizza_count[store.id][pizza_type] * store.costs[pizza_type]
            for store in stores.values()
            for pizza_type in pizza_types
        ]
        self._constraints.append(cpy.sum(expr) <= PizzaAssortOptimizer.MAX_BUDGET)

    def _create_constr_variable_types(self):
        stores: Dict[int, Store] = self._data_center.stores
        pizza_types: List[str] = self._data_center.pizza_types
        for store in stores.values():
            for pizza_type in pizza_types:
                self._constraints.append(self._var_pizza_count[store.id][pizza_type] >= 0)
                self._constraints.append(self._var_pizza_count[store.id][pizza_type] <= PizzaAssortOptimizer.MAX_PIZZA_PER_STORE)

    def _retrieve_opt_values(self):
        stores: Dict[int, Store] = self._data_center.stores
        pizza_types: List[str] = self._data_center.pizza_types
        for store in stores.values():
            opt_count = {}
            for pizza_type in pizza_types:
                opt_count[pizza_type] = round(self._var_pizza_count[store.id][pizza_type].value)
            self._opt_pizza_count[store.id] = opt_count

    def _show_opt_values(self):
        df = pd.DataFrame(self._opt_pizza_count)
        print(df)
