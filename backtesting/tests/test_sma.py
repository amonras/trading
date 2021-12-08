import datetime

import pytest

from backtesting.strategies import *
from backtesting.strategies.strategy import Strategy


@pytest.fixture
def sma() -> Sma:
    strtgy = Sma(20, 10)

    yield strtgy
    if hasattr(strtgy, 'db_client'):
        strtgy.db_client.hf.close()


def test_enter_at(sma: Sma):
    exchange = 'binance'
    symbol = 'BTCUSDT'

    tf = '15m'
    from_time = 0
    to_time = int(datetime.datetime.now().timestamp() * 1000)

    sma.set_target(exchange=exchange, symbol=symbol, tf=tf, from_time=from_time, to_time=to_time, path="tests/resources")
    sma._execute()

    size = sma._size()
    enter_at = sma._enter_at(size)

    print(enter_at)


def test_trades(sma: Sma):
    exchange = 'binance'
    symbol = 'BTCUSDT'

    tf = '15m'
    from_time = 0
    to_time = int(datetime.datetime.now().timestamp() * 1000)

    sma.set_target(exchange=exchange, symbol=symbol, tf=tf, from_time=from_time, to_time=to_time, path="tests/resources")
    ret = sma.backtest()

    trades = sma._trades()
    print(trades)

