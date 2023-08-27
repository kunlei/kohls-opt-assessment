import pytest

from src.common.data_center import DataCenter


class TestDataCenter:

    @pytest.fixture(scope='class')
    def data_center(self):
        return DataCenter()

    def test_stores(self, data_center):
        assert type(data_center.stores) == dict and len(data_center.stores) == 0

    def test_pizza_types(self, data_center):
        pizza_types = data_center.pizza_types
        assert set(pizza_types) == {'A', 'B', 'C'}

    def test_max_pizza_count(self, data_center):
        assert data_center.max_pizza_count > 0

    def test_max_budget(self, data_center):
        assert data_center.max_budget > 0

    def test_num_pizza_groups(self, data_center):
        assert data_center.num_pizza_groups > 0
