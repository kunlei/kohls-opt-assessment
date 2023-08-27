from gekko import GEKKO
import os
import pandas as pd

from src.common.data_center import DataCenter
from src.processor.input_processor import InputProcessor
from src.processor.output_processor import OutputProcessor
from src.utils.validator import Validator
from src.model.pizza_assortment_optimizer import PizzaAssortmentOptimizer
from src.model.pizza_assortment_optimizer_group import PizzaAssortmentOptimizerWtGroup
import logging

logging.basicConfig(level=logging.INFO)


class OptService:
    """
    this class defines an optimization interface that provides service to solve the pizza assortment problem
    """

    def __init__(self):
        logging.info("OptService constructor starts.")
        # parse inputs
        self._input_processor = InputProcessor()
        # model 1 optimizer
        self._pizza_assortment_optimizer = PizzaAssortmentOptimizer()
        # model 2 optimizer
        self._pizza_assortment_optimizer_wt_group = PizzaAssortmentOptimizerWtGroup()
        # result validator
        self._validator = None
        # process output
        self._output_processor = OutputProcessor()
        logging.info("OptService constructor completes.")

    def optimize(self, pizza_data: pd.DataFrame, enable_group_constraint: bool):
        logging.info("OptService optimize() starts.")
        # process input for optimizer use
        data_center: DataCenter = self._input_processor.process(pizza_data)
        self._validator = Validator(data_center)

        if enable_group_constraint:
            # solve model 2
            self._pizza_assortment_optimizer_wt_group.optimize(data_center)
            optimal_assortment = self._pizza_assortment_optimizer_wt_group.optimal_assortment
            error_msg = self._validator.validate_model2_solution(optimal_assortment)
        else:
            # solve model 1
            self._pizza_assortment_optimizer.optimize(data_center)
            optimal_assortment = self._pizza_assortment_optimizer.optimal_assortment
            error_msg = self._validator.validate_model1_solution(optimal_assortment)

        if len(error_msg) > 0:
            logging.error(error_msg)

        logging.info("OptService optimize() completes.")
        return optimal_assortment, error_msg


if __name__ == "__main__":
    data_path = "/Users/klian/dev/learn/python/kohls-opt-assessment/tests/data"
    pizza_file = os.path.join(data_path, "new_pizza.csv")
    pizza = pd.read_csv(pizza_file)

    opt_service = OptService()
    opt_service.optimize(pizza, False)

    # m = GEKKO()  # Initialize gekko
    # m.options.SOLVER = 1  # APOPT is an MINLP solver
    #
    # # optional solver settings with APOPT
    # m.solver_options = ['minlp_maximum_iterations 500', \
    #                     # minlp iterations with integer solution
    #                     'minlp_max_iter_with_int_sol 10', \
    #                     # treat minlp as nlp
    #                     'minlp_as_nlp 0', \
    #                     # nlp sub-problem max iterations
    #                     'nlp_maximum_iterations 50', \
    #                     # 1 = depth first, 2 = breadth first
    #                     'minlp_branch_method 1', \
    #                     # maximum deviation from whole number
    #                     'minlp_integer_tol 0.05', \
    #                     # covergence tolerance
    #                     'minlp_gap_tol 0.01']
    #
    # # Initialize variables
    # x1 = m.Var(value=1, lb=1, ub=5)
    # x2 = m.Var(value=5, lb=1, ub=5)
    # # Integer constraints for x3 and x4
    # x3 = m.Var(value=5, lb=1, ub=5, integer=True)
    # x4 = m.Var(value=1, lb=1, ub=5, integer=True)
    # # Equations
    # m.Equation(x1 * x2 * x3 * x4 >= 25)
    # m.Equation(x1 ** 2 + x2 ** 2 + x3 ** 2 + x4 ** 2 == 40)
    # m.Obj(x1 * x4 * (x1 + x2 + x3) + x3)  # Objective
    # m.solve(disp=True)  # Solve
    # print('Results')
    # print('x1: ' + str(x1.value))
    # print('x2: ' + str(x2.value))
    # print('x3: ' + str(x3.value))
    # print('x4: ' + str(x4.value))
    # print('Objective: ' + str(m.options.objfcnval))
