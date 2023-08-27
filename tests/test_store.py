import pytest

from src.common.store import Store


class TestStore:

    @pytest.fixture(scope='class')
    def store(self):
        return Store(1)

    def test_id(self):
        store = Store(0)
        assert store.id == 0

    def test_prices(self, store):
        assert type(store.prices) == dict and len(store.prices) == 0

    def test_costs(self, store):
        assert type(store.costs) == dict and len(store.costs) == 0

    def test_alpha(self, store):
        assert type(store.alpha) == dict and len(store.alpha) == 0

    def test_beta(self, store):
        assert type(store.beta) == dict and len(store.beta) == 0
