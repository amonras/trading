import datetime

import pytest

from backtesting.models.models import BacktestResult
from backtesting.optimization.optimizer import Nsga2

exchange = 'binance'
symbol = 'BTCUSDT'

tf = '15m'
from_time = 0
to_time = int(datetime.datetime.now().timestamp() * 1000)

POP_SIZE = 10


@pytest.fixture(
    params=[
        'obv',
        'ichimoku',
        'sup_res',
        'sma',
        'psar'
    ]
)
def strategy(request) -> str:
    strtgy = request.param
    yield strtgy


def test_initial_population(strategy: str):
    nsga2 = Nsga2(exchange, symbol, strategy, tf, from_time, to_time, POP_SIZE)

    assert len(nsga2.create_initial_population()) == POP_SIZE


def test_create_new_population():
    pass


def test_crowding_distance():
    pass


def test_create_offspring_population():
    pass


def test_non_dominated_sorting():
    population = {}
    nsga2 = Nsga2(exchange, symbol, 'obv', tf, from_time, to_time, POP_SIZE)

    for pnl in range(10):
        for max_dd in range(10):
            br = BacktestResult()
            br.pnl = pnl
            br.max_dd = max_dd
            population[pnl * 100 + max_dd] = br

    fronts = nsga2.non_dominated_sorting(population)

    # There should be 19 fronts as there are 19 anti-diagonals in a 10x10 matrix
    assert len(fronts) == 19


def test_evaluate_population():
    pass
