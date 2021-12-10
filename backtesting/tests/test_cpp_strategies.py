import datetime

import pytest

from backtesting.strategies import *
from backtesting.strategies.strategy import Strategy
from strategies.cpp_strategy import CppStrategy


@pytest.fixture(
    params=[
        Sma(20, 10),
        Psar(.1, .1, .1)
    ]
)
def strategy(request) -> Strategy:
    strtgy = request.param
    yield strtgy


def test_enter_at(strategy: CppStrategy):
    exchange = 'binance'
    symbol = 'BTCUSDT'

    tf = '15m'
    from_time = 0
    to_time = int(datetime.datetime.now().timestamp() * 1000)

    strategy.set_target(exchange=exchange, symbol=symbol, tf=tf, from_time=from_time, to_time=to_time, path="tests/resources")
    strategy._execute()

    size = strategy._size()
    enter_at = strategy._enter_at(size)

    print(enter_at)


def test_trades(strategy: CppStrategy):
    exchange = 'binance'
    symbol = 'BTCUSDT'

    tf = '15m'
    from_time = 0
    to_time = int(datetime.datetime.now().timestamp() * 1000)

    strategy.set_target(exchange=exchange, symbol=symbol, tf=tf, from_time=from_time, to_time=to_time, path="tests/resources")
    ret = strategy.backtest()

    trades = strategy.trade_history(None)
    print(trades)

