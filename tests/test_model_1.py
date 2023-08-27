import os
import pandas as pd

from src.opt_service import OptService


class TestModel1:

    def test_inst_1(self):
        data_path = "/Users/klian/dev/learn/python/kohls-opt-assessment/tests/data"
        pizza_file = os.path.join(data_path, "new_pizza.csv")
        pizza = pd.read_csv(pizza_file)

        opt_service = OptService()
        opt_assortment, error_msg = opt_service.optimize(pizza, False)
        print("\nshow pizza assortment: ")
        print(opt_assortment)
        assert len(error_msg) < 1
