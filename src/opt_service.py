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
            group_assignment = self._pizza_assortment_optimizer_wt_group.optimal_assign_store_type_group
            error_msg = self._validator.validate_model2_solution(optimal_assortment, group_assignment)
        else:
            # solve model 1
            self._pizza_assortment_optimizer.optimize(data_center)
            optimal_assortment = self._pizza_assortment_optimizer.optimal_assortment
            error_msg = self._validator.validate_model1_solution(optimal_assortment)

        if len(error_msg) > 0:
            logging.error(error_msg)

        logging.info("OptService optimize() completes.")
        return optimal_assortment, error_msg
