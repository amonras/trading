from datetime import datetime
import pandas as pd

import pytest

from backtesting.strategies import *
from backtesting.strategies.strategy import Strategy
from storage.database import Hdf5Client
from strategies.cpp_strategy import CppStrategy
from utils import resample_timeframe

from_time = int(datetime(2021, 1, 1).timestamp() * 1000)
to_time = int(datetime(2021, 2, 1).timestamp() * 1000)

exchange = 'binance'
symbol = 'BTCUSDT'

tf = '1h'

db_client = Hdf5Client(exchange, path="tests/resources")


@pytest.fixture(
    params=[
        Sma(20, 10),
        Psar(.1, .1, .1)
    ]
)
def strategy(request) -> Strategy:
    strtgy = request.param
    strtgy.set_target(exchange=exchange, symbol=symbol, tf=tf, from_time=from_time, to_time=to_time,
                        path="tests/resources")
    strtgy._execute()
    yield strtgy


@pytest.fixture
def data():
    df = db_client.get_data(symbol=symbol, from_time=from_time, to_time=to_time)
    df = resample_timeframe(df, tf)
    yield df


def test_enter_at(strategy: CppStrategy):
    size = strategy._size()
    enter_at = strategy._enter_at(size)

    print(enter_at)


def test_trades(strategy: CppStrategy):
    ret = strategy.backtest()

    trades = strategy.trade_history(None)
    print(trades)


def test_position_history(strategy: CppStrategy, data: pd.DataFrame):
    position_history = strategy.signal_history(data)
    assert len(data) == len(position_history)


def test_signal_history_returns_same_size(strategy: CppStrategy, data: pd.DataFrame):
    pass


def test_trades_from_signal_match(strategy: CppStrategy, data: pd.DataFrame):
    # Trades computed according to trade signal from C++
    python_calculation = strategy.trade_history_from_signal(data)

    # Trades computed according to trade records from C++
    cpp_calculation = strategy._trade_history(data)

    assert python_calculation.equals(cpp_calculation)