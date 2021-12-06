import datetime

import pytest

from backtesting.strategies import *
from backtesting.strategies.strategy import Strategy


@pytest.fixture(
    params=[
        Obv(ma_period=10),
        Ichimoku(20, 10),
        SupportResistance(2, 2, 1, 1, 1),
        Sma(20, 10),
        Psar(.1, .1, .1)
    ]
)
def strategy(request) -> Strategy:
    strtgy = request.param
    yield strtgy
    if hasattr(strtgy, 'db_client'):
        strtgy.db_client.hf.close()


def test_strategy(strategy: Strategy):
    exchange = 'binance'
    symbol = 'BTCUSDT'

    tf = '15m'
    from_time = 0
    to_time = int(datetime.datetime.now().timestamp() * 1000)

    strategy.set_target(exchange=exchange, symbol=symbol, tf=tf, from_time=from_time, to_time=to_time, path="tests/resources")
    ret = strategy.backtest()

    assert isinstance(ret, tuple)
    assert len(ret) == 2
